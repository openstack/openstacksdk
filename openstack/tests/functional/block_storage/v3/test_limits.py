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


from openstack.tests.functional.block_storage.v3 import base


class TestLimits(base.BaseBlockStorageTest):
    def test_get(self):
        sot = self.operator_cloud.block_storage.get_limits()
        self.assertIsNotNone(sot.absolute.max_total_backup_gigabytes)
        self.assertIsNotNone(sot.absolute.max_total_backups)
        self.assertIsNotNone(sot.absolute.max_total_snapshots)
        self.assertIsNotNone(sot.absolute.max_total_volume_gigabytes)
        self.assertIsNotNone(sot.absolute.max_total_volumes)
        self.assertIsNotNone(sot.absolute.total_backup_gigabytes_used)
        self.assertIsNotNone(sot.absolute.total_backups_used)
        self.assertIsNotNone(sot.absolute.total_gigabytes_used)
        self.assertIsNotNone(sot.absolute.total_snapshots_used)
        self.assertIsNotNone(sot.absolute.total_volumes_used)
        self.assertIsNotNone(sot.rate)
