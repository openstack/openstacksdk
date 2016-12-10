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

from openstack.network.v2 import flavor

IDENTIFIER = 'IDENTIFIER'
EXAMPLE_WITH_OPTIONAL = {
    'name': 'test-flavor',
    'service_type': 'VPN',
    'description': 'VPN flavor',
    'enabled': True,
    'service_profiles': ['1', '2'],
}

EXAMPLE = {
    'name': 'test-flavor',
    'service_type': 'VPN',
}


class TestFlavor(testtools.TestCase):
    def test_basic(self):
        flavors = flavor.Flavor()
        self.assertEqual('flavor', flavors.resource_key)
        self.assertEqual('flavors', flavors.resources_key)
        self.assertEqual('/flavors', flavors.base_path)
        self.assertEqual('network', flavors.service.service_type)
        self.assertTrue(flavors.allow_create)
        self.assertTrue(flavors.allow_get)
        self.assertTrue(flavors.allow_update)
        self.assertTrue(flavors.allow_delete)
        self.assertTrue(flavors.allow_list)

    def test_make_it(self):
        flavors = flavor.Flavor(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], flavors.name)
        self.assertEqual(EXAMPLE['service_type'], flavors.service_type)

    def test_make_it_with_optional(self):
        flavors = flavor.Flavor(**EXAMPLE_WITH_OPTIONAL)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['name'], flavors.name)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['service_type'],
                         flavors.service_type)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['description'],
                         flavors.description)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['enabled'], flavors.is_enabled)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['service_profiles'],
                         flavors.service_profile_ids)
