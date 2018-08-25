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

from openstack.identity.v3 import project

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'description': '1',
    'domain_id': '2',
    'enabled': True,
    'id': IDENTIFIER,
    'is_domain': False,
    'name': '5',
    'parent_id': '6',
}


class TestProject(base.TestCase):

    def test_basic(self):
        sot = project.Project()
        self.assertEqual('project', sot.resource_key)
        self.assertEqual('projects', sot.resources_key)
        self.assertEqual('/projects', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

        self.assertDictEqual(
            {
                'domain_id': 'domain_id',
                'is_domain': 'is_domain',
                'name': 'name',
                'parent_id': 'parent_id',
                'is_enabled': 'enabled',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping)

    def test_make_it(self):
        sot = project.Project(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['domain_id'], sot.domain_id)
        self.assertFalse(sot.is_domain)
        self.assertTrue(sot.is_enabled)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['parent_id'], sot.parent_id)


class TestUserProject(base.TestCase):

    def test_basic(self):
        sot = project.UserProject()
        self.assertEqual('project', sot.resource_key)
        self.assertEqual('projects', sot.resources_key)
        self.assertEqual('/users/%(user_id)s/projects', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)
