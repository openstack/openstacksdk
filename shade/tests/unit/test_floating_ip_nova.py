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
test_floating_ip_nova
----------------------------------

Tests Floating IP resource methods for nova-network
"""

from mock import patch
import os_client_config

from novaclient import exceptions as n_exc

from shade import OpenStackCloud
from shade.tests.fakes import FakeFloatingIP
from shade.tests.unit import base


def has_service_side_effect(s):
    if s == 'network':
        return False
    return True


class TestFloatingIP(base.TestCase):
    mock_floating_ip_list_rep = [
        {
            'fixed_ip': None,
            'id': 1,
            'instance_id': None,
            'ip': '203.0.113.1',
            'pool': 'nova'
        },
        {
            'fixed_ip': None,
            'id': 2,
            'instance_id': None,
            'ip': '203.0.113.2',
            'pool': 'nova'
        },
        {
            'fixed_ip': '192.0.2.3',
            'id': 29,
            'instance_id': 'myself',
            'ip': '198.51.100.29',
            'pool': 'black_hole'
        }
    ]

    mock_floating_ip_pools = [
        {'id': 'pool1_id', 'name': 'nova'},
        {'id': 'pool2_id', 'name': 'pool2'}]

    def assertAreInstances(self, elements, elem_type):
        for e in elements:
            self.assertIsInstance(e, elem_type)

    def setUp(self):
        super(TestFloatingIP, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.client = OpenStackCloud(
            cloud_config=config.get_one_cloud(validate=False))

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_list_floating_ips(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = [
            FakeFloatingIP(**ip) for ip in self.mock_floating_ip_list_rep
        ]

        floating_ips = self.client.list_floating_ips()

        mock_nova_client.floating_ips.list.assert_called_with()
        self.assertIsInstance(floating_ips, list)
        self.assertEqual(3, len(floating_ips))
        self.assertAreInstances(floating_ips, dict)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_search_floating_ips(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = [
            FakeFloatingIP(**ip) for ip in self.mock_floating_ip_list_rep
        ]

        floating_ips = self.client.search_floating_ips(
            filters={'attached': False})

        mock_nova_client.floating_ips.list.assert_called_with()
        self.assertIsInstance(floating_ips, list)
        self.assertEqual(2, len(floating_ips))
        self.assertAreInstances(floating_ips, dict)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_get_floating_ip(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = [
            FakeFloatingIP(**ip) for ip in self.mock_floating_ip_list_rep
        ]

        floating_ip = self.client.get_floating_ip(id='29')

        mock_nova_client.floating_ips.list.assert_called_with()
        self.assertIsInstance(floating_ip, dict)
        self.assertEqual('198.51.100.29', floating_ip['floating_ip_address'])

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_get_floating_ip_not_found(
            self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = [
            FakeFloatingIP(**ip) for ip in self.mock_floating_ip_list_rep
        ]

        floating_ip = self.client.get_floating_ip(id='666')

        self.assertIsNone(floating_ip)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_create_floating_ip(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.create.return_value = FakeFloatingIP(
            **self.mock_floating_ip_list_rep[1])

        self.client.create_floating_ip(network='nova')

        mock_nova_client.floating_ips.create.assert_called_with(pool='nova')

    @patch.object(OpenStackCloud, '_nova_list_floating_ips')
    @patch.object(OpenStackCloud, 'has_service')
    def test_available_floating_ip_existing(
            self, mock_has_service, mock__nova_list_floating_ips):
        mock_has_service.side_effect = has_service_side_effect
        mock__nova_list_floating_ips.return_value = \
            self.mock_floating_ip_list_rep[:1]

        ip = self.client.available_floating_ip(network='nova')

        self.assertEqual(self.mock_floating_ip_list_rep[0]['ip'],
                         ip['floating_ip_address'])

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, '_nova_list_floating_ips')
    @patch.object(OpenStackCloud, 'has_service')
    def test_available_floating_ip_new(
            self, mock_has_service, mock__nova_list_floating_ips,
            mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock__nova_list_floating_ips.return_value = []
        mock_nova_client.floating_ips.create.return_value = \
            FakeFloatingIP(**self.mock_floating_ip_list_rep[0])

        ip = self.client.available_floating_ip(network='nova')

        self.assertEqual(self.mock_floating_ip_list_rep[0]['ip'],
                         ip['floating_ip_address'])

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_delete_floating_ip_existing(
            self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.delete.return_value = None

        ret = self.client.delete_floating_ip(
            floating_ip_id='a-wild-id-appears')

        mock_nova_client.floating_ips.delete.assert_called_with(
            floating_ip='a-wild-id-appears')
        self.assertTrue(ret)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_delete_floating_ip_not_found(
            self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.delete.side_effect = n_exc.NotFound(
            code=404)

        ret = self.client.delete_floating_ip(
            floating_ip_id='a-wild-id-appears')

        self.assertFalse(ret)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_attach_ip_to_server(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = [
            FakeFloatingIP(**ip) for ip in self.mock_floating_ip_list_rep
        ]

        self.client.attach_ip_to_server(
            server_id='server-id', floating_ip_id=1,
            fixed_address='192.0.2.129')

        mock_nova_client.servers.add_floating_ip.assert_called_with(
            server='server-id', address='203.0.113.1',
            fixed_address='192.0.2.129')

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_detach_ip_from_server(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = [
            FakeFloatingIP(**ip) for ip in self.mock_floating_ip_list_rep
        ]

        self.client.detach_ip_from_server(
            server_id='server-id', floating_ip_id=1)

        mock_nova_client.servers.remove_floating_ip.assert_called_with(
            server='server-id', address='203.0.113.1')

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_add_ip_from_pool(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = [
            FakeFloatingIP(**ip) for ip in self.mock_floating_ip_list_rep
        ]

        ip = self.client.add_ip_from_pool(
            server_id='server-id',
            network='nova',
            fixed_address='192.0.2.129')

        self.assertEqual('203.0.113.1', ip['floating_ip_address'])
