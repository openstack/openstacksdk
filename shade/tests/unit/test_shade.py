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

from heatclient import client as heat_client
from neutronclient.common import exceptions as n_exc
import testtools

from os_client_config import cloud_config
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


class TestShade(base.TestCase):

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
    @mock.patch.object(cloud_config.CloudConfig, 'get_legacy_client')
    def test_heat_args(self, get_legacy_client_mock, get_session_mock):
        session_mock = mock.Mock()
        get_session_mock.return_value = session_mock
        self.cloud.heat_client
        get_legacy_client_mock.assert_called_once_with(
            service_key='orchestration',
            client_class=heat_client.Client,
            interface_key=None,
            pass_version_arg=True,
        )

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_list_networks(self, mock_neutron):
        net1 = {'id': '1', 'name': 'net1'}
        net2 = {'id': '2', 'name': 'net2'}
        mock_neutron.list_networks.return_value = {
            'networks': [net1, net2]
        }
        nets = self.cloud.list_networks()
        mock_neutron.list_networks.assert_called_once_with()
        self.assertEqual([net1, net2], nets)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_list_networks_filtered(self, mock_neutron):
        self.cloud.list_networks(filters={'name': 'test'})
        mock_neutron.list_networks.assert_called_once_with(name='test')

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_list_networks_exception(self, mock_neutron):
        mock_neutron.list_networks.side_effect = Exception()
        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Error fetching network list"
        ):
            self.cloud.list_networks()

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
    def test_create_router_specific_tenant(self, mock_client):
        self.cloud.create_router("goofy", project_id="project_id_value")
        mock_client.create_router.assert_called_once_with(
            body=dict(
                router=dict(
                    name='goofy',
                    admin_state_up=True,
                    tenant_id="project_id_value",
                )
            )
        )

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_router_with_enable_snat_True(self, mock_client):
        """Do not send enable_snat when same as neutron default."""
        self.cloud.create_router(name='goofy', admin_state_up=True,
                                 enable_snat=True)
        mock_client.create_router.assert_called_once_with(
            body=dict(
                router=dict(
                    name='goofy',
                    admin_state_up=True,
                )
            )
        )

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_router_with_enable_snat_False(self, mock_client):
        """Send enable_snat when it is False."""
        self.cloud.create_router(name='goofy', admin_state_up=True,
                                 enable_snat=False)
        mock_client.create_router.assert_called_once_with(
            body=dict(
                router=dict(
                    name='goofy',
                    admin_state_up=True,
                    external_gateway_info=dict(
                        enable_snat=False
                    )
                )
            )
        )

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

    def test_remove_router_interface_missing_argument(self):
        self.assertRaises(ValueError, self.cloud.remove_router_interface,
                          {'id': '123'})

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

    @mock.patch.object(shade.OpenStackCloud, 'search_ports')
    def test_list_router_interfaces_no_gw(self, mock_search):
        """
        If a router does not have external_gateway_info, do not fail.
        """
        external_port = {'id': 'external_port_id',
                         'fixed_ips': [
                             ('external_subnet_id', 'ip_address'),
                         ]}
        port_list = [external_port]
        router = {
            'id': 'router_id',
        }
        mock_search.return_value = port_list
        ret = self.cloud.list_router_interfaces(router,
                                                interface_type='external')
        mock_search.assert_called_once_with(
            filters={'device_id': router['id']}
        )
        self.assertEqual([], ret)

        # A router can have its external_gateway_info set to None
        router['external_gateway_info'] = None
        ret = self.cloud.list_router_interfaces(router,
                                                interface_type='external')
        self.assertEqual([], ret)

    @mock.patch.object(shade.OpenStackCloud, 'search_ports')
    def test_list_router_interfaces_all(self, mock_search):
        internal_port = {'id': 'internal_port_id',
                         'fixed_ips': [
                             ('internal_subnet_id', 'ip_address'),
                         ]}
        external_port = {'id': 'external_port_id',
                         'fixed_ips': [
                             ('external_subnet_id', 'ip_address'),
                         ]}
        port_list = [internal_port, external_port]
        router = {
            'id': 'router_id',
            'external_gateway_info': {
                'external_fixed_ips': [('external_subnet_id', 'ip_address')]
            }
        }
        mock_search.return_value = port_list
        ret = self.cloud.list_router_interfaces(router)
        mock_search.assert_called_once_with(
            filters={'device_id': router['id']}
        )
        self.assertEqual(port_list, ret)

    @mock.patch.object(shade.OpenStackCloud, 'search_ports')
    def test_list_router_interfaces_internal(self, mock_search):
        internal_port = {'id': 'internal_port_id',
                         'fixed_ips': [
                             ('internal_subnet_id', 'ip_address'),
                         ]}
        external_port = {'id': 'external_port_id',
                         'fixed_ips': [
                             ('external_subnet_id', 'ip_address'),
                         ]}
        port_list = [internal_port, external_port]
        router = {
            'id': 'router_id',
            'external_gateway_info': {
                'external_fixed_ips': [('external_subnet_id', 'ip_address')]
            }
        }
        mock_search.return_value = port_list
        ret = self.cloud.list_router_interfaces(router,
                                                interface_type='internal')
        mock_search.assert_called_once_with(
            filters={'device_id': router['id']}
        )
        self.assertEqual([internal_port], ret)

    @mock.patch.object(shade.OpenStackCloud, 'search_ports')
    def test_list_router_interfaces_external(self, mock_search):
        internal_port = {'id': 'internal_port_id',
                         'fixed_ips': [
                             ('internal_subnet_id', 'ip_address'),
                         ]}
        external_port = {'id': 'external_port_id',
                         'fixed_ips': [
                             ('external_subnet_id', 'ip_address'),
                         ]}
        port_list = [internal_port, external_port]
        router = {
            'id': 'router_id',
            'external_gateway_info': {
                'external_fixed_ips': [('external_subnet_id', 'ip_address')]
            }
        }
        mock_search.return_value = port_list
        ret = self.cloud.list_router_interfaces(router,
                                                interface_type='external')
        mock_search.assert_called_once_with(
            filters={'device_id': router['id']}
        )
        self.assertEqual([external_port], ret)

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

    @mock.patch.object(shade.OpenStackCloud, '_compute_client')
    def test__nova_extensions(self, mock_compute):
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
        mock_compute.get.return_value = body
        extensions = self.cloud._nova_extensions()
        mock_compute.get.assert_called_once_with('/extensions')
        self.assertEqual(set(['NMN', 'OS-DCF']), extensions)

    @mock.patch.object(shade.OpenStackCloud, '_compute_client')
    def test__nova_extensions_fails(self, mock_compute):
        mock_compute.get.side_effect = Exception()
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            "Error fetching extension list for nova"
        ):
            self.cloud._nova_extensions()

    @mock.patch.object(shade.OpenStackCloud, '_compute_client')
    def test__has_nova_extension(self, mock_compute):
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
        mock_compute.get.return_value = body
        self.assertTrue(self.cloud._has_nova_extension('NMN'))
        self.assertFalse(self.cloud._has_nova_extension('invalid'))

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
