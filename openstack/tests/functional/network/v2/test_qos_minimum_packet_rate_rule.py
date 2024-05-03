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


from openstack.network.v2 import (
    qos_minimum_packet_rate_rule as _qos_minimum_packet_rate_rule,
)
from openstack.tests.functional import base


class TestQoSMinimumPacketRateRule(base.BaseFunctionalTest):
    QOS_POLICY_ID = None
    QOS_IS_SHARED = False
    QOS_POLICY_DESCRIPTION = "QoS policy description"
    RULE_ID = None
    RULE_MIN_KPPS = 1200
    RULE_MIN_KPPS_NEW = 1800
    RULE_DIRECTION = "egress"
    RULE_DIRECTION_NEW = "ingress"

    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        # Skip the tests if qos-pps-minimum extension is not enabled.
        if not self.operator_cloud.network.find_extension("qos-pps-minimum"):
            self.skipTest("Network qos-pps-minimum extension disabled")

        self.QOS_POLICY_NAME = self.getUniqueString()
        qos_policy = self.operator_cloud.network.create_qos_policy(
            description=self.QOS_POLICY_DESCRIPTION,
            name=self.QOS_POLICY_NAME,
            shared=self.QOS_IS_SHARED,
        )
        self.QOS_POLICY_ID = qos_policy.id
        qos_min_pps_rule = (
            self.operator_cloud.network.create_qos_minimum_packet_rate_rule(
                self.QOS_POLICY_ID,
                direction=self.RULE_DIRECTION,
                min_kpps=self.RULE_MIN_KPPS,
            )
        )
        assert isinstance(
            qos_min_pps_rule,
            _qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
        )
        self.assertEqual(self.RULE_MIN_KPPS, qos_min_pps_rule.min_kpps)
        self.assertEqual(self.RULE_DIRECTION, qos_min_pps_rule.direction)
        self.RULE_ID = qos_min_pps_rule.id

    def tearDown(self):
        rule = self.operator_cloud.network.delete_qos_minimum_packet_rate_rule(
            self.RULE_ID, self.QOS_POLICY_ID
        )
        qos_policy = self.operator_cloud.network.delete_qos_policy(
            self.QOS_POLICY_ID
        )
        self.assertIsNone(rule)
        self.assertIsNone(qos_policy)
        super().tearDown()

    def test_find(self):
        sot = self.operator_cloud.network.find_qos_minimum_packet_rate_rule(
            self.RULE_ID, self.QOS_POLICY_ID
        )
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.RULE_DIRECTION, sot.direction)
        self.assertEqual(self.RULE_MIN_KPPS, sot.min_kpps)

    def test_get(self):
        sot = self.operator_cloud.network.get_qos_minimum_packet_rate_rule(
            self.RULE_ID, self.QOS_POLICY_ID
        )
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.QOS_POLICY_ID, sot.qos_policy_id)
        self.assertEqual(self.RULE_DIRECTION, sot.direction)
        self.assertEqual(self.RULE_MIN_KPPS, sot.min_kpps)

    def test_list(self):
        rule_ids = [
            o.id
            for o in self.operator_cloud.network.qos_minimum_packet_rate_rules(
                self.QOS_POLICY_ID
            )
        ]
        self.assertIn(self.RULE_ID, rule_ids)

    def test_update(self):
        sot = self.operator_cloud.network.update_qos_minimum_packet_rate_rule(
            self.RULE_ID,
            self.QOS_POLICY_ID,
            min_kpps=self.RULE_MIN_KPPS_NEW,
            direction=self.RULE_DIRECTION_NEW,
        )
        self.assertEqual(self.RULE_MIN_KPPS_NEW, sot.min_kpps)
        self.assertEqual(self.RULE_DIRECTION_NEW, sot.direction)
