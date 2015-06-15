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
    #: The administrative state of the load_balancer, which is up
    #: ``True`` or down ``False``. *Type: bool*
    admin_state_up = resource.prop('admin_state_up', type=bool)
    #: Description for the load_balancer.
    description = resource.prop('description')
    #: List of IDs of listeners associated with this load_balancer.
    #: *Type: list*
    listeners = resource.prop('listeners')
    #: Name of the load_balancer
    name = resource.prop('name')
    #: Status of load_balancer operating, e.g. ONLINE, OFFLINE.
    operating_status = resource.prop('operating_status')
    #: The project this load_balancer is associated with.
    project_id = resource.prop('tenant_id')
    #: Status of load_balancer provisioning, e.g. ACTIVE, INACTIVE.
    provisioning_status = resource.prop('provisioning_status')
    #: The IP address of the VIP.
    vip_address = resource.prop('vip_address')
    #: The ID of the subnet on which to allocate the VIP address.
    vip_subnet_id = resource.prop('vip_subnet_id')
