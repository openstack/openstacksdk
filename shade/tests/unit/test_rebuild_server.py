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
test_rebuild_server
----------------------------------

Tests for the `rebuild_server` command.
"""

from mock import patch, Mock
from shade import meta
from shade import OpenStackCloud
from shade.exc import (OpenStackCloudException, OpenStackCloudTimeout)
from shade.tests import fakes
from shade.tests.unit import base


class TestRebuildServer(base.TestCase):

    def test_rebuild_server_rebuild_exception(self):
        """
        Test that an exception in the novaclient rebuild raises an exception in
        rebuild_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.rebuild.side_effect": Exception("exception"),
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudException, self.cloud.rebuild_server, "a", "b")

    def test_rebuild_server_server_error(self):
        """
        Test that a server error while waiting for the server to rebuild
        raises an exception in rebuild_server.
        """
        rebuild_server = fakes.FakeServer('1234', '', 'REBUILD')
        error_server = fakes.FakeServer('1234', '', 'ERROR')
        fake_floating_ip = fakes.FakeFloatingIP('1234', 'ippool',
                                                '1.1.1.1', '2.2.2.2',
                                                '5678')
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.rebuild.return_value": rebuild_server,
                "servers.list.return_value": [error_server],
                "floating_ips.list.return_value": [fake_floating_ip]
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudException,
                self.cloud.rebuild_server, "1234", "b", wait=True)

    def test_rebuild_server_timeout(self):
        """
        Test that a timeout while waiting for the server to rebuild raises an
        exception in rebuild_server.
        """
        rebuild_server = fakes.FakeServer('1234', '', 'REBUILD')
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.rebuild.return_value": rebuild_server,
                "servers.list.return_value": [rebuild_server],
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudTimeout,
                self.cloud.rebuild_server, "a", "b", wait=True, timeout=0.001)

    def test_rebuild_server_no_wait(self):
        """
        Test that rebuild_server with no wait and no exception in the
        novaclient rebuild call returns the server instance.
        """
        with patch("shade.OpenStackCloud"):
            rebuild_server = fakes.FakeServer('1234', '', 'REBUILD')
            config = {
                "servers.rebuild.return_value": rebuild_server
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertEqual(meta.obj_to_dict(rebuild_server),
                             self.cloud.rebuild_server("a", "b"))

    def test_rebuild_server_with_admin_pass_no_wait(self):
        """
        Test that a server with an admin_pass passed returns the password
        """
        with patch("shade.OpenStackCloud"):
            rebuild_server = fakes.FakeServer('1234', '', 'REBUILD',
                                              adminPass='ooBootheiX0edoh')
            config = {
                "servers.rebuild.return_value": rebuild_server,
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertEqual(
                meta.obj_to_dict(rebuild_server),
                self.cloud.rebuild_server(
                    'a', 'b', admin_pass='ooBootheiX0edoh'))

    def test_rebuild_server_with_admin_pass_wait(self):
        """
        Test that a server with an admin_pass passed returns the password
        """
        with patch("shade.OpenStackCloud"):
            rebuild_server = fakes.FakeServer('1234', '', 'REBUILD',
                                              adminPass='ooBootheiX0edoh')
            active_server = fakes.FakeServer('1234', '', 'ACTIVE')
            ret_active_server = fakes.FakeServer('1234', '', 'ACTIVE',
                                                 adminPass='ooBootheiX0edoh')
            fake_floating_ip = fakes.FakeFloatingIP('1234', 'ippool',
                                                    '1.1.1.1', '2.2.2.2',
                                                    '5678')
            config = {
                "servers.rebuild.return_value": rebuild_server,
                "servers.list.return_value": [active_server],
                "floating_ips.list.return_value": [fake_floating_ip]
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.cloud.name = 'cloud-name'
            self.assertEqual(
                self.cloud._normalize_server(
                    meta.obj_to_dict(ret_active_server)),
                self.cloud.rebuild_server(
                    "1234", "b", wait=True, admin_pass='ooBootheiX0edoh'))

    def test_rebuild_server_wait(self):
        """
        Test that rebuild_server with a wait returns the server instance when
        its status changes to "ACTIVE".
        """
        with patch("shade.OpenStackCloud"):
            rebuild_server = fakes.FakeServer('1234', '', 'REBUILD')
            active_server = fakes.FakeServer('1234', '', 'ACTIVE')
            fake_floating_ip = fakes.FakeFloatingIP('1234', 'ippool',
                                                    '1.1.1.1', '2.2.2.2',
                                                    '5678')
            config = {
                "servers.rebuild.return_value": rebuild_server,
                "servers.list.return_value": [active_server],
                "floating_ips.list.return_value": [fake_floating_ip]
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.cloud.name = 'cloud-name'
            self.assertEqual(
                self.cloud._normalize_server(
                    meta.obj_to_dict(active_server)),
                self.cloud.rebuild_server("1234", "b", wait=True))
