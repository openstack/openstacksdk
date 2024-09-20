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

from openstack.network.v2 import quota as _quota
from openstack.tests.functional import base


class TestQuota(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud required for this test")

        self.project = self.create_temporary_project()

    def test_quota(self):
        # update quota

        quota = self.operator_cloud.network.update_quota(
            self.project.id, networks=123456789
        )
        self.assertIsInstance(quota, _quota.Quota)
        self.assertEqual(quota.networks, 123456789)

        # retrieve details of the (updated) quota

        quota = self.operator_cloud.network.get_quota(self.project.id)
        self.assertIsInstance(quota, _quota.Quota)
        self.assertEqual(quota.networks, 123456789)

        # retrieve quota defaults

        defaults = self.operator_cloud.network.get_quota_default(
            self.project.id
        )
        self.assertIsInstance(defaults, _quota.QuotaDefault)
        self.assertNotEqual(defaults.networks, 123456789)

        # list quotas

        quotas = list(self.operator_cloud.network.quotas())
        self.assertIn(self.project.id, [x.project_id for x in quotas])

        # revert quota

        ret = self.operator_cloud.network.delete_quota(self.project.id)
        self.assertIsNone(ret)
