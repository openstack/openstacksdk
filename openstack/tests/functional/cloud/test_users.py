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

"""
test_users
----------------------------------

Functional tests for `shade` user methods.
"""

from openstack.cloud.exc import OpenStackCloudException
from openstack.tests.functional.cloud import base


class TestUsers(base.KeystoneBaseFunctionalTestCase):
    def setUp(self):
        super(TestUsers, self).setUp()
        self.user_prefix = self.getUniqueString('user')
        self.addCleanup(self._cleanup_users)

    def _cleanup_users(self):
        exception_list = list()
        for user in self.operator_cloud.list_users():
            if user['name'].startswith(self.user_prefix):
                try:
                    self.operator_cloud.delete_user(user['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise OpenStackCloudException('\n'.join(exception_list))

    def _create_user(self, **kwargs):
        domain_id = None
        i_ver = self.operator_cloud.config.get_api_version('identity')
        if i_ver not in ('2', '2.0'):
            domain = self.operator_cloud.get_domain('default')
            domain_id = domain['id']
        return self.operator_cloud.create_user(domain_id=domain_id, **kwargs)

    def test_list_users(self):
        users = self.operator_cloud.list_users()
        self.assertIsNotNone(users)
        self.assertNotEqual([], users)

    def test_get_user(self):
        user = self.operator_cloud.get_user('admin')
        self.assertIsNotNone(user)
        self.assertIn('id', user)
        self.assertIn('name', user)
        self.assertEqual('admin', user['name'])

    def test_search_users(self):
        users = self.operator_cloud.search_users(filters={'enabled': True})
        self.assertIsNotNone(users)

    def test_search_users_jmespath(self):
        users = self.operator_cloud.search_users(filters="[?enabled]")
        self.assertIsNotNone(users)

    def test_create_user(self):
        user_name = self.user_prefix + '_create'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name, email=user_email)
        self.assertIsNotNone(user)
        self.assertEqual(user_name, user['name'])
        self.assertEqual(user_email, user['email'])
        self.assertTrue(user['enabled'])

    def test_delete_user(self):
        user_name = self.user_prefix + '_delete'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name, email=user_email)
        self.assertIsNotNone(user)
        self.assertTrue(self.operator_cloud.delete_user(user['id']))

    def test_delete_user_not_found(self):
        self.assertFalse(self.operator_cloud.delete_user('does_not_exist'))

    def test_update_user(self):
        user_name = self.user_prefix + '_updatev3'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name, email=user_email)
        self.assertIsNotNone(user)
        self.assertTrue(user['enabled'])

        # Pass some keystone v3 params. This should work no matter which
        # version of keystone we are testing against.
        new_user = self.operator_cloud.update_user(
            user['id'],
            name=user_name + '2',
            email='somebody@nowhere.com',
            enabled=False,
            password='secret',
            description='')
        self.assertIsNotNone(new_user)
        self.assertEqual(user['id'], new_user['id'])
        self.assertEqual(user_name + '2', new_user['name'])
        self.assertEqual('somebody@nowhere.com', new_user['email'])
        self.assertFalse(new_user['enabled'])

    def test_update_user_password(self):
        user_name = self.user_prefix + '_password'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name,
                                 email=user_email,
                                 password='old_secret')
        self.assertIsNotNone(user)
        self.assertTrue(user['enabled'])

        # This should work for both v2 and v3
        new_user = self.operator_cloud.update_user(
            user['id'], password='new_secret')
        self.assertIsNotNone(new_user)
        self.assertEqual(user['id'], new_user['id'])
        self.assertEqual(user_name, new_user['name'])
        self.assertEqual(user_email, new_user['email'])
        self.assertTrue(new_user['enabled'])
        self.assertTrue(self.operator_cloud.grant_role(
            'member', user=user['id'], project='demo', wait=True))
        self.addCleanup(
            self.operator_cloud.revoke_role,
            'member', user=user['id'], project='demo', wait=True)

        new_cloud = self.operator_cloud.connect_as(
            user_id=user['id'],
            password='new_secret',
            project_name='demo')

        self.assertIsNotNone(new_cloud)
        location = new_cloud.current_location
        self.assertEqual(location['project']['name'], 'demo')
        self.assertIsNotNone(new_cloud.service_catalog)

    def test_users_and_groups(self):
        i_ver = self.operator_cloud.config.get_api_version('identity')
        if i_ver in ('2', '2.0'):
            self.skipTest('Identity service does not support groups')

        group_name = self.getUniqueString('group')
        self.addCleanup(self.operator_cloud.delete_group, group_name)

        # Create a group
        group = self.operator_cloud.create_group(group_name, 'test group')
        self.assertIsNotNone(group)

        # Create a user
        user_name = self.user_prefix + '_ug'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name, email=user_email)
        self.assertIsNotNone(user)

        # Add the user to the group
        self.operator_cloud.add_user_to_group(user_name, group_name)
        self.assertTrue(
            self.operator_cloud.is_user_in_group(user_name, group_name))

        # Remove them from the group
        self.operator_cloud.remove_user_from_group(user_name, group_name)
        self.assertFalse(
            self.operator_cloud.is_user_in_group(user_name, group_name))
