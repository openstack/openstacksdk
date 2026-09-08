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
from openstack.identity.v3 import _proxy as _identity_v3
from openstack.key_manager.v1 import project_quota as _project_quota
from openstack.tests.functional import base


class TestProjectQuota(base.BaseFunctionalTest):
    _identity: _identity_v3.Proxy

    def setUp(self):
        super().setUp()
        self.require_service('key-manager')

        identity = self.system_admin_cloud.identity
        assert identity.api_version == '3'
        self._identity = identity

        self.project_name = self.getUniqueString('project')
        self.project = self._identity.create_project(
            name=self.project_name,
        )
        self.addCleanup(self._identity.delete_project, self.project)

        # Barbican's project_quotas:put policy requires role:admin in the
        # project scope. Assign the admin role to the operator user so
        # quota operations succeed against the test project.
        admin_role = self._identity.find_role('admin', ignore_missing=False)
        self.user_id = self.system_admin_cloud.current_user_id
        assert self.user_id is not None
        self._identity.assign_project_role_to_user(
            project=self.project, user=self.user_id, role=admin_role
        )
        self.addCleanup(
            self._identity.unassign_project_role_from_user,
            project=self.project,
            user=self.user_id,
            role=admin_role,
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
        self.operator_cloud.key_manager.delete_project_quota(self.project.id)
        self.assertRaises(
            sdk_exc.NotFoundException,
            self.operator_cloud.key_manager.get_project_quota,
            project_quota,
        )
