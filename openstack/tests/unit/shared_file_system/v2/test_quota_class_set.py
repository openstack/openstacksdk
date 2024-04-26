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


from openstack.shared_file_system.v2 import quota_class_set
from openstack.tests.unit import base

EXAMPLE = {
    "share_groups": 50,
    "gigabytes": 1000,
    "share_group_snapshots": 50,
    "snapshots": 50,
    "snapshot_gigabytes": 1000,
    "shares": 50,
    "id": "default",
    "share_networks": 10,
    "share_replicas": 100,
    "replica_gigabytes": 1000,
    "per_share_gigabytes": -1,
    "backups": 50,
    "backup_gigabytes": 1000,
}


class TestQuotaClassSet(base.TestCase):
    def test_basic(self):
        _quota_class_set = quota_class_set.QuotaClassSet()

        self.assertEqual('/quota-class-sets', _quota_class_set.base_path)
        self.assertTrue(_quota_class_set.allow_fetch)
        self.assertTrue(_quota_class_set.allow_commit)
        self.assertFalse(_quota_class_set.allow_create)
        self.assertFalse(_quota_class_set.allow_delete)
        self.assertFalse(_quota_class_set.allow_list)
        self.assertFalse(_quota_class_set.allow_head)

    def test_get_quota_class_set(self):
        _quota_class_set = quota_class_set.QuotaClassSet(**EXAMPLE)
        self.assertEqual(
            EXAMPLE['share_groups'], _quota_class_set.share_groups
        )
        self.assertEqual(EXAMPLE['gigabytes'], _quota_class_set.gigabytes)
        self.assertEqual(
            EXAMPLE['share_group_snapshots'],
            _quota_class_set.share_group_snapshots,
        )
        self.assertEqual(EXAMPLE['snapshots'], _quota_class_set.snapshots)
        self.assertEqual(
            EXAMPLE['snapshot_gigabytes'], _quota_class_set.snapshot_gigabytes
        )
        self.assertEqual(EXAMPLE['shares'], _quota_class_set.shares)
        self.assertEqual(EXAMPLE['id'], _quota_class_set.id)
        self.assertEqual(
            EXAMPLE['share_networks'], _quota_class_set.share_networks
        )
        self.assertEqual(
            EXAMPLE['share_replicas'], _quota_class_set.share_replicas
        )
        self.assertEqual(
            EXAMPLE['replica_gigabytes'], _quota_class_set.replica_gigabytes
        )
        self.assertEqual(
            EXAMPLE['per_share_gigabytes'],
            _quota_class_set.per_share_gigabytes,
        )
        self.assertEqual(EXAMPLE['backups'], _quota_class_set.backups)
        self.assertEqual(
            EXAMPLE['backup_gigabytes'], _quota_class_set.backup_gigabytes
        )

    def test_update_quota_class_set(self):
        _quota_class_set = quota_class_set.QuotaClassSet(**EXAMPLE)
        updated_attributes = {
            "share_groups": 100,
            "gigabytes": 2000,
            "share_group_snapshots": 100,
        }
        _quota_class_set._update(**updated_attributes)

        self.assertEqual(
            updated_attributes['share_groups'], _quota_class_set.share_groups
        )
        self.assertEqual(
            updated_attributes['gigabytes'], _quota_class_set.gigabytes
        )
        self.assertEqual(
            updated_attributes['share_group_snapshots'],
            _quota_class_set.share_group_snapshots,
        )
        self.assertEqual(EXAMPLE['snapshots'], _quota_class_set.snapshots)
