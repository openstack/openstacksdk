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

import testtools

from openstack.orchestration.v1 import stack

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'capabilities': '1',
    'creation_time': '2',
    'description': '3',
    'disable_rollback': True,
    'id': IDENTIFIER,
    'links': '6',
    'notification_topics': '7',
    'outputs': '8',
    'parameters': {'OS::stack_id': '9'},
    'stack_name': '10',
    'stack_status': '11',
    'stack_status_reason': '12',
    'template_description': '13',
    'timeout_mins': '14',
    'updated_time': '15',
}


class TestStack(testtools.TestCase):

    def test_basic(self):
        sot = stack.Stack()
        self.assertEqual('stack', sot.resource_key)
        self.assertEqual('stacks', sot.resources_key)
        self.assertEqual('/stacks', sot.base_path)
        self.assertEqual('orchestration', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = stack.Stack(EXAMPLE)
        self.assertEqual(EXAMPLE['capabilities'], sot.capabilities)
        self.assertEqual(EXAMPLE['creation_time'], sot.creation_time)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['disable_rollback'], sot.disable_rollback)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['notification_topics'],
                         sot.notification_topics)
        self.assertEqual(EXAMPLE['outputs'], sot.outputs)
        self.assertEqual(EXAMPLE['parameters'], sot.parameters)
        self.assertEqual(EXAMPLE['stack_name'], sot.name)
        self.assertEqual(EXAMPLE['stack_status'], sot.stack_status)
        self.assertEqual(EXAMPLE['stack_status_reason'],
                         sot.stack_status_reason)
        self.assertEqual(EXAMPLE['template_description'],
                         sot.template_description)
        self.assertEqual(EXAMPLE['timeout_mins'], sot.timeout_mins)
        self.assertEqual(EXAMPLE['updated_time'], sot.updated_time)
