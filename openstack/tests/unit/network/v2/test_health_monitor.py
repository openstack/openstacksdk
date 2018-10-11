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

from openstack.network.v2 import health_monitor

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'delay': '2',
    'expected_codes': '3',
    'http_method': '4',
    'id': IDENTIFIER,
    'max_retries': '6',
    'pools': [{'id': '7'}],
    'pool_id': '7',
    'tenant_id': '8',
    'timeout': '9',
    'type': '10',
    'url_path': '11',
    'name': '12',
}


class TestHealthMonitor(base.TestCase):

    def test_basic(self):
        sot = health_monitor.HealthMonitor()
        self.assertEqual('healthmonitor', sot.resource_key)
        self.assertEqual('healthmonitors', sot.resources_key)
        self.assertEqual('/lbaas/healthmonitors', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = health_monitor.HealthMonitor(**EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['delay'], sot.delay)
        self.assertEqual(EXAMPLE['expected_codes'], sot.expected_codes)
        self.assertEqual(EXAMPLE['http_method'], sot.http_method)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['max_retries'], sot.max_retries)
        self.assertEqual(EXAMPLE['pools'], sot.pool_ids)
        self.assertEqual(EXAMPLE['pool_id'], sot.pool_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['timeout'], sot.timeout)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['url_path'], sot.url_path)
        self.assertEqual(EXAMPLE['name'], sot.name)
