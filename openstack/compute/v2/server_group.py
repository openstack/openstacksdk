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

from openstack.compute import compute_service
from openstack import resource2


class ServerGroup(resource2.Resource):
    resource_key = 'server_group'
    resources_key = 'server_groups'
    base_path = '/os-server-groups'
    service = compute_service.ComputeService()

    _query_mapping = resource2.QueryParameters("all_projects")

    # capabilities
    allow_create = True
    allow_get = True
    allow_delete = True
    allow_list = True

    # Properties
    #: A name identifying the server group
    name = resource2.Body('name')
    #: The list of policies supported by the server group
    policies = resource2.Body('policies')
    #: The list of members in the server group
    member_ids = resource2.Body('members')
    #: The metadata associated with the server group
    metadata = resource2.Body('metadata')
