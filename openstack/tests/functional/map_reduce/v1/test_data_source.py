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


def auto_create_data_source(conn, name):
    ds = {
        "name": name,
        "url": "/sdk/unittest/input",
        "is_protected": False,
        "is_public": False,
        "type": "hdfs",
        "description": ""
    }
    return conn.map_reduce.create_data_source(**ds)


class TestDataSource(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex
    ds = None

    @classmethod
    def setUpClass(cls):
        super(TestDataSource, cls).setUpClass()
        # prepare a data-source
        cls.ds = auto_create_data_source(cls.conn, cls.NAME)

    @classmethod
    def tearDownClass(cls):
        cls.conn.map_reduce.delete_data_source(cls.ds)

    def get_current_ds(self):
        query = dict(sort_by="-created_at")
        data_sources = list(self.conn.map_reduce.data_sources(**query))
        for ds in data_sources:
            if ds.id == self.ds.id:
                return ds
        return None

    def test_1_list_data_source(self):
        ds = self.get_current_ds()
        self.assertIsNotNone(ds)

    def test_2_get_data_source(self):
        _ds = self.conn.map_reduce.get_data_source(self.ds)
        self.assertEqual(_ds.id, self.ds.id)
        self.assertEqual(self.NAME, _ds.name)
        self.assertEqual("/sdk/unittest/input", _ds.url)
        self.assertEqual("hdfs", _ds.type)
        self.assertEqual("", _ds.description)

    def test_3_update_data_source(self):
        updated = {
            "url": "/sdk/unittest/input1",
            "description": "SDK unittests"
        }
        _ds = self.conn.map_reduce.update_data_source(self.ds, **updated)
        self.assertEqual(_ds.id, self.ds.id)
        self.assertEqual(self.NAME, _ds.name)
        self.assertEqual("/sdk/unittest/input1", _ds.url)
        self.assertEqual("SDK unittests", _ds.description)
