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

from openstack.block_storage.v3 import _proxy
from openstack.block_storage.v3 import backup
from openstack.block_storage.v3 import snapshot
from openstack.block_storage.v3 import stats
from openstack.block_storage.v3 import type
from openstack.block_storage.v3 import volume
from openstack.tests.unit import test_proxy_base


class TestVolumeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestVolumeProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_snapshot_get(self):
        self.verify_get(self.proxy.get_snapshot, snapshot.Snapshot)

    def test_snapshot_find(self):
        self.verify_find(self.proxy.find_snapshot, snapshot.Snapshot)

    def test_snapshots_detailed(self):
        self.verify_list(self.proxy.snapshots, snapshot.SnapshotDetail,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1,
                                          "base_path": "/snapshots/detail"})

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

    def test_type_get(self):
        self.verify_get(self.proxy.get_type, type.Type)

    def test_type_find(self):
        self.verify_find(self.proxy.find_type, type.Type)

    def test_types(self):
        self.verify_list(self.proxy.types, type.Type)

    def test_type_create_attrs(self):
        self.verify_create(self.proxy.create_type, type.Type)

    def test_type_delete(self):
        self.verify_delete(self.proxy.delete_type, type.Type, False)

    def test_type_delete_ignore(self):
        self.verify_delete(self.proxy.delete_type, type.Type, True)

    def test_type_update(self):
        self.verify_update(self.proxy.update_type, type.Type)

    def test_type_extra_specs_update(self):
        kwargs = {"a": "1", "b": "2"}
        id = "an_id"
        self._verify2(
            "openstack.block_storage.v3.type.Type.set_extra_specs",
            self.proxy.update_type_extra_specs,
            method_args=[id],
            method_kwargs=kwargs,
            method_result=type.Type.existing(id=id,
                                             extra_specs=kwargs),
            expected_args=[self.proxy],
            expected_kwargs=kwargs,
            expected_result=kwargs)

    def test_type_extra_specs_delete(self):
        self._verify2(
            "openstack.block_storage.v3.type.Type.delete_extra_specs",
            self.proxy.delete_type_extra_specs,
            expected_result=None,
            method_args=["value", "key"],
            expected_args=[self.proxy, "key"])

    def test_type_encryption_get(self):
        self.verify_get(self.proxy.get_type_encryption,
                        type.TypeEncryption,
                        expected_args=[type.TypeEncryption],
                        expected_kwargs={
                            'volume_type_id': 'value',
                            'requires_id': False
                        })

    def test_type_encryption_create(self):
        self.verify_create(self.proxy.create_type_encryption,
                           type.TypeEncryption,
                           method_kwargs={'volume_type': 'id'},
                           expected_kwargs={'volume_type_id': 'id'}
                           )

    def test_type_encryption_update(self):
        self.verify_update(self.proxy.update_type_encryption,
                           type.TypeEncryption)

    def test_type_encryption_delete(self):
        self.verify_delete(self.proxy.delete_type_encryption,
                           type.TypeEncryption, False)

    def test_type_encryption_delete_ignore(self):
        self.verify_delete(self.proxy.delete_type_encryption,
                           type.TypeEncryption, True)

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

    def test_volume_extend(self):
        self._verify("openstack.block_storage.v3.volume.Volume.extend",
                     self.proxy.extend_volume,
                     method_args=["value", "new-size"],
                     expected_args=["new-size"])

    def test_backend_pools(self):
        self.verify_list(self.proxy.backend_pools, stats.Pools)

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

    def test_backup_find(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_find(self.proxy.find_backup, backup.Backup)

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

    def test_backup_create_attrs(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_create(self.proxy.create_backup, backup.Backup)

    def test_backup_restore(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self._verify2(
            'openstack.block_storage.v3.backup.Backup.restore',
            self.proxy.restore_backup,
            method_args=['volume_id'],
            method_kwargs={'volume_id': 'vol_id', 'name': 'name'},
            expected_args=[self.proxy],
            expected_kwargs={'volume_id': 'vol_id', 'name': 'name'}
        )
