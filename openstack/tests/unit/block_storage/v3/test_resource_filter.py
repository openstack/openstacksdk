# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
# # Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.block_storage.v3 import resource_filter
from openstack.tests.unit import base

RESOURCE_FILTER = {
    'filters': [
        'name',
        'status',
        'image_metadata',
        'bootable',
        'migration_status',
    ],
    'resource': 'volume',
}


class TestResourceFilter(base.TestCase):
    def test_basic(self):
        resource = resource_filter.ResourceFilter()
        self.assertEqual('resource_filters', resource.resources_key)
        self.assertEqual('/resource_filters', resource.base_path)
        self.assertFalse(resource.allow_create)
        self.assertFalse(resource.allow_fetch)
        self.assertFalse(resource.allow_commit)
        self.assertFalse(resource.allow_delete)
        self.assertTrue(resource.allow_list)

        self.assertDictEqual(
            {
                "resource": "resource",
            },
            resource._query_mapping._mapping,
        )

    def test_make_resource_filter(self):
        resource = resource_filter.ResourceFilter(**RESOURCE_FILTER)
        self.assertEqual(RESOURCE_FILTER['filters'], resource.filters)
        self.assertEqual(RESOURCE_FILTER['resource'], resource.resource)
