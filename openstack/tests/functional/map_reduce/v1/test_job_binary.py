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


def auto_create_job_binary(conn, name, url):
    binary = {
        "name": name,
        "url": url,
        "is_protected": False,
        "is_public": False,
        "description": ""
    }
    return conn.map_reduce.create_job_binary(**binary)


class TestJobBinary(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex
    binary = None

    @classmethod
    def setUpClass(cls):
        super(TestJobBinary, cls).setUpClass()
        cls.binary = auto_create_job_binary(cls.conn, cls.NAME)

    @classmethod
    def tearDownClass(cls):
        cls.conn.map_reduce.delete_job_binary(cls.binary)

    def get_current_binary(self):
        query = dict(sort_by="-created_at")
        job_binaries = list(self.conn.map_reduce.job_binaries(**query))
        for ds in job_binaries:
            if ds.id == self.binary.id:
                return ds
        return None

    def test_1_list_job_binary(self):
        binary = self.get_current_binary()
        self.assertIsNotNone(binary)

    def test_2_get_job_binary(self):
        _binary = self.conn.map_reduce.get_job_binary(self.binary)
        self.assertEqual(_binary.id, self.binary.id)
        self.assertEqual(self.NAME, _binary.name)
        self.assertEqual("/sdk/mapreduce/input1", _binary.url)
        self.assertEqual("", _binary.description)

    def test_3_update_job_binary(self):
        updated = {
            "url": "/sdk/unittest/input1",
            "description": "SDK unittests"
        }
        _binary = self.conn.map_reduce.update_job_binary(self.binary,
                                                         **updated)
        self.assertEqual(_binary.id, self.binary.id)
        self.assertEqual(self.NAME, _binary.name)
        self.assertEqual("/sdk/unittest/input1", _binary.url)
        self.assertEqual("SDK unittests", _binary.description)
