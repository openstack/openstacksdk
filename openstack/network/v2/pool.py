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
from openstack import resource2 as resource


class Pool(resource.Resource):
    resource_key = 'pool'
    resources_key = 'pools'
    base_path = '/lbaas/pools'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'lb_algorithm', 'name',
        'protocol', 'provider', 'subnet_id', 'virtual_ip_id',
        is_admin_state_up='admin_state_up',
        project_id='tenant_id',
    )

    # Properties
    #: Description for the pool.
    description = resource.Body('description')
    #: The ID of the associated health monitors.
    health_monitor_ids = resource.Body('health_monitors', type=list)
    #: The statuses of the associated health monitors.
    health_monitor_status = resource.Body('health_monitor_status', type=list)
    #: The administrative state of the pool, which is up ``True`` or down
    #: ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The load-balancer algorithm, which is round-robin, least-connections,
    #: and so on. This value, which must be supported, is dependent on the
    #: load-balancer provider. Round-robin must be supported.
    lb_algorithm = resource.Body('lb_algorithm')
    #: List of associated listeners.
    #: *Type: list of dicts which contain the listener IDs*
    listener_ids = resource.Body('listeners', type=list)
    #: List of associated load balancers.
    #: *Type: list of dicts which contain the load balancer IDs*
    load_balancer_ids = resource.Body('loadbalancers', type=list)
    #: List of members that belong to the pool.
    #: *Type: list of dicts which contain the member IDs*
    member_ids = resource.Body('members', type=list)
    #: Pool name. Does not have to be unique.
    name = resource.Body('name')
    #: The ID of the project this pool is associated with.
    project_id = resource.Body('tenant_id')
    #: The protocol of the pool, which is TCP, HTTP, or HTTPS.
    protocol = resource.Body('protocol')
    #: The provider name of the load balancer service.
    provider = resource.Body('provider')
    #: Human readable description of the status.
    status = resource.Body('status')
    #: The status of the network.
    status_description = resource.Body('status_description')
    #: The subnet on which the members of the pool will be located.
    subnet_id = resource.Body('subnet_id')
    #: Session persistence algorithm that should be used (if any).
    #: *Type: dict with keys ``type`` and ``cookie_name``*
    session_persistence = resource.Body('session_persistence')
    #: The ID of the virtual IP (VIP) address.
    virtual_ip_id = resource.Body('vip_id')
