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

from openstack.shared_file_system.v2 import share as _share
from openstack.tests.functional.shared_file_system import base


class ShareTest(base.BaseSharedFileSystemTest):

    def setUp(self):
        super(ShareTest, self).setUp()

        self.SHARE_NAME = self.getUniqueString()
        my_share = self.create_share(
            name=self.SHARE_NAME, size=2, share_type="dhss_false",
            share_protocol='NFS', description=None)
        self.SHARE_ID = my_share.id
        my_share_snapshot = self.create_share_snapshot(
            share_id=self.SHARE_ID
        )
        self.SHARE_SNAPSHOT_ID = my_share_snapshot.id

    def test_get(self):
        sot = self.user_cloud.share.get_share(self.SHARE_ID)
        assert isinstance(sot, _share.Share)
        self.assertEqual(self.SHARE_ID, sot.id)

    def test_list_share(self):
        shares = self.user_cloud.share.shares(details=False)
        self.assertGreater(len(list(shares)), 0)
        for share in shares:
            for attribute in ('id', 'name', 'created_at', 'updated_at'):
                self.assertTrue(hasattr(share, attribute))

    def test_update(self):
        updated_share = self.user_cloud.share.update_share(
            self.SHARE_ID, display_description='updated share')
        get_updated_share = self.user_cloud.share.get_share(
            updated_share.id)
        self.assertEqual('updated share', get_updated_share.description)

    def test_revert_share_to_snapshot(self):
        self.user_cloud.share.revert_share_to_snapshot(
            self.SHARE_ID, self.SHARE_SNAPSHOT_ID)
        get_reverted_share = self.user_cloud.share.get_share(
            self.SHARE_ID)
        self.user_cloud.share.wait_for_status(
            get_reverted_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout)
        self.assertIsNotNone(get_reverted_share.id)
