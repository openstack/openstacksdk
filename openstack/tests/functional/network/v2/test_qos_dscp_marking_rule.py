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

from openstack.network.v2 import (qos_dscp_marking_rule as
                                  _qos_dscp_marking_rule)
from openstack.tests.functional import base


class TestQoSDSCPMarkingRule(base.BaseFunctionalTest):

    QOS_POLICY_ID = None
    QOS_POLICY_NAME = uuid.uuid4().hex
    QOS_IS_SHARED = False
    QOS_POLICY_DESCRIPTION = "QoS policy description"
    RULE_ID = uuid.uuid4().hex
    RULE_DSCP_MARK = 36
    RULE_DSCP_MARK_NEW = 40

    @classmethod
    def setUpClass(cls):
        super(TestQoSDSCPMarkingRule, cls).setUpClass()
        qos_policy = cls.conn.network.create_qos_policy(
            description=cls.QOS_POLICY_DESCRIPTION,
            name=cls.QOS_POLICY_NAME,
            shared=cls.QOS_IS_SHARED,
        )
        cls.QOS_POLICY_ID = qos_policy.id
        qos_rule = cls.conn.network.create_qos_dscp_marking_rule(
            cls.QOS_POLICY_ID, dscp_mark=cls.RULE_DSCP_MARK,
        )
        assert isinstance(qos_rule, _qos_dscp_marking_rule.QoSDSCPMarkingRule)
        cls.assertIs(cls.RULE_DSCP_MARK, qos_rule.dscp_mark)
        cls.RULE_ID = qos_rule.id

    @classmethod
    def tearDownClass(cls):
        rule = cls.conn.network.delete_qos_minimum_bandwidth_rule(
            cls.RULE_ID,
            cls.QOS_POLICY_ID)
        qos_policy = cls.conn.network.delete_qos_policy(cls.QOS_POLICY_ID)
        cls.assertIs(None, rule)
        cls.assertIs(None, qos_policy)

    def test_find(self):
        sot = self.conn.network.find_qos_dscp_marking_rule(
            self.RULE_ID,
            self.QOS_POLICY_ID)
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.RULE_DSCP_MARK, sot.dscp_mark)

    def test_get(self):
        sot = self.conn.network.get_qos_dscp_marking_rule(
            self.RULE_ID,
            self.QOS_POLICY_ID)
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.QOS_POLICY_ID, sot.qos_policy_id)
        self.assertEqual(self.RULE_DSCP_MARK, sot.dscp_mark)

    def test_list(self):
        rule_ids = [o.id for o in
                    self.conn.network.qos_dscp_marking_rules(
                        self.QOS_POLICY_ID)]
        self.assertIn(self.RULE_ID, rule_ids)

    def test_update(self):
        sot = self.conn.network.update_qos_dscp_marking_rule(
            self.RULE_ID,
            self.QOS_POLICY_ID,
            dscp_mark=self.RULE_DSCP_MARK_NEW)
        self.assertEqual(self.RULE_DSCP_MARK_NEW, sot.dscp_mark)
