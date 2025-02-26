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

import base64
from unittest import mock
import uuid

from openstack.compute.v2 import server
from openstack import connection
from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestCreateServer(base.TestCase):
    def _compare_servers(self, exp, real):
        self.assertDictEqual(
            server.Server(**exp).to_dict(computed=False),
            real.to_dict(computed=False),
        )

    def test_create_server_with_get_exception(self):
        """
        Test that a bad status code when attempting to get the server instance
        raises an exception in create_server.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    status_code=404,
                ),
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_server,
            'server-name',
            {'id': 'image-id'},
            {'id': 'flavor-id'},
        )
        self.assert_calls()

    def test_create_server_with_server_error(self):
        """
        Test that a server error before we return or begin waiting for the
        server instance spawn raises an exception in create_server.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        error_server = fakes.make_fake_server('1234', '', 'ERROR')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': error_server},
                ),
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_server,
            'server-name',
            {'id': 'image-id'},
            {'id': 'flavor-id'},
        )
        self.assert_calls()

    def test_create_server_wait_server_error(self):
        """
        Test that a server error while waiting for the server to spawn
        raises an exception in create_server.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        error_server = fakes.make_fake_server('1234', '', 'ERROR')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': build_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': error_server},
                ),
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_server,
            'server-name',
            dict(id='image-id'),
            dict(id='flavor-id'),
            wait=True,
        )

        self.assert_calls()

    def test_create_server_with_timeout(self):
        """
        Test that a timeout while waiting for the server to spawn raises an
        exception in create_server.
        """
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
            ]
        )
        self.assertRaises(
            exceptions.ResourceTimeout,
            self.cloud.create_server,
            'server-name',
            dict(id='image-id'),
            dict(id='flavor-id'),
            wait=True,
            timeout=0.01,
        )
        # We poll at the end, so we don't know real counts
        self.assert_calls(do_count=False)

    def test_create_server_no_wait(self):
        """
        Test that create_server with no wait and no exception in the
        create call returns the server instance.
        """
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
            ]
        )
        self.assertDictEqual(
            server.Server(**fake_server).to_dict(computed=False),
            self.cloud.create_server(
                name='server-name',
                image=dict(id='image-id'),
                flavor=dict(id='flavor-id'),
            ).to_dict(computed=False),
        )

        self.assert_calls()

    def test_create_server_config_drive(self):
        """
        Test that config_drive gets passed in properly
        """
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'config_drive': True,
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
            ]
        )
        self.assertDictEqual(
            server.Server(**fake_server).to_dict(computed=False),
            self.cloud.create_server(
                name='server-name',
                image=dict(id='image-id'),
                flavor=dict(id='flavor-id'),
                config_drive=True,
            ).to_dict(computed=False),
        )

        self.assert_calls()

    def test_create_server_config_drive_none(self):
        """
        Test that config_drive gets not passed in properly
        """
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
            ]
        )
        self.assertEqual(
            server.Server(**fake_server).to_dict(computed=False),
            self.cloud.create_server(
                name='server-name',
                image=dict(id='image-id'),
                flavor=dict(id='flavor-id'),
                config_drive=None,
            ).to_dict(computed=False),
        )

        self.assert_calls()

    def test_create_server_with_admin_pass_no_wait(self):
        """
        Test that a server with an admin_pass passed returns the password
        """
        admin_pass = self.getUniqueString('password')
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_create_server = fakes.make_fake_server(
            '1234', '', 'BUILD', admin_pass=admin_pass
        )
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_create_server},
                    validate=dict(
                        json={
                            'server': {
                                'adminPass': admin_pass,
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
            ]
        )
        self.assertEqual(
            admin_pass,
            self.cloud.create_server(
                name='server-name',
                image=dict(id='image-id'),
                flavor=dict(id='flavor-id'),
                admin_pass=admin_pass,
            )['admin_password'],
        )

        self.assert_calls()

    @mock.patch.object(connection.Connection, "wait_for_server")
    def test_create_server_with_admin_pass_wait(self, mock_wait):
        """
        Test that a server with an admin_pass passed returns the password
        """
        admin_pass = self.getUniqueString('password')
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_server_with_pass = fakes.make_fake_server(
            '1234', '', 'BUILD', admin_pass=admin_pass
        )
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server_with_pass},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'adminPass': admin_pass,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
            ]
        )

        # The wait returns non-password server
        mock_wait.return_value = server.Server(**fake_server)

        new_server = self.cloud.create_server(
            name='server-name',
            image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            admin_pass=admin_pass,
            wait=True,
            timeout=0.01,
        )

        # Assert that we did wait
        self.assertTrue(mock_wait.called)

        # Even with the wait, we should still get back a passworded server
        self.assertEqual(
            new_server['admin_password'], fake_server_with_pass['adminPass']
        )
        self.assert_calls()

    def test_create_server_user_data_base64(self):
        """
        Test that a server passed user-data sends it base64 encoded.
        """
        user_data = self.getUniqueString('user_data')
        user_data_b64 = base64.b64encode(user_data.encode('utf-8')).decode(
            'utf-8'
        )
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_server['user_data'] = user_data

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'user_data': user_data_b64,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
            ]
        )

        self.cloud.create_server(
            name='server-name',
            image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            userdata=user_data,
            wait=False,
        )

        self.assert_calls()

    @mock.patch.object(connection.Connection, "get_active_server")
    @mock.patch.object(connection.Connection, "get_server")
    def test_wait_for_server(self, mock_get_server, mock_get_active_server):
        """
        Test that waiting for a server returns the server instance when
        its status changes to "ACTIVE".
        """
        # TODO(mordred) Rework this to not mock methods
        building_server = {'id': 'fake_server_id', 'status': 'BUILDING'}
        active_server = {'id': 'fake_server_id', 'status': 'ACTIVE'}

        mock_get_server.side_effect = iter([building_server, active_server])
        mock_get_active_server.side_effect = iter(
            [building_server, active_server]
        )

        server = self.cloud.wait_for_server(building_server)

        self.assertEqual(2, mock_get_server.call_count)
        mock_get_server.assert_has_calls(
            [
                mock.call(building_server['id']),
                mock.call(active_server['id']),
            ]
        )

        self.assertEqual(2, mock_get_active_server.call_count)
        mock_get_active_server.assert_has_calls(
            [
                mock.call(
                    server=building_server,
                    reuse=True,
                    auto_ip=True,
                    ips=None,
                    ip_pool=None,
                    wait=True,
                    timeout=mock.ANY,
                    nat_destination=None,
                ),
                mock.call(
                    server=active_server,
                    reuse=True,
                    auto_ip=True,
                    ips=None,
                    ip_pool=None,
                    wait=True,
                    timeout=mock.ANY,
                    nat_destination=None,
                ),
            ]
        )

        self.assertEqual('ACTIVE', server['status'])

    @mock.patch.object(connection.Connection, 'wait_for_server')
    def test_create_server_wait(self, mock_wait):
        """
        Test that create_server with a wait actually does the wait.
        """
        # TODO(mordred) Make this a full proper response
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
            ]
        )
        self.cloud.create_server(
            'server-name',
            dict(id='image-id'),
            dict(id='flavor-id'),
            wait=True,
            timeout=0.01,
        )

        # This is a pretty dirty hack to ensure we in principle use object with
        # expected properties
        srv = server.Server.existing(
            connection=self.cloud,
            min_count=1,
            max_count=1,
            networks='auto',
            imageRef='image-id',
            flavorRef='flavor-id',
            **fake_server,
        )
        mock_wait.assert_called_once_with(
            srv,
            auto_ip=True,
            ips=None,
            ip_pool=None,
            reuse=True,
            timeout=0.01,
            nat_destination=None,
        )
        self.assert_calls()

    @mock.patch.object(connection.Connection, 'add_ips_to_server')
    def test_create_server_no_addresses(self, mock_add_ips_to_server):
        """
        Test that create_server with a wait throws an exception if the
        server doesn't have addresses.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_server = fakes.make_fake_server(
            '1234', '', 'ACTIVE', addresses={}
        )
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'ports'],
                        qs_elements=['device_id=1234'],
                    ),
                    json={'ports': []},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    status_code=404,
                ),
            ]
        )
        mock_add_ips_to_server.return_value = fake_server

        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_server,
            'server-name',
            {'id': 'image-id'},
            {'id': 'flavor-id'},
            wait=True,
            timeout=0.01,
        )

        self.assert_calls()

    def test_create_server_network_with_no_nics(self):
        """
        Verify that if 'network' is supplied, and 'nics' is not, that we
        attempt to get the network for the server.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        network = {'id': 'network-id', 'name': 'network-name'}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', 'network-name'],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks'],
                        qs_elements=['name=network-name'],
                    ),
                    json={'networks': [network]},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'networks': [{'uuid': 'network-id'}],
                                'name': 'server-name',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': build_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': [network]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'subnets']
                    ),
                    json={'subnets': []},
                ),
            ]
        )
        self.cloud.create_server(
            'server-name',
            dict(id='image-id'),
            dict(id='flavor-id'),
            network='network-name',
        )
        self.assert_calls()

    def test_create_server_network_with_empty_nics(self):
        """
        Verify that if 'network' is supplied, along with an empty 'nics' list,
        it's treated the same as if 'nics' were not included.
        """
        network = {'id': 'network-id', 'name': 'network-name'}
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', 'network-name'],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks'],
                        qs_elements=['name=network-name'],
                    ),
                    json={'networks': [network]},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'networks': [{'uuid': 'network-id'}],
                                'name': 'server-name',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': build_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': [network]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'subnets']
                    ),
                    json={'subnets': []},
                ),
            ]
        )
        self.cloud.create_server(
            'server-name',
            dict(id='image-id'),
            dict(id='flavor-id'),
            network='network-name',
            nics=[],
        )
        self.assert_calls()

    def test_create_server_network_fixed_ip(self):
        """
        Verify that if 'fixed_ip' is supplied in nics, we pass it to networks
        appropriately.
        """
        network = {'id': 'network-id', 'name': 'network-name'}
        fixed_ip = '10.0.0.1'
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'networks': [{'fixed_ip': fixed_ip}],
                                'name': 'server-name',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': build_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': [network]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'subnets']
                    ),
                    json={'subnets': []},
                ),
            ]
        )
        self.cloud.create_server(
            'server-name',
            dict(id='image-id'),
            dict(id='flavor-id'),
            nics=[{'fixed_ip': fixed_ip}],
        )
        self.assert_calls()

    def test_create_server_network_v4_fixed_ip(self):
        """
        Verify that if 'v4-fixed-ip' is supplied in nics, we pass it to
        networks appropriately.
        """
        network = {'id': 'network-id', 'name': 'network-name'}
        fixed_ip = '10.0.0.1'
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'networks': [{'fixed_ip': fixed_ip}],
                                'name': 'server-name',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': build_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': [network]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'subnets']
                    ),
                    json={'subnets': []},
                ),
            ]
        )
        self.cloud.create_server(
            'server-name',
            dict(id='image-id'),
            dict(id='flavor-id'),
            nics=[{'fixed_ip': fixed_ip}],
        )
        self.assert_calls()

    def test_create_server_network_v6_fixed_ip(self):
        """
        Verify that if 'v6-fixed-ip' is supplied in nics, we pass it to
        networks appropriately.
        """
        network = {'id': 'network-id', 'name': 'network-name'}
        # Note - it doesn't actually have to be a v6 address - it's just
        # an alias.
        fixed_ip = 'fe80::28da:5fff:fe57:13ed'
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'networks': [{'fixed_ip': fixed_ip}],
                                'name': 'server-name',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': build_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': [network]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'subnets']
                    ),
                    json={'subnets': []},
                ),
            ]
        )
        self.cloud.create_server(
            'server-name',
            dict(id='image-id'),
            dict(id='flavor-id'),
            nics=[{'fixed_ip': fixed_ip}],
        )
        self.assert_calls()

    def test_create_server_network_fixed_ip_conflicts(self):
        """
        Verify that if 'fixed_ip' and 'v4-fixed-ip' are both supplied in nics,
        we throw an exception.
        """
        # Note - it doesn't actually have to be a v6 address - it's just
        # an alias.
        self.use_nothing()
        fixed_ip = '10.0.0.1'
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_server,
            'server-name',
            dict(id='image-id'),
            dict(id='flavor-id'),
            nics=[{'fixed_ip': fixed_ip, 'v4-fixed-ip': fixed_ip}],
        )
        self.assert_calls()

    def test_create_server_get_flavor_image(self):
        self.use_glance()
        image_id = str(uuid.uuid4())
        fake_image_dict = fakes.make_fake_image(image_id=image_id)
        fake_image_search_return = {'images': [fake_image_dict]}

        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        active_server = fakes.make_fake_server('1234', '', 'BUILD')

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'https://image.example.com/v2/images/{image_id}',
                    json=fake_image_search_return,
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['flavors', 'vanilla'],
                        qs_elements=[],
                    ),
                    json=fakes.FAKE_FLAVOR,
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': fakes.FLAVOR_ID,
                                'imageRef': image_id,
                                'max_count': 1,
                                'min_count': 1,
                                'networks': [{'uuid': 'some-network'}],
                                'name': 'server-name',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': active_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
            ]
        )

        self.cloud.create_server(
            'server-name',
            image_id,
            'vanilla',
            nics=[{'net-id': 'some-network'}],
            wait=False,
        )

        self.assert_calls()

    def test_create_server_nics_port_id(self):
        '''Verify port-id in nics input turns into port in REST.'''
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        active_server = fakes.make_fake_server('1234', '', 'BUILD')
        image_id = uuid.uuid4().hex
        port_id = uuid.uuid4().hex

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': fakes.FLAVOR_ID,
                                'imageRef': image_id,
                                'max_count': 1,
                                'min_count': 1,
                                'networks': [{'port': port_id}],
                                'name': 'server-name',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': active_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
            ]
        )

        self.cloud.create_server(
            'server-name',
            dict(id=image_id),
            dict(id=fakes.FLAVOR_ID),
            nics=[{'port-id': port_id}],
            wait=False,
        )

        self.assert_calls()

    def test_create_boot_attach_volume(self):
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        active_server = fakes.make_fake_server('1234', '', 'BUILD')
        volume_id = '20e82d93-14fa-475b-bfcc-f5e6246dd194'

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                self.get_cinder_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['volumes', volume_id]
                    ),
                    json={
                        'volume': {
                            'id': volume_id,
                            'status': 'available',
                            'size': 1,
                            'availability_zone': 'cinder',
                            'name': '',
                            'description': None,
                            'volume_type': 'lvmdriver-1',
                        }
                    },
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'block_device_mapping_v2': [
                                    {
                                        'boot_index': 0,
                                        'delete_on_termination': True,
                                        'destination_type': 'local',
                                        'source_type': 'image',
                                        'uuid': 'image-id',
                                    },
                                    {
                                        'boot_index': '-1',
                                        'delete_on_termination': False,
                                        'destination_type': 'volume',
                                        'source_type': 'volume',
                                        'uuid': volume_id,
                                    },
                                ],
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': active_server},
                ),
            ]
        )

        self.cloud.create_server(
            name='server-name',
            image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            boot_from_volume=False,
            volumes=[volume_id],
            wait=False,
        )

        self.assert_calls()

    def test_create_boot_from_volume_image_terminate(self):
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        active_server = fakes.make_fake_server('1234', '', 'BUILD')

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': build_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': '',
                                'max_count': 1,
                                'min_count': 1,
                                'block_device_mapping_v2': [
                                    {
                                        'boot_index': '0',
                                        'delete_on_termination': True,
                                        'destination_type': 'volume',
                                        'source_type': 'image',
                                        'uuid': 'image-id',
                                        'volume_size': '1',
                                    }
                                ],
                                'name': 'server-name',
                                'networks': 'auto',
                            }
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': active_server},
                ),
            ]
        )

        self.cloud.create_server(
            name='server-name',
            image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            boot_from_volume=True,
            terminate_volume=True,
            volume_size=1,
            wait=False,
        )

        self.assert_calls()

    def test_create_server_scheduler_hints(self):
        """
        Test that setting scheduler_hints will include them in POST request
        """
        scheduler_hints = {
            'group': self.getUniqueString('group'),
        }
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_server['scheduler_hints'] = scheduler_hints

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            },
                            'OS-SCH-HNT:scheduler_hints': scheduler_hints,
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
            ]
        )

        self.cloud.create_server(
            name='server-name',
            image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            scheduler_hints=scheduler_hints,
            wait=False,
        )

        self.assert_calls()

    def test_create_server_scheduler_hints_group_merge(self):
        """
        Test that setting both scheduler_hints and group results in merged
        hints in POST request
        """
        group_id = uuid.uuid4().hex
        group_name = self.getUniqueString('server-group')
        policies = ['affinity']
        fake_group = fakes.make_fake_server_group(
            group_id, group_name, policies
        )

        # The scheduler hints we pass in
        scheduler_hints = {
            'different_host': [],
        }

        # The scheduler hints we expect to be in POST request
        scheduler_hints_merged = {
            'different_host': [],
            'group': group_id,
        }

        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_server['scheduler_hints'] = scheduler_hints_merged

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['os-server-groups', group_id],
                    ),
                    json={'server_groups': [fake_group]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            },
                            'OS-SCH-HNT:scheduler_hints': scheduler_hints_merged,  # noqa: E501
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
            ]
        )

        self.cloud.create_server(
            name='server-name',
            image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            scheduler_hints=dict(scheduler_hints),
            group=group_id,
            wait=False,
        )

        self.assert_calls()

    def test_create_server_scheduler_hints_group_override(self):
        """
        Test that setting group in both scheduler_hints and group param prefers
        param
        """
        group_id_scheduler_hints = uuid.uuid4().hex
        group_id = uuid.uuid4().hex
        group_name = self.getUniqueString('server-group')
        policies = ['affinity']
        fake_group = fakes.make_fake_server_group(
            group_id, group_name, policies
        )

        # The scheduler hints we pass in that are expected to be ignored in
        # POST call
        scheduler_hints = {
            'group': group_id_scheduler_hints,
        }

        # The scheduler hints we expect to be in POST request
        group_scheduler_hints = {
            'group': group_id,
        }

        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_server['scheduler_hints'] = group_scheduler_hints

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['os-server-groups', group_id],
                    ),
                    json={'server_groups': [fake_group]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': []},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers']
                    ),
                    json={'server': fake_server},
                    validate=dict(
                        json={
                            'server': {
                                'flavorRef': 'flavor-id',
                                'imageRef': 'image-id',
                                'max_count': 1,
                                'min_count': 1,
                                'name': 'server-name',
                                'networks': 'auto',
                            },
                            'OS-SCH-HNT:scheduler_hints': group_scheduler_hints,  # noqa: E501
                        }
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', '1234']
                    ),
                    json={'server': fake_server},
                ),
            ]
        )

        self.cloud.create_server(
            name='server-name',
            image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            scheduler_hints=dict(scheduler_hints),
            group=group_id,
            wait=False,
        )

        self.assert_calls()
