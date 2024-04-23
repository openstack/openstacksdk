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
test_network
----------------------------------

Functional tests for network methods.
"""

from openstack import exceptions
from openstack.tests.functional import base


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
