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
test_server_delete_metadata
----------------------------------

Tests for the `delete_server_metadata` command.
"""

import uuid

from openstack.cloud.exc import OpenStackCloudURINotFound
from openstack.tests import fakes
from openstack.tests.unit import base


class TestServerDeleteMetadata(base.TestCase):

    def setUp(self):
        super(TestServerDeleteMetadata, self).setUp()
        self.server_id = str(uuid.uuid4())
        self.server_name = self.getUniqueString('name')
        self.fake_server = fakes.make_fake_server(
            self.server_id, self.server_name)

    def test_server_delete_metadata_with_exception(self):
        """
        Test that a missing metadata throws an exception.
        """
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.fake_server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.fake_server['id'],
                             'metadata', 'key']),
                 status_code=404),
        ])

        self.assertRaises(
            OpenStackCloudURINotFound, self.cloud.delete_server_metadata,
            self.server_name, ['key'])

        self.assert_calls()

    def test_server_delete_metadata(self):
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.fake_server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.fake_server['id'],
                             'metadata', 'key']),
                 status_code=200),
        ])

        self.cloud.delete_server_metadata(self.server_id, ['key'])

        self.assert_calls()
