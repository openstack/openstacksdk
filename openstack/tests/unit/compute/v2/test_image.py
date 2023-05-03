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

from openstack.compute.v2 import image
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'

EXAMPLE = {
    'id': IDENTIFIER,
    'links': '2',
    'name': '3',
    'created': '2015-03-09T12:14:57.233772',
    'metadata': {'key': '2'},
    'minDisk': 3,
    'minRam': 4,
    'progress': 5,
    'status': '6',
    'updated': '2015-03-09T12:15:57.233772',
    'OS-EXT-IMG-SIZE:size': 8,
}


class TestImage(base.TestCase):
    def test_basic(self):
        sot = image.Image()
        self.assertEqual('image', sot.resource_key)
        self.assertEqual('images', sot.resources_key)
        self.assertEqual('/images', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                "server": "server",
                "name": "name",
                "status": "status",
                "type": "type",
                "min_disk": "minDisk",
                "min_ram": "minRam",
                "changes_since": "changes-since",
                "limit": "limit",
                "marker": "marker",
            },
            sot._query_mapping._mapping,
        )

    def test_make_basic(self):
        sot = image.Image(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['created'], sot.created_at)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(EXAMPLE['minDisk'], sot.min_disk)
        self.assertEqual(EXAMPLE['minRam'], sot.min_ram)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['progress'], sot.progress)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(EXAMPLE['OS-EXT-IMG-SIZE:size'], sot.size)
