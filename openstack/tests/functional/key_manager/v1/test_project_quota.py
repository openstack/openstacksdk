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

from openstack import exceptions as sdk_exc
from openstack.key_manager.v1 import project_quota as _project_quota
from openstack.tests.functional import base

# NOTE(jbeen): Barbican policy may require 'key-manager:service-admin' for
# project quotas. Create and assign it per test project to avoid 403 errors.
ADMIN_ROLE_NAME = 'key-manager:service-admin'


class TestProjectQuota(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('key-manager')

        self.project_name = self.getUniqueString('project')
        self.project = self.system_admin_cloud.identity.create_project(
            name=self.project_name,
        )
        self.addCleanup(
            self.system_admin_cloud.identity.delete_project, self.project
        )

        self.role = self.system_admin_cloud.identity.create_role(
            name=ADMIN_ROLE_NAME
        )
        self.addCleanup(
            self.system_admin_cloud.identity.delete_role, self.role.id
        )

        self.user_id = self.system_admin_cloud.current_user_id
        self.system_admin_cloud.identity.assign_project_role_to_user(
            project=self.project, user=self.user_id, role=self.role
        )
        self.addCleanup(
            self.system_admin_cloud.identity.unassign_project_role_from_user,
            project=self.project,
            user=self.user_id,
            role=self.role,
        )

        self._set_operator_cloud(project_id=self.project.id)

    def test_project_quotas(self):
        # update project quota
        project_quota = self.operator_cloud.key_manager.update_project_quota(
            self.project.id,
            secrets=1,
            orders=2,
            containers=3,
            consumers=4,
            cas=5,
        )

        self.assertIsInstance(project_quota, _project_quota.ProjectQuota)
        self.assertIsNotNone(project_quota.id)
        self.assertEqual(1, project_quota.secrets)
        self.assertEqual(2, project_quota.orders)
        self.assertEqual(3, project_quota.containers)
        self.assertEqual(4, project_quota.consumers)
        self.assertEqual(5, project_quota.cas)

        # get project quota
        project_id = self.project.id
        project_quota = self.operator_cloud.key_manager.get_project_quota(
            project_id
        )
        self.assertIsInstance(project_quota, _project_quota.ProjectQuota)

        # delete project quota
        self.operator_cloud.key_manager.delete_project_quota(project_quota)
        self.assertRaises(
            sdk_exc.NotFoundException,
            self.operator_cloud.key_manager.get_project_quota,
            project_quota,
        )
