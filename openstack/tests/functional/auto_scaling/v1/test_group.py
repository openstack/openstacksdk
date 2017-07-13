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
from openstack.tests.functional import base


def auto_create_group(conn, group_name, config_id):
    # routers = conn.network.routers(limit=1)
    # router = None
    # for _router in routers:
    #     router = _router
    #     break
    #
    # security_group = None
    # security_groups = conn.network.security_groups(limit=1)
    # for _security_group in security_groups:
    #     security_group = _security_group
    #     break
    #
    # if not router or not security_group:
    #     raise Exception("VPC/Network/SecurityGroup is not realy")

    # ok.. we just use fixed vpc/network/sg here
    vpc_id = "31d158b8-e7d7-4b4a-b2a7-a5240296b267"
    network_id = "85d0d006-44f9-4f32-8384-7f8a8198bed6"
    sg_id = "0005ba27-b937-4a7c-a280-c7b65cea2e47"
    return create_group(conn,
                        group_name,
                        config_id,
                        vpc_id,
                        [{"id": network_id}],
                        [{"id": sg_id}])


def create_group(conn, group_name, config_id, vpc_id, networks,
                 security_groups):
    _group = {
        "name": group_name,
        "scaling_configuration_id": config_id,
        "desire_instance_number": 1,
        "min_instance_number": 0,
        "max_instance_number": 3,
        "cool_down_time": 200,
        "health_periodic_audit_method": "NOVA_AUDIT",
        "health_periodic_audit_time": "5",
        "instance_terminate_policy": "OLD_CONFIG_OLD_INSTANCE",
        "vpc_id": vpc_id,
        "networks": networks,
        "security_groups": security_groups,
        "notifications": ["EMAIL"]
    }

    return conn.auto_scaling.create_group(**_group)


class TestGroup(base.BaseFunctionalTest):
    GROUP_NAME = "SDK-" + uuid.uuid4().hex
    group = None

    @classmethod
    def setUpClass(cls):
        super(TestGroup, cls).setUpClass()
        cls.config = auto_create_config(cls.conn, cls.GROUP_NAME)
        cls.group = auto_create_group(cls.conn, cls.GROUP_NAME, cls.config.id)

    @classmethod
    def tearDownClass(cls):
        cls.conn.auto_scaling.delete_group(cls.group)
        cls.conn.auto_scaling.delete_config(cls.config)

    def test_list_group(self):
        groups = list(self.conn.auto_scaling.groups(name=self.GROUP_NAME))
        self.assertEqual(1, len(list(groups)))
        self.assertEqual(self.group.id, groups[0].id)

    def test_get_group(self):
        _group = self.conn.auto_scaling.get_group(self.group.id)
        self.assertEqual(_group.id, self.group.id)

    def test_group_actions(self):
        self.conn.auto_scaling.pause_group(self.group)
        self.group = self.conn.auto_scaling.get_group(self.group)
        self.assertEqual("PAUSED", self.group.status)

        self.conn.auto_scaling.resume_group(self.group)
        self.group = self.conn.auto_scaling.get_group(self.group)
        self.assertEqual("INSERVICE", self.group.status)
