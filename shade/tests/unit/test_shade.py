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

    def test__filter_list_name_or_id(self):
        el1 = dict(id=100, name='donald')
        el2 = dict(id=200, name='pluto')
        data = [el1, el2]
        ret = self.cloud._filter_list(data, 'donald', None)
        self.assertEquals([el1], ret)

    def test__filter_list_filter(self):
        el1 = dict(id=100, name='donald', other='duck')
        el2 = dict(id=200, name='donald', other='trump')
        data = [el1, el2]
        ret = self.cloud._filter_list(data, 'donald', {'other': 'duck'})
        self.assertEquals([el1], ret)

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
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.delete_router,
                          'goofy')
        self.assertFalse(mock_client.delete_router.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_router_multiple_found(self, mock_client):
        router1 = dict(id='123', name='mickey')
        router2 = dict(id='456', name='mickey')
        mock_client.list_routers.return_value = dict(routers=[router1,
                                                              router2])
        self.assertRaises(shade.OpenStackCloudException,
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
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.create_subnet,
                          'duck', '192.168.199.0/24')
        self.assertFalse(mock_client.create_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_subnet_non_unique_network(self, mock_client, mock_search):
        net1 = dict(id='123', name='donald')
        net2 = dict(id='456', name='donald')
        mock_search.return_value = [net1, net2]
        self.assertRaises(shade.OpenStackCloudException,
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
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.delete_subnet,
                          'goofy')
        self.assertFalse(mock_client.delete_subnet.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_subnet_multiple_found(self, mock_client):
        subnet1 = dict(id='123', name='mickey')
        subnet2 = dict(id='456', name='mickey')
        mock_client.list_subnets.return_value = dict(subnets=[subnet1,
                                                              subnet2])
        self.assertRaises(shade.OpenStackCloudException,
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

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_no_action(self, mock_patch, mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            name = 'node01'

        expected_machine = dict(
            uuid='00000000-0000-0000-0000-000000000000',
            name='node01'
        )
        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine('node01')
        self.assertIsNone(update_dict['changes'])
        self.assertFalse(mock_patch.called)
        self.assertDictEqual(expected_machine, update_dict['node'])

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_no_action_name(self, mock_patch,
                                                 mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            name = 'node01'

        expected_machine = dict(
            uuid='00000000-0000-0000-0000-000000000000',
            name='node01'
        )
        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine('node01', name='node01')
        self.assertIsNone(update_dict['changes'])
        self.assertFalse(mock_patch.called)
        self.assertDictEqual(expected_machine, update_dict['node'])

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_action_name(self, mock_patch,
                                              mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            name = 'evil'

        expected_patch = [dict(op='replace', path='/name', value='good')]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine('evil', name='good')
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/name', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_name(self, mock_patch,
                                              mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            name = 'evil'

        expected_patch = [dict(op='replace', path='/name', value='good')]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine('evil', name='good')
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/name', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_chassis_uuid(self, mock_patch,
                                                      mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            chassis_uuid = None

        expected_patch = [
            dict(
                op='replace',
                path='/chassis_uuid',
                value='00000000-0000-0000-0000-000000000001'
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            chassis_uuid='00000000-0000-0000-0000-000000000001')
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/chassis_uuid', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_driver(self, mock_patch,
                                                mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            driver = None

        expected_patch = [
            dict(
                op='replace',
                path='/driver',
                value='fake'
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            driver='fake'
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/driver', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_driver_info(self, mock_patch,
                                                     mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            driver_info = None

        expected_patch = [
            dict(
                op='replace',
                path='/driver_info',
                value=dict(var='fake')
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            driver_info=dict(var="fake")
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/driver_info', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_instance_info(self, mock_patch,
                                                       mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            instance_info = None

        expected_patch = [
            dict(
                op='replace',
                path='/instance_info',
                value=dict(var='fake')
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            instance_info=dict(var="fake")
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/instance_info', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_instance_uuid(self, mock_patch,
                                                       mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            instance_uuid = None

        expected_patch = [
            dict(
                op='replace',
                path='/instance_uuid',
                value='00000000-0000-0000-0000-000000000002'
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            instance_uuid='00000000-0000-0000-0000-000000000002'
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/instance_uuid', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_properties(self, mock_patch,
                                                    mock_client):
        class client_return_value:
            uuid = '00000000-0000-0000-0000-000000000000'
            properties = None

        expected_patch = [
            dict(
                op='replace',
                path='/properties',
                value=dict(var='fake')
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            properties=dict(var="fake")
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/properties', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_register_machine(self, mock_client):
        class fake_node:
            uuid = "00000000-0000-0000-0000-000000000000"

        expected_return_value = dict(
            uuid="00000000-0000-0000-0000-000000000000",
        )
        mock_client.node.create.return_value = fake_node
        nics = [{'mac': '00:00:00:00:00:00'}]
        return_value = self.cloud.register_machine(nics)
        self.assertDictEqual(expected_return_value, return_value)
        self.assertTrue(mock_client.node.create.called)
        self.assertTrue(mock_client.port.create.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_register_machine_port_create_failed(self, mock_client):
        nics = [{'mac': '00:00:00:00:00:00'}]
        mock_client.port.create.side_effect = (
            shade.OpenStackCloudException("Error"))
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.register_machine,
                          nics)
        self.assertTrue(mock_client.node.create.called)
        self.assertTrue(mock_client.port.create.called)
        self.assertTrue(mock_client.node.delete.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_unregister_machine(self, mock_client):
        nics = [{'mac': '00:00:00:00:00:00'}]
        uuid = "00000000-0000-0000-0000-000000000000"
        self.cloud.unregister_machine(nics, uuid)
        self.assertTrue(mock_client.node.delete.called)
        self.assertTrue(mock_client.port.delete.called)
        self.assertTrue(mock_client.port.get_by_address.called)

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_get_image_name(self, glance_mock):

        class Image(object):
            id = '22'
            name = '22 name'
            status = 'success'
        fake_image = Image()
        glance_mock.images.list.return_value = [fake_image]
        self.assertEqual('22 name', self.cloud.get_image_name('22'))
        self.assertEqual('22 name', self.cloud.get_image_name('22 name'))

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_get_image_id(self, glance_mock):

        class Image(object):
            id = '22'
            name = '22 name'
            status = 'success'
        fake_image = Image()
        glance_mock.images.list.return_value = [fake_image]
        self.assertEqual('22', self.cloud.get_image_id('22'))
        self.assertEqual('22', self.cloud.get_image_id('22 name'))
