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


class ConsistencyGroupSnapshot(resource.Resource):
    resource_key = "cgsnapshot"
    resources_key = "cgsnapshots"
    base_path = "/cgsnapshots"

    _query_mapping = resource.QueryParameters(
        "limit",
        "marker",
        "offset",
        "sort_dir",
        "sort_key",
        "sort",
    )

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The UUID of the source consistency group.
    consistencygroup_id = resource.Body("consistencygroup_id")
    #: The date and time when this resource was created.
    created_at = resource.Body("created_at")
    #: The description.
    description = resource.Body("description")
    #: The name.
    name = resource.Body("name")
    #: The status.
    status = resource.Body("status")
