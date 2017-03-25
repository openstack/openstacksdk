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

import mock
import shade
from shade import exc
from shade import meta
from shade.tests import fakes
from shade.tests.unit import base


class TestCreateServer(base.RequestsMockTestCase):

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_with_create_exception(self, mock_nova):
        """
        Test that an exception in the novaclient create raises an exception in
        create_server.
        """
        mock_nova.servers.create.side_effect = Exception("exception")
        self.assertRaises(
            exc.OpenStackCloudException, self.cloud.create_server,
            'server-name', {'id': 'image-id'}, {'id': 'flavor-id'})

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_with_get_exception(self, mock_nova):
        """
        Test that an exception when attempting to get the server instance via
        the novaclient raises an exception in create_server.
        """

        mock_nova.servers.create.return_value = mock.Mock(status="BUILD")
        mock_nova.servers.get.side_effect = Exception("exception")
        self.assertRaises(
            exc.OpenStackCloudException, self.cloud.create_server,
            'server-name', {'id': 'image-id'}, {'id': 'flavor-id'})

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_with_server_error(self, mock_nova):
        """
        Test that a server error before we return or begin waiting for the
        server instance spawn raises an exception in create_server.
        """
        build_server = fakes.FakeServer('1234', '', 'BUILD')
        error_server = fakes.FakeServer('1234', '', 'ERROR')
        mock_nova.servers.create.return_value = build_server
        mock_nova.servers.get.return_value = error_server
        self.assertRaises(
            exc.OpenStackCloudException, self.cloud.create_server,
            'server-name', {'id': 'image-id'}, {'id': 'flavor-id'})

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_wait_server_error(self, mock_nova):
        """
        Test that a server error while waiting for the server to spawn
        raises an exception in create_server.
        """
        build_server = fakes.FakeServer('1234', '', 'BUILD')
        error_server = fakes.FakeServer('1234', '', 'ERROR')
        fake_floating_ip = fakes.FakeFloatingIP('1234', 'ippool',
                                                '1.1.1.1', '2.2.2.2',
                                                '5678')
        mock_nova.servers.create.return_value = build_server
        mock_nova.servers.get.return_value = build_server
        mock_nova.servers.list.side_effect = [[build_server], [error_server]]
        mock_nova.floating_ips.list.return_value = [fake_floating_ip]
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_server,
            'server-name', dict(id='image-id'),
            dict(id='flavor-id'), wait=True)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_with_timeout(self, mock_nova):
        """
        Test that a timeout while waiting for the server to spawn raises an
        exception in create_server.
        """
        fake_server = fakes.FakeServer('1234', '', 'BUILD')
        mock_nova.servers.create.return_value = fake_server
        mock_nova.servers.get.return_value = fake_server
        mock_nova.servers.list.return_value = [fake_server]
        self.assertRaises(
            exc.OpenStackCloudTimeout,
            self.cloud.create_server,
            'server-name',
            dict(id='image-id'), dict(id='flavor-id'),
            wait=True, timeout=0.01)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_no_wait(self, mock_nova):
        """
        Test that create_server with no wait and no exception in the
        novaclient create call returns the server instance.
        """
        fake_server = fakes.FakeServer('1234', '', 'BUILD')
        fake_floating_ip = fakes.FakeFloatingIP('1234', 'ippool',
                                                '1.1.1.1', '2.2.2.2',
                                                '5678')
        mock_nova.servers.create.return_value = fake_server
        mock_nova.servers.get.return_value = fake_server
        mock_nova.floating_ips.list.return_value = [fake_floating_ip]
        self.assertEqual(
            self.cloud._normalize_server(
                meta.obj_to_dict(fake_server)),
            self.cloud.create_server(
                name='server-name',
                image=dict(id='image=id'),
                flavor=dict(id='flavor-id')))

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_with_admin_pass_no_wait(self, mock_nova):
        """
        Test that a server with an admin_pass passed returns the password
        """
        fake_server = fakes.FakeServer('1234', '', 'BUILD')
        fake_create_server = fakes.FakeServer('1234', '', 'BUILD',
                                              adminPass='ooBootheiX0edoh')
        fake_floating_ip = fakes.FakeFloatingIP('1234', 'ippool',
                                                '1.1.1.1', '2.2.2.2',
                                                '5678')
        mock_nova.servers.create.return_value = fake_create_server
        mock_nova.servers.get.return_value = fake_server
        mock_nova.floating_ips.list.return_value = [fake_floating_ip]
        self.assertEqual(
            self.cloud._normalize_server(
                meta.obj_to_dict(fake_create_server)),
            self.cloud.create_server(
                name='server-name', image=dict(id='image=id'),
                flavor=dict(id='flavor-id'), admin_pass='ooBootheiX0edoh'))

    @mock.patch.object(shade.OpenStackCloud, "wait_for_server")
    @mock.patch.object(shade.OpenStackCloud, "nova_client")
    def test_create_server_with_admin_pass_wait(self, mock_nova, mock_wait):
        """
        Test that a server with an admin_pass passed returns the password
        """
        fake_server = fakes.FakeServer('1234', '', 'BUILD')
        fake_server_with_pass = fakes.FakeServer('1234', '', 'BUILD',
                                                 adminPass='ooBootheiX0edoh')

        mock_nova.servers.create.return_value = fake_server
        mock_nova.servers.get.return_value = fake_server
        # The wait returns non-password server
        mock_wait.return_value = self.cloud._normalize_server(
            meta.obj_to_dict(fake_server))

        server = self.cloud.create_server(
            name='server-name', image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            admin_pass='ooBootheiX0edoh', wait=True)

        # Assert that we did wait
        self.assertTrue(mock_wait.called)

        # Even with the wait, we should still get back a passworded server
        self.assertEqual(
            server,
            self.cloud._normalize_server(
                meta.obj_to_dict(fake_server_with_pass))
        )

    @mock.patch.object(shade.OpenStackCloud, "get_active_server")
    @mock.patch.object(shade.OpenStackCloud, "get_server")
    def test_wait_for_server(self, mock_get_server, mock_get_active_server):
        """
        Test that waiting for a server returns the server instance when
        its status changes to "ACTIVE".
        """
        building_server = {'id': 'fake_server_id', 'status': 'BUILDING'}
        active_server = {'id': 'fake_server_id', 'status': 'ACTIVE'}

        mock_get_server.side_effect = iter([building_server, active_server])
        mock_get_active_server.side_effect = iter([
            building_server, active_server])

        server = self.cloud.wait_for_server(building_server)

        self.assertEqual(2, mock_get_server.call_count)
        mock_get_server.assert_has_calls([
            mock.call(building_server['id']),
            mock.call(active_server['id']),
        ])

        self.assertEqual(2, mock_get_active_server.call_count)
        mock_get_active_server.assert_has_calls([
            mock.call(server=building_server, reuse=True, auto_ip=True,
                      ips=None, ip_pool=None, wait=True, timeout=mock.ANY,
                      nat_destination=None),
            mock.call(server=active_server, reuse=True, auto_ip=True,
                      ips=None, ip_pool=None, wait=True, timeout=mock.ANY,
                      nat_destination=None),
        ])

        self.assertEqual('ACTIVE', server['status'])

    @mock.patch.object(shade.OpenStackCloud, 'wait_for_server')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_wait(self, mock_nova, mock_wait):
        """
        Test that create_server with a wait actually does the wait.
        """
        fake_server = {'id': 'fake_server_id', 'status': 'BUILDING'}
        mock_nova.servers.create.return_value = fake_server

        self.cloud.create_server(
            'server-name',
            dict(id='image-id'), dict(id='flavor-id'), wait=True),

        mock_wait.assert_called_once_with(
            fake_server, auto_ip=True, ips=None,
            ip_pool=None, reuse=True, timeout=180,
            nat_destination=None,
        )

    @mock.patch.object(shade.OpenStackCloud, 'add_ips_to_server')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    @mock.patch('time.sleep')
    def test_create_server_no_addresses(
            self, mock_sleep, mock_nova, mock_add_ips_to_server):
        """
        Test that create_server with a wait throws an exception if the
        server doesn't have addresses.
        """
        build_server = fakes.FakeServer('1234', '', 'BUILD')
        fake_server = fakes.FakeServer('1234', '', 'ACTIVE')
        fake_floating_ip = fakes.FakeFloatingIP('1234', 'ippool',
                                                '1.1.1.1', '2.2.2.2',
                                                '5678')
        mock_nova.servers.create.return_value = build_server
        mock_nova.servers.get.return_value = [build_server, None]
        mock_nova.servers.list.side_effect = [[build_server], [fake_server]]
        mock_nova.servers.delete.return_value = None
        mock_nova.floating_ips.list.return_value = [fake_floating_ip]
        mock_add_ips_to_server.return_value = fake_server
        self.cloud._SERVER_AGE = 0

        self.assertRaises(
            exc.OpenStackCloudException, self.cloud.create_server,
            'server-name', {'id': 'image-id'}, {'id': 'flavor-id'},
            wait=True)

    @mock.patch('shade.OpenStackCloud.nova_client')
    @mock.patch('shade.OpenStackCloud.get_network')
    def test_create_server_network_with_no_nics(self, mock_get_network,
                                                mock_nova):
        """
        Verify that if 'network' is supplied, and 'nics' is not, that we
        attempt to get the network for the server.
        """
        self.cloud.create_server(
            'server-name',
            dict(id='image-id'), dict(id='flavor-id'), network='network-name')
        mock_get_network.assert_called_once_with(name_or_id='network-name')

    @mock.patch('shade.OpenStackCloud.nova_client')
    @mock.patch('shade.OpenStackCloud.get_network')
    def test_create_server_network_with_empty_nics(self,
                                                   mock_get_network,
                                                   mock_nova):
        """
        Verify that if 'network' is supplied, along with an empty 'nics' list,
        it's treated the same as if 'nics' were not included.
        """
        self.cloud.create_server(
            'server-name', dict(id='image-id'), dict(id='flavor-id'),
            network='network-name', nics=[])
        mock_get_network.assert_called_once_with(name_or_id='network-name')

    @mock.patch.object(shade.OpenStackCloud, 'get_server_by_id')
    @mock.patch.object(shade.OpenStackCloud, 'get_image')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_server_get_flavor_image(
            self, mock_nova, mock_image, mock_get_server_by_id):

        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/flavors/detail?is_public=None'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 json={'flavors': fakes.FAKE_FLAVOR_LIST})])

        self.cloud.create_server(
            'server-name', 'image-id', 'vanilla',
            nics=[{'net-id': 'some-network'}])
        mock_image.assert_called_once()

        self.assert_calls()
