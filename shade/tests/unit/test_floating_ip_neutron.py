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

import mock
from mock import patch

from neutronclient.common import exceptions as n_exc

from shade import _utils
from shade import exc
from shade import meta
from shade import OpenStackCloud
from shade.tests import fakes
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

    mock_floating_ip_port_rep = {
        'floatingip': {
            'fixed_ip_address': '10.0.0.4',
            'floating_ip_address': '172.24.4.229',
            'floating_network_id': 'my-network-id',
            'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda8',
            'port_id': 'ce705c24-c1ef-408a-bda3-7bbd946164ab',
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

    mock_search_ports_rep = [
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
            'device_owner': 'compute:None',
            'mac_address': 'fa:16:3e:58:42:ed',
            'binding:profile': {},
            'binding:vnic_type': 'normal',
            'fixed_ips': [
                {
                    'subnet_id': '008ba151-0b8c-4a67-98b5-0d2b87666062',
                    'ip_address': u'172.24.4.2'
                }
            ],
            'id': 'ce705c24-c1ef-408a-bda3-7bbd946164ac',
            'security_groups': [],
            'device_id': 'server_id'
        }
    ]

    def assertAreInstances(self, elements, elem_type):
        for e in elements:
            self.assertIsInstance(e, elem_type)

    def setUp(self):
        super(TestFloatingIP, self).setUp()

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
            self.mock_floating_ip_list_rep['floatingips'])[0]

    def test_float_no_status(self):
        floating_ips = [
            {
                'fixed_ip_address': '10.0.0.4',
                'floating_ip_address': '172.24.4.229',
                'floating_network_id': 'my-network-id',
                'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda8',
                'port_id': None,
                'router_id': None,
                'tenant_id': '4969c491a3c74ee4af974e6d800c62df'
            }
        ]
        normalized = self.cloud._normalize_floating_ips(floating_ips)
        self.assertEqual('UNKNOWN', normalized[0]['status'])

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service', return_value=True)
    def test_list_floating_ips(self, mock_has_service, mock_neutron_client):
        mock_neutron_client.list_floatingips.return_value = \
            self.mock_floating_ip_list_rep

        floating_ips = self.cloud.list_floating_ips()

        mock_neutron_client.list_floatingips.assert_called_with()
        self.assertIsInstance(floating_ips, list)
        self.assertAreInstances(floating_ips, dict)
        self.assertEqual(2, len(floating_ips))

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service', return_value=True)
    def test_list_floating_ips_with_filters(self, mock_has_service,
                                            mock_neutron_client):
        mock_neutron_client.list_floatingips.side_effect = \
            exc.OpenStackCloudURINotFound("")

        try:
            self.cloud.list_floating_ips(filters={'Foo': 42})
        except exc.OpenStackCloudException as e:
            self.assertIsInstance(
                e.inner_exception[1], exc.OpenStackCloudURINotFound)

        mock_neutron_client.list_floatingips.assert_called_once_with(Foo=42)

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_search_floating_ips(self, mock_has_service, mock_neutron_client):
        mock_has_service.return_value = True
        mock_neutron_client.list_floatingips.return_value = \
            self.mock_floating_ip_list_rep

        floating_ips = self.cloud.search_floating_ips(
            filters={'attached': False})

        mock_neutron_client.list_floatingips.assert_called_with(attached=False)
        self.assertIsInstance(floating_ips, list)
        self.assertAreInstances(floating_ips, dict)
        self.assertEqual(1, len(floating_ips))

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_get_floating_ip(self, mock_has_service, mock_neutron_client):
        mock_has_service.return_value = True
        mock_neutron_client.list_floatingips.return_value = \
            self.mock_floating_ip_list_rep

        floating_ip = self.cloud.get_floating_ip(
            id='2f245a7b-796b-4f26-9cf9-9e82d248fda7')

        mock_neutron_client.list_floatingips.assert_called_with()
        self.assertIsInstance(floating_ip, dict)
        self.assertEqual('203.0.113.29', floating_ip['floating_ip_address'])
        self.assertEqual(
            self.mock_floating_ip_list_rep['floatingips'][0]['tenant_id'],
            floating_ip['project_id']
        )
        self.assertEqual(
            self.mock_floating_ip_list_rep['floatingips'][0]['tenant_id'],
            floating_ip['tenant_id']
        )
        self.assertIn('location', floating_ip)

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_get_floating_ip_not_found(
            self, mock_has_service, mock_neutron_client):
        mock_has_service.return_value = True
        mock_neutron_client.list_floatingips.return_value = \
            self.mock_floating_ip_list_rep

        floating_ip = self.cloud.get_floating_ip(id='non-existent')

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

        ip = self.cloud.create_floating_ip(network='my-network')

        mock_neutron_client.create_floatingip.assert_called_with(
            body={'floatingip': {'floating_network_id': 'my-network-id'}}
        )
        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['floating_ip_address'],
            ip['floating_ip_address'])

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'search_networks')
    @patch.object(OpenStackCloud, 'has_service')
    def test_create_floating_ip_port_bad_response(
            self, mock_has_service, mock_search_networks, mock_neutron_client):
        mock_has_service.return_value = True
        mock_search_networks.return_value = [self.mock_get_network_rep]
        mock_neutron_client.create_floatingip.return_value = \
            self.mock_floating_ip_new_rep

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_floating_ip,
            network='my-network', port='ce705c24-c1ef-408a-bda3-7bbd946164ab')

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'search_networks')
    @patch.object(OpenStackCloud, 'has_service')
    def test_create_floating_ip_port(
            self, mock_has_service, mock_search_networks, mock_neutron_client):
        mock_has_service.return_value = True
        mock_search_networks.return_value = [self.mock_get_network_rep]
        mock_neutron_client.create_floatingip.return_value = \
            self.mock_floating_ip_port_rep

        ip = self.cloud.create_floating_ip(
            network='my-network', port='ce705c24-c1ef-408a-bda3-7bbd946164ab')

        mock_neutron_client.create_floatingip.assert_called_with(
            body={'floatingip': {
                'floating_network_id': 'my-network-id',
                'port_id': 'ce705c24-c1ef-408a-bda3-7bbd946164ab',
            }}
        )
        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['floating_ip_address'],
            ip['floating_ip_address'])

    @patch.object(_utils, '_filter_list')
    @patch.object(OpenStackCloud, '_neutron_create_floating_ip')
    @patch.object(OpenStackCloud, '_neutron_list_floating_ips')
    @patch.object(OpenStackCloud, 'get_external_ipv4_floating_networks')
    @patch.object(OpenStackCloud, 'keystone_session')
    def test__neutron_available_floating_ips(
            self,
            mock_keystone_session,
            mock_get_ext_nets,
            mock__neutron_list_fips,
            mock__neutron_create_fip,
            mock__filter_list):
        """
        Test without specifying a network name.
        """
        mock_keystone_session.get_project_id.return_value = 'proj-id'
        mock_get_ext_nets.return_value = [self.mock_get_network_rep]
        mock__neutron_list_fips.return_value = []
        mock__filter_list.return_value = []

        # Test if first network is selected if no network is given
        self.cloud._neutron_available_floating_ips()

        mock_keystone_session.get_project_id.assert_called_once_with()
        mock_get_ext_nets.assert_called_once_with()
        mock__neutron_list_fips.assert_called_once_with(None)
        mock__filter_list.assert_called_once_with(
            [], name_or_id=None,
            filters={'port_id': None,
                     'floating_network_id': self.mock_get_network_rep['id'],
                     'tenant_id': 'proj-id'}
        )
        mock__neutron_create_fip.assert_called_once_with(
            network_id=self.mock_get_network_rep['id'],
            server=None
        )

    @patch.object(_utils, '_filter_list')
    @patch.object(OpenStackCloud, '_neutron_create_floating_ip')
    @patch.object(OpenStackCloud, '_neutron_list_floating_ips')
    @patch.object(OpenStackCloud, 'get_external_ipv4_floating_networks')
    @patch.object(OpenStackCloud, 'keystone_session')
    def test__neutron_available_floating_ips_network(
            self,
            mock_keystone_session,
            mock_get_ext_nets,
            mock__neutron_list_fips,
            mock__neutron_create_fip,
            mock__filter_list):
        """
        Test with specifying a network name.
        """
        mock_keystone_session.get_project_id.return_value = 'proj-id'
        mock_get_ext_nets.return_value = [self.mock_get_network_rep]
        mock__neutron_list_fips.return_value = []
        mock__filter_list.return_value = []

        self.cloud._neutron_available_floating_ips(
            network=self.mock_get_network_rep['name']
        )

        mock_keystone_session.get_project_id.assert_called_once_with()
        mock_get_ext_nets.assert_called_once_with()
        mock__neutron_list_fips.assert_called_once_with(None)
        mock__filter_list.assert_called_once_with(
            [], name_or_id=None,
            filters={'port_id': None,
                     'floating_network_id': self.mock_get_network_rep['id'],
                     'tenant_id': 'proj-id'}
        )
        mock__neutron_create_fip.assert_called_once_with(
            network_id=self.mock_get_network_rep['id'],
            server=None
        )

    @patch.object(OpenStackCloud, 'get_external_ipv4_networks')
    @patch.object(OpenStackCloud, 'keystone_session')
    def test__neutron_available_floating_ips_invalid_network(
            self,
            mock_keystone_session,
            mock_get_ext_nets):
        """
        Test with an invalid network name.
        """
        mock_keystone_session.get_project_id.return_value = 'proj-id'
        mock_get_ext_nets.return_value = []
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud._neutron_available_floating_ips,
                          network='INVALID')

    @patch.object(OpenStackCloud, 'nova_client')
    @patch.object(OpenStackCloud, 'keystone_session')
    @patch.object(OpenStackCloud, '_neutron_create_floating_ip')
    @patch.object(OpenStackCloud, '_attach_ip_to_server')
    @patch.object(OpenStackCloud, 'has_service')
    def test_auto_ip_pool_no_reuse(
            self, mock_has_service,
            mock_attach_ip_to_server,
            mock__neutron_create_floating_ip,
            mock_keystone_session,
            mock_nova_client):
        mock_has_service.return_value = True
        fip = self.cloud._normalize_floating_ips(
            self.mock_floating_ip_list_rep['floatingips'])[0]
        mock__neutron_create_floating_ip.return_value = fip
        mock_keystone_session.get_project_id.return_value = \
            '4969c491a3c74ee4af974e6d800c62df'
        fake_server = meta.obj_to_dict(fakes.FakeServer('1234', '', 'ACTIVE'))

        self.cloud.add_ips_to_server(
            fake_server, ip_pool='my-network', reuse=False)

        mock__neutron_create_floating_ip.assert_called_once_with(
            network_name_or_id='my-network', server=None, port=None,
            fixed_address=None, nat_destination=None, wait=False, timeout=60)
        mock_attach_ip_to_server.assert_called_once_with(
            server=fake_server, fixed_address=None,
            floating_ip=fip, wait=False, timeout=mock.ANY)

    @patch.object(OpenStackCloud, 'keystone_session')
    @patch.object(OpenStackCloud, '_neutron_create_floating_ip')
    @patch.object(OpenStackCloud, '_neutron_list_floating_ips')
    @patch.object(OpenStackCloud, 'list_networks')
    @patch.object(OpenStackCloud, 'has_service')
    def test_available_floating_ip_new(
            self, mock_has_service, mock_list_networks,
            mock__neutron_list_floating_ips,
            mock__neutron_create_floating_ip, mock_keystone_session):
        mock_has_service.return_value = True
        mock_list_networks.return_value = [self.mock_get_network_rep]
        mock__neutron_list_floating_ips.return_value = []
        mock__neutron_create_floating_ip.return_value = \
            self.mock_floating_ip_new_rep['floatingip']
        mock_keystone_session.get_project_id.return_value = \
            '4969c491a3c74ee4af974e6d800c62df'

        ip = self.cloud.available_floating_ip(network='my-network')

        self.assertEqual(
            self.mock_floating_ip_new_rep['floatingip']['floating_ip_address'],
            ip['floating_ip_address'])

    @patch.object(OpenStackCloud, 'get_floating_ip')
    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_delete_floating_ip_existing(
            self, mock_has_service, mock_neutron_client, mock_get_floating_ip):
        mock_has_service.return_value = True
        fake_fip = {
            'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
            'floating_ip_address': '172.99.106.167',
            'status': 'ACTIVE',
        }

        mock_get_floating_ip.side_effect = [fake_fip, fake_fip, None]
        mock_neutron_client.delete_floatingip.return_value = None

        ret = self.cloud.delete_floating_ip(
            floating_ip_id='2f245a7b-796b-4f26-9cf9-9e82d248fda7',
            retry=2)

        mock_neutron_client.delete_floatingip.assert_called_with(
            floatingip='2f245a7b-796b-4f26-9cf9-9e82d248fda7'
        )
        self.assertEqual(mock_get_floating_ip.call_count, 3)
        self.assertTrue(ret)

    @patch.object(OpenStackCloud, 'get_floating_ip')
    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_delete_floating_ip_existing_down(
            self, mock_has_service, mock_neutron_client, mock_get_floating_ip):
        mock_has_service.return_value = True
        fake_fip = {
            'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
            'floating_ip_address': '172.99.106.167',
            'status': 'ACTIVE',
        }
        down_fip = {
            'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
            'floating_ip_address': '172.99.106.167',
            'status': 'DOWN',
        }

        mock_get_floating_ip.side_effect = [fake_fip, down_fip, None]
        mock_neutron_client.delete_floatingip.return_value = None

        ret = self.cloud.delete_floating_ip(
            floating_ip_id='2f245a7b-796b-4f26-9cf9-9e82d248fda7',
            retry=2)

        mock_neutron_client.delete_floatingip.assert_called_with(
            floatingip='2f245a7b-796b-4f26-9cf9-9e82d248fda7'
        )
        self.assertEqual(mock_get_floating_ip.call_count, 2)
        self.assertTrue(ret)

    @patch.object(OpenStackCloud, 'get_floating_ip')
    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_delete_floating_ip_existing_no_delete(
            self, mock_has_service, mock_neutron_client, mock_get_floating_ip):
        mock_has_service.return_value = True
        fake_fip = {
            'id': '2f245a7b-796b-4f26-9cf9-9e82d248fda7',
            'floating_ip_address': '172.99.106.167',
            'status': 'ACTIVE',
        }

        mock_get_floating_ip.side_effect = [fake_fip, fake_fip, fake_fip]
        mock_neutron_client.delete_floatingip.return_value = None

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.delete_floating_ip,
            floating_ip_id='2f245a7b-796b-4f26-9cf9-9e82d248fda7',
            retry=2)

        mock_neutron_client.delete_floatingip.assert_called_with(
            floatingip='2f245a7b-796b-4f26-9cf9-9e82d248fda7'
        )
        self.assertEqual(mock_get_floating_ip.call_count, 3)

    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_delete_floating_ip_not_found(
            self, mock_has_service, mock_neutron_client):
        mock_has_service.return_value = True
        mock_neutron_client.delete_floatingip.side_effect = \
            n_exc.NotFound()

        ret = self.cloud.delete_floating_ip(
            floating_ip_id='a-wild-id-appears')

        self.assertFalse(ret)

    @patch.object(OpenStackCloud, 'search_ports')
    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_attach_ip_to_server(
            self, mock_has_service, mock_neutron_client, mock_search_ports):
        mock_has_service.return_value = True

        mock_search_ports.return_value = self.mock_search_ports_rep

        mock_neutron_client.list_floatingips.return_value = \
            self.mock_floating_ip_list_rep

        self.cloud._attach_ip_to_server(
            server=self.fake_server,
            floating_ip=self.floating_ip)

        mock_neutron_client.update_floatingip.assert_called_with(
            floatingip=self.mock_floating_ip_list_rep['floatingips'][0]['id'],
            body={
                'floatingip': {
                    'port_id': self.mock_search_ports_rep[0]['id'],
                    'fixed_ip_address': self.mock_search_ports_rep[0][
                        'fixed_ips'][0]['ip_address']
                }
            }
        )

    @patch.object(OpenStackCloud, 'delete_floating_ip')
    @patch.object(OpenStackCloud, 'get_server')
    @patch.object(OpenStackCloud, 'create_floating_ip')
    @patch.object(OpenStackCloud, 'has_service')
    def test_add_ip_refresh_timeout(
            self, mock_has_service, mock_create_floating_ip,
            mock_get_server, mock_delete_floating_ip):
        mock_has_service.return_value = True

        mock_create_floating_ip.return_value = self.floating_ip
        mock_get_server.return_value = self.fake_server

        self.assertRaises(
            exc.OpenStackCloudTimeout,
            self.cloud._add_auto_ip,
            server=self.fake_server,
            wait=True, timeout=0.01,
            reuse=False)

        mock_delete_floating_ip.assert_called_once_with(
            self.floating_ip['id'])

    @patch.object(OpenStackCloud, 'get_floating_ip')
    @patch.object(OpenStackCloud, 'neutron_client')
    @patch.object(OpenStackCloud, 'has_service')
    def test_detach_ip_from_server(
            self, mock_has_service, mock_neutron_client,
            mock_get_floating_ip):
        mock_has_service.return_value = True
        mock_get_floating_ip.return_value = \
            self.cloud._normalize_floating_ips(
                self.mock_floating_ip_list_rep['floatingips'])[0]

        self.cloud.detach_ip_from_server(
            server_id='server-id',
            floating_ip_id='2f245a7b-796b-4f26-9cf9-9e82d248fda7')

        mock_neutron_client.update_floatingip.assert_called_with(
            floatingip='2f245a7b-796b-4f26-9cf9-9e82d248fda7',
            body={
                'floatingip': {
                    'port_id': None
                }
            }
        )

    @patch.object(OpenStackCloud, '_attach_ip_to_server')
    @patch.object(OpenStackCloud, 'available_floating_ip')
    @patch.object(OpenStackCloud, 'has_service')
    def test_add_ip_from_pool(
            self, mock_has_service, mock_available_floating_ip,
            mock_attach_ip_to_server):
        mock_has_service.return_value = True
        mock_available_floating_ip.return_value = \
            self.cloud._normalize_floating_ips([
                self.mock_floating_ip_new_rep['floatingip']])[0]
        mock_attach_ip_to_server.return_value = self.fake_server

        server = self.cloud._add_ip_from_pool(
            server=self.fake_server,
            network='network-name',
            fixed_address='192.0.2.129')

        self.assertEqual(server, self.fake_server)

    @patch.object(OpenStackCloud, 'delete_floating_ip')
    @patch.object(OpenStackCloud, 'list_floating_ips')
    @patch.object(OpenStackCloud, '_use_neutron_floating')
    def test_cleanup_floating_ips(
            self, mock_use_neutron_floating, mock_list_floating_ips,
            mock_delete_floating_ip):
        mock_use_neutron_floating.return_value = True
        floating_ips = [{
            "id": "this-is-a-floating-ip-id",
            "fixed_ip_address": None,
            "internal_network": None,
            "floating_ip_address": "203.0.113.29",
            "network": "this-is-a-net-or-pool-id",
            "attached": False,
            "status": "ACTIVE"
        }, {
            "id": "this-is-an-attached-floating-ip-id",
            "fixed_ip_address": None,
            "internal_network": None,
            "floating_ip_address": "203.0.113.29",
            "network": "this-is-a-net-or-pool-id",
            "attached": True,
            "status": "ACTIVE"
        }]

        mock_list_floating_ips.return_value = floating_ips

        self.cloud.delete_unattached_floating_ips()

        mock_delete_floating_ip.assert_called_once_with(
            floating_ip_id='this-is-a-floating-ip-id', retry=1)

    @patch.object(OpenStackCloud, '_submit_create_fip')
    @patch.object(OpenStackCloud, '_nat_destination_port')
    @patch.object(OpenStackCloud, 'get_external_ipv4_networks')
    def test_create_floating_ip_no_port(
            self, mock_get_ext_nets, mock_nat_destination_port,
            mock_submit_create_fip):
        fake_port = dict(id='port-id')
        mock_get_ext_nets.return_value = [self.mock_get_network_rep]
        mock_nat_destination_port.return_value = (fake_port, '10.0.0.2')
        mock_submit_create_fip.return_value = dict(port_id=None)

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud._neutron_create_floating_ip,
            server=dict(id='some-server'))
