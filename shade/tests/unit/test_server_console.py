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
import novaclient.exceptions as nova_exceptions

import shade
from shade.tests.unit import base
from shade.tests import fakes


class TestServerConsole(base.TestCase):

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_server_console_dict(self, mock_nova):
        server = dict(id='12345')
        self.cloud.get_server_console(server)

        mock_nova.servers.list.assert_not_called()
        mock_nova.servers.get_console_output.assert_called_once_with(
            server='12345', length=None)

    @mock.patch.object(shade.OpenStackCloud, 'has_service')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_server_console_name_or_id(self, mock_nova, mock_has_service):
        server = '12345'

        fake_server = fakes.FakeServer(server, '', 'ACTIVE')
        mock_nova.servers.get.return_value = fake_server
        mock_nova.servers.list.return_value = [fake_server]
        mock_has_service.return_value = False

        self.cloud.get_server_console(server)

        mock_nova.servers.get_console_output.assert_called_once_with(
            server='12345', length=None)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_server_console_no_console(self, mock_nova):
        server = dict(id='12345')
        exc = nova_exceptions.BadRequest(
            'There is no such action: os-getConsoleOutput')
        mock_nova.servers.get_console_output.side_effect = exc
        log = self.cloud.get_server_console(server)

        self.assertEqual('', log)
        mock_nova.servers.list.assert_not_called()
        mock_nova.servers.get_console_output.assert_called_once_with(
            server='12345', length=None)
