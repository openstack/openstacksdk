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

from openstack.network.v2 import metering_label_rule

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'direction': '1',
    'excluded': False,
    'id': IDENTIFIER,
    'metering_label_id': '4',
    'tenant_id': '5',
    'remote_ip_prefix': '6',
}


class TestMeteringLabelRule(base.TestCase):

    def test_basic(self):
        sot = metering_label_rule.MeteringLabelRule()
        self.assertEqual('metering_label_rule', sot.resource_key)
        self.assertEqual('metering_label_rules', sot.resources_key)
        self.assertEqual('/metering/metering-label-rules', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = metering_label_rule.MeteringLabelRule(**EXAMPLE)
        self.assertEqual(EXAMPLE['direction'], sot.direction)
        self.assertFalse(sot.is_excluded)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['metering_label_id'], sot.metering_label_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['remote_ip_prefix'], sot.remote_ip_prefix)

    def test_make_it_source_and_destination(self):
        custom_example = EXAMPLE.copy()
        custom_example["source_ip_prefix"] = "192.168.0.11/32"
        custom_example["destination_ip_prefix"] = "0.0.0.0/0"

        sot = metering_label_rule.MeteringLabelRule(**custom_example)
        self.assertEqual(custom_example['direction'], sot.direction)
        self.assertFalse(sot.is_excluded)
        self.assertEqual(custom_example['id'], sot.id)
        self.assertEqual(
            custom_example['metering_label_id'], sot.metering_label_id)
        self.assertEqual(custom_example['tenant_id'], sot.project_id)
        self.assertEqual(
            custom_example['remote_ip_prefix'], sot.remote_ip_prefix)

        self.assertEqual(
            custom_example['source_ip_prefix'], sot.source_ip_prefix)
        self.assertEqual(
            custom_example['destination_ip_prefix'], sot.destination_ip_prefix)
