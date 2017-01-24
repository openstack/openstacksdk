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

from openstack.workflow.v2 import workflow


FAKE = {
    'scope': 'private',
    'id': 'ffaed25e-46f5-4089-8e20-b3b4722fd597',
    'definition': 'workflow_def',
}


class TestWorkflow(testtools.TestCase):

    def setUp(self):
        super(TestWorkflow, self).setUp()

    def test_basic(self):
        sot = workflow.Workflow()
        self.assertEqual('workflow', sot.resource_key)
        self.assertEqual('workflows', sot.resources_key)
        self.assertEqual('/workflows', sot.base_path)
        self.assertEqual('workflowv2', sot.service.service_type)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)

    def test_instantiate(self):
        sot = workflow.Workflow(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['scope'], sot.scope)
        self.assertEqual(FAKE['definition'], sot.definition)
