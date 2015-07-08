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
from openstack import resource


class Snapshot(resource.Resource):
    resource_key = "snapshot"
    resources_key = "snapshots"
    base_path = "/snapshots"
    service = block_store_service.BlockStoreService()

    # capabilities
    allow_retrieve = True
    allow_create = True
    allow_delete = True
    allow_update = True

    # Properties
    #: A UUID representing this snapshot.
    id = resource.prop("id")
    #: Name of the snapshot. Default is None.
    name = resource.prop("name")

    #: The current status of this snapshot. Potential values are creating,
    #: available, deleting, error, and error_deleting.
    status = resource.prop("status")
    #: Description of snapshot. Default is None.
    description = resource.prop("description")
    #: The timestamp of this snapshot creation.
    created_at = resource.prop("created_at")
    #: Metadata associated with this snapshot.
    metadata = resource.prop("metadata", type=dict)
    #: The ID of the volume this snapshot was taken of.
    volume = resource.prop("volume_id")
    #: The size of the volume, in GBs.
    size = resource.prop("size", type=int)
    #: Indicate whether to snapshot, even if the volume is attached.
    #: Default is False.
    force = resource.prop("force", type=bool)


class SnapshotDetail(Snapshot):

    base_path = "/snapshots/detail"

    #: The percentage of completeness the snapshot is currently at.
    progress = resource.prop("os-extended-snapshot-attributes:progress")
    #: The tenant ID this snapshot is associatd with.
    project_id = resource.prop("os-extended-snapshot-attributes:project_id")
