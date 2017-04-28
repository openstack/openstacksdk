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

import testtools

from openstack.network.v2 import network

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'availability_zone_hints': ['1', '2'],
    'availability_zones': ['3'],
    'created_at': '2016-03-09T12:14:57.233772',
    'description': '4',
    'dns_domain': '5',
    'id': IDENTIFIER,
    'ipv4_address_scope': '6',
    'ipv6_address_scope': '7',
    'is_default': False,
    'mtu': 8,
    'name': '9',
    'port_security_enabled': True,
    'project_id': '10',
    'provider:network_type': '11',
    'provider:physical_network': '12',
    'provider:segmentation_id': '13',
    'qos_policy_id': '14',
    'revision_number': 15,
    'router:external': True,
    'segments': '16',
    'shared': True,
    'status': '17',
    'subnets': ['18', '19'],
    'updated_at': '2016-07-09T12:14:57.233772',
    'vlan_transparent': False,
}


class TestNetwork(testtools.TestCase):

    def test_basic(self):
        sot = network.Network()
        self.assertEqual('network', sot.resource_key)
        self.assertEqual('networks', sot.resources_key)
        self.assertEqual('/networks', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = network.Network(**EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['availability_zone_hints'],
                         sot.availability_zone_hints)
        self.assertEqual(EXAMPLE['availability_zones'],
                         sot.availability_zones)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['dns_domain'], sot.dns_domain)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['ipv4_address_scope'],
                         sot.ipv4_address_scope_id)
        self.assertEqual(EXAMPLE['ipv6_address_scope'],
                         sot.ipv6_address_scope_id)
        self.assertFalse(sot.is_default)
        self.assertEqual(EXAMPLE['mtu'], sot.mtu)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertTrue(sot.is_port_security_enabled)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['provider:network_type'],
                         sot.provider_network_type)
        self.assertEqual(EXAMPLE['provider:physical_network'],
                         sot.provider_physical_network)
        self.assertEqual(EXAMPLE['provider:segmentation_id'],
                         sot.provider_segmentation_id)
        self.assertEqual(EXAMPLE['qos_policy_id'], sot.qos_policy_id)
        self.assertEqual(EXAMPLE['revision_number'], sot.revision_number)
        self.assertTrue(sot.is_router_external)
        self.assertEqual(EXAMPLE['segments'], sot.segments)
        self.assertTrue(sot.is_shared)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['subnets'], sot.subnet_ids)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['vlan_transparent'], sot.is_vlan_transparent)

        self.assertDictEqual(
            {'limit': 'limit',
             'marker': 'marker',
             'description': 'description',
             'name': 'name',
             'project_id': 'project_id',
             'status': 'status',
             'ipv4_address_scope_id': 'ipv4_address_scope',
             'ipv6_address_scope_id': 'ipv6_address_scope',
             'is_admin_state_up': 'admin_state_up',
             'is_port_security_enabled': 'port_security_enabled',
             'is_router_external': 'router:external',
             'is_shared': 'shared',
             'provider_network_type': 'provider:network_type',
             'provider_physical_network': 'provider:physical_network',
             'provider_segmentation_id': 'provider:segmentation_id',
             'tags': 'tags',
             'any_tags': 'tags-any',
             'not_tags': 'not-tags',
             'not_any_tags': 'not-tags-any',
             },
            sot._query_mapping._mapping)


class TestDHCPAgentHostingNetwork(testtools.TestCase):

    def test_basic(self):
        net = network.DHCPAgentHostingNetwork()
        self.assertEqual('network', net.resource_key)
        self.assertEqual('networks', net.resources_key)
        self.assertEqual('/agents/%(agent_id)s/dhcp-networks', net.base_path)
        self.assertEqual('dhcp-network', net.resource_name)
        self.assertEqual('network', net.service.service_type)
        self.assertFalse(net.allow_create)
        self.assertTrue(net.allow_get)
        self.assertFalse(net.allow_update)
        self.assertFalse(net.allow_delete)
        self.assertTrue(net.allow_list)
