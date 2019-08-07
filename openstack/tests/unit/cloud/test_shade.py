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

from openstack.cloud import exc
from openstack import connection
from openstack.tests import fakes
from openstack.tests.unit import base
from openstack import utils


RANGE_DATA = [
    dict(id=1, key1=1, key2=5),
    dict(id=2, key1=1, key2=20),
    dict(id=3, key1=2, key2=10),
    dict(id=4, key1=2, key2=30),
    dict(id=5, key1=3, key2=40),
    dict(id=6, key1=3, key2=40),
]


class TestShade(base.TestCase):

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
        self.assertIsInstance(self.cloud, connection.Connection)

    def test_endpoint_for(self):
        dns_override = 'https://override.dns.example.com'
        self.cloud.config.config['dns_endpoint_override'] = dns_override
        self.assertEqual(
            'https://compute.example.com/v2.1/',
            self.cloud.endpoint_for('compute'))
        self.assertEqual(
            'https://internal.compute.example.com/v2.1/',
            self.cloud.endpoint_for('compute', interface='internal'))
        self.assertIsNone(
            self.cloud.endpoint_for('compute', region_name='unknown-region'))
        self.assertEqual(
            dns_override,
            self.cloud.endpoint_for('dns'))

    def test_connect_as(self):
        # Do initial auth/catalog steps
        # This should authenticate a second time, but should not
        # need a second identity discovery
        project_name = 'test_project'
        self.register_uris([
            self.get_keystone_v3_token(project_name=project_name),
            self.get_nova_discovery_mock_dict(),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    'compute', 'public', append=['servers', 'detail']),
                json={'servers': []},
            ),
        ])

        c2 = self.cloud.connect_as(project_name=project_name)
        self.assertEqual(c2.list_servers(), [])
        self.assert_calls()

    def test_connect_as_context(self):
        # Do initial auth/catalog steps
        # This should authenticate a second time, but should not
        # need a second identity discovery
        project_name = 'test_project'
        self.register_uris([
            self.get_keystone_v3_token(project_name=project_name),
            self.get_nova_discovery_mock_dict(),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    'compute', 'public', append=['servers', 'detail']),
                json={'servers': []},
            ),
        ])

        with self.cloud.connect_as(project_name=project_name) as c2:
            self.assertEqual(c2.list_servers(), [])
        self.assert_calls()

    @mock.patch.object(connection.Connection, 'search_images')
    def test_get_images(self, mock_search):
        image1 = dict(id='123', name='mickey')
        mock_search.return_value = [image1]
        r = self.cloud.get_image('mickey')
        self.assertIsNotNone(r)
        self.assertDictEqual(image1, r)

    @mock.patch.object(connection.Connection, 'search_images')
    def test_get_image_not_found(self, mock_search):
        mock_search.return_value = []
        r = self.cloud.get_image('doesNotExist')
        self.assertIsNone(r)

    def test_global_request_id(self):
        request_id = uuid.uuid4().hex
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    'compute', 'public', append=['servers', 'detail']),
                json={'servers': []},
                validate=dict(
                    headers={'X-Openstack-Request-Id': request_id}),
            ),
        ])

        cloud2 = self.cloud.global_request(request_id)
        self.assertEqual([], cloud2.list_servers())

        self.assert_calls()

    def test_global_request_id_context(self):
        request_id = uuid.uuid4().hex
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    'compute', 'public', append=['servers', 'detail']),
                json={'servers': []},
                validate=dict(
                    headers={'X-Openstack-Request-Id': request_id}),
            ),
        ])

        with self.cloud.global_request(request_id) as c2:
            self.assertEqual([], c2.list_servers())

        self.assert_calls()

    def test_get_server(self):
        server1 = fakes.make_fake_server('123', 'mickey')
        server2 = fakes.make_fake_server('345', 'mouse')

        self.register_uris([
            self.get_nova_discovery_mock_dict(),
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
            self.get_nova_discovery_mock_dict(),
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
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 status_code=400)
        ])

        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.list_servers)

        self.assert_calls()

    def test_neutron_not_found(self):
        self.use_nothing()
        self.cloud.has_service = mock.Mock(return_value=False)
        self.assertEqual([], self.cloud.list_networks())
        self.assert_calls()

    def test_list_servers(self):
        server_id = str(uuid.uuid4())
        server_name = self.getUniqueString('name')
        fake_server = fakes.make_fake_server(server_id, server_name)
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [fake_server]}),
        ])

        r = self.cloud.list_servers()

        self.assertEqual(1, len(r))
        self.assertEqual(server_name, r[0]['name'])

        self.assert_calls()

    def test_list_server_private_ip(self):
        self.has_neutron = True
        fake_server = {
            "OS-EXT-STS:task_state": None,
            "addresses": {
                "private": [
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:b4:a3:07",
                        "version": 4,
                        "addr": "10.4.0.13",
                        "OS-EXT-IPS:type": "fixed"
                    }, {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:b4:a3:07",
                        "version": 4,
                        "addr": "89.40.216.229",
                        "OS-EXT-IPS:type": "floating"
                    }]},
            "links": [
                {
                    "href": "http://example.com/images/95e4c4",
                    "rel": "self"
                }, {
                    "href": "http://example.com/images/95e4c4",
                    "rel": "bookmark"
                }
            ],
            "image": {
                "id": "95e4c449-8abf-486e-97d9-dc3f82417d2d",
                "links": [
                    {
                        "href": "http://example.com/images/95e4c4",
                        "rel": "bookmark"
                    }
                ]
            },
            "OS-EXT-STS:vm_state": "active",
            "OS-SRV-USG:launched_at": "2018-03-01T02:44:50.000000",
            "flavor": {
                "id": "3bd99062-2fe8-4eac-93f0-9200cc0f97ae",
                "links": [
                    {
                        "href": "http://example.com/flavors/95e4c4",
                        "rel": "bookmark"
                    }
                ]
            },
            "id": "97fe35e9-756a-41a2-960a-1d057d2c9ee4",
            "security_groups": [{"name": "default"}],
            "user_id": "c17534835f8f42bf98fc367e0bf35e09",
            "OS-DCF:diskConfig": "MANUAL",
            "accessIPv4": "",
            "accessIPv6": "",
            "progress": 0,
            "OS-EXT-STS:power_state": 1,
            "OS-EXT-AZ:availability_zone": "nova",
            "metadata": {},
            "status": "ACTIVE",
            "updated": "2018-03-01T02:44:51Z",
            "hostId": "",
            "OS-SRV-USG:terminated_at": None,
            "key_name": None,
            "name": "mttest",
            "created": "2018-03-01T02:44:46Z",
            "tenant_id": "65222a4d09ea4c68934fa1028c77f394",
            "os-extended-volumes:volumes_attached": [],
            "config_drive": ""
        }
        fake_networks = {"networks": [
            {
                "status": "ACTIVE",
                "router:external": True,
                "availability_zone_hints": [],
                "availability_zones": ["nova"],
                "description": None,
                "subnets": [
                    "df3e17fa-a4b2-47ae-9015-bc93eb076ba2",
                    "6b0c3dc9-b0b8-4d87-976a-7f2ebf13e7ec",
                    "fc541f48-fc7f-48c0-a063-18de6ee7bdd7"
                ],
                "shared": False,
                "tenant_id": "a564613210ee43708b8a7fc6274ebd63",
                "tags": [],
                "ipv6_address_scope": "9f03124f-89af-483a-b6fd-10f08079db4d",
                "mtu": 1550,
                "is_default": False,
                "admin_state_up": True,
                "revision_number": 0,
                "ipv4_address_scope": None,
                "port_security_enabled": True,
                "project_id": "a564613210ee43708b8a7fc6274ebd63",
                "id": "0232c17f-2096-49bc-b205-d3dcd9a30ebf",
                "name": "ext-net"
            }, {
                "status": "ACTIVE",
                "router:external": False,
                "availability_zone_hints": [],
                "availability_zones": ["nova"],
                "description": "",
                "subnets": ["f0ad1df5-53ee-473f-b86b-3604ea5591e9"],
                "shared": False,
                "tenant_id": "65222a4d09ea4c68934fa1028c77f394",
                "created_at": "2016-10-22T13:46:26Z",
                "tags": [],
                "ipv6_address_scope": None,
                "updated_at": "2016-10-22T13:46:26Z",
                "admin_state_up": True,
                "mtu": 1500,
                "revision_number": 0,
                "ipv4_address_scope": None,
                "port_security_enabled": True,
                "project_id": "65222a4d09ea4c68934fa1028c77f394",
                "id": "2c9adcb5-c123-4c5a-a2ba-1ad4c4e1481f",
                "name": "private"
            }]}
        fake_subnets = {
            "subnets": [
                {
                    "service_types": [],
                    "description": "",
                    "enable_dhcp": True,
                    "tags": [],
                    "network_id": "827c6bb6-492f-4168-9577-f3a131eb29e8",
                    "tenant_id": "65222a4d09ea4c68934fa1028c77f394",
                    "created_at": "2017-06-12T13:23:57Z",
                    "dns_nameservers": [],
                    "updated_at": "2017-06-12T13:23:57Z",
                    "gateway_ip": "10.24.4.1",
                    "ipv6_ra_mode": None,
                    "allocation_pools": [
                        {
                            "start": "10.24.4.2",
                            "end": "10.24.4.254"
                        }],
                    "host_routes": [],
                    "revision_number": 0,
                    "ip_version": 4,
                    "ipv6_address_mode": None,
                    "cidr": "10.24.4.0/24",
                    "project_id": "65222a4d09ea4c68934fa1028c77f394",
                    "id": "3f0642d9-4644-4dff-af25-bcf64f739698",
                    "subnetpool_id": None,
                    "name": "foo_subnet"
                }, {
                    "service_types": [],
                    "description": "",
                    "enable_dhcp": True,
                    "tags": [],
                    "network_id": "2c9adcb5-c123-4c5a-a2ba-1ad4c4e1481f",
                    "tenant_id": "65222a4d09ea4c68934fa1028c77f394",
                    "created_at": "2016-10-22T13:46:26Z",
                    "dns_nameservers": ["89.36.90.101", "89.36.90.102"],
                    "updated_at": "2016-10-22T13:46:26Z",
                    "gateway_ip": "10.4.0.1",
                    "ipv6_ra_mode": None,
                    "allocation_pools": [
                        {
                            "start": "10.4.0.2",
                            "end": "10.4.0.200"
                        }],
                    "host_routes": [],
                    "revision_number": 0,
                    "ip_version": 4,
                    "ipv6_address_mode": None,
                    "cidr": "10.4.0.0/24",
                    "project_id": "65222a4d09ea4c68934fa1028c77f394",
                    "id": "f0ad1df5-53ee-473f-b86b-3604ea5591e9",
                    "subnetpool_id": None,
                    "name": "private-subnet-ipv4"
                }]}
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [fake_server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json=fake_networks),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json=fake_subnets)
        ])

        r = self.cloud.get_server('97fe35e9-756a-41a2-960a-1d057d2c9ee4')

        self.assertEqual('10.4.0.13', r['private_v4'])

        self.assert_calls()

    def test_list_servers_all_projects(self):
        '''This test verifies that when list_servers is called with
        `all_projects=True` that it passes `all_tenants=True` to nova.'''
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail'],
                     qs_elements=['all_tenants=True']),
                 complete_qs=True,
                 json={'servers': []}),
        ])

        self.cloud.list_servers(all_projects=True)

        self.assert_calls()

    def test_list_servers_filters(self):
        '''This test verifies that when list_servers is called with
        `filters` dict that it passes it to nova.'''
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail'],
                     qs_elements=[
                         'deleted=True',
                         'changes-since=2014-12-03T00:00:00Z'
                     ]),
                 complete_qs=True,
                 json={'servers': []}),
        ])

        self.cloud.list_servers(filters={
            'deleted': True,
            'changes-since': '2014-12-03T00:00:00Z'
        })

        self.assert_calls()

    def test_iterate_timeout_bad_wait(self):
        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Wait value must be an int or float value."):
            for count in utils.iterate_timeout(
                    1, "test_iterate_timeout_bad_wait", wait="timeishard"):
                pass

    @mock.patch('time.sleep')
    def test_iterate_timeout_str_wait(self, mock_sleep):
        iter = utils.iterate_timeout(
            10, "test_iterate_timeout_str_wait", wait="1.6")
        next(iter)
        next(iter)
        mock_sleep.assert_called_with(1.6)

    @mock.patch('time.sleep')
    def test_iterate_timeout_int_wait(self, mock_sleep):
        iter = utils.iterate_timeout(
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
            for count in utils.iterate_timeout(0.1, message, wait=1):
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

    def test__neutron_extensions(self):
        body = [
            {
                "updated": "2014-06-1T10:00:00-00:00",
                "name": "Distributed Virtual Router",
                "links": [],
                "alias": "dvr",
                "description":
                    "Enables configuration of Distributed Virtual Routers."
            },
            {
                "updated": "2013-07-23T10:00:00-00:00",
                "name": "Allowed Address Pairs",
                "links": [],
                "alias": "allowed-address-pairs",
                "description": "Provides allowed address pairs"
            },
        ]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json=dict(extensions=body))
        ])
        extensions = self.cloud._neutron_extensions()
        self.assertEqual(set(['dvr', 'allowed-address-pairs']), extensions)

        self.assert_calls()

    def test__neutron_extensions_fails(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 status_code=404)
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudURINotFound,
            "Error fetching extension list for neutron"
        ):
            self.cloud._neutron_extensions()

        self.assert_calls()

    def test__has_neutron_extension(self):
        body = [
            {
                "updated": "2014-06-1T10:00:00-00:00",
                "name": "Distributed Virtual Router",
                "links": [],
                "alias": "dvr",
                "description":
                    "Enables configuration of Distributed Virtual Routers."
            },
            {
                "updated": "2013-07-23T10:00:00-00:00",
                "name": "Allowed Address Pairs",
                "links": [],
                "alias": "allowed-address-pairs",
                "description": "Provides allowed address pairs"
            },
        ]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json=dict(extensions=body))
        ])
        self.assertTrue(self.cloud._has_neutron_extension('dvr'))
        self.assert_calls()

    def test__has_neutron_extension_missing(self):
        body = [
            {
                "updated": "2014-06-1T10:00:00-00:00",
                "name": "Distributed Virtual Router",
                "links": [],
                "alias": "dvr",
                "description":
                    "Enables configuration of Distributed Virtual Routers."
            },
            {
                "updated": "2013-07-23T10:00:00-00:00",
                "name": "Allowed Address Pairs",
                "links": [],
                "alias": "allowed-address-pairs",
                "description": "Provides allowed address pairs"
            },
        ]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json=dict(extensions=body))
        ])
        self.assertFalse(self.cloud._has_neutron_extension('invalid'))
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
