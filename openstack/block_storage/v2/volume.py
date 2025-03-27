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


from openstack.common import metadata
from openstack import format
from openstack import resource
from openstack import utils


class Volume(resource.Resource, metadata.MetadataMixin):
    resource_key = "volume"
    resources_key = "volumes"
    base_path = "/volumes"

    _query_mapping = resource.QueryParameters(
        'name', 'status', 'project_id', all_projects='all_tenants'
    )

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    # Properties
    #: TODO(briancurtin): This is currently undocumented in the API.
    attachments = resource.Body("attachments")
    #: The availability zone.
    availability_zone = resource.Body("availability_zone")
    #: ID of the consistency group.
    consistency_group_id = resource.Body("consistencygroup_id")
    #: The timestamp of this volume creation.
    created_at = resource.Body("created_at")
    #: The date and time when the resource was updated.
    updated_at = resource.Body("updated_at")
    #: The volume description.
    description = resource.Body("description")
    #: Extended replication status on this volume.
    extended_replication_status = resource.Body(
        "os-volume-replication:extended_status"
    )
    #: The volume's current back-end.
    host = resource.Body("os-vol-host-attr:host")
    #: The ID of the image from which you want to create the volume.
    #: Required to create a bootable volume.
    image_id = resource.Body("imageRef")
    #: Enables or disables the bootable attribute. You can boot an
    #: instance from a bootable volume. *Type: bool*
    is_bootable = resource.Body("bootable", type=format.BoolStr)
    #: ``True`` if this volume is encrypted, ``False`` if not.
    #: *Type: bool*
    is_encrypted = resource.Body("encrypted", type=format.BoolStr)
    #: The volume ID that this volume's name on the back-end is based on.
    migration_id = resource.Body("os-vol-mig-status-attr:name_id")
    #: The status of this volume's migration (None means that a migration
    #: is not currently in progress).
    migration_status = resource.Body("os-vol-mig-status-attr:migstat")
    #: The project ID associated with current back-end.
    project_id = resource.Body("os-vol-tenant-attr:tenant_id")
    #: Data set by the replication driver
    replication_driver_data = resource.Body(
        "os-volume-replication:driver_data"
    )
    #: Status of replication on this volume.
    replication_status = resource.Body("replication_status")
    #: Scheduler hints for the volume
    scheduler_hints = resource.Body('OS-SCH-HNT:scheduler_hints', type=dict)
    #: The size of the volume, in GBs. *Type: int*
    size = resource.Body("size", type=int)
    #: To create a volume from an existing snapshot, specify the ID of
    #: the existing volume snapshot. If specified, the volume is created
    #: in same availability zone and with same size of the snapshot.
    snapshot_id = resource.Body("snapshot_id")
    #: To create a volume from an existing volume, specify the ID of
    #: the existing volume. If specified, the volume is created with
    #: same size of the source volume.
    source_volume_id = resource.Body("source_volid")
    #: One of the following values: creating, available, attaching, in-use
    #: deleting, error, error_deleting, backing-up, restoring-backup,
    #: error_restoring. For details on these statuses, see the
    #: Block Storage API documentation.
    status = resource.Body("status")
    #: The user ID associated with the volume
    user_id = resource.Body("user_id")
    #: One or more metadata key and value pairs about image
    volume_image_metadata = resource.Body("volume_image_metadata")
    #: The name of the associated volume type.
    volume_type = resource.Body("volume_type")

    def _action(self, session, body):
        """Preform volume actions given the message body."""
        # NOTE: This is using Volume.base_path instead of self.base_path
        # as both Volume and VolumeDetail instances can be acted on, but
        # the URL used is sans any additional /detail/ part.
        url = utils.urljoin(Volume.base_path, self.id, 'action')
        return session.post(url, json=body)

    def extend(self, session, size):
        """Extend a volume size."""
        body = {'os-extend': {'new_size': size}}
        self._action(session, body)

    def set_bootable_status(self, session, bootable=True):
        """Set volume bootable status flag"""
        body = {'os-set_bootable': {'bootable': bootable}}
        self._action(session, body)

    def set_readonly(self, session, readonly):
        """Set volume readonly flag"""
        body = {'os-update_readonly_flag': {'readonly': readonly}}
        self._action(session, body)

    def set_image_metadata(self, session, metadata):
        """Sets image metadata key-value pairs on the volume"""
        body = {'os-set_image_metadata': metadata}
        self._action(session, body)

    def delete_image_metadata(self, session):
        """Remove all image metadata from the volume"""
        for key in self.metadata:
            body = {'os-unset_image_metadata': key}
            self._action(session, body)

    def delete_image_metadata_item(self, session, key):
        """Remove a single image metadata from the volume"""
        body = {'os-unset_image_metadata': key}
        self._action(session, body)

    def reset_status(
        self, session, status=None, attach_status=None, migration_status=None
    ):
        """Reset volume statuses (admin operation)"""
        body: dict[str, dict[str, str]] = {'os-reset_status': {}}
        if status:
            body['os-reset_status']['status'] = status
        if attach_status:
            body['os-reset_status']['attach_status'] = attach_status
        if migration_status:
            body['os-reset_status']['migration_status'] = migration_status
        self._action(session, body)

    def attach(self, session, mountpoint, instance):
        """Attach volume to server"""
        body = {
            'os-attach': {'mountpoint': mountpoint, 'instance_uuid': instance}
        }

        self._action(session, body)

    def detach(self, session, attachment, force=False):
        """Detach volume from server"""
        if not force:
            body = {'os-detach': {'attachment_id': attachment}}
        if force:
            body = {'os-force_detach': {'attachment_id': attachment}}

        self._action(session, body)

    def unmanage(self, session):
        """Unmanage volume"""
        body = {'os-unmanage': None}

        self._action(session, body)

    def retype(self, session, new_type, migration_policy=None):
        """Change volume type"""
        body = {'os-retype': {'new_type': new_type}}
        if migration_policy:
            body['os-retype']['migration_policy'] = migration_policy

        self._action(session, body)

    def migrate(
        self, session, host=None, force_host_copy=False, lock_volume=False
    ):
        """Migrate volume"""
        req = dict()
        if host is not None:
            req['host'] = host
        if force_host_copy:
            req['force_host_copy'] = force_host_copy
        if lock_volume:
            req['lock_volume'] = lock_volume
        body = {'os-migrate_volume': req}

        self._action(session, body)

    def complete_migration(self, session, new_volume_id, error=False):
        """Complete volume migration"""
        body = {
            'os-migrate_volume_completion': {
                'new_volume': new_volume_id,
                'error': error,
            }
        }

        self._action(session, body)

    def force_delete(self, session):
        """Force volume deletion"""
        body = {'os-force_delete': None}

        self._action(session, body)


VolumeDetail = Volume
