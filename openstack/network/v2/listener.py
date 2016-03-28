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


class Listener(resource.Resource):
    resource_key = 'listener'
    resources_key = 'listeners'
    base_path = '/lbaas/listeners'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The maximum number of connections permitted for this load balancer.
    #: Default is infinite.
    connection_limit = resource.prop('connection_limit')
    #: ID of default pool. Must have compatible protocol with listener.
    default_pool_id = resource.prop('default_pool_id')
    #: A reference to a container of TLS secrets.
    default_tls_container_ref = resource.prop('default_tls_container_ref')
    #: Description for the listener.
    description = resource.prop('description')
    #: The administrative state of the listener, which is up
    #: ``True`` or down ``False``. *Type: bool*
    is_admin_state_up = resource.prop('admin_state_up', type=bool)
    #: List of load balancers associated with this listener.
    #: *Type: list of dicts which contain the load balancer IDs*
    load_balancer_ids = resource.prop('loadbalancers')
    #: Name of the listener
    name = resource.prop('name')
    #: The ID of the project this listener is associated with.
    project_id = resource.prop('tenant_id')
    #: The protocol of the listener, which is TCP, HTTP, HTTPS
    #: or TERMINATED_HTTPS.
    protocol = resource.prop('protocol')
    #: Port the listener will listen to, e.g. 80.
    protocol_port = resource.prop('protocol_port')
    #: A list of references to TLS secrets.
    #: *Type: list*
    sni_container_refs = resource.prop('sni_container_refs')
