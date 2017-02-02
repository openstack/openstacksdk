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

from openstack.load_balancer.v2 import load_balancer

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'created_at': '3',
    'description': 'fake_description',
    'id': IDENTIFIER,
    'listeners': [{'id', '4'}],
    'name': 'test_load_balancer',
    'operating_status': '6',
    'provisioning_status': '7',
    'project_id': '8',
    'vip_address': '9',
    'vip_subnet_id': '10',
    'vip_port_id': '11',
    'pools': [{'id', '13'}],
}


class TestLoadBalancer(testtools.TestCase):

    def test_basic(self):
        test_load_balancer = load_balancer.LoadBalancer()
        self.assertEqual('loadbalancer', test_load_balancer.resource_key)
        self.assertEqual('loadbalancers', test_load_balancer.resources_key)
        self.assertEqual('/loadbalancers', test_load_balancer.base_path)
        self.assertEqual('load_balancer',
                         test_load_balancer.service.service_type)
        self.assertTrue(test_load_balancer.allow_create)
        self.assertTrue(test_load_balancer.allow_get)
        self.assertTrue(test_load_balancer.allow_delete)
        self.assertTrue(test_load_balancer.allow_list)

    def test_make_it(self):
        test_load_balancer = load_balancer.LoadBalancer(**EXAMPLE)
        self.assertTrue(test_load_balancer.is_admin_state_up)
        self.assertEqual(EXAMPLE['created_at'], test_load_balancer.created_at),
        self.assertEqual(EXAMPLE['description'],
                         test_load_balancer.description)
        self.assertEqual(EXAMPLE['id'], test_load_balancer.id)
        self.assertEqual(EXAMPLE['listeners'], test_load_balancer.listeners)
        self.assertEqual(EXAMPLE['name'], test_load_balancer.name)
        self.assertEqual(EXAMPLE['operating_status'],
                         test_load_balancer.operating_status)
        self.assertEqual(EXAMPLE['provisioning_status'],
                         test_load_balancer.provisioning_status)
        self.assertEqual(EXAMPLE['project_id'], test_load_balancer.project_id)
        self.assertEqual(EXAMPLE['vip_address'],
                         test_load_balancer.vip_address)
        self.assertEqual(EXAMPLE['vip_subnet_id'],
                         test_load_balancer.vip_subnet_id)
        self.assertEqual(EXAMPLE['vip_port_id'],
                         test_load_balancer.vip_port_id)
        self.assertEqual(EXAMPLE['pools'], test_load_balancer.pools)
