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


def auto_create_external_lb(conn, name, vpc_id):
    """auto create a lb for functional test

    :param conn:
    :param name:
    :return:
    """
    _lb = {
        "name": name,
        "vpc_id": vpc_id,
        "bandwidth": 1,
        "type": "External",
        "is_admin_state_up": True
    }
    job = conn.load_balancer.create_load_balancer(**_lb)
    job = _job.Job(id=job.job_id)
    resource2.wait_for_status(conn.load_balancer._session,
                              job,
                              "SUCCESS",
                              interval=3,
                              failures=["FAIL"])
    elb_id = job.entities["elb"]["id"]
    return conn.load_balancer.get_load_balancer(elb_id)


class TestLoadBalancer(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex
    lb = None

    @classmethod
    def setUpClass(cls):
        super(TestLoadBalancer, cls).setUpClass()
        # create an external load balancer
        router = cls.get_first_router()
        cls.lb = auto_create_external_lb(cls.conn, cls.NAME, router.id)

    @classmethod
    def tearDownClass(cls):
        job = cls.conn.load_balancer.delete_load_balancer(cls.lb)
        job = _job.Job(id=job.job_id)
        resource2.wait_for_status(cls.conn.load_balancer._session,
                                  job,
                                  "SUCCESS",
                                  interval=3,
                                  failures=["FAIL"])

    def test_list_lb(self):
        query = dict(name=self.NAME)
        lbs = list(self.conn.load_balancer.load_balancers(**query))
        self.assertEqual(1, len(list(lbs)))
        self.assertEqual(self.lb.id, lbs[0].id)

    def test_update_lb(self):
        updated = {
            "description": "lb created by functional test",
            "bandwidth": 2,
            "admin_state_up": True
        }
        job = self.conn.load_balancer.update_load_balancer(self.lb, **updated)
        job = _job.Job(id=job.job_id)
        resource2.wait_for_status(self.conn.load_balancer._session,
                                  job,
                                  "SUCCESS",
                                  interval=3,
                                  failures=["FAIL"])
        self.conn.load_balancer.wait_for_status(job, "SUCCESS", interval=2)
        lb = self.conn.load_balancer.get_load_balancer(self.lb)
        self.assertEqual(updated["description"], lb.description)
        self.assertEqual(updated["bandwidth"], lb.bandwidth)
        self.assertEqual(updated["admin_state_up"], lb.is_admin_state_up)
        self.lb = lb
