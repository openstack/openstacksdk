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

from openstack.network.v2 import security_group_rule

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'created_at': '0',
    'description': '1',
    'direction': '2',
    'ethertype': '3',
    'id': IDENTIFIER,
    'port_range_max': 4,
    'port_range_min': 5,
    'protocol': '6',
    'remote_group_id': '7',
    'remote_ip_prefix': '8',
    'revision_number': 9,
    'security_group_id': '10',
    'tenant_id': '11',
    'updated_at': '12'
}


class TestSecurityGroupRule(testtools.TestCase):

    def test_basic(self):
        sot = security_group_rule.SecurityGroupRule()
        self.assertEqual('security_group_rule', sot.resource_key)
        self.assertEqual('security_group_rules', sot.resources_key)
        self.assertEqual('/security-group-rules', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = security_group_rule.SecurityGroupRule(**EXAMPLE)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['direction'], sot.direction)
        self.assertEqual(EXAMPLE['ethertype'], sot.ether_type)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['port_range_max'], sot.port_range_max)
        self.assertEqual(EXAMPLE['port_range_min'], sot.port_range_min)
        self.assertEqual(EXAMPLE['protocol'], sot.protocol)
        self.assertEqual(EXAMPLE['remote_group_id'], sot.remote_group_id)
        self.assertEqual(EXAMPLE['remote_ip_prefix'], sot.remote_ip_prefix)
        self.assertEqual(EXAMPLE['revision_number'], sot.revision_number)
        self.assertEqual(EXAMPLE['security_group_id'], sot.security_group_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
