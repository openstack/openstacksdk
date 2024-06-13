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

from openstack import exceptions
from openstack.shared_file_system.v2 import share as _share
from openstack.tests.functional.shared_file_system import base


class ShareTest(base.BaseSharedFileSystemTest):
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
        self.SHARE_SIZE = my_share.size
        my_share_snapshot = self.create_share_snapshot(share_id=self.SHARE_ID)
        self.SHARE_SNAPSHOT_ID = my_share_snapshot.id

    def test_get(self):
        sot = self.user_cloud.share.get_share(self.SHARE_ID)
        assert isinstance(sot, _share.Share)
        self.assertEqual(self.SHARE_ID, sot.id)

    def test_find(self):
        sot = self.user_cloud.share.find_share(name_or_id=self.SHARE_NAME)
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
            self.SHARE_ID, display_description='updated share'
        )
        get_updated_share = self.user_cloud.share.get_share(updated_share.id)
        self.assertEqual('updated share', get_updated_share.description)

    def test_revert_share_to_snapshot(self):
        self.user_cloud.share.revert_share_to_snapshot(
            self.SHARE_ID, self.SHARE_SNAPSHOT_ID
        )
        get_reverted_share = self.user_cloud.share.get_share(self.SHARE_ID)
        self.user_cloud.share.wait_for_status(
            get_reverted_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertIsNotNone(get_reverted_share.id)

    def test_resize_share_larger(self):
        larger_size = 3
        self.user_cloud.share.resize_share(self.SHARE_ID, larger_size)

        get_resized_share = self.user_cloud.share.get_share(self.SHARE_ID)

        self.user_cloud.share.wait_for_status(
            get_resized_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertEqual(larger_size, get_resized_share.size)

    def test_resize_share_smaller(self):
        # Resize to 3 GiB
        smaller_size = 1

        self.user_cloud.share.resize_share(self.SHARE_ID, smaller_size)

        get_resized_share = self.user_cloud.share.get_share(self.SHARE_ID)

        self.user_cloud.share.wait_for_status(
            get_resized_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertEqual(smaller_size, get_resized_share.size)

    def test_resize_share_larger_no_extend(self):
        larger_size = 3

        self.user_cloud.share.resize_share(
            self.SHARE_ID, larger_size, no_extend=True
        )

        get_resized_share = self.user_cloud.share.get_share(self.SHARE_ID)

        self.user_cloud.share.wait_for_status(
            get_resized_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )

        # Assert that no change was made.
        self.assertEqual(self.SHARE_SIZE, get_resized_share.size)

    def test_resize_share_smaller_no_shrink(self):
        smaller_size = 1

        self.user_cloud.share.resize_share(
            self.SHARE_ID, smaller_size, no_shrink=True
        )

        get_resized_share = self.user_cloud.share.get_share(self.SHARE_ID)

        self.user_cloud.share.wait_for_status(
            get_resized_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )

        # Assert that no change was made.
        self.assertEqual(self.SHARE_SIZE, get_resized_share.size)

    def test_resize_share_with_force(self):
        """Test that extend with force works as expected."""
        # Resize to 3 GiB
        larger_size = 3
        self.operator_cloud.share.resize_share(
            self.SHARE_ID, larger_size, force=True
        )

        get_resized_share = self.user_cloud.share.get_share(self.SHARE_ID)

        self.user_cloud.share.wait_for_status(
            get_resized_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertEqual(larger_size, get_resized_share.size)


class ManageUnmanageShareTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        self.NEW_SHARE = self.create_share(
            share_proto="NFS",
            name="accounting_p8787",
            size=2,
        )
        self.SHARE_ID = self.NEW_SHARE.id

        self.export_locations = self.operator_cloud.share.export_locations(
            self.SHARE_ID
        )
        export_paths = [export['path'] for export in self.export_locations]
        self.export_path = export_paths[0]

        self.share_host = self.operator_cloud.share.get_share(self.SHARE_ID)[
            'host'
        ]

    def test_manage_and_unmanage_share(self):
        self.operator_cloud.share.unmanage_share(self.SHARE_ID)

        self.operator_cloud.shared_file_system.wait_for_delete(
            self.NEW_SHARE, interval=2, wait=self._wait_for_timeout
        )

        try:
            self.operator_cloud.share.get_share(self.SHARE_ID)
        except exceptions.NotFoundException:
            pass

        managed_share = self.operator_cloud.share.manage_share(
            self.NEW_SHARE.share_protocol, self.export_path, self.share_host
        )

        self.operator_cloud.share.wait_for_status(
            managed_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )

        self.assertEqual(
            self.NEW_SHARE.share_protocol, managed_share.share_protocol
        )

        managed_host = self.operator_cloud.share.get_share(managed_share.id)[
            'host'
        ]

        self.assertEqual(self.share_host, managed_host)
