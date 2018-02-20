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

from openstack.load_balancer.v2 import listener

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'connection_limit': '2',
    'default_pool_id': uuid.uuid4(),
    'description': 'test description',
    'id': IDENTIFIER,
    'insert_headers': {"X-Forwarded-For": "true"},
    'l7policies': [{'id': uuid.uuid4()}],
    'loadbalancers': [{'id': uuid.uuid4()}],
    'name': 'test_listener',
    'project_id': uuid.uuid4(),
    'protocol': 'TEST_PROTOCOL',
    'protocol_port': 10,
    'default_tls_container_ref': ('http://198.51.100.10:9311/v1/containers/'
                                  'a570068c-d295-4780-91d4-3046a325db51'),
    'sni_container_refs': [],
    'created_at': '2017-07-17T12:14:57.233772',
    'updated_at': '2017-07-17T12:16:57.233772',
    'operating_status': 'ONLINE',
    'provisioning_status': 'ACTIVE',
}


class TestListener(base.TestCase):

    def test_basic(self):
        test_listener = listener.Listener()
        self.assertEqual('listener', test_listener.resource_key)
        self.assertEqual('listeners', test_listener.resources_key)
        self.assertEqual('/v2.0/lbaas/listeners', test_listener.base_path)
        self.assertEqual('load-balancer', test_listener.service.service_type)
        self.assertTrue(test_listener.allow_create)
        self.assertTrue(test_listener.allow_get)
        self.assertTrue(test_listener.allow_update)
        self.assertTrue(test_listener.allow_delete)
        self.assertTrue(test_listener.allow_list)

    def test_make_it(self):
        test_listener = listener.Listener(**EXAMPLE)
        self.assertTrue(test_listener.is_admin_state_up)
        self.assertEqual(EXAMPLE['connection_limit'],
                         test_listener.connection_limit)
        self.assertEqual(EXAMPLE['default_pool_id'],
                         test_listener.default_pool_id)
        self.assertEqual(EXAMPLE['description'], test_listener.description)
        self.assertEqual(EXAMPLE['id'], test_listener.id)
        self.assertEqual(EXAMPLE['insert_headers'],
                         test_listener.insert_headers)
        self.assertEqual(EXAMPLE['l7policies'],
                         test_listener.l7_policies)
        self.assertEqual(EXAMPLE['loadbalancers'],
                         test_listener.load_balancers)
        self.assertEqual(EXAMPLE['name'], test_listener.name)
        self.assertEqual(EXAMPLE['project_id'], test_listener.project_id)
        self.assertEqual(EXAMPLE['protocol'], test_listener.protocol)
        self.assertEqual(EXAMPLE['protocol_port'], test_listener.protocol_port)
        self.assertEqual(EXAMPLE['default_tls_container_ref'],
                         test_listener.default_tls_container_ref)
        self.assertEqual(EXAMPLE['sni_container_refs'],
                         test_listener.sni_container_refs)
        self.assertEqual(EXAMPLE['created_at'], test_listener.created_at)
        self.assertEqual(EXAMPLE['updated_at'], test_listener.updated_at)
        self.assertEqual(EXAMPLE['provisioning_status'],
                         test_listener.provisioning_status)
        self.assertEqual(EXAMPLE['operating_status'],
                         test_listener.operating_status)
