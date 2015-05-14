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
test_delete_server
----------------------------------

Tests for the `delete_server` command.
"""

import mock
from novaclient import exceptions as nova_exc
import os_client_config

from shade import OpenStackCloud
from shade import exc as shade_exc
from shade.tests import fakes
from shade.tests.unit import base


class TestDeleteServer(base.TestCase):
    novaclient_exceptions = (nova_exc.BadRequest,
                             nova_exc.Unauthorized,
                             nova_exc.Forbidden,
                             nova_exc.MethodNotAllowed,
                             nova_exc.Conflict,
                             nova_exc.OverLimit,
                             nova_exc.RateLimit,
                             nova_exc.HTTPNotImplemented)

    def setUp(self):
        super(TestDeleteServer, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.cloud = OpenStackCloud(
            cloud_config=config.get_one_cloud(validate=False))

    @mock.patch('shade.OpenStackCloud.nova_client')
    def test_delete_server(self, nova_mock):
        """
        Test that novaclient server delete is called when wait=False
        """
        server = fakes.FakeServer('1234', 'daffy', 'ACTIVE')
        nova_mock.servers.list.return_value = [server]
        self.cloud.delete_server('daffy', wait=False)
        nova_mock.servers.delete.assert_called_with(server=server.id)

    @mock.patch('shade.OpenStackCloud.nova_client')
    def test_delete_server_already_gone(self, nova_mock):
        """
        Test that we return immediately when server is already gone
        """
        nova_mock.servers.list.return_value = []
        self.cloud.delete_server('tweety', wait=False)
        self.assertFalse(nova_mock.servers.delete.called)

    @mock.patch('shade.OpenStackCloud.nova_client')
    def test_delete_server_already_gone_wait(self, nova_mock):
        self.cloud.delete_server('speedy', wait=True)
        self.assertFalse(nova_mock.servers.delete.called)

    @mock.patch('shade.OpenStackCloud.nova_client')
    def test_delete_server_wait_for_notfound(self, nova_mock):
        """
        Test that delete_server waits for NotFound from novaclient
        """
        server = fakes.FakeServer('9999', 'wily', 'ACTIVE')
        nova_mock.servers.list.return_value = [server]

        def _delete_wily(*args, **kwargs):
            self.assertIn('server', kwargs)
            self.assertEqual('9999', kwargs['server'])
            nova_mock.servers.list.return_value = []

            def _raise_notfound(*args, **kwargs):
                self.assertIn('server', kwargs)
                self.assertEqual('9999', kwargs['server'])
                raise nova_exc.NotFound(code='404')
            nova_mock.servers.get.side_effect = _raise_notfound

        nova_mock.servers.delete.side_effect = _delete_wily
        self.cloud.delete_server('wily', wait=True)
        nova_mock.servers.delete.assert_called_with(server=server.id)

    @mock.patch('shade.OpenStackCloud.nova_client')
    def test_delete_server_fails(self, nova_mock):
        """
        Test that delete_server wraps novaclient exceptions
        """
        nova_mock.servers.list.return_value = [fakes.FakeServer('1212',
                                                                'speedy',
                                                                'ACTIVE')]
        for fail in self.novaclient_exceptions:

            def _raise_fail(server):
                raise fail(code=fail.http_status)

            nova_mock.servers.delete.side_effect = _raise_fail
            exc = self.assertRaises(shade_exc.OpenStackCloudException,
                                    self.cloud.delete_server, 'speedy',
                                    wait=False)
            # Note that message is deprecated from Exception, but not in
            # the novaclient exceptions.
            self.assertIn(fail.message, str(exc))

    @mock.patch('shade.OpenStackCloud.nova_client')
    def test_delete_server_get_fails(self, nova_mock):
        """
        Test that delete_server wraps novaclient exceptions on wait fails
        """
        nova_mock.servers.list.return_value = [fakes.FakeServer('2000',
                                                                'yosemite',
                                                                'ACTIVE')]
        for fail in self.novaclient_exceptions:

            def _raise_fail(server):
                raise fail(code=fail.http_status)

            nova_mock.servers.get.side_effect = _raise_fail
            exc = self.assertRaises(shade_exc.OpenStackCloudException,
                                    self.cloud.delete_server, 'yosemite',
                                    wait=True)
            # Note that message is deprecated from Exception, but not in
            # the novaclient exceptions.
            self.assertIn(fail.message, str(exc))
