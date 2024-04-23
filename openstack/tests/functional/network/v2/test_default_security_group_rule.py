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

import random

from openstack.network.v2 import default_security_group_rule
from openstack.tests.functional import base


class TestDefaultSecurityGroupRule(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.user_cloud._has_neutron_extension(
            "security-groups-default-rules"
        ):
            self.skipTest(
                "Neutron security-groups-default-rules extension "
                "is required for this test"
            )

        self.IPV4 = random.choice(["IPv4", "IPv6"])
        self.PROTO = random.choice(["tcp", "udp"])
        self.PORT = random.randint(1, 65535)
        self.DIR = random.choice(["ingress", "egress"])
        self.USED_IN_DEFAULT_SG = random.choice([True, False])
        self.USED_IN_NON_DEFAULT_SG = random.choice([True, False])

        rul = self.operator_cloud.network.create_default_security_group_rule(
            direction=self.DIR,
            ethertype=self.IPV4,
            port_range_max=self.PORT,
            port_range_min=self.PORT,
            protocol=self.PROTO,
            used_in_default_sg=self.USED_IN_DEFAULT_SG,
            used_in_non_default_sg=self.USED_IN_NON_DEFAULT_SG,
        )
        assert isinstance(
            rul, default_security_group_rule.DefaultSecurityGroupRule
        )
        self.RULE_ID = rul.id

    def tearDown(self):
        sot = self.operator_cloud.network.delete_default_security_group_rule(
            self.RULE_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.operator_cloud.network.find_default_security_group_rule(
            self.RULE_ID
        )
        self.assertEqual(self.RULE_ID, sot.id)

    def test_get(self):
        sot = self.operator_cloud.network.get_default_security_group_rule(
            self.RULE_ID
        )
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.DIR, sot.direction)
        self.assertEqual(self.PROTO, sot.protocol)
        self.assertEqual(self.PORT, sot.port_range_min)
        self.assertEqual(self.PORT, sot.port_range_max)
        self.assertEqual(self.USED_IN_DEFAULT_SG, sot.used_in_default_sg)
        self.assertEqual(
            self.USED_IN_NON_DEFAULT_SG, sot.used_in_non_default_sg
        )

    def test_list(self):
        ids = [
            o.id
            for o in self.operator_cloud.network.default_security_group_rules()
        ]
        self.assertIn(self.RULE_ID, ids)
