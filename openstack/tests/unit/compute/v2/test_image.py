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

from openstack.compute.v2 import image

IDENTIFIER = 'IDENTIFIER'
BASIC_EXAMPLE = {
    'id': IDENTIFIER,
    'links': '2',
    'name': '3',
}

DETAILS = {
    'created': '2015-03-09T12:14:57.233772',
    'metadata': {'key': '2'},
    'minDisk': 3,
    'minRam': 4,
    'progress': 5,
    'status': '6',
    'updated': '2015-03-09T12:15:57.233772',
    'OS-EXT-IMG-SIZE:size': 8
}

DETAIL_EXAMPLE = BASIC_EXAMPLE.copy()
DETAIL_EXAMPLE.update(DETAILS)


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

        self.assertDictEqual({"server": "server",
                              "name": "name",
                              "status": "status",
                              "type": "type",
                              "min_disk": "minDisk",
                              "min_ram": "minRam",
                              "changes_since": "changes-since",
                              "limit": "limit",
                              "marker": "marker"},
                             sot._query_mapping._mapping)

    def test_make_basic(self):
        sot = image.Image(**BASIC_EXAMPLE)
        self.assertEqual(BASIC_EXAMPLE['id'], sot.id)
        self.assertEqual(BASIC_EXAMPLE['links'], sot.links)
        self.assertEqual(BASIC_EXAMPLE['name'], sot.name)

    def test_detail(self):
        sot = image.ImageDetail()
        self.assertEqual('image', sot.resource_key)
        self.assertEqual('images', sot.resources_key)
        self.assertEqual('/images/detail', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_detail(self):
        sot = image.ImageDetail(**DETAIL_EXAMPLE)
        self.assertEqual(DETAIL_EXAMPLE['created'], sot.created_at)
        self.assertEqual(DETAIL_EXAMPLE['id'], sot.id)
        self.assertEqual(DETAIL_EXAMPLE['links'], sot.links)
        self.assertEqual(DETAIL_EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(DETAIL_EXAMPLE['minDisk'], sot.min_disk)
        self.assertEqual(DETAIL_EXAMPLE['minRam'], sot.min_ram)
        self.assertEqual(DETAIL_EXAMPLE['name'], sot.name)
        self.assertEqual(DETAIL_EXAMPLE['progress'], sot.progress)
        self.assertEqual(DETAIL_EXAMPLE['status'], sot.status)
        self.assertEqual(DETAIL_EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(DETAIL_EXAMPLE['OS-EXT-IMG-SIZE:size'], sot.size)
