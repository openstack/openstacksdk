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

from openstack.network.v2 import security_group_rule
from openstack.tests.unit import base


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
    'project_id': '11',
    'updated_at': '12',
    'remote_address_group_id': '13',
}


class TestSecurityGroupRule(base.TestCase):
    def test_basic(self):
        sot = security_group_rule.SecurityGroupRule()
        self.assertEqual('security_group_rule', sot.resource_key)
        self.assertEqual('security_group_rules', sot.resources_key)
        self.assertEqual('/security-group-rules', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                'any_tags': 'tags-any',
                'description': 'description',
                'direction': 'direction',
                'id': 'id',
                'ether_type': 'ethertype',
                'limit': 'limit',
                'marker': 'marker',
                'not_any_tags': 'not-tags-any',
                'not_tags': 'not-tags',
                'port_range_max': 'port_range_max',
                'port_range_min': 'port_range_min',
                'tenant_id': 'tenant_id',
                'protocol': 'protocol',
                'remote_group_id': 'remote_group_id',
                'remote_address_group_id': 'remote_address_group_id',
                'remote_ip_prefix': 'remote_ip_prefix',
                'revision_number': 'revision_number',
                'security_group_id': 'security_group_id',
                'sort_dir': 'sort_dir',
                'sort_key': 'sort_key',
                'tags': 'tags',
                'project_id': 'project_id',
            },
            sot._query_mapping._mapping,
        )

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
        self.assertEqual(
            EXAMPLE['remote_address_group_id'], sot.remote_address_group_id
        )
        self.assertEqual(EXAMPLE['remote_ip_prefix'], sot.remote_ip_prefix)
        self.assertEqual(EXAMPLE['revision_number'], sot.revision_number)
        self.assertEqual(EXAMPLE['security_group_id'], sot.security_group_id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
