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


class LoadBalancer(resource.Resource):
    resource_key = 'loadbalancer'
    resources_key = 'loadbalancers'
    base_path = '/lbaas/loadbalancers'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Description for the load balancer.
    description = resource.prop('description')
    #: The administrative state of the load balancer, which is up
    #: ``True`` or down ``False``. *Type: bool*
    is_admin_state_up = resource.prop('admin_state_up', type=bool)
    #: List of listeners associated with this load balancer.
    #: *Type: list of dicts which contain the listener IDs*
    listener_ids = resource.prop('listeners', type=list)
    #: Name of the load balancer
    name = resource.prop('name')
    #: Status of load_balancer operating, e.g. ONLINE, OFFLINE.
    operating_status = resource.prop('operating_status')
    #: List of pools associated with this load balancer.
    #: *Type: list of dicts which contain the pool IDs*
    pool_ids = resource.prop('pools', type=list)
    #: The ID of the project this load balancer is associated with.
    project_id = resource.prop('tenant_id')
    #: The name of the provider.
    provider = resource.prop('provider')
    #: Status of load balancer provisioning, e.g. ACTIVE, INACTIVE.
    provisioning_status = resource.prop('provisioning_status')
    #: The IP address of the VIP.
    vip_address = resource.prop('vip_address')
    #: The ID of the port for the VIP.
    vip_port_id = resource.prop('vip_port_id')
    #: The ID of the subnet on which to allocate the VIP address.
    vip_subnet_id = resource.prop('vip_subnet_id')
