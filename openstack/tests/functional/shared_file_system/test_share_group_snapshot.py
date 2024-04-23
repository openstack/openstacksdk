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

from openstack import resource
from openstack.shared_file_system.v2 import (
    share_group_snapshot as _share_group_snapshot,
)
from openstack.tests.functional.shared_file_system import base


class ShareGroupSnapshotTest(base.BaseSharedFileSystemTest):
    min_microversion = '2.55'

    def setUp(self):
        super().setUp()

        self.SHARE_GROUP_NAME = self.getUniqueString()
        share_grp = self.user_cloud.shared_file_system.create_share_group(
            name=self.SHARE_GROUP_NAME
        )
        self.user_cloud.shared_file_system.wait_for_status(
            share_grp,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertIsNotNone(share_grp)
        self.assertIsNotNone(share_grp.id)
        self.SHARE_GROUP_ID = share_grp.id

        self.SHARE_GROUP_SNAPSHOT_NAME = self.getUniqueString()
        grp_ss = (
            self.user_cloud.shared_file_system.create_share_group_snapshot(
                self.SHARE_GROUP_ID, name=self.SHARE_GROUP_SNAPSHOT_NAME
            )
        )
        self.user_cloud.shared_file_system.wait_for_status(
            grp_ss,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertIsNotNone(grp_ss)
        self.assertIsNotNone(grp_ss.id)
        self.SHARE_GROUP_SNAPSHOT_ID = grp_ss.id

    def tearDown(self):
        sot = self.user_cloud.shared_file_system.get_share_group_snapshot(
            self.SHARE_GROUP_SNAPSHOT_ID
        )
        self.user_cloud.shared_file_system.delete_share_group_snapshot(
            self.SHARE_GROUP_SNAPSHOT_ID, ignore_missing=False
        )
        resource.wait_for_delete(
            self.user_cloud.share, sot, wait=self._wait_for_timeout, interval=2
        )
        self.user_cloud.shared_file_system.delete_share_group(
            self.SHARE_GROUP_ID, ignore_missing=False
        )
        super().tearDown()

    def test_get(self):
        sot = self.user_cloud.shared_file_system.get_share_group_snapshot(
            self.SHARE_GROUP_SNAPSHOT_ID
        )
        assert isinstance(sot, _share_group_snapshot.ShareGroupSnapshot)
        self.assertEqual(self.SHARE_GROUP_SNAPSHOT_ID, sot.id)

    def test_list(self):
        snapshots = self.user_cloud.shared_file_system.share_group_snapshots()
        self.assertGreater(len(list(snapshots)), 0)
        for snapshot in snapshots:
            for attribute in ('id', 'name', 'created_at'):
                self.assertTrue(hasattr(snapshot, attribute))

    def test_update(self):
        u_ss = self.user_cloud.shared_file_system.update_share_group_snapshot(
            self.SHARE_GROUP_SNAPSHOT_ID,
            description='updated share group snapshot',
        )
        get_u_ss = self.user_cloud.shared_file_system.get_share_group_snapshot(
            u_ss.id
        )
        self.assertEqual('updated share group snapshot', get_u_ss.description)

    def test_reset(self):
        res = self.operator_cloud.shared_file_system.reset_share_group_snapshot_status(
            self.SHARE_GROUP_SNAPSHOT_ID, 'error'
        )
        self.assertIsNone(res)
        sot = self.user_cloud.shared_file_system.get_share_group_snapshot(
            self.SHARE_GROUP_SNAPSHOT_ID
        )
        self.assertEqual('error', sot.status)
