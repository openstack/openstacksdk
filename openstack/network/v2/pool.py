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


class Pool(resource.Resource):
    resource_key = 'pool'
    resources_key = 'pools'
    base_path = '/lbaas/pools'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Description for the pool.
    description = resource.prop('description')
    #: The ID of the associated health monitor.
    health_monitor_id = resource.prop('healthmonitor_id')
    #: The administrative state of the pool, which is up ``True`` or down
    #: ``False``. *Type: bool*
    is_admin_state_up = resource.prop('admin_state_up', type=bool)
    #: The load-balancer algorithm, which is round-robin, least-connections,
    #: and so on. This value, which must be supported, is dependent on the
    #: load-balancer provider. Round-robin must be supported.
    lb_algorithm = resource.prop('lb_algorithm')
    #: List of associated listeners.
    #: *Type: list of dicts which contain the listener IDs*
    listener_ids = resource.prop('listeners', type=list)
    #: List of associated load balancers.
    #: *Type: list of dicts which contain the load balancer IDs*
    load_balancer_ids = resource.prop('loadbalancers', type=list)
    #: List of members that belong to the pool.
    #: *Type: list of dicts which contain the member IDs*
    member_ids = resource.prop('members', type=list)
    #: Pool name. Does not have to be unique.
    name = resource.prop('name')
    #: The ID of the project this pool is associated with.
    project_id = resource.prop('tenant_id')
    #: The protocol of the pool, which is TCP, HTTP, or HTTPS.
    protocol = resource.prop('protocol')
    #: Session persistence algorithm that should be used (if any).
    #: *Type: dict with keys ``type`` and ``cookie_name``*
    session_persistence = resource.prop('session_persistence')
