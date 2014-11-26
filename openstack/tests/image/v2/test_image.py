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

import testtools

from openstack.image.v2 import image

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'checksum': '1',
    'container_format': '2',
    'created_at': '2014-11-19T10:44:55.123450Z',
    'disk_format': '4',
    'min_disk': 5,
    'name': '6',
    'owner': '7',
    'properties': {'a': 'z', 'b': 'y', },
    'protected': False,
    'status': '8',
    'tags': ['g', 'h', 'i'],
    'updated_at': '2014-11-19T10:44:55.123450Z',
    'virtual_size': '10',
    'visibility': '11'
}


class TestImage(testtools.TestCase):
    def test_basic(self):
        sot = image.Image()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('images', sot.resources_key)
        self.assertEqual('/images', sot.base_path)
        self.assertEqual('image', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = image.Image(EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['checksum'], sot.checksum)
        self.assertEqual(EXAMPLE['container_format'], sot.container_format)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['disk_format'], sot.disk_format)
        self.assertEqual(EXAMPLE['min_disk'], sot.min_disk)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['owner'], sot.owner)
        self.assertEqual(EXAMPLE['properties'], sot.properties)
        self.assertEqual(EXAMPLE['protected'], sot.protected)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['tags'], sot.tags)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['virtual_size'], sot.virtual_size)
        self.assertEqual(EXAMPLE['visibility'], sot.visibility)