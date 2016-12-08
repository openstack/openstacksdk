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

from openstack.network.v2 import service_profile

IDENTIFIER = 'IDENTIFIER'
EXAMPLE_WITH_OPTIONAL = {
    'description': 'test flavor profile',
    'driver': 'neutron_lbaas.drivers.octavia.driver.OctaviaDriver',
    'enabled': True,
    'metainfo': {'foo': 'bar'},
    'tenant_id': '5',
}

EXAMPLE = {
    'driver': 'neutron_lbaas.drivers.octavia.driver.OctaviaDriver',
}


class TestServiceProfile(testtools.TestCase):
    def test_basic(self):
        service_profiles = service_profile.ServiceProfile()
        self.assertEqual('service_profile', service_profiles.resource_key)
        self.assertEqual('service_profiles', service_profiles.resources_key)
        self.assertEqual('/service_profiles', service_profiles.base_path)
        self.assertTrue(service_profiles.allow_create)
        self.assertTrue(service_profiles.allow_get)
        self.assertTrue(service_profiles.allow_update)
        self.assertTrue(service_profiles.allow_delete)
        self.assertTrue(service_profiles.allow_list)

    def test_make_it(self):
        service_profiles = service_profile.ServiceProfile(**EXAMPLE)
        self.assertEqual(EXAMPLE['driver'], service_profiles.driver)

    def test_make_it_with_optional(self):
        service_profiles = service_profile.ServiceProfile(
            **EXAMPLE_WITH_OPTIONAL)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['description'],
                         service_profiles.description)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['driver'],
                         service_profiles.driver)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['enabled'],
                         service_profiles.is_enabled)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['metainfo'],
                         service_profiles.meta_info)
        self.assertEqual(EXAMPLE_WITH_OPTIONAL['tenant_id'],
                         service_profiles.project_id)
