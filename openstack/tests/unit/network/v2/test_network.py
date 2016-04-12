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

import datetime

import testtools

from openstack.network.v2 import network

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'id': IDENTIFIER,
    'name': '3',
    'tenant_id': '4',
    'provider:network_type': '5',
    'provider:physical_network': '6',
    'provider:segmentation_id': '7',
    'router:external': True,
    'segments': '9',
    'shared': True,
    'status': '11',
    'subnets': ['12a', '12b'],
    'mtu': 1400,
    'port_security_enabled': True,
    'availability_zone_hints': ['15', '16'],
    'availability_zones': ['16'],
    'ipv4_address_scope': '17',
    'ipv6_address_scope': '18',
    'description': '19',
    'created_at': '2016-03-09T12:14:57.233772',
    'updated_at': '2016-07-09T12:14:57.233772',
    'is_default': False,
}


class TestNetwork(testtools.TestCase):

    def test_basic(self):
        sot = network.Network()
        self.assertEqual('network', sot.resource_key)
        self.assertEqual('networks', sot.resources_key)
        self.assertEqual('/networks', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = network.Network(EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['provider:network_type'],
                         sot.provider_network_type)
        self.assertEqual(EXAMPLE['provider:physical_network'],
                         sot.provider_physical_network)
        self.assertEqual(EXAMPLE['provider:segmentation_id'],
                         sot.provider_segmentation_id)
        self.assertTrue(sot.is_router_external)
        self.assertEqual(EXAMPLE['segments'], sot.segments)
        self.assertTrue(sot.is_shared)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['subnets'], sot.subnet_ids)
        self.assertEqual(EXAMPLE['mtu'], sot.mtu)
        self.assertTrue(sot.is_port_security_enabled)
        self.assertEqual(EXAMPLE['availability_zone_hints'],
                         sot.availability_zone_hints)
        self.assertEqual(EXAMPLE['availability_zones'],
                         sot.availability_zones)
        self.assertEqual(EXAMPLE['ipv4_address_scope'],
                         sot.ipv4_address_scope_id)
        self.assertEqual(EXAMPLE['ipv6_address_scope'],
                         sot.ipv6_address_scope_id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        dt = datetime.datetime(2016, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
        dt = datetime.datetime(2016, 7, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))
        self.assertFalse(sot.is_default)
