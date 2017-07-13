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

from openstack.load_balancer.v1 import job as _job
from openstack import resource2
from openstack.tests.functional import base
from openstack.tests.functional.load_balancer.v1 import test_listener
from openstack.tests.functional.load_balancer.v1 import test_load_balancer


def auto_create_health_check(conn, listener_id):
    """auto create a load balancer listener for functional test

    :param conn:
    :param listener_id: listener id this health check belongs to
    :return:
    """
    health_check = {
        "listener_id": listener_id,
        "healthcheck_protocol": "HTTP",
        "healthcheck_connect_port": 80,
        "healthcheck_interval": 5,
        "healthcheck_timeout": 10,
        "healthcheck_uri": "/health",
        "healthy_threshold": 3,
        "unhealthy_threshold": 3
    }
    return conn.load_balancer.create_health_check(**health_check)


class TestHealthCheck(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex
    lb = None
    listener = None
    health_check = None

    @classmethod
    def setUpClass(cls):
        super(TestHealthCheck, cls).setUpClass()
        # create an external load balancer
        router = cls.get_first_router()
        cls.lb = test_load_balancer.auto_create_external_lb(cls.conn,
                                                            cls.NAME,
                                                            router.id)
        # create a listener
        cls.listener = test_listener.auto_create_listener(cls.conn,
                                                          cls.NAME,
                                                          cls.lb.id)
        # create health check
        cls.health_check = auto_create_health_check(cls.conn, cls.listener.id)

    @classmethod
    def tearDownClass(cls):
        # delete health check created in setup
        cls.conn.load_balancer.delete_health_check(cls.health_check)
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

    def test_update_health_check(self):
        updated = {
            "healthcheck_connect_port": 88,
            "healthcheck_interval": 5,
            "healthcheck_protocol": "HTTP",
            "healthcheck_timeout": 10,
            "healthcheck_uri": "/",
            "healthy_threshold": 3,
            "unhealthy_threshold": 2
        }

        health_check = self.conn.load_balancer.update_health_check(
            self.health_check, **updated)

        self.assertEqual(88, health_check.healthcheck_connect_port)
        self.assertEqual(5, health_check.healthcheck_interval)
        self.assertEqual("HTTP", health_check.healthcheck_protocol)
        self.assertEqual(10, health_check.healthcheck_timeout)
        self.assertEqual("/", health_check.healthcheck_uri)
        self.assertEqual(3, health_check.healthy_threshold)
        self.assertEqual(2, health_check.unhealthy_threshold)
        self.health_check = health_check

    def test_get_health_check(self):
        health_check = self.conn.load_balancer.get_health_check(
            self.health_check)
        self.assertEqual(self.health_check, health_check)
