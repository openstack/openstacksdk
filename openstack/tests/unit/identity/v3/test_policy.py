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

from openstack.identity.v3 import policy

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'blob': '1',
    'id': IDENTIFIER,
    'links': {'self': 'a-pointer'},
    'project_id': '2',
    'type': '3',
    'user_id': '4',
}


class TestPolicy(base.TestCase):

    def test_basic(self):
        sot = policy.Policy()
        self.assertEqual('policy', sot.resource_key)
        self.assertEqual('policies', sot.resources_key)
        self.assertEqual('/policies', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

    def test_make_it(self):
        sot = policy.Policy(**EXAMPLE)
        self.assertEqual(EXAMPLE['blob'], sot.blob)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
