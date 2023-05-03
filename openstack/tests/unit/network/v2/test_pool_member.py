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

from openstack.network.v2 import pool_member
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'address': '1',
    'admin_state_up': True,
    'id': IDENTIFIER,
    'project_id': '4',
    'protocol_port': 5,
    'subnet_id': '6',
    'weight': 7,
    'name': '8',
    'pool_id': 'FAKE_POOL',
}


class TestPoolMember(base.TestCase):
    def test_basic(self):
        sot = pool_member.PoolMember()
        self.assertEqual('member', sot.resource_key)
        self.assertEqual('members', sot.resources_key)
        self.assertEqual('/lbaas/pools/%(pool_id)s/members', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = pool_member.PoolMember(**EXAMPLE)
        self.assertEqual(EXAMPLE['address'], sot.address)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['protocol_port'], sot.protocol_port)
        self.assertEqual(EXAMPLE['subnet_id'], sot.subnet_id)
        self.assertEqual(EXAMPLE['weight'], sot.weight)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['pool_id'], sot.pool_id)
