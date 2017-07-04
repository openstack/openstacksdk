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


def auto_create_ptr(conn, eip_id, domain_name):
    ptr = {
        'region': 'eu-de',
        'floating_ip_id': eip_id,
        'ptrdname': domain_name,
        'description': 'SDK unittests',
        'ttl': 300,
    }

    return conn.dns.create_ptr(**ptr)


class TestPTR(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex + ".unittest.com."
    ptr = None

    @classmethod
    def setUpClass(cls):
        super(TestPTR, cls).setUpClass()
        ips = cls.conn.network.ips(limit=1, status="ACTIVE")
        for _eip in ips:
            cls.eip = _eip
            break
        if not cls.eip:
            raise Exception("no floating ip available for test")
        cls.ptr = auto_create_ptr(cls.conn, cls.eip.id, cls.NAME)

    def test_1_get_ptr(self):
        ptr = self.conn.dns.get_ptr("eu-de", self.eip.id)
        self.assertEqual(ptr.id, self.ptr.id)
        self.assertEqual(ptr.ptrdname.lower(), str(self.NAME).lower())
        self.assertEqual(ptr.description, "SDK unittests")
        self.assertEqual(ptr.address, self.eip.floating_ip_address)
        self.assertEqual(ptr.ttl, 300)

    def test_2_list_ptr(self):
        ptrs = list(self.conn.dns.ptrs(limit=50))
        found = False
        for ptr in ptrs:
            if ptr.id == self.ptr.id:
                found = True
        self.assertTrue(found)

    def test_3_restore_ptrs(self):
        self.conn.dns.restore_ptr("eu-de", self.eip.id)
