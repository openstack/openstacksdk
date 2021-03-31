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

from openstack.block_storage.v3 import group_type as _group_type
from openstack.tests.functional.block_storage.v3 import base


class TestGroupType(base.BaseBlockStorageTest):

    def setUp(self):
        super(TestGroupType, self).setUp()

        self.GROUP_TYPE_NAME = self.getUniqueString()
        self.GROUP_TYPE_ID = None

        group_type = self.conn.block_storage.create_group_type(
            name=self.GROUP_TYPE_NAME)
        self.assertIsInstance(group_type, _group_type.GroupType)
        self.assertEqual(self.GROUP_TYPE_NAME, group_type.name)
        self.GROUP_TYPE_ID = group_type.id

    def tearDown(self):
        group_type = self.conn.block_storage.delete_group_type(
            self.GROUP_TYPE_ID, ignore_missing=False)
        self.assertIsNone(group_type)
        super(TestGroupType, self).tearDown()

    def test_get(self):
        group_type = self.conn.block_storage.get_group_type(self.GROUP_TYPE_ID)
        self.assertEqual(self.GROUP_TYPE_NAME, group_type.name)
