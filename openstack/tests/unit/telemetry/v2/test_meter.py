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

from openstack.telemetry.v2 import meter

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'meter_id': IDENTIFIER,
    'name': 'instance',
    'project_id': '123',
    'resource_id': '456',
    'source': 'abc',
    'type': 'def',
    'unit': 'ghi',
    'user_id': '789'
}


class TestMeter(testtools.TestCase):

    def test_basic(self):
        sot = meter.Meter()
        self.assertEqual('meter', sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/meters', sot.base_path)
        self.assertEqual('metering', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = meter.Meter(EXAMPLE)
        self.assertEqual(EXAMPLE['meter_id'], sot.id)
        self.assertEqual(EXAMPLE['meter_id'], sot.meter_id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['resource_id'], sot.resource_id)
        self.assertEqual(EXAMPLE['source'], sot.source)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['unit'], sot.unit)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
