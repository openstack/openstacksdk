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

from openstack.tests.functional.auto_scaling.v1.test_config import \
    auto_create_config
from openstack.tests.functional.auto_scaling.v1.test_group import \
    auto_create_group
from openstack.tests.functional import base


def create_policy(conn, policy_name, group_id):
    _policy = {
        "name": policy_name,
        "scaling_policy_action": {
            "operation": "ADD",
            "instance_number": 1
        },
        "cool_down_time": 900,
        "scheduled_policy": {
            "launch_time": "16:00",
            "recurrence_type": "Daily",
            "recurrence_value": None,
            "start_time": "2017-07-14T03:34Z",
            "end_time": "2017-07-27T03:34Z"
        },
        "type": "RECURRENCE",
        "scaling_group_id": group_id
    }

    return conn.auto_scaling.create_policy(**_policy)


class TestPolicy(base.BaseFunctionalTest):
    POLICY_NAME = "SDK-" + uuid.uuid4().hex
    policy = None
    group = None
    config = None

    @classmethod
    def setUpClass(cls):
        super(TestPolicy, cls).setUpClass()
        cls.config = auto_create_config(cls.conn, cls.POLICY_NAME)
        cls.group = auto_create_group(cls.conn, cls.POLICY_NAME, cls.config.id)
        cls.policy = create_policy(cls.conn, cls.POLICY_NAME, cls.group.id)

    @classmethod
    def tearDownClass(cls):
        cls.conn.auto_scaling.delete_policy(cls.policy)
        cls.conn.auto_scaling.delete_group(cls.group)
        cls.conn.auto_scaling.delete_config(cls.config)

    def test_list_policy(self):
        policies = list(self.conn.auto_scaling.policies(self.group.id,
                                                        name=self.POLICY_NAME))
        self.assertEqual(1, len(list(policies)))
        self.assertEqual(self.policy.id, policies[0].id)

    def test_get_policy(self):
        _policy = self.conn.auto_scaling.get_policy(self.policy.id)
        self.assertEqual(_policy.id, self.policy.id)

    def test_delete_policy(self):
        name = "SDK-" + uuid.uuid4().hex
        created = create_policy(self.conn,
                                name,
                                self.policy.scaling_group_id)
        self.conn.auto_scaling.delete_policy(created)

        ids = [p.id for p in self.conn.auto_scaling.policies(self.group.id)]
        self.assertNotIn(created.id, ids)

    def test_policy_actions(self):
        self.conn.auto_scaling.resume_policy(self.policy.id)
        self.policy = self.conn.auto_scaling.get_policy(self.policy.id)
        self.assertEqual("INSERVICE", self.policy.status)

        self.conn.auto_scaling.pause_policy(self.policy.id)
        self.policy = self.conn.auto_scaling.get_policy(self.policy.id)
        self.assertEqual("PAUSED", self.policy.status)

    def test_update_policy(self):
        new_name = "SDK-" + uuid.uuid4().hex
        self.conn.auto_scaling.update_policy(self.policy,
                                             name=new_name,
                                             cool_down_time=300)
        self.policy = self.conn.auto_scaling.get_policy(self.policy)
        self.assertEqual(new_name, self.policy.name)
        self.assertEqual(300, self.policy.cool_down_time)
