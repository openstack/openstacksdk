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

from openstack.load_balancer import load_balancer_service as lb_service
from openstack import resource


class Pool(resource.Resource):
    resource_key = 'pool'
    resources_key = 'pools'
    base_path = '/v2.0/lbaas/pools'
    service = lb_service.LoadBalancerService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True
    allow_update = True

    _query_mapping = resource.QueryParameters(
        'health_monitor_id', 'lb_algorithm', 'listener_id', 'loadbalancer_id',
        'description', 'name', 'project_id', 'protocol',
        'created_at', 'updated_at', 'provisioning_status', 'operating_status',
        is_admin_state_up='admin_state_up'
    )

    #: Properties
    #: Timestamp when the pool was created
    created_at = resource.Body('created_at')
    #: Description for the pool.
    description = resource.Body('description')
    #: Health Monitor ID
    health_monitor_id = resource.Body('healthmonitor_id')
    #: The administrative state of the pool *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The loadbalancing algorithm used in the pool
    lb_algorithm = resource.Body('lb_algorithm')
    #: ID of listener associated with this pool
    listener_id = resource.Body('listener_id')
    #: List of listeners associated with this pool
    listeners = resource.Body('listeners', type=list)
    #: ID of load balancer associated with this pool
    loadbalancer_id = resource.Body('loadbalancer_id')
    #: List of loadbalancers associated with this pool
    loadbalancers = resource.Body('loadbalancers', type=list)
    #: Members associated with this pool
    members = resource.Body('members', type=list)
    #: The pool name
    name = resource.Body('name')
    #: Operating status of the pool
    operating_status = resource.Body('operating_status')
    #: The ID of the project
    project_id = resource.Body('project_id')
    #: The protocol of the pool
    protocol = resource.Body('protocol')
    #: Provisioning status of the pool
    provisioning_status = resource.Body('provisioning_status')
    #: A JSON object specifying the session persistence for the pool.
    session_persistence = resource.Body('session_persistence', type=dict)
    #: Timestamp when the pool was updated
    updated_at = resource.Body('updated_at')
