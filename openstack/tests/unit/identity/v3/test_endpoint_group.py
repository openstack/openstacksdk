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

from typing import Any

from openstack.identity.v3 import endpoint_group
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE: dict[str, Any] = {
    'description': '1',
    'id': IDENTIFIER,
    'filters': {
        'interface': '3.1',
        'region_id': '3.2',
        'service_id': '3.3',
    },
    'links': {'self': 'http://example.com/endpoint_group1'},
    'name': '4',
}


class TestEndpointGroup(base.TestCase):
    def test_basic(self):
        sot = endpoint_group.EndpointGroup()
        self.assertEqual('endpoint_group', sot.resource_key)
        self.assertEqual('endpoint_groups', sot.resources_key)
        self.assertEqual('/OS-EP-FILTER/endpoint_groups', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)
        self.assertDictEqual(
            {
                'name': 'name',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = endpoint_group.EndpointGroup(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertDictEqual(EXAMPLE['filters'], sot.filters)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['name'], sot.name)
