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

from openstack.block_storage.v3 import availability_zone as az
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "id": IDENTIFIER,
    "zoneState": {"available": True},
    "zoneName": "zone1",
}


class TestAvailabilityZone(base.TestCase):
    def test_basic(self):
        sot = az.AvailabilityZone()
        self.assertEqual('availabilityZoneInfo', sot.resources_key)
        self.assertEqual('/os-availability-zone', sot.base_path)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = az.AvailabilityZone(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['zoneState'], sot.state)
        self.assertEqual(EXAMPLE['zoneName'], sot.name)
