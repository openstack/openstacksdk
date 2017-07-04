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
from openstack.tests.functional import base
from openstack.tests.functional.dns.v2 import test_zone


def auto_create_recordset(conn, zone, name):
    recordset = {
        "name": name,
        "description": "SDK unittests",
        "type": "A",
        "ttl": 3600,
        "records": [
            "192.168.10.1",
            "192.168.10.2"
        ]
    }

    return conn.dns.create_recordset(zone, **recordset)


class TestRecordset(base.BaseFunctionalTest):
    ZONE_NAME = uuid.uuid4().hex + ".unittest.com."
    NAME = "SDK-" + uuid.uuid4().hex + "." + ZONE_NAME
    zone = None
    recordset = None
    router = None
    router2 = None

    @classmethod
    def setUpClass(cls):
        super(TestRecordset, cls).setUpClass()
        # get a router
        cls.router = cls.get_first_router()
        # create zone for test
        cls.zone = test_zone.auto_create_private_zone(cls.conn,
                                                      cls.ZONE_NAME,
                                                      cls.router.id,
                                                      "eu-de")
        # waiting until zone's status turn into ACTIVE
        resource2.wait_for_status(cls.conn.dns._session,
                                  cls.zone,
                                  "ACTIVE",
                                  interval=5,
                                  failures=["ERROR"])
        cls.recordset = auto_create_recordset(cls.conn, cls.zone, cls.NAME)

    @classmethod
    def tearDownClass(cls):
        #: delete zone
        cls.conn.dns.delete_recordset(cls.zone, cls.recordset)
        cls.conn.dns.delete_zone(cls.zone)

    def test_1_get_recordset(self):
        recordset = self.conn.dns.get_recordset(self.zone, self.recordset)
        self.assertEqual(recordset.id, self.recordset.id)
        self.assertEqual(recordset.name, str(self.NAME).lower())
        self.assertEqual(recordset.description, "SDK unittests")
        self.assertEqual(recordset.type, "A")
        self.assertEqual(recordset.ttl, 3600)
        self.assertListEqual(recordset.records,
                             ["192.168.10.2", "192.168.10.1"])

    def test_2_list_recordset(self):
        recordsets = list(self.conn.dns.recordsets(self.zone, limit=50))
        found = False
        for recordset in recordsets:
            if recordset.id == self.recordset.id:
                found = True
        self.assertTrue(found)

    def test_3_list_all_recordsets(self):
        recordsets = list(self.conn.dns.all_recordsets(limit=50))
        found = False
        for recordset in recordsets:
            if recordset.id == self.recordset.id:
                found = True
        self.assertTrue(found)
