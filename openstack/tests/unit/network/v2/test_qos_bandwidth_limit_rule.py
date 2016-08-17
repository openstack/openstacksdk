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
import uuid

from openstack.network.v2 import qos_bandwidth_limit_rule

EXAMPLE = {
    'id': 'IDENTIFIER',
    'qos_policy_id': 'qos-policy-' + uuid.uuid4().hex,
    'max_kbps': 1500,
    'max_burst_kbps': 1200,
    'direction': 'egress',
}


class TestQoSBandwidthLimitRule(testtools.TestCase):

    def test_basic(self):
        sot = qos_bandwidth_limit_rule.QoSBandwidthLimitRule()
        self.assertEqual('bandwidth_limit_rule', sot.resource_key)
        self.assertEqual('bandwidth_limit_rules', sot.resources_key)
        self.assertEqual(
            '/qos/policies/%(qos_policy_id)s/bandwidth_limit_rules',
            sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = qos_bandwidth_limit_rule.QoSBandwidthLimitRule(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['qos_policy_id'], sot.qos_policy_id)
        self.assertEqual(EXAMPLE['max_kbps'], sot.max_kbps)
        self.assertEqual(EXAMPLE['max_burst_kbps'], sot.max_burst_kbps)
        self.assertEqual(EXAMPLE['direction'], sot.direction)
