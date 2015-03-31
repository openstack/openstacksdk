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

from openstack.network.v2 import pool_member

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'address': '1',
    'admin_state_up': True,
    'id': IDENTIFIER,
    'tenant_id': '4',
    'protocol_port': 5,
    'status': '6',
    'subnet_id': '7',
    'weight': 8,
}


class TestPoolMember(testtools.TestCase):

    def test_basic(self):
        sot = pool_member.PoolMember()
        self.assertEqual('member', sot.resource_key)
        self.assertEqual('members', sot.resources_key)
        self.assertEqual('/pools/%(pool_id)s/members', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = pool_member.PoolMember(EXAMPLE)
        self.assertEqual(EXAMPLE['address'], sot.address)
        self.assertEqual(EXAMPLE['admin_state_up'], sot.admin_state_up)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['protocol_port'], sot.protocol_port)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['subnet_id'], sot.subnet_id)
        self.assertEqual(EXAMPLE['weight'], sot.weight)
