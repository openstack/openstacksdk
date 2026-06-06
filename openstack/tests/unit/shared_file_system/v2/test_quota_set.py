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

from openstack.shared_file_system.v2 import quota_set
from openstack.tests.unit import base

EXAMPLE = {
    "gigabytes": 1000,
    "shares": 50,
    "snapshot_gigabytes": 1000,
    "snapshots": 50,
    "id": "16e1ab15c35a457e9c2b2aa189f544e1",
    "share_networks": 10,
    "share_groups": 10,
    "share_group_snapshots": 10,
    "share_replicas": 100,
    "replica_gigabytes": 1000,
    "per_share_gigabytes": -1,
    "backups": 50,
    "backup_gigabytes": 1000,
}


class TestQuotaSet(base.TestCase):
    def test_basic(self):
        sot = quota_set.QuotaSet()
        self.assertEqual("quota_sets", sot.resources_key)
        self.assertEqual("/quota-sets/%(project_id)s", sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.requires_id)

    def test_create_quota_set(self):
        sot = quota_set.QuotaSet(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['gigabytes'], sot.gigabytes)
        self.assertEqual(EXAMPLE['shares'], sot.shares)
        self.assertEqual(EXAMPLE['snapshot_gigabytes'], sot.snapshot_gigabytes)
        self.assertEqual(EXAMPLE['share_networks'], sot.share_networks)
        self.assertEqual(EXAMPLE['share_replicas'], sot.share_replicas)
        self.assertEqual(
            EXAMPLE['per_share_gigabytes'], sot.per_share_gigabytes
        )
        self.assertEqual(EXAMPLE['backups'], sot.backups)
