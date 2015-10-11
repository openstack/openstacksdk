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

from shade import operator_cloud
from shade.tests import base


class TestIdentity(base.TestCase):
    def setUp(self):
        super(TestIdentity, self).setUp()
        self.cloud = operator_cloud(cloud='devstack-admin')

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
