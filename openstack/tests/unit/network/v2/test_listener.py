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

from openstack.network.v2 import listener
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'connection_limit': '2',
    'default_pool_id': '3',
    'description': '4',
    'id': IDENTIFIER,
    'loadbalancers': [{'id': '6'}],
    'loadbalancer_id': '6',
    'name': '7',
    'project_id': '8',
    'protocol': '9',
    'protocol_port': '10',
    'default_tls_container_ref': '11',
    'sni_container_refs': [],
}


class TestListener(base.TestCase):
    def test_basic(self):
        sot = listener.Listener()
        self.assertEqual('listener', sot.resource_key)
        self.assertEqual('listeners', sot.resources_key)
        self.assertEqual('/lbaas/listeners', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = listener.Listener(**EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['connection_limit'], sot.connection_limit)
        self.assertEqual(EXAMPLE['default_pool_id'], sot.default_pool_id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['loadbalancers'], sot.load_balancer_ids)
        self.assertEqual(EXAMPLE['loadbalancer_id'], sot.load_balancer_id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['protocol'], sot.protocol)
        self.assertEqual(EXAMPLE['protocol_port'], sot.protocol_port)
        self.assertEqual(
            EXAMPLE['default_tls_container_ref'], sot.default_tls_container_ref
        )
        self.assertEqual(EXAMPLE['sni_container_refs'], sot.sni_container_refs)
