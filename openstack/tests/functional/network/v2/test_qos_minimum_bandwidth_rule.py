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

import uuid

from openstack.network.v2 import (qos_minimum_bandwidth_rule as
                                  _qos_minimum_bandwidth_rule)
from openstack.tests.functional import base


class TestQoSMinimumBandwidthRule(base.BaseFunctionalTest):

    QOS_POLICY_ID = None
    QOS_POLICY_NAME = uuid.uuid4().hex
    QOS_IS_SHARED = False
    QOS_POLICY_DESCRIPTION = "QoS policy description"
    RULE_ID = None
    RULE_MIN_KBPS = 1200
    RULE_MIN_KBPS_NEW = 1800
    RULE_DIRECTION = 'egress'

    @classmethod
    def setUpClass(cls):
        super(TestQoSMinimumBandwidthRule, cls).setUpClass()
        qos_policy = cls.conn.network.create_qos_policy(
            description=cls.QOS_POLICY_DESCRIPTION,
            name=cls.QOS_POLICY_NAME,
            shared=cls.QOS_IS_SHARED,
        )
        cls.QOS_POLICY_ID = qos_policy.id
        qos_min_bw_rule = cls.conn.network.create_qos_minimum_bandwidth_rule(
            cls.QOS_POLICY_ID, direction=cls.RULE_DIRECTION,
            min_kbps=cls.RULE_MIN_KBPS,
        )
        assert isinstance(qos_min_bw_rule,
                          _qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule)
        cls.assertIs(cls.RULE_MIN_KBPS, qos_min_bw_rule.min_kbps)
        cls.assertIs(cls.RULE_DIRECTION, qos_min_bw_rule.direction)
        cls.RULE_ID = qos_min_bw_rule.id

    @classmethod
    def tearDownClass(cls):
        rule = cls.conn.network.delete_qos_minimum_bandwidth_rule(
            cls.RULE_ID,
            cls.QOS_POLICY_ID)
        qos_policy = cls.conn.network.delete_qos_policy(cls.QOS_POLICY_ID)
        cls.assertIs(None, rule)
        cls.assertIs(None, qos_policy)

    def test_find(self):
        sot = self.conn.network.find_qos_minimum_bandwidth_rule(
            self.RULE_ID,
            self.QOS_POLICY_ID)
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.RULE_DIRECTION, sot.direction)
        self.assertEqual(self.RULE_MIN_KBPS, sot.min_kbps)

    def test_get(self):
        sot = self.conn.network.get_qos_minimum_bandwidth_rule(
            self.RULE_ID,
            self.QOS_POLICY_ID)
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.QOS_POLICY_ID, sot.qos_policy_id)
        self.assertEqual(self.RULE_DIRECTION, sot.direction)
        self.assertEqual(self.RULE_MIN_KBPS, sot.min_kbps)

    def test_list(self):
        rule_ids = [o.id for o in
                    self.conn.network.qos_minimum_bandwidth_rules(
                        self.QOS_POLICY_ID)]
        self.assertIn(self.RULE_ID, rule_ids)

    def test_update(self):
        sot = self.conn.network.update_qos_minimum_bandwidth_rule(
            self.RULE_ID,
            self.QOS_POLICY_ID,
            min_kbps=self.RULE_MIN_KBPS_NEW)
        self.assertEqual(self.RULE_MIN_KBPS_NEW, sot.min_kbps)
