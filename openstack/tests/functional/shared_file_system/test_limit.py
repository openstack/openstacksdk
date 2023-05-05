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

from openstack.tests.functional.shared_file_system import base


class LimitTest(base.BaseSharedFileSystemTest):
    def test_limits(self):
        limits = self.user_cloud.shared_file_system.limits()
        self.assertGreater(len(list(limits)), 0)
        for limit in limits:
            for attribute in (
                "maxTotalReplicaGigabytes",
                "maxTotalShares",
                "maxTotalShareGigabytes",
                "maxTotalShareNetworks",
                "maxTotalShareSnapshots",
                "maxTotalShareReplicas",
                "maxTotalSnapshotGigabytes",
                "totalReplicaGigabytesUsed",
                "totalShareGigabytesUsed",
                "totalSharesUsed",
                "totalShareNetworksUsed",
                "totalShareSnapshotsUsed",
                "totalSnapshotGigabytesUsed",
                "totalShareReplicasUsed",
            ):
                self.assertTrue(hasattr(limit, attribute))
