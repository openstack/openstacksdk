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

from openstack.database.v1 import flavor

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'links': '1',
    'name': '2',
    'ram': '3',
}


class TestFlavor(testtools.TestCase):

    def test_basic(self):
        sot = flavor.Flavor()
        self.assertEqual('flavor', sot.resource_key)
        self.assertEqual('flavors', sot.resources_key)
        self.assertEqual('/flavors', sot.base_path)
        self.assertEqual('database', sot.service.service_type)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)

    def test_make_it(self):
        sot = flavor.Flavor(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['ram'], sot.ram)
