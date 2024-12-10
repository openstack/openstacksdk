# Copyrigh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import mock

from openstack.cloud import meta
from openstack.compute.v2 import server as _server
from openstack import connection
from openstack.tests import fakes
from openstack.tests.unit import base


PRIVATE_V4 = '198.51.100.3'
PUBLIC_V4 = '192.0.2.99'
PUBLIC_V6 = '2001:0db8:face:0da0:face::0b00:1c'  # rfc3849


class FakeConfig:
    def get_region_name(self, service_type=None):
        # TODO(efried): Validate service_type?
        return 'test-region'


class FakeCloud:
    config = FakeConfig()
    name = 'test-name'
    private = False
    force_ipv4 = False
    service_val = True
    _unused = "useless"
    _local_ipv6 = True

    def get_flavor_name(self, id):
        return 'test-flavor-name'

    def get_image_name(self, id):
        return 'test-image-name'

    def get_volumes(self, server):
        return []

    def has_service(self, service_name):
        return self.service_val

    def use_internal_network(self):
        return True

    def use_external_network(self):
        return True

    def get_internal_networks(self):
        return []

    def get_external_networks(self):
        return []

    def get_internal_ipv4_networks(self):
        return []

    def get_external_ipv4_networks(self):
        return []

    def get_internal_ipv6_networks(self):
        return []

    def get_external_ipv6_networks(self):
        return []

    def list_server_security_groups(self, server):
        return []

    def get_default_network(self):
        return None


standard_fake_server = fakes.make_fake_server(
    server_id='test-id-0',
    name='test-id-0',
    status='ACTIVE',
    addresses={
        'private': [
            {'OS-EXT-IPS:type': 'fixed', 'addr': PRIVATE_V4, 'version': 4}
        ],
        'public': [
            {'OS-EXT-IPS:type': 'floating', 'addr': PUBLIC_V4, 'version': 4}
        ],
    },
    flavor={'id': '101'},
    image={'id': '471c2475-da2f-47ac-aba5-cb4aa3d546f5'},
)
standard_fake_server['metadata'] = {'group': 'test-group'}

SUBNETS_WITH_NAT = [
    {
        'name': '',
        'enable_dhcp': True,
        'network_id': '5ef0358f-9403-4f7b-9151-376ca112abf7',
        'tenant_id': '29c79f394b2946f1a0f8446d715dc301',
        'dns_nameservers': [],
        'ipv6_ra_mode': None,
        'allocation_pools': [{'start': '10.10.10.2', 'end': '10.10.10.254'}],
        'gateway_ip': '10.10.10.1',
        'ipv6_address_mode': None,
        'ip_version': 4,
        'host_routes': [],
        'cidr': '10.10.10.0/24',
        'id': '14025a85-436e-4418-b0ee-f5b12a50f9b4',
    },
]

OSIC_NETWORKS = [
    {
        'admin_state_up': True,
        'id': '7004a83a-13d3-4dcd-8cf5-52af1ace4cae',
        'mtu': 0,
        'name': 'GATEWAY_NET',
        'router:external': True,
        'shared': True,
        'status': 'ACTIVE',
        'subnets': ['cf785ee0-6cc9-4712-be3d-0bf6c86cf455'],
        'tenant_id': '7a1ca9f7cc4e4b13ac0ed2957f1e8c32',
    },
    {
        'admin_state_up': True,
        'id': '405abfcc-77dc-49b2-a271-139619ac9b26',
        'mtu': 0,
        'name': 'openstackjenkins-network1',
        'router:external': False,
        'shared': False,
        'status': 'ACTIVE',
        'subnets': ['a47910bc-f649-45db-98ec-e2421c413f4e'],
        'tenant_id': '7e9c4d5842b3451d94417bd0af03a0f4',
    },
    {
        'admin_state_up': True,
        'id': '54753d2c-0a58-4928-9b32-084c59dd20a6',
        'mtu': 0,
        'name': 'GATEWAY_NET_V6',
        'router:external': True,
        'shared': True,
        'status': 'ACTIVE',
        'subnets': [
            '9c21d704-a8b9-409a-b56d-501cb518d380',
            '7cb0ce07-64c3-4a3d-92d3-6f11419b45b9',
        ],
        'tenant_id': '7a1ca9f7cc4e4b13ac0ed2957f1e8c32',
    },
]

