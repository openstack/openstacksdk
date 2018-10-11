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

from openstack.database.v1 import database


IDENTIFIER = 'NAME'
INSTANCE_ID = 'INSTANCE_ID'
EXAMPLE = {
    'character_set': '1',
    'collate': '2',
    'instance_id': INSTANCE_ID,
    'name': IDENTIFIER,
}


class TestDatabase(base.TestCase):

    def test_basic(self):
        sot = database.Database()
        self.assertEqual('database', sot.resource_key)
        self.assertEqual('databases', sot.resources_key)
        path = '/instances/%(instance_id)s/databases'
        self.assertEqual(path, sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)

    def test_make_it(self):
        sot = database.Database(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['character_set'], sot.character_set)
        self.assertEqual(EXAMPLE['collate'], sot.collate)
        self.assertEqual(EXAMPLE['instance_id'], sot.instance_id)
        self.assertEqual(IDENTIFIER, sot.name)
        self.assertEqual(IDENTIFIER, sot.id)
