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

from openstack.network.v2 import port

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'allowed_address_pairs': {'2': 2},
    'binding:host_id': '3',
    'binding:profile': '4',
    'binding:vif_details': {'5': 5},
    'binding:vif_type': '6',
    'binding:vnic_type': '7',
    'device_id': '8',
    'device_owner': '9',
    'extra_dhcp_opts': {'10': 10},
    'fixed_ips': {'11': '12'},
    'id': IDENTIFIER,
    'mac_address': '13',
    'name': '14',
    'network_id': '15',
    'tenant_id': '16',
    'security_groups': '17',
    'status': '18',
}


class TestPort(testtools.TestCase):

    def test_basic(self):
        sot = port.Port()
        self.assertEqual('port', sot.resource_key)
        self.assertEqual('ports', sot.resources_key)
        self.assertEqual('/ports', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = port.Port(EXAMPLE)
        self.assertEqual(EXAMPLE['admin_state_up'], sot.admin_state_up)
        self.assertEqual(EXAMPLE['allowed_address_pairs'],
                         sot.allowed_address_pairs)
        self.assertEqual(EXAMPLE['binding:host_id'], sot.binding_host_id)
        self.assertEqual(EXAMPLE['binding:profile'], sot.binding_profile)
        self.assertEqual(EXAMPLE['binding:vif_details'],
                         sot.binding_vif_details)
        self.assertEqual(EXAMPLE['binding:vif_type'], sot.binding_vif_type)
        self.assertEqual(EXAMPLE['binding:vnic_type'], sot.binding_vnic_type)
        self.assertEqual(EXAMPLE['device_id'], sot.device_id)
        self.assertEqual(EXAMPLE['device_owner'], sot.device_owner)
        self.assertEqual(EXAMPLE['extra_dhcp_opts'], sot.extra_dhcp_opts)
        self.assertEqual(EXAMPLE['fixed_ips'], sot.fixed_ips)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['mac_address'], sot.mac_address)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['network_id'], sot.network_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['security_groups'], sot.security_groups)
        self.assertEqual(EXAMPLE['status'], sot.status)
