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

import mock

from keystoneauth1 import adapter

from openstack.tests.unit import base

from openstack import exceptions
from openstack.block_storage.v2 import backup

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


class TestBackup(base.TestCase):

    def setUp(self):
        super(TestBackup, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.headers = {}
        self.resp.status_code = 202

        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.get = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)
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
                "name": "name",
                "project_id": "project_id",
                "sort_dir": "sort_dir",
                "sort_key": "sort_key",
                "status": "status",
                "volume_id": "volume_id"
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

    def test_restore(self):
        sot = backup.Backup(**BACKUP)

        self.assertEqual(sot, sot.restore(self.sess, 'vol', 'name'))

        url = 'backups/%s/restore' % FAKE_ID
        body = {"restore": {"volume_id": "vol", "name": "name"}}
        self.sess.post.assert_called_with(url, json=body)

    def test_restore_name(self):
        sot = backup.Backup(**BACKUP)

        self.assertEqual(sot, sot.restore(self.sess, name='name'))

        url = 'backups/%s/restore' % FAKE_ID
        body = {"restore": {"name": "name"}}
        self.sess.post.assert_called_with(url, json=body)

    def test_restore_vol_id(self):
        sot = backup.Backup(**BACKUP)

        self.assertEqual(sot, sot.restore(self.sess, volume_id='vol'))

        url = 'backups/%s/restore' % FAKE_ID
        body = {"restore": {"volume_id": "vol"}}
        self.sess.post.assert_called_with(url, json=body)

    def test_restore_no_params(self):
        sot = backup.Backup(**BACKUP)

        self.assertRaises(
            exceptions.SDKException,
            sot.restore,
            self.sess
        )
