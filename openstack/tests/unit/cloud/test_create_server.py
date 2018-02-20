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
import uuid

import mock

import openstack.cloud
from openstack.cloud import exc
from openstack.cloud import meta
from openstack.tests import fakes
from openstack.tests.unit import base


class TestCreateServer(base.TestCase):

    def test_create_server_with_get_exception(self):
        """
        Test that a bad status code when attempting to get the server instance
        raises an exception in create_server.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 status_code=404),
        ])
        self.assertRaises(
            exc.OpenStackCloudException, self.cloud.create_server,
            'server-name', {'id': 'image-id'}, {'id': 'flavor-id'})
        self.assert_calls()

    def test_create_server_with_server_error(self):
        """
        Test that a server error before we return or begin waiting for the
        server instance spawn raises an exception in create_server.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        error_server = fakes.make_fake_server('1234', '', 'ERROR')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': error_server}),
        ])
        self.assertRaises(
            exc.OpenStackCloudException, self.cloud.create_server,
            'server-name', {'id': 'image-id'}, {'id': 'flavor-id'})
        self.assert_calls()

    def test_create_server_wait_server_error(self):
        """
        Test that a server error while waiting for the server to spawn
        raises an exception in create_server.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        error_server = fakes.make_fake_server('1234', '', 'ERROR')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [build_server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [error_server]}),
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_server,
            'server-name', dict(id='image-id'),
            dict(id='flavor-id'), wait=True)

        self.assert_calls()

    def test_create_server_with_timeout(self):
        """
        Test that a timeout while waiting for the server to spawn raises an
        exception in create_server.
        """
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': fake_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [fake_server]}),
        ])
        self.assertRaises(
            exc.OpenStackCloudTimeout,
            self.cloud.create_server,
            'server-name',
            dict(id='image-id'), dict(id='flavor-id'),
            wait=True, timeout=0.01)
        # We poll at the end, so we don't know real counts
        self.assert_calls(do_count=False)

    def test_create_server_no_wait(self):
        """
        Test that create_server with no wait and no exception in the
        create call returns the server instance.
        """
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': fake_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': fake_server}),
        ])
        normalized = self.cloud._expand_server(
            self.cloud._normalize_server(fake_server), False, False)
        self.assertEqual(
            normalized,
            self.cloud.create_server(
                name='server-name',
                image=dict(id='image-id'),
                flavor=dict(id='flavor-id')))

        self.assert_calls()

    def test_create_server_config_drive(self):
        """
        Test that config_drive gets passed in properly
        """
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': fake_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'config_drive': True,
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': fake_server}),
        ])
        normalized = self.cloud._expand_server(
            self.cloud._normalize_server(fake_server), False, False)
        self.assertEqual(
            normalized,
            self.cloud.create_server(
                name='server-name',
                image=dict(id='image-id'),
                flavor=dict(id='flavor-id'),
                config_drive=True))

        self.assert_calls()

    def test_create_server_config_drive_none(self):
        """
        Test that config_drive gets not passed in properly
        """
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': fake_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': fake_server}),
        ])
        normalized = self.cloud._expand_server(
            self.cloud._normalize_server(fake_server), False, False)
        self.assertEqual(
            normalized,
            self.cloud.create_server(
                name='server-name',
                image=dict(id='image-id'),
                flavor=dict(id='flavor-id'),
                config_drive=None))

        self.assert_calls()

    def test_create_server_with_admin_pass_no_wait(self):
        """
        Test that a server with an admin_pass passed returns the password
        """
        admin_pass = self.getUniqueString('password')
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_create_server = fakes.make_fake_server(
            '1234', '', 'BUILD', admin_pass=admin_pass)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': fake_create_server},
                 validate=dict(
                     json={'server': {
                         u'adminPass': admin_pass,
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': fake_server}),
        ])
        self.assertEqual(
            self.cloud._normalize_server(fake_create_server)['adminPass'],
            self.cloud.create_server(
                name='server-name', image=dict(id='image-id'),
                flavor=dict(id='flavor-id'),
                admin_pass=admin_pass)['adminPass'])

        self.assert_calls()

    @mock.patch.object(openstack.cloud.OpenStackCloud, "wait_for_server")
    def test_create_server_with_admin_pass_wait(self, mock_wait):
        """
        Test that a server with an admin_pass passed returns the password
        """
        admin_pass = self.getUniqueString('password')
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_server_with_pass = fakes.make_fake_server(
            '1234', '', 'BUILD', admin_pass=admin_pass)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': fake_server_with_pass},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'adminPass': admin_pass,
                         u'name': u'server-name'}})),
        ])

        # The wait returns non-password server
        mock_wait.return_value = self.cloud._normalize_server(fake_server)

        server = self.cloud.create_server(
            name='server-name', image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            admin_pass=admin_pass, wait=True)

        # Assert that we did wait
        self.assertTrue(mock_wait.called)

        # Even with the wait, we should still get back a passworded server
        self.assertEqual(
            server['adminPass'],
            self.cloud._normalize_server(fake_server_with_pass)['adminPass']
        )
        self.assert_calls()

    def test_create_server_user_data_base64(self):
        """
        Test that a server passed user-data sends it base64 encoded.
        """
        user_data = self.getUniqueString('user_data')
        user_data_b64 = base64.b64encode(
            user_data.encode('utf-8')).decode('utf-8')
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_server['user_data'] = user_data

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': fake_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'user_data': user_data_b64,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': fake_server}),
        ])

        self.cloud.create_server(
            name='server-name', image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            userdata=user_data, wait=False)

        self.assert_calls()

    @mock.patch.object(openstack.cloud.OpenStackCloud, "get_active_server")
    @mock.patch.object(openstack.cloud.OpenStackCloud, "get_server")
    def test_wait_for_server(self, mock_get_server, mock_get_active_server):
        """
        Test that waiting for a server returns the server instance when
        its status changes to "ACTIVE".
        """
        # TODO(mordred) Rework this to not mock methods
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

    @mock.patch.object(openstack.cloud.OpenStackCloud, 'wait_for_server')
    def test_create_server_wait(self, mock_wait):
        """
        Test that create_server with a wait actually does the wait.
        """
        # TODO(mordred) Make this a full proper response
        fake_server = fakes.make_fake_server('1234', '', 'BUILD')

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': fake_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
        ])
        self.cloud.create_server(
            'server-name',
            dict(id='image-id'), dict(id='flavor-id'), wait=True),

        mock_wait.assert_called_once_with(
            fake_server,
            auto_ip=True, ips=None,
            ip_pool=None, reuse=True, timeout=180,
            nat_destination=None,
        )
        self.assert_calls()

    @mock.patch.object(openstack.cloud.OpenStackCloud, 'add_ips_to_server')
    def test_create_server_no_addresses(
            self, mock_add_ips_to_server):
        """
        Test that create_server with a wait throws an exception if the
        server doesn't have addresses.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        fake_server = fakes.make_fake_server(
            '1234', '', 'ACTIVE', addresses={})
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [build_server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [fake_server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json'],
                     qs_elements=['device_id=1234']),
                 json={'ports': []}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234'])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        mock_add_ips_to_server.return_value = fake_server
        self.cloud._SERVER_AGE = 0

        self.assertRaises(
            exc.OpenStackCloudException, self.cloud.create_server,
            'server-name', {'id': 'image-id'}, {'id': 'flavor-id'},
            wait=True)

        self.assert_calls()

    def test_create_server_network_with_no_nics(self):
        """
        Verify that if 'network' is supplied, and 'nics' is not, that we
        attempt to get the network for the server.
        """
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        network = {
            'id': 'network-id',
            'name': 'network-name'
        }
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [network]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'networks': [{u'uuid': u'network-id'}],
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': build_server}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [network]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': []}),
        ])
        self.cloud.create_server(
            'server-name',
            dict(id='image-id'), dict(id='flavor-id'), network='network-name')
        self.assert_calls()

    def test_create_server_network_with_empty_nics(self):
        """
        Verify that if 'network' is supplied, along with an empty 'nics' list,
        it's treated the same as if 'nics' were not included.
        """
        network = {
            'id': 'network-id',
            'name': 'network-name'
        }
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [network]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': u'flavor-id',
                         u'imageRef': u'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'networks': [{u'uuid': u'network-id'}],
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': build_server}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [network]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': []}),
        ])
        self.cloud.create_server(
            'server-name', dict(id='image-id'), dict(id='flavor-id'),
            network='network-name', nics=[])
        self.assert_calls()

    def test_create_server_get_flavor_image(self):
        self.use_glance()
        image_id = str(uuid.uuid4())
        fake_image_dict = fakes.make_fake_image(image_id=image_id)
        fake_image_search_return = {'images': [fake_image_dict]}

        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        active_server = fakes.make_fake_server('1234', '', 'BUILD')

        self.register_uris([
            dict(method='GET',
                 uri='https://image.example.com/v2/images',
                 json=fake_image_search_return),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['flavors', 'detail'],
                     qs_elements=['is_public=None']),
                 json={'flavors': fakes.FAKE_FLAVOR_LIST}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': fakes.FLAVOR_ID,
                         u'imageRef': image_id,
                         u'max_count': 1,
                         u'min_count': 1,
                         u'networks': [{u'uuid': u'some-network'}],
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': active_server}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
        ])

        self.cloud.create_server(
            'server-name', image_id, 'vanilla',
            nics=[{'net-id': 'some-network'}], wait=False)

        self.assert_calls()

    def test_create_server_nics_port_id(self):
        '''Verify port-id in nics input turns into port in REST.'''
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        active_server = fakes.make_fake_server('1234', '', 'BUILD')
        image_id = uuid.uuid4().hex
        port_id = uuid.uuid4().hex

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': fakes.FLAVOR_ID,
                         u'imageRef': image_id,
                         u'max_count': 1,
                         u'min_count': 1,
                         u'networks': [{u'port': port_id}],
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': active_server}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
        ])

        self.cloud.create_server(
            'server-name', dict(id=image_id), dict(id=fakes.FLAVOR_ID),
            nics=[{'port-id': port_id}], wait=False)

        self.assert_calls()

    def test_create_boot_attach_volume(self):
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        active_server = fakes.make_fake_server('1234', '', 'BUILD')

        vol = {'id': 'volume001', 'status': 'available',
               'name': '', 'attachments': []}
        volume = meta.obj_to_munch(fakes.FakeVolume(**vol))

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-volumes_boot']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': 'flavor-id',
                         u'imageRef': 'image-id',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'block_device_mapping_v2': [
                             {
                                 u'boot_index': 0,
                                 u'delete_on_termination': True,
                                 u'destination_type': u'local',
                                 u'source_type': u'image',
                                 u'uuid': u'image-id'
                             },
                             {
                                 u'boot_index': u'-1',
                                 u'delete_on_termination': False,
                                 u'destination_type': u'volume',
                                 u'source_type': u'volume',
                                 u'uuid': u'volume001'
                             }
                         ],
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': active_server}),
        ])

        self.cloud.create_server(
            name='server-name',
            image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            boot_from_volume=False,
            volumes=[volume],
            wait=False)

        self.assert_calls()

    def test_create_boot_from_volume_image_terminate(self):
        build_server = fakes.make_fake_server('1234', '', 'BUILD')
        active_server = fakes.make_fake_server('1234', '', 'BUILD')

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-volumes_boot']),
                 json={'server': build_server},
                 validate=dict(
                     json={'server': {
                         u'flavorRef': 'flavor-id',
                         u'imageRef': '',
                         u'max_count': 1,
                         u'min_count': 1,
                         u'block_device_mapping_v2': [{
                             u'boot_index': u'0',
                             u'delete_on_termination': True,
                             u'destination_type': u'volume',
                             u'source_type': u'image',
                             u'uuid': u'image-id',
                             u'volume_size': u'1'}],
                         u'name': u'server-name'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234']),
                 json={'server': active_server}),
        ])

        self.cloud.create_server(
            name='server-name',
            image=dict(id='image-id'),
            flavor=dict(id='flavor-id'),
            boot_from_volume=True,
            terminate_volume=True,
            volume_size=1,
            wait=False)

        self.assert_calls()
