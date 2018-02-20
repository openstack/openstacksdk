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

from openstack.identity.v3 import user

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'default_project_id': '1',
    'description': '2',
    'domain_id': '3',
    'email': '4',
    'enabled': True,
    'id': IDENTIFIER,
    'links': {'self': 'http://example.com/user1'},
    'name': '6',
    'password': '7',
    'password_expires_at': '8',
}


class TestUser(base.TestCase):

    def test_basic(self):
        sot = user.User()
        self.assertEqual('user', sot.resource_key)
        self.assertEqual('users', sot.resources_key)
        self.assertEqual('/users', sot.base_path)
        self.assertEqual('identity', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.update_method)

        self.assertDictEqual(
            {
                'domain_id': 'domain_id',
                'name': 'name',
                'password_expires_at': 'password_expires_at',
                'is_enabled': 'enabled',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping)

    def test_make_it(self):
        sot = user.User(**EXAMPLE)
        self.assertEqual(EXAMPLE['default_project_id'],
                         sot.default_project_id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['domain_id'], sot.domain_id)
        self.assertEqual(EXAMPLE['email'], sot.email)
        self.assertTrue(sot.is_enabled)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['password'], sot.password)
        self.assertEqual(EXAMPLE['password_expires_at'],
                         sot.password_expires_at)
