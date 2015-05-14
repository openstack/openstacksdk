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
test_floating_ip_common
----------------------------------

Tests floating IP resource methods for Neutron and Nova-network.
"""

from mock import patch
import os_client_config
from shade import meta
from shade import OpenStackCloud
from shade.tests.fakes import FakeServer
from shade.tests.unit import base


class TestFloatingIP(base.TestCase):
    def setUp(self):
        super(TestFloatingIP, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.client = OpenStackCloud(
            cloud_config=config.get_one_cloud(validate=False))

    @patch.object(OpenStackCloud, 'get_floating_ip')
    @patch.object(OpenStackCloud, 'attach_ip_to_server')
    @patch.object(OpenStackCloud, 'available_floating_ip')
    def test_add_auto_ip(
            self, mock_available_floating_ip, mock_attach_ip_to_server,
            mock_get_floating_ip):
        server = FakeServer(
            id='server-id', name='test-server', status="ACTIVE", addresses={}
        )
        server_dict = meta.obj_to_dict(server)

        mock_available_floating_ip.return_value = {
            "id": "this-is-a-floating-ip-id",
            "fixed_ip_address": None,
            "floating_ip_address": "203.0.113.29",
            "network": "this-is-a-net-or-pool-id",
            "attached": False,
            "status": "ACTIVE"
        }

        self.client.add_auto_ip(server=server_dict)

        mock_attach_ip_to_server.assert_called_with(
            timeout=60, wait=False, server_id='server-id',
            floating_ip_id='this-is-a-floating-ip-id')

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'add_ip_from_pool')
    def test_add_ips_to_server_pool(
            self, mock_add_ip_from_pool, mock_nova_client):
        server = FakeServer(
            id='romeo', name='test-server', status="ACTIVE", addresses={}
        )
        server_dict = meta.obj_to_dict(server)
        pool = 'nova'

        mock_nova_client.servers.get.return_value = server

        self.client.add_ips_to_server(server_dict, ip_pool=pool)

        mock_add_ip_from_pool.assert_called_with('romeo', pool)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'add_ip_list')
    def test_add_ips_to_server_ip_list(
            self, mock_add_ip_list, mock_nova_client):
        server = FakeServer(
            id='server-id', name='test-server', status="ACTIVE", addresses={}
        )
        server_dict = meta.obj_to_dict(server)
        ips = ['203.0.113.29', '172.24.4.229']
        mock_nova_client.servers.get.return_value = server

        self.client.add_ips_to_server(server_dict, ips=ips)

        mock_add_ip_list.assert_called_with(server_dict, ips)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'add_auto_ip')
    def test_add_ips_to_server_auto_ip(
            self, mock_add_auto_ip, mock_nova_client):
        server = FakeServer(
            id='server-id', name='test-server', status="ACTIVE", addresses={}
        )
        server_dict = meta.obj_to_dict(server)

        mock_nova_client.servers.get.return_value = server

        self.client.add_ips_to_server(server_dict)

        mock_add_auto_ip.assert_called_with(server_dict)
