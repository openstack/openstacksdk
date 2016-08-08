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

from openstack.orchestration.v1 import software_deployment

FAKE = {
    'id': 'ce8ae86c-9810-4cb1-8888-7fb53bc523bf',
    'action': 'CREATE',
    'config_id': 'CONFIG ID',
    'creation_time': '2015-03-09T12:15:57',
    'server_id': 'FAKE_SERVER',
    'stack_user_project_id': 'ANOTHER PROJECT',
    'status': 'IN_PROGRESS',
    'status_reason': 'Why are we here?',
    'input_values': {'foo': 'bar'},
    'output_values': {'baz': 'zoo'},
    'updated_time': '2015-03-09T12:15:57',
}


class TestSoftwareDeployment(testtools.TestCase):

    def test_basic(self):
        sot = software_deployment.SoftwareDeployment()
        self.assertEqual('software_deployment', sot.resource_key)
        self.assertEqual('software_deployments', sot.resources_key)
        self.assertEqual('/software_deployments', sot.base_path)
        self.assertEqual('orchestration', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = software_deployment.SoftwareDeployment(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['action'], sot.action)
        self.assertEqual(FAKE['config_id'], sot.config_id)
        self.assertEqual(FAKE['creation_time'], sot.created_at)
        self.assertEqual(FAKE['server_id'], sot.server_id)
        self.assertEqual(FAKE['stack_user_project_id'],
                         sot.stack_user_project_id)
        self.assertEqual(FAKE['input_values'], sot.input_values)
        self.assertEqual(FAKE['output_values'], sot.output_values)
        self.assertEqual(FAKE['status'], sot.status)
        self.assertEqual(FAKE['status_reason'], sot.status_reason)
        self.assertEqual(FAKE['updated_time'], sot.updated_at)
