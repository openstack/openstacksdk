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


class ShareSnapshot(resource.Resource):
    resource_key = "snapshot"
    resources_key = "snapshots"
    base_path = "/snapshots"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_head = False

    _query_mapping = resource.QueryParameters("snapshot_id")

    #: Properties
    #: The date and time stamp when the resource was
    #: created within the service’s database.
    created_at = resource.Body("created_at")
    #: The user defined description of the resource.
    description = resource.Body("description", type=str)
    #: The user defined name of the resource.
    display_name = resource.Body("display_name", type=str)
    #: The user defined description of the resource
    display_description = resource.Body("display_description", type=str)
    #: ID of the project that the snapshot belongs to.
    project_id = resource.Body("project_id", type=str)
    #: The UUID of the source share that was used to
    #: create the snapshot.
    share_id = resource.Body("share_id", type=str)
    #: The file system protocol of a share snapshot
    share_proto = resource.Body("share_proto", type=str)
    #: The snapshot's source share's size, in GiBs.
    share_size = resource.Body("share_size", type=int)
    #: The snapshot size, in GiBs.
    size = resource.Body("size", type=int)
    #: The snapshot status
    status = resource.Body("status", type=str)
    #: ID of the user that the snapshot was created by.
    user_id = resource.Body("user_id", type=str)
