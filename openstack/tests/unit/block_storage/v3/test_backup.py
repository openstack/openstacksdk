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

import copy
import mock

from keystoneauth1 import adapter

from openstack.tests.unit import base

from openstack.block_storage.v3 import backup

FAKE_ID = "6685584b-1eac-4da6-b5c3-555430cf68ff"

BACKUP = {
    "availability_zone": "az1",
    "container": "volumebackups",
    "created_at": "2018-04-02T10:35:27.000000",
    "updated_at": "2018-04-03T10:35:27.000000",
    "description": 'description',
    "fail_reason": 'fail reason',
    "id": FAKE_ID,
    "name": "backup001",
    "object_count": 22,
    "size": 1,
    "status": "available",
    "volume_id": "e5185058-943a-4cb4-96d9-72c184c337d6",
    "is_incremental": True,
    "has_dependent_backups": False
}

DETAILS = {
}

BACKUP_DETAIL = copy.copy(BACKUP)
BACKUP_DETAIL.update(DETAILS)


class TestBackup(base.TestCase):

    def setUp(self):
        super(TestBackup, self).setUp()
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.get = mock.Mock()
        self.sess.default_microversion = mock.Mock(return_value='')

    def test_basic(self):
        sot = backup.Backup(BACKUP)
        self.assertEqual("backup", sot.resource_key)
        self.assertEqual("backups", sot.resources_key)
        self.assertEqual("/backups", sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_fetch)

        self.assertDictEqual(
            {
                "all_tenants": "all_tenants",
                "limit": "limit",
                "marker": "marker",
                "sort_dir": "sort_dir",
                "sort_key": "sort_key"
            },
            sot._query_mapping._mapping
        )

    def test_create(self):
        sot = backup.Backup(**BACKUP)
        self.assertEqual(BACKUP["id"], sot.id)
        self.assertEqual(BACKUP["name"], sot.name)
        self.assertEqual(BACKUP["status"], sot.status)
        self.assertEqual(BACKUP["container"], sot.container)
        self.assertEqual(BACKUP["availability_zone"], sot.availability_zone)
        self.assertEqual(BACKUP["created_at"], sot.created_at)
        self.assertEqual(BACKUP["updated_at"], sot.updated_at)
        self.assertEqual(BACKUP["description"], sot.description)
        self.assertEqual(BACKUP["fail_reason"], sot.fail_reason)
        self.assertEqual(BACKUP["volume_id"], sot.volume_id)
        self.assertEqual(BACKUP["object_count"], sot.object_count)
        self.assertEqual(BACKUP["is_incremental"], sot.is_incremental)
        self.assertEqual(BACKUP["size"], sot.size)
        self.assertEqual(BACKUP["has_dependent_backups"],
                         sot.has_dependent_backups)


class TestBackupDetail(base.TestCase):

    def test_basic(self):
        sot = backup.BackupDetail(BACKUP_DETAIL)
        self.assertIsInstance(sot, backup.Backup)
        self.assertEqual("/backups/detail", sot.base_path)

    def test_create(self):
        sot = backup.Backup(**BACKUP_DETAIL)
        self.assertEqual(BACKUP_DETAIL["id"], sot.id)
        self.assertEqual(BACKUP_DETAIL["name"], sot.name)
        self.assertEqual(BACKUP_DETAIL["status"], sot.status)
        self.assertEqual(BACKUP_DETAIL["container"], sot.container)
        self.assertEqual(BACKUP_DETAIL["availability_zone"],
                         sot.availability_zone)
        self.assertEqual(BACKUP_DETAIL["created_at"], sot.created_at)
        self.assertEqual(BACKUP_DETAIL["updated_at"], sot.updated_at)
        self.assertEqual(BACKUP_DETAIL["description"], sot.description)
        self.assertEqual(BACKUP_DETAIL["fail_reason"], sot.fail_reason)
        self.assertEqual(BACKUP_DETAIL["volume_id"], sot.volume_id)
        self.assertEqual(BACKUP_DETAIL["object_count"], sot.object_count)
        self.assertEqual(BACKUP_DETAIL["is_incremental"], sot.is_incremental)
        self.assertEqual(BACKUP_DETAIL["size"], sot.size)
        self.assertEqual(BACKUP_DETAIL["has_dependent_backups"],
                         sot.has_dependent_backups)
