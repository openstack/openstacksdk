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


class Listener(resource.Resource):
    resource_key = 'listener'
    resources_key = 'listeners'
    base_path = '/lbaas/listeners'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'connection_limit', 'default_pool_id', 'default_tls_container_ref',
        'description', 'name', 'project_id', 'protocol', 'protocol_port',
        is_admin_state_up='admin_state_up'
    )

    # Properties
    #: The maximum number of connections permitted for this load balancer.
    #: Default is infinite.
    connection_limit = resource.Body('connection_limit')
    #: ID of default pool. Must have compatible protocol with listener.
    default_pool_id = resource.Body('default_pool_id')
    #: A reference to a container of TLS secrets.
    default_tls_container_ref = resource.Body('default_tls_container_ref')
    #: Description for the listener.
    description = resource.Body('description')
    #: The administrative state of the listener, which is up
    #: ``True`` or down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: List of load balancers associated with this listener.
    #: *Type: list of dicts which contain the load balancer IDs*
    load_balancer_ids = resource.Body('loadbalancers')
    #: The ID of the load balancer associated with this listener.
    load_balancer_id = resource.Body('loadbalancer_id')
    #: Name of the listener
    name = resource.Body('name')
    #: The ID of the project this listener is associated with.
    project_id = resource.Body('project_id')
    #: The protocol of the listener, which is TCP, HTTP, HTTPS
    #: or TERMINATED_HTTPS.
    protocol = resource.Body('protocol')
    #: Port the listener will listen to, e.g. 80.
    protocol_port = resource.Body('protocol_port')
    #: A list of references to TLS secrets.
    #: *Type: list*
    sni_container_refs = resource.Body('sni_container_refs')
