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


class LoadBalancer(resource.Resource):
    resource_key = 'loadbalancer'
    resources_key = 'loadbalancers'
    base_path = '/lbaas/loadbalancers'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Description for the load balancer.
    description = resource.Body('description')
    #: The administrative state of the load balancer, which is up
    #: ``True`` or down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: List of listeners associated with this load balancer.
    #: *Type: list of dicts which contain the listener IDs*
    listener_ids = resource.Body('listeners', type=list)
    #: Name of the load balancer
    name = resource.Body('name')
    #: Status of load_balancer operating, e.g. ONLINE, OFFLINE.
    operating_status = resource.Body('operating_status')
    #: List of pools associated with this load balancer.
    #: *Type: list of dicts which contain the pool IDs*
    pool_ids = resource.Body('pools', type=list)
    #: The ID of the project this load balancer is associated with.
    project_id = resource.Body('tenant_id')
    #: The name of the provider.
    provider = resource.Body('provider')
    #: Status of load balancer provisioning, e.g. ACTIVE, INACTIVE.
    provisioning_status = resource.Body('provisioning_status')
    #: The IP address of the VIP.
    vip_address = resource.Body('vip_address')
    #: The ID of the port for the VIP.
    vip_port_id = resource.Body('vip_port_id')
    #: The ID of the subnet on which to allocate the VIP address.
    vip_subnet_id = resource.Body('vip_subnet_id')
