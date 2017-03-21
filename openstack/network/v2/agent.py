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
from openstack import utils


class Agent(resource.Resource):
    """Neutron agent extension."""
    resource_key = 'agent'
    resources_key = 'agents'
    base_path = '/agents'
    service = network_service.NetworkService()

    # capabilities
    allow_create = False
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # NOTE: We skip query for JSON fields and datetime fields
    _query_mapping = resource.QueryParameters(
        'agent_type', 'availability_zone', 'binary', 'description', 'host',
        'topic',
        is_admin_state_up='admin_state_up', is_alive='alive',
    )

    # Properties
    #: The type of network agent.
    agent_type = resource.Body('agent_type')
    #: Availability zone for the network agent.
    availability_zone = resource.Body('availability_zone')
    #: The name of the network agent's application binary.
    binary = resource.Body('binary')
    #: Network agent configuration data specific to the agent_type.
    configuration = resource.Body('configurations')
    #: Timestamp when the network agent was created.
    created_at = resource.Body('created_at')
    #: The network agent description.
    description = resource.Body('description')
    #: Timestamp when the network agent's heartbeat was last seen.
    last_heartbeat_at = resource.Body('heartbeat_timestamp')
    #: The host the agent is running on.
    host = resource.Body('host')
    #: The administrative state of the network agent, which is up
    #: ``True`` or down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: Whether or not the network agent is alive.
    #: *Type: bool*
    is_alive = resource.Body('alive', type=bool)
    #: Timestamp when the network agent was last started.
    started_at = resource.Body('started_at')
    #: The messaging queue topic the network agent subscribes to.
    topic = resource.Body('topic')
    #: The HA state of the L3 agent. This is one of 'active', 'standby' or
    #: 'fault' for HA routers, or None for other types of routers.
    ha_state = resource.Body('ha_state')

    def add_agent_to_network(self, session, network_id):
        body = {'network_id': network_id}
        url = utils.urljoin(self.base_path, self.id, 'dhcp-networks')
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json()

    def remove_agent_from_network(self, session, network_id):
        body = {'network_id': network_id}
        url = utils.urljoin(self.base_path, self.id, 'dhcp-networks',
                            network_id)
        session.delete(url, endpoint_filter=self.service, json=body)

    def add_router_to_agent(self, session, router):
        body = {'router_id': router}
        url = utils.urljoin(self.base_path, self.id, 'l3-routers')
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json()

    def remove_router_from_agent(self, session, router):
        body = {'router_id': router}
        url = utils.urljoin(self.base_path, self.id, 'l3-routers', router)
        session.delete(url, endpoint_filter=self.service, json=body)


class NetworkHostingDHCPAgent(Agent):
    resource_key = 'agent'
    resources_key = 'agents'
    resource_name = 'dhcp-agent'
    base_path = '/networks/%(network_id)s/dhcp-agents'
    service = network_service.NetworkService()

    # capabilities
    allow_create = False
    allow_get = True
    allow_update = False
    allow_delete = False
    allow_list = True

    # NOTE: Doesn't support query yet.


class RouterL3Agent(Agent):
    resource_key = 'agent'
    resources_key = 'agents'
    base_path = '/routers/%(router_id)s/l3-agents'
    resource_name = 'l3-agent'
    service = network_service.NetworkService()

    # capabilities
    allow_create = False
    allow_retrieve = True
    allow_update = False
    allow_delete = False
    allow_list = True

    # NOTE: No query parameter is supported
