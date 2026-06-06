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

from openstack.tests.functional.shared_file_system.v2 import base


class ShareSnapshotMetadataTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()
        self.user_client = self.user_cloud.shared_file_system

        self.SHARE_NAME = self.getUniqueString()
        share = self.user_client.create_share(
            name=self.SHARE_NAME,
            size=2,
            share_type="dhss_false",
            share_protocol='NFS',
            description=None,
        )
        self.assertIsNotNone(share)
        self.assertIsNotNone(share.id)
        self.user_client.wait_for_status(
            share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.SHARE_ID = share.id

        self.SNAPSHOT_NAME = self.getUniqueString()
        snapshot = self.user_client.create_share_snapshot(
            name=self.SNAPSHOT_NAME,
            share_id=share.id,
            description=None,
        )
        self.assertIsNotNone(snapshot)
        self.assertIsNotNone(snapshot.id)
        self.user_client.wait_for_status(
            snapshot,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.SNAPSHOT_ID = snapshot.id

    def tearDown(self):
        snapshot = self.user_client.get_share_snapshot(self.SNAPSHOT_ID)
        sot = self.user_client.delete_share_snapshot(
            snapshot, ignore_missing=False
        )
        self.assertIsNone(sot)
        self.user_client.wait_for_delete(
            snapshot, interval=2, wait=self._wait_for_timeout
        )
        sot = self.user_client.delete_share(
            self.SHARE_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_share_snapshot_metadata(self):
        # create
        sot = self.user_client.set_share_snapshot_metadata(
            self.SNAPSHOT_ID, foo='bar'
        )
        self.assertEqual(sot['metadata'], {'foo': 'bar'})

        # get all metadata
        sot = self.user_client.fetch_share_snapshot_metadata(self.SNAPSHOT_ID)
        self.assertEqual('bar', sot['metadata']['foo'])

        # get metadata item
        sot = self.user_client.fetch_share_snapshot_metadata_item(
            self.SNAPSHOT_ID, 'foo'
        )
        self.assertEqual('bar', sot['metadata']['foo'])

        # update (merge)
        self.user_client.set_share_snapshot_metadata(
            self.SNAPSHOT_ID, new_foo='new_bar'
        )
        sot = self.user_client.fetch_share_snapshot_metadata(self.SNAPSHOT_ID)
        self.assertEqual(sot['metadata'], {'foo': 'bar', 'new_foo': 'new_bar'})

        # delete
        self.user_client.delete_share_snapshot_metadata(
            self.SNAPSHOT_ID, ['foo']
        )
        sot = self.user_client.fetch_share_snapshot_metadata(self.SNAPSHOT_ID)
        self.assertEqual(sot['metadata'], {'new_foo': 'new_bar'})

        # replace with empty
        sot = self.user_client.set_share_snapshot_metadata(
            self.SNAPSHOT_ID, replace=True
        )
        self.assertEqual(sot['metadata'], {})

        sot = self.user_client.fetch_share_snapshot_metadata(self.SNAPSHOT_ID)
        self.assertEqual(sot['metadata'], {})
