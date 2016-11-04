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
from novaclient import exceptions as n_exc

from shade import meta
from shade import OpenStackCloud
from shade.tests import fakes
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
        self.floating_ips = [
            fakes.FakeFloatingIP(**ip) for ip in self.mock_floating_ip_list_rep
        ]

        self.fake_server = meta.obj_to_dict(
            fakes.FakeServer(
                'server-id', '', 'ACTIVE',
                addresses={u'test_pnztt_net': [{
                    u'OS-EXT-IPS:type': u'fixed',
                    u'addr': '192.0.2.129',
                    u'version': 4,
                    u'OS-EXT-IPS-MAC:mac_addr':
                    u'fa:16:3e:ae:7d:42'}]}))

        self.floating_ip = self.cloud._normalize_floating_ips(
            meta.obj_list_to_dict(self.floating_ips))[0]

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_list_floating_ips(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = self.floating_ips

        floating_ips = self.cloud.list_floating_ips()

        mock_nova_client.floating_ips.list.assert_called_with()
        self.assertIsInstance(floating_ips, list)
        self.assertEqual(3, len(floating_ips))
        self.assertAreInstances(floating_ips, dict)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_list_floating_ips_with_filters(self, mock_has_service,
                                            mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect

        self.assertRaisesRegex(
            ValueError, "Nova-network don't support server-side",
            self.cloud.list_floating_ips, filters={'Foo': 42}
        )

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_search_floating_ips(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = self.floating_ips

        floating_ips = self.cloud.search_floating_ips(
            filters={'attached': False})

        mock_nova_client.floating_ips.list.assert_called_with()
        self.assertIsInstance(floating_ips, list)
        self.assertEqual(2, len(floating_ips))
        self.assertAreInstances(floating_ips, dict)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_get_floating_ip(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = self.floating_ips

        floating_ip = self.cloud.get_floating_ip(id='29')

        mock_nova_client.floating_ips.list.assert_called_with()
        self.assertIsInstance(floating_ip, dict)
        self.assertEqual('198.51.100.29', floating_ip['floating_ip_address'])

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_get_floating_ip_not_found(
            self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = self.floating_ips

        floating_ip = self.cloud.get_floating_ip(id='666')

        self.assertIsNone(floating_ip)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_create_floating_ip(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.create.return_value =\
            fakes.FakeFloatingIP(**self.mock_floating_ip_list_rep[1])

        self.cloud.create_floating_ip(network='nova')

        mock_nova_client.floating_ips.create.assert_called_with(pool='nova')

    @patch.object(OpenStackCloud, '_nova_list_floating_ips')
    @patch.object(OpenStackCloud, 'has_service')
    def test_available_floating_ip_existing(
            self, mock_has_service, mock__nova_list_floating_ips):
        mock_has_service.side_effect = has_service_side_effect
        mock__nova_list_floating_ips.return_value = \
            self.mock_floating_ip_list_rep[:1]

        ip = self.cloud.available_floating_ip(network='nova')

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
            fakes.FakeFloatingIP(**self.mock_floating_ip_list_rep[0])

        ip = self.cloud.available_floating_ip(network='nova')

        self.assertEqual(self.mock_floating_ip_list_rep[0]['ip'],
                         ip['floating_ip_address'])

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_delete_floating_ip_existing(
            self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.delete.return_value = None

        ret = self.cloud.delete_floating_ip(
            floating_ip_id='a-wild-id-appears')

        mock_nova_client.floating_ips.delete.assert_called_with(
            floating_ip='a-wild-id-appears')
        self.assertTrue(ret)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'get_floating_ip')
    @patch.object(OpenStackCloud, '_use_neutron_floating')
    def test_delete_floating_ip_not_found(
            self, mock_use_floating, mock_get_floating_ip, mock_nova_client):
        mock_use_floating.return_value = False
        mock_get_floating_ip.return_value = None
        mock_nova_client.floating_ips.delete.side_effect = n_exc.NotFound(
            code=404)

        ret = self.cloud.delete_floating_ip(
            floating_ip_id='a-wild-id-appears')

        self.assertFalse(ret)

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_attach_ip_to_server(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = self.floating_ips

        self.cloud._attach_ip_to_server(
            server=self.fake_server, floating_ip=self.floating_ip,
            fixed_address='192.0.2.129')

        mock_nova_client.servers.add_floating_ip.assert_called_with(
            server='server-id', address='203.0.113.1',
            fixed_address='192.0.2.129')

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_detach_ip_from_server(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = [
            fakes.FakeFloatingIP(**ip) for ip in self.mock_floating_ip_list_rep
        ]

        self.cloud.detach_ip_from_server(
            server_id='server-id', floating_ip_id=1)

        mock_nova_client.servers.remove_floating_ip.assert_called_with(
            server='server-id', address='203.0.113.1')

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_add_ip_from_pool(self, mock_has_service, mock_nova_client):
        mock_has_service.side_effect = has_service_side_effect
        mock_nova_client.floating_ips.list.return_value = self.floating_ips

        server = self.cloud._add_ip_from_pool(
            server=self.fake_server,
            network='nova',
            fixed_address='192.0.2.129')

        self.assertEqual(server, self.fake_server)

    @patch.object(OpenStackCloud, 'delete_floating_ip')
    @patch.object(OpenStackCloud, 'list_floating_ips')
    @patch.object(OpenStackCloud, '_use_neutron_floating')
    def test_cleanup_floating_ips(
            self, mock_use_neutron_floating, mock_list_floating_ips,
            mock_delete_floating_ip):
        mock_use_neutron_floating.return_value = False

        self.cloud.delete_unattached_floating_ips()

        mock_delete_floating_ip.assert_not_called()
        mock_list_floating_ips.assert_not_called()
