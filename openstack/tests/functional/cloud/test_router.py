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

"""
test_router
----------------------------------

Functional tests for `shade` router methods.
"""

import ipaddress

from openstack.cloud.exc import OpenStackCloudException
from openstack.tests.functional.cloud import base


EXPECTED_TOPLEVEL_FIELDS = (
    'id', 'name', 'admin_state_up', 'external_gateway_info',
    'tenant_id', 'routes', 'status'
)

EXPECTED_GW_INFO_FIELDS = ('network_id', 'enable_snat', 'external_fixed_ips')


class TestRouter(base.BaseFunctionalTestCase):
    def setUp(self):
        super(TestRouter, self).setUp()
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
            raise OpenStackCloudException('\n'.join(exception_list))

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
            raise OpenStackCloudException('\n'.join(exception_list))

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
            raise OpenStackCloudException('\n'.join(exception_list))

    def test_create_router_basic(self):
        net1_name = self.network_prefix + '_net1'
        net1 = self.operator_cloud.create_network(
            name=net1_name, external=True)

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
        proj_id = project['id']
        net1_name = self.network_prefix + '_net1'
        net1 = self.operator_cloud.create_network(
            name=net1_name, external=True, project_id=proj_id)

        router_name = self.router_prefix + '_create_project'
        router = self.operator_cloud.create_router(
            name=router_name,
            admin_state_up=True,
            ext_gateway_net_id=net1['id'],
            project_id=proj_id
        )

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, router)

        ext_gw_info = router['external_gateway_info']
        for field in EXPECTED_GW_INFO_FIELDS:
            self.assertIn(field, ext_gw_info)

        self.assertEqual(router_name, router['name'])
        self.assertEqual('ACTIVE', router['status'])
        self.assertEqual(proj_id, router['tenant_id'])
        self.assertEqual(net1['id'], ext_gw_info['network_id'])
        self.assertTrue(ext_gw_info['enable_snat'])

    def _create_and_verify_advanced_router(self,
                                           external_cidr,
                                           external_gateway_ip=None):
        # external_cidr must be passed in as unicode (u'')
        # NOTE(Shrews): The arguments are needed because these tests
        # will run in parallel and we want to make sure that each test
        # is using different resources to prevent race conditions.
        net1_name = self.network_prefix + '_net1'
        sub1_name = self.subnet_prefix + '_sub1'
        net1 = self.operator_cloud.create_network(
            name=net1_name, external=True)
        sub1 = self.operator_cloud.create_subnet(
            net1['id'], external_cidr, subnet_name=sub1_name,
            gateway_ip=external_gateway_ip
        )

        ip_net = ipaddress.IPv4Network(external_cidr)
        last_ip = str(list(ip_net.hosts())[-1])

        router_name = self.router_prefix + '_create_advanced'
        router = self.operator_cloud.create_router(
            name=router_name,
            admin_state_up=False,
            ext_gateway_net_id=net1['id'],
            enable_snat=False,
            ext_fixed_ips=[
                {'subnet_id': sub1['id'], 'ip_address': last_ip}
            ]
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
            sub1['id'],
            ext_gw_info['external_fixed_ips'][0]['subnet_id']
        )
        self.assertEqual(
            last_ip,
            ext_gw_info['external_fixed_ips'][0]['ip_address']
        )

        return router

    def test_create_router_advanced(self):
        self._create_and_verify_advanced_router(external_cidr=u'10.2.2.0/24')

    def test_add_remove_router_interface(self):
        router = self._create_and_verify_advanced_router(
            external_cidr=u'10.3.3.0/24')
        net_name = self.network_prefix + '_intnet1'
        sub_name = self.subnet_prefix + '_intsub1'
        net = self.operator_cloud.create_network(name=net_name)
        sub = self.operator_cloud.create_subnet(
            net['id'], '10.4.4.0/24', subnet_name=sub_name,
            gateway_ip='10.4.4.1'
        )

        iface = self.operator_cloud.add_router_interface(
            router, subnet_id=sub['id'])
        self.assertIsNone(
            self.operator_cloud.remove_router_interface(
                router, subnet_id=sub['id'])
        )

        # Test return values *after* the interface is detached so the
        # resources we've created can be cleaned up if these asserts fail.
        self.assertIsNotNone(iface)
        for key in ('id', 'subnet_id', 'port_id', 'tenant_id'):
            self.assertIn(key, iface)
        self.assertEqual(router['id'], iface['id'])
        self.assertEqual(sub['id'], iface['subnet_id'])

    def test_list_router_interfaces(self):
        router = self._create_and_verify_advanced_router(
            external_cidr=u'10.5.5.0/24')
        net_name = self.network_prefix + '_intnet1'
        sub_name = self.subnet_prefix + '_intsub1'
        net = self.operator_cloud.create_network(name=net_name)
        sub = self.operator_cloud.create_subnet(
            net['id'], '10.6.6.0/24', subnet_name=sub_name,
            gateway_ip='10.6.6.1'
        )

        iface = self.operator_cloud.add_router_interface(
            router, subnet_id=sub['id'])
        all_ifaces = self.operator_cloud.list_router_interfaces(router)
        int_ifaces = self.operator_cloud.list_router_interfaces(
            router, interface_type='internal')
        ext_ifaces = self.operator_cloud.list_router_interfaces(
            router, interface_type='external')
        self.assertIsNone(
            self.operator_cloud.remove_router_interface(
                router, subnet_id=sub['id'])
        )

        # Test return values *after* the interface is detached so the
        # resources we've created can be cleaned up if these asserts fail.
        self.assertIsNotNone(iface)
        self.assertEqual(2, len(all_ifaces))
        self.assertEqual(1, len(int_ifaces))
        self.assertEqual(1, len(ext_ifaces))

        ext_fixed_ips = router['external_gateway_info']['external_fixed_ips']
        self.assertEqual(ext_fixed_ips[0]['subnet_id'],
                         ext_ifaces[0]['fixed_ips'][0]['subnet_id'])
        self.assertEqual(sub['id'], int_ifaces[0]['fixed_ips'][0]['subnet_id'])

    def test_update_router_name(self):
        router = self._create_and_verify_advanced_router(
            external_cidr=u'10.7.7.0/24')

        new_name = self.router_prefix + '_update_name'
        updated = self.operator_cloud.update_router(
            router['id'], name=new_name)
        self.assertIsNotNone(updated)

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, updated)

        # Name is the only change we expect
        self.assertEqual(new_name, updated['name'])

        # Validate nothing else changed
        self.assertEqual(router['status'], updated['status'])
        self.assertEqual(router['admin_state_up'], updated['admin_state_up'])
        self.assertEqual(router['external_gateway_info'],
                         updated['external_gateway_info'])

    def test_update_router_admin_state(self):
        router = self._create_and_verify_advanced_router(
            external_cidr=u'10.8.8.0/24')

        updated = self.operator_cloud.update_router(
            router['id'], admin_state_up=True)
        self.assertIsNotNone(updated)

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, updated)

        # admin_state_up is the only change we expect
        self.assertTrue(updated['admin_state_up'])
        self.assertNotEqual(router['admin_state_up'],
                            updated['admin_state_up'])

        # Validate nothing else changed
        self.assertEqual(router['status'], updated['status'])
        self.assertEqual(router['name'], updated['name'])
        self.assertEqual(router['external_gateway_info'],
                         updated['external_gateway_info'])

    def test_update_router_ext_gw_info(self):
        router = self._create_and_verify_advanced_router(
            external_cidr=u'10.9.9.0/24')

        # create a new subnet
        existing_net_id = router['external_gateway_info']['network_id']
        sub_name = self.subnet_prefix + '_update'
        sub = self.operator_cloud.create_subnet(
            existing_net_id, '10.10.10.0/24', subnet_name=sub_name,
            gateway_ip='10.10.10.1'
        )

        updated = self.operator_cloud.update_router(
            router['id'],
            ext_gateway_net_id=existing_net_id,
            ext_fixed_ips=[
                {'subnet_id': sub['id'], 'ip_address': '10.10.10.77'}
            ]
        )
        self.assertIsNotNone(updated)

        for field in EXPECTED_TOPLEVEL_FIELDS:
            self.assertIn(field, updated)

        # external_gateway_info is the only change we expect
        ext_gw_info = updated['external_gateway_info']
        self.assertEqual(1, len(ext_gw_info['external_fixed_ips']))
        self.assertEqual(
            sub['id'],
            ext_gw_info['external_fixed_ips'][0]['subnet_id']
        )
        self.assertEqual(
            '10.10.10.77',
            ext_gw_info['external_fixed_ips'][0]['ip_address']
        )

        # Validate nothing else changed
        self.assertEqual(router['status'], updated['status'])
        self.assertEqual(router['name'], updated['name'])
        self.assertEqual(router['admin_state_up'], updated['admin_state_up'])
