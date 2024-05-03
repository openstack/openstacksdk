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


class ShareSnapshotInstanceTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        self.SHARE_NAME = self.getUniqueString()
        my_share = self.create_share(
            name=self.SHARE_NAME,
            size=2,
            share_type="dhss_false",
            share_protocol='NFS',
            description=None,
        )
        self.SHARE_ID = my_share.id
        self.create_share_snapshot(share_id=self.SHARE_ID)

    def test_share_snapshot_instances(self):
        sots = (
            self.operator_cloud.shared_file_system.share_snapshot_instances()
        )
        self.assertGreater(len(list(sots)), 0)
        for sot in sots:
            for attribute in ('id', 'name', 'created_at', 'updated_at'):
                self.assertTrue(hasattr(sot, attribute))
                self.assertIsInstance(getattr(sot, attribute), 'str')
