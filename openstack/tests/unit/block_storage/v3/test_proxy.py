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
import warnings

from openstack.block_storage.v3 import _proxy
from openstack.block_storage.v3 import backup
from openstack.block_storage.v3 import capabilities
from openstack.block_storage.v3 import extension
from openstack.block_storage.v3 import group
from openstack.block_storage.v3 import group_snapshot
from openstack.block_storage.v3 import group_type
from openstack.block_storage.v3 import quota_class_set
from openstack.block_storage.v3 import quota_set
from openstack.block_storage.v3 import resource_filter
from openstack.block_storage.v3 import service
from openstack.block_storage.v3 import snapshot
from openstack.block_storage.v3 import stats
from openstack.block_storage.v3 import transfer
from openstack.block_storage.v3 import type
from openstack.block_storage.v3 import volume
from openstack.identity.v3 import project
from openstack import proxy as proxy_base
from openstack.tests.unit import test_proxy_base
from openstack import warnings as os_warnings


class TestVolumeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestVolume(TestVolumeProxy):
    def test_volume_get(self):
        self.verify_get(self.proxy.get_volume, volume.Volume)

    def test_volume_find(self):
        self.verify_find(
            self.proxy.find_volume,
            volume.Volume,
            method_kwargs={'all_projects': True},
            expected_kwargs={
                "list_base_path": "/volumes/detail",
                "all_projects": True,
            },
        )

    def test_volumes_detailed(self):
        self.verify_list(
            self.proxy.volumes,
            volume.Volume,
            method_kwargs={"details": True, "query": 1},
            expected_kwargs={"query": 1, "base_path": "/volumes/detail"},
        )

    def test_volumes_not_detailed(self):
        self.verify_list(
            self.proxy.volumes,
            volume.Volume,
            method_kwargs={"details": False, "query": 1},
            expected_kwargs={"query": 1},
        )

    def test_volume_create_attrs(self):
        self.verify_create(self.proxy.create_volume, volume.Volume)

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_volume_delete(self, mock_mv):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.delete",
            self.proxy.delete_volume,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_kwargs={"params": {"cascade": False}},
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_volume_delete_force(self, mock_mv):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.force_delete",
            self.proxy.delete_volume,
            method_args=["value"],
            method_kwargs={"force": True},
            expected_args=[self.proxy],
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    def test_volume_delete_force_v323(self, mock_mv):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.delete",
            self.proxy.delete_volume,
            method_args=["value"],
            method_kwargs={"force": True},
            expected_args=[self.proxy],
            expected_kwargs={"params": {"cascade": False, "force": True}},
        )

    def test_volume_update(self):
        self.verify_update(self.proxy.update_volume, volume.Volume)

    def test_get_volume_metadata(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.fetch_metadata",
            self.proxy.get_volume_metadata,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_result=volume.Volume(id="value", metadata={}),
        )

    def test_set_volume_metadata(self):
        kwargs = {"a": "1", "b": "2"}
        id = "an_id"
        self._verify(
            "openstack.block_storage.v3.volume.Volume.set_metadata",
            self.proxy.set_volume_metadata,
            method_args=[id],
            method_kwargs=kwargs,
            method_result=volume.Volume.existing(id=id, metadata=kwargs),
            expected_args=[self.proxy],
            expected_kwargs={'metadata': kwargs},
            expected_result=volume.Volume.existing(id=id, metadata=kwargs),
        )

    def test_delete_volume_metadata(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.delete_metadata_item",
            self.proxy.delete_volume_metadata,
            expected_result=None,
            method_args=["value", ["key"]],
            expected_args=[self.proxy, "key"],
        )

    def test_volume_wait_for(self):
        value = volume.Volume(id='1234')
        self.verify_wait_for_status(
            self.proxy.wait_for_status,
            method_args=[value],
            expected_args=[
                self.proxy,
                value,
                'available',
                ['error'],
                2,
                None,
                'status',
                None,
            ],
        )


