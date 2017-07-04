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


def auto_create_private_zone(conn, name, router_id, router_region):
    _zone = {
        "name": name,
        "description": "SDK unittest",
        "zone_type": "private",
        "email": "admin@unittest.com",
        "ttl": 500,
        "router": {
            "router_id": router_id,
            "router_region": router_region
        }
    }
    return conn.dns.create_zone(**_zone)


class TestZone(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex + ".unittest.com."
    zone = None
    router = None
    router2 = None

    @classmethod
    def setUpClass(cls):
        super(TestZone, cls).setUpClass()
        # get a router
        routers = cls.conn.network.routers(limit=2)
        idx = 0
        for _router in routers:
            idx += 1
            if idx == 1:
                cls.router = _router
            if idx == 2:
                cls.router2 = _router
                break
        # create zone for test
        cls.zone = auto_create_private_zone(cls.conn, cls.NAME, cls.router.id,
                                            "eu-de")

    @classmethod
    def tearDownClass(cls):
        #: delete zone
        cls.conn.dns.delete_zone(cls.zone)

    def test_1_get_zone(self):
        zone = self.conn.dns.get_zone(self.zone)
        self.assertEqual(zone.id, self.zone.id)
        self.assertEqual(zone.name, str(self.NAME).lower())
        self.assertEqual(zone.description, "SDK unittest")
        self.assertEqual(zone.zone_type, "private")
        self.assertEqual(zone.email, "admin@unittest.com")
        self.assertEqual(zone.ttl, 500)
        self.assertEqual(zone.router.router_id, self.router.id)
        self.assertEqual(zone.router.router_region, "eu-de")

    def test_2_list_zone(self):
        zones = list(self.conn.dns.zones(limit=50))
        found = False
        for zone in zones:
            if zone.id == self.zone.id:
                found = True
        self.assertTrue(found)

    def test_3_list_nameserver(self):
        nameservers = list(self.conn.dns.nameservers(self.zone))
        self.assertTrue(len(nameservers) > 0)

    def test_4_add_router_to_zone(self):
        resource2.wait_for_status(self.conn.dns._session,
                                  self.zone,
                                  "ACTIVE",
                                  interval=5,
                                  failures=["ERROR"])
        result = self.conn.dns.add_router_to_zone(self.zone, **{
            "router_id": self.router2.id,
            "router_region": "eu-de"
        })
        self.assertEqual(result.router_id, self.router2.id)
        self.assertEqual(result.router_region, "eu-de")

        zone = self.conn.dns.get_zone(self.zone)
        self.assertEqual(2, len(zone.routers))
        router_ids = [_router["router_id"] for _router in zone.routers]
        self.assertIn(self.router.id, router_ids)

    def test_5_remove_router_of_zone(self):
        resource2.wait_for_status(self.conn.dns._session,
                                  self.zone,
                                  "ACTIVE",
                                  interval=5,
                                  failures=["ERROR"])
        result = self.conn.dns.remove_router_from_zone(self.zone, **{
            "router_id": self.router.id,
            "router_region": "eu-de"
        })
        self.assertEqual(result.router_id, self.router.id)
        self.assertEqual(result.router_region, "eu-de")
