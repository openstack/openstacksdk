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

from openstack.block_store import block_store_service
from openstack import format
from openstack import resource


class Volume(resource.Resource):
    resource_key = "volume"
    resources_key = "volumes"
    base_path = "/volumes"
    service = block_store_service.BlockStoreService()

    # capabilities
    allow_retrieve = True
    allow_create = True
    allow_delete = True
    allow_update = True

    # Properties
    #: A ID representing this volume.
    id = resource.prop("id")
    #: The name of this volume.
    name = resource.prop("name")
    #: A list of links associated with this volume. *Type: list*
    links = resource.prop("links", type=list)

    #: The availability zone.
    availability_zone = resource.prop("availability_zone")
    #: To create a volume from an existing volume, specify the ID of
    #: the existing volume. If specified, the volume is created with
    #: same size of the source volume.
    source_volume_id = resource.prop("source_volid")
    #: The volume description.
    description = resource.prop("description")
    #: To create a volume from an existing snapshot, specify the ID of
    #: the existing volume snapshot. If specified, the volume is created
    #: in same availability zone and with same size of the snapshot.
    snapshot_id = resource.prop("snapshot_id")
    #: The size of the volume, in GBs. *Type: int*
    size = resource.prop("size", type=int)
    #: The ID of the image from which you want to create the volume.
    #: Required to create a bootable volume.
    image_id = resource.prop("imageRef")
    #: The name of the associated volume type.
    volume_type = resource.prop("volume_type")
    #: Enables or disables the bootable attribute. You can boot an
    #: instance from a bootable volume. *Type: bool*
    is_bootable = resource.prop("bootable", type=format.BoolStr)
    #: One or more metadata key and value pairs to associate with the volume.
    metadata = resource.prop("metadata")

    #: One of the following values: creating, available, attaching, in-use
    #: deleting, error, error_deleting, backing-up, restoring-backup,
    #: error_restoring. For details on these statuses, see the
    #: Block Storage API documentation.
    status = resource.prop("status")
    #: TODO(briancurtin): This is currently undocumented in the API.
    attachments = resource.prop("attachments")
    #: The timestamp of this volume creation.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop("created_at", type=format.ISO8601)


class VolumeDetail(Volume):

    base_path = "/volumes/detail"

    #: The volume's current back-end.
    host = resource.prop("os-vol-host-attr:host")
    #: The project ID associated with current back-end.
    project_id = resource.prop("os-vol-tenant-attr:tenant_id")
    #: The status of this volume's migration (None means that a migration
    #: is not currently in progress).
    migration_status = resource.prop("os-vol-mig-status-attr:migstat")
    #: The volume ID that this volume's name on the back-end is based on.
    migration_id = resource.prop("os-vol-mig-status-attr:name_id")
    #: Status of replication on this volume.
    replication_status = resource.prop("replication_status")
    #: Extended replication status on this volume.
    extended_replication_status = resource.prop(
        "os-volume-replication:extended_status")
    #: ID of the consistency group.
    consistency_group_id = resource.prop("consistencygroup_id")
    #: Data set by the replication driver
    replication_driver_data = resource.prop(
        "os-volume-replication:driver_data")
    #: ``True`` if this volume is encrypted, ``False`` if not.
    #: *Type: bool*
    is_encrypted = resource.prop("encrypted", type=format.BoolStr)
