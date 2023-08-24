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

import uuid

from openstack.load_balancer.v2 import listener
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'allowed_cidrs': ['192.168.1.0/24'],
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
    'default_tls_container_ref': (
        'http://198.51.100.10:9311/v1/containers/'
        'a570068c-d295-4780-91d4-3046a325db51'
    ),
    'sni_container_refs': [],
    'created_at': '2017-07-17T12:14:57.233772',
    'updated_at': '2017-07-17T12:16:57.233772',
    'operating_status': 'ONLINE',
    'provisioning_status': 'ACTIVE',
    'hsts_include_subdomains': True,
    'hsts_max_age': 30_000_000,
    'hsts_preload': False,
    'timeout_client_data': 50000,
    'timeout_member_connect': 5000,
    'timeout_member_data': 50000,
    'timeout_tcp_inspect': 0,
    'tls_ciphers': 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256',
    'tls_versions': ['TLSv1.1', 'TLSv1.2'],
    'alpn_protocols': ['h2', 'http/1.1', 'http/1.0'],
}

EXAMPLE_STATS = {
    'active_connections': 1,
    'bytes_in': 2,
    'bytes_out': 3,
    'request_errors': 4,
    'total_connections': 5,
}


class TestListener(base.TestCase):
    def test_basic(self):
        test_listener = listener.Listener()
        self.assertEqual('listener', test_listener.resource_key)
        self.assertEqual('listeners', test_listener.resources_key)
        self.assertEqual('/lbaas/listeners', test_listener.base_path)
        self.assertTrue(test_listener.allow_create)
        self.assertTrue(test_listener.allow_fetch)
        self.assertTrue(test_listener.allow_commit)
        self.assertTrue(test_listener.allow_delete)
        self.assertTrue(test_listener.allow_list)

    def test_make_it(self):
        test_listener = listener.Listener(**EXAMPLE)
        self.assertTrue(test_listener.is_admin_state_up)
        self.assertEqual(EXAMPLE['allowed_cidrs'], test_listener.allowed_cidrs)
        self.assertEqual(
            EXAMPLE['connection_limit'], test_listener.connection_limit
        )
        self.assertEqual(
            EXAMPLE['default_pool_id'], test_listener.default_pool_id
        )
        self.assertEqual(EXAMPLE['description'], test_listener.description)
        self.assertEqual(EXAMPLE['id'], test_listener.id)
        self.assertEqual(
            EXAMPLE['insert_headers'], test_listener.insert_headers
        )
        self.assertEqual(EXAMPLE['l7policies'], test_listener.l7_policies)
        self.assertEqual(
            EXAMPLE['loadbalancers'], test_listener.load_balancers
        )
        self.assertEqual(EXAMPLE['name'], test_listener.name)
        self.assertEqual(EXAMPLE['project_id'], test_listener.project_id)
        self.assertEqual(EXAMPLE['protocol'], test_listener.protocol)
        self.assertEqual(EXAMPLE['protocol_port'], test_listener.protocol_port)
        self.assertEqual(
            EXAMPLE['default_tls_container_ref'],
            test_listener.default_tls_container_ref,
        )
        self.assertEqual(
            EXAMPLE['sni_container_refs'], test_listener.sni_container_refs
        )
        self.assertEqual(EXAMPLE['created_at'], test_listener.created_at)
        self.assertEqual(EXAMPLE['updated_at'], test_listener.updated_at)
        self.assertTrue(test_listener.is_hsts_include_subdomains)
        self.assertEqual(EXAMPLE['hsts_max_age'], test_listener.hsts_max_age)
        self.assertFalse(test_listener.is_hsts_preload)
        self.assertEqual(
            EXAMPLE['provisioning_status'], test_listener.provisioning_status
        )
        self.assertEqual(
            EXAMPLE['operating_status'], test_listener.operating_status
        )
        self.assertEqual(
            EXAMPLE['timeout_client_data'], test_listener.timeout_client_data
        )
        self.assertEqual(
            EXAMPLE['timeout_member_connect'],
            test_listener.timeout_member_connect,
        )
        self.assertEqual(
            EXAMPLE['timeout_member_data'], test_listener.timeout_member_data
        )
        self.assertEqual(
            EXAMPLE['timeout_tcp_inspect'], test_listener.timeout_tcp_inspect
        )
        self.assertEqual(EXAMPLE['tls_ciphers'], test_listener.tls_ciphers)
        self.assertEqual(EXAMPLE['tls_versions'], test_listener.tls_versions)
        self.assertEqual(
            EXAMPLE['alpn_protocols'], test_listener.alpn_protocols
        )

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'created_at': 'created_at',
                'updated_at': 'updated_at',
                'description': 'description',
                'name': 'name',
                'project_id': 'project_id',
                'tags': 'tags',
                'any_tags': 'tags-any',
                'not_tags': 'not-tags',
                'not_any_tags': 'not-tags-any',
                'operating_status': 'operating_status',
                'provisioning_status': 'provisioning_status',
                'is_admin_state_up': 'admin_state_up',
                'is_hsts_include_subdomains': 'hsts_include_subdomains',
                'hsts_max_age': 'hsts_max_age',
                'is_hsts_preload': 'hsts_preload',
                'allowed_cidrs': 'allowed_cidrs',
                'connection_limit': 'connection_limit',
                'default_pool_id': 'default_pool_id',
                'default_tls_container_ref': 'default_tls_container_ref',
                'sni_container_refs': 'sni_container_refs',
                'insert_headers': 'insert_headers',
                'load_balancer_id': 'load_balancer_id',
                'protocol': 'protocol',
                'protocol_port': 'protocol_port',
                'timeout_client_data': 'timeout_client_data',
                'timeout_member_connect': 'timeout_member_connect',
                'timeout_member_data': 'timeout_member_data',
                'timeout_tcp_inspect': 'timeout_tcp_inspect',
                'tls_ciphers': 'tls_ciphers',
                'tls_versions': 'tls_versions',
                'alpn_protocols': 'alpn_protocols',
            },
            test_listener._query_mapping._mapping,
        )


class TestListenerStats(base.TestCase):
    def test_basic(self):
        test_listener = listener.ListenerStats()
        self.assertEqual('stats', test_listener.resource_key)
        self.assertEqual(
            '/lbaas/listeners/%(listener_id)s/stats', test_listener.base_path
        )
        self.assertFalse(test_listener.allow_create)
        self.assertTrue(test_listener.allow_fetch)
        self.assertFalse(test_listener.allow_delete)
        self.assertFalse(test_listener.allow_list)
        self.assertFalse(test_listener.allow_commit)

    def test_make_it(self):
        test_listener = listener.ListenerStats(**EXAMPLE_STATS)
        self.assertEqual(
            EXAMPLE_STATS['active_connections'],
            test_listener.active_connections,
        )
        self.assertEqual(EXAMPLE_STATS['bytes_in'], test_listener.bytes_in)
        self.assertEqual(EXAMPLE_STATS['bytes_out'], test_listener.bytes_out)
        self.assertEqual(
            EXAMPLE_STATS['request_errors'], test_listener.request_errors
        )
        self.assertEqual(
            EXAMPLE_STATS['total_connections'], test_listener.total_connections
        )