OSIC_SUBNETS = [
    {
        'allocation_pools': [
            {'end': '172.99.106.254', 'start': '172.99.106.5'}
        ],
        'cidr': '172.99.106.0/24',
        'dns_nameservers': ['69.20.0.164', '69.20.0.196'],
        'enable_dhcp': True,
        'gateway_ip': '172.99.106.1',
        'host_routes': [],
        'id': 'cf785ee0-6cc9-4712-be3d-0bf6c86cf455',
        'ip_version': 4,
        'ipv6_address_mode': None,
        'ipv6_ra_mode': None,
        'name': 'GATEWAY_NET',
        'network_id': '7004a83a-13d3-4dcd-8cf5-52af1ace4cae',
        'subnetpool_id': None,
        'tenant_id': '7a1ca9f7cc4e4b13ac0ed2957f1e8c32',
    },
    {
        'allocation_pools': [{'end': '10.0.1.254', 'start': '10.0.1.2'}],
        'cidr': '10.0.1.0/24',
        'dns_nameservers': ['8.8.8.8', '8.8.4.4'],
        'enable_dhcp': True,
        'gateway_ip': '10.0.1.1',
        'host_routes': [],
        'id': 'a47910bc-f649-45db-98ec-e2421c413f4e',
        'ip_version': 4,
        'ipv6_address_mode': None,
        'ipv6_ra_mode': None,
        'name': 'openstackjenkins-subnet1',
        'network_id': '405abfcc-77dc-49b2-a271-139619ac9b26',
        'subnetpool_id': None,
        'tenant_id': '7e9c4d5842b3451d94417bd0af03a0f4',
    },
    {
        'allocation_pools': [{'end': '10.255.255.254', 'start': '10.0.0.2'}],
        'cidr': '10.0.0.0/8',
        'dns_nameservers': ['8.8.8.8', '8.8.4.4'],
        'enable_dhcp': True,
        'gateway_ip': '10.0.0.1',
        'host_routes': [],
        'id': '9c21d704-a8b9-409a-b56d-501cb518d380',
        'ip_version': 4,
        'ipv6_address_mode': None,
        'ipv6_ra_mode': None,
        'name': 'GATEWAY_SUBNET_V6V4',
        'network_id': '54753d2c-0a58-4928-9b32-084c59dd20a6',
        'subnetpool_id': None,
        'tenant_id': '7a1ca9f7cc4e4b13ac0ed2957f1e8c32',
    },
    {
        'allocation_pools': [
            {
                'end': '2001:4800:1ae1:18:ffff:ffff:ffff:ffff',
                'start': '2001:4800:1ae1:18::2',
            }
        ],
        'cidr': '2001:4800:1ae1:18::/64',
        'dns_nameservers': ['2001:4860:4860::8888'],
        'enable_dhcp': True,
        'gateway_ip': '2001:4800:1ae1:18::1',
        'host_routes': [],
        'id': '7cb0ce07-64c3-4a3d-92d3-6f11419b45b9',
        'ip_version': 6,
        'ipv6_address_mode': 'dhcpv6-stateless',
        'ipv6_ra_mode': None,
        'name': 'GATEWAY_SUBNET_V6V6',
        'network_id': '54753d2c-0a58-4928-9b32-084c59dd20a6',
        'subnetpool_id': None,
        'tenant_id': '7a1ca9f7cc4e4b13ac0ed2957f1e8c32',
    },
]


