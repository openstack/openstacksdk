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

from openstack.identity.v3 import project as _project
from openstack.tests.functional import base


class TestProject(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.project_name = self.getUniqueString('project')
        self.project_description = self.getUniqueString('project')

    def _delete_project(self, project):
        ret = self.operator_cloud.identity.delete_project(project)
        self.assertIsNone(ret)

    def test_project(self):
        # create the project

        project = self.operator_cloud.identity.create_project(
            name=self.project_name,
        )
        self.assertIsInstance(project, _project.Project)
        self.assertEqual('', project.description)
        self.addCleanup(self._delete_project, project)

        # update the project

        project = self.operator_cloud.identity.update_project(
            project, description=self.project_description
        )
        self.assertIsInstance(project, _project.Project)
        self.assertEqual(self.project_description, project.description)

        # retrieve details of the (updated) project by ID

        project = self.operator_cloud.identity.get_project(project.id)
        self.assertIsInstance(project, _project.Project)
        self.assertEqual(self.project_description, project.description)

        # retrieve details of the (updated) project by name

        project = self.operator_cloud.identity.find_project(project.name)
        self.assertIsInstance(project, _project.Project)
        self.assertEqual(self.project_description, project.description)

        # list all projects

        projects = list(self.operator_cloud.identity.projects())
        self.assertIsInstance(projects[0], _project.Project)
        self.assertIn(
            self.project_name,
            {x.name for x in projects},
        )

    def test_user_project(self):
        # list all user projects

        user_projects = list(
            self.operator_cloud.identity.user_projects(
                self.operator_cloud.current_user_id
            )
        )
        self.assertIsInstance(user_projects[0], _project.UserProject)
        self.assertIn(
            self.operator_cloud.current_project_id,
            {x.id for x in user_projects},
        )
