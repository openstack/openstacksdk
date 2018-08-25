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

    _query_mapping = resource.QueryParameters(
        'description', 'flavor', 'name', 'project_id', 'provider',
        'vip_address', 'vip_network_id', 'vip_port_id', 'vip_subnet_id',
        'vip_qos_policy_id', 'provisioning_status', 'operating_status',
        is_admin_state_up='admin_state_up'
    )

    #: Properties
    #: The administrative state of the load balancer *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: Timestamp when the load balancer was created
    created_at = resource.Body('created_at')
    #: The load balancer description
    description = resource.Body('description')
    #: The load balancer flavor
    flavor = resource.Body('flavor')
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
