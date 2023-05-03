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
from openstack.shared_file_system.v2 import share_network_subnet


class ShareNetwork(resource.Resource):
    resource_key = "share_network"
    resources_key = "share_networks"
    base_path = "/share-networks"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_head = False

    _query_mapping = resource.QueryParameters(
        "project_id",
        "name",
        "description",
        "created_since",
        "created_before",
        "security_service_id",
        "limit",
        "offset",
        all_projects="all_tenants",
    )

    #: Properties
    #: The date and time stamp when the resource was created within the
    #: service’s database.
    created_at = resource.Body("created_at")
    #: The user defined description of the resource.
    description = resource.Body("description", type=str)
    #: The ID of the project that owns the resource.
    project_id = resource.Body("project_id", type=str)
    #: A list of share network subnets that pertain to the related share
    #: network.
    share_network_subnets = resource.Body(
        "share_network_subnets",
        type=list,
        list_type=share_network_subnet.ShareNetworkSubnet,
    )
    #: The UUID of a neutron network when setting up or
    #: updating a share network subnet with neutron.
    neutron_net_id = resource.Body("neutron_net_id", type=str)
    #: The UUID of the neutron subnet when setting up or updating
    #: a share network subnet with neutron.
    neutron_subnet_id = resource.Body("neutron_subnet_id", type=str)
    #: The date and time stamp when the resource was last updated within
    #: the service’s database.
    updated_at = resource.Body("updated_at", type=str)
