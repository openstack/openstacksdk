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
import iso8601

import testtools

from openstack.cluster.v1 import action


FAKE_ID = '633bd3c6-520b-420f-8e6a-dc2a47022b53'
FAKE_NAME = 'node_create_c3783474'

FAKE = {
    'name': FAKE_NAME,
    'target': 'c378e474-d091-43a3-b083-e19719291358',
    'action': 'NODE_CREATE',
    'cause': 'RPC Request',
    'owner': None,
    'interval': -1,
    'start_time': 1453414055.48672,
    'end_time': 1453414055.48672,
    'timeout': 3600,
    'status': 'SUCCEEDED',
    'status_reason': 'Action completed successfully.',
    'inputs': {},
    'outputs': {},
    'depends_on': [],
    'depended_by': [],
    'created_at': '2015-10-10T12:46:36.000000',
    'updated_at': '2016-10-10T12:46:36.000000',
}


class TestAction(testtools.TestCase):

    def setUp(self):
        super(TestAction, self).setUp()

    def test_basic(self):
        sot = action.Action()
        self.assertEqual('action', sot.resource_key)
        self.assertEqual('actions', sot.resources_key)
        self.assertEqual('/actions', sot.base_path)
        self.assertEqual('clustering', sot.service.service_type)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = action.Action(FAKE)
        self.assertIsNone(sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['target'], sot.target_id)
        self.assertEqual(FAKE['action'], sot.action)
        self.assertEqual(FAKE['cause'], sot.cause)
        self.assertEqual(FAKE['owner'], sot.owner_id)
        self.assertEqual(FAKE['interval'], sot.interval)
        self.assertEqual(datetime.datetime(2016, 1, 21, 22, 7, 35, 486720,
                                           tzinfo=iso8601.UTC),
                         sot.start_at)
        self.assertEqual(datetime.datetime(2016, 1, 21, 22, 7, 35, 486720,
                                           tzinfo=iso8601.UTC),
                         sot.end_at)
        self.assertEqual(FAKE['timeout'], sot.timeout)
        self.assertEqual(FAKE['status'], sot.status)
        self.assertEqual(FAKE['status_reason'], sot.status_reason)
        self.assertEqual(FAKE['inputs'], sot.inputs)
        self.assertEqual(FAKE['outputs'], sot.outputs)
        self.assertEqual(FAKE['depends_on'], sot.depends_on)
        self.assertEqual(FAKE['depended_by'], sot.depended_by)
        dt = datetime.datetime(2015, 10, 10, 12, 46, 36, 000000).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
        dt = datetime.datetime(2016, 10, 10, 12, 46, 36, 000000).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))
