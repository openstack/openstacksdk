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
    qos_packet_rate_limit_rule as _qos_packet_rate_limit_rule,
)
from openstack.tests.functional import base


class TestQoSPacketRateLimitRule(base.BaseFunctionalTest):
    QOS_POLICY_ID = None
    QOS_IS_SHARED = False
    QOS_POLICY_DESCRIPTION = 'QoS policy description'
    RULE_MAX_KPPS = 1500
    RULE_MAX_KPPS_NEW = 1800
    RULE_MAX_BURST_KPPS = 1100
    RULE_MAX_BURST_KPPS_NEW = 1300
    RULE_DIRECTION = 'egress'
    RULE_DIRECTION_NEW = 'ingress'
    RULE_DIRECTION_NEW_2 = 'any'

    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest('Operator cloud required for this test')

        # Skip the tests if qos-bw-limit-direction extension is not enabled.
        if not self.operator_cloud.network.find_extension('qos-pps'):
            self.skipTest("Network qos-pps extension disabled")

        self.QOS_POLICY_NAME = self.getUniqueString()
        self.RULE_ID = self.getUniqueString()
        qos_policy = self.operator_cloud.network.create_qos_policy(
            description=self.QOS_POLICY_DESCRIPTION,
            name=self.QOS_POLICY_NAME,
            shared=self.QOS_IS_SHARED,
        )
        self.QOS_POLICY_ID = qos_policy.id
        qos_rule = (
            self.operator_cloud.network.create_qos_packet_rate_limit_rule(
                self.QOS_POLICY_ID,
                max_kpps=self.RULE_MAX_KPPS,
                max_burst_kpps=self.RULE_MAX_BURST_KPPS,
                direction=self.RULE_DIRECTION,
            )
        )
        assert isinstance(
            qos_rule, _qos_packet_rate_limit_rule.QoSPacketRateLimitRule
        )
        self.assertEqual(self.RULE_MAX_KPPS, qos_rule.max_kpps)
        self.assertEqual(self.RULE_MAX_BURST_KPPS, qos_rule.max_burst_kpps)
        self.assertEqual(self.RULE_DIRECTION, qos_rule.direction)
        self.RULE_ID = qos_rule.id

    def tearDown(self):
        rule = self.operator_cloud.network.delete_qos_packet_rate_limit_rule(
            self.RULE_ID, self.QOS_POLICY_ID
        )
        qos_policy = self.operator_cloud.network.delete_qos_policy(
            self.QOS_POLICY_ID
        )
        self.assertIsNone(rule)
        self.assertIsNone(qos_policy)
        super().tearDown()

    def test_find(self):
        sot = self.operator_cloud.network.find_qos_packet_rate_limit_rule(
            self.RULE_ID, self.QOS_POLICY_ID
        )
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.RULE_MAX_KPPS, sot.max_kpps)
        self.assertEqual(self.RULE_MAX_BURST_KPPS, sot.max_burst_kpps)
        self.assertEqual(self.RULE_DIRECTION, sot.direction)

    def test_get(self):
        sot = self.operator_cloud.network.get_qos_packet_rate_limit_rule(
            self.RULE_ID, self.QOS_POLICY_ID
        )
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.QOS_POLICY_ID, sot.qos_policy_id)
        self.assertEqual(self.RULE_MAX_KPPS, sot.max_kpps)
        self.assertEqual(self.RULE_MAX_BURST_KPPS, sot.max_burst_kpps)
        self.assertEqual(self.RULE_DIRECTION, sot.direction)

    def test_list(self):
        rule_ids = [
            o.id
            for o in self.operator_cloud.network.qos_packet_rate_limit_rules(
                self.QOS_POLICY_ID
            )
        ]
        self.assertIn(self.RULE_ID, rule_ids)

    def test_update(self):
        sot = self.operator_cloud.network.update_qos_packet_rate_limit_rule(
            self.RULE_ID,
            self.QOS_POLICY_ID,
            max_kpps=self.RULE_MAX_KPPS_NEW,
            max_burst_kpps=self.RULE_MAX_BURST_KPPS_NEW,
            direction=self.RULE_DIRECTION_NEW,
        )
        self.assertEqual(self.RULE_MAX_KPPS_NEW, sot.max_kpps)
        self.assertEqual(self.RULE_MAX_BURST_KPPS_NEW, sot.max_burst_kpps)
        self.assertEqual(self.RULE_DIRECTION_NEW, sot.direction)
