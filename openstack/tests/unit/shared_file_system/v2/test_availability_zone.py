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

from openstack.shared_file_system.v2 import availability_zone as az
from openstack.tests.unit import base

IDENTIFIER = '08a87d37-5ca2-4308-86c5-cba06d8d796c'
EXAMPLE = {
    "id": IDENTIFIER,
    "name": "nova",
    "created_at": "2021-01-21T20:13:55.000000",
    "updated_at": None,
}


class TestAvailabilityZone(base.TestCase):
    def test_basic(self):
        az_resource = az.AvailabilityZone()
        self.assertEqual('availability_zones', az_resource.resources_key)
        self.assertEqual('/availability-zones', az_resource.base_path)
        self.assertTrue(az_resource.allow_list)

    def test_make_availability_zone(self):
        az_resource = az.AvailabilityZone(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], az_resource.id)
        self.assertEqual(EXAMPLE['name'], az_resource.name)
        self.assertEqual(EXAMPLE['created_at'], az_resource.created_at)
        self.assertEqual(EXAMPLE['updated_at'], az_resource.updated_at)
