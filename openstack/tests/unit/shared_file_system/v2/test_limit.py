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

from openstack.shared_file_system.v2 import limit
from openstack.tests.unit import base

EXAMPLE = {
    "totalShareNetworksUsed": 0,
    "maxTotalShareGigabytes": 1000,
    "maxTotalShareNetworks": 10,
    "totalSharesUsed": 0,
    "totalShareGigabytesUsed": 0,
    "totalShareSnapshotsUsed": 0,
    "maxTotalShares": 50,
    "totalSnapshotGigabytesUsed": 0,
    "maxTotalSnapshotGigabytes": 1000,
    "maxTotalShareSnapshots": 50,
    "maxTotalShareReplicas": 100,
    "maxTotalReplicaGigabytes": 1000,
    "totalShareReplicasUsed": 0,
    "totalReplicaGigabytesUsed": 0,
}


class TestLimit(base.TestCase):
    def test_basic(self):
        limits = limit.Limit()
        self.assertEqual('limits', limits.resources_key)
        self.assertEqual('/limits', limits.base_path)
        self.assertTrue(limits.allow_list)
        self.assertFalse(limits.allow_fetch)
        self.assertFalse(limits.allow_create)
        self.assertFalse(limits.allow_commit)
        self.assertFalse(limits.allow_delete)
        self.assertFalse(limits.allow_head)

    def test_make_limits(self):
        limits = limit.Limit(**EXAMPLE)
        self.assertEqual(
            EXAMPLE['totalShareNetworksUsed'], limits.totalShareNetworksUsed
        )
        self.assertEqual(
            EXAMPLE['maxTotalShareGigabytes'], limits.maxTotalShareGigabytes
        )
        self.assertEqual(
            EXAMPLE['maxTotalShareNetworks'], limits.maxTotalShareNetworks
        )
        self.assertEqual(EXAMPLE['totalSharesUsed'], limits.totalSharesUsed)
        self.assertEqual(
            EXAMPLE['totalShareGigabytesUsed'], limits.totalShareGigabytesUsed
        )
        self.assertEqual(
            EXAMPLE['totalShareSnapshotsUsed'], limits.totalShareSnapshotsUsed
        )
        self.assertEqual(EXAMPLE['maxTotalShares'], limits.maxTotalShares)
        self.assertEqual(
            EXAMPLE['totalSnapshotGigabytesUsed'],
            limits.totalSnapshotGigabytesUsed,
        )
        self.assertEqual(
            EXAMPLE['maxTotalSnapshotGigabytes'],
            limits.maxTotalSnapshotGigabytes,
        )
        self.assertEqual(
            EXAMPLE['maxTotalShareSnapshots'], limits.maxTotalShareSnapshots
        )
        self.assertEqual(
            EXAMPLE['maxTotalShareReplicas'], limits.maxTotalShareReplicas
        )
        self.assertEqual(
            EXAMPLE['maxTotalReplicaGigabytes'],
            limits.maxTotalReplicaGigabytes,
        )
        self.assertEqual(
            EXAMPLE['totalShareReplicasUsed'], limits.totalShareReplicasUsed
        )
        self.assertEqual(
            EXAMPLE['totalReplicaGigabytesUsed'],
            limits.totalReplicaGigabytesUsed,
        )
