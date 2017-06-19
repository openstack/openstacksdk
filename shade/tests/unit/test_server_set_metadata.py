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
test_server_set_metadata
----------------------------------

Tests for the `set_server_metadata` command.
"""

import uuid

from shade.exc import OpenStackCloudBadRequest
from shade.tests import fakes
from shade.tests.unit import base


class TestServerSetMetadata(base.RequestsMockTestCase):

    def setUp(self):
        super(TestServerSetMetadata, self).setUp()
        self.server_id = str(uuid.uuid4())
        self.server_name = self.getUniqueString('name')
        self.fake_server = fakes.make_fake_server(
            self.server_id, self.server_name)

    def test_server_set_metadata_with_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.fake_server]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.fake_server['id'],
                             'metadata']),
                 validate=dict(json={'metadata': {'meta': 'data'}}),
                 json={},
                 status_code=400),
        ])

        self.assertRaises(
            OpenStackCloudBadRequest, self.cloud.set_server_metadata,
            self.server_name, {'meta': 'data'})

        self.assert_calls()

    def test_server_set_metadata(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.fake_server]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.fake_server['id'], 'metadata']),
                 validate=dict(json={'metadata': {'meta': 'data'}}),
                 status_code=200),
        ])

        self.cloud.set_server_metadata(self.server_id, {'meta': 'data'})

        self.assert_calls()
