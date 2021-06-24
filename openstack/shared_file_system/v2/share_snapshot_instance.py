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

from openstack import resource


class ShareSnapshotInstance(resource.Resource):
    resource_key = "snapshot_instance"
    resources_key = "snapshot_instances"
    base_path = "/snapshot-instances"

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True
    allow_head = False

    #: Properties
    #: The date and time stamp when the resource was created within the
    #: service’s database.
    created_at = resource.Body("created_at", type=str)
    #: The progress of the snapshot creation.
    progress = resource.Body("progress", type=str)
    #: Provider location of the snapshot on the backend.
    provider_location = resource.Body("provider_location", type=str)
    #: The UUID of the share.
    share_id = resource.Body("share_id", type=str)
    #: The UUID of the share instance.
    share_instance_id = resource.Body("share_instance_id", type=str)
    #: The UUID of the snapshot.
    snapshot_id = resource.Body("snapshot_id", type=str)
    #: The snapshot instance status.
    status = resource.Body("status", type=str)
    #: The date and time stamp when the resource was updated within the
    #: service’s database.
    updated_at = resource.Body("updated_at", type=str)
