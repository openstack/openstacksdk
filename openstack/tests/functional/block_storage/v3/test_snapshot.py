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


from openstack.block_storage.v3 import snapshot as _snapshot
from openstack.block_storage.v3 import volume as _volume
from openstack.tests.functional.block_storage.v3 import base


class TestSnapshot(base.BaseBlockStorageTest):
    def setUp(self):
        super().setUp()

        self.SNAPSHOT_NAME = self.getUniqueString()
        self.SNAPSHOT_ID = None
        self.VOLUME_NAME = self.getUniqueString()
        self.VOLUME_ID = None

        volume = self.user_cloud.block_storage.create_volume(
            name=self.VOLUME_NAME, size=1
        )
        self.user_cloud.block_storage.wait_for_status(
            volume,
            status='available',
            failures=['error'],
            interval=2,
            wait=self._wait_for_timeout,
        )
        assert isinstance(volume, _volume.Volume)
        self.assertEqual(self.VOLUME_NAME, volume.name)
        self.VOLUME_ID = volume.id
        snapshot = self.user_cloud.block_storage.create_snapshot(
            name=self.SNAPSHOT_NAME, volume_id=self.VOLUME_ID
        )
        self.user_cloud.block_storage.wait_for_status(
            snapshot,
            status='available',
            failures=['error'],
            interval=2,
            wait=self._wait_for_timeout,
        )
        assert isinstance(snapshot, _snapshot.Snapshot)
        self.assertEqual(self.SNAPSHOT_NAME, snapshot.name)
        self.SNAPSHOT_ID = snapshot.id

    def tearDown(self):
        snapshot = self.user_cloud.block_storage.get_snapshot(self.SNAPSHOT_ID)
        sot = self.user_cloud.block_storage.delete_snapshot(
            snapshot, ignore_missing=False
        )
        self.user_cloud.block_storage.wait_for_delete(
            snapshot, interval=2, wait=self._wait_for_timeout
        )
        self.assertIsNone(sot)
        sot = self.user_cloud.block_storage.delete_volume(
            self.VOLUME_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_get(self):
        sot = self.user_cloud.block_storage.get_snapshot(self.SNAPSHOT_ID)
        self.assertEqual(self.SNAPSHOT_NAME, sot.name)
