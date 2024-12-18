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

from openstack import exceptions
from openstack.network.v2 import bgp_speaker as _speaker
from openstack import resource
from openstack import utils


class Agent(resource.Resource):
    """Neutron agent extension."""

    resource_key = 'agent'
    resources_key = 'agents'
    base_path = '/agents'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # NOTE: We skip query for JSON fields and datetime fields
    _query_mapping = resource.QueryParameters(
        'agent_type',
        'availability_zone',
        'binary',
        'description',
        'host',
        'topic',
        is_admin_state_up='admin_state_up',
        is_alive='alive',
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
    #: Whether or not the agent is succesffully synced towards placement.
    #: Agents supporting the guaranteed minimum bandwidth feature share their
    #: resource view with neutron-server and neutron-server share this view
    #: with placement, resources_synced represents the success of the latter.
    #: The value None means no resource view synchronization to Placement was
    #: attempted. true / false values signify the success of the last
    #: synchronization attempt.
    #: *Type: bool*
    resources_synced = resource.Body('resources_synced', type=bool)
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
        resp = session.post(url, json=body)
        return resp.json()

    def remove_agent_from_network(self, session, network_id):
        body = {'network_id': network_id}
        url = utils.urljoin(
            self.base_path, self.id, 'dhcp-networks', network_id
        )
        session.delete(url, json=body)

    def add_router_to_agent(self, session, router):
        body = {'router_id': router}
        url = utils.urljoin(self.base_path, self.id, 'l3-routers')
        resp = session.post(url, json=body)
        return resp.json()

    def remove_router_from_agent(self, session, router):
        body = {'router_id': router}
        url = utils.urljoin(self.base_path, self.id, 'l3-routers', router)
        session.delete(url, json=body)

    def get_bgp_speakers_hosted_by_dragent(self, session):
        """List BGP speakers hosted by a Dynamic Routing Agent

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :returns: A list of BgpSpeakers
        :rtype: :class:`~openstack.network.v2.bgp_speaker.BgpSpeaker`
        """
        url = utils.urljoin(self.base_path, self.id, 'bgp-drinstances')
        resp = session.get(url)
        exceptions.raise_from_response(resp)
        self._body.attributes.update(resp.json())
        speaker_ids = [sp['id'] for sp in resp.json()['bgp_speakers']]
        speakers = _speaker.BgpSpeaker.list(session=session)
        return [sp for sp in speakers if sp.id in speaker_ids]


class NetworkHostingDHCPAgent(Agent):
    resource_key = 'agent'
    resources_key = 'agents'
    resource_name = 'dhcp-agent'
    base_path = '/networks/%(network_id)s/dhcp-agents'

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True

    # NOTE: Doesn't support query yet.


class RouterL3Agent(Agent):
    resource_key = 'agent'
    resources_key = 'agents'
    base_path = '/routers/%(router_id)s/l3-agents'
    resource_name = 'l3-agent'

    # capabilities
    allow_create = False
    allow_retrieve = True
    allow_commit = False
    allow_delete = False
    allow_list = True

    # NOTE: No query parameter is supported
