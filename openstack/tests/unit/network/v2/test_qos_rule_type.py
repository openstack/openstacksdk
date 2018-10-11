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

from openstack.network.v2 import qos_rule_type

EXAMPLE = {
    'type': 'bandwidth_limit',
    'drivers': [{
        'name': 'openvswitch',
        'supported_parameters': [{
            'parameter_values': {'start': 0, 'end': 2147483647},
            'parameter_type': 'range',
            'parameter_name': 'max_kbps'
        }, {
            'parameter_values': ['ingress', 'egress'],
            'parameter_type': 'choices',
            'parameter_name': 'direction'
        }, {
            'parameter_values': {'start': 0, 'end': 2147483647},
            'parameter_type': 'range',
            'parameter_name': 'max_burst_kbps'
        }]
    }]
}


class TestQoSRuleType(base.TestCase):

    def test_basic(self):
        sot = qos_rule_type.QoSRuleType()
        self.assertEqual('rule_type', sot.resource_key)
        self.assertEqual('rule_types', sot.resources_key)
        self.assertEqual('/qos/rule-types', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = qos_rule_type.QoSRuleType(**EXAMPLE)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['drivers'], sot.drivers)
