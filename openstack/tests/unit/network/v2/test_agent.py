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

import mock
import testtools

from openstack.network.v2 import agent

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'agent_type': 'Test Agent',
    'alive': True,
    'availability_zone': 'az1',
    'binary': 'test-binary',
    'configurations': {'attr1': 'value1', 'attr2': 'value2'},
    'created_at': '2016-03-09T12:14:57.233772',
    'description': 'test description',
    'heartbeat_timestamp': '2016-08-09T12:14:57.233772',
    'host': 'test-host',
    'id': IDENTIFIER,
    'started_at': '2016-07-09T12:14:57.233772',
    'topic': 'test-topic'
}


class TestAgent(testtools.TestCase):

    def test_basic(self):
        sot = agent.Agent()
        self.assertEqual('agent', sot.resource_key)
        self.assertEqual('agents', sot.resources_key)
        self.assertEqual('/agents', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = agent.Agent(**EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['agent_type'], sot.agent_type)
        self.assertTrue(sot.is_alive)
        self.assertEqual(EXAMPLE['availability_zone'],
                         sot.availability_zone)
        self.assertEqual(EXAMPLE['binary'], sot.binary)
        self.assertEqual(EXAMPLE['configurations'], sot.configuration)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['heartbeat_timestamp'], sot.last_heartbeat_at)
        self.assertEqual(EXAMPLE['host'], sot.host)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['started_at'], sot.started_at)
        self.assertEqual(EXAMPLE['topic'], sot.topic)

    def test_add_agent_to_network(self):
        # Add agent to network
        net = agent.Agent(**EXAMPLE)
        response = mock.Mock()
        response.body = {'network_id': '1'}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)
        body = {'network_id': '1'}
        self.assertEqual(response.body, net.add_agent_to_network(sess, **body))

        url = 'agents/IDENTIFIER/dhcp-networks'
        sess.post.assert_called_with(url, endpoint_filter=net.service,
                                     json=body)

    def test_remove_agent_from_network(self):
        # Remove agent from agent
        net = agent.Agent(**EXAMPLE)
        sess = mock.Mock()
        self.assertIsNone(net.remove_agent_from_network(sess))
        body = {}

        sess.delete.assert_called_with('agents/IDENTIFIER/dhcp-networks/',
                                       endpoint_filter=net.service, json=body)


class TestDHCPAgentHostingNetwork(testtools.TestCase):

    def test_basic(self):
        net = agent.DHCPAgentHostingNetwork()
        self.assertEqual('network', net.resource_key)
        self.assertEqual('networks', net.resources_key)
        self.assertEqual('/agents/%(agent_id)s/dhcp-networks', net.base_path)
        self.assertEqual('dhcp-network', net.resource_name)
        self.assertEqual('network', net.service.service_type)
        self.assertFalse(net.allow_create)
        self.assertTrue(net.allow_get)
        self.assertFalse(net.allow_update)
        self.assertFalse(net.allow_delete)
        self.assertTrue(net.allow_list)
