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


class TestInstance(base.BaseFunctionalTest):
    POLICY_NAME = "Qianbiao-" + uuid.uuid4().hex
    group = "588b4592-0998-4722-b51d-e6dbc574ec32"
    config = None
    instances = None

    # @classmethod
    # def setUpClass(cls):
    #     super(TestInstance, cls).setUpClass()
    #     cls.config = auto_create_config(cls.conn, cls.POLICY_NAME)
    #     cls.group = auto_create_group(cls.conn, cls.POLICY_NAME,
    #                                   cls.config.id)
    #     cls.policy = create_policy(cls.conn, cls.POLICY_NAME, cls.group.id)
    #     cls.conn.auto_scaling.resume_group(cls.group)
    #     cls.conn.auto_scaling.execute_policy(cls.policy)
    #     cls.instances = list(cls.conn.auto_scaling.instances(cls.group))
    #
    # @classmethod
    # def tearDownClass(cls):
    #     cls.conn.auto_scaling.delete_group(cls.group)
    #     cls.conn.auto_scaling.delete_config(cls.config)
    #     cls.conn.auto_scaling.delete_policy(cls.policy)

    def test_instances(self):
        self.instances = list(self.conn.auto_scaling.instances(self.group))
        self.assertEqual(2, len(self.instances))

        self.conn.auto_scaling.remove_instance(self.instances[0].id,
                                               delete_instance=False)
        instances = list(self.conn.auto_scaling.instances(self.group))
        self.assertEqual(1, len(instances))

        self.conn.auto_scaling.batch_remove_instances(self.group,
                                                      self.instances)
        instances = list(self.conn.auto_scaling.instances(self.group.id))
        self.assertEqual(0, len(self.instances))

        self.conn.auto_scaling.batch_add_instances(self.group,
                                                   self.instances)
        instances = list(self.conn.auto_scaling.instances(self.group))
        self.assertEqual(2, len(instances))

    def test_batch_add(self):
        instances = ["7f8e7f05-0323-4d5f-9e48-445da24e1cee"]
        self.conn.auto_scaling.batch_add_instances(self.group,
                                                   instances)
        instances = list(self.conn.auto_scaling.instances(self.group))
        self.assertEqual(2, len(instances))

    def test_batch_remove(self):
        instances = ["7f8e7f05-0323-4d5f-9e48-445da24e1cee"]
        self.conn.auto_scaling.batch_remove_instances(self.group,
                                                      instances,
                                                      delete_instance=True)
