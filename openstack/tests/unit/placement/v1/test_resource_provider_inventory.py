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

from openstack.placement.v1 import resource_provider_inventory
from openstack.tests.unit import base

FAKE = {
    'allocation_ratio': 1.0,
    'max_unit': 35,
    'min_unit': 1,
    'reserved': 0,
    'step_size': 1,
    'total': 35,
}


class TestResourceProviderInventory(base.TestCase):
    def test_basic(self):
        sot = resource_provider_inventory.ResourceProviderInventory()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual(
            '/resource_providers/%(resource_provider_id)s/inventories',
            sot.base_path,
        )
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_patch)

        self.assertDictEqual({}, sot._query_mapping._mapping)

    def test_make_it(self):
        sot = resource_provider_inventory.ResourceProviderInventory(**FAKE)
        self.assertEqual(FAKE['allocation_ratio'], sot.allocation_ratio)
        self.assertEqual(FAKE['max_unit'], sot.max_unit)
        self.assertEqual(FAKE['min_unit'], sot.min_unit)
        self.assertEqual(FAKE['reserved'], sot.reserved)
        self.assertEqual(FAKE['step_size'], sot.step_size)
        self.assertEqual(FAKE['total'], sot.total)
