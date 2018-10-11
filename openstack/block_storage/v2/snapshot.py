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


class Snapshot(resource.Resource):
    resource_key = "snapshot"
    resources_key = "snapshots"
    base_path = "/snapshots"

    _query_mapping = resource.QueryParameters(
        'all_tenants', 'name', 'status', 'volume_id')

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    # Properties
    #: A ID representing this snapshot.
    id = resource.Body("id")
    #: Name of the snapshot. Default is None.
    name = resource.Body("name")

    #: The current status of this snapshot. Potential values are creating,
    #: available, deleting, error, and error_deleting.
    status = resource.Body("status")
    #: Description of snapshot. Default is None.
    description = resource.Body("description")
    #: The timestamp of this snapshot creation.
    created_at = resource.Body("created_at")
    #: Metadata associated with this snapshot.
    metadata = resource.Body("metadata", type=dict)
    #: The ID of the volume this snapshot was taken of.
    volume_id = resource.Body("volume_id")
    #: The size of the volume, in GBs.
    size = resource.Body("size", type=int)
    #: Indicate whether to create snapshot, even if the volume is attached.
    #: Default is ``False``. *Type: bool*
    is_forced = resource.Body("force", type=format.BoolStr)


class SnapshotDetail(Snapshot):

    base_path = "/snapshots/detail"

    #: The percentage of completeness the snapshot is currently at.
    progress = resource.Body("os-extended-snapshot-attributes:progress")
    #: The project ID this snapshot is associated with.
    project_id = resource.Body("os-extended-snapshot-attributes:project_id")
