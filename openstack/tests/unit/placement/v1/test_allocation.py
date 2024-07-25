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

from typing import Any

from openstack.placement.v1 import allocation
from openstack.tests.unit import base

FAKE: dict[str, Any] = {
    'allocations': {
        '5f8d0b47-543c-4a21-a3fa-f43a05a8f3de': {
            'generation': 1,
            'resources': {
                'DISK_GB': 4,
                'VCPU': 2,
            },
        },
    },
    'consumer_generation': 1,
    'consumer_type': 'INSTANCE',
    'project_id': '33aa1afc-03fe-43b8-8201-4e0d3b4b8ab5',
    'user_id': '6efcd28a-4680-4e77-a5b5-4a8f10b6eae9',
}


class TestAllocation(base.TestCase):
    def test_basic(self):
        sot = allocation.Allocation()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/allocations', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)

        self.assertDictEqual({}, sot._query_mapping._mapping)

    def test_make_it(self):
        sot = allocation.Allocation(**FAKE)
        self.assertEqual(FAKE['allocations'], sot.allocations)
        self.assertEqual(FAKE['consumer_generation'], sot.consumer_generation)
        self.assertEqual(FAKE['consumer_type'], sot.consumer_type)
        self.assertEqual(FAKE['project_id'], sot.project_id)
        self.assertEqual(FAKE['user_id'], sot.user_id)
