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

from openstack.compute.v2 import server_group

EXAMPLE = {
    'id': 'IDENTIFIER',
    'name': 'test',
    'members': ['server1', 'server2'],
    'metadata': {'k': 'v'},
    'policies': ['anti-affinity'],
}


class TestServerGroup(base.TestCase):

    def test_basic(self):
        sot = server_group.ServerGroup()
        self.assertEqual('server_group', sot.resource_key)
        self.assertEqual('server_groups', sot.resources_key)
        self.assertEqual('/os-server-groups', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({"all_projects": "all_projects",
                              "limit": "limit", "marker": "marker"},
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = server_group.ServerGroup(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['members'], sot.member_ids)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(EXAMPLE['policies'], sot.policies)
