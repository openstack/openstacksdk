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

from openstack.identity.v3 import registered_limit as _registered_limit
from openstack.tests.functional import base


class TestRegisteredLimit(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.region_name = self.getUniqueString('region')
        self.region = self.system_admin_cloud.identity.create_region(
            name=self.region_name
        )
        self.addCleanup(
            self.system_admin_cloud.identity.delete_region, self.region
        )

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
        self.registered_limit_description = self.getUniqueString(
            'registered_limit'
        )

    def _delete_registered_limit(self, registered_limit):
        ret = self.system_admin_cloud.identity.delete_registered_limit(
            registered_limit
        )
        self.assertIsNone(ret)

    def test_registered_limit(self):
        # create the registered limit

        registered_limit = (
            self.system_admin_cloud.identity.create_registered_limit(
                resource_name=self.resource_name,
                service_id=self.service.id,
                region_id=self.region.id,
                default_limit=10,
            )
        )
        self.addCleanup(self._delete_registered_limit, registered_limit)
        self.assertIsInstance(
            registered_limit, _registered_limit.RegisteredLimit
        )
        self.assertIsNotNone(registered_limit.id)
        self.assertIsNone(registered_limit.description)
        self.assertEqual(self.service.id, registered_limit.service_id)
        self.assertEqual(self.region.id, registered_limit.region_id)

        # update the registered limit

        registered_limit = (
            self.system_admin_cloud.identity.update_registered_limit(
                registered_limit, description=self.registered_limit_description
            )
        )
        self.assertIsInstance(
            registered_limit, _registered_limit.RegisteredLimit
        )
        self.assertEqual(
            self.registered_limit_description, registered_limit.description
        )

        # retrieve details of the (updated) registered limit by ID

        registered_limit = (
            self.system_admin_cloud.identity.get_registered_limit(
                registered_limit.id
            )
        )
        self.assertIsInstance(
            registered_limit, _registered_limit.RegisteredLimit
        )
        self.assertEqual(
            self.registered_limit_description, registered_limit.description
        )

        # (there's no name, so no way to retrieve by name)

        # list all registered limits

        registered_limits = list(
            self.system_admin_cloud.identity.registered_limits()
        )
        self.assertIsInstance(
            registered_limits[0], _registered_limit.RegisteredLimit
        )
        self.assertIn(
            self.resource_name,
            {x.resource_name for x in registered_limits},
        )
