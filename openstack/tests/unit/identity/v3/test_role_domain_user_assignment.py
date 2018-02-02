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

from openstack.identity.v3 import role_domain_user_assignment

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'links': {'self': 'http://example.com/user1'},
    'name': '2',
    'domain_id': '3',
    'user_id': '4'
}


class TestRoleDomainUserAssignment(base.TestCase):

    def test_basic(self):
        sot = role_domain_user_assignment.RoleDomainUserAssignment()
        self.assertEqual('role', sot.resource_key)
        self.assertEqual('roles', sot.resources_key)
        self.assertEqual('/domains/%(domain_id)s/users/%(user_id)s/roles',
                         sot.base_path)
        self.assertEqual('identity', sot.service.service_type)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = \
            role_domain_user_assignment.RoleDomainUserAssignment(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['domain_id'], sot.domain_id)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
