# -*- coding: utf-8 -*-

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

import random
import string

from shade import openstack_cloud
from shade.exc import OpenStackCloudException
from shade.tests import base


EXPECTED_TOPLEVEL_FIELDS = (
    'id', 'name', 'admin_state_up', 'external_gateway_info',
    'tenant_id', 'routes', 'status'
)

EXPECTED_GW_INFO_FIELDS = ('network_id', 'enable_snat', 'external_fixed_ips')


class TestRouter(base.TestCase):
    def setUp(self):
        super(TestRouter, self).setUp()
        self.cloud = openstack_cloud(cloud='devstack-admin')
        if not self.cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')

        self.router_prefix = 'test_router' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))
        self.network_prefix = 'test_network' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))
        self.subnet_prefix = 'test_subnet' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))

        # NOTE(Shrews): Order matters!
        self.addCleanup(self._cleanup_networks)
        self.addCleanup(self._cleanup_subnets)
        self.addCleanup(self._cleanup_routers)

    def _cleanup_routers(self):
        exception_list = list()
        for router in self.cloud.list_routers():
            if router['name'].startswith(self.router_prefix):
                try:
                    self.cloud.delete_router(router['name'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise OpenStackCloudException('\n'.join(exception_list))

    def _cleanup_networks(self):
        exception_list = list()
        for network in self.cloud.list_networks():
            if network['name'].startswith(self.network_prefix):
                try:
                    self.cloud.delete_network(network['name'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise OpenStackCloudException('\n'.join(exception_list))

    def _cleanup_subnets(self):
        exception_list = list()
        for subnet in self.cloud.list_subnets():
            if subnet['name'].startswith(self.subnet_prefix):
                try:
                    self.cloud.delete_subnet(subnet['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise OpenStackCloudException('\n'.join(exception_list))

    def test_create_router_basic(self):
        net1_name = self.network_prefix + '_net1'
        net1 = self.cloud.create_network(name=net1_name, external=True)

        router_name = self.router_prefix + '_create_basic'
        router = self.cloud.create_router(
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

    def _create_and_verify_advanced_router(self):
        net1_name = self.network_prefix + '_net1'
        sub1_name = self.subnet_prefix + '_sub1'
        net1 = self.cloud.create_network(name=net1_name, external=True)
        sub1 = self.cloud.create_subnet(
            net1['id'], '10.5.5.0/24', subnet_name=sub1_name,
            gateway_ip='10.5.5.1'
        )

        router_name = self.router_prefix + '_create_advanced'
        router = self.cloud.create_router(
            name=router_name,
            admin_state_up=False,
            ext_gateway_net_id=net1['id'],
            enable_snat=False,
            ext_fixed_ips=[
                {'subnet_id': sub1['id'], 'ip_address': '10.5.5.99'}
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
            '10.5.5.99',
            ext_gw_info['external_fixed_ips'][0]['ip_address']
        )

        return router

    def test_create_router_advanced(self):
        self._create_and_verify_advanced_router()

    def test_update_router_name(self):
        router = self._create_and_verify_advanced_router()

        new_name = self.router_prefix + '_update_name'
        updated = self.cloud.update_router(router['id'], name=new_name)
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
        router = self._create_and_verify_advanced_router()

        updated = self.cloud.update_router(router['id'],
                                           admin_state_up=True)
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
        router = self._create_and_verify_advanced_router()

        # create a new subnet
        existing_net_id = router['external_gateway_info']['network_id']
        sub_name = self.subnet_prefix + '_update'
        sub = self.cloud.create_subnet(
            existing_net_id, '10.6.6.0/24', subnet_name=sub_name,
            gateway_ip='10.6.6.1'
        )

        updated = self.cloud.update_router(
            router['id'],
            ext_gateway_net_id=existing_net_id,
            ext_fixed_ips=[
                {'subnet_id': sub['id'], 'ip_address': '10.6.6.77'}
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
            '10.6.6.77',
            ext_gw_info['external_fixed_ips'][0]['ip_address']
        )

        # Validate nothing else changed
        self.assertEqual(router['status'], updated['status'])
        self.assertEqual(router['name'], updated['name'])
        self.assertEqual(router['admin_state_up'], updated['admin_state_up'])
