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

from openstack.identity.v3 import endpoint

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'enabled': True,
    'id': IDENTIFIER,
    'interface': '3',
    'links': {'self': 'http://example.com/endpoint1'},
    'region_id': '4',
    'service_id': '5',
    'url': '6',
}


class TestEndpoint(base.TestCase):

    def test_basic(self):
        sot = endpoint.Endpoint()
        self.assertEqual('endpoint', sot.resource_key)
        self.assertEqual('endpoints', sot.resources_key)
        self.assertEqual('/endpoints', sot.base_path)
        self.assertEqual('identity', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.update_method)
        self.assertDictEqual(
            {
                'interface': 'interface',
                'service_id': 'service_id',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping)

    def test_make_it(self):
        sot = endpoint.Endpoint(**EXAMPLE)
        self.assertTrue(sot.is_enabled)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['interface'], sot.interface)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['region_id'], sot.region_id)
        self.assertEqual(EXAMPLE['service_id'], sot.service_id)
        self.assertEqual(EXAMPLE['url'], sot.url)
