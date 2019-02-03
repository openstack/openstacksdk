# Copyright 2017 Rackspace, US Inc.
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

from openstack.load_balancer.v2 import health_monitor

EXAMPLE = {
    'admin_state_up': True,
    'created_at': '2017-07-17T12:14:57.233772',
    'delay': 10,
    'expected_codes': '200, 202',
    'http_method': 'HEAD',
    'id': uuid.uuid4(),
    'max_retries': 2,
    'max_retries_down': 3,
    'name': 'test_health_monitor',
    'operating_status': 'ONLINE',
    'pools': [{'id': uuid.uuid4()}],
    'pool_id': uuid.uuid4(),
    'project_id': uuid.uuid4(),
    'provisioning_status': 'ACTIVE',
    'timeout': 4,
    'type': 'HTTP',
    'updated_at': '2017-07-17T12:16:57.233772',
    'url_path': '/health_page.html'
}


class TestPoolHealthMonitor(base.TestCase):

    def test_basic(self):
        test_hm = health_monitor.HealthMonitor()
        self.assertEqual('healthmonitor', test_hm.resource_key)
        self.assertEqual('healthmonitors', test_hm.resources_key)
        self.assertEqual('/lbaas/healthmonitors', test_hm.base_path)
        self.assertTrue(test_hm.allow_create)
        self.assertTrue(test_hm.allow_fetch)
        self.assertTrue(test_hm.allow_commit)
        self.assertTrue(test_hm.allow_delete)
        self.assertTrue(test_hm.allow_list)

    def test_make_it(self):
        test_hm = health_monitor.HealthMonitor(**EXAMPLE)
        self.assertTrue(test_hm.is_admin_state_up)
        self.assertEqual(EXAMPLE['created_at'], test_hm.created_at)
        self.assertEqual(EXAMPLE['delay'], test_hm.delay)
        self.assertEqual(EXAMPLE['expected_codes'], test_hm.expected_codes)
        self.assertEqual(EXAMPLE['http_method'], test_hm.http_method)
        self.assertEqual(EXAMPLE['id'], test_hm.id)
        self.assertEqual(EXAMPLE['max_retries'], test_hm.max_retries)
        self.assertEqual(EXAMPLE['max_retries_down'], test_hm.max_retries_down)
        self.assertEqual(EXAMPLE['name'], test_hm.name)
        self.assertEqual(EXAMPLE['operating_status'], test_hm.operating_status)
        self.assertEqual(EXAMPLE['pools'], test_hm.pools)
        self.assertEqual(EXAMPLE['pool_id'], test_hm.pool_id)
        self.assertEqual(EXAMPLE['project_id'], test_hm.project_id)
        self.assertEqual(EXAMPLE['provisioning_status'],
                         test_hm.provisioning_status)
        self.assertEqual(EXAMPLE['timeout'], test_hm.timeout)
        self.assertEqual(EXAMPLE['type'], test_hm.type)
        self.assertEqual(EXAMPLE['updated_at'], test_hm.updated_at)
        self.assertEqual(EXAMPLE['url_path'], test_hm.url_path)

        self.assertDictEqual(
            {'limit': 'limit',
             'marker': 'marker',
             'created_at': 'created_at',
             'updated_at': 'updated_at',
             'name': 'name',
             'project_id': 'project_id',
             'tags': 'tags',
             'any_tags': 'tags-any',
             'not_tags': 'not-tags',
             'not_any_tags': 'not-tags-any',
             'operating_status': 'operating_status',
             'provisioning_status': 'provisioning_status',
             'is_admin_state_up': 'admin_state_up',

             'delay': 'delay',
             'expected_codes': 'expected_codes',
             'http_method': 'http_method',
             'max_retries': 'max_retries',
             'max_retries_down': 'max_retries_down',
             'pool_id': 'pool_id',
             'timeout': 'timeout',
             'type': 'type',
             'url_path': 'url_path'
             },
            test_hm._query_mapping._mapping)
