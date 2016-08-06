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

"""
test_update_server
----------------------------------

Tests for the `update_server` command.
"""

from mock import patch, Mock
import os_client_config
from shade import OpenStackCloud
from shade.exc import OpenStackCloudException
from shade.tests import base, fakes


class TestUpdateServer(base.TestCase):

    def setUp(self):
        super(TestUpdateServer, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.client = OpenStackCloud(
            cloud_config=config.get_one_cloud(validate=False))
        self.client._SERVER_AGE = 0

    def test_update_server_with_update_exception(self):
        """
        Test that an exception in the novaclient update raises an exception in
        update_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.update.side_effect": Exception("exception"),
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudException, self.client.update_server,
                'server-name')

    def test_update_server_name(self):
        """
        Test that update_server updates the name without raising any exception
        """
        with patch("shade.OpenStackCloud"):
            fake_server = fakes.FakeServer('1234', 'server-name', 'ACTIVE')
            fake_update_server = fakes.FakeServer('1234', 'server-name2',
                                                  'ACTIVE')
            fake_floating_ip = fakes.FakeFloatingIP('1234', 'ippool',
                                                    '1.1.1.1', '2.2.2.2',
                                                    '5678')
            config = {
                "servers.list.return_value": [fake_server],
                "servers.update.return_value": fake_update_server,
                "floating_ips.list.return_value": [fake_floating_ip]
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertEqual(
                'server-name2',
                self.client.update_server(
                    'server-name', name='server-name2')['name'])
