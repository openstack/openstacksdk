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
from openstack.shared_file_system.v2 import resource_locks
from openstack.shared_file_system.v2 import share
from openstack.shared_file_system.v2 import share_access_rule
from openstack.shared_file_system.v2 import share_group
from openstack.shared_file_system.v2 import share_group_snapshot
from openstack.shared_file_system.v2 import share_instance
from openstack.shared_file_system.v2 import share_network
from openstack.shared_file_system.v2 import share_network_subnet
from openstack.shared_file_system.v2 import share_snapshot
from openstack.shared_file_system.v2 import share_snapshot_instance
from openstack.shared_file_system.v2 import storage_pool
from openstack.shared_file_system.v2 import user_message
from openstack.tests.unit import test_proxy_base


class TestSharedFileSystemProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestSharedFileSystemShare(TestSharedFileSystemProxy):
    def test_shares(self):
        self.verify_list(self.proxy.shares, share.Share)

    def test_shares_detailed(self):
        self.verify_list(
            self.proxy.shares,
            share.Share,
            method_kwargs={"details": True, "query": 1},
            expected_kwargs={"query": 1},
        )

    def test_shares_not_detailed(self):
        self.verify_list(
            self.proxy.shares,
            share.Share,
            method_kwargs={"details": False, "query": 1},
            expected_kwargs={"query": 1},
        )

    def test_share_get(self):
        self.verify_get(self.proxy.get_share, share.Share)

    def test_share_find(self):
        self.verify_find(self.proxy.find_share, share.Share)

    def test_share_delete(self):
        self.verify_delete(self.proxy.delete_share, share.Share, False)

    def test_share_delete_ignore(self):
        self.verify_delete(self.proxy.delete_share, share.Share, True)

    def test_share_create(self):
        self.verify_create(self.proxy.create_share, share.Share)

    def test_share_update(self):
        self.verify_update(self.proxy.update_share, share.Share)

    def test_share_resize_extend(self):
        mock_share = share.Share(size=10, id='fakeId')
        self.proxy._get = mock.Mock(return_value=mock_share)

        self._verify(
            "openstack.shared_file_system.v2.share." + "Share.extend_share",
            self.proxy.resize_share,
            method_args=['fakeId', 20],
            expected_args=[self.proxy, 20, False],
        )

    def test_share_resize_shrink(self):
        mock_share = share.Share(size=30, id='fakeId')
        self.proxy._get = mock.Mock(return_value=mock_share)

        self._verify(
            "openstack.shared_file_system.v2.share." + "Share.shrink_share",
            self.proxy.resize_share,
            method_args=['fakeId', 20],
            expected_args=[self.proxy, 20],
        )

    def test_share_instances(self):
        self.verify_list(
            self.proxy.share_instances, share_instance.ShareInstance
        )

    def test_share_instance_get(self):
        self.verify_get(
            self.proxy.get_share_instance, share_instance.ShareInstance
        )

    def test_share_instance_reset(self):
        self._verify(
            "openstack.shared_file_system.v2.share_instance."
            + "ShareInstance.reset_status",
            self.proxy.reset_share_instance_status,
            method_args=['id', 'available'],
            expected_args=[self.proxy, 'available'],
        )

    def test_share_instance_delete(self):
        self._verify(
            "openstack.shared_file_system.v2.share_instance."
            + "ShareInstance.force_delete",
            self.proxy.delete_share_instance,
            method_args=['id'],
            expected_args=[self.proxy],
        )

    @mock.patch("openstack.resource.wait_for_status")
    def test_wait_for(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_status(mock_resource, 'ACTIVE')

        mock_wait.assert_called_once_with(
            self.proxy, mock_resource, 'ACTIVE', None, 2, None, 'status', None
        )


class TestSharedFileSystemStoragePool(TestSharedFileSystemProxy):
    def test_storage_pools(self):
        self.verify_list(self.proxy.storage_pools, storage_pool.StoragePool)

    def test_storage_pool_detailed(self):
        self.verify_list(
            self.proxy.storage_pools,
            storage_pool.StoragePool,
            method_kwargs={"details": True, "backend": "alpha"},
            expected_kwargs={"backend": "alpha"},
        )

    def test_storage_pool_not_detailed(self):
        self.verify_list(
            self.proxy.storage_pools,
            storage_pool.StoragePool,
            method_kwargs={"details": False, "backend": "alpha"},
            expected_kwargs={"backend": "alpha"},
        )


class TestSharedFileSystemShareMetadata(TestSharedFileSystemProxy):
    def test_get_share_metadata(self):
        self._verify(
            "openstack.shared_file_system.v2.share.Share.fetch_metadata",
            self.proxy.get_share_metadata,
            method_args=["share_id"],
            expected_args=[self.proxy],
            expected_result=share.Share(
                id="share_id", metadata={"key": "value"}
            ),
        )

    def test_get_share_metadata_item(self):
        self._verify(
            "openstack.shared_file_system.v2.share.Share.get_metadata_item",
            self.proxy.get_share_metadata_item,
            method_args=["share_id", "key"],
            expected_args=[self.proxy, "key"],
            expected_result=share.Share(
                id="share_id", metadata={"key": "value"}
            ),
        )

    def test_create_share_metadata(self):
        metadata = {"foo": "bar", "newFoo": "newBar"}
        self._verify(
            "openstack.shared_file_system.v2.share.Share.set_metadata",
            self.proxy.create_share_metadata,
            method_args=["share_id"],
            method_kwargs=metadata,
            expected_args=[self.proxy],
            expected_kwargs={"metadata": metadata},
            expected_result=share.Share(id="share_id", metadata=metadata),
        )

    def test_update_share_metadata(self):
        metadata = {"foo": "bar", "newFoo": "newBar"}
        replace = True
        self._verify(
            "openstack.shared_file_system.v2.share.Share.set_metadata",
            self.proxy.update_share_metadata,
            method_args=["share_id", metadata, replace],
            expected_args=[self.proxy],
            expected_kwargs={"metadata": metadata, "replace": replace},
            expected_result=share.Share(id="share_id", metadata=metadata),
        )

    def test_delete_share_metadata(self):
        self._verify(
            "openstack.shared_file_system.v2.share.Share.delete_metadata_item",
            self.proxy.delete_share_metadata,
            expected_result=None,
            method_args=["share_id", ["key"]],
            expected_args=[self.proxy, "key"],
        )


class TestUserMessageProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_user_messages(self):
        self.verify_list(self.proxy.user_messages, user_message.UserMessage)

    def test_user_messages_queried(self):
        self.verify_list(
            self.proxy.user_messages,
            user_message.UserMessage,
            method_kwargs={"action_id": "1"},
            expected_kwargs={"action_id": "1"},
        )

    def test_user_message_get(self):
        self.verify_get(self.proxy.get_user_message, user_message.UserMessage)

    def test_delete_user_message(self):
        self.verify_delete(
            self.proxy.delete_user_message, user_message.UserMessage, False
        )

    def test_delete_user_message_true(self):
        self.verify_delete(
            self.proxy.delete_user_message, user_message.UserMessage, True
        )

    def test_limit(self):
        self.verify_list(self.proxy.limits, limit.Limit)


class TestShareSnapshotResource(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_share_snapshots(self):
        self.verify_list(
            self.proxy.share_snapshots, share_snapshot.ShareSnapshot
        )

    def test_share_snapshots_detailed(self):
        self.verify_list(
            self.proxy.share_snapshots,
            share_snapshot.ShareSnapshot,
            method_kwargs={"details": True, "name": "my_snapshot"},
            expected_kwargs={"name": "my_snapshot"},
        )

    def test_share_snapshots_not_detailed(self):
        self.verify_list(
            self.proxy.share_snapshots,
            share_snapshot.ShareSnapshot,
            method_kwargs={"details": False, "name": "my_snapshot"},
            expected_kwargs={"name": "my_snapshot"},
        )

    def test_share_snapshot_get(self):
        self.verify_get(
            self.proxy.get_share_snapshot, share_snapshot.ShareSnapshot
        )

    def test_share_snapshot_delete(self):
        self.verify_delete(
            self.proxy.delete_share_snapshot,
            share_snapshot.ShareSnapshot,
            False,
        )

    def test_share_snapshot_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_share_snapshot,
            share_snapshot.ShareSnapshot,
            True,
        )

    def test_share_snapshot_create(self):
        self.verify_create(
            self.proxy.create_share_snapshot, share_snapshot.ShareSnapshot
        )

    def test_share_snapshot_update(self):
        self.verify_update(
            self.proxy.update_share_snapshot, share_snapshot.ShareSnapshot
        )

    @mock.patch("openstack.resource.wait_for_delete")
    def test_wait_for_delete(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_delete(mock_resource)

        mock_wait.assert_called_once_with(
            self.proxy, mock_resource, 2, 120, None
        )


class TestShareSnapshotInstanceResource(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_share_snapshot_instances(self):
        self.verify_list(
            self.proxy.share_snapshot_instances,
            share_snapshot_instance.ShareSnapshotInstance,
        )

    def test_share_snapshot_instance_detailed(self):
        self.verify_list(
            self.proxy.share_snapshot_instances,
            share_snapshot_instance.ShareSnapshotInstance,
            method_kwargs={"details": True, "query": {'snapshot_id': 'fake'}},
            expected_kwargs={"query": {'snapshot_id': 'fake'}},
        )

    def test_share_snapshot_instance_not_detailed(self):
        self.verify_list(
            self.proxy.share_snapshot_instances,
            share_snapshot_instance.ShareSnapshotInstance,
            method_kwargs={"details": False, "query": {'snapshot_id': 'fake'}},
            expected_kwargs={"query": {'snapshot_id': 'fake'}},
        )

    def test_share_snapshot_instance_get(self):
        self.verify_get(
            self.proxy.get_share_snapshot_instance,
            share_snapshot_instance.ShareSnapshotInstance,
        )


class TestShareNetworkResource(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_share_networks(self):
        self.verify_list(self.proxy.share_networks, share_network.ShareNetwork)

    def test_share_networks_detailed(self):
        self.verify_list(
            self.proxy.share_networks,
            share_network.ShareNetwork,
            method_kwargs={"details": True, "name": "my_net"},
            expected_kwargs={"name": "my_net"},
        )

    def test_share_networks_not_detailed(self):
        self.verify_list(
            self.proxy.share_networks,
            share_network.ShareNetwork,
            method_kwargs={"details": False, "name": "my_net"},
            expected_kwargs={"name": "my_net"},
        )

    def test_share_network_get(self):
        self.verify_get(
            self.proxy.get_share_network, share_network.ShareNetwork
        )

    def test_share_network_delete(self):
        self.verify_delete(
            self.proxy.delete_share_network, share_network.ShareNetwork, False
        )

    def test_share_network_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_share_network, share_network.ShareNetwork, True
        )

    def test_share_network_create(self):
        self.verify_create(
            self.proxy.create_share_network, share_network.ShareNetwork
        )

    def test_share_network_update(self):
        self.verify_update(
            self.proxy.update_share_network, share_network.ShareNetwork
        )


class TestShareNetworkSubnetResource(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_share_network_subnets(self):
        self.verify_list(
            self.proxy.share_network_subnets,
            share_network_subnet.ShareNetworkSubnet,
            method_args=["test_share"],
            expected_args=[],
            expected_kwargs={"share_network_id": "test_share"},
        )

    def test_share_network_subnet_get(self):
        self.verify_get(
            self.proxy.get_share_network_subnet,
            share_network_subnet.ShareNetworkSubnet,
            method_args=["fake_network_id", "fake_sub_network_id"],
            expected_args=['fake_sub_network_id'],
            expected_kwargs={'share_network_id': 'fake_network_id'},
        )

    def test_share_network_subnet_create(self):
        self.verify_create(
            self.proxy.create_share_network_subnet,
            share_network_subnet.ShareNetworkSubnet,
            method_args=["fake_network_id"],
            method_kwargs={"p1": "v1"},
            expected_args=[],
            expected_kwargs={
                "share_network_id": "fake_network_id",
                "p1": "v1",
            },
        )

    def test_share_network_subnet_delete(self):
        self.verify_delete(
            self.proxy.delete_share_network_subnet,
            share_network_subnet.ShareNetworkSubnet,
            False,
            method_args=["fake_network_id", "fake_sub_network_id"],
            expected_args=["fake_sub_network_id"],
            expected_kwargs={'share_network_id': 'fake_network_id'},
        )


class TestAccessRuleProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_access_ruless(self):
        self.verify_list(
            self.proxy.access_rules,
            share_access_rule.ShareAccessRule,
            method_args=["test_share"],
            expected_args=[],
            expected_kwargs={"share_id": "test_share"},
        )

    def test_access_rules_get(self):
        self.verify_get(
            self.proxy.get_access_rule, share_access_rule.ShareAccessRule
        )

    def test_access_rules_create(self):
        self.verify_create(
            self.proxy.create_access_rule,
            share_access_rule.ShareAccessRule,
            method_args=["share_id"],
            expected_args=[],
        )

    def test_access_rules_delete(self):
        self._verify(
            "openstack.shared_file_system.v2.share_access_rule.ShareAccessRule.delete",
            self.proxy.delete_access_rule,
            method_args=[
                'access_id',
                'share_id',
            ],
            expected_args=[self.proxy],
            expected_kwargs={'unrestrict': False},
        )


class TestResourceLocksProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_list_resource_locks(self):
        self.verify_list(
            self.proxy.resource_locks, resource_locks.ResourceLock
        )

    def test_resource_lock_get(self):
        self.verify_get(
            self.proxy.get_resource_lock, resource_locks.ResourceLock
        )

    def test_resource_lock_delete(self):
        self.verify_delete(
            self.proxy.delete_resource_lock, resource_locks.ResourceLock, False
        )

    def test_resource_lock_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_resource_lock, resource_locks.ResourceLock, True
        )

    def test_resource_lock_create(self):
        self.verify_create(
            self.proxy.create_resource_lock, resource_locks.ResourceLock
        )

    def test_resource_lock_update(self):
        self.verify_update(
            self.proxy.update_resource_lock, resource_locks.ResourceLock
        )


class TestShareGroupResource(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_share_groups(self):
        self.verify_list(self.proxy.share_groups, share_group.ShareGroup)

    def test_share_groups_query(self):
        self.verify_list(
            self.proxy.share_groups,
            share_group.ShareGroup,
            method_kwargs={"query": 1},
            expected_kwargs={"query": 1},
        )

    def test_share_group_get(self):
        self.verify_get(self.proxy.get_share_group, share_group.ShareGroup)

    def test_share_group_find(self):
        self.verify_find(self.proxy.find_share_group, share_group.ShareGroup)

    def test_share_group_delete(self):
        self.verify_delete(
            self.proxy.delete_share_group, share_group.ShareGroup, False
        )

    def test_share_group_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_share_group, share_group.ShareGroup, True
        )

    def test_share_group_create(self):
        self.verify_create(
            self.proxy.create_share_group, share_group.ShareGroup
        )

    def test_share_group_update(self):
        self.verify_update(
            self.proxy.update_share_group, share_group.ShareGroup
        )

    def test_share_group_snapshots(self):
        self.verify_list(
            self.proxy.share_group_snapshots,
            share_group_snapshot.ShareGroupSnapshot,
        )

    def test_share_group_snapshot_get(self):
        self.verify_get(
            self.proxy.get_share_group_snapshot,
            share_group_snapshot.ShareGroupSnapshot,
        )

    def test_share_group_snapshot_update(self):
        self.verify_update(
            self.proxy.update_share_group_snapshot,
            share_group_snapshot.ShareGroupSnapshot,
        )

    def test_share_group_snapshot_delete(self):
        self.verify_delete(
            self.proxy.delete_share_group_snapshot,
            share_group_snapshot.ShareGroupSnapshot,
            False,
        )

    def test_share_group_snapshot_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_share_group_snapshot,
            share_group_snapshot.ShareGroupSnapshot,
            True,
        )
