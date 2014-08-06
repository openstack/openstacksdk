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

from openstack.network.v2 import floatingip

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'fixed_ip_address': '1',
    'floating_ip_address': '2',
    'floating_network_id': '3',
    'id': IDENTIFIER,
    'port_id': '5',
    'tenant_id': '6',
    'router_id': '7',
}


class TestFloatingIP(testtools.TestCase):

    def test_basic(self):
        sot = floatingip.FloatingIP()
        self.assertEqual('floatingip', sot.resource_key)
        self.assertEqual('floatingips', sot.resources_key)
        self.assertEqual('/v2.0/floatingips', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = floatingip.FloatingIP(EXAMPLE)
        self.assertEqual(EXAMPLE['fixed_ip_address'], sot.fixed_ip_address)
        self.assertEqual(EXAMPLE['floating_ip_address'],
                         sot.floating_ip_address)
        self.assertEqual(EXAMPLE['floating_network_id'],
                         sot.floating_network_id)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['port_id'], sot.port_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['router_id'], sot.router_id)
