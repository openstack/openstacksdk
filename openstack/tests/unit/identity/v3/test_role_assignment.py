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

from openstack.identity.v3 import role_assignment
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'links': {'self': 'http://example.com/user1'},
    'scope': {'domain': {'id': '2'}},
    'user': {'id': '3'},
    'group': {'id': '4'},
}


class TestRoleAssignment(base.TestCase):
    def test_basic(self):
        sot = role_assignment.RoleAssignment()
        self.assertEqual('role_assignment', sot.resource_key)
        self.assertEqual('role_assignments', sot.resources_key)
        self.assertEqual('/role_assignments', sot.base_path)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                'group_id': 'group.id',
                'role_id': 'role.id',
                'scope_domain_id': 'scope.domain.id',
                'scope_project_id': 'scope.project.id',
                'scope_system': 'scope.system',
                'user_id': 'user.id',
                'effective': 'effective',
                'inherited_to': 'scope.OS-INHERIT:inherited_to',
                'include_names': 'include_names',
                'include_subtree': 'include_subtree',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = role_assignment.RoleAssignment(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['scope'], sot.scope)
        self.assertEqual(EXAMPLE['user'], sot.user)
        self.assertEqual(EXAMPLE['group'], sot.group)
