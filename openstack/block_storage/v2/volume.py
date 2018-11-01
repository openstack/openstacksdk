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

from openstack import format
from openstack import resource
from openstack import utils


class Volume(resource.Resource):
    resource_key = "volume"
    resources_key = "volumes"
    base_path = "/volumes"

    _query_mapping = resource.QueryParameters(
        'name', 'status', 'project_id', all_projects='all_tenants')

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    # Properties
    #: A ID representing this volume.
    id = resource.Body("id")
    #: The name of this volume.
    name = resource.Body("name")
    #: A list of links associated with this volume. *Type: list*
    links = resource.Body("links", type=list)

    #: The availability zone.
    availability_zone = resource.Body("availability_zone")
    #: To create a volume from an existing volume, specify the ID of
    #: the existing volume. If specified, the volume is created with
    #: same size of the source volume.
    source_volume_id = resource.Body("source_volid")
    #: The volume description.
    description = resource.Body("description")
    #: To create a volume from an existing snapshot, specify the ID of
    #: the existing volume snapshot. If specified, the volume is created
    #: in same availability zone and with same size of the snapshot.
    snapshot_id = resource.Body("snapshot_id")
    #: The size of the volume, in GBs. *Type: int*
    size = resource.Body("size", type=int)
    #: The ID of the image from which you want to create the volume.
    #: Required to create a bootable volume.
    image_id = resource.Body("imageRef")
    #: The name of the associated volume type.
    volume_type = resource.Body("volume_type")
    #: Enables or disables the bootable attribute. You can boot an
    #: instance from a bootable volume. *Type: bool*
    is_bootable = resource.Body("bootable", type=format.BoolStr)
    #: One or more metadata key and value pairs to associate with the volume.
    metadata = resource.Body("metadata")
    #: One or more metadata key and value pairs about image
    volume_image_metadata = resource.Body("volume_image_metadata")

    #: One of the following values: creating, available, attaching, in-use
    #: deleting, error, error_deleting, backing-up, restoring-backup,
    #: error_restoring. For details on these statuses, see the
    #: Block Storage API documentation.
    status = resource.Body("status")
    #: TODO(briancurtin): This is currently undocumented in the API.
    attachments = resource.Body("attachments")
    #: The timestamp of this volume creation.
    created_at = resource.Body("created_at")

    def _action(self, session, body):
        """Preform volume actions given the message body."""
        # NOTE: This is using Volume.base_path instead of self.base_path
        # as both Volume and VolumeDetail instances can be acted on, but
        # the URL used is sans any additional /detail/ part.
        url = utils.urljoin(Volume.base_path, self.id, 'action')
        headers = {'Accept': ''}
        return session.post(url, json=body, headers=headers)

    def extend(self, session, size):
        """Extend a volume size."""
        body = {'os-extend': {'new_size': size}}
        self._action(session, body)


class VolumeDetail(Volume):

    base_path = "/volumes/detail"

    # capabilities
    allow_fetch = False
    allow_create = False
    allow_delete = False
    allow_commit = False
    allow_list = True

    #: The volume's current back-end.
    host = resource.Body("os-vol-host-attr:host")
    #: The project ID associated with current back-end.
    project_id = resource.Body("os-vol-tenant-attr:tenant_id")
    #: The status of this volume's migration (None means that a migration
    #: is not currently in progress).
    migration_status = resource.Body("os-vol-mig-status-attr:migstat")
    #: The volume ID that this volume's name on the back-end is based on.
    migration_id = resource.Body("os-vol-mig-status-attr:name_id")
    #: Status of replication on this volume.
    replication_status = resource.Body("replication_status")
    #: Extended replication status on this volume.
    extended_replication_status = resource.Body(
        "os-volume-replication:extended_status")
    #: ID of the consistency group.
    consistency_group_id = resource.Body("consistencygroup_id")
    #: Data set by the replication driver
    replication_driver_data = resource.Body(
        "os-volume-replication:driver_data")
    #: ``True`` if this volume is encrypted, ``False`` if not.
    #: *Type: bool*
    is_encrypted = resource.Body("encrypted", type=format.BoolStr)
