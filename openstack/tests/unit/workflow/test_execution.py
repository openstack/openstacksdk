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

from openstack.workflow.v2 import execution

FAKE_INPUT = {
    'cluster_id': '8c74607c-5a74-4490-9414-a3475b1926c2',
    'node_id': 'fba2cc5d-706f-4631-9577-3956048d13a2',
    'flavor_id': '1'
}

FAKE = {
    'id': 'ffaed25e-46f5-4089-8e20-b3b4722fd597',
    'workflow_name': 'cluster-coldmigration',
    'input': FAKE_INPUT,
}


class TestExecution(testtools.TestCase):

    def setUp(self):
        super(TestExecution, self).setUp()

    def test_basic(self):
        sot = execution.Execution()
        self.assertEqual('execution', sot.resource_key)
        self.assertEqual('executions', sot.resources_key)
        self.assertEqual('/executions', sot.base_path)
        self.assertEqual('workflowv2', sot.service.service_type)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)

    def test_instantiate(self):
        sot = execution.Execution(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['workflow_name'], sot.workflow_name)
        self.assertEqual(FAKE['input'], sot.input)
