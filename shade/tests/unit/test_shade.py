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

import mock
import munch

import testtools

import shade
from shade import _utils
from shade import exc
from shade.tests import fakes
from shade.tests.unit import base


RANGE_DATA = [
    dict(id=1, key1=1, key2=5),
    dict(id=2, key1=1, key2=20),
    dict(id=3, key1=2, key2=10),
    dict(id=4, key1=2, key2=30),
    dict(id=5, key1=3, key2=40),
    dict(id=6, key1=3, key2=40),
]


class TestShade(base.RequestsMockTestCase):

    def setUp(self):
        # This set of tests are not testing neutron, they're testing
        # rebuilding servers, but we do several network calls in service
        # of a NORMAL rebuild to find the default_network. Putting
        # in all of the neutron mocks for that will make the tests harder
        # to read. SO - we're going mock neutron into the off position
        # and then turn it back on in the few tests that specifically do.
        # Maybe we should reorg these into two classes - one with neutron
        # mocked out - and one with it not mocked out
        super(TestShade, self).setUp()
        self.has_neutron = False

        def fake_has_service(*args, **kwargs):
            return self.has_neutron

        self.cloud.has_service = fake_has_service

    def test_openstack_cloud(self):
        self.assertIsInstance(self.cloud, shade.OpenStackCloud)

    @mock.patch.object(shade.OpenStackCloud, 'search_images')
    def test_get_images(self, mock_search):
        image1 = dict(id='123', name='mickey')
        mock_search.return_value = [image1]
        r = self.cloud.get_image('mickey')
        self.assertIsNotNone(r)
        self.assertDictEqual(image1, r)

    @mock.patch.object(shade.OpenStackCloud, 'search_images')
    def test_get_image_not_found(self, mock_search):
        mock_search.return_value = []
        r = self.cloud.get_image('doesNotExist')
        self.assertIsNone(r)

    @mock.patch.object(shade.OpenStackCloud, '_expand_server')
    @mock.patch.object(shade.OpenStackCloud, 'list_servers')
    def test_get_server(self, mock_list, mock_expand):
        server1 = dict(id='123', name='mickey')
        server2 = dict(id='345', name='mouse')

        def expand_server(server, detailed, bare):
            return server
        mock_expand.side_effect = expand_server
        mock_list.return_value = [server1, server2]
        r = self.cloud.get_server('mickey')
        self.assertIsNotNone(r)
        self.assertDictEqual(server1, r)

    @mock.patch.object(shade.OpenStackCloud, 'search_servers')
    def test_get_server_not_found(self, mock_search):
        mock_search.return_value = []
        r = self.cloud.get_server('doesNotExist')
        self.assertIsNone(r)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_servers_exception(self, mock_client):
        mock_client.servers.list.side_effect = Exception()
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.list_servers)

    def test__neutron_exceptions_resource_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 status_code=404)
        ])
        self.assertRaises(exc.OpenStackCloudResourceNotFound,
                          self.cloud.list_networks)
        self.assert_calls()

    def test__neutron_exceptions_url_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 status_code=404)
        ])
        self.assertRaises(exc.OpenStackCloudURINotFound,
                          self.cloud.list_networks)
        self.assert_calls()

    @mock.patch.object(shade._tasks.ServerList, 'main')
    @mock.patch('shade.meta.add_server_interfaces')
    def test_list_servers(self, mock_add_srv_int, mock_serverlist):
        '''This test verifies that calling list_servers results in a call
        to the ServerList task.'''
        server_obj = munch.Munch({'name': 'testserver',
                                  'id': '1',
                                  'flavor': {},
                                  'addresses': {},
                                  'accessIPv4': '',
                                  'accessIPv6': '',
                                  'image': ''})
        mock_serverlist.return_value = [server_obj]
        mock_add_srv_int.side_effect = [server_obj]

        r = self.cloud.list_servers()

        self.assertEqual(1, len(r))
        self.assertEqual(1, mock_add_srv_int.call_count)
        self.assertEqual('testserver', r[0]['name'])

    @mock.patch.object(shade._tasks.ServerList, 'main')
    @mock.patch('shade.meta.get_hostvars_from_server')
    def test_list_servers_detailed(self,
                                   mock_get_hostvars_from_server,
                                   mock_serverlist):
        '''This test verifies that when list_servers is called with
        `detailed=True` that it calls `get_hostvars_from_server` for each
        server in the list.'''
        mock_serverlist.return_value = [
            fakes.FakeServer('server1', '', 'ACTIVE'),
            fakes.FakeServer('server2', '', 'ACTIVE'),
        ]
        mock_get_hostvars_from_server.side_effect = [
            {'name': 'server1', 'id': '1'},
            {'name': 'server2', 'id': '2'},
        ]

        r = self.cloud.list_servers(detailed=True)

        self.assertEqual(2, len(r))
        self.assertEqual(len(r), mock_get_hostvars_from_server.call_count)
        self.assertEqual('server1', r[0]['name'])
        self.assertEqual('server2', r[1]['name'])

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_servers_all_projects(self, mock_nova_client):
        '''This test verifies that when list_servers is called with
        `all_projects=True` that it passes `all_tenants=1` to novaclient.'''
        mock_nova_client.servers.list.return_value = [
            fakes.FakeServer('server1', '', 'ACTIVE'),
            fakes.FakeServer('server2', '', 'ACTIVE'),
        ]

        self.cloud.list_servers(all_projects=True)

        mock_nova_client.servers.list.assert_called_with(
            search_opts={'all_tenants': True})

    def test_iterate_timeout_bad_wait(self):
        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Wait value must be an int or float value."):
            for count in _utils._iterate_timeout(
                    1, "test_iterate_timeout_bad_wait", wait="timeishard"):
                pass

    @mock.patch('time.sleep')
    def test_iterate_timeout_str_wait(self, mock_sleep):
        iter = _utils._iterate_timeout(
            10, "test_iterate_timeout_str_wait", wait="1.6")
        next(iter)
        next(iter)
        mock_sleep.assert_called_with(1.6)

    @mock.patch('time.sleep')
    def test_iterate_timeout_int_wait(self, mock_sleep):
        iter = _utils._iterate_timeout(
            10, "test_iterate_timeout_int_wait", wait=1)
        next(iter)
        next(iter)
        mock_sleep.assert_called_with(1.0)

    @mock.patch('time.sleep')
    def test_iterate_timeout_timeout(self, mock_sleep):
        message = "timeout test"
        with testtools.ExpectedException(
                exc.OpenStackCloudTimeout,
                message):
            for count in _utils._iterate_timeout(0.1, message, wait=1):
                pass
        mock_sleep.assert_called_with(1.0)

    def test__nova_extensions(self):
        body = [
            {
                "updated": "2014-12-03T00:00:00Z",
                "name": "Multinic",
                "links": [],
                "namespace": "http://openstack.org/compute/ext/fake_xml",
                "alias": "NMN",
                "description": "Multiple network support."
            },
            {
                "updated": "2014-12-03T00:00:00Z",
                "name": "DiskConfig",
                "links": [],
                "namespace": "http://openstack.org/compute/ext/fake_xml",
                "alias": "OS-DCF",
                "description": "Disk Management Extension."
            },
        ]
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/extensions'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 json=dict(extensions=body))
        ])
        extensions = self.cloud._nova_extensions()
        self.assertEqual(set(['NMN', 'OS-DCF']), extensions)

        self.assert_calls()

    def test__nova_extensions_fails(self):
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/extensions'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 status_code=404),
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudURINotFound,
            "Error fetching extension list for nova"
        ):
            self.cloud._nova_extensions()

        self.assert_calls()

    def test__has_nova_extension(self):
        body = [
            {
                "updated": "2014-12-03T00:00:00Z",
                "name": "Multinic",
                "links": [],
                "namespace": "http://openstack.org/compute/ext/fake_xml",
                "alias": "NMN",
                "description": "Multiple network support."
            },
            {
                "updated": "2014-12-03T00:00:00Z",
                "name": "DiskConfig",
                "links": [],
                "namespace": "http://openstack.org/compute/ext/fake_xml",
                "alias": "OS-DCF",
                "description": "Disk Management Extension."
            },
        ]
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/extensions'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 json=dict(extensions=body))
        ])
        self.assertTrue(self.cloud._has_nova_extension('NMN'))

        self.assert_calls()

    def test__has_nova_extension_missing(self):
        body = [
            {
                "updated": "2014-12-03T00:00:00Z",
                "name": "Multinic",
                "links": [],
                "namespace": "http://openstack.org/compute/ext/fake_xml",
                "alias": "NMN",
                "description": "Multiple network support."
            },
            {
                "updated": "2014-12-03T00:00:00Z",
                "name": "DiskConfig",
                "links": [],
                "namespace": "http://openstack.org/compute/ext/fake_xml",
                "alias": "OS-DCF",
                "description": "Disk Management Extension."
            },
        ]
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/extensions'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 json=dict(extensions=body))
        ])
        self.assertFalse(self.cloud._has_nova_extension('invalid'))

        self.assert_calls()

    def test_range_search(self):
        filters = {"key1": "min", "key2": "20"}
        retval = self.cloud.range_search(RANGE_DATA, filters)
        self.assertIsInstance(retval, list)
        self.assertEqual(1, len(retval))
        self.assertEqual([RANGE_DATA[1]], retval)

    def test_range_search_2(self):
        filters = {"key1": "<=2", "key2": ">10"}
        retval = self.cloud.range_search(RANGE_DATA, filters)
        self.assertIsInstance(retval, list)
        self.assertEqual(2, len(retval))
        self.assertEqual([RANGE_DATA[1], RANGE_DATA[3]], retval)

    def test_range_search_3(self):
        filters = {"key1": "2", "key2": "min"}
        retval = self.cloud.range_search(RANGE_DATA, filters)
        self.assertIsInstance(retval, list)
        self.assertEqual(0, len(retval))

    def test_range_search_4(self):
        filters = {"key1": "max", "key2": "min"}
        retval = self.cloud.range_search(RANGE_DATA, filters)
        self.assertIsInstance(retval, list)
        self.assertEqual(0, len(retval))

    def test_range_search_5(self):
        filters = {"key1": "min", "key2": "min"}
        retval = self.cloud.range_search(RANGE_DATA, filters)
        self.assertIsInstance(retval, list)
        self.assertEqual(1, len(retval))
        self.assertEqual([RANGE_DATA[0]], retval)
