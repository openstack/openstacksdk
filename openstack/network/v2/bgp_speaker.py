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
from openstack.network.v2 import agent as _agent
from openstack import resource
from openstack import utils


class BgpSpeaker(resource.Resource):
    resource_key = 'bgp_speaker'
    resources_key = 'bgp_speakers'
    base_path = '/bgp-speakers'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The Id of the BGP Speaker
    id = resource.Body('id')
    #: The BGP speaker's name.
    name = resource.Body('name')
    #: The ID of the project that owns the BGP Speaker.
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: The IP version (4 or 6) of the BGP Speaker.
    ip_version = resource.Body('ip_version')
    #: Whether to enable or disable the advertisement of floating ip host
    #: routes by the BGP Speaker. True by default.
    advertise_floating_ip_host_routes = resource.Body(
        'advertise_floating_ip_host_routes'
    )
    #: Whether to enable or disable the advertisement of tenant network
    #: routes by the BGP Speaker. True by default.
    advertise_tenant_networks = resource.Body('advertise_tenant_networks')
    #: The local Autonomous System number of the BGP Speaker.
    local_as = resource.Body('local_as')
    #: The ID of the network to which the BGP Speaker is associated.
    networks = resource.Body('networks')

    def _put(self, session, url, body):
        resp = session.put(url, json=body)
        exceptions.raise_from_response(resp)
        return resp

    def add_bgp_peer(self, session, peer_id):
        """Add BGP Peer to a BGP Speaker

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param peer_id: id of the peer to associate with the speaker.

        :returns: A dictionary as the API Reference describes it.

        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'add_bgp_peer')
        body = {'bgp_peer_id': peer_id}
        resp = self._put(session, url, body)
        return resp.json()

    def remove_bgp_peer(self, session, peer_id):
        """Remove BGP Peer from a BGP Speaker

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param peer_id: The ID of the peer to disassociate from the speaker.

        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'remove_bgp_peer')
        body = {'bgp_peer_id': peer_id}
        self._put(session, url, body)

    def add_gateway_network(self, session, network_id):
        """Add Network to a BGP Speaker

        :param: session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param network_id: The ID of the network to associate with the speaker

        :returns: A dictionary as the API Reference describes it.
        """
        body = {'network_id': network_id}
        url = utils.urljoin(self.base_path, self.id, 'add_gateway_network')
        resp = session.put(url, json=body)
        return resp.json()

    def remove_gateway_network(self, session, network_id):
        """Delete Network from a BGP Speaker

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param network_id: The ID of the network to disassociate
               from the speaker
        """
        body = {'network_id': network_id}
        url = utils.urljoin(self.base_path, self.id, 'remove_gateway_network')
        session.put(url, json=body)

    def get_advertised_routes(self, session):
        """List routes advertised by a BGP Speaker

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :returns: The response as a list of routes (cidr/nexthop pair
                  advertised by the BGP Speaker.

        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'get_advertised_routes')
        resp = session.get(url)
        exceptions.raise_from_response(resp)
        self._body.attributes.update(resp.json())
        return resp.json()

    def get_bgp_dragents(self, session):
        """List Dynamic Routing Agents hosting a specific BGP Speaker

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :returns: The response as a list of dragents hosting a specific
                  BGP Speaker.
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'bgp-dragents')
        resp = session.get(url)
        exceptions.raise_from_response(resp)
        self._body.attributes.update(resp.json())
        agent_ids = [ag['id'] for ag in resp.json()['agents']]
        agents = _agent.Agent.list(session=session)
        return [ag for ag in agents if ag.id in agent_ids]

    def add_bgp_speaker_to_dragent(self, session, bgp_agent_id):
        """Add BGP Speaker to a Dynamic Routing Agent

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param bgp_agent_id: The id of the dynamic routing agent to which
                             add the speaker.
        """
        body = {'bgp_speaker_id': self.id}
        url = utils.urljoin('agents', bgp_agent_id, 'bgp-drinstances')
        session.post(url, json=body)

    def remove_bgp_speaker_from_dragent(self, session, bgp_agent_id):
        """Delete BGP Speaker from a Dynamic Routing Agent

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param bgp_agent_id: The id of the dynamic routing agent from which
                             remove the speaker.
        """
        url = utils.urljoin('agents', bgp_agent_id, 'bgp-drinstances', self.id)
        session.delete(url)
