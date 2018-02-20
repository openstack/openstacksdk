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

from openstack.load_balancer.v2 import pool

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'name': 'test_pool',
    'description': 'fake_description',
    'admin_state_up': True,
    'provisioning_status': 'ACTIVE',
    'operating_status': 'ONLINE',
    'protocol': 'HTTP',
    'listener_id': uuid.uuid4(),
    'loadbalancer_id': uuid.uuid4(),
    'lb_algorithm': 'ROUND_ROBIN',
    'session_persistence': {"type": "SOURCE_IP"},
    'project_id': uuid.uuid4(),
    'loadbalancers': [{'id': uuid.uuid4()}],
    'listeners': [{'id': uuid.uuid4()}],
    'created_at': '2017-07-17T12:14:57.233772',
    'updated_at': '2017-07-17T12:16:57.233772',
    'health_monitor': 'healthmonitor',
    'health_monitor_id': uuid.uuid4(),
    'members': [{'id': uuid.uuid4()}]
}


class TestPool(base.TestCase):

    def test_basic(self):
        test_pool = pool.Pool()
        self.assertEqual('pool', test_pool.resource_key)
        self.assertEqual('pools', test_pool.resources_key)
        self.assertEqual('/v2.0/lbaas/pools', test_pool.base_path)
        self.assertEqual('load-balancer',
                         test_pool.service.service_type)
        self.assertTrue(test_pool.allow_create)
        self.assertTrue(test_pool.allow_get)
        self.assertTrue(test_pool.allow_delete)
        self.assertTrue(test_pool.allow_list)
        self.assertTrue(test_pool.allow_update)

    def test_make_it(self):
        test_pool = pool.Pool(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], test_pool.name),
        self.assertEqual(EXAMPLE['description'],
                         test_pool.description)
        self.assertEqual(EXAMPLE['admin_state_up'],
                         test_pool.is_admin_state_up)
        self.assertEqual(EXAMPLE['provisioning_status'],
                         test_pool.provisioning_status)
        self.assertEqual(EXAMPLE['protocol'], test_pool.protocol)
        self.assertEqual(EXAMPLE['operating_status'],
                         test_pool.operating_status)
        self.assertEqual(EXAMPLE['listener_id'], test_pool.listener_id)
        self.assertEqual(EXAMPLE['loadbalancer_id'],
                         test_pool.loadbalancer_id)
        self.assertEqual(EXAMPLE['lb_algorithm'],
                         test_pool.lb_algorithm)
        self.assertEqual(EXAMPLE['session_persistence'],
                         test_pool.session_persistence)
        self.assertEqual(EXAMPLE['project_id'],
                         test_pool.project_id)
        self.assertEqual(EXAMPLE['loadbalancers'],
                         test_pool.loadbalancers)
        self.assertEqual(EXAMPLE['listeners'],
                         test_pool.listeners)
        self.assertEqual(EXAMPLE['created_at'], test_pool.created_at)
        self.assertEqual(EXAMPLE['updated_at'], test_pool.updated_at)
        self.assertEqual(EXAMPLE['health_monitor_id'],
                         test_pool.health_monitor_id)
        self.assertEqual(EXAMPLE['members'], test_pool.members)
