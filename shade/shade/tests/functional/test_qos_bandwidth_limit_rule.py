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
test_qos_bandwidth_limit_rule
----------------------------------

Functional tests for `shade`QoS bandwidth limit methods.
"""

from shade.exc import OpenStackCloudException
from shade.tests.functional import base


class TestQosBandwidthLimitRule(base.BaseFunctionalTestCase):
    def setUp(self):
        super(TestQosBandwidthLimitRule, self).setUp()
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

    def test_qos_bandwidth_limit_rule_lifecycle(self):
        max_kbps = 1500
        max_burst_kbps = 500
        updated_max_kbps = 2000

        # Create bw limit rule
        rule = self.operator_cloud.create_qos_bandwidth_limit_rule(
            self.policy['id'],
            max_kbps=max_kbps,
            max_burst_kbps=max_burst_kbps)
        self.assertIn('id', rule)
        self.assertEqual(max_kbps, rule['max_kbps'])
        self.assertEqual(max_burst_kbps, rule['max_burst_kbps'])

        # Now try to update rule
        updated_rule = self.operator_cloud.update_qos_bandwidth_limit_rule(
            self.policy['id'],
            rule['id'],
            max_kbps=updated_max_kbps)
        self.assertIn('id', updated_rule)
        self.assertEqual(updated_max_kbps, updated_rule['max_kbps'])
        self.assertEqual(max_burst_kbps, updated_rule['max_burst_kbps'])

        # List rules from policy
        policy_rules = self.operator_cloud.list_qos_bandwidth_limit_rules(
            self.policy['id'])
        self.assertEqual([updated_rule], policy_rules)

        # Delete rule
        self.operator_cloud.delete_qos_bandwidth_limit_rule(
            self.policy['id'], updated_rule['id'])

        # Check if there is no rules in policy
        policy_rules = self.operator_cloud.list_qos_bandwidth_limit_rules(
            self.policy['id'])
        self.assertEqual([], policy_rules)

    def test_create_qos_bandwidth_limit_rule_direction(self):
        if not self.operator_cloud._has_neutron_extension(
                'qos-bw-limit-direction'):
            self.skipTest("'qos-bw-limit-direction' network extension "
                          "not supported by cloud")
        max_kbps = 1500
        direction = "ingress"
        updated_direction = "egress"

        # Create bw limit rule
        rule = self.operator_cloud.create_qos_bandwidth_limit_rule(
            self.policy['id'],
            max_kbps=max_kbps,
            direction=direction)
        self.assertIn('id', rule)
        self.assertEqual(max_kbps, rule['max_kbps'])
        self.assertEqual(direction, rule['direction'])

        # Now try to update direction in rule
        updated_rule = self.operator_cloud.update_qos_bandwidth_limit_rule(
            self.policy['id'],
            rule['id'],
            direction=updated_direction)
        self.assertIn('id', updated_rule)
        self.assertEqual(max_kbps, updated_rule['max_kbps'])
        self.assertEqual(updated_direction, updated_rule['direction'])
