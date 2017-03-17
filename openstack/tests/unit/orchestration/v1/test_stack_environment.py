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

from openstack.orchestration.v1 import stack_environment as se


FAKE = {
    'encrypted_param_names': ['n1', 'n2'],
    'event_sinks': {
        's1': 'v1'
    },
    'parameters': {
        'key_name': {
            'type': 'string'
        }
    },
    'parameter_defaults': {
        'p1': 'def1'
    },
    'resource_registry': {
        'resources': {
            'type1': 'type2'
        }
    },
}


class TestStackTemplate(testtools.TestCase):

    def test_basic(self):
        sot = se.StackEnvironment()
        self.assertEqual('orchestration', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = se.StackEnvironment(**FAKE)
        self.assertEqual(FAKE['encrypted_param_names'],
                         sot.encrypted_param_names)
        self.assertEqual(FAKE['event_sinks'], sot.event_sinks)
        self.assertEqual(FAKE['parameters'], sot.parameters)
        self.assertEqual(FAKE['parameter_defaults'], sot.parameter_defaults)
        self.assertEqual(FAKE['resource_registry'], sot.resource_registry)
