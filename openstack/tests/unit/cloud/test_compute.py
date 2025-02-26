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

import uuid

from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestServers(base.TestCase):
    def test_get_server(self):
        server1 = fakes.make_fake_server('123', 'mickey')
        server2 = fakes.make_fake_server('345', 'mouse')

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', 'mickey']
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['name=mickey'],
                    ),
                    json={'servers': [server1, server2]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={"networks": []},
                ),
            ]
        )

        r = self.cloud.get_server('mickey')
        self.assertIsNotNone(r)
        self.assertEqual(server1['name'], r['name'])

        self.assert_calls()

    def test_get_server_not_found(self):
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', 'doesNotExist']
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['name=doesNotExist'],
                    ),
                    json={'servers': []},
                ),
            ]
        )

        r = self.cloud.get_server('doesNotExist')
        self.assertIsNone(r)

        self.assert_calls()

    def test_list_servers(self):
        server_id = str(uuid.uuid4())
        server_name = self.getUniqueString('name')
        fake_server = fakes.make_fake_server(server_id, server_name)
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', 'detail']
                    ),
                    json={'servers': [fake_server]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={"networks": []},
                ),
            ]
        )

        r = self.cloud.list_servers()

        self.assertEqual(1, len(r))
        self.assertEqual(server_name, r[0]['name'])

        self.assert_calls()

    def test_list_server_private_ip(self):
        self.has_neutron = True
        server_id = "97fe35e9-756a-41a2-960a-1d057d2c9ee4"
        fake_server = {
            "OS-EXT-STS:task_state": None,
            "addresses": {
                "private": [
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:b4:a3:07",
                        "version": 4,
                        "addr": "10.4.0.13",
                        "OS-EXT-IPS:type": "fixed",
                    },
                    {
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:b4:a3:07",
                        "version": 4,
                        "addr": "89.40.216.229",
                        "OS-EXT-IPS:type": "floating",
                    },
                ]
            },
            "links": [
                {"href": "http://example.com/images/95e4c4", "rel": "self"},
                {
                    "href": "http://example.com/images/95e4c4",
                    "rel": "bookmark",
                },
            ],
            "image": {
                "id": "95e4c449-8abf-486e-97d9-dc3f82417d2d",
                "links": [
                    {
                        "href": "http://example.com/images/95e4c4",
                        "rel": "bookmark",
                    }
                ],
            },
            "OS-EXT-STS:vm_state": "active",
            "OS-SRV-USG:launched_at": "2018-03-01T02:44:50.000000",
            "flavor": {
                "id": "3bd99062-2fe8-4eac-93f0-9200cc0f97ae",
                "links": [
                    {
                        "href": "http://example.com/flavors/95e4c4",
                        "rel": "bookmark",
                    }
                ],
            },
            "id": server_id,
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
            "config_drive": "",
        }
        fake_networks = {
            "networks": [
                {
                    "status": "ACTIVE",
                    "router:external": True,
                    "availability_zone_hints": [],
                    "availability_zones": ["nova"],
                    "description": None,
                    "subnets": [
                        "df3e17fa-a4b2-47ae-9015-bc93eb076ba2",
                        "6b0c3dc9-b0b8-4d87-976a-7f2ebf13e7ec",
                        "fc541f48-fc7f-48c0-a063-18de6ee7bdd7",
                    ],
                    "shared": False,
                    "tenant_id": "a564613210ee43708b8a7fc6274ebd63",
                    "tags": [],
                    "ipv6_address_scope": "9f03124f-89af-483a-b6fd-10f08079db4d",  # noqa: E501
                    "mtu": 1550,
                    "is_default": False,
                    "admin_state_up": True,
                    "revision_number": 0,
                    "ipv4_address_scope": None,
                    "port_security_enabled": True,
                    "project_id": "a564613210ee43708b8a7fc6274ebd63",
                    "id": "0232c17f-2096-49bc-b205-d3dcd9a30ebf",
                    "name": "ext-net",
                },
                {
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
                    "name": "private",
                },
            ]
        }
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
                        {"start": "10.24.4.2", "end": "10.24.4.254"}
                    ],
                    "host_routes": [],
                    "revision_number": 0,
                    "ip_version": 4,
                    "ipv6_address_mode": None,
                    "cidr": "10.24.4.0/24",
                    "project_id": "65222a4d09ea4c68934fa1028c77f394",
                    "id": "3f0642d9-4644-4dff-af25-bcf64f739698",
                    "subnetpool_id": None,
                    "name": "foo_subnet",
                },
                {
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
                        {"start": "10.4.0.2", "end": "10.4.0.200"}
                    ],
                    "host_routes": [],
                    "revision_number": 0,
                    "ip_version": 4,
                    "ipv6_address_mode": None,
                    "cidr": "10.4.0.0/24",
                    "project_id": "65222a4d09ea4c68934fa1028c77f394",
                    "id": "f0ad1df5-53ee-473f-b86b-3604ea5591e9",
                    "subnetpool_id": None,
                    "name": "private-subnet-ipv4",
                },
            ]
        }
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', server_id]
                    ),
                    json={'server': fake_server},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json=fake_networks,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'subnets']
                    ),
                    json=fake_subnets,
                ),
            ]
        )

        r = self.cloud.get_server(server_id)

        self.assertEqual('10.4.0.13', r['private_v4'])

        self.assert_calls()

    def test_list_servers_all_projects(self):
        """This test verifies that when list_servers is called with
        `all_projects=True` that it passes `all_tenants=True` to nova."""
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['all_tenants=True'],
                    ),
                    complete_qs=True,
                    json={'servers': []},
                ),
            ]
        )

        self.cloud.list_servers(all_projects=True)

        self.assert_calls()

    def test_list_servers_filters(self):
        """This test verifies that when list_servers is called with
        `filters` dict that it passes it to nova."""
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=[
                            'deleted=True',
                            'changes-since=2014-12-03T00:00:00Z',
                        ],
                    ),
                    complete_qs=True,
                    json={'servers': []},
                ),
            ]
        )

        self.cloud.list_servers(
            filters={'deleted': True, 'changes-since': '2014-12-03T00:00:00Z'}
        )

        self.assert_calls()

    def test_list_servers_exception(self):
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', 'detail']
                    ),
                    status_code=400,
                ),
            ]
        )

        self.assertRaises(exceptions.SDKException, self.cloud.list_servers)

        self.assert_calls()
