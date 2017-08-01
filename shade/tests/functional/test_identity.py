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
test_identity
----------------------------------

Functional tests for `shade` identity methods.
"""

import random
import string

from shade import OpenStackCloudException
from shade.tests.functional import base


class TestIdentity(base.KeystoneBaseFunctionalTestCase):
    def setUp(self):
        super(TestIdentity, self).setUp()
        self.role_prefix = 'test_role' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))
        self.user_prefix = self.getUniqueString('user')
        self.group_prefix = self.getUniqueString('group')

        self.addCleanup(self._cleanup_users)
        if self.identity_version not in ('2', '2.0'):
            self.addCleanup(self._cleanup_groups)
        self.addCleanup(self._cleanup_roles)

    def _cleanup_groups(self):
        exception_list = list()
        for group in self.operator_cloud.list_groups():
            if group['name'].startswith(self.group_prefix):
                try:
                    self.operator_cloud.delete_group(group['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise OpenStackCloudException('\n'.join(exception_list))

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

    def _cleanup_roles(self):
        exception_list = list()
        for role in self.operator_cloud.list_roles():
            if role['name'].startswith(self.role_prefix):
                try:
                    self.operator_cloud.delete_role(role['name'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise OpenStackCloudException('\n'.join(exception_list))

    def _create_user(self, **kwargs):
        domain_id = None
        if self.identity_version not in ('2', '2.0'):
            domain = self.operator_cloud.get_domain('default')
            domain_id = domain['id']
        return self.operator_cloud.create_user(domain_id=domain_id, **kwargs)

    def test_list_roles(self):
        roles = self.operator_cloud.list_roles()
        self.assertIsNotNone(roles)
        self.assertNotEqual([], roles)

    def test_get_role(self):
        role = self.operator_cloud.get_role('admin')
        self.assertIsNotNone(role)
        self.assertIn('id', role)
        self.assertIn('name', role)
        self.assertEqual('admin', role['name'])

    def test_search_roles(self):
        roles = self.operator_cloud.search_roles(filters={'name': 'admin'})
        self.assertIsNotNone(roles)
        self.assertEqual(1, len(roles))
        self.assertEqual('admin', roles[0]['name'])

    def test_create_role(self):
        role_name = self.role_prefix + '_create_role'
        role = self.operator_cloud.create_role(role_name)
        self.assertIsNotNone(role)
        self.assertIn('id', role)
        self.assertIn('name', role)
        self.assertEqual(role_name, role['name'])

    def test_delete_role(self):
        role_name = self.role_prefix + '_delete_role'
        role = self.operator_cloud.create_role(role_name)
        self.assertIsNotNone(role)
        self.assertTrue(self.operator_cloud.delete_role(role_name))

    # TODO(Shrews): Once we can support assigning roles within shade, we
    # need to make this test a little more specific, and add more for testing
    # filtering functionality.
    def test_list_role_assignments(self):
        if self.identity_version in ('2', '2.0'):
            self.skipTest("Identity service does not support role assignments")
        assignments = self.operator_cloud.list_role_assignments()
        self.assertIsInstance(assignments, list)
        self.assertGreater(len(assignments), 0)

    def test_list_role_assignments_v2(self):
        user = self.operator_cloud.get_user('demo')
        project = self.operator_cloud.get_project('demo')
        assignments = self.operator_cloud.list_role_assignments(
            filters={'user': user['id'], 'project': project['id']})
        self.assertIsInstance(assignments, list)
        self.assertGreater(len(assignments), 0)

    def test_grant_revoke_role_user_project(self):
        user_name = self.user_prefix + '_user_project'
        user_email = 'nobody@nowhere.com'
        role_name = self.role_prefix + '_grant_user_project'
        role = self.operator_cloud.create_role(role_name)
        user = self._create_user(name=user_name,
                                 email=user_email,
                                 default_project='demo')
        self.assertTrue(self.operator_cloud.grant_role(
            role_name, user=user['id'], project='demo', wait=True))
        assignments = self.operator_cloud.list_role_assignments({
            'role': role['id'],
            'user': user['id'],
            'project': self.operator_cloud.get_project('demo')['id']
        })
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(self.operator_cloud.revoke_role(
            role_name, user=user['id'], project='demo', wait=True))
        assignments = self.operator_cloud.list_role_assignments({
            'role': role['id'],
            'user': user['id'],
            'project': self.operator_cloud.get_project('demo')['id']
        })
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))

    def test_grant_revoke_role_group_project(self):
        if self.identity_version in ('2', '2.0'):
            self.skipTest("Identity service does not support group")
        role_name = self.role_prefix + '_grant_group_project'
        role = self.operator_cloud.create_role(role_name)
        group_name = self.group_prefix + '_group_project'
        group = self.operator_cloud.create_group(
            name=group_name,
            description='test group',
            domain='default')
        self.assertTrue(self.operator_cloud.grant_role(
            role_name, group=group['id'], project='demo'))
        assignments = self.operator_cloud.list_role_assignments({
            'role': role['id'],
            'group': group['id'],
            'project': self.operator_cloud.get_project('demo')['id']
        })
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(self.operator_cloud.revoke_role(
            role_name, group=group['id'], project='demo'))
        assignments = self.operator_cloud.list_role_assignments({
            'role': role['id'],
            'group': group['id'],
            'project': self.operator_cloud.get_project('demo')['id']
        })
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))

    def test_grant_revoke_role_user_domain(self):
        if self.identity_version in ('2', '2.0'):
            self.skipTest("Identity service does not support domain")
        role_name = self.role_prefix + '_grant_user_domain'
        role = self.operator_cloud.create_role(role_name)
        user_name = self.user_prefix + '_user_domain'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name,
                                 email=user_email,
                                 default_project='demo')
        self.assertTrue(self.operator_cloud.grant_role(
            role_name, user=user['id'], domain='default'))
        assignments = self.operator_cloud.list_role_assignments({
            'role': role['id'],
            'user': user['id'],
            'domain': self.operator_cloud.get_domain('default')['id']
        })
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(self.operator_cloud.revoke_role(
            role_name, user=user['id'], domain='default'))
        assignments = self.operator_cloud.list_role_assignments({
            'role': role['id'],
            'user': user['id'],
            'domain': self.operator_cloud.get_domain('default')['id']
        })
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))

    def test_grant_revoke_role_group_domain(self):
        if self.identity_version in ('2', '2.0'):
            self.skipTest("Identity service does not support domain or group")
        role_name = self.role_prefix + '_grant_group_domain'
        role = self.operator_cloud.create_role(role_name)
        group_name = self.group_prefix + '_group_domain'
        group = self.operator_cloud.create_group(
            name=group_name,
            description='test group',
            domain='default')
        self.assertTrue(self.operator_cloud.grant_role(
            role_name, group=group['id'], domain='default'))
        assignments = self.operator_cloud.list_role_assignments({
            'role': role['id'],
            'group': group['id'],
            'domain': self.operator_cloud.get_domain('default')['id']
        })
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(self.operator_cloud.revoke_role(
            role_name, group=group['id'], domain='default'))
        assignments = self.operator_cloud.list_role_assignments({
            'role': role['id'],
            'group': group['id'],
            'domain': self.operator_cloud.get_domain('default')['id']
        })
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))
