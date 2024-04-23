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

from openstack.orchestration.v1 import stack_event
from openstack.tests.unit import base


FAKE_ID = 'ce8ae86c-9810-4cb1-8888-7fb53bc523bf'
FAKE_NAME = 'test_stack'
FAKE = {
    'event_time': '2015-03-09T12:15:57.233772',
    'id': FAKE_ID,
    'links': [{'href': f'stacks/{FAKE_NAME}/{FAKE_ID}', 'rel': 'self'}],
    'logical_resource_id': 'my_test_group',
    'physical_resource_id': 'my_test_group',
    'resource_name': 'my_test_resource',
    'resource_status': 'CREATE_IN_PROGRESS',
    'resource_status_reason': 'state changed',
}


class TestStackEvent(base.TestCase):
    def test_basic(self):
        sot = stack_event.StackEvent()
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = stack_event.StackEvent(**FAKE)
        self.assertEqual(FAKE['event_time'], sot.event_time)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['logical_resource_id'], sot.logical_resource_id)
        self.assertEqual(
            FAKE['physical_resource_id'], sot.physical_resource_id
        )
        self.assertEqual(FAKE['resource_name'], sot.resource_name)
        self.assertEqual(FAKE['resource_status'], sot.resource_status)
        self.assertEqual(
            FAKE['resource_status_reason'], sot.resource_status_reason
        )
