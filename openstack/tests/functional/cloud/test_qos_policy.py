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
test_qos_policy
----------------------------------

Functional tests for QoS policies methods.
"""

from openstack import exceptions
from openstack.tests.functional import base


class TestQosPolicy(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('Network service not supported by cloud')
        if not self.operator_cloud._has_neutron_extension('qos'):
            self.skipTest('QoS network extension not supported by cloud')
        self.policy_name = self.getUniqueString('qos_policy')
        self.addCleanup(self._cleanup_policies)

    def _cleanup_policies(self):
        exception_list = list()
        for policy in self.operator_cloud.list_qos_policies():
            if policy['name'].startswith(self.policy_name):
                try:
                    self.operator_cloud.delete_qos_policy(policy['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_qos_policy_basic(self):
        policy = self.operator_cloud.create_qos_policy(name=self.policy_name)
        self.assertIn('id', policy)
        self.assertEqual(self.policy_name, policy['name'])
        self.assertFalse(policy['is_shared'])
        self.assertFalse(policy['is_default'])

    def test_create_qos_policy_shared(self):
        policy = self.operator_cloud.create_qos_policy(
            name=self.policy_name, shared=True
        )
        self.assertIn('id', policy)
        self.assertEqual(self.policy_name, policy['name'])
        self.assertTrue(policy['is_shared'])
        self.assertFalse(policy['is_default'])

    def test_create_qos_policy_default(self):
        if not self.operator_cloud._has_neutron_extension('qos-default'):
            self.skipTest(
                "'qos-default' network extension not supported by cloud"
            )
        policy = self.operator_cloud.create_qos_policy(
            name=self.policy_name, default=True
        )
        self.assertIn('id', policy)
        self.assertEqual(self.policy_name, policy['name'])
        self.assertFalse(policy['is_shared'])
        self.assertTrue(policy['is_default'])

    def test_update_qos_policy(self):
        policy = self.operator_cloud.create_qos_policy(name=self.policy_name)
        self.assertEqual(self.policy_name, policy['name'])
        self.assertFalse(policy['is_shared'])
        self.assertFalse(policy['is_default'])

        updated_policy = self.operator_cloud.update_qos_policy(
            policy['id'], shared=True, default=True
        )
        self.assertEqual(self.policy_name, updated_policy['name'])
        self.assertTrue(updated_policy['is_shared'])
        self.assertTrue(updated_policy['is_default'])

    def test_list_qos_policies_filtered(self):
        policy1 = self.operator_cloud.create_qos_policy(name=self.policy_name)
        self.assertIsNotNone(policy1)
        policy2 = self.operator_cloud.create_qos_policy(
            name=self.policy_name + 'other'
        )
        self.assertIsNotNone(policy2)
        match = self.operator_cloud.list_qos_policies(
            filters=dict(name=self.policy_name)
        )
        self.assertEqual(1, len(match))
        self.assertEqual(policy1['name'], match[0]['name'])
