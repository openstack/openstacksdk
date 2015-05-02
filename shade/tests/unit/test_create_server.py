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
test_create_server
----------------------------------

Tests for the `create_server` command.
"""

from mock import patch, Mock
from shade import OpenStackCloud
from shade.exc import (OpenStackCloudException, OpenStackCloudTimeout)
from shade.tests import base


class TestCreateServer(base.TestCase):

    def setUp(self):
        super(TestCreateServer, self).setUp()
        self.client = OpenStackCloud("cloud", {})

    def test_create_server_with_create_exception(self):
        """
        Test that an exception in the novaclient create raises an exception in
        create_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.create.side_effect": Exception("exception"),
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudException, self.client.create_server)

    def test_create_server_with_get_exception(self):
        """
        Test that an exception when attempting to get the server instance via
        the novaclient raises an exception in create_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.create.return_value": Mock(status="BUILD"),
                "servers.get.side_effect": Exception("exception")
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudException, self.client.create_server)

    def test_create_server_with_server_error(self):
        """
        Test that a server error before we return or begin waiting for the
        server instance spawn raises an exception in create_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.create.return_value": Mock(status="BUILD"),
                "servers.get.return_value": Mock(status="ERROR")
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudException, self.client.create_server)

    def test_create_server_wait_server_error(self):
        """
        Test that a server error while waiting for the server to spawn
        raises an exception in create_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.create.return_value": Mock(status="BUILD"),
                "servers.get.side_effect": [
                    Mock(status="BUILD"), Mock(status="ERROR")]
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudException,
                self.client.create_server, wait=True)

    def test_create_server_with_timeout(self):
        """
        Test that a timeout while waiting for the server to spawn raises an
        exception in create_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.create.return_value": Mock(status="BUILD"),
                "servers.get.return_value": Mock(status="BUILD")
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudTimeout,
                self.client.create_server, wait=True, timeout=1)

    def test_create_server_no_wait(self):
        """
        Test that create_server with no wait and no exception in the
        novaclient create call returns the server instance.
        """
        with patch("shade.OpenStackCloud"):
            mock_server = Mock(status="BUILD")
            config = {
                "servers.create.return_value": mock_server,
                "servers.get.return_value": mock_server
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertEqual(
                self.client.create_server(), mock_server)

    def test_create_server_wait(self):
        """
        Test that create_server with a wait returns the server instance when
        its status changes to "ACTIVE".
        """
        with patch("shade.OpenStackCloud"):
            mock_server = Mock(status="ACTIVE")
            config = {
                "servers.create.return_value": Mock(status="BUILD"),
                "servers.get.side_effect": [
                    Mock(status="BUILD"), mock_server]
            }
            OpenStackCloud.nova_client = Mock(**config)
            with patch.object(OpenStackCloud, "add_ips_to_server",
                              return_value=mock_server):
                self.assertEqual(
                    self.client.create_server(wait=True),
                    mock_server)
