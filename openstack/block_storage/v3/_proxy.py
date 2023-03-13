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

import typing as ty
import warnings

from openstack.block_storage.v3 import attachment as _attachment
from openstack.block_storage.v3 import availability_zone
from openstack.block_storage.v3 import backup as _backup
from openstack.block_storage.v3 import block_storage_summary as _summary
from openstack.block_storage.v3 import capabilities as _capabilities
from openstack.block_storage.v3 import default_type as _default_type
from openstack.block_storage.v3 import extension as _extension
from openstack.block_storage.v3 import group as _group
from openstack.block_storage.v3 import group_snapshot as _group_snapshot
from openstack.block_storage.v3 import group_type as _group_type
from openstack.block_storage.v3 import limits as _limits
from openstack.block_storage.v3 import quota_class_set as _quota_class_set
from openstack.block_storage.v3 import quota_set as _quota_set
from openstack.block_storage.v3 import resource_filter as _resource_filter
from openstack.block_storage.v3 import service as _service
from openstack.block_storage.v3 import snapshot as _snapshot
from openstack.block_storage.v3 import stats as _stats
from openstack.block_storage.v3 import transfer as _transfer
from openstack.block_storage.v3 import type as _type
from openstack.block_storage.v3 import volume as _volume
from openstack import exceptions
from openstack.identity.v3 import project as _project
from openstack import proxy
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings


