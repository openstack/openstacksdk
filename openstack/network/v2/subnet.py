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


class Subnet(resource.Resource):
    resource_key = 'subnet'
    resources_key = 'subnets'
    base_path = '/subnets'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    put_update = True

    # Properties
    allocation_pools = resource.prop('allocation_pools')
    cidr = resource.prop('cidr')
    dns_nameservers = resource.prop('dns_nameservers')
    enable_dhcp = resource.prop('enable_dhcp', type=bool)
    gateway_ip = resource.prop('gateway_ip')
    host_routes = resource.prop('host_routes')
    ip_version = resource.prop('ip_version')
    name = resource.prop('name')
    network_id = resource.prop('network_id')
    project_id = resource.prop('tenant_id')
