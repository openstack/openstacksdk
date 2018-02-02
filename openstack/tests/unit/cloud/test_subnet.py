# Copyright 2017 OVH SAS
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
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

import copy
import testtools

from openstack.cloud import exc
from openstack.tests.unit import base


class TestSubnet(base.TestCase):

    network_name = 'network_name'
    subnet_name = 'subnet_name'
    subnet_id = '1f1696eb-7f47-47f6-835c-4889bff88604'
    subnet_cidr = '192.168.199.0/24'

    mock_network_rep = {
        'id': '881d1bb7-a663-44c0-8f9f-ee2765b74486',
        'name': network_name,
    }

    mock_subnet_rep = {
        'allocation_pools': [{
            'start': u'192.168.199.2',
            'end': u'192.168.199.254'
        }],
        'cidr': subnet_cidr,
        'created_at': '2017-04-24T20:22:23Z',
        'description': '',
        'dns_nameservers': [],
        'enable_dhcp': False,
        'gateway_ip': '192.168.199.1',
        'host_routes': [],
        'id': subnet_id,
        'ip_version': 4,
        'ipv6_address_mode': None,
        'ipv6_ra_mode': None,
        'name': subnet_name,
        'network_id': mock_network_rep['id'],
        'project_id': '861808a93da0484ea1767967c4df8a23',
        'revision_number': 2,
        'service_types': [],
        'subnetpool_id': None,
        'tags': []
    }

    def test_get_subnet(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': [self.mock_subnet_rep]})
        ])
        r = self.cloud.get_subnet(self.subnet_name)
        self.assertIsNotNone(r)
        self.assertDictEqual(self.mock_subnet_rep, r)
        self.assert_calls()

    def test_get_subnet_by_id(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0',
                                                  'subnets',
                                                  self.subnet_id]),
                 json={'subnet': self.mock_subnet_rep})
        ])
        r = self.cloud.get_subnet_by_id(self.subnet_id)
        self.assertIsNotNone(r)
        self.assertDictEqual(self.mock_subnet_rep, r)
        self.assert_calls()

    def test_create_subnet(self):
        pool = [{'start': '192.168.199.2', 'end': '192.168.199.254'}]
        dns = ['8.8.8.8']
        routes = [{"destination": "0.0.0.0/0", "nexthop": "123.456.78.9"}]
        mock_subnet_rep = copy.copy(self.mock_subnet_rep)
        mock_subnet_rep['allocation_pools'] = pool
        mock_subnet_rep['dns_nameservers'] = dns
        mock_subnet_rep['host_routes'] = routes
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_network_rep]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnet': mock_subnet_rep},
                 validate=dict(
                     json={'subnet': {
                         'cidr': self.subnet_cidr,
                         'enable_dhcp': False,
                         'ip_version': 4,
                         'network_id': self.mock_network_rep['id'],
                         'allocation_pools': pool,
                         'dns_nameservers': dns,
                         'host_routes': routes}}))
        ])
        subnet = self.cloud.create_subnet(self.network_name, self.subnet_cidr,
                                          allocation_pools=pool,
                                          dns_nameservers=dns,
                                          host_routes=routes)
        self.assertDictEqual(mock_subnet_rep, subnet)
        self.assert_calls()

    def test_create_subnet_string_ip_version(self):
        '''Allow ip_version as a string'''
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_network_rep]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnet': self.mock_subnet_rep},
                 validate=dict(
                     json={'subnet': {
                         'cidr': self.subnet_cidr,
                         'enable_dhcp': False,
                         'ip_version': 4,
                         'network_id': self.mock_network_rep['id']}}))
        ])
        subnet = self.cloud.create_subnet(
            self.network_name, self.subnet_cidr, ip_version='4')
        self.assertDictEqual(self.mock_subnet_rep, subnet)
        self.assert_calls()

    def test_create_subnet_bad_ip_version(self):
        '''String ip_versions must be convertable to int'''
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_network_rep]})
        ])
        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "ip_version must be an integer"
        ):
            self.cloud.create_subnet(
                self.network_name, self.subnet_cidr, ip_version='4x')
        self.assert_calls()

    def test_create_subnet_without_gateway_ip(self):
        pool = [{'start': '192.168.199.2', 'end': '192.168.199.254'}]
        dns = ['8.8.8.8']
        mock_subnet_rep = copy.copy(self.mock_subnet_rep)
        mock_subnet_rep['allocation_pools'] = pool
        mock_subnet_rep['dns_nameservers'] = dns
        mock_subnet_rep['gateway_ip'] = None
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_network_rep]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnet': mock_subnet_rep},
                 validate=dict(
                     json={'subnet': {
                         'cidr': self.subnet_cidr,
                         'enable_dhcp': False,
                         'ip_version': 4,
                         'network_id': self.mock_network_rep['id'],
                         'allocation_pools': pool,
                         'gateway_ip': None,
                         'dns_nameservers': dns}}))
        ])
        subnet = self.cloud.create_subnet(self.network_name, self.subnet_cidr,
                                          allocation_pools=pool,
                                          dns_nameservers=dns,
                                          disable_gateway_ip=True)
        self.assertDictEqual(mock_subnet_rep, subnet)
        self.assert_calls()

    def test_create_subnet_with_gateway_ip(self):
        pool = [{'start': '192.168.199.8', 'end': '192.168.199.254'}]
        gateway = '192.168.199.2'
        dns = ['8.8.8.8']
        mock_subnet_rep = copy.copy(self.mock_subnet_rep)
        mock_subnet_rep['allocation_pools'] = pool
        mock_subnet_rep['dns_nameservers'] = dns
        mock_subnet_rep['gateway_ip'] = gateway
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_network_rep]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnet': mock_subnet_rep},
                 validate=dict(
                     json={'subnet': {
                         'cidr': self.subnet_cidr,
                         'enable_dhcp': False,
                         'ip_version': 4,
                         'network_id': self.mock_network_rep['id'],
                         'allocation_pools': pool,
                         'gateway_ip': gateway,
                         'dns_nameservers': dns}}))
        ])
        subnet = self.cloud.create_subnet(self.network_name, self.subnet_cidr,
                                          allocation_pools=pool,
                                          dns_nameservers=dns,
                                          gateway_ip=gateway)
        self.assertDictEqual(mock_subnet_rep, subnet)
        self.assert_calls()

    def test_create_subnet_conflict_gw_ops(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_network_rep]})
        ])
        gateway = '192.168.200.3'
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.create_subnet, 'kooky',
                          self.subnet_cidr, gateway_ip=gateway,
                          disable_gateway_ip=True)
        self.assert_calls()

    def test_create_subnet_bad_network(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [self.mock_network_rep]})
        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.create_subnet,
                          'duck', self.subnet_cidr)
        self.assert_calls()

    def test_create_subnet_non_unique_network(self):
        net1 = dict(id='123', name=self.network_name)
        net2 = dict(id='456', name=self.network_name)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [net1, net2]})
        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.create_subnet,
                          self.network_name, self.subnet_cidr)
        self.assert_calls()

    def test_delete_subnet(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': [self.mock_subnet_rep]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'subnets', '%s.json' % self.subnet_id]),
                 json={})
        ])
        self.assertTrue(self.cloud.delete_subnet(self.subnet_name))
        self.assert_calls()

    def test_delete_subnet_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': []})
        ])
        self.assertFalse(self.cloud.delete_subnet('goofy'))
        self.assert_calls()

    def test_delete_subnet_multiple_found(self):
        subnet1 = dict(id='123', name=self.subnet_name)
        subnet2 = dict(id='456', name=self.subnet_name)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': [subnet1, subnet2]})
        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.delete_subnet,
                          self.subnet_name)
        self.assert_calls()

    def test_delete_subnet_multiple_using_id(self):
        subnet1 = dict(id='123', name=self.subnet_name)
        subnet2 = dict(id='456', name=self.subnet_name)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': [subnet1, subnet2]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'subnets', '%s.json' % subnet1['id']]),
                 json={})
        ])
        self.assertTrue(self.cloud.delete_subnet(subnet1['id']))
        self.assert_calls()

    def test_update_subnet(self):
        expected_subnet = copy.copy(self.mock_subnet_rep)
        expected_subnet['name'] = 'goofy'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': [self.mock_subnet_rep]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'subnets', '%s.json' % self.subnet_id]),
                 json={'subnet': expected_subnet},
                 validate=dict(
                     json={'subnet': {'name': 'goofy'}}))
        ])
        subnet = self.cloud.update_subnet(self.subnet_id, subnet_name='goofy')
        self.assertDictEqual(expected_subnet, subnet)
        self.assert_calls()

    def test_update_subnet_gateway_ip(self):
        expected_subnet = copy.copy(self.mock_subnet_rep)
        gateway = '192.168.199.3'
        expected_subnet['gateway_ip'] = gateway
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': [self.mock_subnet_rep]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'subnets', '%s.json' % self.subnet_id]),
                 json={'subnet': expected_subnet},
                 validate=dict(
                     json={'subnet': {'gateway_ip': gateway}}))
        ])
        subnet = self.cloud.update_subnet(self.subnet_id, gateway_ip=gateway)
        self.assertDictEqual(expected_subnet, subnet)
        self.assert_calls()

    def test_update_subnet_disable_gateway_ip(self):
        expected_subnet = copy.copy(self.mock_subnet_rep)
        expected_subnet['gateway_ip'] = None
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'subnets.json']),
                 json={'subnets': [self.mock_subnet_rep]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'subnets', '%s.json' % self.subnet_id]),
                 json={'subnet': expected_subnet},
                 validate=dict(
                     json={'subnet': {'gateway_ip': None}}))
        ])
        subnet = self.cloud.update_subnet(self.subnet_id,
                                          disable_gateway_ip=True)
        self.assertDictEqual(expected_subnet, subnet)
        self.assert_calls()

    def test_update_subnet_conflict_gw_ops(self):
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.update_subnet,
                          self.subnet_id, gateway_ip="192.168.199.3",
                          disable_gateway_ip=True)
