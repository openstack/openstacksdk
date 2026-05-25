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

from openstack.shared_file_system.v2 import share_transfer as _share_transfer
from openstack.tests.functional.shared_file_system.v2 import base


class ShareTransfersTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        # Create a share
        self.SHARE_NAME = self.getUniqueString()
        share = self.user_cloud.share.create_share(
            name=self.SHARE_NAME,
            size=1,
            share_type="dhss_false",
            share_protocol='NFS',
            description=None,
        )
        self.addCleanup(
            self.user_cloud.share.delete_share,
            share.id,
        )
        self.SHARE_ID = share.id
        self.user_cloud.share.wait_for_status(
            share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )

    def test_share_transfers(self):
        # Create a share transfer
        self.SHARE_TRANSFER_NAME = self.getUniqueString()
        new_transfer = self.operator_cloud.share.create_share_transfer(
            share_id=self.SHARE_ID, name=self.SHARE_TRANSFER_NAME
        )
        self.addCleanup(
            self.operator_cloud.share.delete_share_transfers,
            new_transfer.id,
        )

        self.share_transfer_id = new_transfer.id
        auth_key = new_transfer.auth_key
        self.assertIsNotNone(new_transfer)
        self.assertIsInstance(new_transfer, _share_transfer.ShareTransfer)
        self.assertEqual(self.SHARE_TRANSFER_NAME, new_transfer.name)

        # get share transfer details
        share_transfer = self.operator_cloud.share.get_share_transfer(
            self.share_transfer_id
        )
        self.assertIsNotNone(share_transfer)
        self.assertIsInstance(share_transfer, _share_transfer.ShareTransfer)
        self.assertEqual(self.share_transfer_id, share_transfer.id)

        # Find share transfer
        share_transfer = self.operator_cloud.share.find_share_transfer(
            self.share_transfer_id, ignore_missing=False
        )
        self.assertIsNotNone(share_transfer)
        self.assertIsInstance(share_transfer, _share_transfer.ShareTransfer)
        self.assertEqual(self.share_transfer_id, share_transfer.id)

        # List share transfers
        transfers_list = list(self.operator_cloud.share.share_transfers())
        self.assertGreater(len(transfers_list), 0)
        self.assertIsInstance(transfers_list[0], _share_transfer.ShareTransfer)

        transfers_details_list = list(
            self.operator_cloud.share.share_transfers(details=True)
        )
        self.assertGreaterEqual(len(transfers_details_list), 0)
        self.assertIsInstance(
            transfers_details_list[0], _share_transfer.ShareTransfer
        )

        # Accept share transfer
        accepted_transfer = self.operator_cloud.share.accept_share_transfer(
            self.share_transfer_id, auth_key=auth_key
        )
        self.assertIsNotNone(accepted_transfer)
        self.assertEqual(self.share_transfer_id, accepted_transfer.id)
        self.assertIsNone(
            self.operator_cloud.share.find_share_transfer(
                name_or_id=self.share_transfer_id
            )
        )

        new_transfer = self.operator_cloud.share.create_share_transfer(
            share_id=self.SHARE_ID, name=self.SHARE_TRANSFER_NAME
        )

        self.share_transfer_id = new_transfer.id

        # Delete share transfer
        self.operator_cloud.share.delete_share_transfers(
            self.share_transfer_id,
        )

        # delete share
        self.operator_cloud.share.delete_share(
            self.SHARE_ID, ignore_missing=False
        )
