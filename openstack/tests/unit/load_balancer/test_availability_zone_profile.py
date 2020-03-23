#
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
import uuid

from openstack.load_balancer.v2 import availability_zone_profile

IDENTIFIER = uuid.uuid4()
EXAMPLE = {
    'id': IDENTIFIER,
    'name': 'acidic',
    'provider_name': 'best',
    'availability_zone_data': '{"loadbalancer_topology": "SINGLE"}'}


class TestAvailabilityZoneProfile(base.TestCase):

    def test_basic(self):
        test_profile = availability_zone_profile.AvailabilityZoneProfile()
        self.assertEqual('availability_zone_profile',
                         test_profile.resource_key)
        self.assertEqual('availability_zone_profiles',
                         test_profile.resources_key)
        self.assertEqual('/lbaas/availabilityzoneprofiles',
                         test_profile.base_path)
        self.assertTrue(test_profile.allow_create)
        self.assertTrue(test_profile.allow_fetch)
        self.assertTrue(test_profile.allow_commit)
        self.assertTrue(test_profile.allow_delete)
        self.assertTrue(test_profile.allow_list)

    def test_make_it(self):
        test_profile = availability_zone_profile.AvailabilityZoneProfile(
            **EXAMPLE)
        self.assertEqual(EXAMPLE['id'], test_profile.id)
        self.assertEqual(EXAMPLE['name'], test_profile.name)
        self.assertEqual(EXAMPLE['provider_name'], test_profile.provider_name)
        self.assertEqual(EXAMPLE['availability_zone_data'],
                         test_profile.availability_zone_data)

        self.assertDictEqual(
            {'limit': 'limit',
             'marker': 'marker',
             'id': 'id',
             'name': 'name',
             'provider_name': 'provider_name',
             'availability_zone_data': 'availability_zone_data'},
            test_profile._query_mapping._mapping)
