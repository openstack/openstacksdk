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

from openstack.network.v2 import metering_label_rule

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'direction': '1',
    'excluded': False,
    'id': IDENTIFIER,
    'metering_label_id': '4',
    'remote_ip_prefix': '5',
}


class TestMeteringLabelRule(testtools.TestCase):

    def test_basic(self):
        sot = metering_label_rule.MeteringLabelRule()
        self.assertEqual('metering_label_rule', sot.resource_key)
        self.assertEqual('metering_label_rules', sot.resources_key)
        self.assertEqual('/metering-label-rules', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = metering_label_rule.MeteringLabelRule(EXAMPLE)
        self.assertEqual(EXAMPLE['direction'], sot.direction)
        self.assertFalse(sot.is_excluded)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['metering_label_id'], sot.metering_label_id)
        self.assertEqual(EXAMPLE['remote_ip_prefix'], sot.remote_ip_prefix)
