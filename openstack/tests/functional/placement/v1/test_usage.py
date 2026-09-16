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

from openstack.placement.v1 import usage as _usage
from openstack.tests.functional import base


class TestUsage(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud.has_service('placement'):
            self.skipTest('placement service not supported by cloud')

        project_id = self.operator_cloud.current_project_id
        user_id = self.operator_cloud.current_user_id
        assert project_id is not None
        assert user_id is not None
        self.project_id = project_id
        self.user_id = user_id

    def test_usage(self):
        # retrieve usages for the project; there may be zero entries if no
        # allocations exist for this project yet.

        results = list(
            self.operator_cloud.placement.usages(
                project_id=self.project_id,
            )
        )
        for result in results:
            self.assertIsInstance(result, _usage.Usage)
            self.assertIsNotNone(result.consumer_type)
            self.assertIsInstance(result.consumer_count, int)
            self.assertIsInstance(result.resources, dict)

        # filtering by user_id should work (subset of or equal to above)

        results_by_user = list(
            self.operator_cloud.placement.usages(
                project_id=self.project_id,
                user_id=self.user_id,
            )
        )
        for result in results_by_user:
            self.assertIsInstance(result, _usage.Usage)
            self.assertIsNotNone(result.consumer_type)
            self.assertIsInstance(result.resources, dict)
