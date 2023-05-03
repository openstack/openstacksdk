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

from openstack.identity.v3 import role_system_group_assignment
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {'id': IDENTIFIER, 'name': '2', 'group_id': '4'}


class TestRoleSystemGroupAssignment(base.TestCase):
    def test_basic(self):
        sot = role_system_group_assignment.RoleSystemGroupAssignment()
        self.assertEqual('role', sot.resource_key)
        self.assertEqual('roles', sot.resources_key)
        self.assertEqual('/system/groups/%(group_id)s/roles', sot.base_path)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = role_system_group_assignment.RoleSystemGroupAssignment(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['group_id'], sot.group_id)
