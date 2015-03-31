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

from openstack.network.v2 import listener

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'connection_limit': '1',
    'default_pool_id': '2',
    'description': '3',
    'id': IDENTIFIER,
    'load_balancer_id': '5',
    'name': '6',
    'tenant_id': '7',
    'protocol': '8',
    'protocol_port': '9',
}


class TestListener(testtools.TestCase):

    def test_basic(self):
        sot = listener.Listener()
        self.assertEqual('listener', sot.resource_key)
        self.assertEqual('listeners', sot.resources_key)
        self.assertEqual('/listeners', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = listener.Listener(EXAMPLE)
        self.assertEqual(EXAMPLE['connection_limit'], sot.connection_limit)
        self.assertEqual(EXAMPLE['default_pool_id'], sot.default_pool_id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['load_balancer_id'], sot.load_balancer_id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['protocol'], sot.protocol)
        self.assertEqual(EXAMPLE['protocol_port'], sot.protocol_port)
