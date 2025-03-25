# Copyright (c) 2016 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_project
----------------------------------

Functional tests for project resource.
"""

import pprint

from openstack import exceptions
from openstack.tests.functional import base


class TestProject(base.KeystoneBaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        self.new_project_name = self.getUniqueString('project')
        self.addCleanup(self._cleanup_projects)

    def _cleanup_projects(self):
        exception_list = list()
        for p in self.operator_cloud.list_projects():
            if p['name'].startswith(self.new_project_name):
                try:
                    self.operator_cloud.delete_project(p['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue
        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_project(self):
        project_name = self.new_project_name + '_create'

        params = {
            'name': project_name,
            'description': 'test_create_project',
            'domain_id': self.operator_cloud.get_domain('default')['id'],
        }

        project = self.operator_cloud.create_project(**params)

        self.assertIsNotNone(project)
        self.assertEqual(project_name, project['name'])
        self.assertEqual('test_create_project', project['description'])

        user_id = self.operator_cloud.current_user_id

        # Grant the current user access to the project
        self.assertTrue(
            self.operator_cloud.grant_role(
                'member', user=user_id, project=project['id'], wait=True
            )
        )
        self.addCleanup(
            self.operator_cloud.revoke_role,
            'member',
            user=user_id,
            project=project['id'],
            wait=True,
        )

        new_cloud = self.operator_cloud.connect_as_project(project)
        self.add_info_on_exception(
            'new_cloud_config', pprint.pformat(new_cloud.config.config)
        )
        location = new_cloud.current_location
        self.assertEqual(project_name, location['project']['name'])

    def test_update_project(self):
        project_name = self.new_project_name + '_update'

        params = {
            'name': project_name,
            'description': 'test_update_project',
            'enabled': True,
            'domain_id': self.operator_cloud.get_domain('default')['id'],
        }

        project = self.operator_cloud.create_project(**params)
        updated_project = self.operator_cloud.update_project(
            project_name, enabled=False, description='new'
        )
        self.assertIsNotNone(updated_project)
        self.assertEqual(project['id'], updated_project['id'])
        self.assertEqual(project['name'], updated_project['name'])
        self.assertEqual(updated_project['description'], 'new')
        self.assertTrue(project['enabled'])
        self.assertFalse(updated_project['enabled'])

        # Revert the description and verify the project is still disabled
        updated_project = self.operator_cloud.update_project(
            project_name, description=params['description']
        )
        self.assertIsNotNone(updated_project)
        self.assertEqual(project['id'], updated_project['id'])
        self.assertEqual(project['name'], updated_project['name'])
        self.assertEqual(
            project['description'], updated_project['description']
        )
        self.assertTrue(project['enabled'])
        self.assertFalse(updated_project['enabled'])

    def test_delete_project(self):
        project_name = self.new_project_name + '_delete'
        params = {
            'name': project_name,
            'domain_id': self.operator_cloud.get_domain('default')['id'],
        }
        project = self.operator_cloud.create_project(**params)
        self.assertIsNotNone(project)
        self.assertTrue(self.operator_cloud.delete_project(project['id']))

    def test_delete_project_not_found(self):
        self.assertFalse(self.operator_cloud.delete_project('doesNotExist'))
