# Copyright 2024 RedHat Inc.
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
import testtools

from openstack.image.v2 import image_tasks

EXAMPLE = {
    'id': '56ab5f98-2bb7-44c7-bc05-52bde37eb53b',
    'type': 'import',
    'status': 'failure',
    'owner': '2858d31bc5f54f4db66e53ab905ef566',
    'expires_at': '2024-10-10T09:28:58.000000',
    'created_at': '2024-10-08T09:28:58.000000',
    'updated_at': '2024-10-08T09:28:58.000000',
    'deleted_at': None,
    'deleted': False,
    'image_id': '56a39162-730d-401c-8a77-11bc078cf3e2',
    'request_id': 'req-7d2f073c-f6f8-4807-9fdb-5ce6b10c65c5',
    'user_id': 'dec9b6d341ec481abddf1027576c2d60',
    'input': {'image_id': '56a39162-730d-401c-8a77-11bc078cf3e2'},
    'result': None,
    'message': "Input does not contain 'import_from' field",
}


class TestImageTasks(testtools.TestCase):
    def test_basic(self):
        sot = image_tasks.ImageTasks()
        self.assertEqual('/images/%(image_id)s/tasks', sot.base_path)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = image_tasks.ImageTasks(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['owner'], sot.owner)
        self.assertEqual(EXAMPLE['expires_at'], sot.expires_at)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['deleted_at'], sot.deleted_at)
        self.assertEqual(EXAMPLE['deleted'], sot.deleted)
        self.assertEqual(EXAMPLE['image_id'], sot.image_id)
        self.assertEqual(EXAMPLE['request_id'], sot.request_id)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
        self.assertEqual(EXAMPLE['input'], sot.input)
        self.assertEqual(EXAMPLE['result'], sot.result)
        self.assertEqual(EXAMPLE['message'], sot.message)
