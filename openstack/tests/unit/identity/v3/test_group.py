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

from openstack.identity.v3 import group

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'description': '1',
    'domain_id': '2',
    'id': IDENTIFIER,
    'name': '4',
}


class TestGroup(base.TestCase):

    def test_basic(self):
        sot = group.Group()
        self.assertEqual('group', sot.resource_key)
        self.assertEqual('groups', sot.resources_key)
        self.assertEqual('/groups', sot.base_path)
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
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping)

    def test_make_it(self):
        sot = group.Group(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['domain_id'], sot.domain_id)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
