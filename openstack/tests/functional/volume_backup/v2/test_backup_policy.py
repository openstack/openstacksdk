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


def create_backup_policy(conn, name):
    data = {
        "remain_first_backup_of_curMonth": True,
        "rentention_num": 10,
        "frequency": 1,
        "start_time": "12:00",
        "status": "ON"
    }
    return conn.volume_backup.create_backup_policy(name, **data)


class TestBackupPolicy(base.BaseFunctionalTest):
    BACKUP_POLICY_NAME = "SDK-" + uuid.uuid4().hex
    policy = None
    volume = None

    @classmethod
    def setUpClass(cls):
        super(TestBackupPolicy, cls).setUpClass()
        for volume in cls.conn.block_store.volumes(limit=1):
            cls.volume = volume
            break
        if not cls.volume:
            raise Exception("no exists volume for test")
        # create backup policy
        cls.policy = create_backup_policy(cls.conn, cls.BACKUP_POLICY_NAME)

    @classmethod
    def tearDownClass(cls):
        #: delete backup policy
        cls.conn.volume_backup.unlink_resources_of_policy(cls.policy,
                                                          [cls.volume.id])
        cls.conn.volume_backup.delete_backup_policy(cls.policy)

    def get_current_policy(self):
        policies = list(self.conn.volume_backup.backup_policies())
        for policy in policies:
            if policy.id == self.policy.id:
                return policy

    def test_list_backup_policies(self):
        policies = list(self.conn.volume_backup.backup_policies())
        self.assertIn(self.policy.name, [p.name for p in policies])

    def test_update_backup_policy(self):
        updated = {
            "scheduled_policy": {
                "frequency": 5,
                "start_time": "01:00"
            }
        }
        self.conn.volume_backup.update_backup_policy(self.policy, **updated)
        policy = self.get_current_policy()
        self.assertEqual(5, policy.scheduled_policy.frequency)
        self.assertEqual("01:00", policy.scheduled_policy.start_time)
        self.policy = policy

    def test_bind_and_execute(self):
        if self.policy.scheduled_policy.status == "OFF":
            self.conn.volume_backup.enable_policy(self.policy)

        self.conn.volume_backup.link_resources_to_policy(self.policy,
                                                         [self.volume.id])
        self.conn.volume_backup.execute_policy(self.policy)

    def test_enable_disable_policy(self):
        if self.policy.scheduled_policy.status == "ON":
            self.conn.volume_backup.disable_policy(self.policy)
            policy = self.get_current_policy()
            self.assertEqual("OFF", policy.scheduled_policy.status)
        self.conn.volume_backup.enable_policy(self.policy)
        self.assertEqual("ON", self.policy.scheduled_policy.status)
