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

from openstack.network.v2 import network_ip_availability

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'network_id': IDENTIFIER,
    'network_name': 'private',
    'subnet_ip_availability': [],
    'tenant_id': '5',
    'total_ips': 6,
    'used_ips': 10,
}

EXAMPLE_WITH_OPTIONAL = {
    'network_id': IDENTIFIER,
    'network_name': 'private',
    'subnet_ip_availability': [{"used_ips": 3, "subnet_id":
                                "2e4db1d6-ab2d-4bb1-93bb-a003fdbc9b39",
                                "subnet_name": "private-subnet",
                                "ip_version": 6, "cidr": "fd91:c3ba:e818::/64",
                                "total_ips": 18446744073709551614}],
    'tenant_id': '2',
    'total_ips': 1844,
    'used_ips': 6,
}


class TestNetworkIPAvailability(base.TestCase):

    def test_basic(self):
        sot = network_ip_availability.NetworkIPAvailability()
        self.assertEqual('network_ip_availability', sot.resource_key)
        self.assertEqual('network_ip_availabilities', sot.resources_key)
        self.assertEqual('/network-ip-availabilities', sot.base_path)
        self.assertEqual('network_name', sot.name_attribute)
        self.assertEqual('network', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = network_ip_availability.NetworkIPAvailability(**EXAMPLE)
        self.assertEqual(EXAMPLE['network_id'], sot.network_id)
        self.assertEqual(EXAMPLE['network_name'], sot.network_name)
        self.assertEqual(EXAMPLE['subnet_ip_availability'],
                         sot.subnet_ip_availability)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['total_ips'], sot.total_ips)
        self.assertEqual(EXAMPLE['used_ips'], sot.used_ips)

    def test_make_it_with_optional(self):
        sot = network_ip_availability.NetworkIPAvailability(
            **EXAMPLE_WITH_OPTIONAL)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['network_id'], sot.network_id)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['network_name'],
                         sot.network_name)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['subnet_ip_availability'],
                         sot.subnet_ip_availability)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['total_ips'], sot.total_ips)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['used_ips'], sot.used_ips)
