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


from openstack.network.v2 import firewall_policy
from openstack.tests.functional import base


class TestFirewallPolicy(base.BaseFunctionalTest):
    ID = None

    def setUp(self):
        super().setUp()
        if not self.user_cloud._has_neutron_extension("fwaas_v2"):
            self.skipTest("fwaas_v2 service not supported by cloud")
        self.NAME = self.getUniqueString()
        sot = self.user_cloud.network.create_firewall_policy(name=self.NAME)
        assert isinstance(sot, firewall_policy.FirewallPolicy)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id

    def tearDown(self):
        sot = self.user_cloud.network.delete_firewall_policy(
            self.ID, ignore_missing=False
        )
        self.assertIs(None, sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_firewall_policy(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.user_cloud.network.get_firewall_policy(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        names = [o.name for o in self.user_cloud.network.firewall_policies()]
        self.assertIn(self.NAME, names)
