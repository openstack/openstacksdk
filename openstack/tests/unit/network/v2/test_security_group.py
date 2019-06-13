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

from openstack.network.v2 import security_group

IDENTIFIER = 'IDENTIFIER'
RULES = [
    {
        "remote_group_id": None,
        "direction": "egress",
        "remote_ip_prefix": None,
        "protocol": None,
        "ethertype":
        "IPv6",
        "tenant_id": "4",
        "port_range_max": None,
        "port_range_min": None,
        "id": "5",
        "security_group_id": IDENTIFIER,
        "created_at": "2016-10-04T12:14:57.233772",
        "updated_at": "2016-10-12T12:15:34.233222",
        "revision_number": 6,
    },
    {
        "remote_group_id": "9",
        "direction": "ingress",
        "remote_ip_prefix": None,
        "protocol": None,
        "ethertype": "IPv6",
        "tenant_id": "4",
        "port_range_max": None,
        "port_range_min": None,
        "id": "6",
        "security_group_id": IDENTIFIER,
        "created_at": "2016-10-04T12:14:57.233772",
        "updated_at": "2016-10-12T12:15:34.233222",
        "revision_number": 7,
    },
]

EXAMPLE = {
    'created_at': '2016-10-04T12:14:57.233772',
    'description': '1',
    'id': IDENTIFIER,
    'name': '2',
    'revision_number': 3,
    'security_group_rules': RULES,
    'tenant_id': '4',
    'project_id': '4',
    'updated_at': '2016-10-14T12:16:57.233772',
    'tags': ['5']
}


class TestSecurityGroup(base.TestCase):

    def test_basic(self):
        sot = security_group.SecurityGroup()
        self.assertEqual('security_group', sot.resource_key)
        self.assertEqual('security_groups', sot.resources_key)
        self.assertEqual('/security-groups', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({'any_tags': 'tags-any',
                              'description': 'description',
                              'limit': 'limit',
                              'marker': 'marker',
                              'name': 'name',
                              'not_any_tags': 'not-tags-any',
                              'not_tags': 'not-tags',
                              'project_id': 'project_id',
                              'revision_number': 'revision_number',
                              'sort_dir': 'sort_dir',
                              'sort_key': 'sort_key',
                              'tags': 'tags',
                              'tenant_id': 'tenant_id'
                              },
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = security_group.SecurityGroup(**EXAMPLE)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['revision_number'], sot.revision_number)
        self.assertEqual(EXAMPLE['security_group_rules'],
                         sot.security_group_rules)
        self.assertEqual(dict, type(sot.security_group_rules[0]))
        self.assertEqual(EXAMPLE['tenant_id'], sot.tenant_id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['tags'], sot.tags)
