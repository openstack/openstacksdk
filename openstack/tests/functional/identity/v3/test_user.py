#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from openstack.identity.v3 import user as _user
from openstack.tests.functional import base


class TestUser(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.username = self.getUniqueString('user')
        self.password = "test_password_123"
        self.email = f"{self.username}@example.com"
        self.description = "Test user for functional testing"

    def _delete_user(self, user):
        ret = self.operator_cloud.identity.delete_user(user)
        self.assertIsNone(ret)

    def test_user(self):
        # Create user
        user = self.operator_cloud.identity.create_user(
            name=self.username,
            password=self.password,
            email=self.email,
            description=self.description,
        )
        self.addCleanup(self._delete_user, user)
        self.assertIsInstance(user, _user.User)
        self.assertIsNotNone(user.id)
        self.assertEqual(self.username, user.name)
        self.assertEqual(self.email, user.email)
        self.assertEqual(self.description, user.description)

        # Update user
        new_email = f"updated_{self.username}@example.com"
        new_description = "Updated description for test user"

        updated_user = self.operator_cloud.identity.update_user(
            user.id, email=new_email, description=new_description
        )
        self.assertIsInstance(updated_user, _user.User)
        self.assertEqual(new_email, updated_user.email)
        self.assertEqual(new_description, updated_user.description)
        self.assertEqual(
            self.username, updated_user.name
        )  # Name should remain unchanged

        # Read user list
        users = list(self.operator_cloud.identity.users())
        self.assertIsInstance(users[0], _user.User)
        user_ids = {ep.id for ep in users}
        self.assertIn(user.id, user_ids)

        # Read user by ID
        user = self.operator_cloud.identity.get_user(user.id)
        self.assertIsInstance(user, _user.User)
        self.assertEqual(user.id, user.id)
        self.assertEqual(self.username, user.name)
        self.assertEqual(new_email, user.email)
        self.assertEqual(new_description, user.description)
