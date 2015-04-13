# -*- coding: utf-8 -*-

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

import shade
from shade.tests.unit import base


class TestShade(base.TestCase):

    def setUp(self):
        super(TestShade, self).setUp()
        self.cloud = shade.openstack_cloud()

    def test_openstack_cloud(self):
        self.assertIsInstance(self.cloud, shade.OpenStackCloud)

    @mock.patch.object(shade.OpenStackCloud, 'list_subnets')
    def test_get_subnet(self, mock_list):
        subnet = dict(id='123', name='mickey')
        mock_list.return_value = [subnet]
        r = self.cloud.get_subnet('mickey')
        self.assertIsNotNone(r)
        self.assertDictEqual(subnet, r)

    @mock.patch.object(shade.OpenStackCloud, 'list_routers')
    def test_get_router(self, mock_list):
        router1 = dict(id='123', name='mickey')
        mock_list.return_value = [router1]
        r = self.cloud.get_router('mickey')
        self.assertIsNotNone(r)
        self.assertDictEqual(router1, r)

    @mock.patch.object(shade.OpenStackCloud, 'list_routers')
    def test_get_router_not_found(self, mock_list):
        mock_list.return_value = []
        r = self.cloud.get_router('goofy')
        self.assertIsNone(r)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_router(self, mock_client):
        self.cloud.create_router(name='goofy', admin_state_up=True)
        self.assertTrue(mock_client.create_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_update_router(self, mock_client):
        self.cloud.update_router(router_id=123, name='goofy')
        self.assertTrue(mock_client.update_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_routers')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_router(self, mock_client, mock_list):
        router1 = dict(id='123', name='mickey')
        mock_list.return_value = [router1]
        self.cloud.delete_router('mickey')
        self.assertTrue(mock_client.delete_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_routers')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_router_not_found(self, mock_client, mock_list):
        router1 = dict(id='123', name='mickey')
        mock_list.return_value = [router1]
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.delete_router,
                          'goofy')
        self.assertFalse(mock_client.delete_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_routers')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_router_multiple_found(self, mock_client, mock_list):
        router1 = dict(id='123', name='mickey')
        router2 = dict(id='456', name='mickey')
        mock_list.return_value = [router1, router2]
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.delete_router,
                          'mickey')
        self.assertFalse(mock_client.delete_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_routers')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_router_multiple_using_id(self, mock_client, mock_list):
        router1 = dict(id='123', name='mickey')
        router2 = dict(id='456', name='mickey')
        mock_list.return_value = [router1, router2]
        self.cloud.delete_router('123')
        self.assertTrue(mock_client.delete_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet(self, mock_client, mock_list):
        net1 = dict(id='123', name='donald')
        mock_list.return_value = [net1]
        pool = [{'start': '192.168.199.2', 'end': '192.168.199.254'}]
        dns = ['8.8.8.8']
        routes = [{"destination": "0.0.0.0/0", "nexthop": "123.456.78.9"}]
        self.cloud.create_subnet('donald', '192.168.199.0/24',
                                 allocation_pools=pool,
                                 dns_nameservers=dns,
                                 host_routes=routes)
        self.assertTrue(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet_bad_network(self, mock_client, mock_list):
        net1 = dict(id='123', name='donald')
        mock_list.return_value = [net1]
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.create_subnet,
                          'duck', '192.168.199.0/24')
        self.assertFalse(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet_non_unique_network(self, mock_client, mock_list):
        net1 = dict(id='123', name='donald')
        net2 = dict(id='456', name='donald')
        mock_list.return_value = [net1, net2]
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.create_subnet,
                          'donald', '192.168.199.0/24')
        self.assertFalse(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_subnets')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_subnet(self, mock_client, mock_list):
        subnet1 = dict(id='123', name='mickey')
        mock_list.return_value = [subnet1]
        self.cloud.delete_subnet('mickey')
        self.assertTrue(mock_client.delete_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_subnets')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_subnet_not_found(self, mock_client, mock_list):
        subnet1 = dict(id='123', name='mickey')
        mock_list.return_value = [subnet1]
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.delete_subnet,
                          'goofy')
        self.assertFalse(mock_client.delete_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_subnets')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_subnet_multiple_found(self, mock_client, mock_list):
        subnet1 = dict(id='123', name='mickey')
        subnet2 = dict(id='456', name='mickey')
        mock_list.return_value = [subnet1, subnet2]
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.delete_subnet,
                          'mickey')
        self.assertFalse(mock_client.delete_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'list_subnets')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_subnet_multiple_using_id(self, mock_client, mock_list):
        subnet1 = dict(id='123', name='mickey')
        subnet2 = dict(id='456', name='mickey')
        mock_list.return_value = [subnet1, subnet2]
        self.cloud.delete_subnet('123')
        self.assertTrue(mock_client.delete_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_update_subnet(self, mock_client):
        self.cloud.update_subnet(subnet_id=123, subnet_name='goofy')
        self.assertTrue(mock_client.update_subnet.called)


class TestShadeOperator(base.TestCase):

    def setUp(self):
        super(TestShadeOperator, self).setUp()
        self.cloud = shade.operator_cloud()

    def test_operator_cloud(self):
        self.assertIsInstance(self.cloud, shade.OperatorCloud)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_patch_machine(self, mock_client):
        node_id = 'node01'
        patch = []
        patch.append({'op': 'remove', 'path': '/instance_info'})
        self.cloud.patch_machine(node_id, patch)
        self.assertTrue(mock_client.node.update.called)
