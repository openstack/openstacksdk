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
        my_share = self.conn.shared_file_system.create_share(
            name=self.SHARE_NAME, size=2, share_type="dhss_false",
            share_protocol='NFS', description=None)
        self.conn.shared_file_system.wait_for_status(
            my_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout)
        self.assertIsNotNone(my_share)
        self.assertIsNotNone(my_share.id)
        self.SHARE_ID = my_share.id

    def tearDown(self):
        sot = self.conn.shared_file_system.delete_share(
            self.SHARE_ID,
            ignore_missing=True)
        self.assertIsNone(sot)
        super(ShareTest, self).tearDown()

    def test_get(self):
        sot = self.conn.shared_file_system.get_share(self.SHARE_ID)
        assert isinstance(sot, _share.Share)
        self.assertEqual(self.SHARE_ID, sot.id)

    def test_list_share(self):
        shares = self.conn.shared_file_system.shares(details=False)
        self.assertGreater(len(list(shares)), 0)
        for share in shares:
            for attribute in ('id', 'name', 'created_at', 'updated_at'):
                self.assertTrue(hasattr(share, attribute))

    def test_update(self):
        updated_share = self.conn.shared_file_system.update_share(
            self.SHARE_ID, display_description='updated share')
        get_updated_share = self.conn.shared_file_system.get_share(
            updated_share.id)
        self.assertEqual('updated share', get_updated_share.description)
