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

from openstack.network.v2 import subnet

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'allocation_pools': '1',
    'cidr': '2',
    'dns_nameservers': '3',
    'enable_dhcp': True,
    'gateway_ip': '5',
    'host_routes': '6',
    'id': IDENTIFIER,
    'ip_version': '8',
    'ipv6_address_mode': 'dhcpv6-stateless',
    'ipv6_ra_mode': 'radvd',
    'name': '9',
    'network_id': '10',
    'tenant_id': '11',
    'subnetpool_id': '12',
    'description': '13',
    'created_at': '2016-03-09T12:14:57.233772',
    'updated_at': '2016-07-09T12:14:57.233772',
}


class TestSubnet(testtools.TestCase):

    def test_basic(self):
        sot = subnet.Subnet()
        self.assertEqual('subnet', sot.resource_key)
        self.assertEqual('subnets', sot.resources_key)
        self.assertEqual('/subnets', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = subnet.Subnet(EXAMPLE)
        self.assertEqual(EXAMPLE['allocation_pools'], sot.allocation_pools)
        self.assertEqual(EXAMPLE['cidr'], sot.cidr)
        self.assertEqual(EXAMPLE['dns_nameservers'], sot.dns_nameservers)
        self.assertTrue(sot.is_dhcp_enabled)
        self.assertEqual(EXAMPLE['gateway_ip'], sot.gateway_ip)
        self.assertEqual(EXAMPLE['host_routes'], sot.host_routes)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['ip_version'], sot.ip_version)
        self.assertEqual(EXAMPLE['ipv6_address_mode'], sot.ipv6_address_mode)
        self.assertEqual(EXAMPLE['ipv6_ra_mode'], sot.ipv6_ra_mode)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['network_id'], sot.network_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['subnetpool_id'], sot.subnet_pool_id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        dt = datetime.datetime(2016, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
        dt = datetime.datetime(2016, 7, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))
