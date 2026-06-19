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

from collections.abc import Callable, Generator, Iterable
from typing import Any, ClassVar, Literal, cast, overload
import warnings

from openstack._utils import renamed_param
from openstack.block_storage.v2 import backup as _backup
from openstack.block_storage.v2 import capabilities as _capabilities
from openstack.block_storage.v2 import consistency_group as _consistency_group
from openstack.block_storage.v2 import (
    consistency_group_snapshot as _consistency_group_snapshot,
)
from openstack.block_storage.v2 import extension as _extension
from openstack.block_storage.v2 import limits as _limits
from openstack.block_storage.v2 import qos_spec as _qos_spec
from openstack.block_storage.v2 import quota_class_set as _quota_class_set
from openstack.block_storage.v2 import quota_set as _quota_set
from openstack.block_storage.v2 import service as _service
from openstack.block_storage.v2 import snapshot as _snapshot
from openstack.block_storage.v2 import stats as _stats
from openstack.block_storage.v2 import transfer as _transfer
from openstack.block_storage.v2 import type as _type
from openstack.block_storage.v2 import volume as _volume
from openstack import exceptions
from openstack.identity.v3 import project as _project
from openstack.image.v2 import image as _image
from openstack import proxy
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings


class Proxy(proxy.Proxy):
    api_version: ClassVar[Literal['2']] = '2'

    # ========== Extensions ==========

    def extensions(self) -> Generator[_extension.Extension, None, None]:
        """Return a generator of extensions

        :returns: A generator of extension
        """
        return self._list(_extension.Extension)

    # ========== Images ==========

    # TODO(stephenfin): Deprecate the unused wait, timeout parameters
    def create_image(
        self,
        name: str,
        volume: str,
        allow_duplicates: bool,
        container_format: str | None,
        disk_format: str | None,
        wait: bool,
        timeout: int,
    ) -> _image.Image:
        if not disk_format:
            disk_format = self._connection.config.config['image_format']

        if not container_format:
            # https://docs.openstack.org/image-guide/image-formats.html
            container_format = 'bare'

        data = self._get_resource(_volume.Volume, volume).upload_to_image(
            self,
            name,
            force=allow_duplicates,
            disk_format=disk_format,
            container_format=container_format,
        )
        # we know we're realistically always working with image v2 nowadays
        return cast(
            _image.Image,
            self._connection.image._existing_image(id=data['image_id']),
        )

    # ========== Snapshots ==========

    def get_snapshot(
        self, snapshot: str | _snapshot.Snapshot
    ) -> _snapshot.Snapshot:
        """Get a single snapshot

        :param snapshot: The value can be the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`
            instance.

        :returns: One :class:`~openstack.block_storage.v2.snapshot.Snapshot`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_snapshot.Snapshot, snapshot)

    @overload
    def find_snapshot(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
        *,
        details: bool = True,
        all_projects: bool = False,
    ) -> _snapshot.Snapshot: ...

    @overload
    def find_snapshot(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
        all_projects: bool = False,
    ) -> _snapshot.Snapshot | None: ...

    def find_snapshot(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
        all_projects: bool = False,
    ) -> _snapshot.Snapshot | None:
        """Find a single snapshot

        :param snapshot: The name or ID a snapshot
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the snapshot does not exist. When set to ``True``, None will
            be returned when attempting to find a nonexistent resource.
        :param details: When set to ``False``, an
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` object will
            be returned. The default, ``True``, will cause an
            :class:`~openstack.block_storage.v2.snapshot.SnapshotDetail` object
            to be returned.
        :param all_projects: When set to ``True``, search for snapshot by
            name across all projects. Note that this will likely result in
            a higher chance of duplicates. Admin-only by default.

        :returns: One :class:`~openstack.block_storage.v2.snapshot.Snapshot`,
            one :class:`~openstack.block_storage.v2.snapshot.SnapshotDetail`
            object, or None.
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

    def snapshots(
        self,
        *,
        details: bool = True,
        all_projects: bool = False,
        **query: Any,
    ) -> Generator[_snapshot.Snapshot, None, None]:
        """Retrieve a generator of snapshots

        :param details: When set to ``False``
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`
            objects will be returned. The default, ``True``, will cause
            :class:`~openstack.block_storage.v2.snapshot.SnapshotDetail`
            objects to be returned.
        :param all_projects: When set to ``True``, list snapshots from all
            projects. Admin-only by default.
        :param query: Optional query parameters to be sent to limit
            the snapshots being returned.  Available parameters include:

            * name: Name of the snapshot as a string.
            * volume_id: volume id of a snapshot.
            * status: Value of the status of the snapshot so that you can
              filter on "available" for example.

        :returns: A generator of snapshot objects.
        """
        if all_projects:
            query['all_projects'] = True
        base_path = '/snapshots/detail' if details else None
        return self._list(_snapshot.Snapshot, base_path=base_path, **query)

    def create_snapshot(self, **attrs: Any) -> _snapshot.Snapshot:
        """Create a new snapshot from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.snapshot.Snapshot`,
            comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        """
        return self._create(_snapshot.Snapshot, **attrs)

    def update_snapshot(
        self, snapshot: str | _snapshot.Snapshot, **attrs: Any
    ) -> _snapshot.Snapshot:
        """Update a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` instance.
        :param attrs: The attributes to update on the snapshot.

        :returns: The updated snapshot
        """
        return self._update(_snapshot.Snapshot, snapshot, **attrs)

    def delete_snapshot(
        self,
        snapshot: str | _snapshot.Snapshot,
        ignore_missing: bool = True,
        force: bool = False,
    ) -> None:
        """Delete a snapshot

        :param snapshot: The value can be either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the snapshot does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent snapshot.
        :param force: Whether to try forcing snapshot deletion.

        :returns: ``None``
        """
        if not force:
            self._delete(
                _snapshot.Snapshot, snapshot, ignore_missing=ignore_missing
            )
        else:
            snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
            snapshot.force_delete(self)

    # ========== Snapshot actions ==========

    def reset_snapshot_status(
        self, snapshot: str | _snapshot.Snapshot, status: str
    ) -> None:
        """Reset status of the snapshot

        :param snapshot: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` instance.
        :param status: New snapshot status

        :returns: None
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        snapshot.reset_status(self, status)

    def reset_snapshot(
        self, snapshot: str | _snapshot.Snapshot, status: str
    ) -> None:
        warnings.warn(
            "reset_snapshot is a deprecated alias for reset_snapshot_status "
            "and will be removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        return self.reset_snapshot_status(snapshot, status)

    def manage_snapshot(self, **attrs: Any) -> _snapshot.Snapshot:
        """Creates a snapshot by using existing storage rather than
        allocating new storage.

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.snapshot.Snapshot`,
            comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        """
        return _snapshot.Snapshot.manage(self, **attrs)

    def unmanage_snapshot(self, snapshot: str | _snapshot.Snapshot) -> None:
        """Unmanage a snapshot from block storage provisioning.

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`.

        :returns: None
        """
        snapshot_obj = self._get_resource(_snapshot.Snapshot, snapshot)
        snapshot_obj.unmanage(self)

    # ========== Types ==========

    def get_type(self, type: str | _type.Type) -> _type.Type:
        """Get a single type

        :param type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.

        :returns: One :class:`~openstack.block_storage.v2.type.Type`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_type.Type, type)

    @overload
    def find_type(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
    ) -> _type.Type: ...

    @overload
    def find_type(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _type.Type | None: ...

    def find_type(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _type.Type | None:
        """Find a single volume type

        :param snapshot: The name or ID a volume type
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the volume type does not exist.

        :returns: One :class:`~openstack.block_storage.v2.type.Type`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        return self._find(
            _type.Type,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def types(self, **query: Any) -> Generator[_type.Type, None, None]:
        """Retrieve a generator of volume types

        :returns: A generator of volume type objects.
        """
        return self._list(_type.Type, **query)

    def create_type(self, **attrs: Any) -> _type.Type:
        """Create a new type from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.type.Type`,
            comprised of the properties on the Type class.

        :returns: The results of type creation
        """
        return self._create(_type.Type, **attrs)

    def delete_type(
        self, type: str | _type.Type, ignore_missing: bool = True
    ) -> None:
        """Delete a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the type does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent type.

        :returns: ``None``
        """
        self._delete(_type.Type, type, ignore_missing=ignore_missing)

    def update_type(
        self,
        type: str | _type.Type,
        **attrs: Any,
    ) -> _type.Type:
        """Update a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param attrs: The attributes to update on the type

        :returns: The updated type
        """
        return self._update(_type.Type, type, **attrs)

    def update_type_extra_specs(
        self,
        type: str | _type.Type,
        **attrs: Any,
    ) -> _type.Type:
        """Update the extra_specs for a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param attrs: The extra spec attributes to update on the type

        :returns: A dict containing updated extra_specs
        """
        res = self._get_resource(_type.Type, type)
        extra_specs = res.set_extra_specs(self, **attrs)
        result = _type.Type.existing(id=res.id, extra_specs=extra_specs)
        return result

    def delete_type_extra_specs(
        self,
        type: str | _type.Type,
        keys: Iterable[str],
    ) -> None:
        """Delete the extra_specs for a type

        Note: This method will do a HTTP DELETE request for every key in keys.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param keys: The keys to delete.

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.delete_extra_specs(self, keys)

    def get_type_access(self, type: str | _type.Type) -> list[dict[str, Any]]:
        """Lists project IDs that have access to private volume type.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.

        :returns: List of dictionaries describing projects that have access to
            the specified type
        """
        res = self._get_resource(_type.Type, type)
        return res.get_private_access(self)

    @renamed_param('project_id', 'project')
    def add_type_access(
        self, type: str | _type.Type, project: str | _project.Project
    ) -> None:
        """Adds private volume type access to a project.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param project: An ID or
            :class:`~openstack.identity.v3.identity.Project` instance of the
            project to add access for.

        :returns: ``None``
        """
        project_id = resource.Resource._get_id(project)
        res = self._get_resource(_type.Type, type)
        res.add_private_access(self, project_id)

    @renamed_param('project_id', 'project')
    def remove_type_access(
        self, type: str | _type.Type, project: str | _project.Project
    ) -> None:
        """Remove private volume type access from a project.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param project: An ID or
            :class:`~openstack.identity.v3.identity.Project` instance of the
            project to remove access for.

        :returns: ``None``
        """
        project_id = resource.Resource._get_id(project)
        res = self._get_resource(_type.Type, type)
        res.remove_private_access(self, project_id)

    def get_type_encryption(
        self, volume_type: str | _type.Type
    ) -> _type.TypeEncryption:
        """Get the encryption details of a volume type

        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type`
            instance.

        :returns: One :class:`~openstack.block_storage.v2.type.TypeEncryption`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        volume_type_id = resource.Resource._get_id(volume_type)
        return self._get(
            _type.TypeEncryption,
            volume_type_id=volume_type_id,
            requires_id=False,
        )

    def create_type_encryption(
        self, volume_type: str | _type.Type, **attrs: Any
    ) -> _type.TypeEncryption:
        """Create new type encryption from attributes

        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type`
            instance.

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.type.TypeEncryption`,
            comprised of the properties on the TypeEncryption class.

        :returns: The results of type encryption creation
        """
        volume_type_id = resource.Resource._get_id(volume_type)
        return self._create(
            _type.TypeEncryption, volume_type_id=volume_type_id, **attrs
        )

    def delete_type_encryption(
        self,
        encryption: str | _type.TypeEncryption | None = None,
        volume_type: str | _type.Type | None = None,
        ignore_missing: bool = True,
    ) -> None:
        """Delete type encryption attributes

        :param encryption: The value can be None or a
            :class:`~openstack.block_storage.v2.type.TypeEncryption`
            instance. If encryption is None then volume_type must be
            specified.
        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance. Required
            if encryption is None.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the type does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent type.

        :returns: ``None``
        """
        if volume_type:
            volume_type_id = resource.Resource._get_id(volume_type)
            encryption = self._get(
                _type.TypeEncryption,
                volume_type_id=volume_type_id,
                requires_id=False,
            )

        self._delete(
            _type.TypeEncryption, encryption, ignore_missing=ignore_missing
        )

    def update_type_encryption(
        self,
        encryption: str | _type.TypeEncryption | None = None,
        volume_type: str | _type.Type | None = None,
        **attrs: Any,
    ) -> _type.TypeEncryption:
        """Update a type

        :param encryption: The value can be None or a
            :class:`~openstack.block_storage.v2.type.TypeEncryption`
            instance. If this is ``None`` then ``volume_type`` must be
            specified.
        :param volume_type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
            Required if ``encryption`` is None.
        :param attrs: The attributes to update on the type encryption.

        :returns: The updated type encryption
        """

        if volume_type:
            volume_type_id = resource.Resource._get_id(volume_type)
            encryption = self._get(
                _type.TypeEncryption,
                volume_type_id=volume_type_id,
                requires_id=False,
            )

        return self._update(_type.TypeEncryption, encryption, **attrs)

    # ========== Volumes ==========

    def get_volume(self, volume: str | _volume.Volume) -> _volume.Volume:
        """Get a single volume

        :param volume: The value can be the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.

        :returns: One :class:`~openstack.block_storage.v2.volume.Volume`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_volume.Volume, volume)

    @overload
    def find_volume(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
        *,
        details: bool = True,
        all_projects: bool = False,
    ) -> _volume.Volume: ...

    @overload
    def find_volume(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
        all_projects: bool = False,
    ) -> _volume.Volume | None: ...

    def find_volume(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
        all_projects: bool = False,
    ) -> _volume.Volume | None:
        """Find a single volume

        :param volume: The name or ID a volume
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume does not exist.
        :param details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause an object with
            additional attributes to be returned.
        :param all_projects: When set to ``True``, search for volume by
            name across all projects. Note that this will likely result in
            a higher chance of duplicates. Admin-only by default.

        :returns: One :class:`~openstack.block_storage.v2.volume.Volume` or
            None.
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

    def volumes(
        self,
        *,
        details: bool = True,
        all_projects: bool = False,
        **query: Any,
    ) -> Generator[_volume.Volume, None, None]:
        """Retrieve a generator of volumes

        :param details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
        :param all_projects: When set to ``True``, list volumes from all
            projects. Admin-only by default.
        :param query: Optional query parameters to be sent to limit
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

    def create_volume(self, **attrs: Any) -> _volume.Volume:
        """Create a new volume from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.volume.Volume`,
            comprised of the properties on the Volume class.

        :returns: The results of volume creation
        """
        return self._create(_volume.Volume, **attrs)

    def update_volume(
        self,
        volume: str | _volume.Volume,
        **attrs: Any,
    ) -> _volume.Volume:
        """Update a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param attrs: The attributes to update on the volume.

        :returns: The updated volume
        """
        return self._update(_volume.Volume, volume, **attrs)

    def delete_volume(
        self,
        volume: str | _volume.Volume,
        ignore_missing: bool = True,
        *,
        force: bool = False,
        cascade: bool = False,
    ) -> None:
        """Delete a volume

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume does not exist.  When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            volume.
        :param force: Whether to try forcing volume deletion.
        :param cascade: Whether to remove any snapshots along with the
            volume.

        :returns: ``None``
        """
        if force:
            volume = self._get_resource(_volume.Volume, volume)
            try:
                volume.force_delete(self)
            except exceptions.NotFoundException:
                if ignore_missing:
                    return None
                raise
        else:
            self._delete(
                _volume.Volume,
                volume,
                ignore_missing=ignore_missing,
                params={'cascade': cascade},
            )

    # ========== Volume actions ==========

    def extend_volume(self, volume: str | _volume.Volume, size: int) -> None:
        """Extend a volume

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param size: New volume size

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.extend(self, size)

    def set_volume_readonly(
        self, volume: str | _volume.Volume, readonly: bool = True
    ) -> None:
        """Set a volume's read-only flag.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param readonly: Whether the volume should be a read-only volume
            or not.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.set_readonly(self, readonly)

    def retype_volume(
        self,
        volume: str | _volume.Volume,
        new_type: str | _type.Type,
        migration_policy: str = "never",
    ) -> None:
        """Retype the volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param new_type: The new volume type that volume is changed with.
            The value can be either the ID of the volume type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param migration_policy: Specify if the volume should be migrated
            when it is re-typed. Possible values are on-demand or never.
            Default: never.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        type_id = resource.Resource._get_id(new_type)
        volume.retype(self, type_id, migration_policy)

    def set_volume_bootable_status(
        self, volume: str | _volume.Volume, bootable: bool
    ) -> None:
        """Set bootable status of the volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param bootable: Specifies whether the volume should be bootable
            or not.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.set_bootable_status(self, bootable)

    def set_volume_image_metadata(
        self, volume: str | _volume.Volume, **metadata: str
    ) -> None:
        """Update image metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.
        :param metadata: Key/value pairs to be updated in the volume's
            image metadata. No other metadata is modified by this call.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.set_image_metadata(self, metadata=metadata)

    def delete_volume_image_metadata(
        self,
        volume: str | _volume.Volume,
        keys: Iterable[str] | None = None,
    ) -> None:
        """Delete metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.
        :param keys: The keys to delete. If omitted, all metadata is removed.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        if keys is not None:
            for key in keys:
                volume.delete_image_metadata_item(self, key)
        else:
            volume.delete_image_metadata(self)

    def reset_volume_status(
        self,
        volume: str | _volume.Volume,
        status: str | None = None,
        attach_status: str | None = None,
        migration_status: str | None = None,
    ) -> None:
        """Reset volume statuses.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param status: The new volume status.
        :param attach_status: The new volume attach status.
        :param migration_status: The new volume migration status (admin
            only).

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.reset_status(self, status, attach_status, migration_status)

    def attach_volume(
        self,
        volume: str | _volume.Volume,
        mountpoint: str,
        instance: str | None = None,
        host_name: str | None = None,
    ) -> None:
        """Attaches a volume to a server.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param mountpoint: The attaching mount point.
        :param instance: The UUID of the attaching instance.
        :param host_name: The name of the attaching host.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.attach(self, mountpoint, instance, host_name)

    def detach_volume(
        self,
        volume: str | _volume.Volume,
        attachment: str,
        force: bool = False,
        connector: dict[str, Any] | None = None,
    ) -> None:
        """Detaches a volume from a server.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param attachment: The ID of the attachment.
        :param force: Whether to force volume detach (Rolls back an
            unsuccessful detach operation after you disconnect the volume.)
        :param connector: The connector object.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.detach(self, attachment, force, connector)

    def unmanage_volume(self, volume: str | _volume.Volume) -> None:
        """Removes a volume from Block Storage management without removing the
            back-end storage object that is associated with it.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.unmanage(self)

    def migrate_volume(
        self,
        volume: str | _volume.Volume,
        host: str | None = None,
        force_host_copy: bool = False,
        lock_volume: bool = False,
    ) -> None:
        """Migrates a volume to the specified host.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param host: The target host for the volume migration. Host
            format is host@backend.
        :param force_host_copy: If false (the default), rely on the volume
            backend driver to perform the migration, which might be optimized.
            If true, or the volume driver fails to migrate the volume itself,
            a generic host-based migration is performed.
        :param lock_volume: If true, migrating an available volume will
            change its status to maintenance preventing other operations from
            being performed on the volume such as attach, detach, retype, etc.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.migrate(self, host, force_host_copy, lock_volume)

    def complete_volume_migration(
        self,
        volume: str | _volume.Volume,
        new_volume: str,
        error: bool = False,
    ) -> None:
        """Complete the migration of a volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param new_volume: The UUID of the new volume.
        :param error: Used to indicate if an error has occured elsewhere
            that requires clean up.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.complete_migration(self, new_volume, error)

    def upload_volume_to_image(
        self,
        volume: str | _volume.Volume,
        image_name: str,
        force: bool = False,
        disk_format: str | None = None,
        container_format: str | None = None,
    ) -> dict[str, Any]:
        """Uploads the specified volume to image service.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v3.volume.Volume` instance.
        :param image_name: The name for the new image.
        :param force: Enables or disables upload of a volume that is
            attached to an instance.
        :param disk_format: Disk format for the new image.
        :param container_format: Container format for the new image.

        :returns: dictionary describing the image.
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.upload_to_image(
            self,
            image_name,
            force=force,
            disk_format=disk_format,
            container_format=container_format,
        )

    # ========== Backend pools ==========

    def backend_pools(
        self,
        **query: Any,
    ) -> Generator[_stats.Pools, None, None]:
        """Returns a generator of cinder Back-end storage pools

        :param query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns A generator of cinder Back-end storage pools objects
        """
        return self._list(_stats.Pools, **query)

    # ========== Backups ==========

    def backups(
        self,
        details: bool = True,
        **query: Any,
    ) -> Generator[_backup.Backup, None, None]:
        """Retrieve a generator of backups

        :param details: When set to ``False`` no additional details will
            be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
        :param query: Optional query parameters to be sent to limit the
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

        :returns: A generator of backup objects.
        """
        base_path = '/backups/detail' if details else None
        return self._list(_backup.Backup, base_path=base_path, **query)

    def get_backup(self, backup: str | _backup.Backup) -> _backup.Backup:
        """Get a backup

        :param backup: The value can be the ID of a backup
            or a :class:`~openstack.block_storage.v2.backup.Backup`
            instance.

        :returns: Backup instance
        """
        return self._get(_backup.Backup, backup)

    @overload
    def find_backup(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
        *,
        details: bool = True,
    ) -> _backup.Backup: ...

    @overload
    def find_backup(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
    ) -> _backup.Backup | None: ...

    def find_backup(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
    ) -> _backup.Backup | None:
        """Find a single backup

        :param snapshot: The name or ID a backup
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the backup does not exist.
        :param details: When set to ``False`` no additional details will
            be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.

        :returns: One :class:`~openstack.block_storage.v2.backup.Backup`
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

    def create_backup(self, **attrs: Any) -> _backup.Backup:
        """Create a new Backup from attributes with native API

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.backup.Backup`
            comprised of the properties on the Backup class.

        :returns: The results of Backup creation
        """
        return self._create(_backup.Backup, **attrs)

    def delete_backup(
        self,
        backup: str | _backup.Backup,
        ignore_missing: bool = True,
        force: bool = False,
    ) -> None:
        """Delete a CloudBackup

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v2.backup.Backup` instance
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent zone.
        :param force: Whether to try forcing backup deletion

        :returns: ``None``
        """
        if not force:
            self._delete(_backup.Backup, backup, ignore_missing=ignore_missing)
        else:
            backup = self._get_resource(_backup.Backup, backup)
            backup.force_delete(self)

    # ========== Backup actions ==========

    def import_backup(self, service: str, url: str) -> _backup.Backup:
        """Create a new backup from an external service.

        :param service: The service used to perform the backup.
        :param url: An identifier string to locate the backup.

        :returns: The imported backup
        """
        return _backup.Backup.import_record(self, service=service, url=url)

    def export_backup(self, backup: str | _backup.Backup) -> dict[str, Any]:
        """Export information about a backup

        :param backup: The value can be the ID of a backup
            or a :class:`~openstack.block_storage.v2.backup.Backup`
            instance.

        :returns: The backup export record fields
        """
        backup = self._get_resource(_backup.Backup, backup)
        return backup.export_record(self)

    # TODO(stephenfin): Remove in 5.0
    def export_record(self, backup: str | _backup.Backup) -> dict[str, Any]:
        warnings.warn(
            "export_record is a deprecated alias for export_backup and will "
            "be removed in a future release.",
            os_warnings.RemovedInSDK50Warning,
        )
        return self.export_backup(backup)

    @renamed_param('volume_id', 'volume')
    def restore_backup(
        self,
        backup: str | _backup.Backup,
        volume: str | _volume.Volume | None = None,
        name: str | None = None,
    ) -> _backup.Backup:
        """Restore a Backup to volume

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v2.backup.Backup` instance
        :param volume: An ID or
            :class:`~openstack.volume.v2.volume.Volume` instance of the
            volume to restore the backup to.
        :param name: The name for new volume creation to restore.

        :returns: Updated backup instance
        """
        volume_id = resource.Resource._get_id(volume) if volume else None
        return self._get_resource(_backup.Backup, backup).restore(
            self, volume_id=volume_id, name=name
        )

    def reset_backup_status(
        self, backup: str | _backup.Backup, status: str
    ) -> None:
        """Reset status of the backup

        :param backup: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v2.backup.Backup` instance.
        :param status: New backup status

        :returns: None
        """
        backup = self._get_resource(_backup.Backup, backup)
        backup.reset_status(self, status)

    def reset_backup(self, backup: str | _backup.Backup, status: str) -> None:
        warnings.warn(
            "reset_backup is a deprecated alias for reset_backup_status "
            "and will be removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        return self.reset_backup_status(backup, status)

    # ========== Limits ==========

    def get_limits(
        self, project: str | _project.Project | None = None
    ) -> _limits.Limits:
        """Retrieves limits

        :param project: A project to get limits for. The value can be either
            the ID of a project or an
            :class:`~openstack.identity.v2.project.Project` instance.
        :returns: A Limits object, including both
            :class:`~openstack.block_storage.v2.limits.AbsoluteLimit` and
            :class:`~openstack.block_storage.v2.limits.RateLimit`
        """
        if project:
            return self._get(
                _limits.Limits,
                requires_id=False,
                project_id=resource.Resource._get_id(project),
            )
        return self._get(_limits.Limits, requires_id=False)

    # ========== Capabilities ==========

    def get_capabilities(self, host: str) -> _capabilities.Capabilities:
        """Get a backend's capabilites

        :param host: Specified backend to obtain volume stats and properties.

        :returns: One :class:
            `~openstack.block_storage.v2.capabilites.Capabilities` instance.
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(_capabilities.Capabilities, host)

    # ====== QoS ======

    def create_qos_spec(self, **attrs: Any) -> _qos_spec.QoSSpec:
        """Create a new QoS Spec from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpec`, comprised
            of the properties on the QoSSpec class.

        :returns: The results of a QoS spec creation
        :rtype: :class:`~openstack.block_storage.v2.qos_spec.QoSSpec`
        """
        return self._create(_qos_spec.QoSSpec, **attrs)

    def delete_qos_spec(
        self,
        qos_spec: str | _qos_spec.QoSSpec,
        ignore_missing: bool = True,
        *,
        force: bool = False,
    ) -> None:
        """Delete a QoS Spec

        :param qos_spec: The value can be either the ID of a QoS spec or a
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpec` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the type does not exist. When set to ``True``, no exception will be
            set when attempting to delete a nonexistent type.
        :param force: Whether to delete the QoS spec even if it's in use.

        :returns: ``None``
        """
        res = self._get_resource(_qos_spec.QoSSpec, qos_spec)
        try:
            res.delete(self, params={'force': force})
        except exceptions.NotFoundException:
            if ignore_missing:
                return None
            raise

    def update_qos_spec(
        self,
        qos_spec: str | _qos_spec.QoSSpec,
        **attrs: Any,
    ) -> _qos_spec.QoSSpec:
        """Update a QoS spec

        :param qos_spec: The value can be either the ID of a QoS spec or a
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpec` instance.
        :param dict attrs: The attributes to update on the QoS spec

        :returns: The updated QoS spec
        :rtype: :class:`~openstack.block_storage.v2.qos_spec.QoSSpec`
        """
        return self._update(_qos_spec.QoSSpec, qos_spec, **attrs)

    def get_qos_spec(self, qos_spec: _qos_spec.QoSSpec) -> _qos_spec.QoSSpec:
        """Get a single QoS spec

        :param qos_spec: The value can be either the ID of a QoS spec or a
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpec` instance.

        :returns: One :class:`~openstack.block_storage.v2.qos_spec.QoSSpec`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            resource can be found.
        """
        return self._get(_qos_spec.QoSSpec, qos_spec)

    @overload
    def find_qos_spec(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
        **query: Any,
    ) -> _qos_spec.QoSSpec: ...

    @overload
    def find_qos_spec(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        **query: Any,
    ) -> _qos_spec.QoSSpec | None: ...

    def find_qos_spec(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        **query: Any,
    ) -> _qos_spec.QoSSpec | None:
        """Find a single QoS spec

        :param name_or_id: The name or ID of a QoS spec
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource does not exist. When set to ``True``, None will
            be returned when attempting to find a nonexistent resource.
        :param query: Additional attributes like 'host'

        :returns: One: class:`~openstack.block_storage.v2.qos_spec.QoSSpec` or
            None
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        return self._find(
            _qos_spec.QoSSpec,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def qos_specs(
        self,
        **query: Any,
    ) -> Generator[_qos_spec.QoSSpec, None, None]:
        """Return a generator of QoS specs

        :param query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of QoSSpec objects
        """
        return self._list(_qos_spec.QoSSpec, **query)

    def associate_qos_spec(
        self,
        qos_spec: str | _qos_spec.QoSSpec,
        vol_type_id: str,
    ) -> None:
        """Associate a QoS spec with a volume type

        :param qos_spec: The value can be either the ID of a QoS spec or a
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpec` instance.
        :param vol_type_id: The ID of the volume type to associate with.

        :returns: ``None``
        """
        qos_spec_obj = self._get_resource(_qos_spec.QoSSpec, qos_spec)
        qos_spec_obj.associate(self, vol_type_id)

    def disassociate_qos_spec(
        self,
        qos_spec: str | _qos_spec.QoSSpec,
        vol_type_id: str,
    ) -> None:
        """Disassociate a QoS spec from a volume type

        :param qos_spec: The value can be either the ID of a QoS spec or a
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpec` instance.
        :param vol_type_id: The ID of the volume type to disassociate from.

        :returns: ``None``
        """
        qos_spec_obj = self._get_resource(_qos_spec.QoSSpec, qos_spec)
        qos_spec_obj.disassociate(self, vol_type_id)

    def disassociate_all_qos_spec(
        self,
        qos_spec: str | _qos_spec.QoSSpec,
    ) -> None:
        """Disassociate a QoS spec from all volume types

        :param qos_spec: The value can be either the ID of a QoS spec or a
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpec` instance.

        :returns: ``None``
        """
        qos_spec_obj = self._get_resource(_qos_spec.QoSSpec, qos_spec)
        qos_spec_obj.disassociate_all(self)

    def delete_qos_spec_metadata(
        self,
        qos_spec: str | _qos_spec.QoSSpec,
        keys: Iterable[Any],
    ) -> None:
        """Delete metadata from a QoS spec

        :param qos_spec: The value can be either the ID of a QoS spec or a
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpec` instance.
        :param keys: The keys to delete from the QoS spec.

        :returns: ``None``
        """
        qos_spec_obj = self._get_resource(_qos_spec.QoSSpec, qos_spec)
        qos_spec_obj.delete_keys(self, keys)

    def qos_spec_associations(
        self,
        qos_spec: str | _qos_spec.QoSSpec,
    ) -> Generator[_qos_spec.QoSSpecAssociation, None, None]:
        """Return a generator of associations for a QoS spec

        :param qos_spec: The value can be either the ID of a QoS spec or a
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpec` instance.

        :returns: A generator of
            :class:`~openstack.block_storage.v2.qos_spec.QoSSpecAssociation`
            objects
        """
        qos_spec_id = resource.Resource._get_id(qos_spec)
        return self._list(
            _qos_spec.QoSSpecAssociation, qos_spec_id=qos_spec_id
        )

    # ========== Quota class sets ==========

    def get_quota_class_set(
        self,
        quota_class_set: str | _quota_class_set.QuotaClassSet = 'default',
    ) -> _quota_class_set.QuotaClassSet:
        """Get a single quota class set

        Only one quota class is permitted, ``default``.

        :param quota_class_set: The value can be the ID of a quota class set
            (only ``default`` is supported) or a
            :class:`~openstack.block_storage.v2.quota_class_set.QuotaClassSet`
            instance.

        :returns: One
            :class:`~openstack.block_storage.v2.quota_class_set.QuotaClassSet`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_quota_class_set.QuotaClassSet, quota_class_set)

    def update_quota_class_set(
        self,
        quota_class_set: str | _quota_class_set.QuotaClassSet,
        **attrs: Any,
    ) -> _quota_class_set.QuotaClassSet:
        """Update a QuotaClassSet.

        Only one quota class is permitted, ``default``.

        :param quota_class_set: Either the ID of a quota class set (only
            ``default`` is supported) or a
            :class:`~openstack.block_storage.v2.quota_class_set.QuotaClassSet`
            instance.
        :param attrs: The attributes to update on the QuotaClassSet represented
            by ``quota_class_set``.

        :returns: The updated QuotaSet
        """
        return self._update(
            _quota_class_set.QuotaClassSet, quota_class_set, **attrs
        )

    # ========== Quota sets ==========

    def get_quota_set(
        self,
        project: str | _project.Project,
        usage: bool = False,
        **query: Any,
    ) -> _quota_set.QuotaSet:
        """Show QuotaSet information for the project

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be retrieved
        :param usage: When set to ``True`` quota usage and reservations
            would be filled.
        :param query: Additional query parameters to use.

        :returns: One :class:`~openstack.block_storage.v2.quota_set.QuotaSet`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        project = self._get_resource(_project.Project, project)
        res = self._get_resource(
            _quota_set.QuotaSet, None, project_id=project.id
        )
        return res.fetch(self, usage=usage, **query)

    def get_quota_set_defaults(
        self, project: str | _project.Project
    ) -> _quota_set.QuotaSet:
        """Show QuotaSet defaults for the project

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be retrieved

        :returns: One :class:`~openstack.block_storage.v2.quota_set.QuotaSet`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        project = self._get_resource(_project.Project, project)
        res = self._get_resource(
            _quota_set.QuotaSet, None, project_id=project.id
        )
        return res.fetch(self, base_path='/os-quota-sets/defaults')

    def revert_quota_set(
        self, project: str | _project.Project, **query: Any
    ) -> None:
        """Reset Quota for the project/user.

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be resetted.
        :param query: Additional parameters to be used.

        :returns: ``None``
        """
        project = self._get_resource(_project.Project, project)
        self._delete(
            _quota_set.QuotaSet,
            None,
            ignore_missing=False,
            project_id=project.id,
            params=query or None,
        )

    # TODO(stephenfin): Drop the QuotaSet fallback in 5.0
    def update_quota_set(
        self,
        project: str | _project.Project | _quota_set.QuotaSet,
        **attrs: Any,
    ) -> _quota_set.QuotaSet:
        """Update a QuotaSet.

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be reset.
        :param attrs: The attributes to update on the QuotaSet represented
            by ``quota_set``.

        :returns: The updated QuotaSet
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

            # we know it'll be one of the two above in this case, per above
            assert isinstance(project, str | _quota_set.QuotaSet)

            res = self._get_resource(_quota_set.QuotaSet, project, **attrs)
            return res.commit(self)
        else:
            project = self._get_resource(_project.Project, project)
            attrs['project_id'] = project.id
            return self._update(_quota_set.QuotaSet, None, **attrs)

    # ========== Services ==========
    @overload
    def find_service(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
        **query: Any,
    ) -> _service.Service: ...

    @overload
    def find_service(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        **query: Any,
    ) -> _service.Service | None: ...

    def find_service(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        **query: Any,
    ) -> _service.Service | None:
        """Find a single service

        :param name_or_id: The name or ID of a service
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource does not exist. When set to ``True``, None will
            be returned when attempting to find a nonexistent resource.
        :param query: Additional attributes like 'host'

        :returns: One: class:`~openstack.block_storage.v2.service.Service` or
            None
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
        **query: Any,
    ) -> Generator[_service.Service, None, None]:
        """Return a generator of service

        :param query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of Service objects
        """
        return self._list(_service.Service, **query)

    def enable_service(
        self,
        service: str | _service.Service,
    ) -> _service.Service:
        """Enable a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v2.service.Service` instance.

        :returns: Updated service instance
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.enable(self)

    def disable_service(
        self,
        service: str | _service.Service,
        *,
        reason: str | None = None,
    ) -> _service.Service:
        """Disable a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v2.service.Service` instance
        :param reason: The reason to disable a service

        :returns: Updated service instance
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.disable(self, reason=reason)

    def thaw_service(
        self,
        service: str | _service.Service,
    ) -> _service.Service:
        """Thaw a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v2.service.Service` instance

        :returns: Updated service instance
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.thaw(self)

    def freeze_service(
        self,
        service: str | _service.Service,
    ) -> _service.Service:
        """Freeze a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v2.service.Service` instance

        :returns: Updated service instance
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.freeze(self)

    def failover_service(
        self,
        service: str | _service.Service,
        *,
        backend_id: str | None = None,
    ) -> _service.Service:
        """Failover a service

        Only applies to replicating cinder-volume services.

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v2.service.Service` instance

        :returns: Updated service instance
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.failover(self, backend_id=backend_id)

    # ========== Volume metadata ==========

    def fetch_volume_metadata(
        self, volume: str | _volume.Volume
    ) -> _volume.Volume:
        """Return a dictionary of metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.

        :returns: A :class:`~openstack.block_storage.v2.volume.Volume` with the
            volume's metadata. All keys and values are Unicode text.
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.fetch_metadata(self)

    # TODO(stephenfin): Remove in 5.0
    def get_volume_metadata(
        self, volume: str | _volume.Volume
    ) -> _volume.Volume:
        """Return a dictionary of metadata for a volume

        .. deprecated:: 4.14.0
            Use :meth:`fetch_volume_metadata` instead.
        """
        warnings.warn(
            "The 'get_volume_metadata' method is deprecated; use "
            "'fetch_volume_metadata' instead.",
            os_warnings.RemovedInSDK50Warning,
        )
        return self.fetch_volume_metadata(volume)

    def set_volume_metadata(
        self, volume: str | _volume.Volume, **metadata: str
    ) -> _volume.Volume:
        """Update metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.
        :param metadata: Key/value pairs to be updated in the volume's
            metadata. No other metadata is modified by this call. All keys
            and values are stored as Unicode.

        :returns: A :class:`~openstack.block_storage.v2.volume.Volume` with the
            volume's metadata. All keys and values are Unicode text.
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.set_metadata(self, metadata=metadata)

    def delete_volume_metadata(
        self,
        volume: str | _volume.Volume,
        keys: Iterable[str] | None = None,
    ) -> None:
        """Delete metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.
        :param keys: The keys to delete. If omitted, all metadata is removed.

        :returns: ``None``
        """
        volume = self._get_resource(_volume.Volume, volume)
        if keys is not None:
            for key in keys:
                volume.delete_metadata_item(self, key)
        else:
            volume.delete_metadata(self)

    # ========== Snapshot metadata ==========

    def fetch_snapshot_metadata(
        self, snapshot: str | _snapshot.Snapshot
    ) -> _snapshot.Snapshot:
        """Return a dictionary of metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`.

        :returns: A
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` with the
            snapshot's metadata. All keys and values are Unicode text.
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        return snapshot.fetch_metadata(self)

    # TODO(stephenfin): Remove in 5.0
    def get_snapshot_metadata(
        self, snapshot: str | _snapshot.Snapshot
    ) -> _snapshot.Snapshot:
        """Return a dictionary of metadata for a snapshot

        .. deprecated:: 4.14.0
            Use :meth:`fetch_snapshot_metadata` instead.
        """
        warnings.warn(
            "The 'get_snapshot_metadata' method is deprecated; use "
            "'fetch_snapshot_metadata' instead.",
            os_warnings.RemovedInSDK50Warning,
        )
        return self.fetch_snapshot_metadata(snapshot)

    def set_snapshot_metadata(
        self, snapshot: str | _snapshot.Snapshot, **metadata: str
    ) -> _snapshot.Snapshot:
        """Update metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`.
        :param metadata: Key/value pairs to be updated in the snapshot's
            metadata. No other metadata is modified by this call. All keys
            and values are stored as Unicode.

        :returns: A
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` with the
            snapshot's metadata. All keys and values are Unicode text.
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        return snapshot.set_metadata(self, metadata=metadata)

    def delete_snapshot_metadata(
        self,
        snapshot: str | _snapshot.Snapshot,
        keys: Iterable[str] | None = None,
    ) -> None:
        """Delete metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`.
        :param keys: The keys to delete. If omitted, all metadata is removed.

        :returns: ``None``
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        if keys is not None:
            for key in keys:
                snapshot.delete_metadata_item(self, key)
        else:
            snapshot.delete_metadata(self)

    # ========== Transfers ==========

    def create_transfer(self, **attrs: Any) -> _transfer.Transfer:
        """Create a new Transfer record

        :param volume_id: The value is ID of the volume.
        :param name: The value is name of the transfer
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.transfer.Transfer`
            comprised of the properties on the Transfer class.

        :returns: The results of Transfer creation
        """
        return self._create(_transfer.Transfer, **attrs)

    def delete_transfer(
        self, transfer: str | _transfer.Transfer, ignore_missing: bool = True
    ) -> None:
        """Delete a volume transfer

        :param transfer: The value can be either the ID of a transfer or a
            :class:`~openstack.block_storage.v2.transfer.Transfer`` instance.
        :param ignore_missing: When set to ``False``
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

    @overload
    def find_transfer(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
    ) -> _transfer.Transfer: ...

    @overload
    def find_transfer(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _transfer.Transfer | None: ...

    def find_transfer(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _transfer.Transfer | None:
        """Find a single transfer

        :param name_or_id: The name or ID a transfer
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume transfer does not exist.

        :returns: One :class:`~openstack.block_storage.v2.transfer.Transfer`
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

    def get_transfer(
        self, transfer: str | _transfer.Transfer
    ) -> _transfer.Transfer:
        """Get a single transfer

        :param transfer: The value can be the ID of a transfer or a
            :class:`~openstack.block_storage.v2.transfer.Transfer`
            instance.

        :returns: One :class:`~openstack.block_storage.v2.transfer.Transfer`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_transfer.Transfer, transfer)

    def transfers(
        self,
        *,
        details: bool = True,
        all_projects: bool = False,
        **query: Any,
    ) -> Generator[_transfer.Transfer, None, None]:
        """Retrieve a generator of transfers

        :param details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
        :param all_projects: When set to ``True``, list transfers from
            all projects. Admin-only by default.
        :param query: Optional query parameters to be sent to limit
            the transfers being returned.

        :returns: A generator of transfer objects.
        """
        if all_projects:
            query['all_projects'] = True
        base_path = '/volume-transfers'
        if details:
            base_path = utils.urljoin(base_path, 'detail')
        return self._list(_transfer.Transfer, base_path=base_path, **query)

    @renamed_param('transfer_id', 'transfer')
    def accept_transfer(
        self, transfer: str | _transfer.Transfer, auth_key: str
    ) -> _transfer.Transfer:
        """Accept a Transfer

        :param transfer: The value can be the ID of a transfer or a
            :class:`~openstack.block_storage.v2.transfer.Transfer`
            instance.
        :param auth_key: The key to authenticate volume transfer.

        :returns: The results of Transfer creation
        """
        transfer = self._get_resource(_transfer.Transfer, transfer)
        return transfer.accept(self, auth_key=auth_key)

    # ========== Consistency groups ==========

    def get_consistency_group(
        self,
        consistency_group: str | _consistency_group.ConsistencyGroup,
    ) -> _consistency_group.ConsistencyGroup:
        """Get a consistency group.

        :param consistency_group: The value can be either the ID of a
            consistency group or a
            :class:`~openstack.block_storage.v2.consistency_group.ConsistencyGroup`
            instance.

        :returns: One
            :class:`~openstack.block_storage.v2.consistency_group.ConsistencyGroup`
        """
        return self._get(
            _consistency_group.ConsistencyGroup, consistency_group
        )

    @overload
    def find_consistency_group(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
        *,
        details: bool = True,
    ) -> _consistency_group.ConsistencyGroup: ...

    @overload
    def find_consistency_group(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
    ) -> _consistency_group.ConsistencyGroup | None: ...

    def find_consistency_group(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
    ) -> _consistency_group.ConsistencyGroup | None:
        """Find a single consistency group.

        :param name_or_id: The name or ID of a consistency group.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the consistency group does not exist.
        :param details: When set to ``False``, no additional details will
            be returned. The default, ``True``, will cause additional details
            to be returned.

        :returns: One
            :class:`~openstack.block_storage.v2.consistency_group.ConsistencyGroup`
            or None.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        list_base_path = '/consistencygroups/detail' if details else None
        return self._find(
            _consistency_group.ConsistencyGroup,
            name_or_id,
            ignore_missing=ignore_missing,
            list_base_path=list_base_path,
        )

    def consistency_groups(
        self, *, details: bool = True, **query: Any
    ) -> Generator[_consistency_group.ConsistencyGroup, None, None]:
        """Retrieve a generator of consistency groups.

        :param details: When set to ``False``, no additional details will
            be returned. The default, ``True``, will cause additional details
            to be returned.
        :param query: Optional query parameters to be sent to limit the
            resources being returned:

            * limit: Returns a number of items up to the limit value.
            * offset: Used in conjunction with limit to return a slice of
              items. Specifies where to start in the list.
            * marker: The ID of the last-seen item.
            * sort_dir: Sorts the response in the requested order.
            * sort_key: Sorts the list of consistency groups by the specified
              attribute.

        :returns: A generator of consistency group objects.
        """
        base_path = '/consistencygroups/detail' if details else None
        return self._list(
            _consistency_group.ConsistencyGroup, base_path=base_path, **query
        )

    def create_consistency_group(
        self, **attrs: Any
    ) -> _consistency_group.ConsistencyGroup:
        """Create a new consistency group.

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.block_storage.v2.consistency_group.ConsistencyGroup`,
            comprised of the properties on the ConsistencyGroup class.

        :returns: The result of consistency group creation.
        """
        return self._create(_consistency_group.ConsistencyGroup, **attrs)

    def create_consistency_group_from_source(
        self,
        *,
        consistency_group_snapshot: (
            str | _consistency_group_snapshot.ConsistencyGroupSnapshot | None
        ) = None,
        consistency_group: (
            str | _consistency_group.ConsistencyGroup | None
        ) = None,
        name: str | None = None,
        description: str | None = None,
    ) -> _consistency_group.ConsistencyGroup:
        """Create a new consistency group from source.

        :param consistency_group_snapshot: The value can be either the ID of
            a consistency group snapshot or a
            :class:`~openstack.block_storage.v2.consistency_group_snapshot.ConsistencyGroupSnapshot`
            instance. Either this or ``consistency_group`` must be provided.
        :param consistency_group: The value can be either the ID of a
            consistency group or a
            :class:`~openstack.block_storage.v2.consistency_group.ConsistencyGroup`
            instance. Either this or ``consistency_group_snapshot`` must be
            provided.
        :param name: The name to assign to the new consistency group.
        :param description: The description to set on the new consistency
            group.

        :returns: The result of consistency group creation.
        """
        cg_id = None
        if consistency_group:
            cg_id = resource.Resource._get_id(consistency_group)

        cg_snap_id = None
        if consistency_group_snapshot:
            cg_snap_id = resource.Resource._get_id(consistency_group_snapshot)

        return _consistency_group.ConsistencyGroup.create_from_source(
            self,
            consistency_group_id=cg_id,
            consistency_group_snapshot_id=cg_snap_id,
            name=name,
            description=description,
        )

    def delete_consistency_group(
        self,
        consistency_group: str | _consistency_group.ConsistencyGroup,
        force: bool = False,
    ) -> None:
        """Delete a consistency group.

        :param consistency_group: The value can be either the ID of a
            consistency group or a
            :class:`~openstack.block_storage.v2.consistency_group.ConsistencyGroup`
            instance.
        :param force: When set to ``True``, volumes in the consistency group
            will also be deleted when the consistency group is deleted.

        :returns: ``None``
        """
        res = self._get_resource(
            _consistency_group.ConsistencyGroup, consistency_group
        )
        res.delete(self, params={'force': force})

    def update_consistency_group(
        self,
        consistency_group: str | _consistency_group.ConsistencyGroup,
        **attrs: Any,
    ) -> _consistency_group.ConsistencyGroup:
        """Update a consistency group.

        :param consistency_group: The value can be either the ID of a
            consistency group or a
            :class:`~openstack.block_storage.v2.consistency_group.ConsistencyGroup`
            instance.
        :param attrs: The attributes to update on the consistency group
            represented by ``consistency_group``. To add or remove volumes,
            pass ``add_volumes`` or ``remove_volumes`` as comma-separated lists
            of volume IDs.

        :returns: The updated consistency group.
        """
        return self._update(
            _consistency_group.ConsistencyGroup, consistency_group, **attrs
        )

    # ========== Consistency group snapshots ==========

    def get_consistency_group_snapshot(
        self,
        consistency_group_snapshot: (
            str | _consistency_group_snapshot.ConsistencyGroupSnapshot
        ),
    ) -> _consistency_group_snapshot.ConsistencyGroupSnapshot:
        """Get a consistency group snapshot.

        :param consistency_group_snapshot: The value can be either the ID of a
            consistency group snapshot or a
            :class:`~openstack.block_storage.v2.consistency_group_snapshot.ConsistencyGroupSnapshot`
            instance.

        :returns: One
            :class:`~openstack.block_storage.v2.consistency_group_snapshot.ConsistencyGroupSnapshot`
        """
        return self._get(
            _consistency_group_snapshot.ConsistencyGroupSnapshot,
            consistency_group_snapshot,
        )

    @overload
    def find_consistency_group_snapshot(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
        *,
        details: bool = True,
    ) -> _consistency_group_snapshot.ConsistencyGroupSnapshot: ...

    @overload
    def find_consistency_group_snapshot(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
    ) -> _consistency_group_snapshot.ConsistencyGroupSnapshot | None: ...

    def find_consistency_group_snapshot(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
        *,
        details: bool = True,
    ) -> _consistency_group_snapshot.ConsistencyGroupSnapshot | None:
        """Find a single consistency group snapshot.

        :param name_or_id: The name or ID of a consistency group snapshot.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the consistency group snapshot does not exist.
        :param details: When set to ``False``, no additional details will
            be returned. The default, ``True``, will cause additional details
            to be returned.

        :returns: One
            :class:`~openstack.block_storage.v2.consistency_group_snapshot.ConsistencyGroupSnapshot`
            or None.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        :raises: :class:`~openstack.exceptions.DuplicateResource` when multiple
            resources are found.
        """
        list_base_path = '/cgsnapshots/detail' if details else None
        return self._find(
            _consistency_group_snapshot.ConsistencyGroupSnapshot,
            name_or_id,
            ignore_missing=ignore_missing,
            list_base_path=list_base_path,
        )

    def consistency_group_snapshots(
        self, *, details: bool = True, **query: Any
    ) -> Generator[
        _consistency_group_snapshot.ConsistencyGroupSnapshot, None, None
    ]:
        """Retrieve a generator of consistency group snapshots.

        :param details: When set to ``False``, no additional details will
            be returned. The default, ``True``, will cause additional details
            to be returned.
        :param query: Optional query parameters to be sent to limit the
            resources being returned:

            * limit: Returns a number of items up to the limit value.
            * offset: Used in conjunction with limit to return a slice of
              items. Specifies where to start in the list.
            * marker: The ID of the last-seen item.

        :returns: A generator of consistency group snapshot objects.
        """
        base_path = '/cgsnapshots/detail' if details else None
        return self._list(
            _consistency_group_snapshot.ConsistencyGroupSnapshot,
            base_path=base_path,
            **query,
        )

    def create_consistency_group_snapshot(
        self, **attrs: Any
    ) -> _consistency_group_snapshot.ConsistencyGroupSnapshot:
        """Create a new consistency group snapshot.

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.block_storage.v2.consistency_group_snapshot.ConsistencyGroupSnapshot`,
            comprised of the properties on the ConsistencyGroupSnapshot class.
            The ``consistencygroup_id`` attribute is required.

        :returns: The result of consistency group snapshot creation.
        """
        return self._create(
            _consistency_group_snapshot.ConsistencyGroupSnapshot, **attrs
        )

    def delete_consistency_group_snapshot(
        self,
        consistency_group_snapshot: (
            str | _consistency_group_snapshot.ConsistencyGroupSnapshot
        ),
        ignore_missing: bool = True,
    ) -> None:
        """Delete a consistency group snapshot.

        :param consistency_group_snapshot: The value can be either the ID of a
            consistency group snapshot or a
            :class:`~openstack.block_storage.v2.consistency_group_snapshot.ConsistencyGroupSnapshot`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the consistency group snapshot does not exist.

        :returns: ``None``
        """
        self._delete(
            _consistency_group_snapshot.ConsistencyGroupSnapshot,
            consistency_group_snapshot,
            ignore_missing=ignore_missing,
        )

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str = 'available',
        failures: list[str] | None = None,
        interval: int | float | None = 2,
        wait: int | None = None,
        attribute: str = 'status',
        callback: Callable[[int], None] | None = None,
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

        :returns: The updated resource.
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
        interval: int | float | None = 2,
        wait: int | None = 120,
        callback: Callable[[int], None] | None = None,
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
