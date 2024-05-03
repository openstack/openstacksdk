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
test_quotas
----------------------------------

Functional tests for quotas methods.
"""

from openstack.tests.functional import base


class TestComputeQuotas(base.BaseFunctionalTest):
    def test_get_quotas(self):
        '''Test quotas functionality'''
        self.user_cloud.get_compute_quotas(self.user_cloud.current_project_id)

    def test_set_quotas(self):
        '''Test quotas functionality'''
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        quotas = self.operator_cloud.get_compute_quotas('demo')
        cores = quotas['cores']
        self.operator_cloud.set_compute_quotas('demo', cores=cores + 1)
        self.assertEqual(
            cores + 1, self.operator_cloud.get_compute_quotas('demo')['cores']
        )
        self.operator_cloud.delete_compute_quotas('demo')
        self.assertEqual(
            cores, self.operator_cloud.get_compute_quotas('demo')['cores']
        )


class TestVolumeQuotas(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')

    def test_get_quotas(self):
        '''Test get quotas functionality'''
        self.user_cloud.get_volume_quotas(self.user_cloud.current_project_id)

    def test_set_quotas(self):
        '''Test set quotas functionality'''
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        quotas = self.operator_cloud.get_volume_quotas('demo')
        volumes = quotas['volumes']
        self.operator_cloud.set_volume_quotas('demo', volumes=volumes + 1)
        self.assertEqual(
            volumes + 1,
            self.operator_cloud.get_volume_quotas('demo')['volumes'],
        )
        self.operator_cloud.delete_volume_quotas('demo')
        self.assertEqual(
            volumes, self.operator_cloud.get_volume_quotas('demo')['volumes']
        )


class TestNetworkQuotas(base.BaseFunctionalTest):
    def test_get_quotas(self):
        '''Test get quotas functionality'''
        self.user_cloud.get_network_quotas(self.user_cloud.current_project_id)

    def test_quotas(self):
        '''Test quotas functionality'''
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('network service not supported by cloud')

        quotas = self.operator_cloud.get_network_quotas('demo')
        network = quotas['networks']
        self.operator_cloud.set_network_quotas('demo', networks=network + 1)
        self.assertEqual(
            network + 1,
            self.operator_cloud.get_network_quotas('demo')['networks'],
        )
        self.operator_cloud.delete_network_quotas('demo')
        self.assertEqual(
            network, self.operator_cloud.get_network_quotas('demo')['networks']
        )

    def test_get_quotas_details(self):
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.operator_cloud.has_service('network'):
            self.skipTest('network service not supported by cloud')

        quotas = [
            'floating_ips',
            'networks',
            'ports',
            'rbac_policies',
            'routers',
            'subnets',
            'subnet_pools',
            'security_group_rules',
            'security_groups',
        ]
        expected_keys = ['limit', 'used', 'reserved']
        '''Test getting details about quota usage'''
        quota_details = self.operator_cloud.get_network_quotas(
            'demo', details=True
        )
        for quota in quotas:
            quota_val = quota_details[quota]
            if quota_val:
                for expected_key in expected_keys:
                    self.assertIn(expected_key, quota_val)
