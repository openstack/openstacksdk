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

import datetime

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
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = agent.Agent(EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['agent_type'], sot.agent_type)
        self.assertTrue(sot.is_alive)
        self.assertEqual(EXAMPLE['availability_zone'],
                         sot.availability_zone)
        self.assertEqual(EXAMPLE['binary'], sot.binary)
        self.assertEqual(EXAMPLE['configurations'], sot.configuration)
        dt = datetime.datetime(2016, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['description'], sot.description)
        dt = datetime.datetime(2016, 8, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt,
                         sot.last_heartbeat_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['host'], sot.host)
        self.assertEqual(EXAMPLE['id'], sot.id)
        dt = datetime.datetime(2016, 7, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.started_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['topic'], sot.topic)
