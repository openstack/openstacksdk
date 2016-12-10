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
    'listeners': [{'id', '4'}],
    'name': '5',
    'operating_status': '6',
    'provisioning_status': '7',
    'tenant_id': '8',
    'vip_address': '9',
    'vip_subnet_id': '10',
    'vip_port_id': '11',
    'provider': '12',
    'pools': [{'id', '13'}],
}


class TestLoadBalancer(testtools.TestCase):

    def test_basic(self):
        sot = load_balancer.LoadBalancer()
        self.assertEqual('loadbalancer', sot.resource_key)
        self.assertEqual('loadbalancers', sot.resources_key)
        self.assertEqual('/lbaas/loadbalancers', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = load_balancer.LoadBalancer(**EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['listeners'], sot.listener_ids)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['operating_status'], sot.operating_status)
        self.assertEqual(EXAMPLE['provisioning_status'],
                         sot.provisioning_status)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['vip_address'], sot.vip_address)
        self.assertEqual(EXAMPLE['vip_subnet_id'], sot.vip_subnet_id)
        self.assertEqual(EXAMPLE['vip_port_id'], sot.vip_port_id)
        self.assertEqual(EXAMPLE['provider'], sot.provider)
        self.assertEqual(EXAMPLE['pools'], sot.pool_ids)
