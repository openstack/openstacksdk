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
import datetime
import mock

import shade
from shade.tests.unit import base


class TestUsage(base.RequestsMockTestCase):

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_usage(self, mock_nova):
        self._add_discovery_uri_call()
        project = self.mock_for_keystone_projects(project_count=1,
                                                  list_get=True)[0]
        start = end = datetime.datetime.now()
        self.op_cloud.get_compute_usage(project.project_id, start, end)

        mock_nova.usage.get.assert_called_once_with(
            start=start, end=end, tenant_id=project.project_id)
        self.assert_calls()
