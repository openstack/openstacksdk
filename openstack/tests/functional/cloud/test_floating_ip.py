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
import sys

from testtools import content

from openstack.cloud import meta
from openstack import exceptions
from openstack import proxy
from openstack.tests.functional import base
from openstack import utils


class TestFloatingIP(base.BaseFunctionalTest):
    timeout = 60

    def setUp(self):
        super().setUp()

        # Generate a random name for these tests
        self.new_item_name = self.getUniqueString()

        self.addCleanup(self._cleanup_network)
        self.addCleanup(self._cleanup_servers)

    def _cleanup_network(self):
        exception_list = list()
        tb_list = list()

        # Delete stale networks as well as networks created for this test
        if self.user_cloud.has_service('network'):
            # Delete routers
            for r in self.user_cloud.list_routers():
                try:
                    if r['name'].startswith(self.new_item_name):
                        self.user_cloud.update_router(
                            r, ext_gateway_net_id=None
                        )
                        for s in self.user_cloud.list_subnets():
                            if s['name'].startswith(self.new_item_name):
                                try:
                                    self.user_cloud.remove_router_interface(
                                        r, subnet_id=s['id']
                                    )
                                except Exception:
                                    pass
                        self.user_cloud.delete_router(r.id)
                except Exception as e:
                    exception_list.append(e)
                    tb_list.append(sys.exc_info()[2])
                    continue
            # Delete subnets
            for s in self.user_cloud.list_subnets():
                if s['name'].startswith(self.new_item_name):
                    try:
                        self.user_cloud.delete_subnet(s.id)
                    except Exception as e:
                        exception_list.append(e)
                        tb_list.append(sys.exc_info()[2])
                        continue
            # Delete networks
            for n in self.user_cloud.list_networks():
                if n['name'].startswith(self.new_item_name):
                    try:
                        self.user_cloud.delete_network(n.id)
                    except Exception as e:
                        exception_list.append(e)
                        tb_list.append(sys.exc_info()[2])
                        continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            if len(exception_list) > 1:
                self.addDetail(
                    'exceptions',
                    content.text_content(
                        '\n'.join([str(ex) for ex in exception_list])
                    ),
                )
            exc = exception_list[0]
            raise exc

    def _cleanup_servers(self):
        exception_list = list()

        # Delete stale servers as well as server created for this test
        for i in self.user_cloud.list_servers(bare=True):
            if i.name.startswith(self.new_item_name):
                try:
                    self.user_cloud.delete_server(i.id, wait=True)
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def _cleanup_ips(self, server):
        exception_list = list()

        fixed_ip = meta.get_server_private_ip(server)

        for ip in self.user_cloud.list_floating_ips():
            if (
                ip.get('fixed_ip', None) == fixed_ip
                or ip.get('fixed_ip_address', None) == fixed_ip
            ):
                try:
                    self.user_cloud.delete_floating_ip(ip.id)
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def _setup_networks(self):
        if self.user_cloud.has_service('network'):
            # Create a network
            self.test_net = self.user_cloud.create_network(
                name=self.new_item_name + '_net'
            )
            # Create a subnet on it
            self.test_subnet = self.user_cloud.create_subnet(
                subnet_name=self.new_item_name + '_subnet',
                network_name_or_id=self.test_net['id'],
                cidr='10.24.4.0/24',
                enable_dhcp=True,
            )
            # Create a router
            self.test_router = self.user_cloud.create_router(
                name=self.new_item_name + '_router'
            )
            # Attach the router to an external network
            ext_nets = self.user_cloud.search_networks(
                filters={'router:external': True}
            )
            self.user_cloud.update_router(
                name_or_id=self.test_router['id'],
                ext_gateway_net_id=ext_nets[0]['id'],
            )
            # Attach the router to the internal subnet
            self.user_cloud.add_router_interface(
                self.test_router, subnet_id=self.test_subnet['id']
            )

            # Select the network for creating new servers
            self.nic = {'net-id': self.test_net['id']}
            self.addDetail(
                'networks-neutron',
                content.text_content(
                    pprint.pformat(self.user_cloud.list_networks())
                ),
            )
        else:
            # Find network names for nova-net
            data = proxy._json_response(
                self.user_cloud.compute.get('/os-tenant-networks')
            )
            nets = meta.get_and_munchify('networks', data)
            self.addDetail(
                'networks-nova', content.text_content(pprint.pformat(nets))
            )
            self.nic = {'net-id': nets[0].id}

    def test_private_ip(self):
        self._setup_networks()

        new_server = self.user_cloud.get_openstack_vars(
            self.user_cloud.create_server(
                wait=True,
                name=self.new_item_name + '_server',
                image=self.image,
                flavor=self.flavor,
                nics=[self.nic],
            )
        )

        self.addDetail(
            'server', content.text_content(pprint.pformat(new_server))
        )
        self.assertNotEqual(new_server['private_v4'], '')

    def test_add_auto_ip(self):
        self._setup_networks()

        new_server = self.user_cloud.create_server(
            wait=True,
            name=self.new_item_name + '_server',
            image=self.image,
            flavor=self.flavor,
            nics=[self.nic],
        )

        # ToDo: remove the following iteration when create_server waits for
        # the IP to be attached
        ip = None
        for _ in utils.iterate_timeout(
            self.timeout, "Timeout waiting for IP address to be attached"
        ):
            ip = meta.get_server_external_ipv4(self.user_cloud, new_server)
            if ip is not None:
                break
            new_server = self.user_cloud.get_server(new_server.id)

        self.addCleanup(self._cleanup_ips, new_server)

    def test_detach_ip_from_server(self):
        self._setup_networks()

        new_server = self.user_cloud.create_server(
            wait=True,
            name=self.new_item_name + '_server',
            image=self.image,
            flavor=self.flavor,
            nics=[self.nic],
        )

        # ToDo: remove the following iteration when create_server waits for
        # the IP to be attached
        ip = None
        for _ in utils.iterate_timeout(
            self.timeout, "Timeout waiting for IP address to be attached"
        ):
            ip = meta.get_server_external_ipv4(self.user_cloud, new_server)
            if ip is not None:
                break
            new_server = self.user_cloud.get_server(new_server.id)

        self.addCleanup(self._cleanup_ips, new_server)

        f_ip = self.user_cloud.get_floating_ip(
            id=None, filters={'floating_ip_address': ip}
        )
        self.user_cloud.detach_ip_from_server(
            server_id=new_server.id, floating_ip_id=f_ip['id']
        )

    def test_list_floating_ips(self):
        if self.operator_cloud:
            fip_admin = self.operator_cloud.create_floating_ip()
            self.addCleanup(
                self.operator_cloud.delete_floating_ip, fip_admin.id
            )
        fip_user = self.user_cloud.create_floating_ip()
        self.addCleanup(self.user_cloud.delete_floating_ip, fip_user.id)

        # Get all the floating ips.
        if self.operator_cloud:
            fip_op_id_list = [
                fip.id for fip in self.operator_cloud.list_floating_ips()
            ]
        fip_user_id_list = [
            fip.id for fip in self.user_cloud.list_floating_ips()
        ]

        if self.user_cloud.has_service('network'):
            self.assertIn(fip_user.id, fip_user_id_list)
            # Neutron returns all FIP for all projects by default
            if self.operator_cloud and fip_admin:
                self.assertIn(fip_user.id, fip_op_id_list)

            # Ask Neutron for only a subset of all the FIPs.
            if self.operator_cloud:
                filtered_fip_id_list = [
                    fip.id
                    for fip in self.operator_cloud.list_floating_ips(
                        {'tenant_id': self.user_cloud.current_project_id}
                    )
                ]
                self.assertNotIn(fip_admin.id, filtered_fip_id_list)
                self.assertIn(fip_user.id, filtered_fip_id_list)

        else:
            if fip_admin:
                self.assertIn(fip_admin.id, fip_op_id_list)
            # By default, Nova returns only the FIPs that belong to the
            # project which made the listing request.
            if self.operator_cloud:
                self.assertNotIn(fip_user.id, fip_op_id_list)
                self.assertRaisesRegex(
                    ValueError,
                    "Nova-network don't support server-side.*",
                    self.operator_cloud.list_floating_ips,
                    filters={'foo': 'bar'},
                )

    def test_search_floating_ips(self):
        fip_user = self.user_cloud.create_floating_ip()
        self.addCleanup(self.user_cloud.delete_floating_ip, fip_user.id)

        self.assertIn(
            fip_user['id'],
            [fip.id for fip in self.user_cloud.search_floating_ips()],
        )

    def test_get_floating_ip_by_id(self):
        fip_user = self.user_cloud.create_floating_ip()
        self.addCleanup(self.user_cloud.delete_floating_ip, fip_user.id)

        ret_fip = self.user_cloud.get_floating_ip_by_id(fip_user.id)
        self.assertEqual(fip_user, ret_fip)

    def test_available_floating_ip(self):
        fips_user = self.user_cloud.list_floating_ips()
        self.assertEqual(fips_user, [])

        new_fip = self.user_cloud.available_floating_ip()
        self.assertIsNotNone(new_fip)
        self.assertIn('id', new_fip)
        self.addCleanup(self.user_cloud.delete_floating_ip, new_fip.id)

        new_fips_user = self.user_cloud.list_floating_ips()
        self.assertEqual(new_fips_user, [new_fip])

        reuse_fip = self.user_cloud.available_floating_ip()
        self.assertEqual(reuse_fip.id, new_fip.id)
