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

import uuid

from openstack.tests import fakes
from openstack.tests.unit import base


class TestServerConsole(base.TestCase):
    def setUp(self):
        super().setUp()

        self.server_id = str(uuid.uuid4())
        self.server_name = self.getUniqueString('name')
        self.server = fakes.make_fake_server(
            server_id=self.server_id, name=self.server_name
        )
        self.output = self.getUniqueString('output')

    def test_get_server_console_dict(self):
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/{self.server_id}/action',
                    json={"output": self.output},
                    validate=dict(json={'os-getConsoleOutput': {'length': 5}}),
                ),
            ]
        )

        self.assertEqual(
            self.output, self.cloud.get_server_console(self.server, 5)
        )
        self.assert_calls()

    def test_get_server_console_name_or_id(self):
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/{self.server_id}',
                    json={'server': self.server},
                ),
                dict(
                    method='POST',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/{self.server_id}/action',
                    json={"output": self.output},
                    validate=dict(json={'os-getConsoleOutput': {}}),
                ),
            ]
        )

        self.assertEqual(
            self.output, self.cloud.get_server_console(self.server['id'])
        )

        self.assert_calls()

    def test_get_server_console_no_console(self):
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/{self.server_id}/action',
                    status_code=400,
                    validate=dict(json={'os-getConsoleOutput': {}}),
                ),
            ]
        )

        self.assertEqual('', self.cloud.get_server_console(self.server))

        self.assert_calls()
