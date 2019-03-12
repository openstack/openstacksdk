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
import mock

from openstack import exceptions

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

    def test_volume_get(self):
        self.verify_get(self.proxy.get_volume, volume.Volume)

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

    def test_backup_no_swift(self):
        """Ensure proxy method raises exception if swift is not available
        """
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=False)
        self.assertRaises(
            exceptions.SDKException,
            self.proxy.restore_backup,
            'backup',
            'volume_id',
            'name')
