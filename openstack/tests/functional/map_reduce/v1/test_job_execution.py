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


def auto_create_job_execution(conn, name):
    binary = {
        "name": name,
        "url": "/sdk/mapreduce/input1",
        "is_protected": False,
        "is_public": False,
        "description": ""
    }
    return conn.map_reduce.create_job_execution(**binary)


class TestJobExecution(base.BaseFunctionalTest):
    """Functional test for job execution

    !!!! Not finished, don't know how to create an execution for now
    """
    NAME = "SDK-" + uuid.uuid4().hex
    execution = None

    @classmethod
    def setUpClass(cls):
        super(TestJobExecution, cls).setUpClass()
        cls.execution = auto_create_job_execution(cls.conn, cls.NAME)

    @classmethod
    def tearDownClass(cls):
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
