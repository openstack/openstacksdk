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

from openstack.identity.v3 import limit as _limit
from openstack.tests.functional import base


class TestLimit(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.service_name = self.getUniqueString('service')
        self.service_type = self.getUniqueString('type')
        self.service = self.system_admin_cloud.identity.create_service(
            name=self.service_name,
            type=self.service_type,
        )
        self.addCleanup(
            self.system_admin_cloud.identity.delete_service, self.service
        )

        self.resource_name = self.getUniqueString('resource')
        self.registered_limit = (
            self.system_admin_cloud.identity.create_registered_limit(
                resource_name=self.resource_name,
                service_id=self.service.id,
                default_limit=10,
            )
        )
        self.addCleanup(
            self.system_admin_cloud.identity.delete_registered_limit,
            self.registered_limit,
        )

        self.project_name = self.getUniqueString('project')
        self.project = self.system_admin_cloud.identity.create_project(
            name=self.project_name,
        )
        self.addCleanup(
            self.system_admin_cloud.identity.delete_project, self.project
        )

        self.limit_description = self.getUniqueString('limit')

    def _delete_limit(self, limit):
        ret = self.system_admin_cloud.identity.delete_limit(limit)
        self.assertIsNone(ret)

    def test_limit(self):
        # create the limit

        limit = self.system_admin_cloud.identity.create_limit(
            resource_name=self.resource_name,
            service_id=self.service.id,
            project_id=self.project.id,
            resource_limit=50,
        )
        self.addCleanup(self._delete_limit, limit)
        self.assertIsInstance(limit, _limit.Limit)
        self.assertIsNotNone(limit.id)
        self.assertIsNone(limit.description)
        self.assertEqual(self.service.id, limit.service_id)
        self.assertEqual(self.project.id, limit.project_id)
        self.assertEqual(50, limit.resource_limit)

        # update the limit

        limit = self.system_admin_cloud.identity.update_limit(
            limit, description=self.limit_description
        )
        self.assertIsInstance(limit, _limit.Limit)
        self.assertEqual(self.limit_description, limit.description)

        # retrieve details of the (updated) limit by ID

        limit = self.system_admin_cloud.identity.get_limit(limit.id)
        self.assertIsInstance(limit, _limit.Limit)
        self.assertEqual(self.limit_description, limit.description)

        # (there's no name, so no way to retrieve by name)

        # list all limits

        limits = list(self.system_admin_cloud.identity.limits())
        self.assertIsInstance(limits[0], _limit.Limit)
        self.assertIn(
            self.resource_name,
            {x.resource_name for x in limits},
        )
