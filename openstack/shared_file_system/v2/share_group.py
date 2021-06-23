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


class ShareGroup(resource.Resource):
    resource_key = "share_group"
    resources_key = "share_groups"
    base_path = "/share-groups"

    _query_mapping = resource.QueryParameters("share_group_id")

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_head = False

    #: Properties
    #: The availability zone ID that the share group exists within.
    availability_zone = resource.Body("availability_zone", type=str)
    #: The consistency snapshot support.
    consistent_snapshot_support = resource.Body(
        "consistent_snapshot_support", type=str
    )
    #: The date and time stamp when the resource was created within the
    #: service’s database.
    created_at = resource.Body("created_at", type=str)
    #: The user defined description of the resource.
    description = resource.Body("description", type=str)
    #: The ID of the project that owns the resource.
    project_id = resource.Body("project_id", type=str)
    #: The share group snapshot ID.
    share_group_snapshot_id = resource.Body(
        "share_group_snapshot_id", type=str
    )
    #: The share group type ID.
    share_group_type_id = resource.Body("share_group_type_id", type=str)
    #: The share network ID where the resource is exported to.
    share_network_id = resource.Body("share_network_id", type=str)
    #: A list of share type IDs.
    share_types = resource.Body("share_types", type=list)
    #: The share status
    status = resource.Body("status", type=str)
