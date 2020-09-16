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


class Listener(resource.Resource, resource.TagMixin):
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
        'created_at', 'updated_at', 'provisioning_status', 'operating_status',
        'sni_container_refs', 'insert_headers', 'load_balancer_id',
        'timeout_client_data', 'timeout_member_connect',
        'timeout_member_data', 'timeout_tcp_inspect', 'allowed_cidrs',
        'tls_ciphers', 'tls_versions', 'alpn_protocols',
        is_admin_state_up='admin_state_up',
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #: List of IPv4 or IPv6 CIDRs.
    allowed_cidrs = resource.Body('allowed_cidrs', type=list)
    #: List of ALPN protocols.
    alpn_protocols = resource.Body('alpn_protocols', type=list)
    #: The maximum number of connections permitted for this load balancer.
    #: Default is infinite.
    connection_limit = resource.Body('connection_limit')
    #: Timestamp when the listener was created.
    created_at = resource.Body('created_at')
    #: Default pool to which the requests will be routed.
    default_pool = resource.Body('default_pool')
    #: ID of default pool. Must have compatible protocol with listener.
    default_pool_id = resource.Body('default_pool_id')
    #: A reference to a container of TLS secrets.
    default_tls_container_ref = resource.Body('default_tls_container_ref')
    #: Description for the listener.
    description = resource.Body('description')
    #: Dictionary of additional headers insertion into HTTP header.
    insert_headers = resource.Body('insert_headers', type=dict)
    #: The administrative state of the listener, which is up
    #: ``True`` or down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: List of l7policies associated with this listener.
    l7_policies = resource.Body('l7policies', type=list)
    #: The ID of the parent load balancer.
    load_balancer_id = resource.Body('loadbalancer_id')
    #: List of load balancers associated with this listener.
    #: *Type: list of dicts which contain the load balancer IDs*
    load_balancers = resource.Body('loadbalancers', type=list)
    #: Name of the listener
    name = resource.Body('name')
    #: Operating status of the listener.
    operating_status = resource.Body('operating_status')
    #: The ID of the project this listener is associated with.
    project_id = resource.Body('project_id')
    #: The protocol of the listener, which is TCP, HTTP, HTTPS
    #: or TERMINATED_HTTPS.
    protocol = resource.Body('protocol')
    #: Port the listener will listen to, e.g. 80.
    protocol_port = resource.Body('protocol_port', type=int)
    #: The provisioning status of this listener.
    provisioning_status = resource.Body('provisioning_status')
    #: A list of references to TLS secrets.
    #: *Type: list*
    sni_container_refs = resource.Body('sni_container_refs')
    #: Timestamp when the listener was last updated.
    updated_at = resource.Body('updated_at')
    #: Frontend client inactivity timeout in milliseconds.
    timeout_client_data = resource.Body('timeout_client_data', type=int)
    #: Backend member connection timeout in milliseconds.
    timeout_member_connect = resource.Body('timeout_member_connect', type=int)
    #: Backend member inactivity timeout in milliseconds.
    timeout_member_data = resource.Body('timeout_member_data', type=int)
    #: Time, in milliseconds, to wait for additional TCP packets for content
    #: inspection.
    timeout_tcp_inspect = resource.Body('timeout_tcp_inspect', type=int)
    #: Stores a cipher string in OpenSSL format.
    tls_ciphers = resource.Body('tls_ciphers')
    #: A lsit of TLS protocols to be used by the listener
    tls_versions = resource.Body('tls_versions', type=list)


class ListenerStats(resource.Resource):
    resource_key = 'stats'
    base_path = '/lbaas/listeners/%(listener_id)s/stats'

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = False

    # Properties
    #: The ID of the listener.
    listener_id = resource.URI('listener_id')
    #: The currently active connections.
    active_connections = resource.Body('active_connections', type=int)
    #: The total bytes received.
    bytes_in = resource.Body('bytes_in', type=int)
    #: The total bytes sent.
    bytes_out = resource.Body('bytes_out', type=int)
    #: The total requests that were unable to be fulfilled.
    request_errors = resource.Body('request_errors', type=int)
    #: The total connections handled.
    total_connections = resource.Body('total_connections', type=int)
