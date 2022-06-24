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


class TestGroup(base.BaseBlockStorageTest):
    # TODO(stephenfin): We should use setUpClass here for MOAR SPEED!!!
    def setUp(self):
        super().setUp()

        if not self.user_cloud.has_service('block-storage'):
            self.skipTest('block-storage service not supported by cloud')

        group_type_name = self.getUniqueString()
        self.group_type = self.conn.block_storage.create_group_type(
            name=group_type_name,
        )
        self.addCleanup(
            self.conn.block_storage.delete_group_type,
            self.group_type,
        )
        self.assertIsInstance(self.group_type, _group_type.GroupType)
        self.assertEqual(group_type_name, self.group_type.name)

    def test_group_type(self):
        # get
        group_type = self.conn.block_storage.get_group_type(self.group_type)
        self.assertEqual(self.group_type.name, group_type.name)

        # find
        group_type = self.conn.block_storage.find_group_type(
            self.group_type.name,
        )
        self.assertEqual(self.group_type.id, group_type.id)

        # list
        group_types = list(self.conn.block_storage.group_types())
        # other tests may have created group types and there can be defaults so
        # we don't assert that this is the *only* group type present
        self.assertIn(self.group_type.id, {g.id for g in group_types})

        # update
        group_type_name = self.getUniqueString()
        group_type_description = self.getUniqueString()
        group_type = self.conn.block_storage.update_group_type(
            self.group_type,
            name=group_type_name,
            description=group_type_description,
        )
        self.assertIsInstance(group_type, _group_type.GroupType)
        group_type = self.conn.block_storage.get_group_type(self.group_type.id)
        self.assertEqual(group_type_name, group_type.name)
        self.assertEqual(group_type_description, group_type.description)

    def test_group_type_group_specs(self):
        # create
        group_type = self.conn.block_storage.create_group_type_group_specs(
            self.group_type,
            {'foo': 'bar', 'acme': 'buzz'},
        )
        self.assertIsInstance(group_type, _group_type.GroupType)
        group_type = self.conn.block_storage.get_group_type(self.group_type.id)
        self.assertEqual(
            {'foo': 'bar', 'acme': 'buzz'}, group_type.group_specs
        )

        # get
        spec = self.conn.block_storage.get_group_type_group_specs_property(
            self.group_type,
            'foo',
        )
        self.assertEqual('bar', spec)

        # update
        spec = self.conn.block_storage.update_group_type_group_specs_property(
            self.group_type,
            'foo',
            'baz',
        )
        self.assertEqual('baz', spec)
        group_type = self.conn.block_storage.get_group_type(self.group_type.id)
        self.assertEqual(
            {'foo': 'baz', 'acme': 'buzz'}, group_type.group_specs
        )

        # delete
        self.conn.block_storage.delete_group_type_group_specs_property(
            self.group_type,
            'foo',
        )
        group_type = self.conn.block_storage.get_group_type(self.group_type.id)
        self.assertEqual({'acme': 'buzz'}, group_type.group_specs)
