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

Functional tests for `shade` quotas methods.
"""

from shade.tests.functional import base


class TestComputeQuotas(base.BaseFunctionalTestCase):

    def test_quotas(self):
        '''Test quotas functionality'''
        quotas = self.operator_cloud.get_compute_quotas('demo')
        cores = quotas['cores']
        self.operator_cloud.set_compute_quotas('demo', cores=cores + 1)
        self.assertEqual(
            cores + 1,
            self.operator_cloud.get_compute_quotas('demo')['cores'])
        self.operator_cloud.delete_compute_quotas('demo')
        self.assertEqual(
            cores, self.operator_cloud.get_compute_quotas('demo')['cores'])


class TestVolumeQuotas(base.BaseFunctionalTestCase):

    def setUp(self):
        super(TestVolumeQuotas, self).setUp()
        if not self.operator_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')

    def test_quotas(self):
        '''Test quotas functionality'''
        quotas = self.operator_cloud.get_volume_quotas('demo')
        volumes = quotas['volumes']
        self.operator_cloud.set_volume_quotas('demo', volumes=volumes + 1)
        self.assertEqual(
            volumes + 1,
            self.operator_cloud.get_volume_quotas('demo')['volumes'])
        self.operator_cloud.delete_volume_quotas('demo')
        self.assertEqual(
            volumes,
            self.operator_cloud.get_volume_quotas('demo')['volumes'])


class TestNetworkQuotas(base.BaseFunctionalTestCase):

    def setUp(self):
        super(TestNetworkQuotas, self).setUp()
        if not self.operator_cloud.has_service('network'):
            self.skipTest('network service not supported by cloud')

    def test_quotas(self):
        '''Test quotas functionality'''
        quotas = self.operator_cloud.get_network_quotas('demo')
        network = quotas['network']
        self.operator_cloud.set_network_quotas('demo', network=network + 1)
        self.assertEqual(
            network + 1,
            self.operator_cloud.get_network_quotas('demo')['network'])
        self.operator_cloud.delete_network_quotas('demo')
        self.assertEqual(
            network,
            self.operator_cloud.get_network_quotas('demo')['network'])
