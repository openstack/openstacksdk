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

from openstack.compute.v2 import flavor

IDENTIFIER = 'IDENTIFIER'
BASIC_EXAMPLE = {
    'id': IDENTIFIER,
    'links': '2',
    'name': '3',
    'description': 'Testing flavor',
    'disk': 4,
    'os-flavor-access:is_public': True,
    'ram': 6,
    'vcpus': 7,
    'swap': 8,
    'OS-FLV-EXT-DATA:ephemeral': 9,
    'OS-FLV-DISABLED:disabled': False,
    'rxtx_factor': 11.0
}


class TestFlavor(base.TestCase):

    def test_basic(self):
        sot = flavor.Flavor()
        self.assertEqual('flavor', sot.resource_key)
        self.assertEqual('flavors', sot.resources_key)
        self.assertEqual('/flavors', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_commit)

        self.assertDictEqual({"sort_key": "sort_key",
                              "sort_dir": "sort_dir",
                              "min_disk": "minDisk",
                              "min_ram": "minRam",
                              "limit": "limit",
                              "marker": "marker",
                              "is_public": "is_public"},
                             sot._query_mapping._mapping)

    def test_make_basic(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        self.assertEqual(BASIC_EXAMPLE['id'], sot.id)
        self.assertEqual(BASIC_EXAMPLE['links'], sot.links)
        self.assertEqual(BASIC_EXAMPLE['name'], sot.name)
        self.assertEqual(BASIC_EXAMPLE['description'], sot.description)
        self.assertEqual(BASIC_EXAMPLE['disk'], sot.disk)
        self.assertEqual(BASIC_EXAMPLE['os-flavor-access:is_public'],
                         sot.is_public)
        self.assertEqual(BASIC_EXAMPLE['ram'], sot.ram)
        self.assertEqual(BASIC_EXAMPLE['vcpus'], sot.vcpus)
        self.assertEqual(BASIC_EXAMPLE['swap'], sot.swap)
        self.assertEqual(BASIC_EXAMPLE['OS-FLV-EXT-DATA:ephemeral'],
                         sot.ephemeral)
        self.assertEqual(BASIC_EXAMPLE['OS-FLV-DISABLED:disabled'],
                         sot.is_disabled)
        self.assertEqual(BASIC_EXAMPLE['rxtx_factor'], sot.rxtx_factor)

    def test_detail(self):
        sot = flavor.FlavorDetail()
        self.assertEqual('flavor', sot.resource_key)
        self.assertEqual('flavors', sot.resources_key)
        self.assertEqual('/flavors/detail', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)
