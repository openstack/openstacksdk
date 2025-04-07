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

from openstack.block_storage.v2 import backup as _backup
from openstack.block_storage.v2 import capabilities as _capabilities
from openstack.block_storage.v2 import extension as _extension
from openstack.block_storage.v2 import limits as _limits
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
from openstack import proxy
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings


class Proxy(proxy.Proxy):
    # ========== Extensions ==========

    def extensions(self):
        """Return a generator of extensions

        :returns: A generator of extension
        :rtype: :class:`~openstack.block_storage.v2.extension.Extension`
        """
        return self._list(_extension.Extension)

    # ========== Images ==========

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

    # ========== Snapshots ==========

    def get_snapshot(self, snapshot):
        """Get a single snapshot

        :param snapshot: The value can be the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`
            instance.

        :returns: One :class:`~openstack.block_storage.v2.snapshot.Snapshot`
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
        :param bool details: When set to ``False``, an
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` object will
            be returned. The default, ``True``, will cause an
            :class:`~openstack.block_storage.v2.snapshot.SnapshotDetail` object
            to be returned.
        :param bool all_projects: When set to ``True``, search for snapshot by
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

    def snapshots(self, *, details=True, all_projects=False, **query):
        """Retrieve a generator of snapshots

        :param bool details: When set to ``False``
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`
            objects will be returned. The default, ``True``, will cause
            :class:`~openstack.block_storage.v2.snapshot.SnapshotDetail`
            objects to be returned.
        :param bool all_projects: When set to ``True``, list snapshots from all
            projects. Admin-only by default.
        :param kwargs query: Optional query parameters to be sent to limit
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

    def create_snapshot(self, **attrs):
        """Create a new snapshot from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.snapshot.Snapshot`,
            comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        :rtype: :class:`~openstack.block_storage.v2.snapshot.Snapshot`
        """
        return self._create(_snapshot.Snapshot, **attrs)

    def update_snapshot(self, snapshot, **attrs):
        """Update a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` instance.
        :param dict attrs: The attributes to update on the snapshot.

        :returns: The updated snapshot
        :rtype: :class:`~openstack.block_storage.v2.snapshot.Snapshot`
        """
        return self._update(_snapshot.Snapshot, snapshot, **attrs)

    def delete_snapshot(self, snapshot, ignore_missing=True):
        """Delete a snapshot

        :param snapshot: The value can be either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the snapshot does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent snapshot.

        :returns: ``None``
        """
        self._delete(
            _snapshot.Snapshot, snapshot, ignore_missing=ignore_missing
        )

    # ========== Snapshot actions ==========

    def reset_snapshot_status(self, snapshot, status):
        """Reset status of the snapshot

        :param snapshot: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` instance.
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

    def manage_snapshot(self, **attrs):
        """Creates a snapshot by using existing storage rather than
        allocating new storage.

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.snapshot.Snapshot`,
            comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        :rtype: :class:`~openstack.block_storage.v2.snapshot.Snapshot`
        """
        return _snapshot.Snapshot.manage(self, **attrs)

    def unmanage_snapshot(self, snapshot):
        """Unmanage a snapshot from block storage provisioning.

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`.

        :returns: None
        """
        snapshot_obj = self._get_resource(_snapshot.Snapshot, snapshot)
        snapshot_obj.unmanage(self)

    # ========== Types ==========

    def get_type(self, type):
        """Get a single type

        :param type: The value can be the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.

        :returns: One :class:`~openstack.block_storage.v2.type.Type`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_type.Type, type)

    def find_type(self, name_or_id, ignore_missing=True):
        """Find a single volume type

        :param snapshot: The name or ID a volume type
        :param bool ignore_missing: When set to ``False``
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

    def types(self, **query):
        """Retrieve a generator of volume types

        :returns: A generator of volume type objects.
        """
        return self._list(_type.Type, **query)

    def create_type(self, **attrs):
        """Create a new type from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.type.Type`,
            comprised of the properties on the Type class.

        :returns: The results of type creation
        :rtype: :class:`~openstack.block_storage.v2.type.Type`
        """
        return self._create(_type.Type, **attrs)

    def delete_type(self, type, ignore_missing=True):
        """Delete a type

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the type does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent type.

        :returns: ``None``
        """
        self._delete(_type.Type, type, ignore_missing=ignore_missing)

    def get_type_access(self, type):
        """Lists project IDs that have access to private volume type.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.

        :returns: List of dictionaries describing projects that have access to
            the specified type
        """
        res = self._get_resource(_type.Type, type)
        return res.get_private_access(self)

    def add_type_access(self, type, project_id):
        """Adds private volume type access to a project.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param str project_id: The ID of the project. Volume Type access to
            be added to this project ID.

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.add_private_access(self, project_id)

    def remove_type_access(self, type, project_id):
        """Remove private volume type access from a project.

        :param type: The value can be either the ID of a type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
        :param str project_id: The ID of the project. Volume Type access to
            be removed to this project ID.

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.remove_private_access(self, project_id)

    # ========== Volumes ==========

    def get_volume(self, volume):
        """Get a single volume

        :param volume: The value can be the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.

        :returns: One :class:`~openstack.block_storage.v2.volume.Volume`
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

        :param volume: The name or ID a volume
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume does not exist.
        :param bool details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause an object with
            additional attributes to be returned.
        :param bool all_projects: When set to ``True``, search for volume by
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
            a :class:`~openstack.block_storage.v2.volume.Volume`,
            comprised of the properties on the Volume class.

        :returns: The results of volume creation
        :rtype: :class:`~openstack.block_storage.v2.volume.Volume`
        """
        return self._create(_volume.Volume, **attrs)

    def delete_volume(
        self, volume, ignore_missing=True, *, force=False, cascade=False
    ):
        """Delete a volume

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the volume does not exist.  When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            volume.
        :param bool force: Whether to try forcing volume deletion.
        :param bool cascade: Whether to remove any snapshots along with the
            volume.

        :returns: ``None``
        """
        volume = self._get_resource(_volume.Volume, volume)
        try:
            if not force:
                volume.delete(self, params={'cascade': cascade})
            else:
                volume.force_delete(self)
        except exceptions.NotFoundException:
            if ignore_missing:
                return None
            raise

    # ========== Volume actions ==========

    def extend_volume(self, volume, size):
        """Extend a volume

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param size: New volume size

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.extend(self, size)

    def set_volume_readonly(self, volume, readonly=True):
        """Set a volume's read-only flag.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param bool readonly: Whether the volume should be a read-only volume
            or not.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.set_readonly(self, readonly)

    def retype_volume(self, volume, new_type, migration_policy="never"):
        """Retype the volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param new_type: The new volume type that volume is changed with.
            The value can be either the ID of the volume type or a
            :class:`~openstack.block_storage.v2.type.Type` instance.
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
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param bool bootable: Specifies whether the volume should be bootable
            or not.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.set_bootable_status(self, bootable)

    def set_volume_image_metadata(self, volume, **metadata):
        """Update image metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.
        :param kwargs metadata: Key/value pairs to be updated in the volume's
            image metadata. No other metadata is modified by this call.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.set_image_metadata(self, metadata=metadata)

    def delete_volume_image_metadata(self, volume, keys=None):
        """Delete metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.
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
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param str status: The new volume status.
        :param str attach_status: The new volume attach status.
        :param str migration_status: The new volume migration status (admin
            only).

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.reset_status(self, status, attach_status, migration_status)

    def attach_volume(self, volume, mountpoint, instance=None, host_name=None):
        """Attaches a volume to a server.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
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
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param str attachment: The ID of the attachment.
        :param bool force: Whether to force volume detach (Rolls back an
            unsuccessful detach operation after you disconnect the volume.)
        :param dict connector: The connector object.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.detach(self, attachment, force, connector)

    def unmanage_volume(self, volume):
        """Removes a volume from Block Storage management without removing the
            back-end storage object that is associated with it.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.unmanage(self)

    def migrate_volume(
        self, volume, host=None, force_host_copy=False, lock_volume=False
    ):
        """Migrates a volume to the specified host.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param str host: The target host for the volume migration. Host
            format is host@backend.
        :param bool force_host_copy: If false (the default), rely on the volume
            backend driver to perform the migration, which might be optimized.
            If true, or the volume driver fails to migrate the volume itself,
            a generic host-based migration is performed.
        :param bool lock_volume: If true, migrating an available volume will
            change its status to maintenance preventing other operations from
            being performed on the volume such as attach, detach, retype, etc.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.migrate(self, host, force_host_copy, lock_volume)

    def complete_volume_migration(self, volume, new_volume, error=False):
        """Complete the migration of a volume.

        :param volume: The value can be either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume` instance.
        :param str new_volume: The UUID of the new volume.
        :param bool error: Used to indicate if an error has occured elsewhere
            that requires clean up.

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.complete_migration(self, new_volume, error)

    # ========== Backend pools ==========

    def backend_pools(self, **query):
        """Returns a generator of cinder Back-end storage pools

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns A generator of cinder Back-end storage pools objects
        """
        return self._list(_stats.Pools, **query)

    # ========== Backups ==========

    def backups(self, details=True, **query):
        """Retrieve a generator of backups

        :param bool details: When set to ``False`` no additional details will
            be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
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

        :returns: A generator of backup objects.
        """
        base_path = '/backups/detail' if details else None
        return self._list(_backup.Backup, base_path=base_path, **query)

    def get_backup(self, backup):
        """Get a backup

        :param backup: The value can be the ID of a backup
            or a :class:`~openstack.block_storage.v2.backup.Backup`
            instance.

        :returns: Backup instance
        :rtype: :class:`~openstack.block_storage.v2.backup.Backup`
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

    def create_backup(self, **attrs):
        """Create a new Backup from attributes with native API

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.backup.Backup`
            comprised of the properties on the Backup class.

        :returns: The results of Backup creation
        :rtype: :class:`~openstack.block_storage.v2.backup.Backup`
        """
        return self._create(_backup.Backup, **attrs)

    def delete_backup(self, backup, ignore_missing=True, force=False):
        """Delete a CloudBackup

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v2.backup.Backup` instance
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

    # ========== Backup actions ==========

    def restore_backup(self, backup, volume_id, name):
        """Restore a Backup to volume

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v2.backup.Backup` instance
        :param volume_id: The ID of the volume to restore the backup to.
        :param name: The name for new volume creation to restore.

        :returns: Updated backup instance
        :rtype: :class:`~openstack.block_storage.v2.backup.Backup`
        """
        backup = self._get_resource(_backup.Backup, backup)
        return backup.restore(self, volume_id=volume_id, name=name)

    def reset_backup_status(self, backup, status):
        """Reset status of the backup

        :param backup: The value can be either the ID of a backup or a
            :class:`~openstack.block_storage.v2.backup.Backup` instance.
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

    # ========== Limits ==========

    def get_limits(self, project=None):
        """Retrieves limits

        :param project: A project to get limits for. The value can be either
            the ID of a project or an
            :class:`~openstack.identity.v2.project.Project` instance.
        :returns: A Limits object, including both
            :class:`~openstack.block_storage.v2.limits.AbsoluteLimit` and
            :class:`~openstack.block_storage.v2.limits.RateLimit`
        :rtype: :class:`~openstack.block_storage.v2.limits.Limits`
        """
        if project:
            return self._get(
                _limits.Limits,
                requires_id=False,
                project_id=resource.Resource._get_id(project),
            )
        return self._get(_limits.Limits, requires_id=False)

    # ========== Capabilities ==========

    def get_capabilities(self, host):
        """Get a backend's capabilites

        :param host: Specified backend to obtain volume stats and properties.

        :returns: One :class:
            `~openstack.block_storage.v2.capabilites.Capabilities` instance.
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(_capabilities.Capabilities, host)

    # ========== Quota class sets ==========

    def get_quota_class_set(self, quota_class_set='default'):
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

    def update_quota_class_set(self, quota_class_set, **attrs):
        """Update a QuotaClassSet.

        Only one quota class is permitted, ``default``.

        :param quota_class_set: Either the ID of a quota class set (only
            ``default`` is supported) or a
            :class:`~openstack.block_storage.v2.quota_class_set.QuotaClassSet`
            instance.
        :param attrs: The attributes to update on the QuotaClassSet represented
            by ``quota_class_set``.

        :returns: The updated QuotaSet
        :rtype: :class:`~openstack.block_storage.v2.quota_set.QuotaSet`
        """
        return self._update(
            _quota_class_set.QuotaClassSet, quota_class_set, **attrs
        )

    # ========== Quota sets ==========

    def get_quota_set(self, project, usage=False, **query):
        """Show QuotaSet information for the project

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be retrieved
        :param bool usage: When set to ``True`` quota usage and reservations
            would be filled.
        :param dict query: Additional query parameters to use.

        :returns: One :class:`~openstack.block_storage.v2.quota_set.QuotaSet`
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

        :returns: One :class:`~openstack.block_storage.v2.quota_set.QuotaSet`
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

        if not query:
            query = {}
        return res.delete(self, **query)

    def update_quota_set(self, project, **attrs):
        """Update a QuotaSet.

        :param project: ID or instance of
            :class:`~openstack.identity.project.Project` of the project for
            which the quota should be reset.
        :param attrs: The attributes to update on the QuotaSet represented
            by ``quota_set``.

        :returns: The updated QuotaSet
        :rtype: :class:`~openstack.block_storage.v2.quota_set.QuotaSet`
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

    # ========== Services ==========
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

        :returns: One: class:`~openstack.block_storage.v2.service.Service` or None
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
        :rtype: class: `~openstack.block_storage.v2.service.Service`
        """
        return self._list(_service.Service, **query)

    def enable_service(
        self,
        service: ty.Union[str, _service.Service],
    ) -> _service.Service:
        """Enable a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v2.service.Service` instance.

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v2.service.Service`
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
            :class:`~openstack.block_storage.v2.service.Service` instance
        :param str reason: The reason to disable a service

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v2.service.Service`
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.disable(self, reason=reason)

    def thaw_service(
        self,
        service: ty.Union[str, _service.Service],
    ) -> _service.Service:
        """Thaw a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v2.service.Service` instance

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v2.service.Service`
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.thaw(self)

    def freeze_service(
        self,
        service: ty.Union[str, _service.Service],
    ) -> _service.Service:
        """Freeze a service

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v2.service.Service` instance

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v2.service.Service`
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.freeze(self)

    def failover_service(
        self,
        service: ty.Union[str, _service.Service],
        *,
        backend_id: ty.Optional[str] = None,
    ) -> _service.Service:
        """Failover a service

        Only applies to replicating cinder-volume services.

        :param service: Either the ID of a service or a
            :class:`~openstack.block_storage.v2.service.Service` instance

        :returns: Updated service instance
        :rtype: class: `~openstack.block_storage.v2.service.Service`
        """
        service_obj = self._get_resource(_service.Service, service)
        return service_obj.failover(self, backend_id=backend_id)

    # ========== Volume metadata ==========

    def get_volume_metadata(self, volume):
        """Return a dictionary of metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.

        :returns: A :class:`~openstack.block_storage.v2.volume.Volume` with the
            volume's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v2.volume.Volume`
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.fetch_metadata(self)

    def set_volume_metadata(self, volume, **metadata):
        """Update metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.
        :param kwargs metadata: Key/value pairs to be updated in the volume's
            metadata. No other metadata is modified by this call. All keys
            and values are stored as Unicode.

        :returns: A :class:`~openstack.block_storage.v2.volume.Volume` with the
            volume's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v2.volume.Volume`
        """
        volume = self._get_resource(_volume.Volume, volume)
        return volume.set_metadata(self, metadata=metadata)

    def delete_volume_metadata(self, volume, keys=None):
        """Delete metadata for a volume

        :param volume: Either the ID of a volume or a
            :class:`~openstack.block_storage.v2.volume.Volume`.
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

    # ========== Snapshot metadata ==========

    def get_snapshot_metadata(self, snapshot):
        """Return a dictionary of metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`.

        :returns: A
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` with the
            snapshot's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v2.snapshot.Snapshot`
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        return snapshot.fetch_metadata(self)

    def set_snapshot_metadata(self, snapshot, **metadata):
        """Update metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`.
        :param kwargs metadata: Key/value pairs to be updated in the snapshot's
            metadata. No other metadata is modified by this call. All keys
            and values are stored as Unicode.

        :returns: A
            :class:`~openstack.block_storage.v2.snapshot.Snapshot` with the
            snapshot's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.block_storage.v2.snapshot.Snapshot`
        """
        snapshot = self._get_resource(_snapshot.Snapshot, snapshot)
        return snapshot.set_metadata(self, metadata=metadata)

    def delete_snapshot_metadata(self, snapshot, keys=None):
        """Delete metadata for a snapshot

        :param snapshot: Either the ID of a snapshot or a
            :class:`~openstack.block_storage.v2.snapshot.Snapshot`.
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

    # ========== Transfers ==========

    def create_transfer(self, **attrs):
        """Create a new Transfer record

        :param volume_id: The value is ID of the volume.
        :param name: The value is name of the transfer
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.transfer.Transfer`
            comprised of the properties on the Transfer class.
        :returns: The results of Transfer creation
        :rtype: :class:`~openstack.block_storage.v2.transfer.Transfer`
        """
        return self._create(_transfer.Transfer, **attrs)

    def delete_transfer(self, transfer, ignore_missing=True):
        """Delete a volume transfer

        :param transfer: The value can be either the ID of a transfer or a
            :class:`~openstack.block_storage.v2.transfer.Transfer`` instance.
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

    def get_transfer(self, transfer):
        """Get a single transfer

        :param transfer: The value can be the ID of a transfer or a
            :class:`~openstack.block_storage.v2.transfer.Transfer`
            instance.

        :returns: One :class:`~openstack.block_storage.v2.transfer.Transfer`
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
        if details:
            base_path = utils.urljoin(base_path, 'detail')
        return self._list(_transfer.Transfer, base_path=base_path, **query)

    def accept_transfer(self, transfer_id, auth_key):
        """Accept a Transfer

        :param transfer_id: The value can be the ID of a transfer or a
            :class:`~openstack.block_storage.v2.transfer.Transfer`
            instance.
        :param auth_key: The key to authenticate volume transfer.

        :returns: The results of Transfer creation
        :rtype: :class:`~openstack.block_storage.v2.transfer.Transfer`
        """
        transfer = self._get_resource(_transfer.Transfer, transfer_id)
        return transfer.accept(self, auth_key=auth_key)

    # ========== Utilities ==========

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
