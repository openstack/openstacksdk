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

from openstack.load_balancer.v2 import member

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'address': '192.0.2.16',
    'admin_state_up': True,
    'id': IDENTIFIER,
    'monitor_address': '192.0.2.17',
    'monitor_port': 9,
    'name': 'test_member',
    'pool_id': uuid.uuid4(),
    'project_id': uuid.uuid4(),
    'protocol_port': 5,
    'subnet_id': uuid.uuid4(),
    'weight': 7,
    'backup': False,
}


class TestPoolMember(base.TestCase):

    def test_basic(self):
        test_member = member.Member()
        self.assertEqual('member', test_member.resource_key)
        self.assertEqual('members', test_member.resources_key)
        self.assertEqual('/lbaas/pools/%(pool_id)s/members',
                         test_member.base_path)
        self.assertTrue(test_member.allow_create)
        self.assertTrue(test_member.allow_fetch)
        self.assertTrue(test_member.allow_commit)
        self.assertTrue(test_member.allow_delete)
        self.assertTrue(test_member.allow_list)

    def test_make_it(self):
        test_member = member.Member(**EXAMPLE)
        self.assertEqual(EXAMPLE['address'], test_member.address)
        self.assertTrue(test_member.is_admin_state_up)
        self.assertEqual(EXAMPLE['id'], test_member.id)
        self.assertEqual(EXAMPLE['monitor_address'],
                         test_member.monitor_address)
        self.assertEqual(EXAMPLE['monitor_port'], test_member.monitor_port)
        self.assertEqual(EXAMPLE['name'], test_member.name)
        self.assertEqual(EXAMPLE['pool_id'], test_member.pool_id)
        self.assertEqual(EXAMPLE['project_id'], test_member.project_id)
        self.assertEqual(EXAMPLE['protocol_port'], test_member.protocol_port)
        self.assertEqual(EXAMPLE['subnet_id'], test_member.subnet_id)
        self.assertEqual(EXAMPLE['weight'], test_member.weight)
        self.assertFalse(test_member.backup)
