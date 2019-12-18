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

from openstack.tests.unit import base

from openstack.network.v2 import subnet

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'allocation_pools': [{'1': 1}],
    'cidr': '2',
    'created_at': '3',
    'description': '4',
    'dns_nameservers': ['5'],
    'dns_publish_fixed_ip': True,
    'enable_dhcp': True,
    'gateway_ip': '6',
    'host_routes': ['7'],
    'id': IDENTIFIER,
    'ip_version': 8,
    'ipv6_address_mode': '9',
    'ipv6_ra_mode': '10',
    'name': '11',
    'network_id': '12',
    'revision_number': 13,
    'segment_id': '14',
    'service_types': ['15'],
    'subnetpool_id': '16',
    'tenant_id': '17',
    'updated_at': '18',
    'use_default_subnetpool': True,
}


class TestSubnet(base.TestCase):

    def test_basic(self):
        sot = subnet.Subnet()
        self.assertEqual('subnet', sot.resource_key)
        self.assertEqual('subnets', sot.resources_key)
        self.assertEqual('/subnets', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = subnet.Subnet(**EXAMPLE)
        self.assertEqual(EXAMPLE['allocation_pools'], sot.allocation_pools)
        self.assertEqual(EXAMPLE['cidr'], sot.cidr)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['dns_nameservers'], sot.dns_nameservers)
        self.assertTrue(sot.dns_publish_fixed_ip)
        self.assertTrue(sot.is_dhcp_enabled)
        self.assertEqual(EXAMPLE['gateway_ip'], sot.gateway_ip)
        self.assertEqual(EXAMPLE['host_routes'], sot.host_routes)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['ip_version'], sot.ip_version)
        self.assertEqual(EXAMPLE['ipv6_address_mode'], sot.ipv6_address_mode)
        self.assertEqual(EXAMPLE['ipv6_ra_mode'], sot.ipv6_ra_mode)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['network_id'], sot.network_id)
        self.assertEqual(EXAMPLE['revision_number'], sot.revision_number)
        self.assertEqual(EXAMPLE['segment_id'], sot.segment_id)
        self.assertEqual(EXAMPLE['service_types'], sot.service_types)
        self.assertEqual(EXAMPLE['subnetpool_id'], sot.subnet_pool_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertTrue(sot.use_default_subnet_pool)
