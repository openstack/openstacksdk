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
import munch

import glanceclient
from heatclient import client as heat_client
from neutronclient.common import exceptions as n_exc

from os_client_config import cloud_config
import shade
from shade import exc
from shade import meta
from shade.tests.unit import base


class TestShade(base.TestCase):

    def setUp(self):
        super(TestShade, self).setUp()
        self.cloud = shade.openstack_cloud(validate=False)

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

    @mock.patch.object(shade.OpenStackCloud, 'search_servers')
    def test_get_server(self, mock_search):
        server1 = dict(id='123', name='mickey')
        mock_search.return_value = [server1]
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

    @mock.patch.object(cloud_config.CloudConfig, 'get_session')
    @mock.patch.object(glanceclient, 'Client')
    def test_glance_args(
            self, mock_client, get_session_mock):
        session_mock = mock.Mock()
        session_mock.get_endpoint.return_value = 'http://example.com/v2'
        get_session_mock.return_value = session_mock
        self.cloud.glance_client
        mock_client.assert_called_with(
            '2',
            endpoint='http://example.com',
            region_name='', service_name=None,
            interface='public',
            service_type='image', session=mock.ANY,
        )

    @mock.patch.object(cloud_config.CloudConfig, 'get_session')
    @mock.patch.object(heat_client, 'Client')
    def test_heat_args(self, mock_client, get_session_mock):
        session_mock = mock.Mock()
        get_session_mock.return_value = session_mock
        self.cloud.heat_client
        mock_client.assert_called_with(
            '1',
            endpoint_type='public',
            region_name='',
            service_name=None,
            service_type='orchestration',
            session=mock.ANY,
        )

    @mock.patch.object(shade.OpenStackCloud, 'search_subnets')
    def test_get_subnet(self, mock_search):
        subnet = dict(id='123', name='mickey')
        mock_search.return_value = [subnet]
        r = self.cloud.get_subnet('mickey')
        self.assertIsNotNone(r)
        self.assertDictEqual(subnet, r)

    @mock.patch.object(shade.OpenStackCloud, 'search_routers')
    def test_get_router(self, mock_search):
        router1 = dict(id='123', name='mickey')
        mock_search.return_value = [router1]
        r = self.cloud.get_router('mickey')
        self.assertIsNotNone(r)
        self.assertDictEqual(router1, r)

    @mock.patch.object(shade.OpenStackCloud, 'search_routers')
    def test_get_router_not_found(self, mock_search):
        mock_search.return_value = []
        r = self.cloud.get_router('goofy')
        self.assertIsNone(r)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_router(self, mock_client):
        self.cloud.create_router(name='goofy', admin_state_up=True)
        self.assertTrue(mock_client.create_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_add_router_interface(self, mock_client):
        self.cloud.add_router_interface({'id': '123'}, subnet_id='abc')
        mock_client.add_interface_router.assert_called_once_with(
            router='123', body={'subnet_id': 'abc'}
        )

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_remove_router_interface(self, mock_client):
        self.cloud.remove_router_interface({'id': '123'}, subnet_id='abc')
        mock_client.remove_interface_router.assert_called_once_with(
            router='123', body={'subnet_id': 'abc'}
        )

    @mock.patch.object(shade.OpenStackCloud, 'get_router')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_update_router(self, mock_client, mock_get):
        router1 = dict(id='123', name='mickey')
        mock_get.return_value = router1
        self.cloud.update_router('123', name='goofy')
        self.assertTrue(mock_client.update_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_routers')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_router(self, mock_client, mock_search):
        router1 = dict(id='123', name='mickey')
        mock_search.return_value = [router1]
        self.cloud.delete_router('mickey')
        self.assertTrue(mock_client.delete_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_routers')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_router_not_found(self, mock_client, mock_search):
        mock_search.return_value = []
        r = self.cloud.delete_router('goofy')
        self.assertFalse(r)
        self.assertFalse(mock_client.delete_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_router_multiple_found(self, mock_client):
        router1 = dict(id='123', name='mickey')
        router2 = dict(id='456', name='mickey')
        mock_client.list_routers.return_value = dict(routers=[router1,
                                                              router2])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.delete_router,
                          'mickey')
        self.assertFalse(mock_client.delete_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_router_multiple_using_id(self, mock_client):
        router1 = dict(id='123', name='mickey')
        router2 = dict(id='456', name='mickey')
        mock_client.list_routers.return_value = dict(routers=[router1,
                                                              router2])
        self.cloud.delete_router('123')
        self.assertTrue(mock_client.delete_router.called)

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

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_flavor_by_ram(self, mock_nova_client):

        class Flavor1(object):
            id = '1'
            name = 'vanilla ice cream'
            ram = 100

        class Flavor2(object):
            id = '2'
            name = 'chocolate ice cream'
            ram = 200

        vanilla = meta.obj_to_dict(Flavor1())
        chocolate = meta.obj_to_dict(Flavor2())
        mock_nova_client.flavors.list.return_value = [vanilla, chocolate]
        flavor = self.cloud.get_flavor_by_ram(ram=150)
        self.assertEquals(chocolate, flavor)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_flavor_by_ram_and_include(self, mock_nova_client):
        class Flavor1(object):
            id = '1'
            name = 'vanilla ice cream'
            ram = 100

        class Flavor2(object):
            id = '2'
            name = 'chocolate ice cream'
            ram = 200

        class Flavor3(object):
            id = '3'
            name = 'strawberry ice cream'
            ram = 250

        vanilla = meta.obj_to_dict(Flavor1())
        chocolate = meta.obj_to_dict(Flavor2())
        strawberry = meta.obj_to_dict(Flavor3())
        mock_nova_client.flavors.list.return_value = [
            vanilla, chocolate, strawberry]
        flavor = self.cloud.get_flavor_by_ram(ram=150, include='strawberry')
        self.assertEquals(strawberry, flavor)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_flavor_by_ram_not_found(self, mock_nova_client):
        mock_nova_client.flavors.list.return_value = []
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.get_flavor_by_ram,
                          ram=100)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_get_flavor_string_and_int(self, mock_nova_client):
        class Flavor1(object):
            id = '1'
            name = 'vanilla ice cream'
            ram = 100

        vanilla = meta.obj_to_dict(Flavor1())
        mock_nova_client.flavors.list.return_value = [vanilla]
        flavor1 = self.cloud.get_flavor('1')
        self.assertEquals(vanilla, flavor1)
        flavor2 = self.cloud.get_flavor(1)
        self.assertEquals(vanilla, flavor2)

    def test__neutron_exceptions_resource_not_found(self):
        with mock.patch.object(
                shade._tasks, 'NetworkList',
                side_effect=n_exc.NotFound()):
            self.assertRaises(exc.OpenStackCloudResourceNotFound,
                              self.cloud.list_networks)

    def test__neutron_exceptions_url_not_found(self):
        with mock.patch.object(
                shade._tasks, 'NetworkList',
                side_effect=n_exc.NeutronClientException(status_code=404)):
            self.assertRaises(exc.OpenStackCloudURINotFound,
                              self.cloud.list_networks)

    def test__neutron_exceptions_neutron_client_generic(self):
        with mock.patch.object(
                shade._tasks, 'NetworkList',
                side_effect=n_exc.NeutronClientException()):
            self.assertRaises(exc.OpenStackCloudException,
                              self.cloud.list_networks)

    def test__neutron_exceptions_generic(self):
        with mock.patch.object(
                shade._tasks, 'NetworkList',
                side_effect=Exception()):
            self.assertRaises(exc.OpenStackCloudException,
                              self.cloud.list_networks)

    @mock.patch.object(shade._tasks.ServerList, 'main')
    def test_list_servers(self, mock_serverlist):
        '''This test verifies that calling list_servers results in a call
        to the ServerList task.'''
        mock_serverlist.return_value = [
            munch.Munch({'name': 'testserver',
                         'id': '1'})
        ]

        r = self.cloud.list_servers()
        self.assertEquals(1, len(r))
        self.assertEquals('testserver', r[0]['name'])

    @mock.patch.object(shade._tasks.ServerList, 'main')
    @mock.patch('shade.meta.get_hostvars_from_server')
    def test_list_servers_detailed(self,
                                   mock_get_hostvars_from_server,
                                   mock_serverlist):
        '''This test verifies that when list_servers is called with
        `detailed=True` that it calls `get_hostvars_from_server` for each
        server in the list.'''
        mock_serverlist.return_value = ['server1', 'server2']
        mock_get_hostvars_from_server.side_effect = [
            {'name': 'server1', 'id': '1'},
            {'name': 'server2', 'id': '2'},
        ]

        r = self.cloud.list_servers(detailed=True)

        self.assertEquals(2, len(r))
        self.assertEquals(len(r), mock_get_hostvars_from_server.call_count)
        self.assertEquals('server1', r[0]['name'])
        self.assertEquals('server2', r[1]['name'])
