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

from openstack.tests.functional.shared_file_system import base


class ShareSnapshotTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        self.SHARE_NAME = self.getUniqueString()
        self.SNAPSHOT_NAME = self.getUniqueString()
        my_share = self.operator_cloud.shared_file_system.create_share(
            name=self.SHARE_NAME,
            size=2,
            share_type="dhss_false",
            share_protocol='NFS',
            description=None,
        )
        self.operator_cloud.shared_file_system.wait_for_status(
            my_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertIsNotNone(my_share)
        self.assertIsNotNone(my_share.id)
        self.SHARE_ID = my_share.id

        msp = self.operator_cloud.shared_file_system.create_share_snapshot(
            share_id=self.SHARE_ID, name=self.SNAPSHOT_NAME, force=True
        )
        self.operator_cloud.shared_file_system.wait_for_status(
            msp,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertIsNotNone(msp.id)
        self.SNAPSHOT_ID = msp.id

    def tearDown(self):
        snpt = self.operator_cloud.shared_file_system.get_share_snapshot(
            self.SNAPSHOT_ID
        )
        sot = self.operator_cloud.shared_file_system.delete_share_snapshot(
            snpt, ignore_missing=False
        )
        self.operator_cloud.shared_file_system.wait_for_delete(
            snpt, interval=2, wait=self._wait_for_timeout
        )
        self.assertIsNone(sot)
        sot = self.operator_cloud.shared_file_system.delete_share(
            self.SHARE_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_get(self):
        sot = self.operator_cloud.shared_file_system.get_share_snapshot(
            self.SNAPSHOT_ID
        )
        self.assertEqual(self.SNAPSHOT_NAME, sot.name)

    def test_list(self):
        snaps = self.operator_cloud.shared_file_system.share_snapshots(
            details=True
        )
        self.assertGreater(len(list(snaps)), 0)
        for snap in snaps:
            for attribute in (
                'id',
                'name',
                'created_at',
                'updated_at',
                'description',
                'share_id',
                'share_proto',
                'share_size',
                'size',
                'status',
                'user_id',
            ):
                self.assertTrue(hasattr(snap, attribute))

    def test_update(self):
        u_snap = self.operator_cloud.shared_file_system.update_share_snapshot(
            self.SNAPSHOT_ID, display_description='updated share snapshot'
        )
        get_u_snap = self.operator_cloud.shared_file_system.get_share_snapshot(
            u_snap.id
        )
        self.assertEqual('updated share snapshot', get_u_snap.description)
