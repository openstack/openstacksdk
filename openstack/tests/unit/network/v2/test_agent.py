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
from openstack.tests.unit import base

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
    'resources_synced': False,
    'started_at': '2016-07-09T12:14:57.233772',
    'topic': 'test-topic',
    'ha_state': 'active'
}


class TestAgent(base.TestCase):

    def test_basic(self):
        sot = agent.Agent()
        self.assertEqual('agent', sot.resource_key)
        self.assertEqual('agents', sot.resources_key)
        self.assertEqual('/agents', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
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
        self.assertEqual(EXAMPLE['resources_synced'], sot.resources_synced)
        self.assertEqual(EXAMPLE['started_at'], sot.started_at)
        self.assertEqual(EXAMPLE['topic'], sot.topic)
        self.assertEqual(EXAMPLE['ha_state'], sot.ha_state)

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
        sess.post.assert_called_with(url,
                                     json=body)

    def test_remove_agent_from_network(self):
        # Remove agent from agent
        net = agent.Agent(**EXAMPLE)
        sess = mock.Mock()
        network_id = {}
        self.assertIsNone(net.remove_agent_from_network(sess, network_id))
        body = {'network_id': {}}

        sess.delete.assert_called_with('agents/IDENTIFIER/dhcp-networks/',
                                       json=body)

    def test_add_router_to_agent(self):
        # Add router to agent
        sot = agent.Agent(**EXAMPLE)
        response = mock.Mock()
        response.body = {'router_id': '1'}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)
        router_id = '1'
        self.assertEqual(response.body,
                         sot.add_router_to_agent(sess, router_id))
        body = {'router_id': router_id}
        url = 'agents/IDENTIFIER/l3-routers'
        sess.post.assert_called_with(url,
                                     json=body)

    def test_remove_router_from_agent(self):
        # Remove router from agent
        sot = agent.Agent(**EXAMPLE)
        sess = mock.Mock()
        router_id = {}
        self.assertIsNone(sot.remove_router_from_agent(sess, router_id))
        body = {'router_id': {}}

        sess.delete.assert_called_with('agents/IDENTIFIER/l3-routers/',
                                       json=body)


class TestNetworkHostingDHCPAgent(base.TestCase):

    def test_basic(self):
        net = agent.NetworkHostingDHCPAgent()
        self.assertEqual('agent', net.resource_key)
        self.assertEqual('agents', net.resources_key)
        self.assertEqual('/networks/%(network_id)s/dhcp-agents', net.base_path)
        self.assertEqual('dhcp-agent', net.resource_name)
        self.assertFalse(net.allow_create)
        self.assertTrue(net.allow_fetch)
        self.assertFalse(net.allow_commit)
        self.assertFalse(net.allow_delete)
        self.assertTrue(net.allow_list)


class TestRouterL3Agent(base.TestCase):

    def test_basic(self):
        sot = agent.RouterL3Agent()
        self.assertEqual('agent', sot.resource_key)
        self.assertEqual('agents', sot.resources_key)
        self.assertEqual('/routers/%(router_id)s/l3-agents', sot.base_path)
        self.assertEqual('l3-agent', sot.resource_name)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)
