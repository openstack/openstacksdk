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

import copy
import testtools

import openstack
import openstack.cloud
from openstack.tests.unit import base


class TestNetwork(base.TestCase):

    mock_new_network_rep = {
        'provider:physical_network': None,
        'ipv6_address_scope': None,
        'revision_number': 3,
        'port_security_enabled': True,
        'provider:network_type': 'local',
        'id': '881d1bb7-a663-44c0-8f9f-ee2765b74486',
        'router:external': False,
        'availability_zone_hints': [],
        'availability_zones': [],
        'provider:segmentation_id': None,
        'ipv4_address_scope': None,
        'shared': False,
        'project_id': '861808a93da0484ea1767967c4df8a23',
        'status': 'ACTIVE',
        'subnets': [],
        'description': '',
        'tags': [],
        'updated_at': '2017-04-22T19:22:53Z',
        'is_default': False,
        'qos_policy_id': None,
        'name': 'netname',
        'admin_state_up': True,
        'tenant_id': '861808a93da0484ea1767967c4df8a23',
        'created_at': '2017-04-22T19:22:53Z',
        'mtu': 0,
        'dns_domain': 'sample.openstack.org.'
    }

    network_availability_zone_extension = {
        "alias": "network_availability_zone",
        "updated": "2015-01-01T10:00:00-00:00",
        "description": "Availability zone support for router.",
        "links": [],
        "name": "Network Availability Zone"
    }

    enabled_neutron_extensions = [network_availability_zone_extension]

    def test_list_networks(self):
        net1 = {'id': '1', 'name': 'net1'}
        net2 = {'id': '2', 'name': 'net2'}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [net1, net2]})
        ])
        nets = self.cloud.list_networks()
        self.assertEqual([net1, net2], nets)
        self.assert_calls()

    def test_list_networks_filtered(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json'],
                     qs_elements=["name=test"]),
                 json={'networks': []})
        ])
        self.cloud.list_networks(filters={'name': 'test'})
        self.assert_calls()

    def test_create_network(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'network': self.mock_new_network_rep},
                 validate=dict(
                     json={'network': {
                         'admin_state_up': True,
                         'name': 'netname'}}))
        ])
        network = self.cloud.create_network("netname")
        self.assertEqual(self.mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_specific_tenant(self):
        project_id = "project_id_value"
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep['project_id'] = project_id
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'network': mock_new_network_rep},
                 validate=dict(
                     json={'network': {
                         'admin_state_up': True,
                         'name': 'netname',
                         'tenant_id': project_id}}))
        ])
        network = self.cloud.create_network("netname", project_id=project_id)
        self.assertEqual(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_external(self):
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep['router:external'] = True
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'network': mock_new_network_rep},
                 validate=dict(
                     json={'network': {
                         'admin_state_up': True,
                         'name': 'netname',
                         'router:external': True}}))
        ])
        network = self.cloud.create_network("netname", external=True)
        self.assertEqual(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_provider(self):
        provider_opts = {'physical_network': 'mynet',
                         'network_type': 'vlan',
                         'segmentation_id': 'vlan1'}
        new_network_provider_opts = {
            'provider:physical_network': 'mynet',
            'provider:network_type': 'vlan',
            'provider:segmentation_id': 'vlan1'
        }
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep.update(new_network_provider_opts)
        expected_send_params = {
            'admin_state_up': True,
            'name': 'netname'
        }
        expected_send_params.update(new_network_provider_opts)
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'network': mock_new_network_rep},
                 validate=dict(
                     json={'network': expected_send_params}))
        ])
        network = self.cloud.create_network("netname", provider=provider_opts)
        self.assertEqual(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_with_availability_zone_hints(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'network': self.mock_new_network_rep},
                 validate=dict(
                     json={'network': {
                         'admin_state_up': True,
                         'name': 'netname',
                         'availability_zone_hints': ['nova']}}))
        ])
        network = self.cloud.create_network("netname",
                                            availability_zone_hints=['nova'])
        self.assertEqual(self.mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_provider_ignored_value(self):
        provider_opts = {'physical_network': 'mynet',
                         'network_type': 'vlan',
                         'segmentation_id': 'vlan1',
                         'should_not_be_passed': 1}
        new_network_provider_opts = {
            'provider:physical_network': 'mynet',
            'provider:network_type': 'vlan',
            'provider:segmentation_id': 'vlan1'
        }
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep.update(new_network_provider_opts)
        expected_send_params = {
            'admin_state_up': True,
            'name': 'netname'
        }
        expected_send_params.update(new_network_provider_opts)
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'network': mock_new_network_rep},
                 validate=dict(
                     json={'network': expected_send_params}))
        ])
        network = self.cloud.create_network("netname", provider=provider_opts)
        self.assertEqual(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_wrong_availability_zone_hints_type(self):
        azh_opts = "invalid"
        with testtools.ExpectedException(
            openstack.cloud.OpenStackCloudException,
            "Parameter 'availability_zone_hints' must be a list"
        ):
            self.cloud.create_network("netname",
                                      availability_zone_hints=azh_opts)

    def test_create_network_provider_wrong_type(self):
        provider_opts = "invalid"
        with testtools.ExpectedException(
            openstack.cloud.OpenStackCloudException,
            "Parameter 'provider' must be a dict"
        ):
            self.cloud.create_network("netname", provider=provider_opts)

    def test_create_network_port_security_disabled(self):
        port_security_state = False
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep['port_security_enabled'] = port_security_state
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'network': mock_new_network_rep},
                 validate=dict(
                     json={'network': {
                         'admin_state_up': True,
                         'name': 'netname',
                         'port_security_enabled': port_security_state}}))
        ])
        network = self.cloud.create_network(
            "netname",
            port_security_enabled=port_security_state
        )
        self.assertEqual(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_with_mtu(self):
        mtu_size = 1500
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep['mtu'] = mtu_size
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'network': mock_new_network_rep},
                 validate=dict(
                     json={'network': {
                         'admin_state_up': True,
                         'name': 'netname',
                         'mtu': mtu_size}}))
        ])
        network = self.cloud.create_network("netname",
                                            mtu_size=mtu_size
                                            )
        self.assertEqual(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_with_wrong_mtu_size(self):
        with testtools.ExpectedException(
                openstack.cloud.OpenStackCloudException,
                "Parameter 'mtu_size' must be greater than 67."
        ):
            self.cloud.create_network("netname", mtu_size=42)

    def test_create_network_with_wrong_mtu_type(self):
        with testtools.ExpectedException(
                openstack.cloud.OpenStackCloudException,
                "Parameter 'mtu_size' must be an integer."
        ):
            self.cloud.create_network("netname", mtu_size="fourty_two")

    def test_delete_network(self):
        network_id = "test-net-id"
        network_name = "network"
        network = {'id': network_id, 'name': network_name}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [network]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'networks', "%s.json" % network_id]),
                 json={})
        ])
        self.assertTrue(self.cloud.delete_network(network_name))
        self.assert_calls()

    def test_delete_network_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
        ])
        self.assertFalse(self.cloud.delete_network('test-net'))
        self.assert_calls()

    def test_delete_network_exception(self):
        network_id = "test-net-id"
        network_name = "network"
        network = {'id': network_id, 'name': network_name}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': [network]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'networks', "%s.json" % network_id]),
                 status_code=503)
        ])
        self.assertRaises(openstack.cloud.OpenStackCloudException,
                          self.cloud.delete_network, network_name)
        self.assert_calls()

    def test_get_network_by_id(self):
        network_id = "test-net-id"
        network_name = "network"
        network = {'id': network_id, 'name': network_name}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'networks', "%s" % network_id]),
                 json={'network': network})
        ])
        self.assertTrue(self.cloud.get_network_by_id(network_id))
        self.assert_calls()
