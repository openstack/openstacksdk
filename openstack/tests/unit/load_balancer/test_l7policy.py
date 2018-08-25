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

from openstack.load_balancer.v2 import l7_policy

EXAMPLE = {
    'action': 'REJECT',
    'admin_state_up': True,
    'created_at': '2017-07-17T12:14:57.233772',
    'description': 'test_description',
    'id': uuid.uuid4(),
    'listener_id': uuid.uuid4(),
    'name': 'test_l7_policy',
    'operating_status': 'ONLINE',
    'position': 7,
    'project_id': uuid.uuid4(),
    'provisioning_status': 'ACTIVE',
    'redirect_pool_id': uuid.uuid4(),
    'redirect_url': '/test_url',
    'rules': [{'id': uuid.uuid4()}],
    'updated_at': '2017-07-17T12:16:57.233772',
}


class TestL7Policy(base.TestCase):

    def test_basic(self):
        test_l7_policy = l7_policy.L7Policy()
        self.assertEqual('l7policy', test_l7_policy.resource_key)
        self.assertEqual('l7policies', test_l7_policy.resources_key)
        self.assertEqual('/lbaas/l7policies', test_l7_policy.base_path)
        self.assertTrue(test_l7_policy.allow_create)
        self.assertTrue(test_l7_policy.allow_fetch)
        self.assertTrue(test_l7_policy.allow_commit)
        self.assertTrue(test_l7_policy.allow_delete)
        self.assertTrue(test_l7_policy.allow_list)

    def test_make_it(self):
        test_l7_policy = l7_policy.L7Policy(**EXAMPLE)
        self.assertTrue(test_l7_policy.is_admin_state_up)
        self.assertEqual(EXAMPLE['action'], test_l7_policy.action)
        self.assertEqual(EXAMPLE['created_at'], test_l7_policy.created_at)
        self.assertEqual(EXAMPLE['description'], test_l7_policy.description)
        self.assertEqual(EXAMPLE['id'], test_l7_policy.id)
        self.assertEqual(EXAMPLE['listener_id'], test_l7_policy.listener_id)
        self.assertEqual(EXAMPLE['name'], test_l7_policy.name)
        self.assertEqual(EXAMPLE['operating_status'],
                         test_l7_policy.operating_status)
        self.assertEqual(EXAMPLE['position'], test_l7_policy.position)
        self.assertEqual(EXAMPLE['project_id'], test_l7_policy.project_id)
        self.assertEqual(EXAMPLE['provisioning_status'],
                         test_l7_policy.provisioning_status)
        self.assertEqual(EXAMPLE['redirect_pool_id'],
                         test_l7_policy.redirect_pool_id)
        self.assertEqual(EXAMPLE['redirect_url'], test_l7_policy.redirect_url)
        self.assertEqual(EXAMPLE['rules'], test_l7_policy.rules)
        self.assertEqual(EXAMPLE['updated_at'], test_l7_policy.updated_at)
