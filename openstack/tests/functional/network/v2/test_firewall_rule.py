# Copyright (c) 2018 China Telecom Corporation
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from openstack.network.v2 import firewall_rule
from openstack.tests.functional import base


class TestFirewallRule(base.BaseFunctionalTest):
    ACTION = "allow"
    DEST_IP = "10.0.0.0/24"
    DEST_PORT = "80"
    IP_VERSION = 4
    PROTOCOL = "tcp"
    SOUR_IP = "10.0.1.0/24"
    SOUR_PORT = "8000"
    ID = None

    def setUp(self):
        super().setUp()
        if not self.user_cloud._has_neutron_extension("fwaas_v2"):
            self.skipTest("fwaas_v2 service not supported by cloud")
        self.NAME = self.getUniqueString()
        sot = self.user_cloud.network.create_firewall_rule(
            name=self.NAME,
            action=self.ACTION,
            source_port=self.SOUR_PORT,
            destination_port=self.DEST_PORT,
            source_ip_address=self.SOUR_IP,
            destination_ip_address=self.DEST_IP,
            ip_version=self.IP_VERSION,
            protocol=self.PROTOCOL,
        )
        assert isinstance(sot, firewall_rule.FirewallRule)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id

    def tearDown(self):
        sot = self.user_cloud.network.delete_firewall_rule(
            self.ID, ignore_missing=False
        )
        self.assertIs(None, sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_firewall_rule(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.user_cloud.network.get_firewall_rule(self.ID)
        self.assertEqual(self.ID, sot.id)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ACTION, sot.action)
        self.assertEqual(self.DEST_IP, sot.destination_ip_address)
        self.assertEqual(self.DEST_PORT, sot.destination_port)
        self.assertEqual(self.IP_VERSION, sot.ip_version)
        self.assertEqual(self.SOUR_IP, sot.source_ip_address)
        self.assertEqual(self.SOUR_PORT, sot.source_port)

    def test_list(self):
        ids = [o.id for o in self.user_cloud.network.firewall_rules()]
        self.assertIn(self.ID, ids)
