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
from openstack import exceptions
from openstack import format
from openstack import resource
from openstack import utils


class Volume(resource.Resource, metadata.MetadataMixin):
    resource_key = "volume"
    resources_key = "volumes"
    base_path = "/volumes"

    _query_mapping = resource.QueryParameters(
        'name',
        'status',
        'user_id',
        'project_id',
        'created_at',
        'updated_at',
        all_projects='all_tenants',
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
    #: The ID of the group that the volume belongs to.
    group_id = resource.Body("group_id")
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
    #: Whether volume will be sharable or not.
    is_multiattach = resource.Body("multiattach", type=bool)
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
    #: The provider ID for the volume.
    provider_id = resource.Body("provider_id")
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

    _max_microversion = "3.71"

    def _action(self, session, body, microversion=None):
        """Preform volume actions given the message body."""
        # NOTE: This is using Volume.base_path instead of self.base_path
        # as both Volume and VolumeDetail instances can be acted on, but
        # the URL used is sans any additional /detail/ part.
        url = utils.urljoin(Volume.base_path, self.id, 'action')
        if microversion is None:
            microversion = self._get_microversion(session)
        resp = session.post(url, json=body, microversion=microversion)
        exceptions.raise_from_response(resp)
        return resp

    def extend(self, session, size):
        """Extend a volume size."""
        body = {'os-extend': {'new_size': size}}
        self._action(session, body)

    def complete_extend(self, session, error=False):
        """Complete volume extend operation"""
        body = {'os-extend_volume_completion': {'error': error}}
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

    def revert_to_snapshot(self, session, snapshot_id):
        """Revert volume to its snapshot"""
        utils.require_microversion(session, "3.40")
        body = {'revert': {'snapshot_id': snapshot_id}}
        self._action(session, body)

    def attach(self, session, mountpoint, instance=None, host_name=None):
        """Attach volume to server"""
        body = {'os-attach': {'mountpoint': mountpoint}}

        if instance is not None:
            body['os-attach']['instance_uuid'] = instance
        elif host_name is not None:
            body['os-attach']['host_name'] = host_name
        else:
            raise ValueError(
                'Either instance_uuid or host_name must be specified'
            )

        self._action(session, body)

    def detach(self, session, attachment, force=False, connector=None):
        """Detach volume from server"""
        if not force:
            body = {'os-detach': {'attachment_id': attachment}}
        if force:
            body = {'os-force_detach': {'attachment_id': attachment}}
            if connector:
                body['os-force_detach']['connector'] = connector

        self._action(session, body)

    @classmethod
    def manage(
        cls,
        session,
        host,
        ref,
        name=None,
        description=None,
        volume_type=None,
        availability_zone=None,
        metadata=None,
        bootable=False,
        cluster=None,
    ):
        """Manage an existing volume."""
        url = '/manageable_volumes'
        if not utils.supports_microversion(session, '3.8'):
            url = '/os-volume-manage'
        body = {
            'volume': {
                'host': host,
                'ref': ref,
                'name': name,
                'description': description,
                'volume_type': volume_type,
                'availability_zone': availability_zone,
                'metadata': metadata,
                'bootable': bootable,
            }
        }
        if cluster is not None:
            body['volume']['cluster'] = cluster
        resp = session.post(url, json=body, microversion=cls._max_microversion)
        exceptions.raise_from_response(resp)
        volume = Volume()
        volume._translate_response(resp)
        return volume

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
        self,
        session,
        host=None,
        force_host_copy=False,
        lock_volume=False,
        cluster=None,
    ):
        """Migrate volume"""
        req = dict()
        if host is not None:
            req['host'] = host
        if force_host_copy:
            req['force_host_copy'] = force_host_copy
        if lock_volume:
            req['lock_volume'] = lock_volume
        if cluster is not None:
            req['cluster'] = cluster
            utils.require_microversion(session, "3.16")
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

    def upload_to_image(
        self,
        session,
        image_name,
        force=False,
        disk_format=None,
        container_format=None,
        visibility=None,
        protected=None,
    ):
        """Upload the volume to image service"""
        req = dict(image_name=image_name, force=force)
        if disk_format is not None:
            req['disk_format'] = disk_format
        if container_format is not None:
            req['container_format'] = container_format
        if visibility is not None:
            req['visibility'] = visibility
        if protected is not None:
            req['protected'] = protected

        if visibility is not None or protected is not None:
            utils.require_microversion(session, "3.1")

        body = {'os-volume_upload_image': req}

        resp = self._action(session, body).json()
        return resp['os-volume_upload_image']

    def reserve(self, session):
        """Reserve volume"""
        body = {'os-reserve': None}

        self._action(session, body)

    def unreserve(self, session):
        """Unreserve volume"""
        body = {'os-unreserve': None}

        self._action(session, body)

    def begin_detaching(self, session):
        """Update volume status to 'detaching'"""
        body = {'os-begin_detaching': None}

        self._action(session, body)

    def abort_detaching(self, session):
        """Roll back volume status to 'in-use'"""
        body = {'os-roll_detaching': None}

        self._action(session, body)

    def init_attachment(self, session, connector):
        """Initialize volume attachment"""
        body = {'os-initialize_connection': {'connector': connector}}

        resp = self._action(session, body).json()
        return resp['connection_info']

    def terminate_attachment(self, session, connector):
        """Terminate volume attachment"""
        body = {'os-terminate_connection': {'connector': connector}}

        self._action(session, body)

    def _prepare_request_body(
        self, patch, prepend_key, *, resource_request_key=None
    ):
        body = self._body.dirty
        # Scheduler hints is external to the standard volume request
        # so pass it separately and not under the volume JSON object.
        scheduler_hints = None
        if 'OS-SCH-HNT:scheduler_hints' in body.keys():
            scheduler_hints = body.pop('OS-SCH-HNT:scheduler_hints')
        if prepend_key and self.resource_key is not None:
            body = {self.resource_key: body}
        # If scheduler hints was passed in the request but the value is
        # None, it doesn't make a difference to include it.
        if scheduler_hints:
            body['OS-SCH-HNT:scheduler_hints'] = scheduler_hints
        return body


VolumeDetail = Volume
