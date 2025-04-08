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

import uuid

from openstack.network.v2 import qos_packet_rate_limit_rule
from openstack.tests.unit import base


EXAMPLE = {
    'id': 'IDENTIFIER',
    'qos_policy_id': 'qos-policy-' + uuid.uuid4().hex,
    'max_kpps': 1600,
    'max_burst_kpps': 1300,
    'direction': 'any',
}


class TestQoSBandwidthLimitRule(base.TestCase):
    def test_basic(self):
        sot = qos_packet_rate_limit_rule.QoSPacketRateLimitRule()
        self.assertEqual('packet_rate_limit_rule', sot.resource_key)
        self.assertEqual('packet_rate_limit_rules', sot.resources_key)
        self.assertEqual(
            '/qos/policies/%(qos_policy_id)s/packet_rate_limit_rules',
            sot.base_path,
        )
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = qos_packet_rate_limit_rule.QoSPacketRateLimitRule(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['qos_policy_id'], sot.qos_policy_id)
        self.assertEqual(EXAMPLE['max_kpps'], sot.max_kpps)
        self.assertEqual(EXAMPLE['max_burst_kpps'], sot.max_burst_kpps)
        self.assertEqual(EXAMPLE['direction'], sot.direction)
