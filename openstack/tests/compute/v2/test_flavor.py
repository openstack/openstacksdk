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
EXAMPLE = {
    'disk': 1,
    'id': IDENTIFIER,
    'os-flavor-access:is_public': True,
    'links': '4',
    'name': '5',
    'ram': 6,
    'vcpus': 7,
}


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

    def test_make_it(self):
        sot = flavor.Flavor(EXAMPLE)
        self.assertEqual(EXAMPLE['disk'], sot.disk)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['os-flavor-access:is_public'], sot.is_public)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['ram'], sot.ram)
        self.assertEqual(EXAMPLE['vcpus'], sot.vcpus)
