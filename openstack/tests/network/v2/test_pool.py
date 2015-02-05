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
    'members': '6',
    'name': '7',
    'tenant_id': '8',
    'protocol': '9',
    'session_persistence': '10',
    'status': '11',
}


class TestPool(testtools.TestCase):

    def test_basic(self):
        sot = pool.Pool()
        self.assertEqual('pool', sot.resource_key)
        self.assertEqual('pools', sot.resources_key)
        self.assertEqual('/pools', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = pool.Pool(EXAMPLE)
        self.assertEqual(EXAMPLE['admin_state_up'], sot.admin_state_up)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['healthmonitor_id'], sot.healthmonitor_id)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['lb_algorithm'], sot.lb_algorithm)
        self.assertEqual(EXAMPLE['members'], sot.members)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['protocol'], sot.protocol)
        self.assertEqual(EXAMPLE['session_persistence'],
                         sot.session_persistence)
        self.assertEqual(EXAMPLE['status'], sot.status)
