# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import warnings

from openstack.cloud import _utils
from openstack.cloud import openstackcloud
from openstack import exceptions
from openstack import resource
from openstack import warnings as os_warnings


class BlockStorageCloudMixin(openstackcloud._OpenStackCloudMixin):
    def list_volumes(self, cache=None):
        """List all available volumes.

        :param cache: **DEPRECATED** This parameter no longer does anything.
        :returns: A list of volume ``Volume`` objects.
        """
        if cache is not None:
            warnings.warn(
                "the 'cache' argument is deprecated and no longer does "
                "anything; consider removing it from calls",
                os_warnings.RemovedInSDK50Warning,
            )
        return list(self.block_storage.volumes())

    def list_volume_types(self, get_extra=None):
        """List all available volume types.

        :param get_extra: **DEPRECATED** This parameter no longer does
            anything.
        :returns: A list of volume ``Type`` objects.
        """
        if get_extra is not None:
            warnings.warn(
                "the 'get_extra' argument is deprecated and no longer does "
                "anything; consider removing it from calls",
                os_warnings.RemovedInSDK50Warning,
            )
        return list(self.block_storage.types())

    # TODO(stephenfin): Remove 'filters' in a future major version
    def get_volume(self, name_or_id, filters=None):
        """Get a volume by name or ID.

        :param name_or_id: Name or unique ID of the volume.
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``Volume`` object if found, else None.
        """
        if filters is not None:
            warnings.warn(
                "The 'filters' argument is deprecated; use "
                "'search_volumes' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_volumes(name_or_id, filters)
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

            return entities[0]

        return self.block_storage.find_volume(name_or_id)

    def get_volume_by_id(self, id):
        """Get a volume by ID

        :param id: ID of the volume.
        :returns: A volume ``Volume`` object if found, else None.
        """
        return self.block_storage.get_volume(id)

    # TODO(stephenfin): Remove 'filters' in a future major version
    def get_volume_type(self, name_or_id, filters=None):
        """Get a volume type by name or ID.

        :param name_or_id: Name or unique ID of the volume type.
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``Type`` object if found, else None.
        """
        if filters is not None:
            warnings.warn(
                "The 'filters' argument is deprecated; use "
                "'search_volume_types' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_volume_types(name_or_id, filters)
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

            return entities[0]

        return self.block_storage.find_type(name_or_id)

    def create_volume(
        self,
        size,
        wait=True,
        timeout=None,
        image=None,
        bootable=None,
        **kwargs,
    ):
        """Create a volume.

        :param size: Size, in GB of the volume to create.
        :param wait: If true, waits for volume to be created.
        :param timeout: Seconds to wait for volume creation. None is forever.
        :param image: (optional) Image name, ID or object from which to create
            the volume
        :param bootable: (optional) Make this volume bootable. If set, wait
            will also be set to true.
        :param kwargs: Keyword arguments as expected for cinder client.

        :returns: The created volume ``Volume`` object.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if wait time
            exceeded.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if bootable is not None:
            wait = True

        if image:
            if isinstance(image, dict):
                if not isinstance(image, resource.Resource):
                    warnings.warn(
                        "Support for passing image as a raw dict has "
                        "been deprecated for removal. Consider passing a "
                        "string name or ID or an Image object instead.",
                        os_warnings.RemovedInSDK60Warning,
                    )
                kwargs['imageRef'] = image['id']
            else:  # object
                image_obj = self.image.find_image(image, ignore_missing=False)
                kwargs['imageRef'] = image_obj['id']
        kwargs = self._get_volume_kwargs(kwargs)
        kwargs['size'] = size

        volume = self.block_storage.create_volume(**kwargs)

        if volume['status'] == 'error':
            raise exceptions.SDKException("Error in creating volume")

        if wait:
            self.block_storage.wait_for_status(volume, wait=timeout)
            if bootable:
                self.block_storage.set_volume_bootable_status(volume, True)

        return volume

    def update_volume(self, name_or_id, **kwargs):
        """Update a volume.

        :param name_or_id: Name or unique ID of the volume.
        :param kwargs: Volume attributes to be updated.
        :returns: The updated volume ``Volume`` object.
        """
        kwargs = self._get_volume_kwargs(kwargs)

        volume = self.get_volume(name_or_id)
        if not volume:
            raise exceptions.SDKException(f"Volume {name_or_id} not found.")

        volume = self.block_storage.update_volume(volume, **kwargs)

        return volume

    def set_volume_bootable(self, name_or_id, bootable=True):
        """Set a volume's bootable flag.

        :param name_or_id: Name or unique ID of the volume.
        :param bool bootable: Whether the volume should be bootable.
            (Defaults to True)

        :returns: None
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if wait time
            exceeded.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """

        volume = self.get_volume(name_or_id)

        if not volume:
            raise exceptions.SDKException(
                f"Volume {name_or_id} does not exist"
            )

        self.block_storage.set_volume_bootable_status(volume, bootable)

    def delete_volume(
        self,
        name_or_id=None,
        wait=True,
        timeout=None,
        force=False,
    ):
        """Delete a volume.

        :param name_or_id: Name or unique ID of the volume.
        :param wait: If true, waits for volume to be deleted.
        :param timeout: Seconds to wait for volume deletion. None is forever.
        :param force: Force delete volume even if the volume is in deleting
            or error_deleting state.

        :returns: True if deletion was successful, else False.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if wait time
            exceeded.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        volume = self.block_storage.find_volume(
            name_or_id, ignore_missing=True
        )
        if not volume:
            self.log.debug(
                "Volume %(name_or_id)s does not exist",
                {'name_or_id': name_or_id},
                exc_info=True,
            )
            return False
        try:
            self.block_storage.delete_volume(volume, force=force)
        except exceptions.SDKException:
            self.log.exception("error in deleting volume")
            raise

        if wait:
            self.block_storage.wait_for_delete(volume, wait=timeout)

        return True

    def get_volumes(self, server, cache=None):
        """Get volumes for a server.

        :param server: The server to fetch volumes for.
        :param cache: **DEPRECATED** This parameter no longer does anything.
        :returns: A list of volume ``Volume`` objects.
        """
        if cache is not None:
            warnings.warn(
                "the 'cache' argument is deprecated and no longer does "
                "anything; consider removing it from calls",
                os_warnings.RemovedInSDK50Warning,
            )
            # avoid spamming warnings
            cache = None

        volumes = []
        for volume in self.list_volumes(cache=cache):
            for attach in volume['attachments']:
                if attach['server_id'] == server['id']:
                    volumes.append(volume)
        return volumes

    def get_volume_limits(self, name_or_id=None):
        """Get volume limits for the current project

        :param name_or_id: (optional) Project name or ID to get limits for
            if different from the current project
        :returns: The volume ``Limits`` object if found, else None.
        """
        params = {}
        if name_or_id:
            project = self.identity.find_project(
                name_or_id, ignore_missing=False
            )
            params['project'] = project
        return self.block_storage.get_limits(**params)

    def get_volume_id(self, name_or_id):
        """Get ID of a volume.

        :param name_or_id: Name or unique ID of the volume.
        :returns: The ID of the volume if found, else None.
        """
        volume = self.get_volume(name_or_id)
        if volume:
            return volume['id']
        return None

    def volume_exists(self, name_or_id):
        """Check if a volume exists.

        :param name_or_id: Name or unique ID of the volume.
        :returns: True if the volume exists, else False.
        """
        return self.get_volume(name_or_id) is not None

    def get_volume_attach_device(self, volume, server_id):
        """Return the device name a volume is attached to for a server.

        This can also be used to verify if a volume is attached to
        a particular server.

        :param volume: The volume to fetch the device name from.
        :param server_id: ID of server to check.
        :returns: Device name if attached, None if volume is not attached.
        """
        for attach in volume['attachments']:
            if server_id == attach['server_id']:
                return attach['device']
        return None

    def detach_volume(self, server, volume, wait=True, timeout=None):
        """Detach a volume from a server.

        :param server: The server dict to detach from.
        :param volume: The volume dict to detach.
        :param wait: If true, waits for volume to be detached.
        :param timeout: Seconds to wait for volume detachment. None is forever.

        :returns: None
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if wait time
            exceeded.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        self.compute.delete_volume_attachment(
            server=server['id'],
            volume=volume['id'],
            ignore_missing=False,
        )
        if wait:
            vol = self.get_volume(volume['id'])
            self.block_storage.wait_for_status(vol)

    def attach_volume(
        self,
        server,
        volume,
        device=None,
        wait=True,
        timeout=None,
    ):
        """Attach a volume to a server.

        This will attach a volume, described by the passed in volume
        dict (as returned by get_volume()), to the server described by
        the passed in server dict (as returned by get_server()) on the
        named device on the server.

        If the volume is already attached to the server, or generally not
        available, then an exception is raised. To re-attach to a server,
        but under a different device, the user must detach it first.

        :param server: The server dict to attach to.
        :param volume: The volume dict to attach.
        :param device: The device name where the volume will attach.
        :param wait: If true, waits for volume to be attached.
        :param timeout: Seconds to wait for volume attachment. None is forever.

        :returns: a volume attachment object.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if wait time
            exceeded.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        dev = self.get_volume_attach_device(volume, server['id'])
        if dev:
            raise exceptions.SDKException(
                "Volume {} already attached to server {} on device {}".format(
                    volume['id'], server['id'], dev
                )
            )

        if volume['status'] != 'available':
            raise exceptions.SDKException(
                "Volume {} is not available. Status is '{}'".format(
                    volume['id'], volume['status']
                )
            )

        payload = {}
        if device:
            payload['device'] = device
        attachment = self.compute.create_volume_attachment(
            server=server['id'],
            volume=volume['id'],
            **payload,
        )

        if wait:
            if not hasattr(volume, 'fetch'):
                # If we got volume as dict we need to re-fetch it to be able to
                # use wait_for_status.
                volume = self.block_storage.get_volume(volume['id'])
            self.block_storage.wait_for_status(volume, 'in-use', wait=timeout)
        return attachment

    def _get_volume_kwargs(self, kwargs):
        name = kwargs.pop('name', kwargs.pop('display_name', None))
        description = kwargs.pop(
            'description', kwargs.pop('display_description', None)
        )
        if name:
            kwargs['name'] = name
        if description:
            kwargs['description'] = description
        return kwargs

    @_utils.valid_kwargs(
        'name', 'display_name', 'description', 'display_description'
    )
    def create_volume_snapshot(
        self,
        volume_id,
        force=False,
        wait=True,
        timeout=None,
        **kwargs,
    ):
        """Create a volume.

        :param volume_id: the ID of the volume to snapshot.
        :param force: If set to True the snapshot will be created even if the
            volume is attached to an instance, if False it will not
        :param name: name of the snapshot, one will be generated if one is
            not provided
        :param description: description of the snapshot, one will be generated
            if one is not provided
        :param wait: If true, waits for volume snapshot to be created.
        :param timeout: Seconds to wait for volume snapshot creation. None is
            forever.

        :returns: The created volume ``Snapshot`` object.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if wait time
            exceeded.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        kwargs = self._get_volume_kwargs(kwargs)
        payload = {'volume_id': volume_id, 'force': force}
        payload.update(kwargs)
        snapshot = self.block_storage.create_snapshot(**payload)
        if wait:
            snapshot = self.block_storage.wait_for_status(
                snapshot, wait=timeout
            )

        return snapshot

    def get_volume_snapshot_by_id(self, snapshot_id):
        """Takes a snapshot_id and gets a dict of the snapshot
        that maches that ID.

        Note: This is more efficient than get_volume_snapshot.

        param: snapshot_id: ID of the volume snapshot.
        :returns: A volume ``Snapshot`` object if found, else None.
        """
        return self.block_storage.get_snapshot(snapshot_id)

    # TODO(stephenfin): Remove 'filters' in a future major version
    def get_volume_snapshot(self, name_or_id, filters=None):
        """Get a volume by name or ID.

        :param name_or_id: Name or unique ID of the volume snapshot.
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``Snapshot`` object if found, else None.
        """
        if filters is not None:
            warnings.warn(
                "The 'filters' argument is deprecated; use "
                "'search_volume_snapshots' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_volume_snapshots(name_or_id, filters)
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

            return entities[0]

        return self.block_storage.find_snapshot(name_or_id)

    def create_volume_backup(
        self,
        volume_id,
        name=None,
        description=None,
        force=False,
        wait=True,
        timeout=None,
        incremental=False,
        snapshot_id=None,
    ):
        """Create a volume backup.

        :param volume_id: the ID of the volume to backup.
        :param name: name of the backup, one will be generated if one is
            not provided
        :param description: description of the backup, one will be generated
            if one is not provided
        :param force: If set to True the backup will be created even if the
            volume is attached to an instance, if False it will not
        :param wait: If true, waits for volume backup to be created.
        :param timeout: Seconds to wait for volume backup creation. None is
            forever.
        :param incremental: If set to true, the backup will be incremental.
        :param snapshot_id: The UUID of the source snapshot to back up.

        :returns: The created volume ``Backup`` object.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if wait time
            exceeded.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        payload = {
            'name': name,
            'volume_id': volume_id,
            'description': description,
            'force': force,
            'is_incremental': incremental,
            'snapshot_id': snapshot_id,
        }

        backup = self.block_storage.create_backup(**payload)

        if wait:
            backup = self.block_storage.wait_for_status(backup, wait=timeout)

        return backup

    # TODO(stephenfin): Remove 'filters' in a future major version
    def get_volume_backup(self, name_or_id, filters=None):
        """Get a volume backup by name or ID.

        :param name_or_id: Name or unique ID of the volume backup.
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``Backup`` object if found, else None.
        """
        if filters is not None:
            warnings.warn(
                "The 'filters' argument is deprecated; use "
                "'search_volume_backups' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_volume_backups(name_or_id, filters)
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

            return entities[0]

        return self.block_storage.find_backup(name_or_id)

    def list_volume_snapshots(self, detailed=True, filters=None):
        """List all volume snapshots.

        :param detailed: Whether or not to add detailed additional information.
        :param filters: A dictionary of meta data to use for further filtering.
            Example::

                {
                    'name': 'my-volume-snapshot',
                    'volume_id': 'e126044c-7b4c-43be-a32a-c9cbbc9ddb56',
                    'all_tenants': 1,
                }

        :returns: A list of volume ``Snapshot`` objects.
        """
        if not filters:
            filters = {}
        return list(self.block_storage.snapshots(details=detailed, **filters))

    def list_volume_backups(self, detailed=True, filters=None):
        """List all volume backups.

        :param detailed: Whether or not to add detailed additional information.
        :param filters: A dictionary of meta data to use for further filtering.
            Example::

                {
                    'name': 'my-volume-backup',
                    'status': 'available',
                    'volume_id': 'e126044c-7b4c-43be-a32a-c9cbbc9ddb56',
                    'all_tenants': 1,
                }

        :returns: A list of volume ``Backup`` objects.
        """
        if not filters:
            filters = {}

        return list(self.block_storage.backups(details=detailed, **filters))

    def delete_volume_backup(
        self, name_or_id=None, force=False, wait=False, timeout=None
    ):
        """Delete a volume backup.

        :param name_or_id: Name or unique ID of the volume backup.
        :param force: Allow delete in state other than error or available.
        :param wait: If true, waits for volume backup to be deleted.
        :param timeout: Seconds to wait for volume backup deletion. None is
            forever.

        :returns: True if deletion was successful, else False.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if wait time
            exceeded.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        volume_backup = self.get_volume_backup(name_or_id)

        if not volume_backup:
            return False

        self.block_storage.delete_backup(
            volume_backup, ignore_missing=False, force=force
        )
        if wait:
            self.block_storage.wait_for_delete(volume_backup, wait=timeout)

        return True

    def delete_volume_snapshot(
        self,
        name_or_id=None,
        wait=False,
        timeout=None,
    ):
        """Delete a volume snapshot.

        :param name_or_id: Name or unique ID of the volume snapshot.
        :param wait: If true, waits for volume snapshot to be deleted.
        :param timeout: Seconds to wait for volume snapshot deletion. None is
            forever.

        :returns: True if deletion was successful, else False.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if wait time
            exceeded.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        volumesnapshot = self.get_volume_snapshot(name_or_id)

        if not volumesnapshot:
            return False

        self.block_storage.delete_snapshot(
            volumesnapshot, ignore_missing=False
        )

        if wait:
            self.block_storage.wait_for_delete(volumesnapshot, wait=timeout)

        return True

    def search_volumes(self, name_or_id=None, filters=None):
        """Search for one or more volumes.

        :param name_or_id: Name or unique ID of volume(s).
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of volume ``Volume`` objects, if any are found.
        """
        volumes = self.list_volumes()
        return _utils._filter_list(volumes, name_or_id, filters)

    def search_volume_snapshots(self, name_or_id=None, filters=None):
        """Search for one or more volume snapshots.

        :param name_or_id: Name or unique ID of volume snapshot(s).
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of volume ``Snapshot`` objects, if any are found.
        """
        volumesnapshots = self.list_volume_snapshots()
        return _utils._filter_list(volumesnapshots, name_or_id, filters)

    def search_volume_backups(self, name_or_id=None, filters=None):
        """Search for one or more volume backups.

        :param name_or_id: Name or unique ID of volume backup(s).
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of volume ``Backup`` objects, if any are found.
        """
        volume_backups = self.list_volume_backups()
        return _utils._filter_list(volume_backups, name_or_id, filters)

    def search_volume_types(
        self,
        name_or_id=None,
        filters=None,
        get_extra=None,
    ):
        """Search for one or more volume types.

        :param name_or_id: Name or unique ID of volume type(s).
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of volume ``Type`` objects, if any are found.
        """
        if get_extra is not None:
            warnings.warn(
                "the 'get_extra' argument is deprecated and no longer does "
                "anything; consider removing it from calls",
                os_warnings.RemovedInSDK50Warning,
            )
        volume_types = self.list_volume_types()
        return _utils._filter_list(volume_types, name_or_id, filters)

    def get_volume_type_access(self, name_or_id):
        """Return a list of volume_type_access.

        :param name_or_id: Name or unique ID of the volume type.
        :returns: A volume ``Type`` object if found, else None.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise exceptions.SDKException(
                f"VolumeType not found: {name_or_id}"
            )

        return self.block_storage.get_type_access(volume_type)

    def add_volume_type_access(self, name_or_id, project_id):
        """Grant access on a volume_type to a project.

        NOTE: the call works even if the project does not exist.

        :param name_or_id: ID or name of a volume_type
        :param project_id: A project id

        :returns: None
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise exceptions.SDKException(
                f"VolumeType not found: {name_or_id}"
            )

        self.block_storage.add_type_access(volume_type, project_id)

    def remove_volume_type_access(self, name_or_id, project_id):
        """Revoke access on a volume_type to a project.

        :param name_or_id: ID or name of a volume_type
        :param project_id: A project id

        :returns: None
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise exceptions.SDKException(
                f"VolumeType not found: {name_or_id}"
            )
        self.block_storage.remove_type_access(volume_type, project_id)

    def set_volume_quotas(self, name_or_id, **kwargs):
        """Set a volume quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :returns: None
        :raises: :class:`~openstack.exceptions.SDKException` if the resource to
            set the quota does not exist.
        """
        project = self.identity.find_project(name_or_id, ignore_missing=False)

        self.block_storage.update_quota_set(project=project, **kwargs)

    def get_volume_quotas(self, name_or_id):
        """Get volume quotas for a project

        :param name_or_id: project name or id

        :returns: A volume ``QuotaSet`` object with the quotas
        :raises: :class:`~openstack.exceptions.SDKException` if it's not a
            valid project
        """
        proj = self.identity.find_project(name_or_id, ignore_missing=False)

        return self.block_storage.get_quota_set(proj)

    def delete_volume_quotas(self, name_or_id):
        """Delete volume quotas for a project

        :param name_or_id: project name or id

        :returns: The deleted volume ``QuotaSet`` object.
        :raises: :class:`~openstack.exceptions.SDKException` if it's not a
            valid project or the call failed
        """
        proj = self.identity.find_project(name_or_id, ignore_missing=False)

        return self.block_storage.revert_quota_set(proj)
