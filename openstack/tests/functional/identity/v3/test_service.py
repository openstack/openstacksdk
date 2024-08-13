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

from openstack.tests.functional.identity.v3 import base


class TestService(base.BaseIdentityTest):
    def setUp(self):
        super().setUp()
        self.svc_name = self.getUniqueString("crud-service")
        self.svc_type = self.getUniqueString("crud-type")

    def test_service(self):
        # create a new service
        service = self.admin_identity_client.create_service(
            name=self.svc_name,
            type=self.svc_type,
            description="CRUD workflow test",
            enabled=True,
        )
        svc_id = service.id
        self.addCleanup(
            self.admin_identity_client.delete_service,
            svc_id,
            ignore_missing=True,
        )

        self.assertEqual(self.svc_name, service.name)
        self.assertEqual(self.svc_type, service.type)
        self.assertTrue(service.is_enabled)

        # retrieve details of the created service
        got = self.admin_identity_client.get_service(svc_id)
        self.assertEqual(svc_id, got.id)

        # verify service appears in list
        ids = {s.id for s in self.admin_identity_client.services()}
        self.assertIn(svc_id, ids)

        # find service by name
        found = self.admin_identity_client.find_service(
            self.svc_name, ignore_missing=False
        )
        self.assertIsNotNone(found)
        self.assertEqual(svc_id, found.id)

        # update service attributes
        new_desc = "Updated CRUD test"
        updated = self.admin_identity_client.update_service(
            svc_id, description=new_desc, enabled=False
        )
        self.assertEqual(new_desc, updated.description)
        self.assertFalse(updated.is_enabled)

        # delete the service
        self.admin_identity_client.delete_service(svc_id)
        self.assertIsNone(
            self.admin_identity_client.find_service(
                svc_id, ignore_missing=True
            )
        )
