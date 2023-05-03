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

from openstack.network.v2 import availability_zone
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'name': '1',
    'resource': '2',
    'state': '3',
}


class TestAvailabilityZone(base.TestCase):
    def test_basic(self):
        sot = availability_zone.AvailabilityZone()
        self.assertEqual('availability_zone', sot.resource_key)
        self.assertEqual('availability_zones', sot.resources_key)
        self.assertEqual('/availability_zones', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = availability_zone.AvailabilityZone(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['resource'], sot.resource)
        self.assertEqual(EXAMPLE['state'], sot.state)
