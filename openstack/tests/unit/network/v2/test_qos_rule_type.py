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

from openstack.network.v2 import qos_rule_type

EXAMPLE = {
    'type': 'bandwidth_limit',
}


class TestQoSRuleType(testtools.TestCase):

    def test_basic(self):
        sot = qos_rule_type.QoSRuleType()
        self.assertEqual('rule_type', sot.resource_key)
        self.assertEqual('rule_types', sot.resources_key)
        self.assertEqual('/qos/rule-types', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = qos_rule_type.QoSRuleType(**EXAMPLE)
        self.assertEqual(EXAMPLE['type'], sot.type)