class TestPools(TestVolumeProxy):
    def test_backend_pools(self):
        self.verify_list(self.proxy.backend_pools, stats.Pools)


class TestLimit(TestVolumeProxy):
    def test_limits_get(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_limits,
            method_args=[],
            method_kwargs={'project': 'foo'},
            expected_args=[self.proxy],
            expected_kwargs={'requires_id': False, 'project_id': 'foo'},
        )


class TestCapabilities(TestVolumeProxy):
    def test_capabilites_get(self):
        self.verify_get(self.proxy.get_capabilities, capabilities.Capabilities)


class TestResourceFilter(TestVolumeProxy):
    def test_resource_filters(self):
        self.verify_list(
            self.proxy.resource_filters, resource_filter.ResourceFilter
        )


class TestGroup(TestVolumeProxy):
    def test_group_get(self):
        self.verify_get(self.proxy.get_group, group.Group)

    def test_group_find(self):
        self.verify_find(
            self.proxy.find_group,
            group.Group,
            expected_kwargs={'list_base_path': '/groups/detail'},
        )

    def test_groups(self):
        self.verify_list(self.proxy.groups, group.Group)

    def test_group_create(self):
        self.verify_create(self.proxy.create_group, group.Group)

    def test_group_create_from_source(self):
        self._verify(
            "openstack.block_storage.v3.group.Group.create_from_source",
            self.proxy.create_group_from_source,
            method_args=[],
            expected_args=[self.proxy],
        )

    def test_group_delete(self):
        self._verify(
            "openstack.block_storage.v3.group.Group.delete",
            self.proxy.delete_group,
            method_args=['delete_volumes'],
            expected_args=[self.proxy],
            expected_kwargs={'delete_volumes': False},
        )

    def test_group_update(self):
        self.verify_update(self.proxy.update_group, group.Group)

    def test_reset_group_status(self):
        self._verify(
            "openstack.block_storage.v3.group.Group.reset_status",
            self.proxy.reset_group_status,
            method_args=["value", "new_status"],
            expected_args=[self.proxy, "new_status"],
        )


class TestGroupSnapshot(TestVolumeProxy):
    def test_group_snapshot_get(self):
        self.verify_get(
            self.proxy.get_group_snapshot, group_snapshot.GroupSnapshot
        )

    def test_group_snapshot_find(self):
        self.verify_find(
            self.proxy.find_group_snapshot,
            group_snapshot.GroupSnapshot,
            expected_kwargs={
                'list_base_path': '/group_snapshots/detail',
            },
        )

    def test_group_snapshots(self):
        self.verify_list(
            self.proxy.group_snapshots,
            group_snapshot.GroupSnapshot,
            expected_kwargs={},
        )

    def test_group_snapshots__detailed(self):
        self.verify_list(
            self.proxy.group_snapshots,
            group_snapshot.GroupSnapshot,
            method_kwargs={'details': True, 'query': 1},
            expected_kwargs={
                'query': 1,
                'base_path': '/group_snapshots/detail',
            },
        )

    def test_group_snapshot_create(self):
        self.verify_create(
            self.proxy.create_group_snapshot, group_snapshot.GroupSnapshot
        )

    def test_group_snapshot_delete(self):
        self.verify_delete(
            self.proxy.delete_group_snapshot,
            group_snapshot.GroupSnapshot,
            False,
        )

    def test_group_snapshot_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_group_snapshot,
            group_snapshot.GroupSnapshot,
            True,
        )


