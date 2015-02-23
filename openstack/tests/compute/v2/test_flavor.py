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

from openstack.compute.v2 import flavor

IDENTIFIER = 'IDENTIFIER'
BASIC_EXAMPLE = {
    'id': IDENTIFIER,
    'links': '4',
    'name': '5',
}

DETAILS = {
    'disk': 1,
    'os-flavor-access:is_public': True,
    'ram': 3,
    'vcpus': 4,
    'swap': 5,
    'OS-FLV-EXT-DATA:ephemeral': 6,
    'OS-FLV-DISABLED:disabled': False,
    'rxtx_factor': 8.0
}

DETAIL_EXAMPLE = BASIC_EXAMPLE.copy()
DETAIL_EXAMPLE.update(DETAILS)


class TestFlavor(testtools.TestCase):

    def test_basic(self):
        sot = flavor.Flavor()
        self.assertEqual('flavor', sot.resource_key)
        self.assertEqual('flavors', sot.resources_key)
        self.assertEqual('/flavors', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_basic(self):
        sot = flavor.Flavor(BASIC_EXAMPLE)
        self.assertEqual(BASIC_EXAMPLE['id'], sot.id)
        self.assertEqual(BASIC_EXAMPLE['links'], sot.links)
        self.assertEqual(BASIC_EXAMPLE['name'], sot.name)

    def test_detail(self):
        sot = flavor.FlavorDetail()
        self.assertEqual('flavor', sot.resource_key)
        self.assertEqual('flavors', sot.resources_key)
        self.assertEqual('/flavors/detail', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_detail(self):
        sot = flavor.FlavorDetail(DETAIL_EXAMPLE)
        self.assertEqual(DETAIL_EXAMPLE['id'], sot.id)
        self.assertEqual(DETAIL_EXAMPLE['links'], sot.links)
        self.assertEqual(DETAIL_EXAMPLE['name'], sot.name)
        self.assertEqual(DETAIL_EXAMPLE['disk'], sot.disk)
        self.assertEqual(DETAIL_EXAMPLE['os-flavor-access:is_public'],
                         sot.is_public)
        self.assertEqual(DETAIL_EXAMPLE['ram'], sot.ram)
        self.assertEqual(DETAIL_EXAMPLE['vcpus'], sot.vcpus)
        self.assertEqual(DETAIL_EXAMPLE['swap'], sot.swap)
        self.assertEqual(DETAIL_EXAMPLE['OS-FLV-EXT-DATA:ephemeral'],
                         sot.ephemeral)
        self.assertEqual(DETAIL_EXAMPLE['OS-FLV-DISABLED:disabled'],
                         sot.disabled)
        self.assertEqual(DETAIL_EXAMPLE['rxtx_factor'], sot.rxtx_factor)
