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

import uuid

from openstack.load_balancer.v2 import availability_zone
from openstack.tests.unit import base


AVAILABILITY_ZONE_PROFILE_ID = uuid.uuid4()
EXAMPLE = {
    'name': 'strawberry',
    'description': 'tasty',
    'is_enabled': False,
    'availability_zone_profile_id': AVAILABILITY_ZONE_PROFILE_ID,
}


class TestAvailabilityZone(base.TestCase):
    def test_basic(self):
        test_availability_zone = availability_zone.AvailabilityZone()
        self.assertEqual(
            'availability_zone', test_availability_zone.resource_key
        )
        self.assertEqual(
            'availability_zones', test_availability_zone.resources_key
        )
        self.assertEqual(
            '/lbaas/availabilityzones', test_availability_zone.base_path
        )
        self.assertTrue(test_availability_zone.allow_create)
        self.assertTrue(test_availability_zone.allow_fetch)
        self.assertTrue(test_availability_zone.allow_commit)
        self.assertTrue(test_availability_zone.allow_delete)
        self.assertTrue(test_availability_zone.allow_list)

    def test_make_it(self):
        test_availability_zone = availability_zone.AvailabilityZone(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], test_availability_zone.name)
        self.assertEqual(
            EXAMPLE['description'], test_availability_zone.description
        )
        self.assertFalse(test_availability_zone.is_enabled)
        self.assertEqual(
            EXAMPLE['availability_zone_profile_id'],
            test_availability_zone.availability_zone_profile_id,
        )

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'name': 'name',
                'description': 'description',
                'is_enabled': 'enabled',
                'availability_zone_profile_id': 'availability_zone_profile_id',
            },
            test_availability_zone._query_mapping._mapping,
        )
