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
from openstack.shared_file_system.v2 import quota_class_set
from openstack.shared_file_system.v2 import resource_locks
from openstack.shared_file_system.v2 import service
from openstack.shared_file_system.v2 import share
from openstack.shared_file_system.v2 import share_access_rule
from openstack.shared_file_system.v2 import share_group
from openstack.shared_file_system.v2 import share_group_snapshot
from openstack.shared_file_system.v2 import share_instance
from openstack.shared_file_system.v2 import share_network
from openstack.shared_file_system.v2 import share_network_subnet
from openstack.shared_file_system.v2 import share_replica
from openstack.shared_file_system.v2 import share_snapshot
from openstack.shared_file_system.v2 import share_snapshot_instance
from openstack.shared_file_system.v2 import share_type
from openstack.shared_file_system.v2 import storage_pool
from openstack.shared_file_system.v2 import user_message
from openstack.tests.unit import test_proxy_base


class TestSharedFileSystemProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestQuotaClassSet(TestSharedFileSystemProxy):
    def test_get_quota_class_set(self):
        self.verify_get(
            self.proxy.get_quota_class_set,
            quota_class_set.QuotaClassSet,
        )

    def test_update_quota_class_set(self):
        self.verify_update(
            self.proxy.update_quota_class_set,
            quota_class_set.QuotaClassSet,
        )


class TestQuotaSet(TestSharedFileSystemProxy):
    def test_get_quota_set(self):
        self._verify(
            'openstack.common.quota_set.QuotaSet.fetch',
            self.proxy.get_quota_set,
            method_args=['prj'],
            expected_args=[self.proxy],
        )

    def test_update_quota_set(self):
        self._verify(
            'openstack.resource.Resource.commit',
            self.proxy.update_quota_set,
            method_args=['prj'],
            method_kwargs={'gigabytes': 100},
            expected_args=[self.proxy],
        )

    def test_revert_quota_set(self):
        self._verify(
            'openstack.resource.Resource.delete',
            self.proxy.revert_quota_set,
            method_args=['prj'],
            expected_args=[self.proxy],
        )


class TestShare(TestSharedFileSystemProxy):
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
            "openstack.shared_file_system.v2.share.Share.extend_share",
            self.proxy.resize_share,
            method_args=['fakeId', 20],
            expected_args=[self.proxy, 20, False],
        )

    def test_share_resize_shrink(self):
        mock_share = share.Share(size=30, id='fakeId')
        self.proxy._get = mock.Mock(return_value=mock_share)

        self._verify(
            "openstack.shared_file_system.v2.share.Share.shrink_share",
            self.proxy.resize_share,
            method_args=['fakeId', 20],
            expected_args=[self.proxy, 20],
        )

    def test_share_soft_delete(self):
        mock_share = share.Share(size=10, id='fakeId')
        self.proxy._get = mock.Mock(return_value=mock_share)

        self._verify(
            "openstack.shared_file_system.v2.share.Share.soft_delete",
            self.proxy.soft_delete_share,
            method_args=['fakeId'],
            expected_args=[self.proxy],
        )

    def test_share_force_delete(self):
        self._verify(
            "openstack.shared_file_system.v2.share.Share.force_delete",
            self.proxy.delete_share,
            method_args=['id'],
            method_kwargs={'force': True},
            expected_args=[self.proxy],
        )

    def test_share_restore(self):
        mock_share = share.Share(size=10, id='fakeId')
        self.proxy._get = mock.Mock(return_value=mock_share)

        self._verify(
            "openstack.shared_file_system.v2.share.Share.restore",
            self.proxy.restore_share,
            method_args=['fakeId'],
            expected_args=[self.proxy],
        )

    def test_share_reset_status(self):
        self._verify(
            "openstack.shared_file_system.v2.share.Share.reset_status",
            self.proxy.reset_share_status,
            method_args=['id', 'available'],
            expected_args=[self.proxy, 'available'],
        )


