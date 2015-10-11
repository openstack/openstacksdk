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
test_identity
----------------------------------

Functional tests for `shade` identity methods.
"""

import random
import string

from shade import operator_cloud
from shade import OpenStackCloudException
from shade.tests import base


class TestIdentity(base.TestCase):
    def setUp(self):
        super(TestIdentity, self).setUp()
        self.cloud = operator_cloud(cloud='devstack-admin')
        self.role_prefix = 'test_role' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5))
        self.addCleanup(self._cleanup_roles)

    def _cleanup_roles(self):
        exception_list = list()
        for role in self.cloud.list_roles():
            if role['name'].startswith(self.role_prefix):
                try:
                    self.cloud.delete_role(role['name'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise OpenStackCloudException('\n'.join(exception_list))

    def test_list_roles(self):
        roles = self.cloud.list_roles()
        self.assertIsNotNone(roles)
        self.assertNotEqual([], roles)

    def test_get_role(self):
        role = self.cloud.get_role('admin')
        self.assertIsNotNone(role)
        self.assertIn('id', role)
        self.assertIn('name', role)
        self.assertEqual('admin', role['name'])

    def test_search_roles(self):
        roles = self.cloud.search_roles(filters={'name': 'admin'})
        self.assertIsNotNone(roles)
        self.assertEqual(1, len(roles))
        self.assertEqual('admin', roles[0]['name'])

    def test_create_role(self):
        role_name = self.role_prefix + '_create_role'
        role = self.cloud.create_role(role_name)
        self.assertIsNotNone(role)
        self.assertIn('id', role)
        self.assertIn('name', role)
        self.assertEqual(role_name, role['name'])

    def test_delete_role(self):
        role_name = self.role_prefix + '_delete_role'
        role = self.cloud.create_role(role_name)
        self.assertIsNotNone(role)
        self.assertTrue(self.cloud.delete_role(role_name))