class Proxy(proxy.Proxy):
    _resource_registry = {
        "availability_zone": availability_zone.AvailabilityZone,
        "attachment": _attachment.Attachment,
        "backup": _backup.Backup,
        "capabilities": _capabilities.Capabilities,
        "extension": _extension.Extension,
        "group": _group.Group,
        "group_snapshot": _group_snapshot.GroupSnapshot,
        "group_type": _group_type.GroupType,
        "limits": _limits.Limits,
        "quota_set": _quota_set.QuotaSet,
        "resource_filter": _resource_filter.ResourceFilter,
        "snapshot": _snapshot.Snapshot,
        "stats_pools": _stats.Pools,
        "summary": _summary.BlockStorageSummary,
        "transfer": _transfer.Transfer,
        "type": _type.Type,
        "volume": _volume.Volume,
    }

    # ====== IMAGES ======
    # TODO(stephenfin): Convert to use resources/proxy rather than direct calls
    def create_image(
        self,
        name,
        volume,
        allow_duplicates,
        container_format,
        disk_format,
        wait,
        timeout,
    ):
        if not disk_format:
            disk_format = self._connection.config.config['image_format']
        if not container_format:
            # https://docs.openstack.org/image-guide/image-formats.html
            container_format = 'bare'

        if 'id' in volume:
            volume_id = volume['id']
        else:
            volume_obj = self.get_volume(volume)
            if not volume_obj:
                raise exceptions.SDKException(
                    f"Volume {volume} given to create_image could not be found"
                )
            volume_id = volume_obj['id']
        data = self.post(
            f'/volumes/{volume_id}/action',
            json={
                'os-volume_upload_image': {
                    'force': allow_duplicates,
                    'image_name': name,
                    'container_format': container_format,
                    'disk_format': disk_format,
                }
            },
        )
        response = self._connection._get_and_munchify(
            'os-volume_upload_image', data
        )
        return self._connection.image._existing_image(id=response['image_id'])

    # ====== SNAPSHOTS ======
    def get_snapshot(self, snapshot):
        """Get a single snapshot

        :param snapshot: The value can be the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`
            instance.

        :returns: One :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_snapshot.Snapshot, snapshot)

    def find_snapshot(
        self,
        name_or_id,
        ignore_missing=True,
        *,
        details=True,
        all_projects=False,
    ):
        """Find a single snapshot

        :param snapshot: The name or ID a snapshot
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the snapshot does not exist. When set to ``True``, None will
            be returned when attempting to find a nonexistent resource.
        :param bool details: When set to ``False`` :class:
            `~openstack.block_storage.v3.snapshot.Snapshot` objects will be
            returned. The default, ``True``, will cause more attributes to be
            returned.
        :param bool all_projects: When set to ``True``, search for snapshot by
            name across all projects. Note that this will likely result in
            a higher chance of duplicates. Admin-only by default.

        :returns: One :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        query = {}
        if all_projects:
            query['all_projects'] = True
        list_base_path = '/snapshots/detail' if details else None
        return self._find(
            _snapshot.Snapshot,
            name_or_id,
            ignore_missing=ignore_missing,
            list_base_path=list_base_path,
            **query,
        )

    def snapshots(self, *, details=True, all_projects=False, **query):
        """Retrieve a generator of snapshots

        :param bool details: When set to ``False`` :class:
            `~openstack.block_storage.v3.snapshot.Snapshot`
            objects will be returned. The default, ``True``, will cause
            more attributes to be returned.
        :param bool all_projects: When set to ``True``, list snapshots from all
            projects. Admin-only by default.
        :param kwargs query: Optional query parameters to be sent to limit
            the snapshots being returned.  Available parameters include:

            * name: Name of the snapshot as a string.
            * project_id: Filter the snapshots by project.
            * volume_id: volume id of a snapshot.
            * status: Value of the status of the snapshot so that you can
              filter on "available" for example.

        :returns: A generator of snapshot objects.
        """
        if all_projects:
            query['all_projects'] = True
        base_path = '/snapshots/detail' if details else None
        return self._list(_snapshot.Snapshot, base_path=base_path, **query)

    def create_snapshot(self, **attrs):
        """Create a new snapshot from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.snapshot.Snapshot`,
            comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        :rtype: :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        """
        return self._create(_snapshot.Snapshot, **attrs)

    def update_snapshot(self, snapshot, **attrs):
        """Update a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` instance.
        :param dict attrs: The attributes to update on the snapshot.

        :returns: The updated snapshot
        :rtype: :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        """
        return self._update(_snapshot.Snapshot, snapshot, **attrs)

    def delete_snapshot(self, snapshot, ignore_missing=True, force=False):
        """Delete a snapshot

        :param snapshot: The value can be either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the snapshot does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent snapshot.
        :param bool force: Whether to try forcing snapshot deletion.

        :returns: ``None``
        """
        if not force:
            self._delete(
                _snapshot.Snapshot, snapshot, ignore_missing=ignore_missing
            )
        else:
            snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
            snapshot.force_delete(self)

    def get_snapshot_metadata(self, snapshot):
        """Return a dictionary of metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`.

        :returns: A
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` with the
            snapshot's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        return snapshot.fetch_metadata(self)

    def set_snapshot_metadata(self, snapshot, **metadata):
        """Update metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`.
        :param kwargs metadata: Key/value pairs to be updated in the snapshot's
            metadata. No other metadata is modified by this call. All keys
            and values are stored as Unicode.

        :returns: A
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` with the
            snapshot's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        return snapshot.set_metadata(self, metadata=metadata)

    def delete_snapshot_metadata(self, snapshot, keys=None):
        """Delete metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`.
        :param list keys: The keys to delete. If left empty complete
            metadata will be removed.

        :rtype: ``None``
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        if keys is not None:
            for key in keys:
                snapshot.delete_metadata_item(self, key)
        else:
            snapshot.delete_metadata(self)

    # ====== SNAPSHOT ACTIONS ======
    def reset_snapshot_status(self, snapshot, status):
        """Reset status of the snapshot

        :param snapshot: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` instance.
        :param str status: New snapshot status

        :returns: None
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        snapshot.reset_status(self, status)

    def reset_snapshot(self, snapshot, status):
        warnings.warn(
            "reset_snapshot is a deprecated alias for reset_snapshot_status "
            "and will be removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        return self.reset_snapshot_status(snapshot, status)

    def set_snapshot_status(self, snapshot, status, progress=None):
        """Update fields related to the status of a snapshot.

        :param snapshot: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` instance.
        :param str status: New snapshot status
        :param str progress: A percentage value for snapshot build progress.

        :returns: None
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        snapshot.set_status(self, status, progress)

    def manage_snapshot(self, **attrs):
        """Creates a snapshot by using existing storage rather than
        allocating new storage.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.snapshot.Snapshot`,
            comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        :rtype: :class:`~openstack.block_storage.v3.snapshot.Snapshot`
        """
        return _snapshot.Snapshot.manage(self, **attrs)

    def unmanage_snapshot(self, snapshot):
        """Unmanage a snapshot from block storage provisioning.

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`.

        :returns: None
        """
        snapshot_obj = self._get_resource(_snapshot.Snapshot, snapshot)
        snapshot_obj.unmanage(self)

    # ====== TYPES ======
    def get_type(self, type):
        """Get a single type

        :param type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.

        :returns: One :class:`~openstack.block_storage.v3.type.Type`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_type.Type, type)

    def find_type(self, name_or_id, ignore_missing=True):
        """Find a single volume type

        :param snapshot: The name or ID a volume type
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume type does not exist.

        :returns: One :class:`~openstack.block_storage.v3.type.Type`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        return self._find(
            _type.Type,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def types(self, **query):
        """Retrieve a generator of volume types

        :returns: A generator of volume type objects.
        """
        return self._list(_type.Type, **query)

    def create_type(self, **attrs):
        """Create a new type from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.type.Type`,
            comprised of the properties on the Type class.

        :returns: The results of type creation
        :rtype: :class:`~openstack.block_storage.v3.type.Type`
        """
        return self._create(_type.Type, **attrs)

    def delete_type(self, type, ignore_missing=True):
        """Delete a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the type does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent type.

        :returns: ``None``
        """
        self._delete(_type.Type, type, ignore_missing=ignore_missing)

    def update_type(self, type, **attrs):
        """Update a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param dict attrs: The attributes to update on the type

        :returns: The updated type
        :rtype: :class:`~openstack.block_storage.v3.type.Type`
        """
        return self._update(_type.Type, type, **attrs)

    def update_type_extra_specs(self, type, **attrs):
        """Update the extra_specs for a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param dict attrs: The extra spec attributes to update on the type

        :returns: A dict containing updated extra_specs
        """
        res = self._get_resource(_type.Type, type)
        extra_specs = res.set_extra_specs(self, **attrs)
        result = _type.Type.existing(id=res.id, extra_specs=extra_specs)
        return result

    def delete_type_extra_specs(self, type, keys):
        """Delete the extra_specs for a type

        Note: This method will do a HTTP DELETE request for every key in keys.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param keys: The keys to delete

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.delete_extra_specs(self, keys)

    def get_type_access(self, type):
        """Lists project IDs that have access to private volume type.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.

        :returns: List of dictionaries describing projects that have access to
            the specified type
        """
        res = self._get_resource(_type.Type, type)
        return res.get_private_access(self)

    def add_type_access(self, type, project_id):
        """Adds private volume type access to a project.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param str project_id: The ID of the project. Volume Type access to
            be added to this project ID.

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.add_private_access(self, project_id)

    def remove_type_access(self, type, project_id):
        """Remove private volume type access from a project.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param str project_id: The ID of the project. Volume Type access to
            be removed to this project ID.

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.remove_private_access(self, project_id)

    def get_type_encryption(self, volume_type_id):
        """Get the encryption details of a volume type

        :param volume_type_id: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type`
            instance.

        :returns: One :class:`~openstack.block_storage.v3.type.TypeEncryption`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        volume_type = self._get_resource(_type.Type, volume_type_id)

        return self._get(
            _type.TypeEncryption,
            volume_type_id=volume_type.id,
            requires_id=False,
        )

    def create_type_encryption(self, volume_type, **attrs):
        """Create new type encryption from attributes

        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type`
            instance.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.type.TypeEncryption`,
            comprised of the properties on the TypeEncryption class.

        :returns: The results of type encryption creation
        :rtype: :class:`~openstack.block_storage.v3.type.TypeEncryption`
        """
        volume_type = self._get_resource(_type.Type, volume_type)

        return self._create(
            _type.TypeEncryption, volume_type_id=volume_type.id, **attrs
        )

    def delete_type_encryption(
        self, encryption=None, volume_type=None, ignore_missing=True
    ):
        """Delete type encryption attributes

        :param encryption: The value can be None or a
            :class:`~openstack.block_storage.v3.type.TypeEncryption`
            instance.  If encryption_id is None then
            volume_type_id must be specified.

        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type`
            instance.  Required if encryption_id is None.

        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the type does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent type.

        :returns: ``None``
        """

        if volume_type:
            volume_type = self._get_resource(_type.Type, volume_type)
            encryption = self._get(
                _type.TypeEncryption,
                volume_type_id=volume_type.id,
                requires_id=False,
            )

        self._delete(
            _type.TypeEncryption, encryption, ignore_missing=ignore_missing
        )

    def update_type_encryption(
        self,
        encryption=None,
        volume_type=None,
        **attrs,
    ):
        """Update a type

        :param encryption: The value can be None or a
            :class:`~openstack.block_storage.v3.type.TypeEncryption`
            instance. If this is ``None`` then ``volume_type_id`` must be
            specified.
        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
            Required if ``encryption_id`` is None.
        :param dict attrs: The attributes to update on the type encryption.

        :returns: The updated type encryption
        :rtype: :class:`~openstack.block_storage.v3.type.TypeEncryption`
        """

        if volume_type:
            volume_type = self._get_resource(_type.Type, volume_type)
            encryption = self._get(
                _type.TypeEncryption,
                volume_type_id=volume_type.id,
                requires_id=False,
            )

        return self._update(_type.TypeEncryption, encryption, **attrs)

    # ====== DEFAULT TYPES ======

    def default_types(self):
        """Lists default types.

        :returns: List of default types associated to projects.
        """
        # This is required since previously default types did not accept
        # URL with project ID
        if not utils.supports_microversion(self, '3.67'):
            raise exceptions.SDKException(
                'List default types require at least microversion 3.67'
            )

        return self._list(_default_type.DefaultType)

    def show_default_type(self, project):
        """Show default type for a project.

        :param project: The value can be either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project` instance.

        :returns: Default type associated to the project.
        """
        # This is required since previously default types did not accept
        # URL with project ID
        if not utils.supports_microversion(self, '3.67'):
            raise exceptions.SDKException(
                'Show default type require at least microversion 3.67'
            )

        project_id = resource.Resource._get_id(project)
        return self._get(_default_type.DefaultType, project_id)

    def set_default_type(self, project, type):
        """Set default type for a project.

        :param project: The value can be either the ID of a project or a
             :class:`~openstack.identity.v3.project.Project` instance.
        :param type: The value can be either the ID of a type or a
             :class:`~openstack.block_storage.v3.type.Type` instance.

        :returns: Dictionary of project ID and it's associated default type.
        """
        # This is required since previously default types did not accept
        # URL with project ID
        if not utils.supports_microversion(self, '3.67'):
            raise exceptions.SDKException(
                'Set default type require at least microversion 3.67'
            )

        type_id = resource.Resource._get_id(type)
        project_id = resource.Resource._get_id(project)
        return self._create(
            _default_type.DefaultType,
            id=project_id,
            volume_type_id=type_id,
        )

    def unset_default_type(self, project):
        """Unset default type for a project.

        :param project: The value can be either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project` instance.

        :returns: ``None``
        """
        # This is required since previously default types did not accept
        # URL with project ID
        if not utils.supports_microversion(self, '3.67'):
            raise exceptions.SDKException(
                'Unset default type require at least microversion 3.67'
            )

        project_id = resource.Resource._get_id(project)
        self._delete(_default_type.DefaultType, project_id)

    # ====== VOLUMES ======
    def get_volume(self, volume):
        """Get a single volume

        :param volume: The value can be the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: One :class:`~openstack.block_storage.v3.volume.Volume`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_volume.Volume, volume)

    def find_volume(
        self,
        name_or_id,
        ignore_missing=True,
        *,
        details=True,
        all_projects=False,
    ):
        """Find a single volume

        :param snapshot: The name or ID a volume
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume does not exist.
        :param bool details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
        :param bool all_projects: When set to ``True``, search for volume by
            name across all projects. Note that this will likely result in
            a higher chance of duplicates. Admin-only by default.

        :returns: One :class:`~openstack.block_storage.v3.volume.Volume`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        query = {}
        if all_projects:
            query['all_projects'] = True
        list_base_path = '/volumes/detail' if details else None
        return self._find(
            _volume.Volume,
            name_or_id,
            ignore_missing=ignore_missing,
            list_base_path=list_base_path,
            **query,
        )

    def volumes(self, *, details=True, all_projects=False, **query):
        """Retrieve a generator of volumes

        :param bool details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
        :param bool all_projects: When set to ``True``, list volumes from all
            projects. Admin-only by default.
        :param kwargs query: Optional query parameters to be sent to limit
            the volumes being returned.  Available parameters include:

            * name: Name of the volume as a string.
            * status: Value of the status of the volume so that you can filter
              on "available" for example.

        :returns: A generator of volume objects.
        """
        if all_projects:
            query['all_projects'] = True
        base_path = '/volumes/detail' if details else None
        return self._list(_volume.Volume, base_path=base_path, **query)

    def create_volume(self, **attrs):
        """Create a new volume from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.volume.Volume`,
            comprised of the properties on the Volume class.

        :returns: The results of volume creation
        :rtype: :class:`~openstack.block_storage.v3.volume.Volume`
        """
        return self._create(_volume.Volume, **attrs)

    def delete_volume(
        self, volume, ignore_missing=True, *, force=False, cascade=False
    ):
        """Delete a volume

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the volume does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent volume.
        :param bool force: Whether to try forcing volume deletion.
        :param bool cascade: Whether to remove any snapshots along with the
            volume.

        :returns: ``None``
        """
        volume = self._get_resource(_volume.Volume, volume)

        params = {'cascade': cascade}
        if utils.supports_microversion(self, '3.23'):
            params['force'] = force

        try:
            if force and not utils.supports_microversion(self, '3.23'):
                volume.force_delete(self)
            else:
                volume.delete(self, params=params)
        except exceptions.NotFoundException:
            if ignore_missing:
                return None
            raise

    def update_volume(self, volume, **attrs):
        """Update a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param dict attrs: The attributes to update on the volume.

        :returns: The updated volume
        :rtype: :class:`~openstack.block_storage.v3.volume.Volume`
        """
        return self._update(_volume.Volume, volume, **attrs)

    def get_volume_metadata(self, volume):
        """Return a dictionary of metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume`.

        :returns: A :class:`~openstack.block_storage.v3.volume.Volume` with the
            volume's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v3.volume.Volume`
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.fetch_metadata(self)

    def set_volume_metadata(self, volume, **metadata):
        """Update metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume`.
        :param kwargs metadata: Key/value pairs to be updated in the volume's
            metadata. No other metadata is modified by this call. All keys
            and values are stored as Unicode.

        :returns: A :class:`~openstack.block_storage.v3.volume.Volume` with the
            volume's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v3.volume.Volume`
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.set_metadata(self, metadata=metadata)

    def delete_volume_metadata(self, volume, keys=None):
        """Delete metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume`.
        :param list keys: The keys to delete. If left empty complete
            metadata will be removed.

        :rtype: ``None``
        """
        volume = self._get_resource(_volume.Volume, volume)
        if keys is not None:
            for key in keys:
                volume.delete_metadata_item(self, key)
        else:
            volume.delete_metadata(self)

    def summary(self, all_projects, **kwargs):
        """Get Volumes Summary

        This method returns the volumes summary in the deployment.

        :param all_projects: Whether to return the summary of all projects
            or not.

        :returns: One :class:
            `~openstack.block_storage.v3.block_storage_summary.Summary`
            instance.
        """
        res = self._get(_summary.BlockStorageSummary, requires_id=False)
        return res.fetch(
            self,
            requires_id=False,
            resource_response_key='volume-summary',
            all_tenants=all_projects,
            **kwargs,
        )

    # ====== VOLUME ACTIONS ======
    def extend_volume(self, volume, size):
        """Extend a volume

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param size: New volume size

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.extend(self, size)

    def complete_volume_extend(self, volume, error=False):
        """Complete a volume extend operation.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param bool error: Used to indicate if an error has occured that
            requires Cinder to roll back the extend operation.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.complete_extend(self, error)

    def set_volume_readonly(self, volume, readonly=True):
        """Set a volume's read-only flag.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param bool readonly: Whether the volume should be a read-only volume
            or not.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.set_readonly(self, readonly)

    def retype_volume(self, volume, new_type, migration_policy="never"):
        """Retype the volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param new_type: The new volume type that volume is changed with.
            The value can be either the ID of the volume type or a
            :class:`~openstack.block_storage.v3.type.Type` instance.
        :param str migration_policy: Specify if the volume should be migrated
            when it is re-typed. Possible values are on-demand or never.
            Default: never.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        type_id = resource.Resource._get_id(new_type)
        volume.retype(self, type_id, migration_policy)

    def set_volume_bootable_status(self, volume, bootable):
        """Set bootable status of the volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param bool bootable: Specifies whether the volume should be bootable
            or not.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.set_bootable_status(self, bootable)

    def set_volume_image_metadata(self, volume, **metadata):
        """Update image metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume`.
        :param kwargs metadata: Key/value pairs to be updated in the volume's
            image metadata. No other metadata is modified by this call.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.set_image_metadata(self, metadata=metadata)

    def delete_volume_image_metadata(self, volume, keys=None):
        """Delete metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume`.
        :param list keys: The keys to delete. If left empty complete
            metadata will be removed.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        if keys is not None:
            for key in keys:
                volume.delete_image_metadata_item(self, key)
        else:
            volume.delete_image_metadata(self)

    def reset_volume_status(
        self, volume, status=None, attach_status=None, migration_status=None
    ):
        """Reset volume statuses.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str status: The new volume status.
        :param str attach_status: The new volume attach status.
        :param str migration_status: The new volume migration status (admin
            only).

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.reset_status(self, status, attach_status, migration_status)

    def revert_volume_to_snapshot(self, volume, snapshot):
        """Revert a volume to its latest snapshot.

        This method only support reverting a detached volume, and the
        volume status must be available.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param snapshot:  The value can be either the ID of a snapshot or a
            :class:`~openstack.block_storage.v3.snapshot.Snapshot` instance.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        volume.revert_to_snapshot(self, snapshot.id)

    def attach_volume(self, volume, mountpoint, instance=None, host_name=None):
        """Attaches a volume to a server.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str mountpoint: The attaching mount point.
        :param str instance: The UUID of the attaching instance.
        :param str host_name: The name of the attaching host.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.attach(self, mountpoint, instance, host_name)

    def detach_volume(self, volume, attachment, force=False, connector=None):
        """Detaches a volume from a server.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str attachment: The ID of the attachment.
        :param bool force: Whether to force volume detach (Rolls back an
            unsuccessful detach operation after you disconnect the volume.)
        :param dict connector: The connector object.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.detach(self, attachment, force, connector)

    def manage_volume(self, **attrs):
        """Creates a volume by using existing storage rather than
            allocating new storage.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.volume.Volume`,
            comprised of the properties on the Volume class.
        :returns: The results of volume creation
        :rtype: :class:`~openstack.block_storage.v3.volume.Volume`
        """
        return _volume.Volume.manage(self, **attrs)

    def unmanage_volume(self, volume):
        """Removes a volume from Block Storage management without removing the
            back-end storage object that is associated with it.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.unmanage(self)

    def migrate_volume(
        self,
        volume,
        host=None,
        force_host_copy=False,
        lock_volume=False,
        cluster=None,
    ):
        """Migrates a volume to the specified host.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str host: The target host for the volume migration. Host
            format is host@backend.
        :param bool force_host_copy: If false (the default), rely on the volume
            backend driver to perform the migration, which might be optimized.
            If true, or the volume driver fails to migrate the volume itself,
            a generic host-based migration is performed.
        :param bool lock_volume: If true, migrating an available volume will
            change its status to maintenance preventing other operations from
            being performed on the volume such as attach, detach, retype, etc.
        :param str cluster: The target cluster for the volume migration.
            Cluster format is cluster@backend. Starting with microversion
            3.16, either cluster or host must be specified. If host is
            specified and is part of a cluster, the cluster is used as the
            target for the migration.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.migrate(self, host, force_host_copy, lock_volume, cluster)

    def complete_volume_migration(self, volume, new_volume, error=False):
        """Complete the migration of a volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str new_volume: The UUID of the new volume.
        :param bool error: Used to indicate if an error has occured elsewhere
            that requires clean up.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.complete_migration(self, new_volume, error)

    def upload_volume_to_image(
        self,
        volume,
        image_name,
        force=False,
        disk_format=None,
        container_format=None,
        visibility=None,
        protected=None,
    ):
        """Uploads the specified volume to image service.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param str image name: The name for the new image.
        :param bool force: Enables or disables upload of a volume that is
            attached to an instance.
        :param str disk_format: Disk format for the new image.
        :param str container_format: Container format for the new image.
        :param str visibility: The visibility property of the new image.
        :param str protected: Whether the new image is protected.

        :returns: dictionary describing the image.
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.upload_to_image(
            self,
            image_name,
            force=force,
            disk_format=disk_format,
            container_format=container_format,
            visibility=visibility,
            protected=protected,
        )

    def reserve_volume(self, volume):
        """Mark volume as reserved.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None"""
        volume = self._get_resource(_volume.Volume, volume)
        volume.reserve(self)

    def unreserve_volume(self, volume):
        """Unmark volume as reserved.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None"""
        volume = self._get_resource(_volume.Volume, volume)
        volume.unreserve(self)

    def begin_volume_detaching(self, volume):
        """Update volume status to 'detaching'.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None"""
        volume = self._get_resource(_volume.Volume, volume)
        volume.begin_detaching(self)

    def abort_volume_detaching(self, volume):
        """Update volume status to 'in-use'.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.

        :returns: None"""
        volume = self._get_resource(_volume.Volume, volume)
        volume.abort_detaching(self)

    def init_volume_attachment(self, volume, connector):
        """Initialize volume attachment.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param dict connector: The connector object.

        :returns: Dictionary containing the modified connector object"""
        volume = self._get_resource(_volume.Volume, volume)
        return volume.init_attachment(self, connector)

    def terminate_volume_attachment(self, volume, connector):
        """Update volume status to 'in-use'.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param dict connector: The connector object.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.terminate_attachment(self, connector)

    # ====== ATTACHMENTS ======

    def create_attachment(self, volume, **attrs):
        """Create a new attachment

        This is an internal API and should only be called by services
        consuming volume attachments like nova, glance, ironic etc.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.attachment.Attachment`
            comprised of the properties on the Attachment class like
            connector, instance_id, mode etc.
        :returns: The results of attachment creation
        :rtype: :class:`~openstack.block_storage.v3.attachment.Attachment`
        """
        volume_id = resource.Resource._get_id(volume)
        return self._create(
            _attachment.Attachment, volume_id=volume_id, **attrs
        )

    def get_attachment(self, attachment):
        """Get a single volume

        This is an internal API and should only be called by services
        consuming volume attachments like nova, glance, ironic etc.

        :param attachment: The value can be the ID of an attachment or a
            :class:`~attachment.Attachment` instance.

        :returns: One :class:`~attachment.Attachment`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_attachment.Attachment, attachment)

    def attachments(self, **query):
        """Returns a generator of attachments.

        This is an internal API and should only be called by services
        consuming volume attachments like nova, glance, ironic etc.

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of attachment objects.
        """
        return self._list(_attachment.Attachment, **query)

    def delete_attachment(self, attachment, ignore_missing=True):
        """Delete an attachment

        This is an internal API and should only be called by services
        consuming volume attachments like nova, glance, ironic etc.

        :param type: The value can be either the ID of a attachment or a
            :class:`~openstack.block_storage.v3.attachment.Attachment`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the attachment does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent attachment.

        :returns: ``None``
        """
        self._delete(
            _attachment.Attachment,
            attachment,
            ignore_missing=ignore_missing,
        )

    def update_attachment(self, attachment, **attrs):
        """Update an attachment

        This is an internal API and should only be called by services
        consuming volume attachments like nova, glance, ironic etc.

        :param attachment: The value can be the ID of an attachment or a
            :class:`~openstack.block_storage.v3.attachment.Attachment`
            instance.
        :param dict attrs: Keyword arguments which will be used to update
            a :class:`~openstack.block_storage.v3.attachment.Attachment`
            comprised of the properties on the Attachment class

        :returns: The updated attachment
        :rtype: :class:`~openstack.volume.v3.attachment.Attachment`
        """
        return self._update(_attachment.Attachment, attachment, **attrs)

    def complete_attachment(self, attachment):
        """Complete an attachment

        This is an internal API and should only be called by services
        consuming volume attachments like nova, glance, ironic etc.

        :param attachment: The value can be the ID of an attachment or a
            :class:`~openstack.block_storage.v3.attachment.Attachment`
            instance.

        :returns: ``None``
        :rtype: :class:`~openstack.volume.v3.attachment.Attachment`
        """
        attachment_obj = self._get_resource(_attachment.Attachment, attachment)
        return attachment_obj.complete(self)

    # ====== BACKEND POOLS ======
    def backend_pools(self, **query):
        """Returns a generator of cinder Back-end storage pools

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns A generator of cinder Back-end storage pools objects
        """
        return self._list(_stats.Pools, **query)

    # ====== BACKUPS ======
    def backups(self, *, details=True, **query):
        """Retrieve a generator of backups

        :param bool details: When set to ``False``
            no additional details will be returned. The default, ``True``,
            will cause objects with additional attributes to be returned.
        :param dict query: Optional query parameters to be sent to limit the
            resources being returned:

            * offset: pagination marker
            * limit: pagination limit
            * sort_key: Sorts by an attribute. A valid value is
              name, status, container_format, disk_format, size, id,
              created_at, or updated_at. Default is created_at.
              The API uses the natural sorting direction of the
              sort_key attribute value.
            * sort_dir: Sorts by one or more sets of attribute and sort
              direction combinations. If you omit the sort direction
              in a set, default is desc.
            * project_id: Project ID to query backups for.

        :returns: A generator of backup objects.
        """
        base_path = '/backups/detail' if details else None
        return self._list(_backup.Backup, base_path=base_path, **query)

    def get_backup(self, backup):
        """Get a backup

        :param backup: The value can be the ID of a backup
            or a :class:`~openstack.block_storage.v3.backup.Backup`
            instance.

        :returns: Backup instance
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        return self._get(_backup.Backup, backup)

    def find_backup(self, name_or_id, ignore_missing=True, *, details=True):
        """Find a single backup

        :param snapshot: The name or ID a backup
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the backup does not exist.
        :param bool details: When set to ``False`` no additional details will
            be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.

        :returns: One :class:`~openstack.block_storage.v3.backup.Backup`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        list_base_path = '/backups/detail' if details else None
        return self._find(
            _backup.Backup,
            name_or_id,
            ignore_missing=ignore_missing,
            list_base_path=list_base_path,
        )

    def create_backup(self, **attrs):
        """Create a new Backup from attributes with native API

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.backup.Backup`
            comprised of the properties on the Backup class.

        :returns: The results of Backup creation
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        return self._create(_backup.Backup, **attrs)

    def delete_backup(self, backup, ignore_missing=True, force=False):
        """Delete a CloudBackup

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup` instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.
        :param bool force: Whether to try forcing backup deletion

        :returns: ``None``
        """
        if not force:
            self._delete(_backup.Backup, backup, ignore_missing=ignore_missing)
        else:
            backup = self._get_resource(_backup.Backup, backup)
            backup.force_delete(self)

    def update_backup(self, backup, **attrs):
        """Update a backup

        :param backup: Either the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup`.
        :param dict attrs: The attributes to update on the volume.

        :returns: The updated backup
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        return self._update(_backup.Backup, backup, **attrs)

    def get_backup_metadata(self, backup):
        """Return a dictionary of metadata for a backup

        :param backup: Either the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup`.

        :returns: A :class:`~openstack.block_storage.v3.backup.Backup` with the
            backup's metadata.
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        backup = self._get_resource(_backup.Backup, backup)
        return backup.fetch_metadata(self)

    def set_backup_metadata(self, backup, **metadata):
        """Update metadata for a backup

        :param backup: Either the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup`.
        :param metadata: Key/value pairs to be updated in the backup's
            metadata. No other metadata is modified by this call.

        :returns: A :class:`~openstack.block_storage.v3.backup.Backup` with the
            backup's metadata.
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        backup = self._get_resource(_backup.Backup, backup)
        return backup.set_metadata(self, metadata=metadata)

    def delete_backup_metadata(self, backup, keys=None):
        """Delete metadata for a backup

        :param backup: Either the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup`.
        :param list keys: The keys to delete. If left empty complete
            metadata will be removed.

        :rtype: ``None``
        """
        backup = self._get_resource(_backup.Backup, backup)
        if keys is not None:
            for key in keys:
                backup.delete_metadata_item(self, key)
        else:
            backup.delete_metadata(self)

    # ====== BACKUP ACTIONS ======
    def restore_backup(self, backup, volume_id=None, name=None):
        """Restore a Backup to volume

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup` instance
        :param volume_id: The ID of the volume to restore the backup to.
        :param name: The name for new volume creation to restore.

        :returns: Updated backup instance
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        backup = self._get_resource(_backup.Backup, backup)
        return backup.restore(self, volume_id=volume_id, name=name)

    def reset_backup_status(self, backup, status):
        """Reset status of the backup

        :param backup: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup` instance.
        :param str status: New backup status

        :returns: None
        """
        backup = self._get_resource(_backup.Backup, backup)
        backup.reset_status(self, status)

    def reset_backup(self, backup, status):
        warnings.warn(
            "reset_backup is a deprecated alias for reset_backup_status "
            "and will be removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        return self.reset_backup_status(backup, status)

    # ====== LIMITS ======
    def get_limits(self, project=None):
        """Retrieves limits

        :param project: A project to get limits for. The value can be either
            the ID of a project or an
            :class:`~openstack.identity.v3.project.Project` instance.
        :returns: A Limits object, including both
            :class:`~openstack.block_storage.v3.limits.AbsoluteLimit` and
            :class:`~openstack.block_storage.v3.limits.RateLimit`
        :rtype: :class:`~openstack.block_storage.v3.limits.Limits`
        """
        project_id = None
        if project:
            project_id = resource.Resource._get_id(project)

        # we don't use Proxy._get since that doesn't allow passing arbitrary
        # query string parameters
        res = self._get_resource(_limits.Limits, None)
        return res.fetch(
            self,
            requires_id=False,
            project_id=project_id,
        )

    # ====== CAPABILITIES ======
    def get_capabilities(self, host):
        """Get a backend's capabilites

        :param host: Specified backend to obtain volume stats and properties.

        :returns: One :class:
            `~openstack.block_storage.v3.capabilites.Capabilities` instance.
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(_capabilities.Capabilities, host)

    # ====== GROUPS ======
    def get_group(self, group_id, **attrs):
        """Get a group

        :param group_id: The ID of the group to get.
        :param dict attrs:  Optional query parameters to be sent to limit the
            resources being returned.

        :returns: A Group instance.
        :rtype: :class:`~openstack.block_storage.v3.group`
        """
        return self._get(_group.Group, group_id, **attrs)

    def find_group(self, name_or_id, ignore_missing=True, *, details=True):
        """Find a single group

        :param name_or_id: The name or ID of a group.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the group snapshot does not exist.
        :param bool details: When set to ``False``, no additional details will
            be returned. The default, ``True``, will cause additional details
            to be returned.

        :returns: One :class:`~openstack.block_storage.v3.group.Group`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        list_base_path = '/groups/detail' if details else None
        return self._find(
            _group.Group,
            name_or_id,
            ignore_missing=ignore_missing,
            list_base_path=list_base_path,
        )

    def groups(self, *, details=True, **query):
        """Retrieve a generator of groups

        :param bool details: When set to ``False``, no additional details will
            be returned. The default, ``True``, will cause additional details
            to be returned.
        :param dict query: Optional query parameters to be sent to limit the
            resources being returned:

            * all_tenants: Shows details for all project.
            * sort: Comma-separated list of sort keys and optional sort
              directions.
            * limit: Returns a number of items up to the limit value.
            * offset: Used in conjunction with limit to return a slice of
              items. Specifies where to start in the list.
            * marker: The ID of the last-seen item.
            * list_volume: Show volume ids in this group.
            * detailed: If True, will list groups with details.
            * search_opts: Search options.

        :returns: A generator of group objects.
        """
        base_path = '/groups/detail' if details else '/groups'
        return self._list(_group.Group, base_path=base_path, **query)

    def create_group(self, **attrs):
        """Create a new group from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.group.Group` comprised of
            the properties on the Group class.

        :returns: The results of group creation.
        :rtype: :class:`~openstack.block_storage.v3.group.Group`.
        """
        return self._create(_group.Group, **attrs)

    def create_group_from_source(self, **attrs):
        """Creates a new group from source

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.group.Group` comprised of
            the properties on the Group class.

        :returns: The results of group creation.
        :rtype: :class:`~openstack.block_storage.v3.group.Group`.
        """
        return _group.Group.create_from_source(self, **attrs)

    def reset_group_status(self, group, status):
        """Reset group status

        :param group: The :class:`~openstack.block_storage.v3.group.Group`
            to set the state.
        :param status: The status for a group.

        :returns: ``None``
        """
        res = self._get_resource(_group.Group, group)
        return res.reset_status(self, status)

    def reset_group_state(self, group, status):
        warnings.warn(
            "reset_group_state is a deprecated alias for reset_group_status "
            "and will be removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        return self.reset_group_status(group, status)

    def delete_group(self, group, delete_volumes=False):
        """Delete a group

        :param group: The :class:`~openstack.block_storage.v3.group.Group` to
            delete.
        :param bool delete_volumes: When set to ``True``, volumes in group
            will be deleted.

        :returns: ``None``.
        """
        res = self._get_resource(_group.Group, group)
        res.delete(self, delete_volumes=delete_volumes)

    def update_group(self, group, **attrs):
        """Update a group

        :param group: The value can be the ID of a group or a
            :class:`~openstack.block_storage.v3.group.Group` instance.
        :param dict attrs: The attributes to update on the group.

        :returns: The updated group
        :rtype: :class:`~openstack.volume.v3.group.Group`
        """
        return self._update(_group.Group, group, **attrs)

    # ====== AVAILABILITY ZONES ======
    def availability_zones(self):
        """Return a generator of availability zones

        :returns: A generator of availability zone
        :rtype:
            :class:`~openstack.block_storage.v3.availability_zone.AvailabilityZone`
        """

        return self._list(availability_zone.AvailabilityZone)

    # ====== GROUP SNAPSHOT ======
    def get_group_snapshot(self, group_snapshot_id):
        """Get a group snapshot

        :param group_snapshot_id: The ID of the group snapshot to get.

        :returns: A GroupSnapshot instance.
        :rtype: :class:`~openstack.block_storage.v3.group_snapshot`
        """
        return self._get(_group_snapshot.GroupSnapshot, group_snapshot_id)

    def find_group_snapshot(
        self,
        name_or_id,
        ignore_missing=True,
        *,
        details=True,
    ):
        """Find a single group snapshot

        :param name_or_id: The name or ID of a group snapshot.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the group snapshot does not exist.
        :param bool details: When set to ``False``, no additional details will
            be returned. The default, ``True``, will cause additional details
            to be returned.

        :returns: One :class:`~openstack.block_storage.v3.group_snapshot`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        list_base_path = '/group_snapshots/detail' if details else None
        return self._find(
            _group_snapshot.GroupSnapshot,
            name_or_id,
            ignore_missing=ignore_missing,
            list_base_path=list_base_path,
        )

    def group_snapshots(self, *, details=True, **query):
        """Retrieve a generator of group snapshots

        :param bool details: When ``True``, returns
            :class:`~openstack.block_storage.v3.group_snapshot.GroupSnapshot`
            objects with additional attributes filled.
        :param kwargs query: Optional query parameters to be sent to limit
            the group snapshots being returned.
        :returns: A generator of group snapshtos.
        """
        base_path = '/group_snapshots/detail' if details else None
        return self._list(
            _group_snapshot.GroupSnapshot,
            base_path=base_path,
            **query,
        )

    def create_group_snapshot(self, **attrs):
        """Create a group snapshot

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.block_storage.v3.group_snapshot.GroupSnapshot`
            comprised of the properties on the GroupSnapshot class.

        :returns: The results of group snapshot creation.
        :rtype: :class:`~openstack.block_storage.v3.group_snapshot`.
        """
        return self._create(_group_snapshot.GroupSnapshot, **attrs)

    def reset_group_snapshot_status(self, group_snapshot, status):
        """Reset group snapshot status

        :param group_snapshot: The
            :class:`~openstack.block_storage.v3.group_snapshot.GroupSnapshot`
            to set the state.
        :param state: The status of the group snapshot to be set.

        :returns: None
        """
        resource = self._get_resource(
            _group_snapshot.GroupSnapshot, group_snapshot
        )
        resource.reset_state(self, status)

    def reset_group_snapshot_state(self, group_snapshot, state):
        warnings.warn(
            "reset_group_snapshot_state is a deprecated alias for "
            "reset_group_snapshot_status and will be removed in a future "
            "release.",
            os_warnings.RemovedInSDK60Warning,
        )
        return self.reset_group_snapshot_status(group_snapshot, state)

    def delete_group_snapshot(self, group_snapshot, ignore_missing=True):
        """Delete a group snapshot

        :param group_snapshot: The :class:`~openstack.block_storage.v3.
            group_snapshot.GroupSnapshot` to delete.

        :returns: None
        """
        self._delete(
            _group_snapshot.GroupSnapshot,
            group_snapshot,
            ignore_missing=ignore_missing,
        )

    # ====== GROUP TYPE ======
    def get_group_type(self, group_type):
        """Get a specific group type

        :param group_type: The value can be the ID of a group type
            or a :class:`~openstack.block_storage.v3.group_type.GroupType`
            instance.

        :returns: One :class:
            `~openstack.block_storage.v3.group_type.GroupType` instance.
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(_group_type.GroupType, group_type)

    def find_group_type(self, name_or_id, ignore_missing=True):
        """Find a single group type

        :param name_or_id: The name or ID of a group type.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the group type does not exist.

        :returns: One
            :class:`~openstack.block_storage.v3.group_type.GroupType`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        return self._find(
            _group_type.GroupType,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def group_types(self, **query):
        """Retrive a generator of group types

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned:

            * sort: Comma-separated list of sort keys and optional sort
              directions in the form of <key> [:<direction>]. A valid
              direction is asc (ascending) or desc (descending).
            * limit: Requests a page size of items. Returns a number of items
              up to a limit value. Use the limit parameter to make an
              initial limited request and use the ID of the last-seen item
              from the response as the marker parameter value in a
              subsequent limited request.
            * offset: Used in conjunction with limit to return a slice of
              items. Is where to start in the list.
            * marker: The ID of the last-seen item.

        :returns: A generator of group type objects.
        """
        return self._list(_group_type.GroupType, **query)

    def create_group_type(self, **attrs):
        """Create a group type

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.group_type.GroupType`
            comprised of the properties on the GroupType class.

        :returns: The results of group type creation.
        :rtype: :class:`~openstack.block_storage.v3.group_type.GroupTye`.
        """
        return self._create(_group_type.GroupType, **attrs)

    def delete_group_type(self, group_type, ignore_missing=True):
        """Delete a group type

        :param group_type: The value can be the ID of a group type
            or a :class:`~openstack.block_storage.v3.group_type.GroupType`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: None
        """
        self._delete(
            _group_type.GroupType, group_type, ignore_missing=ignore_missing
        )

    def update_group_type(self, group_type, **attrs):
        """Update a group_type

        :param group_type: The value can be the ID of a group type or a
            :class:`~openstack.block_storage.v3.group_type.GroupType`
            instance.
        :param dict attrs: The attributes to update on the group type.

        :returns: The updated group type.
        :rtype: :class:`~openstack.block_storage.v3.group_type.GroupType`
        """
        return self._update(_group_type.GroupType, group_type, **attrs)

    def fetch_group_type_group_specs(self, group_type):
        """Lists group specs of a group type.

        :param group_type: Either the ID of a group type or a
            :class:`~openstack.block_storage.v3.group_type.GroupType` instance.

        :returns: One :class:`~openstack.block_storage.v3.group_type.GroupType`
        """
        group_type = self._get_resource(_group_type.GroupType, group_type)
        return group_type.fetch_group_specs(self)

    def create_group_type_group_specs(self, group_type, group_specs):
        """Create group specs for a group type.

        :param group_type: Either the ID of a group type or a
            :class:`~openstack.block_storage.v3.group_type.GroupType` instance.
        :param dict group_specs: dict of extra specs

        :returns: One :class:`~openstack.block_storage.v3.group_type.GroupType`
        """
        group_type = self._get_resource(_group_type.GroupType, group_type)
        return group_type.create_group_specs(self, specs=group_specs)

    def get_group_type_group_specs_property(self, group_type, prop):
        """Retrieve a group spec property for a group type.

        :param group_type: Either the ID of a group type or a
            :class:`~openstack.block_storage.v3.group_type.GroupType` instance.
        :param str prop: Property name.

        :returns: String value of the requested property.
        """
        group_type = self._get_resource(_group_type.GroupType, group_type)
        return group_type.get_group_specs_property(self, prop)

    def update_group_type_group_specs_property(self, group_type, prop, val):
        """Update a group spec property for a group type.

        :param group_type: Either the ID of a group type or a
            :class:`~openstack.block_storage.v3.group_type.GroupType` instance.
        :param str prop: Property name.
        :param str val: Property value.

        :returns: String value of the requested property.
        """
        group_type = self._get_resource(_group_type.GroupType, group_type)
        return group_type.update_group_specs_property(self, prop, val)

    def delete_group_type_group_specs_property(self, group_type, prop):
        """Delete a group spec property from a group type.

        :param group_type: Either the ID of a group type or a
            :class:`~openstack.block_storage.v3.group_type.GroupType` instance.
        :param str prop: Property name.

        :returns: None
        """
        group_type = self._get_resource(_group_type.GroupType, group_type)
        return group_type.delete_group_specs_property(self, prop)

    # ====== QUOTA CLASS SETS ======

    def get_quota_class_set(self, quota_class_set='default'):
        """Get a single quota class set

        Only one quota class is permitted, ``default``.

        :param quota_class_set: The value can be the ID of a quota class set
            (only ``default`` is supported) or a
            :class:`~openstack.block_storage.v3.quota_class_set.QuotaClassSet`
            instance.

        :returns: One
            :class:`~openstack.block_storage.v3.quota_class_set.QuotaClassSet`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_quota_class_set.QuotaClassSet, quota_class_set)

    def update_quota_class_set(self, quota_class_set, **attrs):
        """Update a QuotaClassSet.

        Only one quota class is permitted, ``default``.

        :param quota_class_set: Either the ID of a quota class set (only
            ``default`` is supported) or a
        :param attrs: The attributes to update on the QuotaClassSet represented
            by ``quota_class_set``.

        :returns: The updated QuotaSet
        :rtype: :class:`~openstack.block_storage.v3.quota_set.QuotaSet`
        """
        return self._update(
            _quota_class_set.QuotaClassSet, quota_class_set, **attrs
        )

    # ====== QUOTA SETS ======

    def get_quota_set(self, project, usage=False, **query):
        """Show QuotaSet information for the project

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be retrieved
        :param bool usage: When set to ``True`` quota usage and reservations
            would be filled.
        :param dict query: Additional query parameters to use.

        :returns: One :class:`~openstack.block_storage.v3.quota_set.QuotaSet`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        project = self._get_resource(_project.Project, project)
        res = self._get_resource(
            _quota_set.QuotaSet, None, project_id=project.id
        )
        return res.fetch(self, usage=usage, **query)

    def get_quota_set_defaults(self, project):
        """Show QuotaSet defaults for the project

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be retrieved

        :returns: One :class:`~openstack.block_storage.v3.quota_set.QuotaSet`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        project = self._get_resource(_project.Project, project)
        res = self._get_resource(
            _quota_set.QuotaSet, None, project_id=project.id
        )
        return res.fetch(self, base_path='/os-quota-sets/defaults')

    def revert_quota_set(self, project, **query):
        """Reset Quota for the project/user.

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be resetted.
        :param dict query: Additional parameters to be used.

        :returns: ``None``
        """
        project = self._get_resource(_project.Project, project)
        res = self._get_resource(
            _quota_set.QuotaSet, None, project_id=project.id
        )

        return res.delete(self, **query)

    def update_quota_set(self, project, **attrs):
        """Update a QuotaSet.

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be reset.
        :param attrs: The attributes to update on the QuotaSet represented
            by ``quota_set``.

        :returns: The updated QuotaSet
        :rtype: :class:`~openstack.block_storage.v3.quota_set.QuotaSet`
        """
        if 'project_id' in attrs or isinstance(project, _quota_set.QuotaSet):
            warnings.warn(
                "The signature of 'update_quota_set' has changed and it "
                "now expects a Project as the first argument, in line "
                "with the other quota set methods.",
                os_warnings.RemovedInSDK50Warning,
            )
            # cinder doesn't support any query parameters so we simply pop
            # these
            if 'query' in attrs:
                warnings.warn(
                    "The query argument is no longer supported and should "
                    "be removed.",
                    os_warnings.RemovedInSDK50Warning,
                )
                attrs.pop('query')

            res = self._get_resource(_quota_set.QuotaSet, project, **attrs)
            return res.commit(self)
        else:
            project = self._get_resource(_project.Project, project)
            attrs['project_id'] = project.id
            return self._update(_quota_set.QuotaSet, None, **attrs)

    # ====== SERVICES ======
    @ty.overload
    def find_service(
        self,
        name_or_id: str,
        ignore_missing: ty.Literal[True] = True,
        **query: ty.Any,
    ) -> ty.Optional[_service.Service]: ...

    @ty.overload
    def find_service(
        self,
        name_or_id: str,
        ignore_missing: ty.Literal[False],
        **query: ty.Any,
    ) -> _service.Service: ...

    # excuse the duplication here: it's mypy's fault
    # https://github.com/python/mypy/issues/14764
    @ty.overload
    def find_service(
        self,
        name_or_id: str,
        ignore_missing: bool,
        **query: ty.Any,
    ) -> ty.Optional[_service.Service]: ...

    def find_service(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        **query: ty.Any,
    ) -> ty.Optional[_service.Service]:
        """Find a single service

        :param name_or_id: The name or ID of a service
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the resource does not exist.
            When set to ``True``, None will be returned when attempting to find
            a nonexistent resource.
        :param dict query: Additional attributes like 'host'

        :returns: One: class:`~openstack.block_storage.v3.service.Service` or None
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        return self._find(
            _service.Service,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def services(
        self,
        **query: ty.Any,
    ) -> ty.Generator[_service.Service, None, None]:
        """Return a generator of service

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of Service objects
        :rtype: class: `~openstack.block_storage.v3.service.Service`
        """
        return self._list(_service.Service, **query)

    def enable_service(
        self,
        service: ty.Union[str, _service.Service],
    ) -> _service.Service:
        """Enable a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v3.service.Service` instance.

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v3.service.Service`
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.enable(self)

    def disable_service(
        self,
        service: ty.Union[str, _service.Service],
        *,
        reason: ty.Optional[str] = None,
    ) -> _service.Service:
        """Disable a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v3.service.Service` instance
        :param str reason: The reason to disable a service

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v3.service.Service`
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.disable(self, reason=reason)

    def thaw_service(
        self,
        service: ty.Union[str, _service.Service],
    ) -> _service.Service:
        """Thaw a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v3.service.Service` instance

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v3.service.Service`
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.thaw(self)

    def freeze_service(
        self,
        service: ty.Union[str, _service.Service],
    ) -> _service.Service:
        """Freeze a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v3.service.Service` instance

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v3.service.Service`
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.freeze(self)

    def set_service_log_levels(
        self,
        *,
        level: _service.Level,
        binary: ty.Optional[_service.Binary] = None,
        server: ty.Optional[str] = None,
        prefix: ty.Optional[str] = None,
    ) -> None:
        """Set log level for services.

        :param level: The log level to set, case insensitive, accepted values
            are ``INFO``, ``WARNING``, ``ERROR`` and ``DEBUG``.
        :param binary: The binary name of the service.
        :param server: The name of the host.
        :param prefix: The prefix for the log path we are querying, for example
            ``cinder.`` or ``sqlalchemy.engine.`` When not present or the empty
            string is passed all log levels will be retrieved.
        :returns: None.
        """
        return _service.Service.set_log_levels(
            self, level=level, binary=binary, server=server, prefix=prefix
        )

    def get_service_log_levels(
        self,
        *,
        binary: ty.Optional[_service.Binary] = None,
        server: ty.Optional[str] = None,
        prefix: ty.Optional[str] = None,
    ) -> ty.Generator[_service.LogLevel, None, None]:
        """Get log level for services.

        :param binary: The binary name of the service.
        :param server: The name of the host.
        :param prefix: The prefix for the log path we are querying, for example
            ``cinder.`` or ``sqlalchemy.engine.`` When not present or the empty
            string is passed all log levels will be retrieved.
        :returns: A generator of
            :class:`~openstack.block_storage.v3.log_level.LogLevel` objects.
        """
        return _service.Service.get_log_levels(
            self, binary=binary, server=server, prefix=prefix
        )

    def failover_service(
        self,
        service: ty.Union[str, _service.Service],
        *,
        cluster: ty.Optional[str] = None,
        backend_id: ty.Optional[str] = None,
    ) -> _service.Service:
        """Failover a service

        Only applies to replicating cinder-volume services.

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v3.service.Service` instance

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v3.service.Service`
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.failover(
            self, cluster=cluster, backend_id=backend_id
        )

    # ====== RESOURCE FILTERS ======
    def resource_filters(self, **query):
        """Retrieve a generator of resource filters

        :returns: A generator of resource filters.
        """
        return self._list(_resource_filter.ResourceFilter, **query)

    # ====== EXTENSIONS ======
    def extensions(self):
        """Return a generator of extensions

        :returns: A generator of extension
        :rtype: :class:`~openstack.block_storage.v3.extension.Extension`
        """
        return self._list(_extension.Extension)

    # ===== TRANFERS =====

    def create_transfer(self, **attrs):
        """Create a new Transfer record

        :param volume_id: The value is ID of the volume.
        :param name: The value is name of the transfer
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.transfer.Transfer`
            comprised of the properties on the Transfer class.
        :returns: The results of Transfer creation
        :rtype: :class:`~openstack.block_storage.v3.transfer.Transfer`
        """
        return self._create(_transfer.Transfer, **attrs)

    def delete_transfer(self, transfer, ignore_missing=True):
        """Delete a volume transfer

        :param transfer: The value can be either the ID of a transfer or a
            :class:`~openstack.block_storage.v3.transfer.Transfer`` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the transfer does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent transfer.

        :returns: ``None``
        """
        self._delete(
            _transfer.Transfer,
            transfer,
            ignore_missing=ignore_missing,
        )

    def find_transfer(self, name_or_id, ignore_missing=True):
        """Find a single transfer

        :param name_or_id: The name or ID a transfer
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume transfer does not exist.

        :returns: One :class:`~openstack.block_storage.v3.transfer.Transfer`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        return self._find(
            _transfer.Transfer,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def get_transfer(self, transfer):
        """Get a single transfer

        :param transfer: The value can be the ID of a transfer or a
            :class:`~openstack.block_storage.v3.transfer.Transfer`
            instance.

        :returns: One :class:`~openstack.block_storage.v3.transfer.Transfer`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_transfer.Transfer, transfer)

    def transfers(self, *, details=True, all_projects=False, **query):
        """Retrieve a generator of transfers

        :param bool details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
        :param bool all_projects: When set to ``True``, list transfers from
            all projects. Admin-only by default.
        :param kwargs query: Optional query parameters to be sent to limit
            the transfers being returned.

        :returns: A generator of transfer objects.
        """
        if all_projects:
            query['all_projects'] = True
        base_path = '/volume-transfers'
        if not utils.supports_microversion(self, '3.55'):
            base_path = '/os-volume-transfer'
        if details:
            base_path = utils.urljoin(base_path, 'detail')
        return self._list(_transfer.Transfer, base_path=base_path, **query)

    def accept_transfer(self, transfer_id, auth_key):
        """Accept a Transfer

        :param transfer_id: The value can be the ID of a transfer or a
            :class:`~openstack.block_storage.v3.transfer.Transfer`
            instance.
        :param auth_key: The key to authenticate volume transfer.

        :returns: The results of Transfer creation
        :rtype: :class:`~openstack.block_storage.v3.transfer.Transfer`
        """
        transfer = self._get_resource(_transfer.Transfer, transfer_id)
        return transfer.accept(self, auth_key=auth_key)

    # ====== UTILS ======
    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str = 'available',
        failures: ty.Optional[list[str]] = None,
        interval: ty.Union[int, float, None] = 2,
        wait: ty.Optional[int] = None,
        attribute: str = 'status',
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :return: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        if failures is None:
            failures = ['error']

        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int = 2,
        wait: int = 120,
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)

    def _get_cleanup_dependencies(self):
        return {'block_storage': {'before': []}}

    def _service_cleanup(
        self,
        dry_run=True,
        client_status_queue=None,
        identified_resources=None,
        filters=None,
        resource_evaluation_fn=None,
        skip_resources=None,
    ):
        # It is not possible to delete backup if there are dependent backups.
        # In order to be able to do cleanup those is required to have multiple
        # iterations (first clean up backups with has no dependent backups, and
        # in next iterations there should be no backups with dependencies
        # remaining. Logically we can have also failures, therefore it is
        # required to limit amount of iterations we do (currently pick 10).  In
        # dry_run all those iterations are doing not what we want, therefore
        # only iterate in a real cleanup mode.
        if not self.should_skip_resource_cleanup("backup", skip_resources):
            if dry_run:
                # Just iterate and evaluate backups in dry_run mode
                for obj in self.backups(details=False):
                    need_delete = self._service_cleanup_del_res(
                        self.delete_backup,
                        obj,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=filters,
                        resource_evaluation_fn=resource_evaluation_fn,
                    )
            else:
                # Set initial iterations conditions
                need_backup_iteration = True
                max_iterations = 10
                while need_backup_iteration and max_iterations > 0:
                    # Reset iteration controls
                    need_backup_iteration = False
                    max_iterations -= 1
                    backups = []
                    # To increase success chance sort backups by age, dependent
                    # backups are logically younger.
                    for obj in self.backups(
                        details=True, sort_key='created_at', sort_dir='desc'
                    ):
                        if not obj.has_dependent_backups:
                            # If no dependent backups - go with it
                            need_delete = self._service_cleanup_del_res(
                                self.delete_backup,
                                obj,
                                dry_run=dry_run,
                                client_status_queue=client_status_queue,
                                identified_resources=identified_resources,
                                filters=filters,
                                resource_evaluation_fn=resource_evaluation_fn,
                            )
                            if not dry_run and need_delete:
                                backups.append(obj)
                        else:
                            # Otherwise we need another iteration
                            need_backup_iteration = True

                    # Before proceeding need to wait for backups to be deleted
                    for obj in backups:
                        try:
                            self.wait_for_delete(obj)
                        except exceptions.SDKException:
                            # Well, did our best, still try further
                            pass

        if not self.should_skip_resource_cleanup("snapshot", skip_resources):
            snapshots = []
            for obj in self.snapshots(details=False):
                need_delete = self._service_cleanup_del_res(
                    self.delete_snapshot,
                    obj,
                    dry_run=dry_run,
                    client_status_queue=client_status_queue,
                    identified_resources=identified_resources,
                    filters=filters,
                    resource_evaluation_fn=resource_evaluation_fn,
                )
                if not dry_run and need_delete:
                    snapshots.append(obj)

            # Before deleting volumes need to wait for snapshots to be deleted
            for obj in snapshots:
                try:
                    self.wait_for_delete(obj)
                except exceptions.SDKException:
                    # Well, did our best, still try further
                    pass

        if not self.should_skip_resource_cleanup("volume", skip_resources):
            for obj in self.volumes(details=True):
                self._service_cleanup_del_res(
                    self.delete_volume,
                    obj,
                    dry_run=dry_run,
                    client_status_queue=client_status_queue,
                    identified_resources=identified_resources,
                    filters=filters,
                    resource_evaluation_fn=resource_evaluation_fn,
                )
