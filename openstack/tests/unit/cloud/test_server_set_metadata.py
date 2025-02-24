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

from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestServerSetMetadata(base.TestCase):
    def setUp(self):
        super().setUp()
        self.server_id = str(uuid.uuid4())
        self.server_name = self.getUniqueString('name')
        self.fake_server = fakes.make_fake_server(
            self.server_id, self.server_name
        )

    def test_server_set_metadata_with_exception(self):
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', self.server_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=[f'name={self.server_name}'],
                    ),
                    json={'servers': [self.fake_server]},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', self.fake_server['id'], 'metadata'],
                    ),
                    validate=dict(json={'metadata': {'meta': 'data'}}),
                    json={},
                    status_code=400,
                ),
            ]
        )

        self.assertRaises(
            exceptions.BadRequestException,
            self.cloud.set_server_metadata,
            self.server_name,
            {'meta': 'data'},
        )

        self.assert_calls()

    def test_server_set_metadata(self):
        metadata = {'meta': 'data'}
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', self.server_id]
                    ),
                    json={'server': self.fake_server},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', self.fake_server['id'], 'metadata'],
                    ),
                    validate=dict(json={'metadata': metadata}),
                    status_code=200,
                    json={'metadata': metadata},
                ),
            ]
        )

        self.cloud.set_server_metadata(self.server_id, metadata)

        self.assert_calls()
