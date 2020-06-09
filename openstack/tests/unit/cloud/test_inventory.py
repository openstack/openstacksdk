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

from unittest import mock

from openstack.cloud import inventory
import openstack.config
from openstack.tests import fakes
from openstack.tests.unit import base


class TestInventory(base.TestCase):

    def setUp(self):
        super(TestInventory, self).setUp()

    @mock.patch("openstack.config.loader.OpenStackConfig")
    @mock.patch("openstack.connection.Connection")
    def test__init(self, mock_cloud, mock_config):
        mock_config.return_value.get_all.return_value = [{}]

        inv = inventory.OpenStackInventory()

        mock_config.assert_called_once_with(
            config_files=openstack.config.loader.CONFIG_FILES
        )
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        self.assertTrue(mock_config.return_value.get_all.called)

    @mock.patch("openstack.config.loader.OpenStackConfig")
    @mock.patch("openstack.connection.Connection")
    def test__init_one_cloud(self, mock_cloud, mock_config):
        mock_config.return_value.get_one.return_value = [{}]

        inv = inventory.OpenStackInventory(cloud='supercloud')

        mock_config.assert_called_once_with(
            config_files=openstack.config.loader.CONFIG_FILES
        )
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        self.assertFalse(mock_config.return_value.get_all.called)
        mock_config.return_value.get_one.assert_called_once_with(
            'supercloud')

    @mock.patch("openstack.config.loader.OpenStackConfig")
    @mock.patch("openstack.connection.Connection")
    def test_list_hosts(self, mock_cloud, mock_config):
        mock_config.return_value.get_all.return_value = [{}]

        inv = inventory.OpenStackInventory()

        server = dict(id='server_id', name='server_name')
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        inv.clouds[0].list_servers.return_value = [server]
        inv.clouds[0].get_openstack_vars.return_value = server

        ret = inv.list_hosts()

        inv.clouds[0].list_servers.assert_called_once_with(detailed=True,
                                                           all_projects=False)
        self.assertFalse(inv.clouds[0].get_openstack_vars.called)
        self.assertEqual([server], ret)

    @mock.patch("openstack.config.loader.OpenStackConfig")
    @mock.patch("openstack.connection.Connection")
    def test_list_hosts_no_detail(self, mock_cloud, mock_config):
        mock_config.return_value.get_all.return_value = [{}]

        inv = inventory.OpenStackInventory()

        server = self.cloud._normalize_server(
            fakes.make_fake_server(
                '1234', 'test', 'ACTIVE', addresses={}))
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        inv.clouds[0].list_servers.return_value = [server]

        inv.list_hosts(expand=False)

        inv.clouds[0].list_servers.assert_called_once_with(detailed=False,
                                                           all_projects=False)
        self.assertFalse(inv.clouds[0].get_openstack_vars.called)

    @mock.patch("openstack.config.loader.OpenStackConfig")
    @mock.patch("openstack.connection.Connection")
    def test_list_hosts_all_projects(self, mock_cloud, mock_config):
        mock_config.return_value.get_all.return_value = [{}]

        inv = inventory.OpenStackInventory()

        server = dict(id='server_id', name='server_name')
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        inv.clouds[0].list_servers.return_value = [server]
        inv.clouds[0].get_openstack_vars.return_value = server

        ret = inv.list_hosts(all_projects=True)

        inv.clouds[0].list_servers.assert_called_once_with(detailed=True,
                                                           all_projects=True)
        self.assertFalse(inv.clouds[0].get_openstack_vars.called)
        self.assertEqual([server], ret)

    @mock.patch("openstack.config.loader.OpenStackConfig")
    @mock.patch("openstack.connection.Connection")
    def test_search_hosts(self, mock_cloud, mock_config):
        mock_config.return_value.get_all.return_value = [{}]

        inv = inventory.OpenStackInventory()

        server = dict(id='server_id', name='server_name')
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        inv.clouds[0].list_servers.return_value = [server]
        inv.clouds[0].get_openstack_vars.return_value = server

        ret = inv.search_hosts('server_id')
        self.assertEqual([server], ret)

    @mock.patch("openstack.config.loader.OpenStackConfig")
    @mock.patch("openstack.connection.Connection")
    def test_get_host(self, mock_cloud, mock_config):
        mock_config.return_value.get_all.return_value = [{}]

        inv = inventory.OpenStackInventory()

        server = dict(id='server_id', name='server_name')
        self.assertIsInstance(inv.clouds, list)
        self.assertEqual(1, len(inv.clouds))
        inv.clouds[0].list_servers.return_value = [server]
        inv.clouds[0].get_openstack_vars.return_value = server

        ret = inv.get_host('server_id')
        self.assertEqual(server, ret)
