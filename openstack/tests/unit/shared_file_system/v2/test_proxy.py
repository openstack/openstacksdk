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

from unittest import mock

from openstack.shared_file_system.v2 import _proxy
from openstack.shared_file_system.v2 import limit
from openstack.shared_file_system.v2 import share
from openstack.shared_file_system.v2 import share_snapshot
from openstack.shared_file_system.v2 import storage_pool
from openstack.shared_file_system.v2 import user_message
from openstack.tests.unit import test_proxy_base


class TestSharedFileSystemProxy(test_proxy_base.TestProxyBase):

    def setUp(self):
        super(TestSharedFileSystemProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestSharedFileSystemShare(TestSharedFileSystemProxy):
    def test_shares(self):
        self.verify_list(self.proxy.shares, share.Share)

    def test_shares_detailed(self):
        self.verify_list(self.proxy.shares, share.Share,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1})

    def test_shares_not_detailed(self):
        self.verify_list(self.proxy.shares, share.Share,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

    def test_share_get(self):
        self.verify_get(self.proxy.get_share, share.Share)

    def test_share_delete(self):
        self.verify_delete(
            self.proxy.delete_share, share.Share, False)

    def test_share_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_share, share.Share, True)

    def test_share_create(self):
        self.verify_create(self.proxy.create_share, share.Share)

    def test_share_update(self):
        self.verify_update(self.proxy.update_share, share.Share)

    @mock.patch("openstack.resource.wait_for_status")
    def test_wait_for(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_status(mock_resource, 'ACTIVE')

        mock_wait.assert_called_once_with(self.proxy, mock_resource,
                                          'ACTIVE', [], 2, 120)


class TestSharedFileSystemStoragePool(TestSharedFileSystemProxy):
    def test_storage_pools(self):
        self.verify_list(
            self.proxy.storage_pools, storage_pool.StoragePool)

    def test_storage_pool_detailed(self):
        self.verify_list(
            self.proxy.storage_pools, storage_pool.StoragePool,
            method_kwargs={"details": True, "backend": "alpha"},
            expected_kwargs={"backend": "alpha"})

    def test_storage_pool_not_detailed(self):
        self.verify_list(
            self.proxy.storage_pools, storage_pool.StoragePool,
            method_kwargs={"details": False, "backend": "alpha"},
            expected_kwargs={"backend": "alpha"})


class TestUserMessageProxy(test_proxy_base.TestProxyBase):

    def setUp(self):
        super(TestUserMessageProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_user_messages(self):
        self.verify_list(self.proxy.user_messages, user_message.UserMessage)

    def test_user_messages_queried(self):
        self.verify_list(
            self.proxy.user_messages, user_message.UserMessage,
            method_kwargs={"action_id": "1"},
            expected_kwargs={"action_id": "1"})

    def test_user_message_get(self):
        self.verify_get(self.proxy.get_user_message, user_message.UserMessage)

    def test_delete_user_message(self):
        self.verify_delete(
            self.proxy.delete_user_message, user_message.UserMessage, False)

    def test_delete_user_message_true(self):
        self.verify_delete(
            self.proxy.delete_user_message, user_message.UserMessage, True)

    def test_limit(self):
        self.verify_list(self.proxy.limits, limit.Limit)


class TestShareSnapshotResource(test_proxy_base.TestProxyBase):

    def setUp(self):
        super(TestShareSnapshotResource, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_share_snapshots(self):
        self.verify_list(
            self.proxy.share_snapshots, share_snapshot.ShareSnapshot)

    def test_share_snapshots_detailed(self):
        self.verify_list(
            self.proxy.share_snapshots,
            share_snapshot.ShareSnapshot,
            method_kwargs={"details": True, "name": "my_snapshot"},
            expected_kwargs={"name": "my_snapshot"})

    def test_share_snapshots_not_detailed(self):
        self.verify_list(
            self.proxy.share_snapshots,
            share_snapshot.ShareSnapshot,
            method_kwargs={"details": False, "name": "my_snapshot"},
            expected_kwargs={"name": "my_snapshot"})

    def test_share_snapshot_get(self):
        self.verify_get(
            self.proxy.get_share_snapshot, share_snapshot.ShareSnapshot)

    def test_share_snapshot_delete(self):
        self.verify_delete(
            self.proxy.delete_share_snapshot,
            share_snapshot.ShareSnapshot, False)

    def test_share_snapshot_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_share_snapshot,
            share_snapshot.ShareSnapshot, True)

    def test_share_snapshot_create(self):
        self.verify_create(
            self.proxy.create_share_snapshot, share_snapshot.ShareSnapshot)

    def test_share_snapshot_update(self):
        self.verify_update(
            self.proxy.update_share_snapshot, share_snapshot.ShareSnapshot)

    @mock.patch("openstack.resource.wait_for_delete")
    def test_wait_for_delete(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_delete(mock_resource)

        mock_wait.assert_called_once_with(self.proxy, mock_resource, 2, 120)
