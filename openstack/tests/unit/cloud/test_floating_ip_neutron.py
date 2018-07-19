# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_floating_ip_neutron
----------------------------------

Tests Floating IP resource methods for Neutron
"""

import copy
import datetime
import munch

from openstack.cloud import exc
from openstack.tests import fakes
from openstack.tests.unit import base


class TestFloatingIP(base.TestCase):
    mock_floating_ip_list_rep = {
        'floatingips': [
            {
                'router_id': 'd23abc8d-2991-4a55-ba98-2aaea84cc72f',
                'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
                'floating_network_id': '376da547-b977-4cfe-9cba-275c80debf57',
                'fixed_ip_address': '10.0.0.4',
                'floating_ip_address': '172.24.4.229',
                'port_id': 'ce705c24-c1ef-408a-bda3-7bbd946164ac',
                'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
                'status': 'ACTIVE'
            },
            {
                'router_id': None,
                'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
                'floating_network_id': '376da547-b977-4cfe-9cba-275c80debf57',
                'fixed_ip_address': None,
                'floating_ip_address': '203.0.113.30',
                'port_id': None,
                'id': '61cea855-49cb-4846-997d-801b70c71bdd',
                'status': 'DOWN'
            }
        ]
    }

    mock_floating_ip_new_rep = {
        'floatingip': {
            'fixed_ip_address': '10.0.0.4',
            'floating_ip_address': '172.24.4.229',
            'floating_network_id': 'my-network-id',
            'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda8',
            'port_id': None,
            'router_id': None,
            'status': 'ACTIVE',
            'tenant_id': '4969c491a3c74ee4af974e6d800c62df'
        }
    }

    mock_floating_ip_port_rep = {
        'floatingip': {
            'fixed_ip_address': '10.0.0.4',
            'floating_ip_address': '172.24.4.229',
            'floating_network_id': 'my-network-id',
            'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda8',
            'port_id': 'ce705c24-c1ef-408a-bda3-7bbd946164ac',
            'router_id': None,
            'status': 'ACTIVE',
            'tenant_id': '4969c491a3c74ee4af974e6d800c62df'
        }
    }

    mock_get_network_rep = {
        'status': 'ACTIVE',
        'subnets': [
            '54d6f61d-db07-451c-9ab3-b9609b6b6f0b'
        ],
        'name': 'my-network',
        'provider:physical_network': None,
        'admin_state_up': True,
        'tenant_id': '4fd44f30292945e481c7b8a0c8908869',
        'provider:network_type': 'local',
        'router:external': True,
        'shared': True,
        'id': 'my-network-id',
        'provider:segmentation_id': None
    }

    mock_search_ports_rep = [
        {
            'status': 'ACTIVE',
            'binding:host_id': 'devstack',
            'name': 'first-port',
            'created_at': datetime.datetime.now().isoformat(),
            'allowed_address_pairs': [],
            'admin_state_up': True,
            'network_id': '70c1db1f-b701-45bd-96e0-a313ee3430b3',
            'tenant_id': '',
            'extra_dhcp_opts': [],
            'binding:vif_details': {
                'port_filter': True,
                'ovs_hybrid_plug': True
            },
            'binding:vif_type': 'ovs',
            'device_owner': 'compute:None',
            'mac_address': 'fa:16:3e:58:42:ed',
            'binding:profile': {},
            'binding:vnic_type': 'normal',
            'fixed_ips': [
                {
                    'subnet_id': '008ba151-0b8c-4a67-98b5-0d2b87666062',
                    'ip_address': u'172.24.4.2'
                }
            ],
            'id': 'ce705c24-c1ef-408a-bda3-7bbd946164ac',
            'security_groups': [],
            'device_id': 'server-id'
        }
    ]

    def assertAreInstances(self, elements, elem_type):
        for e in elements:
            self.assertIsInstance(e, elem_type)

    def setUp(self):
        super(TestFloatingIP, self).setUp()

        self.fake_server = fakes.make_fake_server(
            'server-id', '', 'ACTIVE',
            addresses={u'test_pnztt_net': [{
                u'OS-EXT-IPS:type': u'fixed',
                u'addr': '192.0.2.129',
                u'version': 4,
                u'OS-EXT-IPS-MAC:mac_addr':
                u'fa:16:3e:ae:7d:42'}]})
        self.floating_ip = self.cloud._normalize_floating_ips(
            self.mock_floating_ip_list_rep['floatingips'])[0]

    def test_float_no_status(self):
        floating_ips = [
            {
                'fixed_ip_address': '10.0.0.4',
                'floating_ip_address': '172.24.4.229',
                'floating_network_id': 'my-network-id',
                'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda8',
                'port_id': None,
                'router_id': None,
                'tenant_id': '4969c491a3c74ee4af974e6d800c62df'
            }
        ]
        normalized = self.cloud._normalize_floating_ips(floating_ips)
        self.assertEqual('UNKNOWN', normalized[0]['status'])

    def test_list_floating_ips(self):
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/floatingips.json',
                 json=self.mock_floating_ip_list_rep)])

        floating_ips = self.cloud.list_floating_ips()

        self.assertIsInstance(floating_ips, list)
        self.assertAreInstances(floating_ips, dict)
        self.assertEqual(2, len(floating_ips))

        self.assert_calls()

    def test_list_floating_ips_with_filters(self):

        self.register_uris([
            dict(method='GET',
                 uri=('https://network.example.com/v2.0/floatingips.json?'
                      'Foo=42'),
                 json={'floatingips': []})])

        self.cloud.list_floating_ips(filters={'Foo': 42})

        self.assert_calls()

    def test_search_floating_ips(self):
        self.register_uris([
            dict(method='GET',
                 uri=('https://network.example.com/v2.0/floatingips.json'),
                 json=self.mock_floating_ip_list_rep)])

        floating_ips = self.cloud.search_floating_ips(
            filters={'attached': False})

        self.assertIsInstance(floating_ips, list)
        self.assertAreInstances(floating_ips, dict)
        self.assertEqual(1, len(floating_ips))
        self.assert_calls()

    def test_get_floating_ip(self):
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/floatingips.json',
                 json=self.mock_floating_ip_list_rep)])

        floating_ip = self.cloud.get_floating_ip(
            id='2f245a7b-796b-4f26-9cf9-9e82d248fda7')

        self.assertIsInstance(floating_ip, dict)
        self.assertEqual('172.24.4.229', floating_ip['floating_ip_address'])
        self.assertEqual(
            self.mock_floating_ip_list_rep['floatingips'][0]['tenant_id'],
            floating_ip['project_id']
        )
        self.assertEqual(
            self.mock_floating_ip_list_rep['floatingips'][0]['tenant_id'],
            floating_ip['tenant_id']
        )
        self.assertIn('location', floating_ip)
        self.assert_calls()

    def test_get_floating_ip_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/floatingips.json',
                 json=self.mock_floating_ip_list_rep)])

        floating_ip = self.cloud.get_floating_ip(id='non-existent')

        self.assertIsNone(floating_ip)
        self.assert_calls()

    def test_get_floating_ip_by_id(self):
        fid = self.mock_floating_ip_new_rep['floatingip']['id']
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/floatingips/'
                     '{id}'.format(id=fid),
                 json=self.mock_floating_ip_new_rep)])

        floating_ip = self.cloud.get_floating_ip_by_id(id=fid)

        self.assertIsInstance(floating_ip, dict)
        self.assertEqual('172.24.4.229', floating_ip['floating_ip_address'])
        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['tenant_id'],
            floating_ip['project_id']
        )
        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['tenant_id'],
            floating_ip['tenant_id']
        )
        self.assertIn('location', floating_ip)
        self.assert_calls()

    def test_create_floating_ip(self):
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/networks.json',
                 json={'networks': [self.mock_get_network_rep]}),
            dict(method='POST',
                 uri='https://network.example.com/v2.0/floatingips.json',
                 json=self.mock_floating_ip_new_rep,
                 validate=dict(
                     json={'floatingip': {
                         'floating_network_id': 'my-network-id'}}))
        ])
        ip = self.cloud.create_floating_ip(network='my-network')

        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['floating_ip_address'],
            ip['floating_ip_address'])
        self.assert_calls()

    def test_create_floating_ip_port_bad_response(self):
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/networks.json',
                 json={'networks': [self.mock_get_network_rep]}),
            dict(method='POST',
                 uri='https://network.example.com/v2.0/floatingips.json',
                 json=self.mock_floating_ip_new_rep,
                 validate=dict(
                     json={'floatingip': {
                         'floating_network_id': 'my-network-id',
                         'port_id': u'ce705c24-c1ef-408a-bda3-7bbd946164ab'}}))
        ])

        # Fails because we requested a port and the returned FIP has no port
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_floating_ip,
            network='my-network', port='ce705c24-c1ef-408a-bda3-7bbd946164ab')
        self.assert_calls()

    def test_create_floating_ip_port(self):
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/networks.json',
                 json={'networks': [self.mock_get_network_rep]}),
            dict(method='POST',
                 uri='https://network.example.com/v2.0/floatingips.json',
                 json=self.mock_floating_ip_port_rep,
                 validate=dict(
                     json={'floatingip': {
                         'floating_network_id': 'my-network-id',
                         'port_id': u'ce705c24-c1ef-408a-bda3-7bbd946164ac'}}))
        ])

        ip = self.cloud.create_floating_ip(
            network='my-network', port='ce705c24-c1ef-408a-bda3-7bbd946164ac')

        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['floating_ip_address'],
            ip['floating_ip_address'])
        self.assert_calls()

    def test_neutron_available_floating_ips(self):
        """
        Test without specifying a network name.
        """
        fips_mock_uri = 'https://network.example.com/v2.0/floatingips.json'
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/networks.json',
                 json={'networks': [self.mock_get_network_rep]}),
            dict(method='GET',
                 uri='https://network.example.com/v2.0/subnets.json',
                 json={'subnets': []}),
            dict(method='GET', uri=fips_mock_uri, json={'floatingips': []}),
            dict(method='POST', uri=fips_mock_uri,
                 json=self.mock_floating_ip_new_rep,
                 validate=dict(json={
                     'floatingip': {
                         'floating_network_id': self.mock_get_network_rep['id']
                     }}))
        ])

        # Test if first network is selected if no network is given
        self.cloud._neutron_available_floating_ips()
        self.assert_calls()

    def test_neutron_available_floating_ips_network(self):
        """
        Test with specifying a network name.
        """
        fips_mock_uri = 'https://network.example.com/v2.0/floatingips.json'
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/networks.json',
                 json={'networks': [self.mock_get_network_rep]}),
            dict(method='GET',
                 uri='https://network.example.com/v2.0/subnets.json',
                 json={'subnets': []}),
            dict(method='GET', uri=fips_mock_uri, json={'floatingips': []}),
            dict(method='POST', uri=fips_mock_uri,
                 json=self.mock_floating_ip_new_rep,
                 validate=dict(json={
                     'floatingip': {
                         'floating_network_id': self.mock_get_network_rep['id']
                     }}))
        ])

        # Test if first network is selected if no network is given
        self.cloud._neutron_available_floating_ips(
            network=self.mock_get_network_rep['name']
        )
        self.assert_calls()

    def test_neutron_available_floating_ips_invalid_network(self):
        """
        Test with an invalid network name.
        """
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/networks.json',
                 json={'networks': [self.mock_get_network_rep]}),
            dict(method='GET',
                 uri='https://network.example.com/v2.0/subnets.json',
                 json={'subnets': []})
        ])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud._neutron_available_floating_ips,
            network='INVALID')

        self.assert_calls()

    def test_auto_ip_pool_no_reuse(self):
        # payloads taken from citycloud
        self.register_uris([
            dict(method='GET',
                 uri='https://network.example.com/v2.0/networks.json',
                 json={"networks": [{
                     "status": "ACTIVE",
                     "subnets": [
                         "df3e17fa-a4b2-47ae-9015-bc93eb076ba2",
                         "6b0c3dc9-b0b8-4d87-976a-7f2ebf13e7ec",
                         "fc541f48-fc7f-48c0-a063-18de6ee7bdd7"],
                     "availability_zone_hints": [],
                     "availability_zones": ["nova"],
                     "name": "ext-net",
                     "admin_state_up": True,
                     "tenant_id": "a564613210ee43708b8a7fc6274ebd63",
                     "tags": [],
                     "ipv6_address_scope": "9f03124f-89af-483a-b6fd-10f08079db4d",  # noqa
                     "mtu": 0,
                     "is_default": False,
                     "router:external": True,
                     "ipv4_address_scope": None,
                     "shared": False,
                     "id": "0232c17f-2096-49bc-b205-d3dcd9a30ebf",
                     "description": None
                 }, {
                     "status": "ACTIVE",
                     "subnets": ["f0ad1df5-53ee-473f-b86b-3604ea5591e9"],
                     "availability_zone_hints": [],
                     "availability_zones": ["nova"],
                     "name": "private",
                     "admin_state_up": True,
                     "tenant_id": "65222a4d09ea4c68934fa1028c77f394",
                     "created_at": "2016-10-22T13:46:26",
                     "tags": [],
                     "updated_at": "2016-10-22T13:46:26",
                     "ipv6_address_scope": None,
                     "router:external": False,
                     "ipv4_address_scope": None,
                     "shared": False,
                     "mtu": 1450,
                     "id": "2c9adcb5-c123-4c5a-a2ba-1ad4c4e1481f",
                     "description": ""
                 }]}),
            dict(method='GET',
                 uri='https://network.example.com/v2.0/ports.json'
                     '?device_id=f80e3ad0-e13e-41d4-8e9c-be79bccdb8f7',
                 json={"ports": [{
                     "status": "ACTIVE",
                     "created_at": "2017-02-06T20:59:45",
                     "description": "",
                     "allowed_address_pairs": [],
                     "admin_state_up": True,
                     "network_id": "2c9adcb5-c123-4c5a-a2ba-1ad4c4e1481f",
                     "dns_name": None,
                     "extra_dhcp_opts": [],
                     "mac_address": "fa:16:3e:e8:7f:03",
                     "updated_at": "2017-02-06T20:59:49",
                     "name": "",
                     "device_owner": "compute:None",
                     "tenant_id": "65222a4d09ea4c68934fa1028c77f394",
                     "binding:vnic_type": "normal",
                     "fixed_ips": [{
                         "subnet_id": "f0ad1df5-53ee-473f-b86b-3604ea5591e9",
                         "ip_address": "10.4.0.16"}],
                     "id": "a767944e-057a-47d1-a669-824a21b8fb7b",
                     "security_groups": [
                         "9fb5ba44-5c46-4357-8e60-8b55526cab54"],
                     "device_id": "f80e3ad0-e13e-41d4-8e9c-be79bccdb8f7",
                 }]}),

            dict(method='POST',
                 uri='https://network.example.com/v2.0/floatingips.json',
                 json={"floatingip": {
                     "router_id": "9de9c787-8f89-4a53-8468-a5533d6d7fd1",
                     "status": "DOWN",
                     "description": "",
                     "dns_domain": "",
                     "floating_network_id": "0232c17f-2096-49bc-b205-d3dcd9a30ebf",  # noqa
                     "fixed_ip_address": "10.4.0.16",
                     "floating_ip_address": "89.40.216.153",
                     "port_id": "a767944e-057a-47d1-a669-824a21b8fb7b",
                     "id": "e69179dc-a904-4c9a-a4c9-891e2ecb984c",
                     "dns_name": "",
                     "tenant_id": "65222a4d09ea4c68934fa1028c77f394"
                 }},
                 validate=dict(json={"floatingip": {
                     "floating_network_id": "0232c17f-2096-49bc-b205-d3dcd9a30ebf",  # noqa
                     "fixed_ip_address": "10.4.0.16",
                     "port_id": "a767944e-057a-47d1-a669-824a21b8fb7b",
                 }})),
            dict(method='GET',
                 uri='{endpoint}/servers/detail'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT),
                 json={"servers": [{
                     "status": "ACTIVE",
                     "updated": "2017-02-06T20:59:49Z",
                     "addresses": {
                         "private": [{
                             "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:e8:7f:03",
                             "version": 4,
                             "addr": "10.4.0.16",
                             "OS-EXT-IPS:type": "fixed"
                         }, {
                             "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:e8:7f:03",
                             "version": 4,
                             "addr": "89.40.216.153",
                             "OS-EXT-IPS:type": "floating"
                         }]},
                     "key_name": None,
                     "image": {"id": "95e4c449-8abf-486e-97d9-dc3f82417d2d"},
                     "OS-EXT-STS:task_state": None,
                     "OS-EXT-STS:vm_state": "active",
                     "OS-SRV-USG:launched_at": "2017-02-06T20:59:48.000000",
                     "flavor": {"id": "2186bd79-a05e-4953-9dde-ddefb63c88d4"},
                     "id": "f80e3ad0-e13e-41d4-8e9c-be79bccdb8f7",
                     "security_groups": [{"name": "default"}],
                     "OS-SRV-USG:terminated_at": None,
                     "OS-EXT-AZ:availability_zone": "nova",
                     "user_id": "c17534835f8f42bf98fc367e0bf35e09",
                     "name": "testmt",
                     "created": "2017-02-06T20:59:44Z",
                     "tenant_id": "65222a4d09ea4c68934fa1028c77f394",
                     "OS-DCF:diskConfig": "MANUAL",
                     "os-extended-volumes:volumes_attached": [],
                     "accessIPv4": "",
                     "accessIPv6": "",
                     "progress": 0,
                     "OS-EXT-STS:power_state": 1,
                     "config_drive": "",
                     "metadata": {}
                 }]}),
            dict(method='GET',
                 uri='https://network.example.com/v2.0/networks.json',
                 json={"networks": [{
                     "status": "ACTIVE",
                     "subnets": [
                         "df3e17fa-a4b2-47ae-9015-bc93eb076ba2",
                         "6b0c3dc9-b0b8-4d87-976a-7f2ebf13e7ec",
                         "fc541f48-fc7f-48c0-a063-18de6ee7bdd7"],
                     "availability_zone_hints": [],
                     "availability_zones": ["nova"],
                     "name": "ext-net",
                     "admin_state_up": True,
                     "tenant_id": "a564613210ee43708b8a7fc6274ebd63",
                     "tags": [],
                     "ipv6_address_scope": "9f03124f-89af-483a-b6fd-10f08079db4d",  # noqa
                     "mtu": 0,
                     "is_default": False,
                     "router:external": True,
                     "ipv4_address_scope": None,
                     "shared": False,
                     "id": "0232c17f-2096-49bc-b205-d3dcd9a30ebf",
                     "description": None
                 }, {
                     "status": "ACTIVE",
                     "subnets": ["f0ad1df5-53ee-473f-b86b-3604ea5591e9"],
                     "availability_zone_hints": [],
                     "availability_zones": ["nova"],
                     "name": "private",
                     "admin_state_up": True,
                     "tenant_id": "65222a4d09ea4c68934fa1028c77f394",
                     "created_at": "2016-10-22T13:46:26",
                     "tags": [],
                     "updated_at": "2016-10-22T13:46:26",
                     "ipv6_address_scope": None,
                     "router:external": False,
                     "ipv4_address_scope": None,
                     "shared": False,
                     "mtu": 1450,
                     "id": "2c9adcb5-c123-4c5a-a2ba-1ad4c4e1481f",
                     "description": ""
                 }]}),
            dict(method='GET',
                 uri='https://network.example.com/v2.0/subnets.json',
                 json={"subnets": [{
                     "description": "",
                     "enable_dhcp": True,
                     "network_id": "2c9adcb5-c123-4c5a-a2ba-1ad4c4e1481f",
                     "tenant_id": "65222a4d09ea4c68934fa1028c77f394",
                     "created_at": "2016-10-22T13:46:26",
                     "dns_nameservers": [
                         "89.36.90.101",
                         "89.36.90.102"],
                     "updated_at": "2016-10-22T13:46:26",
                     "gateway_ip": "10.4.0.1",
                     "ipv6_ra_mode": None,
                     "allocation_pools": [{
                         "start": "10.4.0.2",
                         "end": "10.4.0.200"}],
                     "host_routes": [],
                     "ip_version": 4,
                     "ipv6_address_mode": None,
                     "cidr": "10.4.0.0/24",
                     "id": "f0ad1df5-53ee-473f-b86b-3604ea5591e9",
                     "subnetpool_id": None,
                     "name": "private-subnet-ipv4",
                 }]})])

        self.cloud.add_ips_to_server(
            munch.Munch(
                id='f80e3ad0-e13e-41d4-8e9c-be79bccdb8f7',
                addresses={
                    "private": [{
                        "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:e8:7f:03",
                        "version": 4,
                        "addr": "10.4.0.16",
                        "OS-EXT-IPS:type": "fixed"
                    }]}),
            ip_pool='ext-net', reuse=False)

        self.assert_calls()

    def test_available_floating_ip_new(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_get_network_rep]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': []}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': []}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 validate=dict(
                     json={'floatingip': {
                         'floating_network_id': 'my-network-id'}}),
                 json=self.mock_floating_ip_new_rep)
        ])

        ip = self.cloud.available_floating_ip(network='my-network')

        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['floating_ip_address'],
            ip['floating_ip_address'])
        self.assert_calls()

    def test_delete_floating_ip_existing(self):
        fip_id = '2f245a7b-796b-4f26-9cf9-9e82d248fda7'
        fake_fip = {
            'id': fip_id,
            'floating_ip_address': '172.99.106.167',
            'status': 'ACTIVE',
        }
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(fip_id)]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [fake_fip]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(fip_id)]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [fake_fip]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(fip_id)]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': []}),
        ])

        self.assertTrue(
            self.cloud.delete_floating_ip(floating_ip_id=fip_id, retry=2))
        self.assert_calls()

    def test_delete_floating_ip_existing_down(self):
        fip_id = '2f245a7b-796b-4f26-9cf9-9e82d248fda7'
        fake_fip = {
            'id': fip_id,
            'floating_ip_address': '172.99.106.167',
            'status': 'ACTIVE',
        }
        down_fip = {
            'id': fip_id,
            'floating_ip_address': '172.99.106.167',
            'status': 'DOWN',
        }
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(fip_id)]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [fake_fip]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(fip_id)]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [down_fip]}),
        ])

        self.assertTrue(
            self.cloud.delete_floating_ip(floating_ip_id=fip_id, retry=2))
        self.assert_calls()

    def test_delete_floating_ip_existing_no_delete(self):
        fip_id = '2f245a7b-796b-4f26-9cf9-9e82d248fda7'
        fake_fip = {
            'id': fip_id,
            'floating_ip_address': '172.99.106.167',
            'status': 'ACTIVE',
        }
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(fip_id)]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [fake_fip]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(fip_id)]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [fake_fip]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(fip_id)]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [fake_fip]}),
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.delete_floating_ip,
            floating_ip_id=fip_id, retry=2)
        self.assert_calls()

    def test_delete_floating_ip_not_found(self):
        self.register_uris([
            dict(method='DELETE',
                 uri=('https://network.example.com/v2.0/floatingips/'
                      'a-wild-id-appears.json'),
                 status_code=404)])

        ret = self.cloud.delete_floating_ip(
            floating_ip_id='a-wild-id-appears')

        self.assertFalse(ret)
        self.assert_calls()

    def test_attach_ip_to_server(self):
        fip = self.mock_floating_ip_list_rep['floatingips'][0]
        device_id = self.fake_server['id']

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json'],
                     qs_elements=["device_id={0}".format(device_id)]),
                 json={'ports': self.mock_search_ports_rep}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(
                         fip['id'])]),
                 json={'floatingip': fip},
                 validate=dict(
                     json={'floatingip': {
                         'port_id': self.mock_search_ports_rep[0]['id'],
                         'fixed_ip_address': self.mock_search_ports_rep[0][
                             'fixed_ips'][0]['ip_address']}})),
        ])

        self.cloud._attach_ip_to_server(
            server=self.fake_server,
            floating_ip=self.floating_ip)
        self.assert_calls()

    def test_add_ip_refresh_timeout(self):
        device_id = self.fake_server['id']

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_get_network_rep]}),
            dict(method='GET',
                 uri='https://network.example.com/v2.0/subnets.json',
                 json={'subnets': []}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json'],
                     qs_elements=["device_id={0}".format(device_id)]),
                 json={'ports': self.mock_search_ports_rep}),
            dict(method='POST',
                 uri='https://network.example.com/v2.0/floatingips.json',
                 json={'floatingip': self.floating_ip},
                 validate=dict(
                     json={'floatingip': {
                         'floating_network_id': 'my-network-id',
                         'fixed_ip_address': self.mock_search_ports_rep[0][
                             'fixed_ips'][0]['ip_address'],
                         'port_id': self.mock_search_ports_rep[0]['id']}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [self.floating_ip]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(
                         self.floating_ip['id'])]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': []}),
        ])

        self.assertRaises(
            exc.OpenStackCloudTimeout,
            self.cloud._add_auto_ip,
            server=self.fake_server,
            wait=True, timeout=0.01,
            reuse=False)
        self.assert_calls()

    def test_detach_ip_from_server(self):
        fip = self.mock_floating_ip_new_rep['floatingip']
        attached_fip = copy.copy(fip)
        attached_fip['port_id'] = 'server-port-id'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [attached_fip]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(
                         fip['id'])]),
                 json={'floatingip': fip},
                 validate=dict(
                     json={'floatingip': {'port_id': None}}))
        ])
        self.cloud.detach_ip_from_server(
            server_id='server-id',
            floating_ip_id=fip['id'])
        self.assert_calls()

    def test_add_ip_from_pool(self):
        network = self.mock_get_network_rep
        fip = self.mock_floating_ip_new_rep['floatingip']
        fixed_ip = self.mock_search_ports_rep[0]['fixed_ips'][0]['ip_address']
        port_id = self.mock_search_ports_rep[0]['id']
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [network]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': []}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [fip]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingip': fip},
                 validate=dict(
                     json={'floatingip': {
                         'floating_network_id': network['id']}})),
            dict(method="GET",
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json'],
                     qs_elements=[
                        "device_id={0}".format(self.fake_server['id'])]),
                 json={'ports': self.mock_search_ports_rep}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(
                         fip['id'])]),
                 json={'floatingip': fip},
                 validate=dict(
                     json={'floatingip': {
                         'fixed_ip_address': fixed_ip,
                         'port_id': port_id}})),
        ])

        server = self.cloud._add_ip_from_pool(
            server=self.fake_server,
            network=network['id'],
            fixed_address=fixed_ip)

        self.assertEqual(server, self.fake_server)
        self.assert_calls()

    def test_cleanup_floating_ips(self):
        floating_ips = [{
            "id": "this-is-a-floating-ip-id",
            "fixed_ip_address": None,
            "internal_network": None,
            "floating_ip_address": "203.0.113.29",
            "network": "this-is-a-net-or-pool-id",
            "port_id": None,
            "status": "ACTIVE"
        }, {
            "id": "this-is-an-attached-floating-ip-id",
            "fixed_ip_address": None,
            "internal_network": None,
            "floating_ip_address": "203.0.113.29",
            "network": "this-is-a-net-or-pool-id",
            "attached": True,
            "port_id": "this-is-id-of-port-with-fip",
            "status": "ACTIVE"
        }]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': floating_ips}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips/{0}.json'.format(
                         floating_ips[0]['id'])]),
                 json={}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingips': [floating_ips[1]]}),
        ])
        self.cloud.delete_unattached_floating_ips()
        self.assert_calls()

    def test_create_floating_ip_no_port(self):
        server_port = {
            "id": "port-id",
            "device_id": "some-server",
            'created_at': datetime.datetime.now().isoformat(),
            'fixed_ips': [
                {
                    'subnet_id': 'subnet-id',
                    'ip_address': '172.24.4.2'
                }
            ],
        }
        floating_ip = {
            "id": "floating-ip-id",
            "port_id": None
        }
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_get_network_rep]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': []}),
            dict(method="GET",
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json'],
                     qs_elements=['device_id=some-server']),
                 json={'ports': [server_port]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 json={'floatingip': floating_ip})
        ])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud._neutron_create_floating_ip,
            server=dict(id='some-server'))
        self.assert_calls()