class TestMeta(base.TestCase):
    def test_find_nova_addresses_key_name(self):
        # Note 198.51.100.0/24 is TEST-NET-2 from rfc5737
        addrs = {
            'public': [{'addr': '198.51.100.1', 'version': 4}],
            'private': [{'addr': '192.0.2.5', 'version': 4}],
        }
        self.assertEqual(
            ['198.51.100.1'],
            meta.find_nova_addresses(addrs, key_name='public'),
        )
        self.assertEqual([], meta.find_nova_addresses(addrs, key_name='foo'))

    def test_find_nova_addresses_ext_tag(self):
        addrs = {
            'public': [
                {
                    'OS-EXT-IPS:type': 'fixed',
                    'addr': '198.51.100.2',
                    'version': 4,
                }
            ]
        }
        self.assertEqual(
            ['198.51.100.2'], meta.find_nova_addresses(addrs, ext_tag='fixed')
        )
        self.assertEqual([], meta.find_nova_addresses(addrs, ext_tag='foo'))

    def test_find_nova_addresses_key_name_and_ext_tag(self):
        addrs = {
            'public': [
                {
                    'OS-EXT-IPS:type': 'fixed',
                    'addr': '198.51.100.2',
                    'version': 4,
                }
            ]
        }
        self.assertEqual(
            ['198.51.100.2'],
            meta.find_nova_addresses(
                addrs, key_name='public', ext_tag='fixed'
            ),
        )
        self.assertEqual(
            [],
            meta.find_nova_addresses(addrs, key_name='public', ext_tag='foo'),
        )
        self.assertEqual(
            [],
            meta.find_nova_addresses(addrs, key_name='bar', ext_tag='fixed'),
        )

    def test_find_nova_addresses_all(self):
        addrs = {
            'public': [
                {
                    'OS-EXT-IPS:type': 'fixed',
                    'addr': '198.51.100.2',
                    'version': 4,
                }
            ]
        }
        self.assertEqual(
            ['198.51.100.2'],
            meta.find_nova_addresses(
                addrs, key_name='public', ext_tag='fixed', version=4
            ),
        )
        self.assertEqual(
            [],
            meta.find_nova_addresses(
                addrs, key_name='public', ext_tag='fixed', version=6
            ),
        )

    def test_find_nova_addresses_floating_first(self):
        # Note 198.51.100.0/24 is TEST-NET-2 from rfc5737
        addrs = {
            'private': [
                {'addr': '192.0.2.5', 'version': 4, 'OS-EXT-IPS:type': 'fixed'}
            ],
            'public': [
                {
                    'addr': '198.51.100.1',
                    'version': 4,
                    'OS-EXT-IPS:type': 'floating',
                }
            ],
        }
        self.assertEqual(
            ['198.51.100.1', '192.0.2.5'], meta.find_nova_addresses(addrs)
        )

    def test_get_server_ip(self):
        srv = meta.obj_to_munch(standard_fake_server)
        self.assertEqual(PRIVATE_V4, meta.get_server_ip(srv, ext_tag='fixed'))
        self.assertEqual(
            PUBLIC_V4, meta.get_server_ip(srv, ext_tag='floating')
        )

    def test_get_server_private_ip(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [
                            {'id': 'test-net-id', 'name': 'test-net-name'}
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
            ]
        )

        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={
                'private': [
                    {
                        'OS-EXT-IPS:type': 'fixed',
                        'addr': PRIVATE_V4,
                        'version': 4,
                    }
                ],
                'public': [
                    {
                        'OS-EXT-IPS:type': 'floating',
                        'addr': PUBLIC_V4,
                        'version': 4,
                    }
                ],
            },
        )

        self.assertEqual(
            PRIVATE_V4, meta.get_server_private_ip(srv, self.cloud)
        )
        self.assert_calls()

    def test_get_server_multiple_private_ip(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [{'id': 'test-net-id', 'name': 'test-net'}]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
            ]
        )

        shared_mac = '11:22:33:44:55:66'
        distinct_mac = '66:55:44:33:22:11'
        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={
                'test-net': [
                    {
                        'OS-EXT-IPS:type': 'fixed',
                        'OS-EXT-IPS-MAC:mac_addr': distinct_mac,
                        'addr': '10.0.0.100',
                        'version': 4,
                    },
                    {
                        'OS-EXT-IPS:type': 'fixed',
                        'OS-EXT-IPS-MAC:mac_addr': shared_mac,
                        'addr': '10.0.0.101',
                        'version': 4,
                    },
                ],
                'public': [
                    {
                        'OS-EXT-IPS:type': 'floating',
                        'OS-EXT-IPS-MAC:mac_addr': shared_mac,
                        'addr': PUBLIC_V4,
                        'version': 4,
                    }
                ],
            },
        )

        self.assertEqual(
            '10.0.0.101', meta.get_server_private_ip(srv, self.cloud)
        )
        self.assert_calls()

    @mock.patch.object(connection.Connection, 'has_service')
    @mock.patch.object(connection.Connection, 'get_volumes')
    @mock.patch.object(connection.Connection, 'get_image_name')
    @mock.patch.object(connection.Connection, 'get_flavor_name')
    def test_get_server_private_ip_devstack(
        self,
        mock_get_flavor_name,
        mock_get_image_name,
        mock_get_volumes,
        mock_has_service,
    ):
        mock_get_image_name.return_value = 'cirros-0.3.4-x86_64-uec'
        mock_get_flavor_name.return_value = 'm1.tiny'
        mock_get_volumes.return_value = []
        mock_has_service.return_value = True

        fake_server = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            flavor={'id': '1'},
            image={
                'name': 'cirros-0.3.4-x86_64-uec',
                'id': 'f93d000b-7c29-4489-b375-3641a1758fe1',
            },
            addresses={
                'test_pnztt_net': [
                    {
                        'OS-EXT-IPS:type': 'fixed',
                        'addr': PRIVATE_V4,
                        'version': 4,
                        'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:ae:7d:42',
                    }
                ]
            },
        )

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=(
                        'https://network.example.com/v2.0/ports?'
                        'device_id=test-id'
                    ),
                    json={
                        'ports': [
                            {
                                'id': 'test_port_id',
                                'mac_address': 'fa:16:3e:ae:7d:42',
                                'device_id': 'test-id',
                            }
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri=(
                        'https://network.example.com/v2.0/'
                        'floatingips?port_id=test_port_id'
                    ),
                    json={'floatingips': []},
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [
                            {
                                'id': 'test_pnztt_net',
                                'name': 'test_pnztt_net',
                                'router:external': False,
                            },
                            {'id': 'private', 'name': 'private'},
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', fake_server['id']],
                    ),
                    json=fake_server,
                ),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/test-id/os-security-groups',
                    json={'security_groups': []},
                ),
            ]
        )

        srv = self.cloud.get_openstack_vars(_server.Server(**fake_server))

        self.assertEqual(PRIVATE_V4, srv['private_v4'])
        self.assert_calls()

    @mock.patch.object(connection.Connection, 'get_volumes')
    @mock.patch.object(connection.Connection, 'get_image_name')
    @mock.patch.object(connection.Connection, 'get_flavor_name')
    def test_get_server_private_ip_no_fip(
        self, mock_get_flavor_name, mock_get_image_name, mock_get_volumes
    ):
        self.cloud._floating_ip_source = None

        mock_get_image_name.return_value = 'cirros-0.3.4-x86_64-uec'
        mock_get_flavor_name.return_value = 'm1.tiny'
        mock_get_volumes.return_value = []

        fake_server = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            flavor={'id': '1'},
            image={
                'name': 'cirros-0.3.4-x86_64-uec',
                'id': 'f93d000b-7c29-4489-b375-3641a1758fe1',
            },
            addresses={
                'test_pnztt_net': [
                    {
                        'OS-EXT-IPS:type': 'fixed',
                        'addr': PRIVATE_V4,
                        'version': 4,
                        'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:ae:7d:42',
                    }
                ]
            },
        )

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [
                            {
                                'id': 'test_pnztt_net',
                                'name': 'test_pnztt_net',
                                'router:external': False,
                            },
                            {'id': 'private', 'name': 'private'},
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', fake_server['id']],
                    ),
                    json=fake_server,
                ),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/test-id/os-security-groups',
                    json={'security_groups': []},
                ),
            ]
        )

        srv = self.cloud.get_openstack_vars(_server.Server(**fake_server))

        self.assertEqual(PRIVATE_V4, srv['private_v4'])
        self.assert_calls()

    @mock.patch.object(connection.Connection, 'get_volumes')
    @mock.patch.object(connection.Connection, 'get_image_name')
    @mock.patch.object(connection.Connection, 'get_flavor_name')
    def test_get_server_cloud_no_fips(
        self, mock_get_flavor_name, mock_get_image_name, mock_get_volumes
    ):
        self.cloud._floating_ip_source = None
        mock_get_image_name.return_value = 'cirros-0.3.4-x86_64-uec'
        mock_get_flavor_name.return_value = 'm1.tiny'
        mock_get_volumes.return_value = []

        fake_server = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            flavor={'id': '1'},
            image={
                'name': 'cirros-0.3.4-x86_64-uec',
                'id': 'f93d000b-7c29-4489-b375-3641a1758fe1',
            },
            addresses={
                'test_pnztt_net': [
                    {
                        'addr': PRIVATE_V4,
                        'version': 4,
                    }
                ]
            },
        )

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [
                            {
                                'id': 'test_pnztt_net',
                                'name': 'test_pnztt_net',
                                'router:external': False,
                            },
                            {'id': 'private', 'name': 'private'},
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', fake_server['id']],
                    ),
                    json=fake_server,
                ),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/test-id/os-security-groups',
                    json={'security_groups': []},
                ),
            ]
        )

        srv = self.cloud.get_openstack_vars(_server.Server(**fake_server))

        self.assertEqual(PRIVATE_V4, srv['private_v4'])
        self.assert_calls()

    @mock.patch.object(connection.Connection, 'has_service')
    @mock.patch.object(connection.Connection, 'get_volumes')
    @mock.patch.object(connection.Connection, 'get_image_name')
    @mock.patch.object(connection.Connection, 'get_flavor_name')
    def test_get_server_cloud_missing_fips(
        self,
        mock_get_flavor_name,
        mock_get_image_name,
        mock_get_volumes,
        mock_has_service,
    ):
        mock_get_image_name.return_value = 'cirros-0.3.4-x86_64-uec'
        mock_get_flavor_name.return_value = 'm1.tiny'
        mock_get_volumes.return_value = []
        mock_has_service.return_value = True

        fake_server = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            flavor={'id': '1'},
            image={
                'name': 'cirros-0.3.4-x86_64-uec',
                'id': 'f93d000b-7c29-4489-b375-3641a1758fe1',
            },
            addresses={
                'test_pnztt_net': [
                    {
                        'addr': PRIVATE_V4,
                        'version': 4,
                        'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:ae:7d:42',
                    }
                ]
            },
        )

        self.register_uris(
            [
                # self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=(
                        'https://network.example.com/v2.0/ports?'
                        'device_id=test-id'
                    ),
                    json={
                        'ports': [
                            {
                                'id': 'test_port_id',
                                'mac_address': 'fa:16:3e:ae:7d:42',
                                'device_id': 'test-id',
                            }
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri=(
                        'https://network.example.com/v2.0/floatingips'
                        '?port_id=test_port_id'
                    ),
                    json={
                        'floatingips': [
                            {
                                'id': 'floating-ip-id',
                                'port_id': 'test_port_id',
                                'fixed_ip_address': PRIVATE_V4,
                                'floating_ip_address': PUBLIC_V4,
                            }
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [
                            {
                                'id': 'test_pnztt_net',
                                'name': 'test_pnztt_net',
                                'router:external': False,
                            },
                            {
                                'id': 'private',
                                'name': 'private',
                            },
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', fake_server['id']],
                    ),
                    json=fake_server,
                ),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/test-id/os-security-groups',
                    json={'security_groups': []},
                ),
            ]
        )

        srv = self.cloud.get_openstack_vars(_server.Server(**fake_server))

        self.assertEqual(PUBLIC_V4, srv['public_v4'])
        self.assert_calls()

    @mock.patch.object(connection.Connection, 'get_volumes')
    @mock.patch.object(connection.Connection, 'get_image_name')
    @mock.patch.object(connection.Connection, 'get_flavor_name')
    def test_get_server_cloud_rackspace_v6(
        self, mock_get_flavor_name, mock_get_image_name, mock_get_volumes
    ):
        self.cloud.config.config['has_network'] = False
        self.cloud._floating_ip_source = None
        self.cloud.force_ipv4 = False
        self.cloud._local_ipv6 = True
        mock_get_image_name.return_value = 'cirros-0.3.4-x86_64-uec'
        mock_get_flavor_name.return_value = 'm1.tiny'
        mock_get_volumes.return_value = []
        fake_server = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            flavor={'id': '1'},
            image={
                'name': 'cirros-0.3.4-x86_64-uec',
                'id': 'f93d000b-7c29-4489-b375-3641a1758fe1',
            },
            addresses={
                'private': [{'addr': "10.223.160.141", 'version': 4}],
                'public': [
                    {'addr': "104.130.246.91", 'version': 4},
                    {
                        'addr': "2001:4800:7819:103:be76:4eff:fe05:8525",
                        'version': 6,
                    },
                ],
            },
        )

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', fake_server['id']],
                    ),
                    json=fake_server,
                ),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/test-id/os-security-groups',
                    json={'security_groups': []},
                ),
            ]
        )

        srv = self.cloud.get_openstack_vars(_server.Server(**fake_server))

        self.assertEqual("10.223.160.141", srv['private_v4'])
        self.assertEqual("104.130.246.91", srv['public_v4'])
        self.assertEqual(
            "2001:4800:7819:103:be76:4eff:fe05:8525", srv['public_v6']
        )
        self.assertEqual(
            "2001:4800:7819:103:be76:4eff:fe05:8525", srv['interface_ip']
        )
        self.assert_calls()

    @mock.patch.object(connection.Connection, 'get_volumes')
    @mock.patch.object(connection.Connection, 'get_image_name')
    @mock.patch.object(connection.Connection, 'get_flavor_name')
    def test_get_server_cloud_osic_split(
        self, mock_get_flavor_name, mock_get_image_name, mock_get_volumes
    ):
        self.cloud._floating_ip_source = None
        self.cloud.force_ipv4 = False
        self.cloud._local_ipv6 = True
        self.cloud._external_ipv4_names = ['GATEWAY_NET']
        self.cloud._external_ipv6_names = ['GATEWAY_NET_V6']
        self.cloud._internal_ipv4_names = ['GATEWAY_NET_V6']
        self.cloud._internal_ipv6_names = []
        mock_get_image_name.return_value = 'cirros-0.3.4-x86_64-uec'
        mock_get_flavor_name.return_value = 'm1.tiny'
        mock_get_volumes.return_value = []

        fake_server = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            flavor={'id': '1'},
            image={
                'name': 'cirros-0.3.4-x86_64-uec',
                'id': 'f93d000b-7c29-4489-b375-3641a1758fe1',
            },
            addresses={
                'private': [{'addr': "10.223.160.141", 'version': 4}],
                'public': [
                    {'addr': "104.130.246.91", 'version': 4},
                    {
                        'addr': "2001:4800:7819:103:be76:4eff:fe05:8525",
                        'version': 6,
                    },
                ],
            },
        )

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={'networks': OSIC_NETWORKS},
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': OSIC_SUBNETS},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', fake_server['id']],
                    ),
                    json=fake_server,
                ),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/servers/test-id/os-security-groups',
                    json={'security_groups': []},
                ),
            ]
        )

        srv = self.cloud.get_openstack_vars(_server.Server(**fake_server))

        self.assertEqual("10.223.160.141", srv['private_v4'])
        self.assertEqual("104.130.246.91", srv['public_v4'])
        self.assertEqual(
            "2001:4800:7819:103:be76:4eff:fe05:8525", srv['public_v6']
        )
        self.assertEqual(
            "2001:4800:7819:103:be76:4eff:fe05:8525", srv['interface_ip']
        )
        self.assert_calls()

    def test_get_server_external_ipv4_neutron(self):
        # Testing Clouds with Neutron
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [
                            {
                                'id': 'test-net-id',
                                'name': 'test-net',
                                'router:external': True,
                            }
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
            ]
        )
        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={'test-net': [{'addr': PUBLIC_V4, 'version': 4}]},
        )
        ip = meta.get_server_external_ipv4(cloud=self.cloud, server=srv)

        self.assertEqual(PUBLIC_V4, ip)
        self.assert_calls()

    def test_get_server_external_provider_ipv4_neutron(self):
        # Testing Clouds with Neutron
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [
                            {
                                'id': 'test-net-id',
                                'name': 'test-net',
                                'provider:network_type': 'vlan',
                                'provider:physical_network': 'vlan',
                            }
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
            ]
        )

        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={'test-net': [{'addr': PUBLIC_V4, 'version': 4}]},
        )
        ip = meta.get_server_external_ipv4(cloud=self.cloud, server=srv)

        self.assertEqual(PUBLIC_V4, ip)
        self.assert_calls()

    def test_get_server_internal_provider_ipv4_neutron(self):
        # Testing Clouds with Neutron
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [
                            {
                                'id': 'test-net-id',
                                'name': 'test-net',
                                'router:external': False,
                                'provider:network_type': 'vxlan',
                                'provider:physical_network': None,
                            }
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
            ]
        )
        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={'test-net': [{'addr': PRIVATE_V4, 'version': 4}]},
        )
        self.assertIsNone(
            meta.get_server_external_ipv4(cloud=self.cloud, server=srv)
        )
        int_ip = meta.get_server_private_ip(cloud=self.cloud, server=srv)

        self.assertEqual(PRIVATE_V4, int_ip)
        self.assert_calls()

    def test_get_server_external_none_ipv4_neutron(self):
        # Testing Clouds with Neutron
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    json={
                        'networks': [
                            {
                                'id': 'test-net-id',
                                'name': 'test-net',
                                'router:external': False,
                            }
                        ]
                    },
                ),
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/subnets',
                    json={'subnets': SUBNETS_WITH_NAT},
                ),
            ]
        )

        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={'test-net': [{'addr': PUBLIC_V4, 'version': 4}]},
        )
        ip = meta.get_server_external_ipv4(cloud=self.cloud, server=srv)

        self.assertIsNone(ip)
        self.assert_calls()

    def test_get_server_external_ipv4_neutron_accessIPv4(self):
        srv = fakes.make_fake_server(
            server_id='test-id', name='test-name', status='ACTIVE'
        )
        srv['accessIPv4'] = PUBLIC_V4
        ip = meta.get_server_external_ipv4(cloud=self.cloud, server=srv)

        self.assertEqual(PUBLIC_V4, ip)

    def test_get_server_external_ipv4_neutron_accessIPv6(self):
        srv = fakes.make_fake_server(
            server_id='test-id', name='test-name', status='ACTIVE'
        )
        srv['accessIPv6'] = PUBLIC_V6
        ip = meta.get_server_external_ipv6(server=srv)

        self.assertEqual(PUBLIC_V6, ip)

    def test_get_server_external_ipv4_neutron_exception(self):
        # Testing Clouds with a non working Neutron
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://network.example.com/v2.0/networks',
                    status_code=404,
                )
            ]
        )

        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={'public': [{'addr': PUBLIC_V4, 'version': 4}]},
        )
        ip = meta.get_server_external_ipv4(cloud=self.cloud, server=srv)

        self.assertEqual(PUBLIC_V4, ip)
        self.assert_calls()

    def test_get_server_external_ipv4_nova_public(self):
        # Testing Clouds w/o Neutron and a network named public
        self.cloud.config.config['has_network'] = False

        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={'public': [{'addr': PUBLIC_V4, 'version': 4}]},
        )
        ip = meta.get_server_external_ipv4(cloud=self.cloud, server=srv)

        self.assertEqual(PUBLIC_V4, ip)

    def test_get_server_external_ipv4_nova_none(self):
        # Testing Clouds w/o Neutron or a globally routable IP
        self.cloud.config.config['has_network'] = False

        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={'test-net': [{'addr': PRIVATE_V4}]},
        )
        ip = meta.get_server_external_ipv4(cloud=self.cloud, server=srv)

        self.assertIsNone(ip)

    def test_get_server_external_ipv6(self):
        srv = fakes.make_fake_server(
            server_id='test-id',
            name='test-name',
            status='ACTIVE',
            addresses={
                'test-net': [
                    {'addr': PUBLIC_V4, 'version': 4},
                    {'addr': PUBLIC_V6, 'version': 6},
                ]
            },
        )
        ip = meta.get_server_external_ipv6(srv)
        self.assertEqual(PUBLIC_V6, ip)

    def test_get_groups_from_server(self):
        server_vars = {
            'flavor': 'test-flavor',
            'image': 'test-image',
            'az': 'test-az',
        }
        self.assertEqual(
            [
                'test-name',
                'test-region',
                'test-name_test-region',
                'test-group',
                'instance-test-id-0',
                'meta-group_test-group',
                'test-az',
                'test-region_test-az',
                'test-name_test-region_test-az',
            ],
            meta.get_groups_from_server(
                FakeCloud(),
                meta.obj_to_munch(standard_fake_server),
                server_vars,
            ),
        )

    def test_obj_list_to_munch(self):
        """Test conversion of a list of objects to a list of dictonaries"""

        class obj0:
            value = 0

        class obj1:
            value = 1

        list = [obj0, obj1]
        new_list = meta.obj_list_to_munch(list)
        self.assertEqual(new_list[0]['value'], 0)
        self.assertEqual(new_list[1]['value'], 1)

    @mock.patch.object(FakeCloud, 'list_server_security_groups')
    def test_get_security_groups(self, mock_list_server_security_groups):
        '''This test verifies that calling get_hostvars_froms_server
        ultimately calls list_server_security_groups, and that the return
        value from list_server_security_groups ends up in
        server['security_groups'].'''
        mock_list_server_security_groups.return_value = [
            {'name': 'testgroup', 'id': '1'}
        ]

        server = meta.obj_to_munch(standard_fake_server)
        hostvars = meta.get_hostvars_from_server(FakeCloud(), server)

        mock_list_server_security_groups.assert_called_once_with(server)
        self.assertEqual('testgroup', hostvars['security_groups'][0]['name'])

    @mock.patch.object(meta, 'get_server_external_ipv6')
    @mock.patch.object(meta, 'get_server_external_ipv4')
    def test_basic_hostvars(
        self, mock_get_server_external_ipv4, mock_get_server_external_ipv6
    ):
        mock_get_server_external_ipv4.return_value = PUBLIC_V4
        mock_get_server_external_ipv6.return_value = PUBLIC_V6

        hostvars = meta.get_hostvars_from_server(
            FakeCloud(),
            self.cloud._normalize_server(
                meta.obj_to_munch(standard_fake_server)
            ),
        )
        self.assertNotIn('links', hostvars)
        self.assertEqual(PRIVATE_V4, hostvars['private_v4'])
        self.assertEqual(PUBLIC_V4, hostvars['public_v4'])
        self.assertEqual(PUBLIC_V6, hostvars['public_v6'])
        self.assertEqual(PUBLIC_V6, hostvars['interface_ip'])
        self.assertEqual('RegionOne', hostvars['region'])
        self.assertEqual('_test_cloud_', hostvars['cloud'])
        self.assertIn('location', hostvars)
        self.assertEqual('_test_cloud_', hostvars['location']['cloud'])
        self.assertEqual('RegionOne', hostvars['location']['region_name'])
        self.assertEqual(
            fakes.PROJECT_ID, hostvars['location']['project']['id']
        )
        self.assertEqual("test-image-name", hostvars['image']['name'])
        self.assertEqual(
            standard_fake_server['image']['id'], hostvars['image']['id']
        )
        self.assertNotIn('links', hostvars['image'])
        self.assertEqual(
            standard_fake_server['flavor']['id'], hostvars['flavor']['id']
        )
        self.assertEqual("test-flavor-name", hostvars['flavor']['name'])
        self.assertNotIn('links', hostvars['flavor'])
        # test having volumes
        # test volume exception
        self.assertEqual([], hostvars['volumes'])

    @mock.patch.object(meta, 'get_server_external_ipv6')
    @mock.patch.object(meta, 'get_server_external_ipv4')
    def test_ipv4_hostvars(
        self, mock_get_server_external_ipv4, mock_get_server_external_ipv6
    ):
        mock_get_server_external_ipv4.return_value = PUBLIC_V4
        mock_get_server_external_ipv6.return_value = PUBLIC_V6

        fake_cloud = FakeCloud()
        fake_cloud.force_ipv4 = True
        hostvars = meta.get_hostvars_from_server(
            fake_cloud, meta.obj_to_munch(standard_fake_server)
        )
        self.assertEqual(PUBLIC_V4, hostvars['interface_ip'])
        self.assertEqual('', hostvars['public_v6'])

    @mock.patch.object(meta, 'get_server_external_ipv4')
    def test_private_interface_ip(self, mock_get_server_external_ipv4):
        mock_get_server_external_ipv4.return_value = PUBLIC_V4

        cloud = FakeCloud()
        cloud.private = True
        hostvars = meta.get_hostvars_from_server(
            cloud, meta.obj_to_munch(standard_fake_server)
        )
        self.assertEqual(PRIVATE_V4, hostvars['interface_ip'])

    @mock.patch.object(meta, 'get_server_external_ipv4')
    def test_image_string(self, mock_get_server_external_ipv4):
        mock_get_server_external_ipv4.return_value = PUBLIC_V4

        server = standard_fake_server
        server['image'] = 'fake-image-id'
        hostvars = meta.get_hostvars_from_server(
            FakeCloud(), meta.obj_to_munch(server)
        )
        self.assertEqual('fake-image-id', hostvars['image']['id'])

    def test_az(self):
        server = standard_fake_server
        server['OS-EXT-AZ:availability_zone'] = 'az1'

        hostvars = self.cloud._normalize_server(meta.obj_to_munch(server))
        self.assertEqual('az1', hostvars['az'])

    def test_current_location(self):
        self.assertEqual(
            {
                'cloud': '_test_cloud_',
                'project': {
                    'id': mock.ANY,
                    'name': 'admin',
                    'domain_id': None,
                    'domain_name': 'default',
                },
                'region_name': 'RegionOne',
                'zone': None,
            },
            self.cloud.current_location,
        )

    def test_current_project(self):
        self.assertEqual(
            {
                'id': mock.ANY,
                'name': 'admin',
                'domain_id': None,
                'domain_name': 'default',
            },
            self.cloud.current_project,
        )

    def test_has_volume(self):
        mock_cloud = mock.MagicMock()

        fake_volume = fakes.FakeVolume(
            id='volume1',
            status='available',
            name='Volume 1 Display Name',
            attachments=[{'device': '/dev/sda0'}],
        )
        fake_volume_dict = meta.obj_to_munch(fake_volume)
        mock_cloud.get_volumes.return_value = [fake_volume_dict]
        hostvars = meta.get_hostvars_from_server(
            mock_cloud, meta.obj_to_munch(standard_fake_server)
        )
        self.assertEqual('volume1', hostvars['volumes'][0]['id'])
        self.assertEqual('/dev/sda0', hostvars['volumes'][0]['device'])

    def test_has_no_volume_service(self):
        fake_cloud = FakeCloud()
        fake_cloud.service_val = False
        hostvars = meta.get_hostvars_from_server(
            fake_cloud, meta.obj_to_munch(standard_fake_server)
        )
        self.assertEqual([], hostvars['volumes'])

    def test_unknown_volume_exception(self):
        mock_cloud = mock.MagicMock()

        class FakeException(Exception):
            pass

        def side_effect(*args):
            raise FakeException("No Volumes")

        mock_cloud.get_volumes.side_effect = side_effect
        self.assertRaises(
            FakeException,
            meta.get_hostvars_from_server,
            mock_cloud,
            meta.obj_to_munch(standard_fake_server),
        )

    def test_obj_to_munch(self):
        cloud = FakeCloud()
        cloud.subcloud = FakeCloud()
        cloud_dict = meta.obj_to_munch(cloud)
        self.assertEqual(FakeCloud.name, cloud_dict['name'])
        self.assertNotIn('_unused', cloud_dict)
        self.assertNotIn('get_flavor_name', cloud_dict)
        self.assertNotIn('subcloud', cloud_dict)
        self.assertTrue(hasattr(cloud_dict, 'name'))
        self.assertEqual(cloud_dict.name, cloud_dict['name'])

    def test_obj_to_munch_subclass(self):
        class FakeObjDict(dict):
            additional = 1

        obj = FakeObjDict(foo='bar')
        obj_dict = meta.obj_to_munch(obj)
        self.assertIn('additional', obj_dict)
        self.assertIn('foo', obj_dict)
        self.assertEqual(obj_dict['additional'], 1)
        self.assertEqual(obj_dict['foo'], 'bar')
