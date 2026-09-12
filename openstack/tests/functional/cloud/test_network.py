# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import ipaddress
import pprint
import random
import string
import sys

from testtools import content

from openstack.cloud import meta
from openstack import exceptions
from openstack import proxy
from openstack.tests.functional import base
from openstack import utils


class TestNetwork(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        if not self.operator_cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')
        self.network_name = self.getUniqueString('network')
        self.addCleanup(self._cleanup_networks)

    def _cleanup_networks(self):
        exception_list = list()
        for network in self.operator_cloud.list_networks():
            if network['name'].startswith(self.network_name):
                try:
                    self.operator_cloud.delete_network(network['name'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_network_basic(self):
        net1 = self.operator_cloud.create_network(name=self.network_name)
        self.assertIn('id', net1)
        self.assertEqual(self.network_name, net1['name'])
        self.assertFalse(net1['shared'])
        self.assertFalse(net1['router:external'])
        self.assertTrue(net1['admin_state_up'])
        self.assertTrue(net1['port_security_enabled'])

    def test_get_network_by_id(self):
        net1 = self.operator_cloud.create_network(name=self.network_name)
        self.assertIn('id', net1)
        self.assertEqual(self.network_name, net1['name'])
        self.assertFalse(net1['shared'])
        self.assertFalse(net1['router:external'])
        self.assertTrue(net1['admin_state_up'])

        ret_net1 = self.operator_cloud.get_network_by_id(net1.id)
        self.assertIn('id', ret_net1)
        self.assertEqual(self.network_name, ret_net1['name'])
        self.assertFalse(ret_net1['shared'])
        self.assertFalse(ret_net1['router:external'])
        self.assertTrue(ret_net1['admin_state_up'])

    def test_create_network_advanced(self):
        net1 = self.operator_cloud.create_network(
            name=self.network_name,
            shared=True,
            external=True,
            admin_state_up=False,
        )
        self.assertIn('id', net1)
        self.assertEqual(self.network_name, net1['name'])
        self.assertTrue(net1['router:external'])
        self.assertTrue(net1['shared'])
        self.assertFalse(net1['admin_state_up'])

    def test_create_network_provider_flat(self):
        existing_public = self.operator_cloud.search_networks(
            filters={'provider:network_type': 'flat'}
        )
        if existing_public:
            self.skipTest('Physical network already allocated')
        net1 = self.operator_cloud.create_network(
            name=self.network_name,
            shared=True,
            provider={
                'physical_network': 'public',
                'network_type': 'flat',
            },
        )
        self.assertIn('id', net1)
        self.assertEqual(self.network_name, net1['name'])
        self.assertEqual('flat', net1['provider:network_type'])
        self.assertEqual('public', net1['provider:physical_network'])
        self.assertIsNone(net1['provider:segmentation_id'])

    def test_create_network_port_security_disabled(self):
        net1 = self.operator_cloud.create_network(
            name=self.network_name,
            port_security_enabled=False,
        )
        self.assertIn('id', net1)
        self.assertEqual(self.network_name, net1['name'])
        self.assertTrue(net1['admin_state_up'])
        self.assertFalse(net1['shared'])
        self.assertFalse(net1['router:external'])
        self.assertFalse(net1['port_security_enabled'])

    def test_list_networks_filtered(self):
        net1 = self.operator_cloud.create_network(name=self.network_name)
        self.assertIsNotNone(net1)
        net2 = self.operator_cloud.create_network(
            name=self.network_name + 'other'
        )
        self.assertIsNotNone(net2)
        match = self.operator_cloud.list_networks(
            filters=dict(name=self.network_name)
        )
        self.assertEqual(1, len(match))
        self.assertEqual(net1['name'], match[0]['name'])

    def test_update_network(self):
        net = self.operator_cloud.create_network(name=self.network_name)
        self.assertEqual(net.name, self.network_name)
        new_name = self.getUniqueString('network')
        net = self.operator_cloud.update_network(net.id, name=new_name)
        self.addCleanup(self.operator_cloud.delete_network, new_name)
        self.assertNotEqual(net.name, self.network_name)
        self.assertEqual(net.name, new_name)


class TestPort(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        # Skip Neutron tests if neutron is not present
        if not self.user_cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')

        net_name = self.getUniqueString('CloudPortName')
        self.net = self.user_cloud.network.create_network(name=net_name)
        self.addCleanup(self.user_cloud.network.delete_network, self.net.id)

        # Generate a unique port name to allow concurrent tests
        self.new_port_name = 'test_' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5)
        )

        self.addCleanup(self._cleanup_ports)

    def _cleanup_ports(self):
        exception_list = list()

        for p in self.user_cloud.list_ports():
            if p['name'].startswith(self.new_port_name):
                try:
                    self.user_cloud.delete_port(name_or_id=p['id'])
                except Exception as e:
                    # We were unable to delete this port, let's try with next
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_port(self):
        port_name = self.new_port_name + '_create'

        port = self.user_cloud.create_port(
            network_id=self.net.id, name=port_name
        )
        self.assertIsInstance(port, dict)
        self.assertIn('id', port)
        self.assertEqual(port.get('name'), port_name)

    def test_get_port(self):
        port_name = self.new_port_name + '_get'

        port = self.user_cloud.create_port(
            network_id=self.net.id, name=port_name
        )
        self.assertIsInstance(port, dict)
        self.assertIn('id', port)
        self.assertEqual(port.get('name'), port_name)

        updated_port = self.user_cloud.get_port(name_or_id=port['id'])
        assert updated_port is not None  # narrow type
        # extra_dhcp_opts is added later by Neutron...
        if 'extra_dhcp_opts' in updated_port and 'extra_dhcp_opts' not in port:
            del updated_port['extra_dhcp_opts']
        self.assertEqual(port, updated_port)

    def test_get_port_by_id(self):
        port_name = self.new_port_name + '_get_by_id'

        port = self.user_cloud.create_port(
            network_id=self.net.id, name=port_name
        )
        self.assertIsInstance(port, dict)
        self.assertIn('id', port)
        self.assertEqual(port.get('name'), port_name)

        updated_port = self.user_cloud.get_port_by_id(port['id'])
        # extra_dhcp_opts is added later by Neutron...
        if 'extra_dhcp_opts' in updated_port and 'extra_dhcp_opts' not in port:
            del updated_port['extra_dhcp_opts']
        self.assertEqual(port, updated_port)

    def test_update_port(self):
        port_name = self.new_port_name + '_update'
        new_port_name = port_name + '_new'

        self.user_cloud.create_port(network_id=self.net.id, name=port_name)

        port = self.user_cloud.update_port(
            name_or_id=port_name, name=new_port_name
        )
        self.assertIsInstance(port, dict)
        self.assertEqual(port.get('name'), new_port_name)

        updated_port = self.user_cloud.get_port(name_or_id=port['id'])
        assert updated_port is not None  # narrow type
        self.assertEqual(port.get('name'), new_port_name)
        port.pop('revision_number', None)
        port.pop('revision_number', None)
        port.pop('updated_at', None)
        port.pop('updated_at', None)
        updated_port.pop('revision_number', None)
        updated_port.pop('revision_number', None)
        updated_port.pop('updated_at', None)
        updated_port.pop('updated_at', None)

        self.assertEqual(port, updated_port)

    def test_delete_port(self):
        port_name = self.new_port_name + '_delete'

        port = self.user_cloud.create_port(
            network_id=self.net.id, name=port_name
        )
        self.assertIsInstance(port, dict)
        self.assertIn('id', port)
        self.assertEqual(port.get('name'), port_name)

        updated_port = self.user_cloud.get_port(name_or_id=port['id'])
        self.assertIsNotNone(updated_port)

        self.user_cloud.delete_port(name_or_id=port_name)

        updated_port = self.user_cloud.get_port(name_or_id=port['id'])
        self.assertIsNone(updated_port)


EXPECTED_TOPLEVEL_FIELDS = (
    'id',
    'name',
    'is_admin_state_up',
    'external_gateway_info',
    'project_id',
    'routes',
    'status',
)

EXPECTED_GW_INFO_FIELDS = ('network_id', 'enable_snat', 'external_fixed_ips')


class TestRouter(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')

        self.router_prefix = self.getUniqueString('router')
        self.network_prefix = self.getUniqueString('network')
        self.subnet_prefix = self.getUniqueString('subnet')

        # NOTE(Shrews): Order matters!
        self.addCleanup(self._cleanup_networks)
        self.addCleanup(self._cleanup_subnets)
        self.addCleanup(self._cleanup_routers)

    def _cleanup_routers(self):
        exception_list = list()
        for router in self.operator_cloud.list_routers():
            if router['name'].startswith(self.router_prefix):
                try:
                    self.operator_cloud.delete_router(router['name'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def _cleanup_networks(self):
        exception_list = list()
        for network in self.operator_cloud.list_networks():
            if network['name'].startswith(self.network_prefix):
                try:
                    self.operator_cloud.delete_network(network['name'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def _cleanup_subnets(self):
        exception_list = list()
        for subnet in self.operator_cloud.list_subnets():
            if subnet['name'].startswith(self.subnet_prefix):
                try:
                    self.operator_cloud.delete_subnet(subnet['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_router_basic(self):
        net1_name = self.network_prefix + '_net1'
        net1 = self.operator_cloud.create_network(
            name=net1_name, external=True
        )

        router_name = self.router_prefix + '_create_basic'
        router = self.operator_cloud.create_router(
            name=router_name,
            admin_state_up=True,
            ext_gateway_net_id=net1['id'],
        )

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, router)

        ext_gw_info = router['external_gateway_info']
        for field in EXPECTED_GW_INFO_FIELDS:
            self.assertIn(field, ext_gw_info)

        self.assertEqual(router_name, router['name'])
        self.assertEqual('ACTIVE', router['status'])
        self.assertEqual(net1['id'], ext_gw_info['network_id'])
        self.assertTrue(ext_gw_info['enable_snat'])

    def test_create_router_project(self):
        project = self.operator_cloud.get_project('demo')
        self.assertIsNotNone(project)
        assert project is not None
        proj_id = project['id']
        net1_name = self.network_prefix + '_net1'
        net1 = self.operator_cloud.create_network(
            name=net1_name, external=True, project_id=proj_id
        )

        router_name = self.router_prefix + '_create_project'
        router = self.operator_cloud.create_router(
            name=router_name,
            admin_state_up=True,
            ext_gateway_net_id=net1['id'],
            project_id=proj_id,
        )

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, router)

        ext_gw_info = router['external_gateway_info']
        for field in EXPECTED_GW_INFO_FIELDS:
            self.assertIn(field, ext_gw_info)

        self.assertEqual(router_name, router['name'])
        self.assertEqual('ACTIVE', router['status'])
        self.assertEqual(proj_id, router['project_id'])
        self.assertEqual(net1['id'], ext_gw_info['network_id'])
        self.assertTrue(ext_gw_info['enable_snat'])

    def _create_and_verify_advanced_router(
        self, external_cidr, external_gateway_ip=None
    ):
        # external_cidr must be passed in as unicode (u'')
        # NOTE(Shrews): The arguments are needed because these tests
        # will run in parallel and we want to make sure that each test
        # is using different resources to prevent race conditions.
        net1_name = self.network_prefix + '_net1'
        sub1_name = self.subnet_prefix + '_sub1'
        net1 = self.operator_cloud.create_network(
            name=net1_name, external=True
        )
        sub1 = self.operator_cloud.create_subnet(
            net1['id'],
            external_cidr,
            subnet_name=sub1_name,
            gateway_ip=external_gateway_ip,
        )

        ip_net = ipaddress.IPv4Network(external_cidr)
        last_ip = str(list(ip_net.hosts())[-1])

        router_name = self.router_prefix + '_create_advanced'
        router = self.operator_cloud.create_router(
            name=router_name,
            admin_state_up=False,
            ext_gateway_net_id=net1['id'],
            enable_snat=False,
            ext_fixed_ips=[{'subnet_id': sub1['id'], 'ip_address': last_ip}],
        )

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, router)

        ext_gw_info = router['external_gateway_info']
        for field in EXPECTED_GW_INFO_FIELDS:
            self.assertIn(field, ext_gw_info)

        self.assertEqual(router_name, router['name'])
        self.assertEqual('ACTIVE', router['status'])
        self.assertFalse(router['admin_state_up'])

        self.assertEqual(1, len(ext_gw_info['external_fixed_ips']))
        self.assertEqual(
            sub1['id'], ext_gw_info['external_fixed_ips'][0]['subnet_id']
        )
        self.assertEqual(
            last_ip, ext_gw_info['external_fixed_ips'][0]['ip_address']
        )

        return router

    def test_create_router_advanced(self):
        self._create_and_verify_advanced_router(external_cidr='10.2.2.0/24')

    def test_add_remove_router_interface(self):
        router = self._create_and_verify_advanced_router(
            external_cidr='10.3.3.0/24'
        )
        net_name = self.network_prefix + '_intnet1'
        sub_name = self.subnet_prefix + '_intsub1'
        net = self.operator_cloud.create_network(name=net_name)
        sub = self.operator_cloud.create_subnet(
            net['id'],
            '10.4.4.0/24',
            subnet_name=sub_name,
            gateway_ip='10.4.4.1',
        )

        iface = self.operator_cloud.add_router_interface(
            router, subnet_id=sub['id']
        )
        self.assertIsNone(
            self.operator_cloud.remove_router_interface(
                router, subnet_id=sub['id']
            )
        )

        # Test return values *after* the interface is detached so the
        # resources we've created can be cleaned up if these asserts fail.
        self.assertIsNotNone(iface)
        for key in ('id', 'subnet_id', 'port_id', 'project_id'):
            self.assertIn(key, iface)
        self.assertEqual(router['id'], iface['id'])
        self.assertEqual(sub['id'], iface['subnet_id'])

    def test_list_router_interfaces(self):
        router = self._create_and_verify_advanced_router(
            external_cidr='10.5.5.0/24'
        )
        net_name = self.network_prefix + '_intnet1'
        sub_name = self.subnet_prefix + '_intsub1'
        net = self.operator_cloud.create_network(name=net_name)
        sub = self.operator_cloud.create_subnet(
            net['id'],
            '10.6.6.0/24',
            subnet_name=sub_name,
            gateway_ip='10.6.6.1',
        )

        iface = self.operator_cloud.add_router_interface(
            router, subnet_id=sub['id']
        )
        all_ifaces = self.operator_cloud.list_router_interfaces(router)
        int_ifaces = self.operator_cloud.list_router_interfaces(
            router, interface_type='internal'
        )
        ext_ifaces = self.operator_cloud.list_router_interfaces(
            router, interface_type='external'
        )
        self.assertIsNone(
            self.operator_cloud.remove_router_interface(
                router, subnet_id=sub['id']
            )
        )

        # Test return values *after* the interface is detached so the
        # resources we've created can be cleaned up if these asserts fail.
        self.assertIsNotNone(iface)
        self.assertEqual(2, len(all_ifaces))
        self.assertEqual(1, len(int_ifaces))
        self.assertEqual(1, len(ext_ifaces))

        ext_fixed_ips = router['external_gateway_info']['external_fixed_ips']
        self.assertEqual(
            ext_fixed_ips[0]['subnet_id'],
            ext_ifaces[0]['fixed_ips'][0]['subnet_id'],
        )
        self.assertEqual(sub['id'], int_ifaces[0]['fixed_ips'][0]['subnet_id'])

    def test_update_router_name(self):
        router = self._create_and_verify_advanced_router(
            external_cidr='10.7.7.0/24'
        )

        new_name = self.router_prefix + '_update_name'
        updated = self.operator_cloud.update_router(
            router['id'], name=new_name
        )
        self.assertIsNotNone(updated)
        assert updated is not None  # narrow type

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, updated)

        # Name is the only change we expect
        self.assertEqual(new_name, updated['name'])

        # Validate nothing else changed
        self.assertEqual(router['status'], updated['status'])
        self.assertEqual(router['admin_state_up'], updated['admin_state_up'])
        self.assertEqual(
            router['external_gateway_info'], updated['external_gateway_info']
        )

    def test_update_router_routes(self):
        router = self._create_and_verify_advanced_router(
            external_cidr='10.7.7.0/24'
        )

        routes = [{"destination": "10.7.7.0/24", "nexthop": "10.7.7.99"}]

        updated = self.operator_cloud.update_router(
            router['id'], routes=routes
        )
        self.assertIsNotNone(updated)
        assert updated is not None  # narrow type

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, updated)

        # Name is the only change we expect
        self.assertEqual(routes, updated['routes'])

        # Validate nothing else changed
        self.assertEqual(router['status'], updated['status'])
        self.assertEqual(router['admin_state_up'], updated['admin_state_up'])
        self.assertEqual(
            router['external_gateway_info'], updated['external_gateway_info']
        )

    def test_update_router_admin_state(self):
        router = self._create_and_verify_advanced_router(
            external_cidr='10.8.8.0/24'
        )

        updated = self.operator_cloud.update_router(
            router['id'], admin_state_up=True
        )
        self.assertIsNotNone(updated)
        assert updated is not None  # narrow type

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, updated)

        # admin_state_up is the only change we expect
        self.assertTrue(updated['admin_state_up'])
        self.assertNotEqual(
            router['admin_state_up'], updated['admin_state_up']
        )

        # Validate nothing else changed
        self.assertEqual(router['status'], updated['status'])
        self.assertEqual(router['name'], updated['name'])
        self.assertEqual(
            router['external_gateway_info'], updated['external_gateway_info']
        )

    def test_update_router_ext_gw_info(self):
        router = self._create_and_verify_advanced_router(
            external_cidr='10.9.9.0/24'
        )

        # create a new subnet
        existing_net_id = router['external_gateway_info']['network_id']
        sub_name = self.subnet_prefix + '_update'
        sub = self.operator_cloud.create_subnet(
            existing_net_id,
            '10.10.10.0/24',
            subnet_name=sub_name,
            gateway_ip='10.10.10.1',
        )

        updated = self.operator_cloud.update_router(
            router['id'],
            ext_gateway_net_id=existing_net_id,
            ext_fixed_ips=[
                {'subnet_id': sub['id'], 'ip_address': '10.10.10.77'}
            ],
        )
        self.assertIsNotNone(updated)
        assert updated is not None  # narrow type

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, updated)

        # external_gateway_info is the only change we expect
        ext_gw_info = updated['external_gateway_info']
        self.assertEqual(1, len(ext_gw_info['external_fixed_ips']))
        self.assertEqual(
            sub['id'], ext_gw_info['external_fixed_ips'][0]['subnet_id']
        )
        self.assertEqual(
            '10.10.10.77', ext_gw_info['external_fixed_ips'][0]['ip_address']
        )

        # Validate nothing else changed
        self.assertEqual(router['status'], updated['status'])
        self.assertEqual(router['name'], updated['name'])
        self.assertEqual(router['admin_state_up'], updated['admin_state_up'])


class TestSecurityGroups(base.BaseFunctionalTest):
    def test_create_list_security_groups(self):
        sg1 = self.user_cloud.create_security_group(
            name="sg1", description="sg1"
        )
        self.addCleanup(self.user_cloud.delete_security_group, sg1['id'])
        if self.user_cloud.has_service('network'):
            # Neutron defaults to all_tenants=1 when admin
            sg_list = self.user_cloud.list_security_groups()
            self.assertIn(sg1['id'], [sg['id'] for sg in sg_list])

        else:
            # Nova does not list all tenants by default
            sg_list = self.operator_cloud.list_security_groups()

    def test_create_list_security_groups_operator(self):
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        sg1 = self.user_cloud.create_security_group(
            name="sg1", description="sg1"
        )
        self.addCleanup(self.user_cloud.delete_security_group, sg1['id'])
        sg2 = self.operator_cloud.create_security_group(
            name="sg2", description="sg2"
        )
        self.addCleanup(self.operator_cloud.delete_security_group, sg2['id'])

        if self.user_cloud.has_service('network'):
            # Neutron defaults to all_tenants=1 when admin
            sg_list = self.operator_cloud.list_security_groups()
            self.assertIn(sg1['id'], [sg['id'] for sg in sg_list])

            sg_list = self.operator_cloud.list_security_groups(
                filters={'project_id': self.user_cloud.current_project_id}
            )
            self.assertIn(sg1['id'], [sg['id'] for sg in sg_list])
            self.assertNotIn(sg2['id'], [sg['id'] for sg in sg_list])

        else:
            # Nova does not list all projects by default
            sg_list = self.operator_cloud.list_security_groups()
            self.assertIn(sg2['id'], [sg['id'] for sg in sg_list])
            self.assertNotIn(sg1['id'], [sg['id'] for sg in sg_list])

            sg_list = self.operator_cloud.list_security_groups(
                filters={'all_tenants': 1}
            )
            self.assertIn(sg1['id'], [sg['id'] for sg in sg_list])

    def test_get_security_group_by_id(self):
        sg = self.user_cloud.create_security_group(name='sg', description='sg')
        self.addCleanup(self.user_cloud.delete_security_group, sg['id'])

        ret_sg = self.user_cloud.get_security_group_by_id(sg['id'])
        self.assertEqual(sg, ret_sg)


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
                            r['id'], ext_gateway_net_id=None
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
            nets = meta.get_and_munchify('networks', data)  # type: ignore[arg-type]
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
            fetched_server = self.user_cloud.get_server(new_server.id)
            assert fetched_server is not None
            new_server = fetched_server

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
            fetched_server = self.user_cloud.get_server(new_server.id)
            assert fetched_server is not None
            new_server = fetched_server

        self.addCleanup(self._cleanup_ips, new_server)

        f_ip = self.user_cloud.get_floating_ip(
            id=None, filters={'floating_ip_address': ip}
        )
        assert f_ip is not None
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
                        {'project_id': self.user_cloud.current_project_id}
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


# When using nova-network, floating IP pools are created with nova-manage
# command.
# When using Neutron, floating IP pools in Nova are mapped from external
# network names. This only if the floating-ip-pools nova extension is
# available.
# For instance, for current implementation of hpcloud that's not true:
# nova floating-ip-pool-list returns 404.


class TestFloatingIPPool(base.BaseFunctionalTest):
    def test_list_floating_ip_pools(self):
        pools = self.user_cloud.list_floating_ip_pools()
        if not pools:
            self.assertFalse('no floating-ip pool available')

        for pool in pools:
            self.assertIn('name', pool)


class TestQosPolicy(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')
        if not self.operator_cloud._has_neutron_extension('qos'):
            self.skipTest('QoS network extension not supported by cloud')
        self.policy_name = self.getUniqueString('qos_policy')
        self.addCleanup(self._cleanup_policies)

    def _cleanup_policies(self):
        exception_list = list()
        for policy in self.operator_cloud.list_qos_policies():
            if policy['name'].startswith(self.policy_name):
                try:
                    self.operator_cloud.delete_qos_policy(policy['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_qos_policy_basic(self):
        policy = self.operator_cloud.create_qos_policy(name=self.policy_name)
        self.assertIn('id', policy)
        self.assertEqual(self.policy_name, policy['name'])
        self.assertFalse(policy['is_shared'])
        self.assertFalse(policy['is_default'])

    def test_create_qos_policy_shared(self):
        policy = self.operator_cloud.create_qos_policy(
            name=self.policy_name, shared=True
        )
        self.assertIn('id', policy)
        self.assertEqual(self.policy_name, policy['name'])
        self.assertTrue(policy['is_shared'])
        self.assertFalse(policy['is_default'])

    def test_create_qos_policy_default(self):
        if not self.operator_cloud._has_neutron_extension('qos-default'):
            self.skipTest(
                "'qos-default' network extension not supported by cloud"
            )
        policy = self.operator_cloud.create_qos_policy(
            name=self.policy_name, default=True
        )
        self.assertIn('id', policy)
        self.assertEqual(self.policy_name, policy['name'])
        self.assertFalse(policy['is_shared'])
        self.assertTrue(policy['is_default'])

    def test_update_qos_policy(self):
        policy = self.operator_cloud.create_qos_policy(name=self.policy_name)
        self.assertEqual(self.policy_name, policy['name'])
        self.assertFalse(policy['is_shared'])
        self.assertFalse(policy['is_default'])

        updated_policy = self.operator_cloud.update_qos_policy(
            policy['id'], shared=True, default=True
        )
        assert updated_policy is not None  # narrow type
        self.assertEqual(self.policy_name, updated_policy['name'])
        self.assertTrue(updated_policy['is_shared'])
        self.assertTrue(updated_policy['is_default'])

    def test_list_qos_policies_filtered(self):
        policy1 = self.operator_cloud.create_qos_policy(name=self.policy_name)
        self.assertIsNotNone(policy1)
        policy2 = self.operator_cloud.create_qos_policy(
            name=self.policy_name + 'other'
        )
        self.assertIsNotNone(policy2)
        match = self.operator_cloud.list_qos_policies(
            filters=dict(name=self.policy_name)
        )
        self.assertEqual(1, len(match))
        self.assertEqual(policy1['name'], match[0]['name'])


class TestQosBandwidthLimitRule(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')
        if not self.operator_cloud._has_neutron_extension('qos'):
            self.skipTest('QoS network extension not supported by cloud')

        policy_name = self.getUniqueString('qos_policy')
        self.policy = self.operator_cloud.create_qos_policy(name=policy_name)

        self.addCleanup(self._cleanup_qos_policy)

    def _cleanup_qos_policy(self):
        try:
            self.operator_cloud.delete_qos_policy(self.policy['id'])
        except Exception as e:
            raise exceptions.SDKException(str(e))

    def test_qos_bandwidth_limit_rule_lifecycle(self):
        max_kbps = 1500
        max_burst_kbps = 500
        updated_max_kbps = 2000

        # Create bw limit rule
        rule = self.operator_cloud.create_qos_bandwidth_limit_rule(
            self.policy['id'], max_kbps=max_kbps, max_burst_kbps=max_burst_kbps
        )
        self.assertIn('id', rule)
        self.assertEqual(max_kbps, rule['max_kbps'])
        self.assertEqual(max_burst_kbps, rule['max_burst_kbps'])

        # Now try to update rule
        updated_rule = self.operator_cloud.update_qos_bandwidth_limit_rule(
            self.policy['id'], rule['id'], max_kbps=updated_max_kbps
        )
        assert updated_rule is not None  # narrow type
        self.assertIn('id', updated_rule)
        self.assertEqual(updated_max_kbps, updated_rule['max_kbps'])
        self.assertEqual(max_burst_kbps, updated_rule['max_burst_kbps'])

        # List rules from policy
        policy_rules = self.operator_cloud.list_qos_bandwidth_limit_rules(
            self.policy['id']
        )
        self.assertEqual([updated_rule], policy_rules)

        # Delete rule
        self.operator_cloud.delete_qos_bandwidth_limit_rule(
            self.policy['id'], updated_rule['id']
        )

        # Check if there is no rules in policy
        policy_rules = self.operator_cloud.list_qos_bandwidth_limit_rules(
            self.policy['id']
        )
        self.assertEqual([], policy_rules)

    def test_create_qos_bandwidth_limit_rule_direction(self):
        if not self.operator_cloud._has_neutron_extension(
            'qos-bw-limit-direction'
        ):
            self.skipTest(
                "'qos-bw-limit-direction' network extension "
                "not supported by cloud"
            )
        max_kbps = 1500
        direction = "ingress"
        updated_direction = "egress"

        # Create bw limit rule
        rule = self.operator_cloud.create_qos_bandwidth_limit_rule(
            self.policy['id'], max_kbps=max_kbps, direction=direction
        )
        self.assertIn('id', rule)
        self.assertEqual(max_kbps, rule['max_kbps'])
        self.assertEqual(direction, rule['direction'])

        # Now try to update direction in rule
        updated_rule = self.operator_cloud.update_qos_bandwidth_limit_rule(
            self.policy['id'], rule['id'], direction=updated_direction
        )
        assert updated_rule is not None  # narrow type
        self.assertIn('id', updated_rule)
        self.assertEqual(max_kbps, updated_rule['max_kbps'])
        self.assertEqual(updated_direction, updated_rule['direction'])


class TestQosDscpMarkingRule(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')
        if not self.operator_cloud._has_neutron_extension('qos'):
            self.skipTest('QoS network extension not supported by cloud')

        policy_name = self.getUniqueString('qos_policy')
        self.policy = self.operator_cloud.create_qos_policy(name=policy_name)

        self.addCleanup(self._cleanup_qos_policy)

    def _cleanup_qos_policy(self):
        try:
            self.operator_cloud.delete_qos_policy(self.policy['id'])
        except Exception as e:
            raise exceptions.SDKException(str(e))

    def test_qos_dscp_marking_rule_lifecycle(self):
        dscp_mark = 16
        updated_dscp_mark = 32

        # Create DSCP marking rule
        rule = self.operator_cloud.create_qos_dscp_marking_rule(
            self.policy['id'], dscp_mark=dscp_mark
        )
        self.assertIn('id', rule)
        self.assertEqual(dscp_mark, rule['dscp_mark'])

        # Now try to update rule
        updated_rule = self.operator_cloud.update_qos_dscp_marking_rule(
            self.policy['id'], rule['id'], dscp_mark=updated_dscp_mark
        )
        assert updated_rule is not None  # narrow type
        self.assertIn('id', updated_rule)
        self.assertEqual(updated_dscp_mark, updated_rule['dscp_mark'])

        # List rules from policy
        policy_rules = self.operator_cloud.list_qos_dscp_marking_rules(
            self.policy['id']
        )
        self.assertEqual([updated_rule], policy_rules)

        # Delete rule
        self.operator_cloud.delete_qos_dscp_marking_rule(
            self.policy['id'], updated_rule['id']
        )

        # Check if there is no rules in policy
        policy_rules = self.operator_cloud.list_qos_dscp_marking_rules(
            self.policy['id']
        )
        self.assertEqual([], policy_rules)


class TestQosMinimumBandwidthRule(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')
        if not self.operator_cloud._has_neutron_extension('qos'):
            self.skipTest('QoS network extension not supported by cloud')

        policy_name = self.getUniqueString('qos_policy')
        self.policy = self.operator_cloud.create_qos_policy(name=policy_name)

        self.addCleanup(self._cleanup_qos_policy)

    def _cleanup_qos_policy(self):
        try:
            self.operator_cloud.delete_qos_policy(self.policy['id'])
        except Exception as e:
            raise exceptions.SDKException(str(e))

    def test_qos_minimum_bandwidth_rule_lifecycle(self):
        min_kbps = 1500
        updated_min_kbps = 2000

        # Create min bw rule
        rule = self.operator_cloud.create_qos_minimum_bandwidth_rule(
            self.policy['id'], min_kbps=min_kbps
        )
        self.assertIn('id', rule)
        self.assertEqual(min_kbps, rule['min_kbps'])

        # Now try to update rule
        updated_rule = self.operator_cloud.update_qos_minimum_bandwidth_rule(
            self.policy['id'], rule['id'], min_kbps=updated_min_kbps
        )
        assert updated_rule is not None  # narrow type
        self.assertIn('id', updated_rule)
        self.assertEqual(updated_min_kbps, updated_rule['min_kbps'])

        # List rules from policy
        policy_rules = self.operator_cloud.list_qos_minimum_bandwidth_rules(
            self.policy['id']
        )
        self.assertEqual([updated_rule], policy_rules)

        # Delete rule
        self.operator_cloud.delete_qos_minimum_bandwidth_rule(
            self.policy['id'], updated_rule['id']
        )

        # Check if there is no rules in policy
        policy_rules = self.operator_cloud.list_qos_minimum_bandwidth_rules(
            self.policy['id']
        )
        self.assertEqual([], policy_rules)


class TestNetworkQuotas(base.BaseFunctionalTest):
    def test_get_quotas(self):
        '''Test get quotas functionality'''
        project_id = self.user_cloud.current_project_id
        assert project_id is not None  # narrow type
        self.user_cloud.get_network_quotas(project_id)

    def test_quotas(self):
        '''Test quotas functionality'''
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('network service not supported by cloud')

        quotas = self.operator_cloud.get_network_quotas('demo')
        network = quotas['networks']
        self.operator_cloud.set_network_quotas('demo', networks=network + 1)
        self.assertEqual(
            network + 1,
            self.operator_cloud.get_network_quotas('demo')['networks'],
        )
        self.operator_cloud.delete_network_quotas('demo')
        self.assertEqual(
            network, self.operator_cloud.get_network_quotas('demo')['networks']
        )

    def test_get_quotas_details(self):
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('network service not supported by cloud')

        quotas = [
            'floating_ips',
            'networks',
            'ports',
            'rbac_policies',
            'routers',
            'subnets',
            'subnet_pools',
            'security_group_rules',
            'security_groups',
        ]
        expected_keys = ['limit', 'used', 'reserved']
        '''Test getting details about quota usage'''
        quota_details = self.operator_cloud.get_network_quotas(
            'demo', details=True
        )
        for quota in quotas:
            quota_val = quota_details[quota]
            if quota_val:
                for expected_key in expected_keys:
                    self.assertIn(expected_key, quota_val)
