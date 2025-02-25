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

from openstack.block_storage.v3 import group as _group
from openstack.block_storage.v3 import group_snapshot as _group_snapshot
from openstack.block_storage.v3 import group_type as _group_type
from openstack.block_storage.v3 import volume as _volume
from openstack.tests.functional.block_storage.v3 import base


class TestGroup(base.BaseBlockStorageTest):
    # TODO(stephenfin): We should use setUpClass here for MOAR SPEED!!!
    def setUp(self):
        super().setUp()

        # there will always be at least one volume type, i.e. the default one
        volume_types = list(self.operator_cloud.block_storage.types())
        self.volume_type = volume_types[0]

        group_type_name = self.getUniqueString()
        self.group_type = self.operator_cloud.block_storage.create_group_type(
            name=group_type_name,
        )
        self.assertIsInstance(self.group_type, _group_type.GroupType)
        self.assertEqual(group_type_name, self.group_type.name)

        group_name = self.getUniqueString()
        self.group = self.operator_cloud.block_storage.create_group(
            name=group_name,
            group_type=self.group_type.id,
            volume_types=[self.volume_type.id],
        )
        self.assertIsInstance(self.group, _group.Group)
        self.assertEqual(group_name, self.group.name)

    def tearDown(self):
        # we do this in tearDown rather than via 'addCleanup' since we need to
        # wait for the deletion of the group before moving onto the deletion of
        # the group type
        self.operator_cloud.block_storage.delete_group(
            self.group, delete_volumes=True
        )
        self.operator_cloud.block_storage.wait_for_delete(self.group)

        self.operator_cloud.block_storage.delete_group_type(self.group_type)
        self.operator_cloud.block_storage.wait_for_delete(self.group_type)

        super().tearDown()

    def test_group_type(self):
        # get
        group_type = self.operator_cloud.block_storage.get_group_type(
            self.group_type.id
        )
        self.assertEqual(self.group_type.name, group_type.name)

        # find
        group_type = self.operator_cloud.block_storage.find_group_type(
            self.group_type.name,
        )
        self.assertEqual(self.group_type.id, group_type.id)

        # list
        group_types = list(self.operator_cloud.block_storage.group_types())
        # other tests may have created group types and there can be defaults so
        # we don't assert that this is the *only* group type present
        self.assertIn(self.group_type.id, {g.id for g in group_types})

        # update
        group_type_name = self.getUniqueString()
        group_type_description = self.getUniqueString()
        group_type = self.operator_cloud.block_storage.update_group_type(
            self.group_type,
            name=group_type_name,
            description=group_type_description,
        )
        self.assertIsInstance(group_type, _group_type.GroupType)
        group_type = self.operator_cloud.block_storage.get_group_type(
            self.group_type.id
        )
        self.assertEqual(group_type_name, group_type.name)
        self.assertEqual(group_type_description, group_type.description)

    def test_group_type_group_specs(self):
        # create
        group_type = (
            self.operator_cloud.block_storage.create_group_type_group_specs(
                self.group_type,
                {'foo': 'bar', 'acme': 'buzz'},
            )
        )
        self.assertIsInstance(group_type, _group_type.GroupType)
        group_type = self.operator_cloud.block_storage.get_group_type(
            self.group_type.id
        )
        self.assertEqual(
            {'foo': 'bar', 'acme': 'buzz'}, group_type.group_specs
        )

        # get
        spec = self.operator_cloud.block_storage.get_group_type_group_specs_property(
            self.group_type,
            'foo',
        )
        self.assertEqual('bar', spec)

        # update
        spec = self.operator_cloud.block_storage.update_group_type_group_specs_property(
            self.group_type,
            'foo',
            'baz',
        )
        self.assertEqual('baz', spec)
        group_type = self.operator_cloud.block_storage.get_group_type(
            self.group_type.id
        )
        self.assertEqual(
            {'foo': 'baz', 'acme': 'buzz'}, group_type.group_specs
        )

        # delete
        self.operator_cloud.block_storage.delete_group_type_group_specs_property(
            self.group_type,
            'foo',
        )
        group_type = self.operator_cloud.block_storage.get_group_type(
            self.group_type.id
        )
        self.assertEqual({'acme': 'buzz'}, group_type.group_specs)

    def test_group(self):
        # get
        group = self.operator_cloud.block_storage.get_group(self.group.id)
        self.assertEqual(self.group.name, group.name)

        # find
        group = self.operator_cloud.block_storage.find_group(self.group.name)
        self.assertEqual(self.group.id, group.id)

        # list
        groups = self.operator_cloud.block_storage.groups()
        # other tests may have created groups and there can be defaults so we
        # don't assert that this is the *only* group present
        self.assertIn(self.group.id, {g.id for g in groups})

        # update
        group_name = self.getUniqueString()
        group_description = self.getUniqueString()
        group = self.operator_cloud.block_storage.update_group(
            self.group,
            name=group_name,
            description=group_description,
        )
        self.assertIsInstance(group, _group.Group)
        group = self.operator_cloud.block_storage.get_group(self.group.id)
        self.assertEqual(group_name, group.name)
        self.assertEqual(group_description, group.description)

    def test_group_snapshot(self):
        # group snapshots require a volume
        # no need for a teardown as the deletion of the group (with the
        # 'delete_volumes' flag) will handle this but we do need to wait for
        # the thing to be created
        volume_name = self.getUniqueString()
        self.volume = self.operator_cloud.block_storage.create_volume(
            name=volume_name,
            volume_type=self.volume_type.id,
            group_id=self.group.id,
            size=1,
        )
        self.operator_cloud.block_storage.wait_for_status(
            self.volume,
            status='available',
            failures=['error'],
            interval=2,
            wait=self._wait_for_timeout,
        )
        self.assertIsInstance(self.volume, _volume.Volume)

        group_snapshot_name = self.getUniqueString()
        self.group_snapshot = (
            self.operator_cloud.block_storage.create_group_snapshot(
                name=group_snapshot_name,
                group_id=self.group.id,
            )
        )
        self.operator_cloud.block_storage.wait_for_status(
            self.group_snapshot,
            status='available',
            failures=['error'],
            interval=2,
            wait=self._wait_for_timeout,
        )
        self.assertIsInstance(
            self.group_snapshot,
            _group_snapshot.GroupSnapshot,
        )

        # get
        group_snapshot = self.operator_cloud.block_storage.get_group_snapshot(
            self.group_snapshot.id,
        )
        self.assertEqual(self.group_snapshot.name, group_snapshot.name)

        # find
        group_snapshot = self.operator_cloud.block_storage.find_group_snapshot(
            self.group_snapshot.name,
        )
        self.assertEqual(self.group_snapshot.id, group_snapshot.id)

        # list
        group_snapshots = self.operator_cloud.block_storage.group_snapshots()
        # other tests may have created group snapshot and there can be defaults
        # so we don't assert that this is the *only* group snapshot present
        self.assertIn(self.group_snapshot.id, {g.id for g in group_snapshots})

        # update (not supported)

        # delete
        self.operator_cloud.block_storage.delete_group_snapshot(
            self.group_snapshot
        )
        self.operator_cloud.block_storage.wait_for_delete(self.group_snapshot)
