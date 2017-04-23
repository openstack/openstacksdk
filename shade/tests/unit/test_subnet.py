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

import mock
import testtools

import shade
from shade import exc
from shade.tests.unit import base


class TestSubnet(base.RequestsMockTestCase):

    @mock.patch.object(shade.OpenStackCloud, 'search_subnets')
    def test_get_subnet(self, mock_search):
        subnet = dict(id='123', name='mickey')
        mock_search.return_value = [subnet]
        r = self.cloud.get_subnet('mickey')
        self.assertIsNotNone(r)
        self.assertDictEqual(subnet, r)

    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet(self, mock_client, mock_search):
        net1 = dict(id='123', name='donald')
        mock_search.return_value = [net1]
        pool = [{'start': '192.168.199.2', 'end': '192.168.199.254'}]
        dns = ['8.8.8.8']
        routes = [{"destination": "0.0.0.0/0", "nexthop": "123.456.78.9"}]
        self.cloud.create_subnet('donald', '192.168.199.0/24',
                                 allocation_pools=pool,
                                 dns_nameservers=dns,
                                 host_routes=routes)
        self.assertTrue(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet_string_ip_version(self, mock_client, mock_search):
        '''Allow ip_version as a string'''
        net1 = dict(id='123', name='donald')
        mock_search.return_value = [net1]
        self.cloud.create_subnet('donald', '192.168.199.0/24', ip_version='4')
        self.assertTrue(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    def test_create_subnet_bad_ip_version(self, mock_search):
        '''String ip_versions must be convertable to int'''
        net1 = dict(id='123', name='donald')
        mock_search.return_value = [net1]

        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "ip_version must be an integer"
        ):
            self.cloud.create_subnet('donald', '192.168.199.0/24',
                                     ip_version='4x')

    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet_without_gateway_ip(self, mock_client, mock_search):
        net1 = dict(id='123', name='donald')
        mock_search.return_value = [net1]
        pool = [{'start': '192.168.200.2', 'end': '192.168.200.254'}]
        dns = ['8.8.8.8']
        self.cloud.create_subnet('kooky', '192.168.200.0/24',
                                 allocation_pools=pool,
                                 dns_nameservers=dns,
                                 disable_gateway_ip=True)
        self.assertTrue(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet_with_gateway_ip(self, mock_client, mock_search):
        net1 = dict(id='123', name='donald')
        mock_search.return_value = [net1]
        pool = [{'start': '192.168.200.8', 'end': '192.168.200.254'}]
        dns = ['8.8.8.8']
        gateway = '192.168.200.2'
        self.cloud.create_subnet('kooky', '192.168.200.0/24',
                                 allocation_pools=pool,
                                 dns_nameservers=dns,
                                 gateway_ip=gateway)
        self.assertTrue(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    def test_create_subnet_conflict_gw_ops(self, mock_search):
        net1 = dict(id='123', name='donald')
        mock_search.return_value = [net1]
        gateway = '192.168.200.3'
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.create_subnet, 'kooky',
                          '192.168.200.0/24', gateway_ip=gateway,
                          disable_gateway_ip=True)

    @mock.patch.object(shade.OpenStackCloud, 'list_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet_bad_network(self, mock_client, mock_list):
        net1 = dict(id='123', name='donald')
        mock_list.return_value = [net1]
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.create_subnet,
                          'duck', '192.168.199.0/24')
        self.assertFalse(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet_non_unique_network(self, mock_client, mock_search):
        net1 = dict(id='123', name='donald')
        net2 = dict(id='456', name='donald')
        mock_search.return_value = [net1, net2]
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.create_subnet,
                          'donald', '192.168.199.0/24')
        self.assertFalse(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_subnets')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_subnet(self, mock_client, mock_search):
        subnet1 = dict(id='123', name='mickey')
        mock_search.return_value = [subnet1]
        self.cloud.delete_subnet('mickey')
        self.assertTrue(mock_client.delete_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_subnets')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_subnet_not_found(self, mock_client, mock_search):
        mock_search.return_value = []
        r = self.cloud.delete_subnet('goofy')
        self.assertFalse(r)
        self.assertFalse(mock_client.delete_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_subnet_multiple_found(self, mock_client):
        subnet1 = dict(id='123', name='mickey')
        subnet2 = dict(id='456', name='mickey')
        mock_client.list_subnets.return_value = dict(subnets=[subnet1,
                                                              subnet2])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.delete_subnet,
                          'mickey')
        self.assertFalse(mock_client.delete_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_subnet_multiple_using_id(self, mock_client):
        subnet1 = dict(id='123', name='mickey')
        subnet2 = dict(id='456', name='mickey')
        mock_client.list_subnets.return_value = dict(subnets=[subnet1,
                                                              subnet2])
        self.cloud.delete_subnet('123')
        self.assertTrue(mock_client.delete_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'get_subnet')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_update_subnet(self, mock_client, mock_get):
        subnet1 = dict(id='123', name='mickey')
        mock_get.return_value = subnet1
        self.cloud.update_subnet('123', subnet_name='goofy')
        self.assertTrue(mock_client.update_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'get_subnet')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_update_subnet_gateway_ip(self, mock_client, mock_get):
        subnet1 = dict(id='456', name='kooky')
        mock_get.return_value = subnet1
        gateway = '192.168.200.3'
        self.cloud.update_subnet(
            '456', gateway_ip=gateway)
        self.assertTrue(mock_client.update_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'get_subnet')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_update_subnet_disable_gateway_ip(self, mock_client, mock_get):
        subnet1 = dict(id='456', name='kooky')
        mock_get.return_value = subnet1
        self.cloud.update_subnet(
            '456', disable_gateway_ip=True)
        self.assertTrue(mock_client.update_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'get_subnet')
    def test_update_subnet_conflict_gw_ops(self, mock_get):
        subnet1 = dict(id='456', name='kooky')
        mock_get.return_value = subnet1
        gateway = '192.168.200.3'
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.update_subnet,
                          '456', gateway_ip=gateway, disable_gateway_ip=True)
