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

from openstack.block_storage import _base_proxy
from openstack.block_storage.v3 import availability_zone
from openstack.block_storage.v3 import backup as _backup
from openstack.block_storage.v3 import snapshot as _snapshot
from openstack.block_storage.v3 import stats as _stats
from openstack.block_storage.v3 import type as _type
from openstack.block_storage.v3 import volume as _volume
from openstack import exceptions
from openstack import resource


class Proxy(_base_proxy.BaseBlockStorageProxy):

    def get_snapshot(self, snapshot):
        """Get a single snapshot

        :param snapshot: The value can be the ID of a snapshot or a
                         :class:`~openstack.volume.v3.snapshot.Snapshot`
                         instance.

        :returns: One :class:`~openstack.volume.v3.snapshot.Snapshot`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_snapshot.Snapshot, snapshot)

    def find_snapshot(self, name_or_id, ignore_missing=True, **attrs):
        """Find a single snapshot

        :param snapshot: The name or ID a snapshot
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the snapshot does not exist.

        :returns: One :class:`~openstack.volume.v3.snapshot.Snapshot`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._find(_snapshot.Snapshot, name_or_id,
                          ignore_missing=ignore_missing)

    def snapshots(self, details=True, **query):
        """Retrieve a generator of snapshots

        :param bool details: When set to ``False``
            :class:`~openstack.block_storage.v3.snapshot.Snapshot`
            objects will be returned. The default, ``True``, will cause
            more attributes to be returned.
        :param kwargs query: Optional query parameters to be sent to limit
            the snapshots being returned.  Available parameters include:

            * name: Name of the snapshot as a string.
            * all_projects: Whether return the snapshots in all projects.
            * project_id: Filter the snapshots by project.
            * volume_id: volume id of a snapshot.
            * status: Value of the status of the snapshot so that you can
                      filter on "available" for example.

        :returns: A generator of snapshot objects.
        """
        base_path = '/snapshots/detail' if details else None
        return self._list(_snapshot.Snapshot, base_path=base_path, **query)

    def create_snapshot(self, **attrs):
        """Create a new snapshot from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.volume.v3.snapshot.Snapshot`,
                           comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        :rtype: :class:`~openstack.volume.v3.snapshot.Snapshot`
        """
        return self._create(_snapshot.Snapshot, **attrs)

    def delete_snapshot(self, snapshot, ignore_missing=True):
        """Delete a snapshot

        :param snapshot: The value can be either the ID of a snapshot or a
                         :class:`~openstack.volume.v3.snapshot.Snapshot`
                         instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the snapshot does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent snapshot.

        :returns: ``None``
        """
        self._delete(_snapshot.Snapshot, snapshot,
                     ignore_missing=ignore_missing)

    def get_type(self, type):
        """Get a single type

        :param type: The value can be the ID of a type or a
                     :class:`~openstack.volume.v3.type.Type` instance.

        :returns: One :class:`~openstack.volume.v3.type.Type`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_type.Type, type)

    def find_type(self, name_or_id, ignore_missing=True, **attrs):
        """Find a single volume type

        :param snapshot: The name or ID a volume type
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the type does not exist.

        :returns: One :class:`~openstack.volume.v3.type.Type`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._find(_type.Type, name_or_id,
                          ignore_missing=ignore_missing)

    def types(self, **query):
        """Retrieve a generator of volume types

        :returns: A generator of volume type objects.
        """
        return self._list(_type.Type, **query)

    def create_type(self, **attrs):
        """Create a new type from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.volume.v3.type.Type`,
                           comprised of the properties on the Type class.

        :returns: The results of type creation
        :rtype: :class:`~openstack.volume.v3.type.Type`
        """
        return self._create(_type.Type, **attrs)

    def delete_type(self, type, ignore_missing=True):
        """Delete a type

        :param type: The value can be either the ID of a type or a
                     :class:`~openstack.volume.v3.type.Type` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the type does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent type.

        :returns: ``None``
        """
        self._delete(_type.Type, type, ignore_missing=ignore_missing)

    def update_type(self, type, **attrs):
        """Update a type

        :param type: The value can be either the ID of a type or a
                     :class:`~openstack.volume.v3.type.Type` instance.
        :param dict attrs: The attributes to update on the type
                           represented by ``value``.

        :returns: The updated type
        :rtype: :class:`~openstack.volume.v3.type.Type`
        """
        return self._update(_type.Type, type, **attrs)

    def update_type_extra_specs(self, type, **attrs):
        """Update the extra_specs for a type

        :param type: The value can be either the ID of a type or a
                     :class:`~openstack.volume.v3.type.Type` instance.
        :param dict attrs: The extra_spec attributes to update on the
                           type represented by ``value``.

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
                     :class:`~openstack.volume.v3.type.Type` instance.
        :param keys: The keys to delete

        :returns: ``None``
        """
        res = self._get_resource(_type.Type, type)
        return res.delete_extra_specs(self, keys)

    def get_type_encryption(self, volume_type_id):
        """Get the encryption details of a volume type

        :param volume_type_id: The value can be the ID of a type or a
                               :class:`~openstack.volume.v3.type.Type`
                               instance.

        :returns: One :class:`~openstack.volume.v3.type.TypeEncryption`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        volume_type = self._get_resource(_type.Type, volume_type_id)

        return self._get(_type.TypeEncryption,
                         volume_type_id=volume_type.id,
                         requires_id=False)

    def create_type_encryption(self, volume_type, **attrs):
        """Create new type encryption from attributes

        :param volume_type: The value can be the ID of a type or a
                            :class:`~openstack.volume.v3.type.Type`
                            instance.

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.volume.v3.type.TypeEncryption`,
                           comprised of the properties on the TypeEncryption
                           class.

        :returns: The results of type encryption creation
        :rtype: :class:`~openstack.volume.v3.type.TypeEncryption`
        """
        volume_type = self._get_resource(_type.Type, volume_type)

        return self._create(_type.TypeEncryption,
                            volume_type_id=volume_type.id, **attrs)

    def delete_type_encryption(self, encryption=None,
                               volume_type=None, ignore_missing=True):
        """Delete type encryption attributes

        :param encryption: The value can be None or a
                           :class:`~openstack.volume.v3.type.TypeEncryption`
                           instance.  If encryption_id is None then
                           volume_type_id must be specified.

        :param volume_type: The value can be the ID of a type or a
                            :class:`~openstack.volume.v3.type.Type`
                            instance.  Required if encryption_id is None.

        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the type does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent type.

        :returns: ``None``
        """

        if volume_type:
            volume_type = self._get_resource(_type.Type, volume_type)
            encryption = self._get(_type.TypeEncryption,
                                   volume_type=volume_type.id,
                                   requires_id=False)

        self._delete(_type.TypeEncryption, encryption,
                     ignore_missing=ignore_missing)

    def update_type_encryption(self, encryption=None,
                               volume_type=None, **attrs):
        """Update a type
        :param encryption: The value can be None or a
                           :class:`~openstack.volume.v3.type.TypeEncryption`
                           instance.  If encryption_id is None then
                           volume_type_id must be specified.

        :param volume_type: The value can be the ID of a type or a
                            :class:`~openstack.volume.v3.type.Type`
                            instance.  Required if encryption_id is None.
        :param dict attrs: The attributes to update on the type encryption.

        :returns: The updated type encryption
        :rtype: :class:`~openstack.volume.v3.type.TypeEncryption`
        """

        if volume_type:
            volume_type = self._get_resource(_type.Type, volume_type)
            encryption = self._get(_type.TypeEncryption,
                                   volume_type=volume_type.id,
                                   requires_id=False)

        return self._update(_type.TypeEncryption, encryption, **attrs)

    def get_volume(self, volume):
        """Get a single volume

        :param volume: The value can be the ID of a volume or a
                       :class:`~openstack.volume.v3.volume.Volume` instance.

        :returns: One :class:`~openstack.volume.v3.volume.Volume`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_volume.Volume, volume)

    def find_volume(self, name_or_id, ignore_missing=True, **attrs):
        """Find a single volume

        :param snapshot: The name or ID a volume
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the volume does not exist.

        :returns: One :class:`~openstack.volume.v3.volume.Volume`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._find(_volume.Volume, name_or_id,
                          ignore_missing=ignore_missing)

    def volumes(self, details=True, **query):
        """Retrieve a generator of volumes

        :param bool details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
        :param kwargs query: Optional query parameters to be sent to limit
            the volumes being returned.  Available parameters include:

            * name: Name of the volume as a string.
            * all_projects: Whether return the volumes in all projects
            * status: Value of the status of the volume so that you can filter
                    on "available" for example.

        :returns: A generator of volume objects.
        """
        base_path = '/volumes/detail' if details else None
        return self._list(_volume.Volume, base_path=base_path, **query)

    def create_volume(self, **attrs):
        """Create a new volume from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.volume.v3.volume.Volume`,
                           comprised of the properties on the Volume class.

        :returns: The results of volume creation
        :rtype: :class:`~openstack.volume.v3.volume.Volume`
        """
        return self._create(_volume.Volume, **attrs)

    def delete_volume(self, volume, ignore_missing=True):
        """Delete a volume

        :param volume: The value can be either the ID of a volume or a
                       :class:`~openstack.volume.v3.volume.Volume` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the volume does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent volume.

        :returns: ``None``
        """
        self._delete(_volume.Volume, volume, ignore_missing=ignore_missing)

    def extend_volume(self, volume, size):
        """Extend a volume

        :param volume: The value can be either the ID of a volume or a
                       :class:`~openstack.volume.v3.volume.Volume` instance.
        :param size: New volume size

        :returns: None
        """
        volume = self._get_resource(_volume.Volume, volume)
        volume.extend(self, size)

    def backend_pools(self):
        """Returns a generator of cinder Back-end storage pools

        :returns A generator of cinder Back-end storage pools objects
        """
        return self._list(_stats.Pools)

    def backups(self, details=True, **query):
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

    def find_backup(self, name_or_id, ignore_missing=True, **attrs):
        """Find a single backup

        :param snapshot: The name or ID a backup
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the backup does not exist.

        :returns: One :class:`~openstack.volume.v3.backup.Backup`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._find(_backup.Backup, name_or_id,
                          ignore_missing=ignore_missing)

    def create_backup(self, **attrs):
        """Create a new Backup from attributes with native API

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v3.backup.Backup`
            comprised of the properties on the Backup class.

        :returns: The results of Backup creation
        :rtype: :class:`~openstack.block_storage.v3.backup.Backup`
        """
        return self._create(_backup.Backup, **attrs)

    def delete_backup(self, backup, ignore_missing=True):
        """Delete a CloudBackup

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v3.backup.Backup` instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: ``None``
        """
        self._delete(_backup.Backup, backup,
                     ignore_missing=ignore_missing)

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

    def availability_zones(self):
        """Return a generator of availability zones

        :returns: A generator of availability zone
        :rtype: :class:`~openstack.block_storage.v3.availability_zone.\
                        AvailabilityZone`
        """

        return self._list(availability_zone.AvailabilityZone)

    def wait_for_status(self, res, status='ACTIVE', failures=None,
                        interval=2, wait=120):
        """Wait for a resource to be in a particular status.

        :param res: The resource to wait on to reach the specified status.
                    The resource must have a ``status`` attribute.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
                 has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
                ``status`` attribute.
        """
        failures = ['Error'] if failures is None else failures
        return resource.wait_for_status(
            self, res, status, failures, interval, wait)

    def wait_for_delete(self, res, interval=2, wait=120):
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait)

    def _get_cleanup_dependencies(self):
        return {
            'block_storage': {
                'before': []
            }
        }

    def _service_cleanup(self, dry_run=True, client_status_queue=None,
                         identified_resources=None,
                         filters=None, resource_evaluation_fn=None):
        backups = []
        for obj in self.backups(details=False):
            need_delete = self._service_cleanup_del_res(
                self.delete_backup,
                obj,
                dry_run=dry_run,
                client_status_queue=client_status_queue,
                identified_resources=identified_resources,
                filters=filters,
                resource_evaluation_fn=resource_evaluation_fn)
            if not dry_run and need_delete:
                backups.append(obj)

        # Before deleting snapshots need to wait for backups to be deleted
        for obj in backups:
            try:
                self.wait_for_delete(obj)
            except exceptions.SDKException:
                # Well, did our best, still try further
                pass

        snapshots = []
        for obj in self.snapshots(details=False):
            need_delete = self._service_cleanup_del_res(
                self.delete_snapshot,
                obj,
                dry_run=dry_run,
                client_status_queue=client_status_queue,
                identified_resources=identified_resources,
                filters=filters,
                resource_evaluation_fn=resource_evaluation_fn)
            if not dry_run and need_delete:
                snapshots.append(obj)

        # Before deleting volumes need to wait for snapshots to be deleted
        for obj in snapshots:
            try:
                self.wait_for_delete(obj)
            except exceptions.SDKException:
                # Well, did our best, still try further
                pass

        for obj in self.volumes(details=True):
            self._service_cleanup_del_res(
                self.delete_volume,
                obj,
                dry_run=dry_run,
                client_status_queue=client_status_queue,
                identified_resources=identified_resources,
                filters=filters,
                resource_evaluation_fn=resource_evaluation_fn)
