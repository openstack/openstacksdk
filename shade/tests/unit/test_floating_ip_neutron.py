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
test_floating_ip_neutron
----------------------------------

Tests Floating IP resource methods for Neutron
"""

from mock import patch
from shade import OpenStackCloud
from shade.tests.unit import base


class TestFloatingIP(base.TestCase):
    mock_floating_ip_list_rep = {
        'floatingips': [
            {
                'router_id': 'd23abc8d-2991-4a55-ba98-2aaea84cc72f',
                'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
                'floating_network_id': '376da547-b977-4cfe-9cba-275c80debf57',
                'fixed_ip_address': '192.0.2.29',
                'floating_ip_address': '203.0.113.29',
                'port_id': 'ce705c24-c1ef-408a-bda3-7bbd946164ab',
                'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
                'status': 'ACTIVE'
            },
            {
                'router_id': None,
                'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
                'floating_network_id': '376da547-b977-4cfe-9cba-275c80debf57',
                'fixed_ip_address': None,
                'floating_ip_address': '203.0.113.30',
                'port_id': None,
                'id': '61cea855-49cb-4846-997d-801b70c71bdd',
                'status': 'DOWN'
            }
        ]
    }

    mock_floating_ip_new_rep = {
        'floatingip': {
            'fixed_ip_address': '10.0.0.4',
            'floating_ip_address': '172.24.4.229',
            'floating_network_id': 'my-network-id',
            'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda8',
            'port_id': None,
            'router_id': None,
            'status': 'ACTIVE',
            'tenant_id': '4969c491a3c74ee4af974e6d800c62df'
        }
    }

    mock_get_network_rep = {
        'status': 'ACTIVE',
        'subnets': [
            '54d6f61d-db07-451c-9ab3-b9609b6b6f0b'
        ],
        'name': 'my-network',
        'provider:physical_network': None,
        'admin_state_up': True,
        'tenant_id': '4fd44f30292945e481c7b8a0c8908869',
        'provider:network_type': 'local',
        'router:external': True,
        'shared': True,
        'id': 'my-network-id',
        'provider:segmentation_id': None
    }

    def assertAreInstances(self, elements, elem_type):
        for e in elements:
            self.assertIsInstance(e, elem_type)

    def setUp(self):
        super(TestFloatingIP, self).setUp()
        # floating_ip_source='neutron' is default for OpenStackCloud()
        self.client = OpenStackCloud("cloud", {})

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_list_floating_ips(self, mock_has_service, mock_neutron_client):
        mock_has_service.return_value = True
        mock_neutron_client.list_floatingips.return_value = \
            self.mock_floating_ip_list_rep

        floating_ips = self.client.list_floating_ips()

        mock_neutron_client.list_floatingips.assert_called_with()
        self.assertIsInstance(floating_ips, list)
        self.assertAreInstances(floating_ips, dict)
        self.assertEqual(2, len(floating_ips))

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_search_floating_ips(self, mock_has_service, mock_neutron_client):
        mock_has_service.return_value = True
        mock_neutron_client.list_floatingips.return_value = \
            self.mock_floating_ip_list_rep

        floating_ips = self.client.search_floating_ips(
            filters={'attached': False})

        mock_neutron_client.list_floatingips.assert_called_with()
        self.assertIsInstance(floating_ips, list)
        self.assertAreInstances(floating_ips, dict)
        self.assertEqual(1, len(floating_ips))

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_get_floating_ip(self, mock_has_service, mock_neutron_client):
        mock_has_service.return_value = True
        mock_neutron_client.list_floatingips.return_value = \
            self.mock_floating_ip_list_rep

        floating_ip = self.client.get_floating_ip(
            id='2f245a7b-796b-4f26-9cf9-9e82d248fda7')

        mock_neutron_client.list_floatingips.assert_called_with()
        self.assertIsInstance(floating_ip, dict)
        self.assertEqual('203.0.113.29', floating_ip['floating_ip_address'])

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_get_floating_ip_not_found(
            self, mock_has_service, mock_neutron_client):
        mock_has_service.return_value = True
        mock_neutron_client.list_floatingips.return_value = \
            self.mock_floating_ip_list_rep

        floating_ip = self.client.get_floating_ip(
            id='non-existent')

        self.assertIsNone(floating_ip)

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'search_networks')
    @patch.object(OpenStackCloud, 'has_service')
    def test_create_floating_ip(
            self, mock_has_service, mock_search_networks, mock_neutron_client):
        mock_has_service.return_value = True
        mock_search_networks.return_value = [self.mock_get_network_rep]
        mock_neutron_client.create_floatingip.return_value = \
            self.mock_floating_ip_new_rep

        ip = self.client.create_floating_ip(network='my-network')

        mock_neutron_client.create_floatingip.assert_called_with(
            body={'floatingip': {'floating_network_id': 'my-network-id'}}
        )
        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['floating_ip_address'],
            ip['floating_ip_address'])

    @patch.object(OpenStackCloud, '_neutron_list_floating_ips')
    @patch.object(OpenStackCloud, 'search_networks')
    @patch.object(OpenStackCloud, 'has_service')
    def test_available_floating_ip_existing(
            self, mock_has_service, mock_search_networks,
            mock__neutron_list_floating_ips):
        mock_has_service.return_value = True
        mock_search_networks.return_value = [self.mock_get_network_rep]
        mock__neutron_list_floating_ips.return_value = \
            [self.mock_floating_ip_new_rep['floatingip']]

        ip = self.client.available_floating_ip(network='my-network')

        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['floating_ip_address'],
            ip['floating_ip_address'])

    @patch.object(OpenStackCloud, '_neutron_create_floating_ip')
    @patch.object(OpenStackCloud, '_neutron_list_floating_ips')
    @patch.object(OpenStackCloud, 'search_networks')
    @patch.object(OpenStackCloud, 'has_service')
    def test_available_floating_ip_new(
            self, mock_has_service, mock_search_networks,
            mock__neutron_list_floating_ips,
            mock__neutron_create_floating_ip):
        mock_has_service.return_value = True
        mock_search_networks.return_value = [self.mock_get_network_rep]
        mock__neutron_list_floating_ips.return_value = []
        mock__neutron_create_floating_ip.return_value = \
            self.mock_floating_ip_new_rep['floatingip']

        ip = self.client.available_floating_ip(network='my-network')

        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['floating_ip_address'],
            ip['floating_ip_address'])
