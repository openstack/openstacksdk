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
test_port
----------------------------------

Test port resource (managed by neutron)
"""

from openstack.cloud.exc import OpenStackCloudException
from openstack.tests.unit import base


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

    def test_create_port(self):
        self.register_uris([
            dict(method="POST",
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json=self.mock_neutron_port_create_rep,
                 validate=dict(
                     json={'port': {
                         'network_id': 'test-net-id',
                         'name': 'test-port-name',
                         'admin_state_up': True}}))
        ])
        port = self.cloud.create_port(
            network_id='test-net-id', name='test-port-name',
            admin_state_up=True)
        self.assertEqual(self.mock_neutron_port_create_rep['port'], port)
        self.assert_calls()

    def test_create_port_parameters(self):
        """Test that we detect invalid arguments passed to create_port"""
        self.assertRaises(
            TypeError, self.cloud.create_port,
            network_id='test-net-id', nome='test-port-name',
            stato_amministrativo_porta=True)

    def test_create_port_exception(self):
        self.register_uris([
            dict(method="POST",
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 status_code=500,
                 validate=dict(
                     json={'port': {
                         'network_id': 'test-net-id',
                         'name': 'test-port-name',
                         'admin_state_up': True}}))
        ])
        self.assertRaises(
            OpenStackCloudException, self.cloud.create_port,
            network_id='test-net-id', name='test-port-name',
            admin_state_up=True)
        self.assert_calls()

    def test_update_port(self):
        port_id = 'd80b1a3b-4fc1-49f3-952e-1e2ab7081d8b'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json=self.mock_neutron_port_list_rep),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'ports', '%s.json' % port_id]),
                 json=self.mock_neutron_port_update_rep,
                 validate=dict(
                     json={'port': {'name': 'test-port-name-updated'}}))
        ])
        port = self.cloud.update_port(
            name_or_id=port_id, name='test-port-name-updated')

        self.assertEqual(self.mock_neutron_port_update_rep['port'], port)
        self.assert_calls()

    def test_update_port_parameters(self):
        """Test that we detect invalid arguments passed to update_port"""
        self.assertRaises(
            TypeError, self.cloud.update_port,
            name_or_id='test-port-id', nome='test-port-name-updated')

    def test_update_port_exception(self):
        port_id = 'd80b1a3b-4fc1-49f3-952e-1e2ab7081d8b'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json=self.mock_neutron_port_list_rep),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'ports', '%s.json' % port_id]),
                 status_code=500,
                 validate=dict(
                     json={'port': {'name': 'test-port-name-updated'}}))
        ])
        self.assertRaises(
            OpenStackCloudException, self.cloud.update_port,
            name_or_id='d80b1a3b-4fc1-49f3-952e-1e2ab7081d8b',
            name='test-port-name-updated')
        self.assert_calls()

    def test_list_ports(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json=self.mock_neutron_port_list_rep)
        ])
        ports = self.cloud.list_ports()
        self.assertCountEqual(self.mock_neutron_port_list_rep['ports'], ports)
        self.assert_calls()

    def test_list_ports_filtered(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json'],
                     qs_elements=['status=DOWN']),
                 json=self.mock_neutron_port_list_rep)
        ])
        ports = self.cloud.list_ports(filters={'status': 'DOWN'})
        self.assertCountEqual(self.mock_neutron_port_list_rep['ports'], ports)
        self.assert_calls()

    def test_list_ports_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 status_code=500)
        ])
        self.assertRaises(OpenStackCloudException, self.cloud.list_ports)

    def test_search_ports_by_id(self):
        port_id = 'f71a6703-d6de-4be1-a91a-a570ede1d159'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json=self.mock_neutron_port_list_rep)
        ])
        ports = self.cloud.search_ports(name_or_id=port_id)

        self.assertEqual(1, len(ports))
        self.assertEqual('fa:16:3e:bb:3c:e4', ports[0]['mac_address'])
        self.assert_calls()

    def test_search_ports_by_name(self):
        port_name = "first-port"
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json=self.mock_neutron_port_list_rep)
        ])
        ports = self.cloud.search_ports(name_or_id=port_name)

        self.assertEqual(1, len(ports))
        self.assertEqual('fa:16:3e:58:42:ed', ports[0]['mac_address'])
        self.assert_calls()

    def test_search_ports_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json=self.mock_neutron_port_list_rep)
        ])
        ports = self.cloud.search_ports(name_or_id='non-existent')
        self.assertEqual(0, len(ports))
        self.assert_calls()

    def test_delete_port(self):
        port_id = 'd80b1a3b-4fc1-49f3-952e-1e2ab7081d8b'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json=self.mock_neutron_port_list_rep),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'ports', '%s.json' % port_id]),
                 json={})
        ])

        self.assertTrue(self.cloud.delete_port(name_or_id='first-port'))

    def test_delete_port_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json=self.mock_neutron_port_list_rep)
        ])
        self.assertFalse(self.cloud.delete_port(name_or_id='non-existent'))
        self.assert_calls()

    def test_delete_subnet_multiple_found(self):
        port_name = "port-name"
        port1 = dict(id='123', name=port_name)
        port2 = dict(id='456', name=port_name)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json={'ports': [port1, port2]})
        ])
        self.assertRaises(OpenStackCloudException,
                          self.cloud.delete_port, port_name)
        self.assert_calls()

    def test_delete_subnet_multiple_using_id(self):
        port_name = "port-name"
        port1 = dict(id='123', name=port_name)
        port2 = dict(id='456', name=port_name)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'ports.json']),
                 json={'ports': [port1, port2]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'ports', '%s.json' % port1['id']]),
                 json={})
        ])
        self.assertTrue(self.cloud.delete_port(name_or_id=port1['id']))
        self.assert_calls()

    def test_get_port_by_id(self):
        fake_port = dict(id='123', name='456')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0',
                                                  'ports',
                                                  fake_port['id']]),
                 json={'port': fake_port})
        ])
        r = self.cloud.get_port_by_id(fake_port['id'])
        self.assertIsNotNone(r)
        self.assertDictEqual(fake_port, r)
        self.assert_calls()
