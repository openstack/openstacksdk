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

from openstack.identity.v3 import group as _group
from openstack.identity.v3 import user as _user
from openstack.tests.functional import base


class TestGroup(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.group_name = self.getUniqueString('group')
        self.group_description = self.getUniqueString('group')
        self.user_name = self.getUniqueString('user')
        self.user_email = f"{self.user_name}@example.com"

        self.user = self.operator_cloud.identity.create_user(
            name=self.user_name,
            email=self.user_email,
        )
        self.addCleanup(self._delete_user, self.user)

    def _delete_group(self, group):
        ret = self.operator_cloud.identity.delete_group(group)
        self.assertIsNone(ret)

    def _delete_user(self, user):
        ret = self.operator_cloud.identity.delete_user(user)
        self.assertIsNone(ret)

    def test_group(self):
        # create the group

        group = self.operator_cloud.identity.create_group(
            name=self.group_name,
        )
        self.addCleanup(self._delete_group, group)
        self.assertIsInstance(group, _group.Group)
        self.assertEqual('', group.description)

        # update the group

        group = self.operator_cloud.identity.update_group(
            group, description=self.group_description
        )
        self.assertIsInstance(group, _group.Group)
        self.assertEqual(self.group_description, group.description)

        # retrieve details of the (updated) group by ID

        group = self.operator_cloud.identity.get_group(group.id)
        self.assertIsInstance(group, _group.Group)
        self.assertEqual(self.group_description, group.description)

        # retrieve details of the (updated) group by name

        group = self.operator_cloud.identity.find_group(group.name)
        self.assertIsInstance(group, _group.Group)
        self.assertEqual(self.group_description, group.description)

        # list all groups

        groups = list(self.operator_cloud.identity.groups())
        self.assertIsInstance(groups[0], _group.Group)
        self.assertIn(
            self.group_name,
            {x.name for x in groups},
        )

        # add user to group
        self.operator_cloud.identity.add_user_to_group(self.user, group)

        is_in_group = self.operator_cloud.identity.check_user_in_group(
            self.user, group
        )
        self.assertTrue(is_in_group)

        group_users = list(self.operator_cloud.identity.group_users(group))
        self.assertIsInstance(group_users[0], _user.User)
        self.assertIn(self.user_name, {x.name for x in group_users})

        # remove user from group

        self.operator_cloud.identity.remove_user_from_group(self.user, group)

        is_in_group = self.operator_cloud.identity.check_user_in_group(
            self.user, group
        )
        self.assertFalse(is_in_group)
