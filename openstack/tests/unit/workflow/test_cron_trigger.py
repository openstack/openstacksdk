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

from openstack.tests.unit import base
from openstack.workflow.v2 import cron_trigger


FAKE_INPUT = {
    'cluster_id': '8c74607c-5a74-4490-9414-a3475b1926c2',
    'node_id': 'fba2cc5d-706f-4631-9577-3956048d13a2',
    'flavor_id': '1',
}

FAKE_PARAMS = {}

FAKE = {
    'id': 'ffaed25e-46f5-4089-8e20-b3b4722fd597',
    'pattern': '0 * * * *',
    'remaining_executions': 14,
    'first_execution_time': '1970-01-01T01:00:00.000000',
    'next_execution_time': '1970-01-01T02:00:00.000000',
    'workflow_name': 'cluster-coldmigration',
    'workflow_id': '1995cf40-c22d-4968-b6e8-558942830642',
    'workflow_input': FAKE_INPUT,
    'workflow_params': FAKE_PARAMS,
}


class TestCronTrigger(base.TestCase):
    def test_basic(self):
        sot = cron_trigger.CronTrigger()
        self.assertEqual('cron_trigger', sot.resource_key)
        self.assertEqual('cron_triggers', sot.resources_key)
        self.assertEqual('/cron_triggers', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)

        self.assertDictEqual(
            {
                'marker': 'marker',
                'limit': 'limit',
                'sort_keys': 'sort_keys',
                'sort_dirs': 'sort_dirs',
                'fields': 'fields',
                'name': 'name',
                'workflow_name': 'workflow_name',
                'workflow_id': 'workflow_id',
                'workflow_input': 'workflow_input',
                'workflow_params': 'workflow_params',
                'scope': 'scope',
                'pattern': 'pattern',
                'remaining_executions': 'remaining_executions',
                'project_id': 'project_id',
                'first_execution_time': 'first_execution_time',
                'next_execution_time': 'next_execution_time',
                'created_at': 'created_at',
                'updated_at': 'updated_at',
                'all_projects': 'all_projects',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = cron_trigger.CronTrigger(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['pattern'], sot.pattern)
        self.assertEqual(
            FAKE['remaining_executions'], sot.remaining_executions
        )
        self.assertEqual(
            FAKE['first_execution_time'], sot.first_execution_time
        )
        self.assertEqual(FAKE['next_execution_time'], sot.next_execution_time)
        self.assertEqual(FAKE['workflow_name'], sot.workflow_name)
        self.assertEqual(FAKE['workflow_id'], sot.workflow_id)
        self.assertEqual(FAKE['workflow_input'], sot.workflow_input)
        self.assertEqual(FAKE['workflow_params'], sot.workflow_params)
