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

from openstack.compute.v2 import image

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'created': '1',
    'id': IDENTIFIER,
    'links': '3',
    'metadata': {'key': '4'},
    'minDisk': 5,
    'minRam': 6,
    'name': '7',
    'progress': 8,
    'status': '9',
    'updated': '10',
}


class TestImage(testtools.TestCase):

    def test_basic(self):
        sot = image.Image()
        self.assertEqual('image', sot.resource_key)
        self.assertEqual('images', sot.resources_key)
        self.assertEqual('/images', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = image.Image(EXAMPLE)
        self.assertEqual(EXAMPLE['created'], sot.created)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(EXAMPLE['minDisk'], sot.min_disk)
        self.assertEqual(EXAMPLE['minRam'], sot.min_ram)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['progress'], sot.progress)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated)
