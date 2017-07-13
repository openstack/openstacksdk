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

from openstack import resource2
from openstack.load_balancer.v1 import job as _job
from openstack.tests.functional import base
from openstack.tests.functional.load_balancer.v1 import test_load_balancer


def auto_create_listener(conn, name, lb_id):
    """auto create a load balancer listener for functional test

    :param conn:
    :param name:
    :param lb_id:
    :return:
    """
    listener = {
        "name": name,
        "loadbalancer_id": lb_id,
        "protocol": "HTTP",
        "port": 10086,
        "backend_protocol": "HTTP",
        "backend_port": 80,
        "lb_algorithm": "roundrobin",
        "is_session_sticky": True,
        "sticky_session_type": "insert",
        "cookie_timeout": 60
    }
    return conn.load_balancer.create_listener(**listener)


class TestListener(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex
    lb = None
    listener = None
    router = None

    @classmethod
    def setUpClass(cls):
        super(TestListener, cls).setUpClass()
        # create an external load balancer
        router = cls.get_first_router()
        cls.lb = test_load_balancer.auto_create_external_lb(cls.conn,
                                                            cls.NAME,
                                                            router.id)
        # create a listener
        cls.listener = auto_create_listener(cls.conn, cls.NAME, cls.lb.id)

    @classmethod
    def tearDownClass(cls):
        # delete listener created in setup
        cls.conn.load_balancer.delete_listener(cls.listener)
        # delete load balancer created in setup
        job = cls.conn.load_balancer.delete_load_balancer(cls.lb)
        job = _job.Job(id=job.job_id)
        resource2.wait_for_status(cls.conn.load_balancer._session,
                                  job,
                                  "SUCCESS",
                                  interval=5,
                                  failures=["FAIL"])

    def test_list_listener(self):
        query = dict(name=self.NAME)
        listeners = list(self.conn.load_balancer.listeners(**query))
        self.assertEqual(1, len(list(listeners)))
        self.assertEqual(self.listener.id, listeners[0].id)

    def test_update_listener(self):
        updated = {
            "description": "listener created by functional test",
            "port": 10000
        }
        listener = self.conn.load_balancer.update_listener(self.listener,
                                                           **updated)

        self.assertEqual(updated["description"], listener.description)
        self.assertEqual(updated["port"], listener.port)
        self.listener = listener

    def test_get_listener(self):
        listener = self.conn.load_balancer.get_listener(self.listener)
        self.assertEqual(self.listener, listener)

    def test_operate_members(self):
        members = []
        servers = self.conn.compute.servers()
        for server in servers:
            vpc_list = server.addresses.keys()
            if self.router.id in vpc_list:
                addr = server.addresses[self.router.id][0]["addr"]
                members.append(dict(server_id=server.id, address=addr))
                if len(members) == 2:
                    break

        job = self.conn.load_balancer.add_members_to_listener(self.listener,
                                                              members)
        # waiting for add members job done
        job = _job.Job(id=job.id)
        resource2.wait_for_status(self.conn.load_balancer._session,
                                  job,
                                  "SUCCESS",
                                  interval=5,
                                  failures=["FAIL"])

        added_members = self.conn.load_balancer.listener_members(self.listener)
        self.assertEqual(2, len(list(added_members)))

        member_ids = [member["server_id"] for member in members]
        job = self.conn.load_balancer.remove_members_of_listener(self.listener,
                                                                 member_ids)
        job = _job.Job(id=job.id)
        resource2.wait_for_status(self.conn.load_balancer._session,
                                  job,
                                  "SUCCESS",
                                  interval=5,
                                  failures=["FAIL"])

        added_members = self.conn.load_balancer.listener_members(self.listener)
        self.assertEqual(0, len(list(added_members)))
