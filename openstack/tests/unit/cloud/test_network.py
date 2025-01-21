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
from unittest import mock

import testtools

from openstack import exceptions
from openstack.network.v2 import network as _network
from openstack.tests.unit import base


class TestNeutronExtensions(base.TestCase):
    def test__neutron_extensions(self):
        body = [
            {
                "updated": "2014-06-1T10:00:00-00:00",
                "name": "Distributed Virtual Router",
                "links": [],
                "alias": "dvr",
                "description": "Enables configuration of Distributed Virtual Routers.",  # noqa: E501
            },
            {
                "updated": "2013-07-23T10:00:00-00:00",
                "name": "Allowed Address Pairs",
                "links": [],
                "alias": "allowed-address-pairs",
                "description": "Provides allowed address pairs",
            },
        ]
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json=dict(extensions=body),
                )
            ]
        )
        extensions = self.cloud._neutron_extensions()
        self.assertEqual({'dvr', 'allowed-address-pairs'}, extensions)

        self.assert_calls()

    def test__neutron_extensions_fails(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    status_code=404,
                )
            ]
        )
        with testtools.ExpectedException(exceptions.NotFoundException):
            self.cloud._neutron_extensions()

        self.assert_calls()

    def test__has_neutron_extension(self):
        body = [
            {
                "updated": "2014-06-1T10:00:00-00:00",
                "name": "Distributed Virtual Router",
                "links": [],
                "alias": "dvr",
                "description": "Enables configuration of Distributed Virtual Routers.",  # noqa: E501
            },
            {
                "updated": "2013-07-23T10:00:00-00:00",
                "name": "Allowed Address Pairs",
                "links": [],
                "alias": "allowed-address-pairs",
                "description": "Provides allowed address pairs",
            },
        ]
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json=dict(extensions=body),
                )
            ]
        )
        self.assertTrue(self.cloud._has_neutron_extension('dvr'))
        self.assert_calls()

    def test__has_neutron_extension_missing(self):
        body = [
            {
                "updated": "2014-06-1T10:00:00-00:00",
                "name": "Distributed Virtual Router",
                "links": [],
                "alias": "dvr",
                "description": "Enables configuration of Distributed Virtual Routers.",  # noqa: E501
            },
            {
                "updated": "2013-07-23T10:00:00-00:00",
                "name": "Allowed Address Pairs",
                "links": [],
                "alias": "allowed-address-pairs",
                "description": "Provides allowed address pairs",
            },
        ]
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json=dict(extensions=body),
                )
            ]
        )
        self.assertFalse(self.cloud._has_neutron_extension('invalid'))
        self.assert_calls()


