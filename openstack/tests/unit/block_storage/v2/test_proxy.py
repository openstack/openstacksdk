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

from openstack.block_storage.v2 import _proxy
from openstack.block_storage.v2 import backup
from openstack.block_storage.v2 import quota_set
from openstack.block_storage.v2 import snapshot
from openstack.block_storage.v2 import stats
from openstack.block_storage.v2 import type
from openstack.block_storage.v2 import volume
from openstack import resource
from openstack.tests.unit import test_proxy_base


class TestVolumeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestVolumeProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestVolume(TestVolumeProxy):

    def test_volume_get(self):
        self.verify_get(self.proxy.get_volume, volume.Volume)

    def test_volume_find(self):
        self.verify_find(self.proxy.find_volume, volume.Volume)

    def test_volumes_detailed(self):
        self.verify_list(self.proxy.volumes, volume.Volume,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1,
                                          "base_path": "/volumes/detail"})

    def test_volumes_not_detailed(self):
        self.verify_list(self.proxy.volumes, volume.Volume,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

    def test_volume_create_attrs(self):
        self.verify_create(self.proxy.create_volume, volume.Volume)

    def test_volume_delete(self):
        self.verify_delete(self.proxy.delete_volume, volume.Volume, False)

    def test_volume_delete_ignore(self):
        self.verify_delete(self.proxy.delete_volume, volume.Volume, True)

    def test_volume_delete_force(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.force_delete",
            self.proxy.delete_volume,
            method_args=["value"],
            method_kwargs={"force": True},
            expected_args=[self.proxy]
        )

    def test_get_volume_metadata(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.fetch_metadata",
            self.proxy.get_volume_metadata,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_result=volume.Volume(id="value", metadata={}))

    def test_set_volume_metadata(self):
        kwargs = {"a": "1", "b": "2"}
        id = "an_id"
        self._verify(
            "openstack.block_storage.v2.volume.Volume.set_metadata",
            self.proxy.set_volume_metadata,
            method_args=[id],
            method_kwargs=kwargs,
            method_result=volume.Volume.existing(
                id=id, metadata=kwargs),
            expected_args=[self.proxy],
            expected_kwargs={'metadata': kwargs},
            expected_result=volume.Volume.existing(
                id=id, metadata=kwargs))

    def test_delete_volume_metadata(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.delete_metadata_item",
            self.proxy.delete_volume_metadata,
            expected_result=None,
            method_args=["value", ["key"]],
            expected_args=[self.proxy, "key"])

    def test_backend_pools(self):
        self.verify_list(self.proxy.backend_pools, stats.Pools)

    def test_volume_wait_for(self):
        value = volume.Volume(id='1234')
        self.verify_wait_for_status(
            self.proxy.wait_for_status,
            method_args=[value],
            expected_args=[self.proxy, value, 'available', ['error'], 2, 120])


class TestVolumeActions(TestVolumeProxy):

    def test_volume_extend(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.extend",
            self.proxy.extend_volume,
            method_args=["value", "new-size"],
            expected_args=[self.proxy, "new-size"])

    def test_volume_set_bootable(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.set_bootable_status",
            self.proxy.set_volume_bootable_status,
            method_args=["value", True],
            expected_args=[self.proxy, True])

    def test_volume_reset_volume_status(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.reset_status",
            self.proxy.reset_volume_status,
            method_args=["value", '1', '2', '3'],
            expected_args=[self.proxy, '1', '2', '3'])

    def test_attach_instance(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.attach",
            self.proxy.attach_volume,
            method_args=["value", '1'],
            method_kwargs={'instance': '2'},
            expected_args=[self.proxy, '1', '2', None])

    def test_attach_host(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.attach",
            self.proxy.attach_volume,
            method_args=["value", '1'],
            method_kwargs={'host_name': '3'},
            expected_args=[self.proxy, '1', None, '3'])

    def test_detach_defaults(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.detach",
            self.proxy.detach_volume,
            method_args=["value", '1'],
            expected_args=[self.proxy, '1', False, None])

    def test_detach_force(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.detach",
            self.proxy.detach_volume,
            method_args=["value", '1', True, {'a': 'b'}],
            expected_args=[self.proxy, '1', True, {'a': 'b'}])

    def test_unmanage(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.unmanage",
            self.proxy.unmanage_volume,
            method_args=["value"],
            expected_args=[self.proxy])

    def test_migrate_default(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.migrate",
            self.proxy.migrate_volume,
            method_args=["value", '1'],
            expected_args=[self.proxy, '1', False, False])

    def test_migrate_nondefault(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.migrate",
            self.proxy.migrate_volume,
            method_args=["value", '1', True, True],
            expected_args=[self.proxy, '1', True, True])

    def test_complete_migration(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.complete_migration",
            self.proxy.complete_volume_migration,
            method_args=["value", '1'],
            expected_args=[self.proxy, "1", False])

    def test_complete_migration_error(self):
        self._verify(
            "openstack.block_storage.v2.volume.Volume.complete_migration",
            self.proxy.complete_volume_migration,
            method_args=["value", "1", True],
            expected_args=[self.proxy, "1", True])


class TestBackup(TestVolumeProxy):
    def test_backups_detailed(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_list(self.proxy.backups, backup.Backup,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1,
                                          "base_path": "/backups/detail"})

    def test_backups_not_detailed(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_list(self.proxy.backups, backup.Backup,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

    def test_backup_get(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_get(self.proxy.get_backup, backup.Backup)

    def test_backup_delete(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_delete(self.proxy.delete_backup, backup.Backup, False)

    def test_backup_delete_ignore(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_delete(self.proxy.delete_backup, backup.Backup, True)

    def test_backup_delete_force(self):
        self._verify(
            "openstack.block_storage.v2.backup.Backup.force_delete",
            self.proxy.delete_backup,
            method_args=["value"],
            method_kwargs={"force": True},
            expected_args=[self.proxy]
        )

    def test_backup_create_attrs(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_create(self.proxy.create_backup, backup.Backup)

    def test_backup_restore(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self._verify(
            'openstack.block_storage.v2.backup.Backup.restore',
            self.proxy.restore_backup,
            method_args=['volume_id'],
            method_kwargs={'volume_id': 'vol_id', 'name': 'name'},
            expected_args=[self.proxy],
            expected_kwargs={'volume_id': 'vol_id', 'name': 'name'}
        )

    def test_backup_reset(self):
        self._verify(
            "openstack.block_storage.v2.backup.Backup.reset",
            self.proxy.reset_backup,
            method_args=["value", "new_status"],
            expected_args=[self.proxy, "new_status"])


class TestSnapshot(TestVolumeProxy):
    def test_snapshot_get(self):
        self.verify_get(self.proxy.get_snapshot, snapshot.Snapshot)

    def test_snapshots_detailed(self):
        self.verify_list(self.proxy.snapshots, snapshot.SnapshotDetail,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1})

    def test_snapshots_not_detailed(self):
        self.verify_list(self.proxy.snapshots, snapshot.Snapshot,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

    def test_snapshot_create_attrs(self):
        self.verify_create(self.proxy.create_snapshot, snapshot.Snapshot)

    def test_snapshot_delete(self):
        self.verify_delete(self.proxy.delete_snapshot,
                           snapshot.Snapshot, False)

    def test_snapshot_delete_ignore(self):
        self.verify_delete(self.proxy.delete_snapshot,
                           snapshot.Snapshot, True)

    def test_reset(self):
        self._verify(
            "openstack.block_storage.v2.snapshot.Snapshot.reset",
            self.proxy.reset_snapshot,
            method_args=["value", "new_status"],
            expected_args=[self.proxy, "new_status"])

    def test_get_snapshot_metadata(self):
        self._verify(
            "openstack.block_storage.v2.snapshot.Snapshot.fetch_metadata",
            self.proxy.get_snapshot_metadata,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_result=snapshot.Snapshot(id="value", metadata={}))

    def test_set_snapshot_metadata(self):
        kwargs = {"a": "1", "b": "2"}
        id = "an_id"
        self._verify(
            "openstack.block_storage.v2.snapshot.Snapshot.set_metadata",
            self.proxy.set_snapshot_metadata,
            method_args=[id],
            method_kwargs=kwargs,
            method_result=snapshot.Snapshot.existing(
                id=id, metadata=kwargs),
            expected_args=[self.proxy],
            expected_kwargs={'metadata': kwargs},
            expected_result=snapshot.Snapshot.existing(
                id=id, metadata=kwargs))

    def test_delete_snapshot_metadata(self):
        self._verify(
            "openstack.block_storage.v2.snapshot.Snapshot."
            "delete_metadata_item",
            self.proxy.delete_snapshot_metadata,
            expected_result=None,
            method_args=["value", ["key"]],
            expected_args=[self.proxy, "key"])


class TestType(TestVolumeProxy):
    def test_type_get(self):
        self.verify_get(self.proxy.get_type, type.Type)

    def test_types(self):
        self.verify_list(self.proxy.types, type.Type)

    def test_type_create_attrs(self):
        self.verify_create(self.proxy.create_type, type.Type)

    def test_type_delete(self):
        self.verify_delete(self.proxy.delete_type, type.Type, False)

    def test_type_delete_ignore(self):
        self.verify_delete(self.proxy.delete_type, type.Type, True)

    def test_type_get_private_access(self):
        self._verify(
            "openstack.block_storage.v2.type.Type.get_private_access",
            self.proxy.get_type_access,
            method_args=["value"],
            expected_args=[self.proxy])

    def test_type_add_private_access(self):
        self._verify(
            "openstack.block_storage.v2.type.Type.add_private_access",
            self.proxy.add_type_access,
            method_args=["value", "a"],
            expected_args=[self.proxy, "a"])

    def test_type_remove_private_access(self):
        self._verify(
            "openstack.block_storage.v2.type.Type.remove_private_access",
            self.proxy.remove_type_access,
            method_args=["value", "a"],
            expected_args=[self.proxy, "a"])


class TestQuota(TestVolumeProxy):
    def test_get(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_quota_set,
            method_args=['prj'],
            expected_args=[self.proxy],
            expected_kwargs={
                'error_message': None,
                'requires_id': False,
                'usage': False,
            },
            method_result=quota_set.QuotaSet(),
            expected_result=quota_set.QuotaSet()
        )

    def test_get_query(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_quota_set,
            method_args=['prj'],
            method_kwargs={
                'usage': True,
                'user_id': 'uid'
            },
            expected_args=[self.proxy],
            expected_kwargs={
                'error_message': None,
                'requires_id': False,
                'usage': True,
                'user_id': 'uid'
            }
        )

    def test_get_defaults(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_quota_set_defaults,
            method_args=['prj'],
            expected_args=[self.proxy],
            expected_kwargs={
                'error_message': None,
                'requires_id': False,
                'base_path': '/os-quota-sets/defaults'
            }
        )

    def test_reset(self):
        self._verify(
            'openstack.resource.Resource.delete',
            self.proxy.revert_quota_set,
            method_args=['prj'],
            method_kwargs={'user_id': 'uid'},
            expected_args=[self.proxy],
            expected_kwargs={
                'user_id': 'uid'
            }
        )

    @mock.patch('openstack.proxy.Proxy._get_resource', autospec=True)
    def test_update(self, gr_mock):
        gr_mock.return_value = resource.Resource()
        gr_mock.commit = mock.Mock()
        self._verify(
            'openstack.resource.Resource.commit',
            self.proxy.update_quota_set,
            method_args=['qs'],
            method_kwargs={
                'query': {'user_id': 'uid'},
                'a': 'b',
            },
            expected_args=[self.proxy],
            expected_kwargs={
                'user_id': 'uid'
            }
        )
        gr_mock.assert_called_with(
            self.proxy,
            quota_set.QuotaSet,
            'qs', a='b'
        )
