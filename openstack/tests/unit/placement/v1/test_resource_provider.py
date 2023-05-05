# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.placement.v1 import resource_provider as rp
from openstack.tests.unit import base

FAKE = {
    'uuid': '751cd30a-df22-4ef8-b028-67c1c5aeddc3',
    'name': 'fake-name',
    'parent_provider_uuid': '9900cc2d-88e8-429d-927a-182adf1577b0',
}


class TestResourceProvider(base.TestCase):
    def test_basic(self):
        sot = rp.ResourceProvider()
        self.assertEqual(None, sot.resource_key)
        self.assertEqual('resource_providers', sot.resources_key)
        self.assertEqual('/resource_providers', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_patch)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'name': 'name',
                'member_of': 'member_of',
                'resources': 'resources',
                'in_tree': 'in_tree',
                'required': 'required',
                'id': 'uuid',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = rp.ResourceProvider(**FAKE)
        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(
            FAKE['parent_provider_uuid'],
            sot.parent_provider_id,
        )
