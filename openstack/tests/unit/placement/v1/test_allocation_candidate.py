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

from openstack.placement.v1 import allocation_candidate
from openstack.tests.unit import base

RP_UUID = '9a9c6b0f-e8d1-4d16-b053-a2bfe8a76757'

FAKE: dict[str, Any] = {
    'allocations': {
        RP_UUID: {'resources': {'VCPU': 1}},
    },
    'mappings': {'': [RP_UUID]},
    'provider_summaries': {
        RP_UUID: {
            'resources': {'VCPU': {'capacity': 4, 'used': 0}},
            'traits': ['HW_NUMA_ROOT'],
        },
    },
}


class TestAllocationCandidate(base.TestCase):
    def test_basic(self):
        sot = allocation_candidate.AllocationCandidate()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/allocation_candidates', sot.base_path)
        self.assertFalse(sot.requires_id)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = allocation_candidate.AllocationCandidate(**FAKE)
        self.assertEqual(FAKE['allocations'], sot.allocations)
        self.assertEqual(FAKE['mappings'], sot.mappings)
        self.assertEqual(FAKE['provider_summaries'], sot.provider_summaries)
