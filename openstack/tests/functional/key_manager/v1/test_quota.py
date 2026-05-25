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

from openstack.key_manager.v1 import quota as _quota
from openstack.tests.functional import base


class TestQuota(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('key-manager')

    def test_quota_get(self):
        """Test getting current project's effective quotas."""
        quota = self.user_cloud.key_manager.get_quota()

        self.assertIsInstance(quota, _quota.Quota)

        # Verify quota attributes exist and are integers
        self.assertIsInstance(quota.secrets, int)
        self.assertIsInstance(quota.orders, int)
        self.assertIsInstance(quota.containers, int)
        self.assertIsInstance(quota.consumers, int)
        self.assertIsInstance(quota.cas, int)

        # Verify quotas are reasonable values (not None or negative)
        self.assertGreaterEqual(quota.secrets, -1)  # -1 means unlimited
        self.assertGreaterEqual(quota.orders, -1)
        self.assertGreaterEqual(quota.containers, -1)
        self.assertGreaterEqual(quota.consumers, -1)
        self.assertGreaterEqual(quota.cas, -1)
