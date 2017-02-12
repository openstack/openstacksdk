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
import mock

import shade
from shade.tests.unit import base


class TestLimits(base.RequestsMockTestCase):

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_compute_limits(self, mock_nova):
        self.cloud.get_compute_limits()

        mock_nova.limits.get.assert_called_once_with()

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_other_get_compute_limits(self, mock_nova):
        self._add_discovery_uri_call()
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        self.op_cloud.get_compute_limits(project.project_id)

        mock_nova.limits.get.assert_called_once_with(
            tenant_id=project.project_id)
        self.assert_calls()
