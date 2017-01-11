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

from mock import patch, Mock
from shade import OpenStackCloud
from shade.exc import OpenStackCloudException
from shade.tests.unit import base


class TestServerDeleteMetadata(base.TestCase):

    def test_server_delete_metadata_with_delete_meta_exception(self):
        """
        Test that a generic exception in the novaclient delete_meta raises
        an exception in delete_server_metadata.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.delete_meta.side_effect": Exception("exception"),
            }
            OpenStackCloud.nova_client = Mock(**config)

            self.assertRaises(
                OpenStackCloudException, self.cloud.delete_server_metadata,
                {'id': 'server-id'}, ['key'])

    def test_server_delete_metadata_with_exception_reraise(self):
        """
        Test that an OpenStackCloudException exception gets re-raised
        in delete_server_metadata.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.delete_meta.side_effect":
                    OpenStackCloudException("exception"),
            }
            OpenStackCloud.nova_client = Mock(**config)

            self.assertRaises(
                OpenStackCloudException, self.cloud.delete_server_metadata,
                'server-id', ['key'])
