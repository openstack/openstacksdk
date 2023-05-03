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

from openstack.identity.v3 import credential
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'blob': '1',
    'id': IDENTIFIER,
    'project_id': '3',
    'type': '4',
    'user_id': '5',
}


class TestCredential(base.TestCase):
    def test_basic(self):
        sot = credential.Credential()
        self.assertEqual('credential', sot.resource_key)
        self.assertEqual('credentials', sot.resources_key)
        self.assertEqual('/credentials', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

        self.assertDictEqual(
            {
                'type': 'type',
                'user_id': 'user_id',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = credential.Credential(**EXAMPLE)
        self.assertEqual(EXAMPLE['blob'], sot.blob)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
