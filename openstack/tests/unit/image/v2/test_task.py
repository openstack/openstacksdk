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

from openstack.image.v2 import task
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'created_at': '2016-06-24T14:40:19Z',
    'id': IDENTIFIER,
    'input': {
        'image_properties': {'container_format': 'ovf', 'disk_format': 'vhd'},
        'import_from': 'http://example.com',
        'import_from_format': 'qcow2',
    },
    'message': 'message',
    'owner': 'fa6c8c1600f4444281658a23ee6da8e8',
    'result': 'some result',
    'schema': '/v2/schemas/task',
    'status': 'processing',
    'type': 'import',
    'updated_at': '2016-06-24T14:40:20Z',
}


class TestTask(base.TestCase):
    def test_basic(self):
        sot = task.Task()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('tasks', sot.resources_key)
        self.assertEqual('/tasks', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'sort_dir': 'sort_dir',
                'sort_key': 'sort_key',
                'status': 'status',
                'type': 'type',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = task.Task(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['input'], sot.input)
        self.assertEqual(EXAMPLE['message'], sot.message)
        self.assertEqual(EXAMPLE['owner'], sot.owner_id)
        self.assertEqual(EXAMPLE['result'], sot.result)
        self.assertEqual(EXAMPLE['schema'], sot.schema)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
