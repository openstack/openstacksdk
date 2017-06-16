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
import uuid

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

    def test_get_server(self):
        server1 = fakes.make_fake_server('123', 'mickey')
        server2 = fakes.make_fake_server('345', 'mouse')

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server1, server2]}),
        ])

        r = self.cloud.get_server('mickey')
        self.assertIsNotNone(r)
        self.assertEqual(server1['name'], r['name'])

        self.assert_calls()

    def test_get_server_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])

        r = self.cloud.get_server('doesNotExist')
        self.assertIsNone(r)

        self.assert_calls()

    def test_list_servers_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 status_code=400)
        ])

        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.list_servers)

        self.assert_calls()

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

    def test_list_servers(self):
        server_id = str(uuid.uuid4())
        server_name = self.getUniqueString('name')
        fake_server = fakes.make_fake_server(server_id, server_name)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [fake_server]}),
        ])

        r = self.cloud.list_servers()

        self.assertEqual(1, len(r))
        self.assertEqual(server_name, r[0]['name'])

        self.assert_calls()

    def test_list_servers_all_projects(self):
        '''This test verifies that when list_servers is called with
        `all_projects=True` that it passes `all_tenants=True` to nova.'''
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail'],
                     qs_elements=['all_tenants=True']),
                 complete_qs=True,
                 json={'servers': []}),
        ])

        self.cloud.list_servers(all_projects=True)

        self.assert_calls()

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
