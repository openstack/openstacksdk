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

from openstack.shared_file_system.v2 import quota_class_set as _quota_class_set
from openstack.tests.functional.shared_file_system import base


class QuotaClassSetTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud required for this test")

        self.project = self.create_temporary_project()

    def test_quota_class_set(self):
        # set quota class set

        quota_class_set = self.operator_cloud.share.update_quota_class_set(
            self.project.id, backups=123
        )
        self.assertIsInstance(quota_class_set, _quota_class_set.QuotaClassSet)
        self.assertEqual(quota_class_set.backups, 123)

        # retrieve details of the (updated) quota class set

        quota_class_set = self.operator_cloud.share.get_quota_class_set(
            self.project.id
        )
        self.assertIsInstance(quota_class_set, _quota_class_set.QuotaClassSet)
        self.assertEqual(quota_class_set.backups, 123)