class TestGroupType(TestVolumeProxy):
    def test_group_type_get(self):
        self.verify_get(self.proxy.get_group_type, group_type.GroupType)

    def test_group_type_find(self):
        self.verify_find(self.proxy.find_group_type, group_type.GroupType)

    def test_group_types(self):
        self.verify_list(self.proxy.group_types, group_type.GroupType)

    def test_group_type_create(self):
        self.verify_create(self.proxy.create_group_type, group_type.GroupType)

    def test_group_type_delete(self):
        self.verify_delete(
            self.proxy.delete_group_type, group_type.GroupType, False
        )

    def test_group_type_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_group_type, group_type.GroupType, True
        )

    def test_group_type_update(self):
        self.verify_update(self.proxy.update_group_type, group_type.GroupType)

    def test_group_type_fetch_group_specs(self):
        self._verify(
            "openstack.block_storage.v3.group_type.GroupType.fetch_group_specs",  # noqa: E501
            self.proxy.fetch_group_type_group_specs,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_group_type_create_group_specs(self):
        self._verify(
            "openstack.block_storage.v3.group_type.GroupType.create_group_specs",  # noqa: E501
            self.proxy.create_group_type_group_specs,
            method_args=["value", {'a': 'b'}],
            expected_args=[self.proxy],
            expected_kwargs={"specs": {'a': 'b'}},
        )

    def test_group_type_get_group_specs_prop(self):
        self._verify(
            "openstack.block_storage.v3.group_type.GroupType.get_group_specs_property",  # noqa: E501
            self.proxy.get_group_type_group_specs_property,
            method_args=["value", "prop"],
            expected_args=[self.proxy, "prop"],
        )

    def test_group_type_update_group_specs_prop(self):
        self._verify(
            "openstack.block_storage.v3.group_type.GroupType.update_group_specs_property",  # noqa: E501
            self.proxy.update_group_type_group_specs_property,
            method_args=["value", "prop", "val"],
            expected_args=[self.proxy, "prop", "val"],
        )

    def test_group_type_delete_group_specs_prop(self):
        self._verify(
            "openstack.block_storage.v3.group_type.GroupType.delete_group_specs_property",  # noqa: E501
            self.proxy.delete_group_type_group_specs_property,
            method_args=["value", "prop"],
            expected_args=[self.proxy, "prop"],
        )


class TestService(TestVolumeProxy):
    def test_services(self):
        self.verify_list(self.proxy.services, service.Service)

    def test_enable_service(self):
        self._verify(
            'openstack.block_storage.v3.service.Service.enable',
            self.proxy.enable_service,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_disable_service(self):
        self._verify(
            'openstack.block_storage.v3.service.Service.disable',
            self.proxy.disable_service,
            method_args=["value"],
            expected_kwargs={"reason": None},
            expected_args=[self.proxy],
        )

    def test_thaw_service(self):
        self._verify(
            'openstack.block_storage.v3.service.Service.thaw',
            self.proxy.thaw_service,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_freeze_service(self):
        self._verify(
            'openstack.block_storage.v3.service.Service.freeze',
            self.proxy.freeze_service,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_set_service_log_levels(self):
        self._verify(
            'openstack.block_storage.v3.service.Service.set_log_levels',
            self.proxy.set_service_log_levels,
            method_kwargs={"level": service.Level.INFO},
            expected_args=[self.proxy],
            expected_kwargs={
                "level": service.Level.INFO,
                "binary": None,
                "server": None,
                "prefix": None,
            },
        )

    def test_get_service_log_level(self):
        self._verify(
            'openstack.block_storage.v3.service.Service.get_log_levels',
            self.proxy.get_service_log_levels,
            method_args=[],
            expected_args=[self.proxy],
            expected_kwargs={
                "binary": None,
                "server": None,
                "prefix": None,
            },
        )

    def test_failover_service(self):
        self._verify(
            'openstack.block_storage.v3.service.Service.failover',
            self.proxy.failover_service,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_kwargs={"backend_id": None, "cluster": None},
        )


class TestExtension(TestVolumeProxy):
    def test_extensions(self):
        self.verify_list(self.proxy.extensions, extension.Extension)


class TestVolumeActions(TestVolumeProxy):
    def test_volume_extend(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.extend",
            self.proxy.extend_volume,
            method_args=["value", "new-size"],
            expected_args=[self.proxy, "new-size"],
        )

    def test_complete_extend(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.complete_extend",
            self.proxy.complete_volume_extend,
            method_args=["value"],
            expected_args=[self.proxy, False],
        )

    def test_complete_extend_error(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.complete_extend",
            self.proxy.complete_volume_extend,
            method_args=["value", True],
            expected_args=[self.proxy, True],
        )

    def test_volume_set_readonly_no_argument(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.set_readonly",
            self.proxy.set_volume_readonly,
            method_args=["value"],
            expected_args=[self.proxy, True],
        )

    def test_volume_set_readonly_false(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.set_readonly",
            self.proxy.set_volume_readonly,
            method_args=["value", False],
            expected_args=[self.proxy, False],
        )

    def test_volume_set_bootable(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.set_bootable_status",
            self.proxy.set_volume_bootable_status,
            method_args=["value", True],
            expected_args=[self.proxy, True],
        )

    def test_volume_reset_volume_status(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.reset_status",
            self.proxy.reset_volume_status,
            method_args=["value", '1', '2', '3'],
            expected_args=[self.proxy, '1', '2', '3'],
        )

    def test_set_volume_image_metadata(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.set_image_metadata",
            self.proxy.set_volume_image_metadata,
            method_args=["value"],
            method_kwargs={'foo': 'bar'},
            expected_args=[self.proxy],
            expected_kwargs={'metadata': {'foo': 'bar'}},
        )

    def test_delete_volume_image_metadata(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.delete_image_metadata",
            self.proxy.delete_volume_image_metadata,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_delete_volume_image_metadata__with_keys(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.delete_image_metadata_item",
            self.proxy.delete_volume_image_metadata,
            method_args=["value", ['foo']],
            expected_args=[self.proxy, 'foo'],
        )

    def test_volume_revert_to_snapshot(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.revert_to_snapshot",
            self.proxy.revert_volume_to_snapshot,
            method_args=["value", '1'],
            expected_args=[self.proxy, '1'],
        )

    def test_attach_instance(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.attach",
            self.proxy.attach_volume,
            method_args=["value", '1'],
            method_kwargs={'instance': '2'},
            expected_args=[self.proxy, '1', '2', None],
        )

    def test_attach_host(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.attach",
            self.proxy.attach_volume,
            method_args=["value", '1'],
            method_kwargs={'host_name': '3'},
            expected_args=[self.proxy, '1', None, '3'],
        )

    def test_detach_defaults(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.detach",
            self.proxy.detach_volume,
            method_args=["value", '1'],
            expected_args=[self.proxy, '1', False, None],
        )

    def test_detach_force(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.detach",
            self.proxy.detach_volume,
            method_args=["value", '1', True, {'a': 'b'}],
            expected_args=[self.proxy, '1', True, {'a': 'b'}],
        )

    def test_unmanage(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.unmanage",
            self.proxy.unmanage_volume,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_migrate_default(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.migrate",
            self.proxy.migrate_volume,
            method_args=["value", '1'],
            expected_args=[self.proxy, '1', False, False, None],
        )

    def test_migrate_nondefault(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.migrate",
            self.proxy.migrate_volume,
            method_args=["value", '1', True, True],
            expected_args=[self.proxy, '1', True, True, None],
        )

    def test_migrate_cluster(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.migrate",
            self.proxy.migrate_volume,
            method_args=["value"],
            method_kwargs={'cluster': '3'},
            expected_args=[self.proxy, None, False, False, '3'],
        )

    def test_complete_migration(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.complete_migration",
            self.proxy.complete_volume_migration,
            method_args=["value", '1'],
            expected_args=[self.proxy, "1", False],
        )

    def test_complete_migration_error(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.complete_migration",
            self.proxy.complete_volume_migration,
            method_args=["value", "1", True],
            expected_args=[self.proxy, "1", True],
        )

    def test_upload_to_image(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.upload_to_image",
            self.proxy.upload_volume_to_image,
            method_args=["value", "1"],
            expected_args=[self.proxy, "1"],
            expected_kwargs={
                "force": False,
                "disk_format": None,
                "container_format": None,
                "visibility": None,
                "protected": None,
            },
        )

    def test_upload_to_image_extended(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.upload_to_image",
            self.proxy.upload_volume_to_image,
            method_args=["value", "1"],
            method_kwargs={
                "disk_format": "2",
                "container_format": "3",
                "visibility": "4",
                "protected": "5",
            },
            expected_args=[self.proxy, "1"],
            expected_kwargs={
                "force": False,
                "disk_format": "2",
                "container_format": "3",
                "visibility": "4",
                "protected": "5",
            },
        )

    def test_reserve(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.reserve",
            self.proxy.reserve_volume,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_unreserve(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.unreserve",
            self.proxy.unreserve_volume,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_begin_detaching(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.begin_detaching",
            self.proxy.begin_volume_detaching,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_abort_detaching(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.abort_detaching",
            self.proxy.abort_volume_detaching,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_init_attachment(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.init_attachment",
            self.proxy.init_volume_attachment,
            method_args=["value", "1"],
            expected_args=[self.proxy, "1"],
        )

    def test_terminate_attachment(self):
        self._verify(
            "openstack.block_storage.v3.volume.Volume.terminate_attachment",
            self.proxy.terminate_volume_attachment,
            method_args=["value", "1"],
            expected_args=[self.proxy, "1"],
        )


class TestBackup(TestVolumeProxy):
    def test_backups_detailed(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_list(
            self.proxy.backups,
            backup.Backup,
            method_kwargs={"details": True, "query": 1},
            expected_kwargs={"query": 1, "base_path": "/backups/detail"},
        )

    def test_backups_not_detailed(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_list(
            self.proxy.backups,
            backup.Backup,
            method_kwargs={"details": False, "query": 1},
            expected_kwargs={"query": 1},
        )

    def test_backup_get(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_get(self.proxy.get_backup, backup.Backup)

    def test_backup_find(self):
        # NOTE: mock has_service
        self.proxy._connection = mock.Mock()
        self.proxy._connection.has_service = mock.Mock(return_value=True)
        self.verify_find(
            self.proxy.find_backup,
            backup.Backup,
            expected_kwargs={'list_base_path': '/backups/detail'},
        )

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
            "openstack.block_storage.v3.backup.Backup.force_delete",
            self.proxy.delete_backup,
            method_args=["value"],
            method_kwargs={"force": True},
            expected_args=[self.proxy],
        )

    def test_backup_update(self):
        self.verify_update(self.proxy.update_backup, backup.Backup)

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
            'openstack.block_storage.v3.backup.Backup.restore',
            self.proxy.restore_backup,
            method_args=['volume_id'],
            method_kwargs={'volume_id': 'vol_id', 'name': 'name'},
            expected_args=[self.proxy],
            expected_kwargs={'volume_id': 'vol_id', 'name': 'name'},
        )

    def test_backup_reset_status(self):
        self._verify(
            "openstack.block_storage.v3.backup.Backup.reset_status",
            self.proxy.reset_backup_status,
            method_args=["value", "new_status"],
            expected_args=[self.proxy, "new_status"],
        )

    def test_backup_get_metadata(self):
        self._verify(
            "openstack.block_storage.v3.backup.Backup.fetch_metadata",
            self.proxy.get_backup_metadata,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_result=volume.Volume(id="value", metadata={}),
        )

    def test_backup_set_metadata(self):
        kwargs = {"a": "1", "b": "2"}
        id = "an_id"
        self._verify(
            "openstack.block_storage.v3.backup.Backup.set_metadata",
            self.proxy.set_backup_metadata,
            method_args=[id],
            method_kwargs=kwargs,
            method_result=volume.Volume.existing(id=id, metadata=kwargs),
            expected_args=[self.proxy],
            expected_kwargs={'metadata': kwargs},
            expected_result=volume.Volume.existing(id=id, metadata=kwargs),
        )

    def test_backup_delete_metadata(self):
        self._verify(
            "openstack.block_storage.v3.backup.Backup.delete_metadata_item",
            self.proxy.delete_backup_metadata,
            expected_result=None,
            method_args=["value", ["key"]],
            expected_args=[self.proxy, "key"],
        )


class TestSnapshot(TestVolumeProxy):
    def test_snapshot_get(self):
        self.verify_get(self.proxy.get_snapshot, snapshot.Snapshot)

    def test_snapshot_find(self):
        self.verify_find(
            self.proxy.find_snapshot,
            snapshot.Snapshot,
            method_kwargs={'all_projects': True},
            expected_kwargs={
                'list_base_path': '/snapshots/detail',
                'all_projects': True,
            },
        )

    def test_snapshots_detailed(self):
        self.verify_list(
            self.proxy.snapshots,
            snapshot.SnapshotDetail,
            method_kwargs={"details": True, "query": 1},
            expected_kwargs={"query": 1, "base_path": "/snapshots/detail"},
        )

    def test_snapshots_not_detailed(self):
        self.verify_list(
            self.proxy.snapshots,
            snapshot.Snapshot,
            method_kwargs={"details": False, "query": 1},
            expected_kwargs={"query": 1},
        )

    def test_snapshot_create_attrs(self):
        self.verify_create(self.proxy.create_snapshot, snapshot.Snapshot)

    def test_snapshot_update(self):
        self.verify_update(self.proxy.update_snapshot, snapshot.Snapshot)

    def test_snapshot_delete(self):
        self.verify_delete(
            self.proxy.delete_snapshot, snapshot.Snapshot, False
        )

    def test_snapshot_delete_ignore(self):
        self.verify_delete(self.proxy.delete_snapshot, snapshot.Snapshot, True)

    def test_snapshot_delete_force(self):
        self._verify(
            "openstack.block_storage.v3.snapshot.Snapshot.force_delete",
            self.proxy.delete_snapshot,
            method_args=["value"],
            method_kwargs={"force": True},
            expected_args=[self.proxy],
        )

    def test_snapshot_reset_status(self):
        self._verify(
            "openstack.block_storage.v3.snapshot.Snapshot.reset_status",
            self.proxy.reset_snapshot_status,
            method_args=["value", "new_status"],
            expected_args=[self.proxy, "new_status"],
        )

    def test_snapshot_set_status(self):
        self._verify(
            "openstack.block_storage.v3.snapshot.Snapshot.set_status",
            self.proxy.set_snapshot_status,
            method_args=["value", "new_status"],
            expected_args=[self.proxy, "new_status", None],
        )

    def test_snapshot_set_status_percentage(self):
        self._verify(
            "openstack.block_storage.v3.snapshot.Snapshot.set_status",
            self.proxy.set_snapshot_status,
            method_args=["value", "new_status", "per"],
            expected_args=[self.proxy, "new_status", "per"],
        )

    def test_snapshot_manage(self):
        kwargs = {
            "volume_id": "fake_id",
            "remote_source": "fake_volume",
            "snapshot_name": "fake_snap",
            "description": "test_snap",
            "property": {"k": "v"},
        }
        self._verify(
            "openstack.block_storage.v3.snapshot.Snapshot.manage",
            self.proxy.manage_snapshot,
            method_kwargs=kwargs,
            method_result=snapshot.Snapshot(id="fake_id"),
            expected_args=[self.proxy],
            expected_kwargs=kwargs,
            expected_result=snapshot.Snapshot(id="fake_id"),
        )

    def test_snapshot_unmanage(self):
        self._verify(
            "openstack.block_storage.v3.snapshot.Snapshot.unmanage",
            self.proxy.unmanage_snapshot,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_result=None,
        )

    def test_get_snapshot_metadata(self):
        self._verify(
            "openstack.block_storage.v3.snapshot.Snapshot.fetch_metadata",
            self.proxy.get_snapshot_metadata,
            method_args=["value"],
            expected_args=[self.proxy],
            expected_result=snapshot.Snapshot(id="value", metadata={}),
        )

    def test_set_snapshot_metadata(self):
        kwargs = {"a": "1", "b": "2"}
        id = "an_id"
        self._verify(
            "openstack.block_storage.v3.snapshot.Snapshot.set_metadata",
            self.proxy.set_snapshot_metadata,
            method_args=[id],
            method_kwargs=kwargs,
            method_result=snapshot.Snapshot.existing(id=id, metadata=kwargs),
            expected_args=[self.proxy],
            expected_kwargs={'metadata': kwargs},
            expected_result=snapshot.Snapshot.existing(id=id, metadata=kwargs),
        )

    def test_delete_snapshot_metadata(self):
        self._verify(
            "openstack.block_storage.v3.snapshot.Snapshot."
            "delete_metadata_item",
            self.proxy.delete_snapshot_metadata,
            expected_result=None,
            method_args=["value", ["key"]],
            expected_args=[self.proxy, "key"],
        )


class TestType(TestVolumeProxy):
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
        self._verify(
            "openstack.block_storage.v3.type.Type.set_extra_specs",
            self.proxy.update_type_extra_specs,
            method_args=[id],
            method_kwargs=kwargs,
            method_result=type.Type.existing(id=id, extra_specs=kwargs),
            expected_args=[self.proxy],
            expected_kwargs=kwargs,
            expected_result=kwargs,
        )

    def test_type_extra_specs_delete(self):
        self._verify(
            "openstack.block_storage.v3.type.Type.delete_extra_specs",
            self.proxy.delete_type_extra_specs,
            expected_result=None,
            method_args=["value", "key"],
            expected_args=[self.proxy, "key"],
        )

    def test_type_get_private_access(self):
        self._verify(
            "openstack.block_storage.v3.type.Type.get_private_access",
            self.proxy.get_type_access,
            method_args=["value"],
            expected_args=[self.proxy],
        )

    def test_type_add_private_access(self):
        self._verify(
            "openstack.block_storage.v3.type.Type.add_private_access",
            self.proxy.add_type_access,
            method_args=["value", "a"],
            expected_args=[self.proxy, "a"],
        )

    def test_type_remove_private_access(self):
        self._verify(
            "openstack.block_storage.v3.type.Type.remove_private_access",
            self.proxy.remove_type_access,
            method_args=["value", "a"],
            expected_args=[self.proxy, "a"],
        )

    def test_type_encryption_get(self):
        self.verify_get(
            self.proxy.get_type_encryption,
            type.TypeEncryption,
            method_args=['value'],
            expected_args=[],
            expected_kwargs={'volume_type_id': 'value', 'requires_id': False},
        )

    def test_type_encryption_create(self):
        self.verify_create(
            self.proxy.create_type_encryption,
            type.TypeEncryption,
            method_kwargs={'volume_type': 'id'},
            expected_kwargs={'volume_type_id': 'id'},
        )

    def test_type_encryption_update(self):
        # Verify that the get call was made with correct kwargs
        self.verify_get(
            self.proxy.get_type_encryption,
            type.TypeEncryption,
            method_args=['value'],
            expected_args=[],
            expected_kwargs={'volume_type_id': 'value', 'requires_id': False},
        )
        self.verify_update(
            self.proxy.update_type_encryption, type.TypeEncryption
        )

    def test_type_encryption_delete(self):
        # Verify that the get call was made with correct kwargs
        self.verify_get(
            self.proxy.get_type_encryption,
            type.TypeEncryption,
            method_args=['value'],
            expected_args=[],
            expected_kwargs={'volume_type_id': 'value', 'requires_id': False},
        )
        self.verify_delete(
            self.proxy.delete_type_encryption, type.TypeEncryption, False
        )

    def test_type_encryption_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_type_encryption, type.TypeEncryption, True
        )


class TestTransfer(TestVolumeProxy):
    def test_transfer_create(self):
        self.verify_create(self.proxy.create_transfer, transfer.Transfer)

    def test_transfer_delete(self):
        self.verify_delete(
            self.proxy.delete_transfer, transfer.Transfer, False
        )

    def test_transfer_get(self):
        self.verify_get(self.proxy.get_transfer, transfer.Transfer)

    def test_transfer_find(self):
        self.verify_find(self.proxy.find_transfer, transfer.Transfer)

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_transfers(self, mock_mv):
        self.verify_list(self.proxy.transfers, transfer.Transfer)

    def test_accept_transfer(self):
        self._verify(
            'openstack.block_storage.v3.transfer.Transfer.accept',
            self.proxy.accept_transfer,
            method_args=['value', 'auth_key'],
            expected_args=[self.proxy],
            expected_kwargs={'auth_key': 'auth_key'},
        )


class TestQuotaClassSet(TestVolumeProxy):
    def test_quota_class_set_get(self):
        self.verify_get(
            self.proxy.get_quota_class_set, quota_class_set.QuotaClassSet
        )

    def test_quota_class_set_update(self):
        self.verify_update(
            self.proxy.update_quota_class_set,
            quota_class_set.QuotaClassSet,
            False,
        )


class TestQuotaSet(TestVolumeProxy):
    def test_quota_set_get(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_quota_set,
            method_args=['prj'],
            expected_args=[
                self.proxy,
                False,
                None,
                None,
                False,
            ],
            expected_kwargs={
                'microversion': None,
                'resource_response_key': None,
                'usage': False,
            },
            method_result=quota_set.QuotaSet(),
            expected_result=quota_set.QuotaSet(),
        )

    def test_quota_set_get_query(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_quota_set,
            method_args=['prj'],
            method_kwargs={'usage': True, 'user_id': 'uid'},
            expected_args=[
                self.proxy,
                False,
                None,
                None,
                False,
            ],
            expected_kwargs={
                'microversion': None,
                'resource_response_key': None,
                'usage': True,
                'user_id': 'uid',
            },
        )

    def test_quota_set_get_defaults(self):
        self._verify(
            'openstack.resource.Resource.fetch',
            self.proxy.get_quota_set_defaults,
            method_args=['prj'],
            expected_args=[
                self.proxy,
                False,
                '/os-quota-sets/defaults',
                None,
                False,
            ],
            expected_kwargs={
                'microversion': None,
                'resource_response_key': None,
            },
        )

    def test_quota_set_reset(self):
        self._verify(
            'openstack.resource.Resource.delete',
            self.proxy.revert_quota_set,
            method_args=['prj'],
            method_kwargs={'user_id': 'uid'},
            expected_args=[self.proxy],
            expected_kwargs={'user_id': 'uid'},
        )

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_quota_set_update(self, mock_get):
        fake_project = project.Project(id='prj')
        mock_get.side_effect = [fake_project]

        self._verify(
            'openstack.proxy.Proxy._update',
            self.proxy.update_quota_set,
            method_args=['prj'],
            method_kwargs={'volumes': 123},
            expected_args=[quota_set.QuotaSet, None],
            expected_kwargs={'project_id': 'prj', 'volumes': 123},
        )
        mock_get.assert_called_once_with(project.Project, 'prj')

    @mock.patch.object(proxy_base.Proxy, "_get_resource")
    def test_quota_set_update__legacy(self, mock_get):
        fake_quota_set = quota_set.QuotaSet(project_id='prj')
        mock_get.side_effect = [fake_quota_set]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            self._verify(
                'openstack.resource.Resource.commit',
                self.proxy.update_quota_set,
                method_args=[fake_quota_set],
                method_kwargs={'ram': 123},
                expected_args=[self.proxy],
                expected_kwargs={},
            )

            self.assertEqual(1, len(w))
            self.assertEqual(
                os_warnings.RemovedInSDK50Warning,
                w[-1].category,
            )
            self.assertIn(
                "The signature of 'update_quota_set' has changed ",
                str(w[-1]),
            )
