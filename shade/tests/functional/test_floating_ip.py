# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_floating_ip
----------------------------------

Functional tests for floating IP resource.
"""

import pprint

from novaclient import exceptions as nova_exc
from testtools import content

from shade import _utils
from shade import meta
from shade.exc import OpenStackCloudException
from shade.tests.functional import base
from shade.tests.functional.util import pick_flavor, pick_image


class TestFloatingIP(base.BaseFunctionalTestCase):
    timeout = 60

    def setUp(self):
        super(TestFloatingIP, self).setUp()
        self.nova = self.demo_cloud.nova_client
        if self.demo_cloud.has_service('network'):
            self.neutron = self.demo_cloud.neutron_client
        self.flavor = pick_flavor(self.nova.flavors.list())
        if self.flavor is None:
            self.assertFalse('no sensible flavor available')
        self.image = pick_image(self.nova.images.list())
        if self.image is None:
            self.assertFalse('no sensible image available')

        # Generate a random name for these tests
        self.new_item_name = self.getUniqueString()

        self.addCleanup(self._cleanup_network)
        self.addCleanup(self._cleanup_servers)

    def _cleanup_network(self):
        exception_list = list()

        # Delete stale networks as well as networks created for this test
        if self.demo_cloud.has_service('network'):
            # Delete routers
            for r in self.demo_cloud.list_routers():
                try:
                    if r['name'].startswith(self.new_item_name):
                        # ToDo: update_router currently won't allow removing
                        # external_gateway_info
                        router = {
                            'external_gateway_info': None
                        }
                        self.neutron.update_router(
                            router=r['id'], body={'router': router})
                        # ToDo: Shade currently doesn't have methods for this
                        for s in self.demo_cloud.list_subnets():
                            if s['name'].startswith(self.new_item_name):
                                try:
                                    self.neutron.remove_interface_router(
                                        router=r['id'],
                                        body={'subnet_id': s['id']})
                                except Exception:
                                    pass
                        self.demo_cloud.delete_router(name_or_id=r['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue
            # Delete subnets
            for s in self.demo_cloud.list_subnets():
                if s['name'].startswith(self.new_item_name):
                    try:
                        self.demo_cloud.delete_subnet(name_or_id=s['id'])
                    except Exception as e:
                        exception_list.append(str(e))
                        continue
            # Delete networks
            for n in self.demo_cloud.list_networks():
                if n['name'].startswith(self.new_item_name):
                    try:
                        self.demo_cloud.delete_network(name_or_id=n['id'])
                    except Exception as e:
                        exception_list.append(str(e))
                        continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise OpenStackCloudException('\n'.join(exception_list))

    def _cleanup_servers(self):
        exception_list = list()

        # Delete stale servers as well as server created for this test
        for i in self.nova.servers.list():
            if i.name.startswith(self.new_item_name):
                self.nova.servers.delete(i)
                for _ in _utils._iterate_timeout(
                        self.timeout, "Timeout deleting servers"):
                    try:
                        self.nova.servers.get(server=i)
                    except nova_exc.NotFound:
                        break
                    except Exception as e:
                        exception_list.append(str(e))
                        continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise OpenStackCloudException('\n'.join(exception_list))

    def _cleanup_ips(self, server):

        exception_list = list()

        fixed_ip = meta.get_server_private_ip(server)

        for ip in self.demo_cloud.list_floating_ips():
            if (ip.get('fixed_ip', None) == fixed_ip
                    or ip.get('fixed_ip_address', None) == fixed_ip):
                try:
                    self.demo_cloud.delete_floating_ip(ip['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise OpenStackCloudException('\n'.join(exception_list))

    def _setup_networks(self):
        if self.demo_cloud.has_service('network'):
            # Create a network
            self.test_net = self.demo_cloud.create_network(
                name=self.new_item_name + '_net')
            # Create a subnet on it
            self.test_subnet = self.demo_cloud.create_subnet(
                subnet_name=self.new_item_name + '_subnet',
                network_name_or_id=self.test_net['id'],
                cidr='10.24.4.0/24',
                enable_dhcp=True
            )
            # Create a router
            self.test_router = self.demo_cloud.create_router(
                name=self.new_item_name + '_router')
            # Attach the router to an external network
            ext_nets = self.demo_cloud.search_networks(
                filters={'router:external': True})
            self.demo_cloud.update_router(
                name_or_id=self.test_router['id'],
                ext_gateway_net_id=ext_nets[0]['id'])
            # Attach the router to the internal subnet
            self.neutron.add_interface_router(
                router=self.test_router['id'],
                body={'subnet_id': self.test_subnet['id']})

            # Select the network for creating new servers
            self.nic = {'net-id': self.test_net['id']}
            self.addDetail(
                'networks-neutron',
                content.text_content(pprint.pformat(
                    self.demo_cloud.list_networks())))
        else:
            # ToDo: remove once we have list/get methods for nova networks
            nets = self.demo_cloud.nova_client.networks.list()
            self.addDetail(
                'networks-nova',
                content.text_content(pprint.pformat(
                    nets)))
            self.nic = {'net-id': nets[0].id}

    def test_private_ip(self):
        self._setup_networks()

        new_server = self.demo_cloud.get_openstack_vars(
            self.demo_cloud.create_server(
                wait=True, name=self.new_item_name + '_server',
                image=self.image,
                flavor=self.flavor, nics=[self.nic]))

        self.addDetail(
            'server', content.text_content(pprint.pformat(new_server)))
        self.assertNotEqual(new_server['private_v4'], '')

    def test_add_auto_ip(self):
        self._setup_networks()

        new_server = self.demo_cloud.create_server(
            wait=True, name=self.new_item_name + '_server',
            image=self.image,
            flavor=self.flavor, nics=[self.nic])

        # ToDo: remove the following iteration when create_server waits for
        # the IP to be attached
        ip = None
        for _ in _utils._iterate_timeout(
                self.timeout, "Timeout waiting for IP address to be attached"):
            ip = meta.get_server_external_ipv4(self.demo_cloud, new_server)
            if ip is not None:
                break
            new_server = self.demo_cloud.get_server(new_server.id)

        self.addCleanup(self._cleanup_ips, new_server)

    def test_detach_ip_from_server(self):
        self._setup_networks()

        new_server = self.demo_cloud.create_server(
            wait=True, name=self.new_item_name + '_server',
            image=self.image,
            flavor=self.flavor, nics=[self.nic])

        # ToDo: remove the following iteration when create_server waits for
        # the IP to be attached
        ip = None
        for _ in _utils._iterate_timeout(
                self.timeout, "Timeout waiting for IP address to be attached"):
            ip = meta.get_server_external_ipv4(self.demo_cloud, new_server)
            if ip is not None:
                break
            new_server = self.demo_cloud.get_server(new_server.id)

        self.addCleanup(self._cleanup_ips, new_server)

        f_ip = self.demo_cloud.get_floating_ip(
            id=None, filters={'floating_ip_address': ip})
        self.demo_cloud.detach_ip_from_server(
            server_id=new_server.id, floating_ip_id=f_ip['id'])

    def test_list_floating_ips(self):
        fip_admin = self.operator_cloud.create_floating_ip()
        self.addCleanup(self.operator_cloud.delete_floating_ip, fip_admin.id)
        fip_user = self.demo_cloud.create_floating_ip()
        self.addCleanup(self.demo_cloud.delete_floating_ip, fip_user.id)

        # Get all the floating ips.
        fip_id_list = [
            fip.id for fip in self.operator_cloud.list_floating_ips()
        ]
        if self.demo_cloud.has_service('network'):
            # Neutron returns all FIP for all projects by default
            self.assertIn(fip_admin.id, fip_id_list)
            self.assertIn(fip_user.id, fip_id_list)

            # Ask Neutron for only a subset of all the FIPs.
            filtered_fip_id_list = [
                fip.id for fip in self.operator_cloud.list_floating_ips(
                    {'tenant_id': self.demo_cloud.current_project_id}
                )
            ]
            self.assertNotIn(fip_admin.id, filtered_fip_id_list)
            self.assertIn(fip_user.id, filtered_fip_id_list)

        else:
            self.assertIn(fip_admin.id, fip_id_list)
            # By default, Nova returns only the FIPs that belong to the
            # project which made the listing request.
            self.assertNotIn(fip_user.id, fip_id_list)
            self.assertRaisesRegex(
                ValueError, "Nova-network don't support server-side.*",
                self.operator_cloud.list_floating_ips, filters={'foo': 'bar'}
            )

    def test_search_floating_ips(self):
        fip_user = self.demo_cloud.create_floating_ip()
        self.addCleanup(self.demo_cloud.delete_floating_ip, fip_user.id)

        self.assertIn(
            fip_user['id'],
            [fip.id for fip in self.demo_cloud.search_floating_ips(
                filters={"attached": False})]
        )
        self.assertNotIn(
            fip_user['id'],
            [fip.id for fip in self.demo_cloud.search_floating_ips(
                filters={"attached": True})]
        )