class TestShareInstance(TestSharedFileSystemProxy):
    def test_share_instances(self):
        self.verify_list(
            self.proxy.share_instances, share_instance.ShareInstance
        )

    def test_share_instance_get(self):
        self.verify_get(
            self.proxy.get_share_instance, share_instance.ShareInstance
        )

    def test_share_instance_reset_status(self):
        self._verify(
            "openstack.shared_file_system.v2.share_instance.ShareInstance.reset_status",
            self.proxy.reset_share_instance_status,
            method_args=['id', 'available'],
            expected_args=[self.proxy, 'available'],
        )

    def test_share_instance_delete(self):
        self._verify(
            "openstack.shared_file_system.v2.share_instance.ShareInstance.force_delete",
            self.proxy.delete_share_instance,
            method_args=['id'],
            expected_args=[self.proxy],
        )

    @mock.patch("openstack.resource.wait_for_status")
    def test_wait_for_status(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_status(mock_resource, 'ACTIVE')

        mock_wait.assert_called_once_with(
            self.proxy, mock_resource, 'ACTIVE', None, 2, None, 'status', None
        )

    @mock.patch("openstack.resource.wait_for_delete")
    def test_wait_for_delete(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_delete(mock_resource)

        mock_wait.assert_called_once_with(
            self.proxy, mock_resource, 2, 120, None
        )


class TestStoragePool(TestSharedFileSystemProxy):
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


class TestShareMetadata(TestSharedFileSystemProxy):
    def test_fetch_share_metadata(self):
        self._verify(
            "openstack.shared_file_system.v2.share.Share.fetch_metadata",
            self.proxy.fetch_share_metadata,
            method_args=["share_id"],
            expected_args=[self.proxy],
            expected_result=share.Share(
                id="share_id", metadata={"key": "value"}
            ),
        )

    def test_fetch_share_metadata_item(self):
        self._verify(
            "openstack.shared_file_system.v2.share.Share.get_metadata_item",
            self.proxy.fetch_share_metadata_item,
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
            expected_kwargs={"metadata": metadata, "replace": False},
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


class TestUserMessage(TestSharedFileSystemProxy):
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


class TestLimit(TestSharedFileSystemProxy):
    def test_limit(self):
        self.verify_list(self.proxy.limits, limit.Limit)


class TestShareSnapshot(TestSharedFileSystemProxy):
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

    def test_share_snapshot_force_delete(self):
        self._verify(
            "openstack.shared_file_system.v2.share_snapshot.ShareSnapshot.force_delete",
            self.proxy.delete_share_snapshot,
            method_args=['id'],
            method_kwargs={'force': True},
            expected_args=[self.proxy],
        )

    def test_share_snapshot_reset_status(self):
        self._verify(
            "openstack.shared_file_system.v2.share_snapshot.ShareSnapshot.reset_status",
            self.proxy.reset_share_snapshot_status,
            method_args=['id', 'available'],
            expected_args=[self.proxy, 'available'],
        )

    def test_manage_share_snapshot(self):
        self._verify(
            "openstack.shared_file_system.v2.share_snapshot.ShareSnapshot.manage",
            self.proxy.manage_share_snapshot,
            method_args=['share_id', 'provider_location'],
            expected_args=[self.proxy, 'share_id', 'provider_location'],
        )

    def test_unmanage_share_snapshot(self):
        self._verify(
            "openstack.shared_file_system.v2.share_snapshot.ShareSnapshot.unmanage",
            self.proxy.unmanage_share_snapshot,
            method_args=['id'],
            expected_args=[self.proxy],
        )


class TestShareSnapshotMetadata(TestSharedFileSystemProxy):
    def test_get_share_snapshot_metadata(self):
        self._verify(
            "openstack.shared_file_system.v2.share_snapshot.ShareSnapshot.fetch_metadata",
            self.proxy.fetch_share_snapshot_metadata,
            method_args=["snapshot_id"],
            expected_args=[self.proxy],
            expected_result=share_snapshot.ShareSnapshot(
                id="snapshot_id", metadata={"key": "value"}
            ),
        )

    def test_get_share_snapshot_metadata_item(self):
        self._verify(
            "openstack.shared_file_system.v2.share_snapshot.ShareSnapshot.get_metadata_item",
            self.proxy.fetch_share_snapshot_metadata_item,
            method_args=["snapshot_id", "key"],
            expected_args=[self.proxy, "key"],
            expected_result=share_snapshot.ShareSnapshot(
                id="snapshot_id", metadata={"key": "value"}
            ),
        )

    def test_set_share_snapshot_metadata(self):
        metadata = {"foo": "bar", "newFoo": "newBar"}
        self._verify(
            "openstack.shared_file_system.v2.share_snapshot.ShareSnapshot.set_metadata",
            self.proxy.set_share_snapshot_metadata,
            method_args=["snapshot_id"],
            method_kwargs=metadata,
            expected_args=[self.proxy],
            expected_kwargs={"metadata": metadata, "replace": False},
            expected_result=share_snapshot.ShareSnapshot(
                id="snapshot_id", metadata=metadata
            ),
        )

    def test_set_share_snapshot_metadata_replace(self):
        metadata = {"foo": "bar", "newFoo": "newBar"}
        self._verify(
            "openstack.shared_file_system.v2.share_snapshot.ShareSnapshot.set_metadata",
            self.proxy.set_share_snapshot_metadata,
            method_args=["snapshot_id"],
            method_kwargs={"replace": True, **metadata},
            expected_args=[self.proxy],
            expected_kwargs={"metadata": metadata, "replace": True},
            expected_result=share_snapshot.ShareSnapshot(
                id="snapshot_id", metadata=metadata
            ),
        )

    def test_delete_share_snapshot_metadata(self):
        self._verify(
            "openstack.shared_file_system.v2.share_snapshot.ShareSnapshot.delete_metadata_item",
            self.proxy.delete_share_snapshot_metadata,
            expected_result=None,
            method_args=["snapshot_id", ["key"]],
            expected_args=[self.proxy, "key"],
        )


class TestShareSnapshotInstance(TestSharedFileSystemProxy):
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


class TestShareNetwork(TestSharedFileSystemProxy):
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


class TestShareNetworkSubnet(TestSharedFileSystemProxy):
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


class TestShareNetworkSubnetMetadata(TestSharedFileSystemProxy):
    def test_fetch_share_network_subnet_metadata(self):
        self._verify(
            "openstack.shared_file_system.v2.share_network_subnet.ShareNetworkSubnet.fetch_metadata",
            self.proxy.fetch_share_network_subnet_metadata,
            method_args=["network_id", "subnet_id"],
            expected_args=[self.proxy],
            expected_result=share_network_subnet.ShareNetworkSubnet(
                id="subnet_id", metadata={"key": "value"}
            ),
        )

    def test_fetch_share_network_subnet_metadata_item(self):
        self._verify(
            "openstack.shared_file_system.v2.share_network_subnet.ShareNetworkSubnet.get_metadata_item",
            self.proxy.fetch_share_network_subnet_metadata_item,
            method_args=["network_id", "subnet_id", "key"],
            expected_args=[self.proxy, "key"],
            expected_result=share_network_subnet.ShareNetworkSubnet(
                id="subnet_id", metadata={"key": "value"}
            ),
        )

    def test_set_share_network_subnet_metadata(self):
        metadata = {"foo": "bar", "newFoo": "newBar"}
        self._verify(
            "openstack.shared_file_system.v2.share_network_subnet.ShareNetworkSubnet.set_metadata",
            self.proxy.set_share_network_subnet_metadata,
            method_args=["network_id", "subnet_id"],
            method_kwargs=metadata,
            expected_args=[self.proxy],
            expected_kwargs={"metadata": metadata, "replace": False},
            expected_result=share_network_subnet.ShareNetworkSubnet(
                id="subnet_id", metadata=metadata
            ),
        )

    def test_delete_share_network_subnet_metadata(self):
        self._verify(
            "openstack.shared_file_system.v2.share_network_subnet.ShareNetworkSubnet.delete_metadata_item",
            self.proxy.delete_share_network_subnet_metadata,
            method_args=["network_id", "subnet_id", ["key"]],
            expected_args=[self.proxy, "key"],
            expected_result=None,
        )


class TestAccessRule(TestSharedFileSystemProxy):
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


class TestResourceLock(TestSharedFileSystemProxy):
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


class TestShareGroup(TestSharedFileSystemProxy):
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


class TestShareReplica(TestSharedFileSystemProxy):
    def test_share_replicas(self):
        self.verify_list(self.proxy.share_replicas, share_replica.ShareReplica)

    def test_share_replica_get(self):
        self.verify_get(
            self.proxy.get_share_replica, share_replica.ShareReplica
        )

    def test_share_replica_delete(self):
        self.verify_delete(
            self.proxy.delete_share_replica, share_replica.ShareReplica, False
        )

    def test_share_replica_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_share_replica, share_replica.ShareReplica, True
        )

    def test_share_replica_force_delete(self):
        self._verify(
            "openstack.shared_file_system.v2.share_replica.ShareReplica.force_delete",
            self.proxy.delete_share_replica,
            method_args=['id', 'ignore_missing', 'force'],
            expected_args=[self.proxy],
        )

    def test_share_replica_reset_status(self):
        self._verify(
            "openstack.shared_file_system.v2.share_replica.ShareReplica.reset_status",
            self.proxy.reset_share_replica_status,
            method_args=['id', 'available'],
            expected_args=[self.proxy, 'available'],
        )

    def test_share_replica_reset_state(self):
        self._verify(
            "openstack.shared_file_system.v2.share_replica.ShareReplica.reset_replica_state",
            self.proxy.reset_share_replica_state,
            method_args=['id', 'active'],
            expected_args=[self.proxy, 'active'],
        )

    def test_share_replica_promote(self):
        self._verify(
            "openstack.shared_file_system.v2.share_replica.ShareReplica.promote",
            self.proxy.promote_share_replica,
            method_args=['id'],
            expected_args=[self.proxy],
        )

    def test_share_replica_resync(self):
        self._verify(
            "openstack.shared_file_system.v2.share_replica.ShareReplica.resync",
            self.proxy.resync_share_replica,
            method_args=['id'],
            expected_args=[self.proxy],
        )


class TestServicesResource(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_services(self):
        self.verify_list(self.proxy.services, service.Service)

    def test_services_queried(self):
        self.verify_list(
            self.proxy.services,
            service.Service,
            method_kwargs={"name": "manila-share"},
            expected_kwargs={"name": "manila-share"},
        )

    def test_service_enable(self):
        self._verify(
            'openstack.shared_file_system.v2.service.Service.enable',
            self.proxy.enable_service,
            method_args=["value", "host1", "manila-share"],
            expected_args=[self.proxy],
        )

    def test_service_disable(self):
        self._verify(
            'openstack.shared_file_system.v2.service.Service.disable',
            self.proxy.disable_service,
            method_args=["value", "host1", "manila-share"],
            expected_args=[self.proxy],
        )


class TestShareTypeResource(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_share_types(self):
        self.verify_list(self.proxy.share_types, share_type.ShareType)

    def test_share_types_query(self):
        self.verify_list(
            self.proxy.share_types,
            share_type.ShareType,
            method_kwargs={"name": "my_share_type"},
            expected_kwargs={"name": "my_share_type"},
        )

    def test_share_type_get(self):
        self.verify_get(self.proxy.get_share_type, share_type.ShareType)

    def test_share_type_delete(self):
        self.verify_delete(
            self.proxy.delete_share_type, share_type.ShareType, False
        )

    def test_share_type_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_share_type, share_type.ShareType, True
        )

    def test_share_type_create(self):
        self.verify_create(
            self.proxy.create_share_type,
            share_type.ShareType,
            method_kwargs={
                "extra_specs": {"driver_handles_share_servers": "False"},
                "name": "my_share_type",
            },
            expected_kwargs={
                "extra_specs": {"driver_handles_share_servers": "False"},
                "name": "my_share_type",
            },
        )

    def test_share_type_update(self):
        self.verify_update(self.proxy.update_share_type, share_type.ShareType)

    def test_share_type_extra_specs_update(self):
        self._verify(
            "openstack.shared_file_system.v2.share_type.ShareType.set_extra_specs",
            self.proxy.update_share_type_extra_specs,
            method_args=["value"],
            method_kwargs={"a": "b"},
            expected_args=[self.proxy],
            expected_kwargs={"a": "b"},
        )

    def test_share_type_extra_spec_property_delete(self):
        self._verify(
            "openstack.shared_file_system.v2.share_type.ShareType.delete_extra_specs_property",
            self.proxy.delete_share_type_extra_spec_property,
            expected_result=None,
            method_args=["value", "key"],
            expected_args=[self.proxy, "key"],
        )
