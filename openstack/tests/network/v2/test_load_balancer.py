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

from openstack.network.v2 import load_balancer

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'description': '2',
    'id': IDENTIFIER,
    'name': '4',
    'tenant_id': '5',
    'status': '6',
}


class TestLoadBalancer(testtools.TestCase):

    def test_basic(self):
        sot = load_balancer.LoadBalancer()
        self.assertEqual('loadbalancer', sot.resource_key)
        self.assertEqual('loadbalancers', sot.resources_key)
        self.assertEqual('/loadbalancers', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = load_balancer.LoadBalancer(EXAMPLE)
        self.assertEqual(EXAMPLE['admin_state_up'], sot.admin_state_up)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
