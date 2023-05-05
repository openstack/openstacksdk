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


class StoragePoolTest(base.BaseSharedFileSystemTest):
    def test_storage_pools(self):
        pools = self.operator_cloud.shared_file_system.storage_pools()
        self.assertGreater(len(list(pools)), 0)
        for pool in pools:
            for attribute in (
                'pool',
                'name',
                'host',
                'backend',
                'capabilities',
            ):
                self.assertTrue(hasattr(pool, attribute))
