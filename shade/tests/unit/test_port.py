# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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

"""
test_port
----------------------------------

Test port resource (managed by neutron)
"""

from mock import patch
import os_client_config
from shade import OpenStackCloud
from shade.exc import OpenStackCloudException
from shade.tests.unit import base


class TestPort(base.TestCase):
    mock_neutron_port_create_rep = {
        'port': {
            'status': 'DOWN',
            'binding:host_id': '',
            'name': 'test-port-name',
            'allowed_address_pairs': [],
            'admin_state_up': True,
            'network_id': 'test-net-id',
            'tenant_id': 'test-tenant-id',
            'binding:vif_details': {},
            'binding:vnic_type': 'normal',
            'binding:vif_type': 'unbound',
            'device_owner': '',
            'mac_address': '50:1c:0d:e4:f0:0d',
            'binding:profile': {},
            'fixed_ips': [
                {
                    'subnet_id': 'test-subnet-id',
                    'ip_address': '29.29.29.29'
                }
            ],
            'id': 'test-port-id',
            'security_groups': [],
            'device_id': ''
        }
    }

    mock_neutron_port_update_rep = {
        'port': {
            'status': 'DOWN',
            'binding:host_id': '',
            'name': 'test-port-name-updated',
            'allowed_address_pairs': [],
            'admin_state_up': True,
            'network_id': 'test-net-id',
            'tenant_id': 'test-tenant-id',
            'binding:vif_details': {},
            'binding:vnic_type': 'normal',
            'binding:vif_type': 'unbound',
            'device_owner': '',
            'mac_address': '50:1c:0d:e4:f0:0d',
            'binding:profile': {},
            'fixed_ips': [
                {
                    'subnet_id': 'test-subnet-id',
                    'ip_address': '29.29.29.29'
                }
            ],
            'id': 'test-port-id',
            'security_groups': [],
            'device_id': ''
        }
    }

    mock_neutron_port_list_rep = {
        'ports': [
            {
                'status': 'ACTIVE',
                'binding:host_id': 'devstack',
                'name': 'first-port',
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
                'device_owner': 'network:router_gateway',
                'mac_address': 'fa:16:3e:58:42:ed',
                'binding:profile': {},
                'binding:vnic_type': 'normal',
                'fixed_ips': [
                    {
                        'subnet_id': '008ba151-0b8c-4a67-98b5-0d2b87666062',
                        'ip_address': '172.24.4.2'
                    }
                ],
                'id': 'd80b1a3b-4fc1-49f3-952e-1e2ab7081d8b',
                'security_groups': [],
                'device_id': '9ae135f4-b6e0-4dad-9e91-3c223e385824'
            },
            {
                'status': 'ACTIVE',
                'binding:host_id': 'devstack',
                'name': '',
                'allowed_address_pairs': [],
                'admin_state_up': True,
                'network_id': 'f27aa545-cbdd-4907-b0c6-c9e8b039dcc2',
                'tenant_id': 'd397de8a63f341818f198abb0966f6f3',
                'extra_dhcp_opts': [],
                'binding:vif_details': {
                    'port_filter': True,
                    'ovs_hybrid_plug': True
                },
                'binding:vif_type': 'ovs',
                'device_owner': 'network:router_interface',
                'mac_address': 'fa:16:3e:bb:3c:e4',
                'binding:profile': {},
                'binding:vnic_type': 'normal',
                'fixed_ips': [
                    {
                        'subnet_id': '288bf4a1-51ba-43b6-9d0a-520e9005db17',
                        'ip_address': '10.0.0.1'
                    }
                ],
                'id': 'f71a6703-d6de-4be1-a91a-a570ede1d159',
                'security_groups': [],
                'device_id': '9ae135f4-b6e0-4dad-9e91-3c223e385824'
            }
        ]
    }

    def setUp(self):
        super(TestPort, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.client = OpenStackCloud(
            cloud_config=config.get_one_cloud(validate=False))

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_create_port(self, mock_neutron_client):
        mock_neutron_client.create_port.return_value = \
            self.mock_neutron_port_create_rep

        port = self.client.create_port(
            network_id='test-net-id', name='test-port-name',
            admin_state_up=True)

        mock_neutron_client.create_port.assert_called_with(
            body={'port': dict(network_id='test-net-id', name='test-port-name',
                               admin_state_up=True)})
        self.assertEqual(self.mock_neutron_port_create_rep['port'], port)

    def test_create_port_parameters(self):
        """Test that we detect invalid arguments passed to create_port"""
        self.assertRaises(
            TypeError, self.client.create_port,
            network_id='test-net-id', nome='test-port-name',
            stato_amministrativo_porta=True)

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_create_port_exception(self, mock_neutron_client):
        mock_neutron_client.create_port.side_effect = Exception('blah')

        self.assertRaises(
            OpenStackCloudException, self.client.create_port,
            network_id='test-net-id', name='test-port-name',
            admin_state_up=True)

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_update_port(self, mock_neutron_client):
        mock_neutron_client.list_ports.return_value = \
            self.mock_neutron_port_list_rep
        mock_neutron_client.update_port.return_value = \
            self.mock_neutron_port_update_rep

        port = self.client.update_port(
            name_or_id='d80b1a3b-4fc1-49f3-952e-1e2ab7081d8b',
            name='test-port-name-updated')

        mock_neutron_client.update_port.assert_called_with(
            port='d80b1a3b-4fc1-49f3-952e-1e2ab7081d8b',
            body={'port': dict(name='test-port-name-updated')})
        self.assertEqual(self.mock_neutron_port_update_rep['port'], port)

    def test_update_port_parameters(self):
        """Test that we detect invalid arguments passed to update_port"""
        self.assertRaises(
            TypeError, self.client.update_port,
            name_or_id='test-port-id', nome='test-port-name-updated')

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_update_port_exception(self, mock_neutron_client):
        mock_neutron_client.list_ports.return_value = \
            self.mock_neutron_port_list_rep
        mock_neutron_client.update_port.side_effect = Exception('blah')

        self.assertRaises(
            OpenStackCloudException, self.client.update_port,
            name_or_id='d80b1a3b-4fc1-49f3-952e-1e2ab7081d8b',
            name='test-port-name-updated')

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_list_ports(self, mock_neutron_client):
        mock_neutron_client.list_ports.return_value = \
            self.mock_neutron_port_list_rep

        ports = self.client.list_ports()

        mock_neutron_client.list_ports.assert_called_with()
        self.assertItemsEqual(self.mock_neutron_port_list_rep['ports'], ports)

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_list_ports_exception(self, mock_neutron_client):
        mock_neutron_client.list_ports.side_effect = Exception('blah')

        self.assertRaises(OpenStackCloudException, self.client.list_ports)

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_search_ports_by_id(self, mock_neutron_client):
        mock_neutron_client.list_ports.return_value = \
            self.mock_neutron_port_list_rep

        ports = self.client.search_ports(
            name_or_id='f71a6703-d6de-4be1-a91a-a570ede1d159')

        mock_neutron_client.list_ports.assert_called_with()
        self.assertEquals(1, len(ports))
        self.assertEquals('fa:16:3e:bb:3c:e4', ports[0]['mac_address'])

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_search_ports_by_name(self, mock_neutron_client):
        mock_neutron_client.list_ports.return_value = \
            self.mock_neutron_port_list_rep

        ports = self.client.search_ports(name_or_id='first-port')

        mock_neutron_client.list_ports.assert_called_with()
        self.assertEquals(1, len(ports))
        self.assertEquals('fa:16:3e:58:42:ed', ports[0]['mac_address'])

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_search_ports_not_found(self, mock_neutron_client):
        mock_neutron_client.list_ports.return_value = \
            self.mock_neutron_port_list_rep

        ports = self.client.search_ports(name_or_id='non-existent')

        mock_neutron_client.list_ports.assert_called_with()
        self.assertEquals(0, len(ports))

    @patch.object(OpenStackCloud, 'neutron_client')
    def test_delete_port(self, mock_neutron_client):
        mock_neutron_client.list_ports.return_value = \
            self.mock_neutron_port_list_rep

        self.client.delete_port(name_or_id='first-port')

        mock_neutron_client.delete_port.assert_called_with(
            port='d80b1a3b-4fc1-49f3-952e-1e2ab7081d8b')
