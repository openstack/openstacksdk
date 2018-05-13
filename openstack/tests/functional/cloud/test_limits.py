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
test_limits
----------------------------------

Functional tests for `shade` limits method
"""
from openstack.tests.functional.cloud import base


class TestUsage(base.BaseFunctionalTestCase):

    def test_get_our_compute_limits(self):
        '''Test quotas functionality'''
        limits = self.user_cloud.get_compute_limits()
        self.assertIsNotNone(limits)
        self.assertTrue(hasattr(limits, 'max_server_meta'))

        # Test normalize limits
        self.assertFalse(hasattr(limits, 'maxImageMeta'))

    def test_get_other_compute_limits(self):
        '''Test quotas functionality'''
        limits = self.operator_cloud.get_compute_limits('demo')
        self.assertIsNotNone(limits)
        self.assertTrue(hasattr(limits, 'max_server_meta'))

        # Test normalize limits
        self.assertFalse(hasattr(limits, 'maxImageMeta'))

    def test_get_our_volume_limits(self):
        '''Test quotas functionality'''
        limits = self.user_cloud.get_volume_limits()
        self.assertIsNotNone(limits)
        self.assertFalse(hasattr(limits, 'maxTotalVolumes'))

    def test_get_other_volume_limits(self):
        '''Test quotas functionality'''
        limits = self.operator_cloud.get_volume_limits('demo')
        self.assertFalse(hasattr(limits, 'maxTotalVolumes'))
