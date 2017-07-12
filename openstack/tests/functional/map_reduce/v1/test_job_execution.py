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
from openstack.tests.functional.map_reduce.v1 import test_job
from openstack.tests.functional.map_reduce.v1 import test_job_binary


def auto_create_job_execution(conn, cluster_id, job, name):
    input_ = test_job_binary.auto_create_job_binary(
        conn, name + "-input", "s3a://sdk-unittest/input")
    output = test_job_binary.auto_create_job_binary(
        conn, name + "-output", "s3a://sdk-unittest/output")

    execution = {
        "cluster_id": cluster_id,
        "input_id": input_.id,
        "output_id": output.id,
        "is_protected": False,
        "is_public": False,
        "job_configs": {
            "args": [
                "wordcount"
            ]
        }
    }
    return conn.map_reduce.execute_job(job, **execution)


def auto_delete_job_execution(conn, execution):
    conn.map_reduce.delete_job_execution(execution)
    conn.map_reduce.delete_job_binary(execution.input_id)
    conn.map_reduce.delete_job_binary(execution.output_id)


class TestJobExecution(base.BaseFunctionalTest):
    """Functional test for job execution

    !!!! Not finished, don't know how to create an execution for now
    """
    NAME = "SDK-" + uuid.uuid4().hex
    job = None
    execution = None
    cluster_id = "0f4ab6b7-a723-4b6c-b326-f8a5711d365a"

    @classmethod
    def setUpClass(cls):
        super(TestJobExecution, cls).setUpClass()
        cls.job = test_job.auto_create_job(cls.conn, cls.NAME)
        cls.execution = auto_create_job_execution(cls.conn,
                                                  cls.cluster_id,
                                                  cls.job,
                                                  cls.NAME)

    @classmethod
    def tearDownClass(cls):
        test_job.auto_delete_job(cls.job)
        cls.conn.map_reduce.delete_job_execution(cls.execution)

    def get_current_binary(self):
        query = dict(sort_by="-created_at")
        job_binaries = list(self.conn.map_reduce.job_binaries(**query))
        for ds in job_binaries:
            if ds.id == self.execution.id:
                return ds
        return None

    def test_1_list_job_execution(self):
        binary = self.get_current_binary()
        self.assertIsNotNone(binary)

    def test_2_get_job_execution(self):
        _binary = self.conn.map_reduce.get_job_execution(self.execution)
        self.assertEqual(_binary.id, self.execution.id)
        self.assertEqual(self.NAME, _binary.name)
        self.assertEqual("/sdk/mapreduce/input1", _binary.url)
        self.assertEqual("", _binary.description)
