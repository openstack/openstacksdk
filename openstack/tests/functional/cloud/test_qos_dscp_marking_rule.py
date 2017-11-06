# Copyright 2017 OVH SAS
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

"""
test_qos_dscp_marking_rule
----------------------------------

Functional tests for `shade`QoS DSCP marking rule methods.
"""

from openstack.cloud.exc import OpenStackCloudException
from openstack.tests.functional.cloud import base


class TestQosDscpMarkingRule(base.BaseFunctionalTestCase):
    def setUp(self):
        super(TestQosDscpMarkingRule, self).setUp()
        if not self.operator_cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')
        if not self.operator_cloud._has_neutron_extension('qos'):
            self.skipTest('QoS network extension not supported by cloud')

        policy_name = self.getUniqueString('qos_policy')
        self.policy = self.operator_cloud.create_qos_policy(name=policy_name)

        self.addCleanup(self._cleanup_qos_policy)

    def _cleanup_qos_policy(self):
        try:
            self.operator_cloud.delete_qos_policy(self.policy['id'])
        except Exception as e:
            raise OpenStackCloudException(e)

    def test_qos_dscp_marking_rule_lifecycle(self):
        dscp_mark = 16
        updated_dscp_mark = 32

        # Create DSCP marking rule
        rule = self.operator_cloud.create_qos_dscp_marking_rule(
            self.policy['id'],
            dscp_mark=dscp_mark)
        self.assertIn('id', rule)
        self.assertEqual(dscp_mark, rule['dscp_mark'])

        # Now try to update rule
        updated_rule = self.operator_cloud.update_qos_dscp_marking_rule(
            self.policy['id'],
            rule['id'],
            dscp_mark=updated_dscp_mark)
        self.assertIn('id', updated_rule)
        self.assertEqual(updated_dscp_mark, updated_rule['dscp_mark'])

        # List rules from policy
        policy_rules = self.operator_cloud.list_qos_dscp_marking_rules(
            self.policy['id'])
        self.assertEqual([updated_rule], policy_rules)

        # Delete rule
        self.operator_cloud.delete_qos_dscp_marking_rule(
            self.policy['id'], updated_rule['id'])

        # Check if there is no rules in policy
        policy_rules = self.operator_cloud.list_qos_dscp_marking_rules(
            self.policy['id'])
        self.assertEqual([], policy_rules)
