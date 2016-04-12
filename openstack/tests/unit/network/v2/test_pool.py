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

from openstack.network.v2 import pool

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'description': '2',
    'healthmonitor_id': '3',
    'id': IDENTIFIER,
    'lb_algorithm': '5',
    'listeners': [{'id': '6'}],
    'members': [{'id': '7'}],
    'name': '8',
    'tenant_id': '9',
    'protocol': '10',
    'session_persistence': '11',
    'loadbalancers': [{'id': '12'}],
}


class TestPool(testtools.TestCase):

    def test_basic(self):
        sot = pool.Pool()
        self.assertEqual('pool', sot.resource_key)
        self.assertEqual('pools', sot.resources_key)
        self.assertEqual('/lbaas/pools', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = pool.Pool(EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['healthmonitor_id'], sot.health_monitor_id)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['lb_algorithm'], sot.lb_algorithm)
        self.assertEqual(EXAMPLE['listeners'], sot.listener_ids)
        self.assertEqual(EXAMPLE['members'], sot.member_ids)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['protocol'], sot.protocol)
        self.assertEqual(EXAMPLE['session_persistence'],
                         sot.session_persistence)
        self.assertEqual(EXAMPLE['loadbalancers'], sot.load_balancer_ids)
