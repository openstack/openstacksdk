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
from openstack.tests.functional.cloud import base


class TestVolume(base.BaseFunctionalTestCase):
    # Creating a volume backup is incredibly slow.
    TIMEOUT_SCALING_FACTOR = 1.5

    def setUp(self):
        super(TestVolume, self).setUp()
        self.skipTest('Volume functional tests temporarily disabled')
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')

        if not self.user_cloud.has_service('object-store'):
            self.skipTest('volume backups require swift')

    def test_create_get_delete_volume_backup(self):
        volume = self.user_cloud.create_volume(
            display_name=self.getUniqueString(), size=1)
        self.addCleanup(self.user_cloud.delete_volume, volume['id'])

        backup_name_1 = self.getUniqueString()
        backup_desc_1 = self.getUniqueString()
        backup = self.user_cloud.create_volume_backup(
            volume_id=volume['id'], name=backup_name_1,
            description=backup_desc_1, wait=True)
        self.assertEqual(backup_name_1, backup['name'])

        backup = self.user_cloud.get_volume_backup(backup['id'])
        self.assertEqual("available", backup['status'])
        self.assertEqual(backup_desc_1, backup['description'])

        self.user_cloud.delete_volume_backup(backup['id'], wait=True)
        self.assertIsNone(self.user_cloud.get_volume_backup(backup['id']))

    def test_list_volume_backups(self):
        vol1 = self.user_cloud.create_volume(
            display_name=self.getUniqueString(), size=1)
        self.addCleanup(self.user_cloud.delete_volume, vol1['id'])

        # We create 2 volumes to create 2 backups. We could have created 2
        # backups from the same volume but taking 2 successive backups seems
        # to be race-condition prone. And I didn't want to use an ugly sleep()
        # here.
        vol2 = self.user_cloud.create_volume(
            display_name=self.getUniqueString(), size=1)
        self.addCleanup(self.user_cloud.delete_volume, vol2['id'])

        backup_name_1 = self.getUniqueString()
        backup = self.user_cloud.create_volume_backup(
            volume_id=vol1['id'], name=backup_name_1)
        self.addCleanup(self.user_cloud.delete_volume_backup, backup['id'])

        backup = self.user_cloud.create_volume_backup(volume_id=vol2['id'])
        self.addCleanup(self.user_cloud.delete_volume_backup, backup['id'])

        backups = self.user_cloud.list_volume_backups()
        self.assertEqual(2, len(backups))

        backups = self.user_cloud.list_volume_backups(
            search_opts={"name": backup_name_1})
        self.assertEqual(1, len(backups))
        self.assertEqual(backup_name_1, backups[0]['name'])
