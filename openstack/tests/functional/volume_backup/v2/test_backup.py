#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
import uuid

from openstack.tests.functional import base


class TestBackup(base.BaseFunctionalTest):
    BACKUP_NAME = "SDK-" + uuid.uuid4().hex
    volume = None
    job = None

    @classmethod
    def setUpClass(cls):
        super(TestBackup, cls).setUpClass()
        # for volume in cls.conn.block_store.volumes(limit=1):
        #     cls.volume = volume
        #     break
        #
        # # because job is in v1, we could not wait job status ...
        # cls.job = cls.conn.volume_backup.create_backup(**{
        #     "volume_id": cls.volume.id,
        #     "name": cls.BACKUP_NAME,
        #     "description": "created by openstacksdk"
        # })

    @classmethod
    def tearDownClass(cls):
        pass

    def test_list_backup(self):
        query = {
            "name": "SDK-6bc16a311d6349f1abd302d6c99ef906",
            "status": "available",
            "limit": 10
        }
        backups = list(self.conn.volume_backup.backups(**query))
        self.assertEqual(1, len(backups))

        backup = self.conn.volume_backup.get_backup(backups[0])
        self.assertEqual("created by openstacksdk", backup.description)
        job = self.conn.volume_backup.restore_backup(backup,
                                                     backup.volume_id)
        self.assertIsNotNone(job.job_id)

    def test_list_backup_details(self):
        query = {
            "name": "SDK-6bc16a311d6349f1abd302d6c99ef906",
            "status": "available",
            "limit": 10
        }
        backups = list(self.conn.volume_backup.backups(details=True, **query))
        self.assertEqual(1, len(backups))
