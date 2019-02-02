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


class LoadBalancer(resource.Resource, resource.TagMixin):
    resource_key = 'loadbalancer'
    resources_key = 'loadbalancers'
    base_path = '/lbaas/loadbalancers'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'flavor_id', 'name', 'project_id', 'provider',
        'vip_address', 'vip_network_id', 'vip_port_id', 'vip_subnet_id',
        'vip_qos_policy_id', 'provisioning_status', 'operating_status',
        is_admin_state_up='admin_state_up',
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #: The administrative state of the load balancer *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: Timestamp when the load balancer was created
    created_at = resource.Body('created_at')
    #: The load balancer description
    description = resource.Body('description')
    #: The load balancer flavor ID
    flavor_id = resource.Body('flavor_id')
    #: List of listeners associated with this load balancer
    listeners = resource.Body('listeners', type=list)
    #: The load balancer name
    name = resource.Body('name')
    #: Operating status of the load balancer
    operating_status = resource.Body('operating_status')
    #: List of pools associated with this load balancer
    pools = resource.Body('pools', type=list)
    #: The ID of the project this load balancer is associated with.
    project_id = resource.Body('project_id')
    #: Provider name for the load balancer.
    provider = resource.Body('provider')
    #: The provisioning status of this load balancer
    provisioning_status = resource.Body('provisioning_status')
    #: Timestamp when the load balancer was last updated
    updated_at = resource.Body('updated_at')
    #: VIP address of load balancer
    vip_address = resource.Body('vip_address')
    #: VIP netowrk ID
    vip_network_id = resource.Body('vip_network_id')
    #: VIP port ID
    vip_port_id = resource.Body('vip_port_id')
    #: VIP subnet ID
    vip_subnet_id = resource.Body('vip_subnet_id')
    # VIP qos policy id
    vip_qos_policy_id = resource.Body('vip_qos_policy_id')

    def delete(self, session, error_message=None):
        request = self._prepare_request()
        headers = {
            "Accept": ""
        }

        request.headers.update(headers)
        params = {}
        if (hasattr(self, 'cascade') and isinstance(self.cascade, bool)
                and self.cascade):
            params['cascade'] = True
        response = session.delete(request.url,
                                  headers=headers,
                                  params=params)

        self._translate_response(response, has_body=False,
                                 error_message=error_message)
        return self


class LoadBalancerStats(resource.Resource):
    resource_key = 'stats'
    base_path = '/lbaas/loadbalancers/%(lb_id)s/stats'

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = False

    # Properties
    #: The ID of the load balancer.
    lb_id = resource.URI('lb_id')
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


class LoadBalancerFailover(resource.Resource):
    base_path = '/lbaas/loadbalancers/%(lb_id)s/failover'

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = True
    allow_delete = False
    allow_list = False
    allow_empty_commit = True

    requires_id = False

    # Properties
    #: The ID of the load balancer.
    lb_id = resource.URI('lb_id')

    # The default _update code path also has no
    # way to pass has_body into this function, so overriding the method here.
    def commit(self, session, base_path=None):
        return super(LoadBalancerFailover, self).commit(
            session, base_path=base_path, has_body=False)
