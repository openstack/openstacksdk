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

import shade
from shade import exc
from shade.tests.unit import base


class TestRouter(base.RequestsMockTestCase):

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
