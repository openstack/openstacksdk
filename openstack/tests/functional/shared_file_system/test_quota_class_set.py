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

from openstack.tests.functional.shared_file_system import base


class QuotaClassSetTest(base.BaseSharedFileSystemTest):
    def test_quota_class_set(self):
        project_id = self.operator_cloud.current_project_id

        initial_quota_class_set = (
            self.operator_cloud.share.get_quota_class_set(project_id)
        )
        self.assertIn('shares', initial_quota_class_set)

        initial_backups_value = initial_quota_class_set['backups']

        updated_quota_class_set = (
            self.operator_cloud.share.update_quota_class_set(
                project_id,
                **{
                    "backups": initial_backups_value + 1,
                }
            )
        )
        self.assertEqual(
            updated_quota_class_set['backups'], initial_backups_value + 1
        )

        reverted = self.operator_cloud.share.update_quota_class_set(
            project_id, **{"backups": initial_backups_value}
        )

        self.assertEqual(initial_quota_class_set, reverted)
