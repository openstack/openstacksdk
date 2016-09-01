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

from openstack.network.v2 import metering_label

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'description': '1',
    'id': IDENTIFIER,
    'name': '3',
    'tenant_id': '4',
    'shared': False,
}


class TestMeteringLabel(testtools.TestCase):

    def test_basic(self):
        sot = metering_label.MeteringLabel()
        self.assertEqual('metering_label', sot.resource_key)
        self.assertEqual('metering_labels', sot.resources_key)
        self.assertEqual('/metering/metering-labels', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = metering_label.MeteringLabel(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['shared'], sot.is_shared)
