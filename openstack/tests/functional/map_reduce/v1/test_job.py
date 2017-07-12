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
from openstack.tests.functional.map_reduce.v1 import test_job_binary


def auto_create_job(conn, name):
    main_ = test_job_binary.auto_create_job_binary(
        conn,
        name + "-main",
        "s3a://sdk-unittest/hadoop-mapreduce-examples-2.7.2.jar"
    )
    job = {
        "name": name,
        "mains": [main_.id],
        "is_protected": False,
        "interface": [],
        "is_public": False,
        "type": "MapReduce",
        "description": "SDK unittest, Feel Free to delete"
    }
    return conn.map_reduce.create_job(**job)


def auto_delete_job(conn, job):
    conn.map_reduce.delete_job(job)
    for main_ in job.mains:
        conn.map_reduce.delete_job_binary(main_["id"])


class TestJob(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex
    job = None
    cluster_id = ""

    @classmethod
    def setUpClass(cls):
        super(TestJob, cls).setUpClass()
        cls.job = auto_create_job(cls.conn, cls.NAME)

    @classmethod
    def tearDownClass(cls):
        auto_delete_job(cls.job)

    def get_current_job(self):
        query = dict(sort_by="-created_at")
        jobs = list(self.conn.map_reduce.jobs(**query))
        for job in jobs:
            if job.id == self.job.id:
                return job
        return None

    def test_1_list_job(self):
        job = self.get_current_job()
        self.assertIsNotNone(job)

    def test_2_get_job(self):
        _job = self.conn.map_reduce.get_job(self.job)
        self.assertEqual(self.job.id, _job.id)
        self.assertEqual(self.NAME, _job.name)
        self.assertEqual("MapReduce", _job.type)
        self.assertEqual("SDK unittest, Feel Free to delete",
                         _job.description)
        self.assertEqual(self.job.libs, _job.libs)

    def test_3_update_job(self):
        updated = {
            "description": "SDK Unittets",
            "is_public": True,
            "is_protected": True
        }
        _job = self.conn.map_reduce.update_job(self.job, **updated)
        self.assertEqual(_job.id, self.job.id)
        self.assertEqual(self.NAME, _job.name)
        self.assertEqual("SDK Unittets", _job.description)
        self.assertTrue(_job.is_public)
        self.assertTrue(_job.is_protected)

    def test_4_execute_job(self):
        pass

    def test_5_run_job(self):
        pass