class TestNetworks(base.TestCase):
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
        'created_at': '2017-04-22T19:22:53Z',
        'mtu': 0,
        'dns_domain': 'sample.openstack.org.',
        'vlan_transparent': None,
        'vlan_qinq': None,
        'segments': None,
    }

    network_availability_zone_extension = {
        "alias": "network_availability_zone",
        "updated": "2015-01-01T10:00:00-00:00",
        "description": "Availability zone support for router.",
        "links": [],
        "name": "Network Availability Zone",
    }

    enabled_neutron_extensions = [network_availability_zone_extension]

    def _compare_networks(self, exp, real):
        self.assertDictEqual(
            _network.Network(**exp).to_dict(computed=False),
            real.to_dict(computed=False),
        )

    def test_list_networks(self):
        net1 = {'id': '1', 'name': 'net1'}
        net2 = {'id': '2', 'name': 'net2'}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'networks': [net1, net2]},
                )
            ]
        )
        nets = self.cloud.list_networks()
        self.assertEqual(
            [
                _network.Network(**i).to_dict(computed=False)
                for i in [net1, net2]
            ],
            [i.to_dict(computed=False) for i in nets],
        )
        self.assert_calls()

    def test_list_networks_filtered(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks'],
                        qs_elements=["name=test"],
                    ),
                    json={'networks': []},
                )
            ]
        )
        self.cloud.list_networks(filters={'name': 'test'})
        self.assert_calls()

    def test_list_networks_neutron_not_found(self):
        self.use_nothing()
        self.cloud.has_service = mock.Mock(return_value=False)
        self.assertEqual([], self.cloud.list_networks())
        self.assert_calls()

    def test_create_network(self):
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'network': self.mock_new_network_rep},
                    validate=dict(
                        json={
                            'network': {
                                'admin_state_up': True,
                                'name': 'netname',
                            }
                        }
                    ),
                )
            ]
        )
        network = self.cloud.create_network("netname")
        self._compare_networks(self.mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_specific_tenant(self):
        project_id = "project_id_value"
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep['project_id'] = project_id
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'network': mock_new_network_rep},
                    validate=dict(
                        json={
                            'network': {
                                'admin_state_up': True,
                                'name': 'netname',
                                'project_id': project_id,
                            }
                        }
                    ),
                )
            ]
        )
        network = self.cloud.create_network("netname", project_id=project_id)
        self._compare_networks(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_external(self):
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep['router:external'] = True
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'network': mock_new_network_rep},
                    validate=dict(
                        json={
                            'network': {
                                'admin_state_up': True,
                                'name': 'netname',
                                'router:external': True,
                            }
                        }
                    ),
                )
            ]
        )
        network = self.cloud.create_network("netname", external=True)
        self._compare_networks(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_provider(self):
        provider_opts = {
            'physical_network': 'mynet',
            'network_type': 'vlan',
            'segmentation_id': 'vlan1',
        }
        new_network_provider_opts = {
            'provider:physical_network': 'mynet',
            'provider:network_type': 'vlan',
            'provider:segmentation_id': 'vlan1',
        }
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep.update(new_network_provider_opts)
        expected_send_params = {'admin_state_up': True, 'name': 'netname'}
        expected_send_params.update(new_network_provider_opts)
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'network': mock_new_network_rep},
                    validate=dict(json={'network': expected_send_params}),
                )
            ]
        )
        network = self.cloud.create_network("netname", provider=provider_opts)
        self._compare_networks(mock_new_network_rep, network)
        self.assert_calls()

    def test_update_network_provider(self):
        network_id = "test-net-id"
        network_name = "network"
        network = {'id': network_id, 'name': network_name}
        provider_opts = {
            'physical_network': 'mynet',
            'network_type': 'vlan',
            'segmentation_id': 'vlan1',
            'should_not_be_passed': 1,
        }
        update_network_provider_opts = {
            'provider:physical_network': 'mynet',
            'provider:network_type': 'vlan',
            'provider:segmentation_id': 'vlan1',
        }
        mock_update_rep = copy.copy(self.mock_new_network_rep)
        mock_update_rep.update(update_network_provider_opts)
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', network_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks'],
                        qs_elements=[f'name={network_name}'],
                    ),
                    json={'networks': [network]},
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', network_id],
                    ),
                    json={'network': mock_update_rep},
                    validate=dict(
                        json={'network': update_network_provider_opts}
                    ),
                ),
            ]
        )
        network = self.cloud.update_network(
            network_name, provider=provider_opts
        )
        self._compare_networks(mock_update_rep, network)
        self.assert_calls()

    def test_create_network_with_availability_zone_hints(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': self.enabled_neutron_extensions},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'network': self.mock_new_network_rep},
                    validate=dict(
                        json={
                            'network': {
                                'admin_state_up': True,
                                'name': 'netname',
                                'availability_zone_hints': ['nova'],
                            }
                        }
                    ),
                ),
            ]
        )
        network = self.cloud.create_network(
            "netname", availability_zone_hints=['nova']
        )
        self._compare_networks(self.mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_provider_ignored_value(self):
        provider_opts = {
            'physical_network': 'mynet',
            'network_type': 'vlan',
            'segmentation_id': 'vlan1',
            'should_not_be_passed': 1,
        }
        new_network_provider_opts = {
            'provider:physical_network': 'mynet',
            'provider:network_type': 'vlan',
            'provider:segmentation_id': 'vlan1',
        }
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep.update(new_network_provider_opts)
        expected_send_params = {'admin_state_up': True, 'name': 'netname'}
        expected_send_params.update(new_network_provider_opts)
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'network': mock_new_network_rep},
                    validate=dict(json={'network': expected_send_params}),
                )
            ]
        )
        network = self.cloud.create_network("netname", provider=provider_opts)
        self._compare_networks(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_wrong_availability_zone_hints_type(self):
        azh_opts = "invalid"
        with testtools.ExpectedException(
            exceptions.SDKException,
            "Parameter 'availability_zone_hints' must be a list",
        ):
            self.cloud.create_network(
                "netname", availability_zone_hints=azh_opts
            )

    def test_create_network_provider_wrong_type(self):
        provider_opts = "invalid"
        with testtools.ExpectedException(
            exceptions.SDKException,
            "Parameter 'provider' must be a dict",
        ):
            self.cloud.create_network("netname", provider=provider_opts)

    def test_create_network_port_security_disabled(self):
        port_security_state = False
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep['port_security_enabled'] = port_security_state
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'network': mock_new_network_rep},
                    validate=dict(
                        json={
                            'network': {
                                'admin_state_up': True,
                                'name': 'netname',
                                'port_security_enabled': port_security_state,
                            }
                        }
                    ),
                )
            ]
        )
        network = self.cloud.create_network(
            "netname", port_security_enabled=port_security_state
        )
        self._compare_networks(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_with_mtu(self):
        mtu_size = 1500
        mock_new_network_rep = copy.copy(self.mock_new_network_rep)
        mock_new_network_rep['mtu'] = mtu_size
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'networks']
                    ),
                    json={'network': mock_new_network_rep},
                    validate=dict(
                        json={
                            'network': {
                                'admin_state_up': True,
                                'name': 'netname',
                                'mtu': mtu_size,
                            }
                        }
                    ),
                )
            ]
        )
        network = self.cloud.create_network("netname", mtu_size=mtu_size)
        self._compare_networks(mock_new_network_rep, network)
        self.assert_calls()

    def test_create_network_with_wrong_mtu_size(self):
        with testtools.ExpectedException(
            exceptions.SDKException,
            "Parameter 'mtu_size' must be greater than 67.",
        ):
            self.cloud.create_network("netname", mtu_size=42)

    def test_create_network_with_wrong_mtu_type(self):
        with testtools.ExpectedException(
            exceptions.SDKException,
            "Parameter 'mtu_size' must be an integer.",
        ):
            self.cloud.create_network("netname", mtu_size="fourty_two")

    def test_delete_network(self):
        network_id = "test-net-id"
        network_name = "network"
        network = {'id': network_id, 'name': network_name}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', network_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks'],
                        qs_elements=[f'name={network_name}'],
                    ),
                    json={'networks': [network]},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', network_id],
                    ),
                    json={},
                ),
            ]
        )
        self.assertTrue(self.cloud.delete_network(network_name))
        self.assert_calls()

    def test_delete_network_not_found(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', 'test-net'],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks'],
                        qs_elements=['name=test-net'],
                    ),
                    json={'networks': []},
                ),
            ]
        )
        self.assertFalse(self.cloud.delete_network('test-net'))
        self.assert_calls()

    def test_delete_network_exception(self):
        network_id = "test-net-id"
        network_name = "network"
        network = {'id': network_id, 'name': network_name}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', network_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks'],
                        qs_elements=[f'name={network_name}'],
                    ),
                    json={'networks': [network]},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', network_id],
                    ),
                    status_code=503,
                ),
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.delete_network,
            network_name,
        )
        self.assert_calls()

    def test_get_network_by_id(self):
        network_id = "test-net-id"
        network_name = "network"
        network = {'id': network_id, 'name': network_name}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'networks', network_id],
                    ),
                    json={'network': network},
                )
            ]
        )
        self.assertTrue(self.cloud.get_network_by_id(network_id))
        self.assert_calls()
