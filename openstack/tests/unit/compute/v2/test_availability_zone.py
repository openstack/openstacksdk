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

from openstack.compute.v2 import availability_zone as az

IDENTIFIER = 'IDENTIFIER'
BASIC_EXAMPLE = {
    'id': IDENTIFIER,
    'zoneState': 'available',
    'hosts': 'host1',
    'zoneName': 'zone1'
}


class TestAvailabilityZone(testtools.TestCase):

    def test_basic(self):
        sot = az.AvailabilityZone()
        self.assertEqual('availability_zone', sot.resource_key)
        self.assertEqual('availabilityZoneInfo', sot.resources_key)
        self.assertEqual('/os-availability-zone', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertEqual('compute', sot.service.service_type)

    def test_make_basic(self):
        sot = az.AvailabilityZone(BASIC_EXAMPLE)
        self.assertEqual(BASIC_EXAMPLE['id'], sot.id)
        self.assertEqual(BASIC_EXAMPLE['zoneState'], sot.state)
        self.assertEqual(BASIC_EXAMPLE['hosts'], sot.hosts)
        self.assertEqual(BASIC_EXAMPLE['zoneName'], sot.name)
