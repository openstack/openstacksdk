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

from openstack.orchestration.v1 import stack_template


FAKE = {
    'description': 'template description',
    'heat_template_version': '2014-10-16',
    'parameters': {
        'key_name': {
            'type': 'string'
        }
    },
    'resources': {
        'resource1': {
            'type': 'ResourceType'
        }
    },
    'outputs': {
        'key1': 'value1'
    }
}


class TestStackTemplate(testtools.TestCase):

    def test_basic(self):
        sot = stack_template.StackTemplate()
        self.assertEqual('orchestration', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = stack_template.StackTemplate(**FAKE)
        self.assertEqual(FAKE['description'], sot.description)
        self.assertEqual(FAKE['heat_template_version'],
                         sot.heat_template_version)
        self.assertEqual(FAKE['outputs'], sot.outputs)
        self.assertEqual(FAKE['parameters'], sot.parameters)
        self.assertEqual(FAKE['resources'], sot.resources)
