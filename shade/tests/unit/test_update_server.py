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

"""
test_update_server
----------------------------------

Tests for the `update_server` command.
"""

import uuid

from shade.exc import OpenStackCloudException
from shade.tests import fakes
from shade.tests.unit import base


class TestUpdateServer(base.RequestsMockTestCase):

    def setUp(self):
        super(TestUpdateServer, self).setUp()
        self.server_id = str(uuid.uuid4())
        self.server_name = self.getUniqueString('name')
        self.updated_server_name = self.getUniqueString('name2')
        self.fake_server = fakes.make_fake_server(
            self.server_id, self.server_name)

    def test_update_server_with_update_exception(self):
        """
        Test that an exception in the update raises an exception in
        update_server.
        """
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.fake_server]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', self.server_id]),
                 status_code=400,
                 validate=dict(
                     json={'server': {'name': self.updated_server_name}})),
        ])
        self.assertRaises(
            OpenStackCloudException, self.cloud.update_server,
            self.server_name, name=self.updated_server_name)

        self.assert_calls()

    def test_update_server_name(self):
        """
        Test that update_server updates the name without raising any exception
        """
        fake_update_server = fakes.make_fake_server(
            self.server_id, self.updated_server_name)

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.fake_server]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', self.server_id]),
                 json={'server': fake_update_server},
                 validate=dict(
                     json={'server': {'name': self.updated_server_name}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
        ])
        self.assertEqual(
            self.updated_server_name,
            self.cloud.update_server(
                self.server_name, name=self.updated_server_name)['name'])

        self.assert_calls()
