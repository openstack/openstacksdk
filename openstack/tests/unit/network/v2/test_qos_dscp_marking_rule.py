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
import uuid

from openstack.network.v2 import qos_dscp_marking_rule

EXAMPLE = {
    'id': 'IDENTIFIER',
    'qos_policy_id': 'qos-policy-' + uuid.uuid4().hex,
    'dscp_mark': 40,
}


class TestQoSDSCPMarkingRule(base.TestCase):

    def test_basic(self):
        sot = qos_dscp_marking_rule.QoSDSCPMarkingRule()
        self.assertEqual('dscp_marking_rule', sot.resource_key)
        self.assertEqual('dscp_marking_rules', sot.resources_key)
        self.assertEqual('/qos/policies/%(qos_policy_id)s/dscp_marking_rules',
                         sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = qos_dscp_marking_rule.QoSDSCPMarkingRule(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['qos_policy_id'], sot.qos_policy_id)
        self.assertEqual(EXAMPLE['dscp_mark'], sot.dscp_mark)
