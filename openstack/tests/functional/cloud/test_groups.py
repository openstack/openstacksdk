# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_groups
----------------------------------

Functional tests for `shade` keystone group resource.
"""

import openstack.cloud
from openstack.tests.functional.cloud import base


class TestGroup(base.BaseFunctionalTestCase):

    def setUp(self):
        super(TestGroup, self).setUp()
        i_ver = self.operator_cloud.config.get_api_version('identity')
        if i_ver in ('2', '2.0'):
            self.skipTest('Identity service does not support groups')
        self.group_prefix = self.getUniqueString('group')
        self.addCleanup(self._cleanup_groups)

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
            raise openstack.cloud.OpenStackCloudException(
                '\n'.join(exception_list))

    def test_create_group(self):
        group_name = self.group_prefix + '_create'
        group = self.operator_cloud.create_group(group_name, 'test group')

        for key in ('id', 'name', 'description', 'domain_id'):
            self.assertIn(key, group)
        self.assertEqual(group_name, group['name'])
        self.assertEqual('test group', group['description'])

    def test_delete_group(self):
        group_name = self.group_prefix + '_delete'

        group = self.operator_cloud.create_group(group_name, 'test group')
        self.assertIsNotNone(group)

        self.assertTrue(self.operator_cloud.delete_group(group_name))

        results = self.operator_cloud.search_groups(
            filters=dict(name=group_name))
        self.assertEqual(0, len(results))

    def test_delete_group_not_exists(self):
        self.assertFalse(self.operator_cloud.delete_group('xInvalidGroupx'))

    def test_search_groups(self):
        group_name = self.group_prefix + '_search'

        # Shouldn't find any group with this name yet
        results = self.operator_cloud.search_groups(
            filters=dict(name=group_name))
        self.assertEqual(0, len(results))

        # Now create a new group
        group = self.operator_cloud.create_group(group_name, 'test group')
        self.assertEqual(group_name, group['name'])

        # Now we should find only the new group
        results = self.operator_cloud.search_groups(
            filters=dict(name=group_name))
        self.assertEqual(1, len(results))
        self.assertEqual(group_name, results[0]['name'])

    def test_update_group(self):
        group_name = self.group_prefix + '_update'
        group_desc = 'test group'

        group = self.operator_cloud.create_group(group_name, group_desc)
        self.assertEqual(group_name, group['name'])
        self.assertEqual(group_desc, group['description'])

        updated_group_name = group_name + '_xyz'
        updated_group_desc = group_desc + ' updated'
        updated_group = self.operator_cloud.update_group(
            group_name,
            name=updated_group_name,
            description=updated_group_desc)
        self.assertEqual(updated_group_name, updated_group['name'])
        self.assertEqual(updated_group_desc, updated_group['description'])
