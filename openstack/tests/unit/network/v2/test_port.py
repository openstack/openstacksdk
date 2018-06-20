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

from openstack.network.v2 import port

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'allowed_address_pairs': [{'2': 2}],
    'binding:host_id': '3',
    'binding:profile': {'4': 4},
    'binding:vif_details': {'5': 5},
    'binding:vif_type': '6',
    'binding:vnic_type': '7',
    'created_at': '2016-03-09T12:14:57.233772',
    'data_plane_status': '32',
    'description': '8',
    'device_id': '9',
    'device_owner': '10',
    'dns_assignment': [{'11': 11}],
    'dns_domain': 'a11',
    'dns_name': '12',
    'extra_dhcp_opts': [{'13': 13}],
    'fixed_ips': [{'14': '14'}],
    'id': IDENTIFIER,
    'mac_address': '16',
    'name': '17',
    'network_id': '18',
    'port_security_enabled': True,
    'qos_policy_id': '21',
    'revision_number': 22,
    'security_groups': ['23'],
    'status': '25',
    'tenant_id': '26',
    'trunk_details': {
        'trunk_id': '27',
        'sub_ports': [{
            'port_id': '28',
            'segmentation_id': 29,
            'segmentation_type': '30',
            'mac_address': '31'}]},
    'updated_at': '2016-07-09T12:14:57.233772',
}


class TestPort(base.TestCase):

    def test_basic(self):
        sot = port.Port()
        self.assertEqual('port', sot.resource_key)
        self.assertEqual('ports', sot.resources_key)
        self.assertEqual('/ports', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({"binding:host_id": "binding:host_id",
                              "binding:profile": "binding:profile",
                              "binding:vif_details": "binding:vif_details",
                              "binding:vif_type": "binding:vif_type",
                              "binding:vnic_type": "binding:vnic_type",
                              "description": "description",
                              "device_id": "device_id",
                              "device_owner": "device_owner",
                              "fixed_ips": "fixed_ips",
                              "ip_address": "ip_address",
                              "mac_address": "mac_address",
                              "name": "name",
                              "network_id": "network_id",
                              "status": "status",
                              "subnet_id": "subnet_id",
                              "is_admin_state_up": "admin_state_up",
                              "is_port_security_enabled":
                                  "port_security_enabled",
                              "project_id": "tenant_id",
                              "limit": "limit",
                              "marker": "marker",
                              "any_tags": "tags-any",
                              "not_any_tags": "not-tags-any",
                              "not_tags": "not-tags",
                              "tags": "tags"},
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = port.Port(**EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['allowed_address_pairs'],
                         sot.allowed_address_pairs)
        self.assertEqual(EXAMPLE['binding:host_id'], sot.binding_host_id)
        self.assertEqual(EXAMPLE['binding:profile'], sot.binding_profile)
        self.assertEqual(EXAMPLE['binding:vif_details'],
                         sot.binding_vif_details)
        self.assertEqual(EXAMPLE['binding:vif_type'], sot.binding_vif_type)
        self.assertEqual(EXAMPLE['binding:vnic_type'], sot.binding_vnic_type)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['data_plane_status'], sot.data_plane_status)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['device_id'], sot.device_id)
        self.assertEqual(EXAMPLE['device_owner'], sot.device_owner)
        self.assertEqual(EXAMPLE['dns_assignment'], sot.dns_assignment)
        self.assertEqual(EXAMPLE['dns_domain'], sot.dns_domain)
        self.assertEqual(EXAMPLE['dns_name'], sot.dns_name)
        self.assertEqual(EXAMPLE['extra_dhcp_opts'], sot.extra_dhcp_opts)
        self.assertEqual(EXAMPLE['fixed_ips'], sot.fixed_ips)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['mac_address'], sot.mac_address)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['network_id'], sot.network_id)
        self.assertTrue(sot.is_port_security_enabled)
        self.assertEqual(EXAMPLE['qos_policy_id'], sot.qos_policy_id)
        self.assertEqual(EXAMPLE['revision_number'], sot.revision_number)
        self.assertEqual(EXAMPLE['security_groups'], sot.security_group_ids)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['trunk_details'], sot.trunk_details)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
