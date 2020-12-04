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
from openstack.block_storage.v2 import backup as _backup
from openstack.block_storage.v2 import snapshot as _snapshot
from openstack.block_storage.v2 import stats as _stats
from openstack.block_storage.v2 import type as _type
from openstack.block_storage.v2 import volume as _volume
from openstack import resource


class Proxy(_base_proxy.BaseBlockStorageProxy):

    def get_snapshot(self, snapshot):
        """Get a single snapshot

        :param snapshot: The value can be the ID of a snapshot or a
                         :class:`~openstack.volume.v2.snapshot.Snapshot`
                         instance.

        :returns: One :class:`~openstack.volume.v2.snapshot.Snapshot`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_snapshot.Snapshot, snapshot)

    def snapshots(self, details=True, **query):
        """Retrieve a generator of snapshots

        :param bool details: When set to ``False``
                    :class:`~openstack.block_storage.v2.snapshot.Snapshot`
                    objects will be returned. The default, ``True``, will cause
                    :class:`~openstack.block_storage.v2.snapshot.SnapshotDetail`
                    objects to be returned.
        :param kwargs query: Optional query parameters to be sent to limit
            the snapshots being returned.  Available parameters include:

            * name: Name of the snapshot as a string.
            * all_projects: Whether return the snapshots in all projects.
            * volume_id: volume id of a snapshot.
            * status: Value of the status of the snapshot so that you can
                      filter on "available" for example.

        :returns: A generator of snapshot objects.
        """
        snapshot = _snapshot.SnapshotDetail if details else _snapshot.Snapshot
        return self._list(snapshot, **query)

    def create_snapshot(self, **attrs):
        """Create a new snapshot from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.volume.v2.snapshot.Snapshot`,
                           comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        :rtype: :class:`~openstack.volume.v2.snapshot.Snapshot`
        """
        return self._create(_snapshot.Snapshot, **attrs)

    def delete_snapshot(self, snapshot, ignore_missing=True):
        """Delete a snapshot

        :param snapshot: The value can be either the ID of a snapshot or a
                         :class:`~openstack.volume.v2.snapshot.Snapshot`
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
                     :class:`~openstack.volume.v2.type.Type` instance.

        :returns: One :class:`~openstack.volume.v2.type.Type`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_type.Type, type)

    def types(self, **query):
        """Retrieve a generator of volume types

        :returns: A generator of volume type objects.
        """
        return self._list(_type.Type, **query)

    def create_type(self, **attrs):
        """Create a new type from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.volume.v2.type.Type`,
                           comprised of the properties on the Type class.

        :returns: The results of type creation
        :rtype: :class:`~openstack.volume.v2.type.Type`
        """
        return self._create(_type.Type, **attrs)

    def delete_type(self, type, ignore_missing=True):
        """Delete a type

        :param type: The value can be either the ID of a type or a
                     :class:`~openstack.volume.v2.type.Type` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the type does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent type.

        :returns: ``None``
        """
        self._delete(_type.Type, type, ignore_missing=ignore_missing)

    def get_volume(self, volume):
        """Get a single volume

        :param volume: The value can be the ID of a volume or a
                       :class:`~openstack.volume.v2.volume.Volume` instance.

        :returns: One :class:`~openstack.volume.v2.volume.Volume`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_volume.Volume, volume)

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
                           a :class:`~openstack.volume.v2.volume.Volume`,
                           comprised of the properties on the Volume class.

        :returns: The results of volume creation
        :rtype: :class:`~openstack.volume.v2.volume.Volume`
        """
        return self._create(_volume.Volume, **attrs)

    def delete_volume(self, volume, ignore_missing=True):
        """Delete a volume

        :param volume: The value can be either the ID of a volume or a
                       :class:`~openstack.volume.v2.volume.Volume` instance.
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
                       :class:`~openstack.volume.v2.volume.Volume` instance.
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

    def create_backup(self, **attrs):
        """Create a new Backup from attributes with native API

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.block_storage.v2.backup.Backup`
            comprised of the properties on the Backup class.

        :returns: The results of Backup creation
        :rtype: :class:`~openstack.block_storage.v2.backup.Backup`
        """
        return self._create(_backup.Backup, **attrs)

    def delete_backup(self, backup, ignore_missing=True):
        """Delete a CloudBackup

        :param backup: The value can be the ID of a backup or a
            :class:`~openstack.block_storage.v2.backup.Backup` instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: ``None``
        """
        self._delete(_backup.Backup, backup,
                     ignore_missing=ignore_missing)

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
