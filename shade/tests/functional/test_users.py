# -*- coding: utf-8 -*-

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

import random
import string

from shade import operator_cloud
from shade import OpenStackCloudException
from shade.tests import base


class TestUsers(base.TestCase):
    def setUp(self):
        super(TestUsers, self).setUp()
        self.cloud = operator_cloud(cloud='devstack-admin')
        self.user_prefix = 'test_user' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))
        self.addCleanup(self._cleanup_users)

    def _cleanup_users(self):
        exception_list = list()
        for user in self.cloud.list_users():
            if user['name'].startswith(self.user_prefix):
                try:
                    self.cloud.delete_user(user['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise OpenStackCloudException('\n'.join(exception_list))

    def _create_user(self, **kwargs):
        domain_id = None
        identity_version = self.cloud.cloud_config.get_api_version('identity')
        if identity_version not in ('2', '2.0'):
            domain = self.cloud.get_identity_domain('default')
            domain_id = domain['id']
        return self.cloud.create_user(domain_id=domain_id, **kwargs)

    def test_list_users(self):
        users = self.cloud.list_users()
        self.assertIsNotNone(users)
        self.assertNotEqual([], users)

    def test_get_user(self):
        user = self.cloud.get_user('admin')
        self.assertIsNotNone(user)
        self.assertIn('id', user)
        self.assertIn('name', user)
        self.assertEqual('admin', user['name'])

    def test_search_users(self):
        users = self.cloud.search_users(filters={'enabled': True})
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
        self.assertTrue(self.cloud.delete_user(user['id']))

    def test_delete_user_not_found(self):
        self.assertFalse(self.cloud.delete_user('does_not_exist'))

    def test_update_user(self):
        user_name = self.user_prefix + '_updatev3'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name, email=user_email)
        self.assertIsNotNone(user)
        self.assertTrue(user['enabled'])

        # Pass some keystone v3 params. This should work no matter which
        # version of keystone we are testing against.
        new_user = self.cloud.update_user(user['id'],
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
