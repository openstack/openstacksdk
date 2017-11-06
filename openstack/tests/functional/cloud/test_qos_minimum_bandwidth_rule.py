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
test_qos_minumum_bandwidth_rule
----------------------------------

Functional tests for `shade`QoS minimum bandwidth methods.
"""

from openstack.cloud.exc import OpenStackCloudException
from openstack.tests.functional.cloud import base


class TestQosMinimumBandwidthRule(base.BaseFunctionalTestCase):
    def setUp(self):
        super(TestQosMinimumBandwidthRule, self).setUp()
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

    def test_qos_minimum_bandwidth_rule_lifecycle(self):
        min_kbps = 1500
        updated_min_kbps = 2000

        # Create min bw rule
        rule = self.operator_cloud.create_qos_minimum_bandwidth_rule(
            self.policy['id'],
            min_kbps=min_kbps)
        self.assertIn('id', rule)
        self.assertEqual(min_kbps, rule['min_kbps'])

        # Now try to update rule
        updated_rule = self.operator_cloud.update_qos_minimum_bandwidth_rule(
            self.policy['id'],
            rule['id'],
            min_kbps=updated_min_kbps)
        self.assertIn('id', updated_rule)
        self.assertEqual(updated_min_kbps, updated_rule['min_kbps'])

        # List rules from policy
        policy_rules = self.operator_cloud.list_qos_minimum_bandwidth_rules(
            self.policy['id'])
        self.assertEqual([updated_rule], policy_rules)

        # Delete rule
        self.operator_cloud.delete_qos_minimum_bandwidth_rule(
            self.policy['id'], updated_rule['id'])

        # Check if there is no rules in policy
        policy_rules = self.operator_cloud.list_qos_minimum_bandwidth_rules(
            self.policy['id'])
        self.assertEqual([], policy_rules)
