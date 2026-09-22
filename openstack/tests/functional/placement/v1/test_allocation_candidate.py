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

from openstack.placement.v1 import (
    allocation_candidate as _allocation_candidate,
)
from openstack.tests.functional import base


class TestAllocationCandidate(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud.has_service('placement'):
            self.skipTest('placement service not supported by cloud')

    def test_allocation_candidate(self):
        # devstack always has at least one compute resource provider with
        # VCPU inventory, so querying for VCPU:1 is guaranteed to return
        # at least one candidate.

        candidates = list(
            self.operator_cloud.placement.allocation_candidates(
                resources='VCPU:1',
            )
        )
        self.assertGreater(len(candidates), 0)

        candidate = candidates[0]
        self.assertIsInstance(
            candidate, _allocation_candidate.AllocationCandidate
        )
        # Each candidate must have allocations and provider_summaries.
        self.assertIsInstance(candidate.allocations, dict)
        self.assertIsInstance(candidate.provider_summaries, dict)

        # provider_summaries must only contain providers referenced in
        # allocations (denormalized from the global provider_summaries).
        self.assertEqual(
            set(candidate.allocations.keys()),
            set(candidate.provider_summaries.keys()),
        )

        # Verify the limit parameter is forwarded correctly.
        limited = list(
            self.operator_cloud.placement.allocation_candidates(
                resources='VCPU:1',
                limit=1,
            )
        )
        self.assertLessEqual(len(limited), 1)
