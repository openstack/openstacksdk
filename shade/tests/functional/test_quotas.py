# -*- coding: utf-8 -*-

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

from shade import operator_cloud
from shade.tests import base


class TestComputeQuotas(base.TestCase):

    def setUp(self):
        super(TestComputeQuotas, self).setUp()
        self.cloud = operator_cloud(cloud='devstack-admin')
        if not self.cloud.has_service('compute'):
            self.skipTest('compute service not supported by cloud')

    def test_quotas(self):
        '''Test quotas functionality'''
        quotas = self.cloud.get_compute_quotas('demo')
        cores = quotas['cores']
        self.cloud.set_compute_quotas('demo', cores=cores + 1)
        self.assertEqual(cores + 1,
                         self.cloud.get_compute_quotas('demo')['cores'])
        self.cloud.delete_compute_quotas('demo')
        self.assertEqual(cores, self.cloud.get_compute_quotas('demo')['cores'])
