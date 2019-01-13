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

from openstack.block_storage.v3 import volume as _volume
from openstack.block_storage.v3 import backup as _backup
from openstack.tests.functional.block_storage.v3 import base


class TestBackup(base.BaseBlockStorageTest):

    def setUp(self):
        super(TestBackup, self).setUp()

        if not self.user_cloud.has_service('object-store'):
            self.skipTest('Object service is requred, but not available')

        self.VOLUME_NAME = self.getUniqueString()
        self.VOLUME_ID = None
        self.BACKUP_NAME = self.getUniqueString()
        self.BACKUP_ID = None

        volume = self.user_cloud.block_storage.create_volume(
            name=self.VOLUME_NAME,
            size=1)
        self.user_cloud.block_storage.wait_for_status(
            volume,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout)
        assert isinstance(volume, _volume.Volume)
        self.VOLUME_ID = volume.id

        backup = self.user_cloud.block_storage.create_backup(
            name=self.BACKUP_NAME,
            volume_id=volume.id)
        self.user_cloud.block_storage.wait_for_status(
            backup,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout)
        assert isinstance(backup, _backup.Backup)
        self.assertEqual(self.BACKUP_NAME, backup.name)
        self.BACKUP_ID = backup.id

    def tearDown(self):
        sot = self.user_cloud.block_storage.delete_backup(
            self.BACKUP_ID,
            ignore_missing=False)
        sot = self.user_cloud.block_storage.delete_volume(
            self.VOLUME_ID,
            ignore_missing=False)
        self.assertIsNone(sot)
        super(TestBackup, self).tearDown()

    def test_get(self):
        sot = self.user_cloud.block_storage.get_backup(self.BACKUP_ID)
        self.assertEqual(self.BACKUP_NAME, sot.name)
