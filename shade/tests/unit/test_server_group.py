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
from shade.tests import fakes


class TestServerGroup(base.TestCase):

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_group(self, mock_nova):
        server_group_name = 'my-server-group'
        self.cloud.create_server_group(name=server_group_name,
                                       policies=['affinity'])

        mock_nova.server_groups.create.assert_called_once_with(
            name=server_group_name, policies=['affinity']
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_server_group(self, mock_nova):
        mock_nova.server_groups.list.return_value = [
            fakes.FakeServerGroup('1234', 'name', ['affinity'])
        ]
        self.assertTrue(self.cloud.delete_server_group('1234'))
        mock_nova.server_groups.list.assert_called_once_with()
        mock_nova.server_groups.delete.assert_called_once_with(
            id='1234'
        )
