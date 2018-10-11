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

from openstack.load_balancer.v2 import l7_rule

EXAMPLE = {
    'admin_state_up': True,
    'compare_type': 'REGEX',
    'created_at': '2017-08-17T12:14:57.233772',
    'id': uuid.uuid4(),
    'invert': False,
    'key': 'my_cookie',
    'l7_policy_id': uuid.uuid4(),
    'operating_status': 'ONLINE',
    'project_id': uuid.uuid4(),
    'provisioning_status': 'ACTIVE',
    'type': 'COOKIE',
    'updated_at': '2017-08-17T12:16:57.233772',
    'value': 'chocolate'
}


class TestL7Rule(base.TestCase):

    def test_basic(self):
        test_l7rule = l7_rule.L7Rule()
        self.assertEqual('rule', test_l7rule.resource_key)
        self.assertEqual('rules', test_l7rule.resources_key)
        self.assertEqual('/lbaas/l7policies/%(l7policy_id)s/rules',
                         test_l7rule.base_path)
        self.assertTrue(test_l7rule.allow_create)
        self.assertTrue(test_l7rule.allow_fetch)
        self.assertTrue(test_l7rule.allow_commit)
        self.assertTrue(test_l7rule.allow_delete)
        self.assertTrue(test_l7rule.allow_list)

    def test_make_it(self):
        test_l7rule = l7_rule.L7Rule(**EXAMPLE)
        self.assertTrue(test_l7rule.is_admin_state_up)
        self.assertEqual(EXAMPLE['compare_type'], test_l7rule.compare_type)
        self.assertEqual(EXAMPLE['created_at'], test_l7rule.created_at)
        self.assertEqual(EXAMPLE['id'], test_l7rule.id)
        self.assertEqual(EXAMPLE['invert'], test_l7rule.invert)
        self.assertEqual(EXAMPLE['key'], test_l7rule.key)
        self.assertEqual(EXAMPLE['l7_policy_id'], test_l7rule.l7_policy_id)
        self.assertEqual(EXAMPLE['operating_status'],
                         test_l7rule.operating_status)
        self.assertEqual(EXAMPLE['project_id'], test_l7rule.project_id)
        self.assertEqual(EXAMPLE['provisioning_status'],
                         test_l7rule.provisioning_status)
        self.assertEqual(EXAMPLE['type'], test_l7rule.type)
        self.assertEqual(EXAMPLE['updated_at'], test_l7rule.updated_at)
        self.assertEqual(EXAMPLE['value'], test_l7rule.rule_value)
