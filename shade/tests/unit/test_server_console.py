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

from shade.tests.unit import base
from shade.tests import fakes


class TestServerConsole(base.RequestsMockTestCase):

    def setUp(self):
        super(TestServerConsole, self).setUp()

        self.server_id = str(uuid.uuid4())
        self.server_name = self.getUniqueString('name')
        self.server = fakes.make_fake_server(
            server_id=self.server_id, name=self.server_name)
        self.output = self.getUniqueString('output')

    def test_get_server_console_dict(self):
        self.register_uris([
            dict(method='POST',
                 uri='{endpoint}/servers/{id}/action'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT,
                     id=self.server_id),
                 json={"output": self.output},
                 validate=dict(
                     json={'os-getConsoleOutput': {'length': None}}))
        ])

        self.assertEqual(
            self.output, self.cloud.get_server_console(self.server))
        self.assert_calls()

    def test_get_server_console_name_or_id(self):

        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/servers/detail'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 json={"servers": [self.server]}),
            dict(method='POST',
                 uri='{endpoint}/servers/{id}/action'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT,
                     id=self.server_id),
                 json={"output": self.output},
                 validate=dict(
                     json={'os-getConsoleOutput': {'length': None}}))
        ])

        self.assertEqual(
            self.output, self.cloud.get_server_console(self.server['id']))

        self.assert_calls()

    def test_get_server_console_no_console(self):

        self.register_uris([
            dict(method='POST',
                 uri='{endpoint}/servers/{id}/action'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT,
                     id=self.server_id),
                 status_code=400,
                 validate=dict(
                     json={'os-getConsoleOutput': {'length': None}}))
        ])

        self.assertEqual('', self.cloud.get_server_console(self.server))

        self.assert_calls()
