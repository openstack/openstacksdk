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

from openstack.compute.v2 import quota_set as _quota_set
from openstack.tests.functional import base


class TestQuotaSet(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud required for this test")

        self.project = self.create_temporary_project()

    def test_quota_set(self):
        # update quota

        quota_set = self.operator_cloud.compute.update_quota_set(
            self.project.id, key_pairs=123
        )
        self.assertIsInstance(quota_set, _quota_set.QuotaSet)
        self.assertEqual(quota_set.key_pairs, 123)

        # retrieve details of the (updated) quota

        quota_set = self.operator_cloud.compute.get_quota_set(self.project.id)
        self.assertIsInstance(quota_set, _quota_set.QuotaSet)
        self.assertEqual(quota_set.key_pairs, 123)

        # retrieve quota defaults

        defaults = self.operator_cloud.compute.get_quota_set_defaults(
            self.project.id
        )
        self.assertIsInstance(defaults, _quota_set.QuotaSet)
        self.assertNotEqual(defaults.key_pairs, 123)

        # revert quota

        self.operator_cloud.compute.revert_quota_set(self.project.id)
