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

from openstack.network import network_service
from openstack import resource


class NetworkIPAvailability(resource.Resource):
    resource_key = 'network_ip_availability'
    resources_key = 'network_ip_availabilities'
    base_path = '/network-ip-availabilities'
    name_attribute = 'network_name'
    service = network_service.NetworkService()

    # capabilities
    allow_create = False
    allow_retrieve = True
    allow_update = False
    allow_delete = False
    allow_list = True

    # Properties
    #: Network ID to use when listing network IP availability.
    network_id = resource.prop('network_id')
    #: Network Name for the particular network IP availability.
    network_name = resource.prop('network_name')
    #: The Subnet IP Availability of all subnets of a network.
    #: *Type: list*
    subnet_ip_availability = resource.prop('subnet_ip_availability', type=list)
    #: The ID of the project this network IP availability is associated with.
    project_id = resource.prop('tenant_id')
    #: The total ips of a network.
    #: *Type: int*
    total_ips = resource.prop('total_ips', type=int)
    #: The used or consumed ip of a network
    #: *Type: int*
    used_ips = resource.prop('used_ips', type=int)
