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

import typing as ty

from openstack import exceptions
from openstack.network.v2 import _base
from openstack.network.v2 import address_group as _address_group
from openstack.network.v2 import address_scope as _address_scope
from openstack.network.v2 import agent as _agent
from openstack.network.v2 import (
    auto_allocated_topology as _auto_allocated_topology,
)
from openstack.network.v2 import availability_zone
from openstack.network.v2 import bgp_peer as _bgp_peer
from openstack.network.v2 import bgp_speaker as _bgp_speaker
from openstack.network.v2 import bgpvpn as _bgpvpn
from openstack.network.v2 import (
    bgpvpn_network_association as _bgpvpn_network_association,
)
from openstack.network.v2 import (
    bgpvpn_port_association as _bgpvpn_port_association,
)
from openstack.network.v2 import (
    bgpvpn_router_association as _bgpvpn_router_association,
)
from openstack.network.v2 import (
    default_security_group_rule as _default_security_group_rule,
)
from openstack.network.v2 import extension
from openstack.network.v2 import firewall_group as _firewall_group
from openstack.network.v2 import firewall_policy as _firewall_policy
from openstack.network.v2 import firewall_rule as _firewall_rule
from openstack.network.v2 import flavor as _flavor
from openstack.network.v2 import floating_ip as _floating_ip
from openstack.network.v2 import health_monitor as _health_monitor
from openstack.network.v2 import l3_conntrack_helper as _l3_conntrack_helper
from openstack.network.v2 import listener as _listener
from openstack.network.v2 import load_balancer as _load_balancer
from openstack.network.v2 import local_ip as _local_ip
from openstack.network.v2 import local_ip_association as _local_ip_association
from openstack.network.v2 import metering_label as _metering_label
from openstack.network.v2 import metering_label_rule as _metering_label_rule
from openstack.network.v2 import ndp_proxy as _ndp_proxy
from openstack.network.v2 import network as _network
from openstack.network.v2 import network_ip_availability
from openstack.network.v2 import (
    network_segment_range as _network_segment_range,
)
from openstack.network.v2 import pool as _pool
from openstack.network.v2 import pool_member as _pool_member
from openstack.network.v2 import port as _port
from openstack.network.v2 import port_binding as _port_binding
from openstack.network.v2 import port_forwarding as _port_forwarding
from openstack.network.v2 import (
    qos_bandwidth_limit_rule as _qos_bandwidth_limit_rule,
)
from openstack.network.v2 import (
    qos_dscp_marking_rule as _qos_dscp_marking_rule,
)
from openstack.network.v2 import (
    qos_minimum_bandwidth_rule as _qos_minimum_bandwidth_rule,
)
from openstack.network.v2 import (
    qos_minimum_packet_rate_rule as _qos_minimum_packet_rate_rule,
)
from openstack.network.v2 import (
    qos_packet_rate_limit_rule as _qos_packet_rate_limit_rule,
)
from openstack.network.v2 import qos_policy as _qos_policy
from openstack.network.v2 import qos_rule_type as _qos_rule_type
from openstack.network.v2 import quota as _quota
from openstack.network.v2 import rbac_policy as _rbac_policy
from openstack.network.v2 import router as _router
from openstack.network.v2 import security_group as _security_group
from openstack.network.v2 import security_group_rule as _security_group_rule
from openstack.network.v2 import segment as _segment
from openstack.network.v2 import service_profile as _service_profile
from openstack.network.v2 import service_provider as _service_provider
from openstack.network.v2 import sfc_flow_classifier as _sfc_flow_classifier
from openstack.network.v2 import sfc_port_chain as _sfc_port_chain
from openstack.network.v2 import sfc_port_pair as _sfc_port_pair
from openstack.network.v2 import sfc_port_pair_group as _sfc_port_pair_group
from openstack.network.v2 import sfc_service_graph as _sfc_sservice_graph
from openstack.network.v2 import subnet as _subnet
from openstack.network.v2 import subnet_pool as _subnet_pool
from openstack.network.v2 import tap_flow as _tap_flow
from openstack.network.v2 import tap_mirror as _tap_mirror
from openstack.network.v2 import tap_service as _tap_service
from openstack.network.v2 import trunk as _trunk
from openstack.network.v2 import vpn_endpoint_group as _vpn_endpoint_group
from openstack.network.v2 import vpn_ike_policy as _ike_policy
from openstack.network.v2 import vpn_ipsec_policy as _ipsec_policy
from openstack.network.v2 import (
    vpn_ipsec_site_connection as _ipsec_site_connection,
)
from openstack.network.v2 import vpn_service as _vpn_service
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):
    _resource_registry = {
        "address_group": _address_group.AddressGroup,
        "address_scope": _address_scope.AddressScope,
        "agent": _agent.Agent,
        "auto_allocated_topology": (
            _auto_allocated_topology.AutoAllocatedTopology
        ),
        "availability_zone": availability_zone.AvailabilityZone,
        "bgp_peer": _bgp_peer.BgpPeer,
        "bgp_speaker": _bgp_speaker.BgpSpeaker,
        "bgpvpn": _bgpvpn.BgpVpn,
        "bgpvpn_network_association": (
            _bgpvpn_network_association.BgpVpnNetworkAssociation
        ),
        "bgpvpn_port_association": (
            _bgpvpn_port_association.BgpVpnPortAssociation
        ),
        "bgpvpn_router_association": (
            _bgpvpn_router_association.BgpVpnRouterAssociation
        ),
        "default_security_group_rule": (
            _default_security_group_rule.DefaultSecurityGroupRule
        ),
        "extension": extension.Extension,
        "firewall_group": _firewall_group.FirewallGroup,
        "firewall_policy": _firewall_policy.FirewallPolicy,
        "firewall_rule": _firewall_rule.FirewallRule,
        "flavor": _flavor.Flavor,
        "floating_ip": _floating_ip.FloatingIP,
        "health_monitor": _health_monitor.HealthMonitor,
        "l3_conntrack_helper": _l3_conntrack_helper.ConntrackHelper,
        "listener": _listener.Listener,
        "load_balancer": _load_balancer.LoadBalancer,
        "local_ip": _local_ip.LocalIP,
        "local_ip_association": _local_ip_association.LocalIPAssociation,
        "metering_label": _metering_label.MeteringLabel,
        "metering_label_rule": _metering_label_rule.MeteringLabelRule,
        "ndp_proxy": _ndp_proxy.NDPProxy,
        "network": _network.Network,
        "network_ip_availability": (
            network_ip_availability.NetworkIPAvailability
        ),
        "network_segment_range": _network_segment_range.NetworkSegmentRange,
        "pool": _pool.Pool,
        "pool_member": _pool_member.PoolMember,
        "port": _port.Port,
        "port_forwarding": _port_forwarding.PortForwarding,
        "qos_bandwidth_limit_rule": (
            _qos_bandwidth_limit_rule.QoSBandwidthLimitRule
        ),
        "qos_dscp_marking_rule": _qos_dscp_marking_rule.QoSDSCPMarkingRule,
        "qos_minimum_bandwidth_rule": (
            _qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule
        ),
        "qos_minimum_packet_rate_rule": (
            _qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule
        ),
        "qos_policy": _qos_policy.QoSPolicy,
        "qos_rule_type": _qos_rule_type.QoSRuleType,
        "quota": _quota.Quota,
        "rbac_policy": _rbac_policy.RBACPolicy,
        "router": _router.Router,
        "security_group": _security_group.SecurityGroup,
        "security_group_rule": _security_group_rule.SecurityGroupRule,
        "segment": _segment.Segment,
        "service_profile": _service_profile.ServiceProfile,
        "service_provider": _service_provider.ServiceProvider,
        "sfc_flow_classifier": _sfc_flow_classifier.SfcFlowClassifier,
        "sfc_port_chain": _sfc_port_chain.SfcPortChain,
        "sfc_port_pair": _sfc_port_pair.SfcPortPair,
        "sfc_port_pair_group": _sfc_port_pair_group.SfcPortPairGroup,
        "sfc_service_graph": _sfc_sservice_graph.SfcServiceGraph,
        "subnet": _subnet.Subnet,
        "subnet_pool": _subnet_pool.SubnetPool,
        "tap_flow": _tap_flow.TapFlow,
        "tap_mirror": _tap_mirror.TapMirror,
        "tap_service": _tap_service.TapService,
        "trunk": _trunk.Trunk,
        "vpn_endpoint_group": _vpn_endpoint_group.VpnEndpointGroup,
        "vpn_ike_policy": _ike_policy.VpnIkePolicy,
        "vpn_ipsec_policy": _ipsec_policy.VpnIpsecPolicy,
        "vpn_ipsec_site_connection": (
            _ipsec_site_connection.VpnIPSecSiteConnection
        ),
        "vpn_service": _vpn_service.VpnService,
    }

    def _update(
        self,
        resource_type: type[resource.ResourceT],
        value: ty.Union[str, resource.ResourceT, None],
        base_path: ty.Optional[str] = None,
        if_revision: ty.Optional[int] = None,
        **attrs: ty.Any,
    ) -> resource.ResourceT:
        if (
            issubclass(resource_type, _base.NetworkResource)
            and if_revision is not None
        ):
            attrs.update({'if_match': f'revision_number={if_revision}'})

        res = self._get_resource(resource_type, value, **attrs)

        return res.commit(self, base_path=base_path)

    def _delete(
        self,
        resource_type: type[resource.ResourceT],
        value: ty.Union[str, resource.ResourceT, None],
        ignore_missing: bool = True,
        if_revision: ty.Optional[int] = None,
        **attrs: ty.Any,
    ) -> ty.Optional[resource.ResourceT]:
        if (
            issubclass(resource_type, _base.NetworkResource)
            and if_revision is not None
        ):
            attrs.update({'if_match': f'revision_number={if_revision}'})

        res = self._get_resource(resource_type, value, **attrs)

        try:
            rv = res.delete(self)
        except exceptions.NotFoundException:
            if ignore_missing:
                return None
            raise

        return rv

    def create_address_group(self, **attrs):
        """Create a new address group from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.address_group.AddressGroup`,
            comprised of the properties on the AddressGroup class.

        :returns: The results of address group creation
        :rtype: :class:`~openstack.network.v2.address_group.AddressGroup`
        """
        return self._create(_address_group.AddressGroup, **attrs)

    def delete_address_group(self, address_group, ignore_missing=True):
        """Delete an address group

        :param address_group: The value can be either the ID of an
            address group or
            a :class:`~openstack.network.v2.address_group.AddressGroup`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will
            be raised when the address group does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent address group.

        :returns: ``None``
        """
        self._delete(
            _address_group.AddressGroup,
            address_group,
            ignore_missing=ignore_missing,
        )

    def find_address_group(self, name_or_id, ignore_missing=True, **query):
        """Find a single address group

        :param name_or_id: The name or ID of an address group.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.address_group.AddressGroup`
            or None
        """
        return self._find(
            _address_group.AddressGroup,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_address_group(self, address_group):
        """Get a single address group

        :param address_group: The value can be the ID of an address group or a
            :class:`~openstack.network.v2.address_group.AddressGroup` instance.

        :returns: One :class:`~openstack.network.v2.address_group.AddressGroup`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_address_group.AddressGroup, address_group)

    def address_groups(self, **query):
        """Return a generator of address groups

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

            * ``name``: Address group name
            * ``description``: Address group description
            * ``project_id``: Owner project ID

        :returns: A generator of address group objects
        :rtype: :class:`~openstack.network.v2.address_group.AddressGroup`
        """
        return self._list(_address_group.AddressGroup, **query)

    def update_address_group(
        self,
        address_group: ty.Union[str, _address_group.AddressGroup],
        **attrs: ty.Any,
    ) -> _address_group.AddressGroup:
        """Update an address group

        :param address_group: Either the ID of an address group or a
            :class:`~openstack.network.v2.address_group.AddressGroup` instance.
        :param attrs: The attributes to update on the address group
            represented by ``value``.

        :returns: The updated address group
        :rtype: :class:`~openstack.network.v2.address_group.AddressGroup`
        """
        return self._update(
            _address_group.AddressGroup, address_group, **attrs
        )

    def add_addresses_to_address_group(self, address_group, addresses):
        """Add addresses to a address group

        :param address_group: Either the ID of an address group or a
            :class:`~openstack.network.v2.address_group.AddressGroup` instance.
        :param list addresses: List of address strings.
        :returns: AddressGroup with updated addresses
        :rtype: :class:`~openstack.network.v2.address_group.AddressGroup`
        """
        ag = self._get_resource(_address_group.AddressGroup, address_group)
        return ag.add_addresses(self, addresses)

    def remove_addresses_from_address_group(self, address_group, addresses):
        """Remove addresses from a address group

        :param address_group: Either the ID of an address group or a
            :class:`~openstack.network.v2.address_group.AddressGroup` instance.
        :param list addresses: List of address strings.
        :returns: AddressGroup with updated addresses
        :rtype: :class:`~openstack.network.v2.address_group.AddressGroup`
        """
        ag = self._get_resource(_address_group.AddressGroup, address_group)
        return ag.remove_addresses(self, addresses)

    def create_address_scope(self, **attrs):
        """Create a new address scope from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.address_scope.AddressScope`,
            comprised of the properties on the AddressScope class.

        :returns: The results of address scope creation
        :rtype: :class:`~openstack.network.v2.address_scope.AddressScope`
        """
        return self._create(_address_scope.AddressScope, **attrs)

    def delete_address_scope(self, address_scope, ignore_missing=True):
        """Delete an address scope

        :param address_scope: The value can be either the ID of an
            address scope or
            a :class:`~openstack.network.v2.address_scope.AddressScope`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the address scope does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent address scope.

        :returns: ``None``
        """
        self._delete(
            _address_scope.AddressScope,
            address_scope,
            ignore_missing=ignore_missing,
        )

    def find_address_scope(self, name_or_id, ignore_missing=True, **query):
        """Find a single address scope

        :param name_or_id: The name or ID of an address scope.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.address_scope.AddressScope`
            or None
        """
        return self._find(
            _address_scope.AddressScope,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_address_scope(self, address_scope):
        """Get a single address scope

        :param address_scope: The value can be the ID of an address scope or a
            :class:`~openstack.network.v2.address_scope.AddressScope` instance.

        :returns: One :class:`~openstack.network.v2.address_scope.AddressScope`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_address_scope.AddressScope, address_scope)

    def address_scopes(self, **query):
        """Return a generator of address scopes

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

            * ``name``: Address scope name
            * ``ip_version``: Address scope IP address version
            * ``tenant_id``: Owner tenant ID
            * ``shared``: Address scope is shared (boolean)

        :returns: A generator of address scope objects
        :rtype: :class:`~openstack.network.v2.address_scope.AddressScope`
        """
        return self._list(_address_scope.AddressScope, **query)

    def update_address_scope(self, address_scope, **attrs):
        """Update an address scope

        :param address_scope: Either the ID of an address scope or a
            :class:`~openstack.network.v2.address_scope.AddressScope` instance.
        :param attrs: The attributes to update on the address scope
            represented by ``value``.

        :returns: The updated address scope
        :rtype: :class:`~openstack.network.v2.address_scope.AddressScope`
        """
        return self._update(
            _address_scope.AddressScope, address_scope, **attrs
        )

    def agents(self, **query):
        """Return a generator of network agents

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * ``agent_type``: Agent type.
            * ``availability_zone``: The availability zone for an agent.
            * ``binary``: The name of the agent's application binary.
            * ``description``: The description of the agent.
            * ``host``: The host (host name or host address) the agent is
              running on.
            * ``topic``: The message queue topic used.
            * ``is_admin_state_up``: The administrative state of the agent.
            * ``is_alive``: Whether the agent is alive.

        :returns: A generator of agents
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        """
        return self._list(_agent.Agent, **query)

    def delete_agent(self, agent, ignore_missing=True):
        """Delete a network agent

        :param agent: The value can be the ID of a agent or a
            :class:`~openstack.network.v2.agent.Agent` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the agent does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent agent.

        :returns: ``None``
        """
        self._delete(_agent.Agent, agent, ignore_missing=ignore_missing)

    def get_agent(self, agent):
        """Get a single network agent

        :param agent: The value can be the ID of a agent or a
            :class:`~openstack.network.v2.agent.Agent` instance.

        :returns: One :class:`~openstack.network.v2.agent.Agent`
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_agent.Agent, agent)

    def update_agent(self, agent, **attrs):
        """Update a network agent

        :param agent: The value can be the ID of a agent or a
            :class:`~openstack.network.v2.agent.Agent` instance.
        :param attrs: The attributes to update on the agent represented
            by ``value``.

        :returns: One :class:`~openstack.network.v2.agent.Agent`
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        """
        return self._update(_agent.Agent, agent, **attrs)

    def dhcp_agent_hosting_networks(self, agent, **query):
        """A generator of networks hosted by a DHCP agent.

        :param agent: Either the agent id of an instance of
            :class:`~openstack.network.v2.network_agent.Agent`
        :param query: kwargs query: Optional query parameters to be sent
            to limit the resources being returned.
        :return: A generator of networks
        """
        agent_obj = self._get_resource(_agent.Agent, agent)
        return self._list(
            _network.DHCPAgentHostingNetwork, agent_id=agent_obj.id, **query
        )

    def add_dhcp_agent_to_network(self, agent, network):
        """Add a DHCP Agent to a network

        :param agent: Either the agent id of an instance of
            :class:`~openstack.network.v2.network_agent.Agent`
        :param network: Network instance
        :return:
        """
        network = self._get_resource(_network.Network, network)
        agent = self._get_resource(_agent.Agent, agent)
        return agent.add_agent_to_network(self, network.id)

    def remove_dhcp_agent_from_network(self, agent, network):
        """Remove a DHCP Agent from a network

        :param agent: Either the agent id of an instance of
            :class:`~openstack.network.v2.network_agent.Agent`
        :param network: Network instance
        :return:
        """
        network = self._get_resource(_network.Network, network)
        agent = self._get_resource(_agent.Agent, agent)
        return agent.remove_agent_from_network(self, network.id)

    def network_hosting_dhcp_agents(self, network, **query):
        """A generator of DHCP agents hosted on a network.

        :param network: The instance of
            :class:`~openstack.network.v2.network.Network`
        :param dict query: Optional query parameters to be sent to limit the
            resources returned.
        :return: A generator of hosted DHCP agents
        """
        net = self._get_resource(_network.Network, network)
        return self._list(
            _agent.NetworkHostingDHCPAgent, network_id=net.id, **query
        )

    def get_auto_allocated_topology(self, project=None):
        """Get the auto-allocated topology of a given tenant

        :param project:
            The value is the ID or name of a project

        :returns: The auto-allocated topology
        :rtype:
            :class:`~openstack.network.v2.auto_allocated_topology.AutoAllocatedTopology`
        """

        # If project option is not given, grab project id from session
        if project is None:
            project = self.get_project_id()
        return self._get(
            _auto_allocated_topology.AutoAllocatedTopology, project
        )

    def delete_auto_allocated_topology(
        self, project=None, ignore_missing=False
    ):
        """Delete auto-allocated topology

        :param project:
            The value is the ID or name of a project
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the topology does not exist.
            When set to ``True``, no exception will be raised when
            attempting to delete nonexistant topology

        :returns: ``None``
        """

        # If project option is not given, grab project id from session
        if project is None:
            project = self.get_project_id()
        self._delete(
            _auto_allocated_topology.AutoAllocatedTopology,
            project,
            ignore_missing=ignore_missing,
        )

    def validate_auto_allocated_topology(self, project=None):
        """Validate the resources for auto allocation

        :param project:
            The value is the ID or name of a project

        :returns: Whether all resources are correctly configured or not
        :rtype:
            :class:`~openstack.network.v2.auto_allocated_topology.ValidateTopology`
        """

        # If project option is not given, grab project id from session
        if project is None:
            project = self.get_project_id()
        return self._get(
            _auto_allocated_topology.ValidateTopology,
            project=project,
            requires_id=False,
        )

    def availability_zones(self, **query):
        """Return a generator of availability zones

        :param dict query: optional query parameters to be set to limit the
            returned resources. Valid parameters include:

            * ``name``: The name of an availability zone.
            * ``resource``: The type of resource for the availability zone.

        :returns: A generator of availability zone objects
        :rtype:
            :class:`~openstack.network.v2.availability_zone.AvailabilityZone`
        """
        return self._list(availability_zone.AvailabilityZone)

    def create_bgp_peer(self, **attrs):
        """Create a new BGP Peer from attributes"""
        return self._create(_bgp_peer.BgpPeer, **attrs)

    def delete_bgp_peer(self, peer, ignore_missing=True):
        """Delete a BGP Peer"""
        self._delete(_bgp_peer.BgpPeer, peer, ignore_missing=ignore_missing)

    def find_bgp_peer(self, name_or_id, ignore_missing=True, **query):
        """Find a single BGP Peer"""
        return self._find(
            _bgp_peer.BgpPeer,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_bgp_peer(self, peer):
        """Get a signle BGP Peer"""
        return self._get(_bgp_peer.BgpPeer, peer)

    def update_bgp_peer(self, peer, **attrs):
        """Update a BGP Peer"""
        return self._update(_bgp_peer.BgpPeer, peer, **attrs)

    def bgp_peers(self, **query):
        """Return a generator of BGP Peers"""
        return self._list(_bgp_peer.BgpPeer, **query)

    def create_bgp_speaker(self, **attrs):
        """Create a new BGP Speaker"""
        return self._create(_bgp_speaker.BgpSpeaker, **attrs)

    def delete_bgp_speaker(self, speaker, ignore_missing=True):
        """Delete a BGP Speaker"""
        self._delete(
            _bgp_speaker.BgpSpeaker, speaker, ignore_missing=ignore_missing
        )

    def find_bgp_speaker(self, name_or_id, ignore_missing=True, **query):
        """Find a single BGP Peer"""
        return self._find(
            _bgp_speaker.BgpSpeaker,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_bgp_speaker(self, speaker):
        """Get a signle BGP Speaker"""
        return self._get(_bgp_speaker.BgpSpeaker, speaker)

    def update_bgp_speaker(self, speaker, **attrs):
        """Update a BGP Speaker"""
        return self._update(_bgp_speaker.BgpSpeaker, speaker, **attrs)

    def bgp_speakers(self, **query):
        """Return a generator of BGP Peers"""
        return self._list(_bgp_speaker.BgpSpeaker, **query)

    def add_bgp_peer_to_speaker(self, speaker, peer_id):
        """Bind the BGP peer to the specified BGP Speaker."""
        speaker = self._get_resource(_bgp_speaker.BgpSpeaker, speaker)
        return speaker.add_bgp_peer(self, peer_id)

    def remove_bgp_peer_from_speaker(self, speaker, peer_id):
        """Unbind the BGP peer from a BGP Speaker."""
        speaker = self._get_resource(_bgp_speaker.BgpSpeaker, speaker)
        return speaker.remove_bgp_peer(self, peer_id)

    def add_gateway_network_to_speaker(self, speaker, network_id):
        """Add a network to the specified BGP speaker."""
        speaker = self._get_resource(_bgp_speaker.BgpSpeaker, speaker)
        return speaker.add_gateway_network(self, network_id)

    def remove_gateway_network_from_speaker(self, speaker, network_id):
        """Remove a network from the specified BGP speaker."""
        speaker = self._get_resource(_bgp_speaker.BgpSpeaker, speaker)
        return speaker.remove_gateway_network(self, network_id)

    def get_advertised_routes_of_speaker(self, speaker):
        """List all routes advertised by the specified BGP Speaker."""
        speaker = self._get_resource(_bgp_speaker.BgpSpeaker, speaker)
        return speaker.get_advertised_routes(self)

    def get_bgp_dragents_hosting_speaker(self, speaker):
        """List all BGP dynamic agents which are hosting the
        specified BGP Speaker."""
        speaker = self._get_resource(_bgp_speaker.BgpSpeaker, speaker)
        return speaker.get_bgp_dragents(self)

    def add_bgp_speaker_to_dragent(self, bgp_agent, bgp_speaker_id):
        """Add a BGP Speaker to the specified dynamic routing agent."""
        speaker = self._get_resource(_bgp_speaker.BgpSpeaker, bgp_speaker_id)
        speaker.add_bgp_speaker_to_dragent(self, bgp_agent)

    def get_bgp_speakers_hosted_by_dragent(self, bgp_agent):
        """List all BGP Seakers hosted on the specified dynamic routing
        agent."""
        agent = self._get_resource(_agent.Agent, bgp_agent)
        return agent.get_bgp_speakers_hosted_by_dragent(self)

    def remove_bgp_speaker_from_dragent(self, bgp_agent, bgp_speaker_id):
        """Delete the BGP Speaker hosted by the specified dynamic
        routing agent."""
        speaker = self._get_resource(_bgp_speaker.BgpSpeaker, bgp_speaker_id)
        speaker.remove_bgp_speaker_from_dragent(self, bgp_agent)

    def create_bgpvpn(self, **attrs):
        """Create a new BGPVPN

        :param attrs: Keyword arguments which will be used to create a
             :class:`~openstack.network.v2.bgpvpn.BgpVpn`, comprised of the
             properties on the BGPVPN class, for details see the Neutron
             api-ref.

        :returns: The result of BGPVPN creation
        :rtype: :class:`~openstack.network.v2.bgpvpn.BgpVpn`
        """
        return self._create(_bgpvpn.BgpVpn, **attrs)

    def delete_bgpvpn(self, bgpvpn, ignore_missing=True):
        """Delete a BGPVPN

        :param bgpvpn: The value can be either the ID of a bgpvpn or
            a :class:`~openstack.network.v2.bgpvpn.BgpVpn`  instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the BGPVPN does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent BGPVPN.

        :returns: ``None``
        """
        self._delete(_bgpvpn.BgpVpn, bgpvpn, ignore_missing=ignore_missing)

    def find_bgpvpn(self, name_or_id, ignore_missing=True, **query):
        """Find a single BGPVPN

        :param name_or_id: The name or ID of a BGPVPN.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.bgpvpn.BGPVPN`
            or None
        """
        return self._find(
            _bgpvpn.BgpVpn, name_or_id, ignore_missing=ignore_missing, **query
        )

    def get_bgpvpn(self, bgpvpn):
        """Get a signle BGPVPN

        :param bgpvpn: The value can be the ID of a BGPVPN or a
            :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.

        :returns: One :class:`~openstack.network.v2.bgpvpn.BgpVpn`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_bgpvpn.BgpVpn, bgpvpn)

    def update_bgpvpn(self, bgppvpn, **attrs):
        """Update a BGPVPN

        :param bgpvpn: Either the ID of a BGPVPN or a
            :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.
        :param attrs: The attributes to update on the BGPVPN represented
            by ``value``.

        :returns: The updated BGPVPN
        :rtype: :class:`~openstack.network.v2.bgpvpn.BgpVpn`
        """
        return self._update(_bgpvpn.BgpVpn, bgppvpn, **attrs)

    def bgpvpns(self, **query):
        """Return a generator of BGP VPNs

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of BgpVPN objects
        :rtype: :class:`~openstack.network.v2.bgpvpn.BgpVpn`
        """
        return self._list(_bgpvpn.BgpVpn, **query)

    def create_bgpvpn_network_association(self, bgpvpn, **attrs):
        """Create a new BGPVPN Network Association

        :param bgpvpn: The value can be either the ID of a bgpvpn or
            a :class:`~openstack.network.v2.bgpvpn.BgpVpn`  instance.
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.bgpvpn_network_association.
            BgpVpnNetworkAssociation`,
            comprised of the properties on the BgpVpnNetworkAssociation class.

        :returns: The results of BgpVpnNetworkAssociation creation
        :rtype: :class:`~openstack.network.v2.bgpvpn_network_association.
            BgpVpnNetworkAssociation`
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._create(
            _bgpvpn_network_association.BgpVpnNetworkAssociation,
            bgpvpn_id=bgpvpn_res.id,
            **attrs,
        )

    def delete_bgpvpn_network_association(
        self, bgpvpn, net_association, ignore_missing=True
    ):
        """Delete a BGPVPN Network Association

        :param bgpvpn: The value can be either the ID of a bgpvpn or
            a :class:`~openstack.network.v2.bgpvpn.BgpVpn`  instance.
        :param net_association: The value can be either the ID of a
            bgpvpn_network_association or
            a :class:`~openstack.network.v2.bgpvpn_network_association.
            BgpVpnNetworkAssociation` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the BgpVpnNetworkAssociation does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent BgpVpnNetworkAssociation.

        :returns: ``None``
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        self._delete(
            _bgpvpn_network_association.BgpVpnNetworkAssociation,
            net_association,
            ignore_missing=ignore_missing,
            bgpvpn_id=bgpvpn_res.id,
        )

    def get_bgpvpn_network_association(self, bgpvpn, net_association):
        """Get a signle BGPVPN Network Association

        :param bgpvpn: The value can be the ID of a BGPVPN or a
            :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.
        :param net_association: The value can be the ID of a
            BgpVpnNetworkAssociation or a
            :class:`~openstack.network.v2.bgpvpn_network_association.
            BgpVpnNetworkAssociation` instance.

        :returns: One :class:`~openstack.network.v2.
           bgpvpn_network_associaition.BgpVpnNetworkAssociation`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._get(
            _bgpvpn_network_association.BgpVpnNetworkAssociation,
            net_association,
            bgpvpn_id=bgpvpn_res.id,
        )

    def bgpvpn_network_associations(self, bgpvpn, **query):
        """Return a generator of BGP VPN Network Associations

        :param: bgpvpn: The value can be the ID of a BGPVPN or a
            :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.
        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of BgpVpnNetworkAssociation objects
        :rtype: :class:`~openstack.network.v2.bgpvpn_network_association.
            BgpVpnNetworkAssociation`
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._list(
            _bgpvpn_network_association.BgpVpnNetworkAssociation,
            bgpvpn_id=bgpvpn_res.id,
            **query,
        )

    def create_bgpvpn_port_association(self, bgpvpn, **attrs):
        """Create a new BGPVPN Port Association

        :param bgpvpn: The value can be either the ID of a bgpvpn or
            a :class:`~openstack.network.v2.bgpvpn.BgpVpn`  instance.
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.bgpvpn_port_association.
            BgpVpnPortAssociation`,
            comprised of the properties on the BgpVpnPortAssociation class.

        :returns: The results of BgpVpnPortAssociation creation
        :rtype: :class:`~openstack.network.v2.bgpvpn_port_association.
            BgpVpnPortAssociation`
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._create(
            _bgpvpn_port_association.BgpVpnPortAssociation,
            bgpvpn_id=bgpvpn_res.id,
            **attrs,
        )

    def delete_bgpvpn_port_association(
        self, bgpvpn, port_association, ignore_missing=True
    ):
        """Delete a BGPVPN Port Association

        :param bgpvpn: The value can be either the ID of a bgpvpn or
            a :class:`~openstack.network.v2.bgpvpn.BgpVpn`  instance.
        :param port_association: The value can be either the ID of a
            bgpvpn_port_association or
            a :class:`~openstack.network.v2.bgpvpn_port_association.
            BgpVpnPortAssociation` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the BgpVpnPortAssociation does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent BgpVpnPortAssociation.

        :returns: ``None``
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        self._delete(
            _bgpvpn_port_association.BgpVpnPortAssociation,
            port_association,
            ignore_missing=ignore_missing,
            bgpvpn_id=bgpvpn_res.id,
        )

    def find_bgpvpn_port_association(
        self, name_or_id, bgpvpn_id, ignore_missing=True, **query
    ):
        """Find a single BGPVPN Port Association

        :param name_or_id: The name or ID of a BgpVpnNetworkAssociation.
        :param bgpvpn_id: The value can be the ID of a BGPVPN.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.bgpvpn.BGPVPN`
            or None
        """
        return self._find(
            _bgpvpn_port_association.BgpVpnPortAssociation,
            name_or_id,
            ignore_missing=ignore_missing,
            bgpvpn_id=bgpvpn_id,
            **query,
        )

    def get_bgpvpn_port_association(self, bgpvpn, port_association):
        """Get a signle BGPVPN Port Association

        :param bgpvpn: The value can be the ID of a BGPVPN or a
            :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.
        :param port_association: The value can be the ID of a
            BgpVpnPortAssociation or a
            :class:`~openstack.network.v2.bgpvpn_port_association.
            BgpVpnPortAssociation` instance.

        :returns: One :class:`~openstack.network.v2.
           bgpvpn_port_associaition.BgpVpnPortAssociation`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._get(
            _bgpvpn_port_association.BgpVpnPortAssociation,
            port_association,
            bgpvpn_id=bgpvpn_res.id,
        )

    def update_bgpvpn_port_association(
        self, bgpvpn, port_association, **attrs
    ):
        """Update a BPGPN Port Association

        :param bgpvpn: Either the ID of a BGPVPN or a
            :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.
        :param port_association:  The value can be the ID of a
            BgpVpnPortAssociation or a
            :class:`~openstack.network.v2.bgpvpn_port_association.
            BgpVpnPortAssociation` instance.
        :param attrs: The attributes to update on the BGPVPN represented
            by ``value``.

        :returns: The updated BgpVpnPortAssociation.
        :rtype: :class:`~openstack.network.v2.bgpvpn.BgpVpn`
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._update(
            _bgpvpn_port_association.BgpVpnPortAssociation,
            port_association,
            bgpvpn_id=bgpvpn_res.id,
            **attrs,
        )

    def bgpvpn_port_associations(self, bgpvpn, **query):
        """Return a generator of BGP VPN Port Associations

        :param: bgpvpn: The value can be the ID of a BGPVPN or a
            :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.
        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of BgpVpnNetworkAssociation objects
        :rtype: :class:`~openstack.network.v2.bgpvpn_network_association.
            BgpVpnNetworkAssociation`
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._list(
            _bgpvpn_port_association.BgpVpnPortAssociation,
            bgpvpn_id=bgpvpn_res.id,
            **query,
        )

    def create_bgpvpn_router_association(self, bgpvpn, **attrs):
        """Create a new BGPVPN Router Association

        :param bgpvpn: The value can be either the ID of a bgpvpn or
            a :class:`~openstack.network.v2.bgpvpn.BgpVpn`  instance.
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.bgpvpn_router_association.
            BgpVpnRouterAssociation`,
            comprised of the properties on the BgpVpnRouterAssociation class.

        :returns: The results of BgpVpnRouterAssociation creation
        :rtype: :class:`~openstack.network.v2.bgpvpn_router_association.
            BgpVpnRouterAssociation`
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._create(
            _bgpvpn_router_association.BgpVpnRouterAssociation,
            bgpvpn_id=bgpvpn_res.id,
            **attrs,
        )

    def delete_bgpvpn_router_association(
        self, bgpvpn, router_association, ignore_missing=True
    ):
        """Delete a BGPVPN Router Association

        :param bgpvpn: The value can be either the ID of a bgpvpn or
            a :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.
        :param port_association: The value can be either the ID of a
            bgpvpn_router_association or
            a :class:`~openstack.network.v2.bgpvpn_router_association.
            BgpVpnRouterAssociation` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the BgpVpnRouterAssociation does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent BgpVpnRouterAsociation.

        :returns: ``None``
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        self._delete(
            _bgpvpn_router_association.BgpVpnRouterAssociation,
            router_association,
            ignore_missing=ignore_missing,
            bgpvpn_id=bgpvpn_res.id,
        )

    def get_bgpvpn_router_association(self, bgpvpn, router_association):
        """Get a signle BGPVPN Router Association

        :param bgpvpn: The value can be the ID of a BGPVPN or a
            :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.
        :param router_association: The value can be the ID of a
            BgpVpnRouterAssociation or a
            :class:`~openstack.network.v2.bgpvpn_router_association.
            BgpVpnRouterAssociation` instance.

        :returns: One :class:`~openstack.network.v2.
           bgpvpn_router_associaition.BgpVpnRouterAssociation`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._get(
            _bgpvpn_router_association.BgpVpnRouterAssociation,
            router_association,
            bgpvpn_id=bgpvpn_res.id,
        )

    def update_bgpvpn_router_association(
        self, bgpvpn, router_association, **attrs
    ):
        """Update a BPGPN Router Association

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of BgpVpnNetworkAssociation objects
        :rtype: :class:`~openstack.network.v2.bgpvpn_network_association.
            BgpVpnNetworkAssociation`
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._update(
            _bgpvpn_router_association.BgpVpnRouterAssociation,
            router_association,
            bgpvpn_id=bgpvpn_res.id,
            **attrs,
        )

    def bgpvpn_router_associations(self, bgpvpn, **query):
        """Return a generator of BGP VPN router Associations

        :param: bgpvpn: The value can be the ID of a BGPVPN or a
            :class:`~openstack.network.v2.bgpvpn.BgpVpn` instance.
        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of BgpVpnRouterAssociation objects
        :rtype: :class:`~openstack.network.v2.bgpvpn_router_association.
            BgpVpnRouterAssociation`
        """
        bgpvpn_res = self._get_resource(_bgpvpn.BgpVpn, bgpvpn)
        return self._list(
            _bgpvpn_router_association.BgpVpnRouterAssociation,
            bgpvpn_id=bgpvpn_res.id,
            **query,
        )

    def find_extension(self, name_or_id, ignore_missing=True, **query):
        """Find a single extension

        :param name_or_id: The name or ID of a extension.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.extension.Extension`
            or None
        """
        return self._find(
            extension.Extension,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def extensions(self, **query):
        """Return a generator of extensions

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Currently no
            parameter is supported.

        :returns: A generator of extension objects
        :rtype: :class:`~openstack.network.v2.extension.Extension`
        """
        return self._list(extension.Extension, **query)

    def create_flavor(self, **attrs):
        """Create a new network service flavor from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.flavor.Flavor`,
            comprised of the properties on the Flavor class.

        :returns: The results of flavor creation
        :rtype: :class:`~openstack.network.v2.flavor.Flavor`
        """
        return self._create(_flavor.Flavor, **attrs)

    def delete_flavor(self, flavor, ignore_missing=True):
        """Delete a network service flavor

        :param flavor:
            The value can be either the ID of a flavor or a
            :class:`~openstack.network.v2.flavor.Flavor` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the flavor does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent flavor.

        :returns: ``None``
        """
        self._delete(_flavor.Flavor, flavor, ignore_missing=ignore_missing)

    def find_flavor(self, name_or_id, ignore_missing=True, **query):
        """Find a single network service flavor

        :param name_or_id: The name or ID of a flavor.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.flavor.Flavor` or None
        """
        return self._find(
            _flavor.Flavor, name_or_id, ignore_missing=ignore_missing, **query
        )

    def get_flavor(self, flavor):
        """Get a single network service flavor

        :param flavor:
            The value can be the ID of a flavor or a
            :class:`~openstack.network.v2.flavor.Flavor` instance.

        :returns: One :class:`~openstack.network.v2.flavor.Flavor`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_flavor.Flavor, flavor)

    def update_flavor(self, flavor, **attrs):
        """Update a network service flavor

        :param flavor: Either the id of a flavor or a
            :class:`~openstack.network.v2.flavor.Flavor` instance.
        :param attrs: The attributes to update on the flavor represented
            by ``flavor``.

        :returns: The updated flavor
        :rtype: :class:`~openstack.network.v2.flavor.Flavor`
        """
        return self._update(_flavor.Flavor, flavor, **attrs)

    def flavors(self, **query):
        """Return a generator of network service flavors

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters
            include:

            * ``description``: The description of a flavor.
            * ``is_enabled``: Whether a flavor is enabled.
            * ``name``: The name of a flavor.
            * ``service_type``: The service type to which a falvor applies.

        :returns: A generator of flavor objects
        :rtype: :class:`~openstack.network.v2.flavor.Flavor`
        """
        return self._list(_flavor.Flavor, **query)

    def associate_flavor_with_service_profile(self, flavor, service_profile):
        """Associate network flavor with service profile.

        :param flavor:
            Either the id of a flavor or a
            :class:`~openstack.network.v2.flavor.Flavor` instance.
        :param service_profile:
            The value can be either the ID of a service profile or a
            :class:`~openstack.network.v2.service_profile.ServiceProfile`
            instance.
        :return:
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        service_profile = self._get_resource(
            _service_profile.ServiceProfile, service_profile
        )
        return flavor.associate_flavor_with_service_profile(
            self, service_profile.id
        )

    def disassociate_flavor_from_service_profile(
        self, flavor, service_profile
    ):
        """Disassociate network flavor from service profile.

        :param flavor:
            Either the id of a flavor or a
            :class:`~openstack.network.v2.flavor.Flavor` instance.
        :param service_profile:
            The value can be either the ID of a service profile or a
            :class:`~openstack.network.v2.service_profile.ServiceProfile`
            instance.
        :return:
        """
        flavor = self._get_resource(_flavor.Flavor, flavor)
        service_profile = self._get_resource(
            _service_profile.ServiceProfile, service_profile
        )
        return flavor.disassociate_flavor_from_service_profile(
            self, service_profile.id
        )

    def create_local_ip(self, **attrs):
        """Create a new local ip from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.local_ip.LocalIP`,
            comprised of the properties on the LocalIP class.

        :returns: The results of local ip creation
        :rtype: :class:`~openstack.network.v2.local_ip.LocalIP`
        """
        return self._create(_local_ip.LocalIP, **attrs)

    def delete_local_ip(self, local_ip, ignore_missing=True, if_revision=None):
        """Delete a local ip

        :param local_ip: The value can be either the ID of a local ip or a
            :class:`~openstack.network.v2.local_ip.LocalIP`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the local ip does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent ip.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.

        :returns: ``None``
        """
        self._delete(
            _local_ip.LocalIP,
            local_ip,
            ignore_missing=ignore_missing,
            if_revision=if_revision,
        )

    def find_local_ip(self, name_or_id, ignore_missing=True, **query):
        """Find a local IP

        :param name_or_id: The name or ID of an local IP.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.local_ip.LocalIP`
            or None
        """
        return self._find(
            _local_ip.LocalIP,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_local_ip(self, local_ip):
        """Get a single local ip

        :param local_ip: The value can be the ID of a local ip or a
            :class:`~openstack.network.v2.local_ip.LocalIP`
            instance.

        :returns: One :class:`~openstack.network.v2.local_ip.LocalIP`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_local_ip.LocalIP, local_ip)

    def local_ips(self, **query):
        """Return a generator of local ips

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

            * ``name``: Local IP name
            * ``description``: Local IP description
            * ``project_id``: Owner project ID
            * ``network_id``: Local IP network
            * ``local_port_id``: Local port ID
            * ``local_ip_address``: The IP address of a Local IP
            * ``ip_mode``: The Local IP mode

        :returns: A generator of local ip objects
        :rtype: :class:`~openstack.network.v2.local_ip.LocalIP`
        """
        return self._list(_local_ip.LocalIP, **query)

    def update_local_ip(self, local_ip, if_revision=None, **attrs):
        """Update a local ip

        :param local_ip: Either the id of a local ip or a
            :class:`~openstack.network.v2.local_ip.LocalIP`
            instance.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.
        :param attrs: The attributes to update on the ip represented
            by ``value``.

        :returns: The updated ip
        :rtype: :class:`~openstack.network.v2.local_ip.LocalIP`
        """
        return self._update(
            _local_ip.LocalIP, local_ip, if_revision=if_revision, **attrs
        )

    def create_local_ip_association(self, local_ip, **attrs):
        """Create a new local ip association from attributes

        :param local_ip: The value can be the ID of a Local IP or a
            :class:`~openstack.network.v2.local_ip.LocalIP`
            instance.
        :param attrs: Keyword arguments which will be used to create
            a
            :class:`~openstack.network.v2.local_ip_association.LocalIPAssociation`,
            comprised of the properties on the LocalIP class.

        :returns: The results of local ip association creation
        :rtype:
            :class:`~openstack.network.v2.local_ip_association.LocalIPAssociation`
        """
        local_ip = self._get_resource(_local_ip.LocalIP, local_ip)
        return self._create(
            _local_ip_association.LocalIPAssociation,
            local_ip_id=local_ip.id,
            **attrs,
        )

    def delete_local_ip_association(
        self, local_ip, fixed_port_id, ignore_missing=True, if_revision=None
    ):
        """Delete a local ip association

        :param local_ip: The value can be the ID of a Local IP or a
            :class:`~openstack.network.v2.local_ip.LocalIP`
            instance.
        :param fixed_port_id: The value can be either the fixed port ID
            or a :class:
            `~openstack.network.v2.local_ip_association.LocalIPAssociation`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the local ip association does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent ip.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.

        :returns: ``None``
        """
        local_ip = self._get_resource(_local_ip.LocalIP, local_ip)
        self._delete(
            _local_ip_association.LocalIPAssociation,
            fixed_port_id,
            local_ip_id=local_ip.id,
            ignore_missing=ignore_missing,
            if_revision=if_revision,
        )

    def find_local_ip_association(
        self, name_or_id, local_ip, ignore_missing=True, **query
    ):
        """Find a local ip association

        :param name_or_id: The name or ID of  local ip association.
        :param local_ip: The value can be the ID of a Local IP or a
            :class:`~openstack.network.v2.local_ip.LocalIP`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.local_ip_association.LocalIPAssociation`
            or None
        """
        local_ip = self._get_resource(_local_ip.LocalIP, local_ip)
        return self._find(
            _local_ip_association.LocalIPAssociation,
            name_or_id,
            local_ip_id=local_ip.id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_local_ip_association(self, local_ip_association, local_ip):
        """Get a single local ip association

        :param local_ip: The value can be the ID of a Local IP or a
            :class:`~openstack.network.v2.local_ip.LocalIP`
            instance.
        :param local_ip_association: The value can be the ID
            of a local ip association or a
            :class:`~openstack.network.v2.local_ip_association.LocalIPAssociation`
            instance.

        :returns: One
            :class:`~openstack.network.v2.local_ip_association.LocalIPAssociation`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        local_ip = self._get_resource(_local_ip.LocalIP, local_ip)
        return self._get(
            _local_ip_association.LocalIPAssociation,
            local_ip_association,
            local_ip_id=local_ip.id,
        )

    def local_ip_associations(self, local_ip, **query):
        """Return a generator of local ip associations

        :param local_ip: The value can be the ID of a Local IP or a
            :class:`~openstack.network.v2.local_ip.LocalIP` instance.
        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

            * ``fixed_port_id``: The ID of the port to which a local IP
              is associated
            * ``fixed_ip``: The fixed ip address associated with a
              a Local IP
            * ``host``: Host where local ip is associated

        :returns: A generator of local ip association objects
        :rtype:
            :class:`~openstack.network.v2.local_ip_association.LocalIPAssociation`
        """
        local_ip = self._get_resource(_local_ip.LocalIP, local_ip)
        return self._list(
            _local_ip_association.LocalIPAssociation,
            local_ip_id=local_ip.id,
            **query,
        )

    def create_ip(self, **attrs):
        """Create a new floating ip from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.floating_ip.FloatingIP`,
            comprised of the properties on the FloatingIP class.

        :returns: The results of floating ip creation
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._create(_floating_ip.FloatingIP, **attrs)

    def delete_ip(self, floating_ip, ignore_missing=True, if_revision=None):
        """Delete a floating ip

        :param floating_ip: The value can be either the ID of a floating ip
            or a :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the floating ip does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent ip.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.

        :returns: ``None``
        """
        self._delete(
            _floating_ip.FloatingIP,
            floating_ip,
            ignore_missing=ignore_missing,
            if_revision=if_revision,
        )

    def find_available_ip(self):
        """Find an available IP

        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
            or None
        """
        return _floating_ip.FloatingIP.find_available(self)

    def find_ip(self, name_or_id, ignore_missing=True, **query):
        """Find a single IP

        :param name_or_id: The name or ID of an IP.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
            or None
        """
        return self._find(
            _floating_ip.FloatingIP,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_ip(self, floating_ip):
        """Get a single floating ip

        :param floating_ip: The value can be the ID of a floating ip or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.

        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_floating_ip.FloatingIP, floating_ip)

    def ips(self, **query):
        """Return a generator of ips

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``description``: The description of a floating IP.
            * ``fixed_ip_address``: The fixed IP address associated with a
              floating IP address.
            * ``floating_ip_address``: The IP address of a floating IP.
            * ``floating_network_id``: The ID of the network associated with
              a floating IP.
            * ``port_id``: The ID of the port to which a floating IP is
              associated.
            * ``project_id``: The ID of the project a floating IP is
              associated with.
            * ``router_id``: The ID of an associated router.
            * ``status``: The status of a floating IP, which can be ``ACTIVE``
              or ``DOWN``.

        :returns: A generator of floating IP objects
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._list(_floating_ip.FloatingIP, **query)

    def update_ip(self, floating_ip, if_revision=None, **attrs):
        """Update a ip

        :param floating_ip: Either the id of a ip or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.
        :param attrs: The attributes to update on the ip represented
            by ``value``.

        :returns: The updated ip
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._update(
            _floating_ip.FloatingIP,
            floating_ip,
            if_revision=if_revision,
            **attrs,
        )

    def create_port_forwarding(self, **attrs):
        """Create a new floating ip port forwarding from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.port_forwarding.PortForwarding`,
            comprised of the properties on the PortForwarding class.

        :returns: The results of port forwarding creation
        :rtype: :class:`~openstack.network.v2.port_forwarding.PortForwarding`
        """
        return self._create(_port_forwarding.PortForwarding, **attrs)

    def get_port_forwarding(self, port_forwarding, floating_ip):
        """Get a single port forwarding

        :param port_forwarding: The value can be the ID of a port forwarding
            or a :class:`~openstack.network.v2.port_forwarding.PortForwarding`
            instance.
        :param floating_ip: The value can be the ID of a Floating IP or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.

        :returns: One
            :class:`~openstack.network.v2.port_forwarding.PortForwarding`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        floating_ip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        return self._get(
            _port_forwarding.PortForwarding,
            port_forwarding,
            floatingip_id=floating_ip.id,
        )

    def find_port_forwarding(
        self, pf_id, floating_ip, ignore_missing=True, **query
    ):
        """Find a single port forwarding

        :param pf_id: The ID of a port forwarding.
        :param floating_ip: The value can be the ID of a Floating IP or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns:
            One :class:`~openstack.network.v2.port_forwarding.PortForwarding`
            or None
        """
        floating_ip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        return self._find(
            _port_forwarding.PortForwarding,
            pf_id,
            floatingip_id=floating_ip.id,
            ignore_missing=ignore_missing,
            **query,
        )

    def delete_port_forwarding(
        self, port_forwarding, floating_ip, ignore_missing=True
    ):
        """Delete a port forwarding

        :param port_forwarding: The value can be the ID of a port forwarding
            or a :class:`~openstack.network.v2.port_forwarding.PortForwarding`
            instance.
        :param floating_ip: The value can be the ID of a Floating IP or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the floating ip does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent ip.

        :returns: ``None``
        """
        fip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        self._delete(
            _port_forwarding.PortForwarding,
            port_forwarding,
            floatingip_id=fip.id,
            ignore_missing=ignore_missing,
        )

    def port_forwardings(self, floating_ip, **query):
        """Return a generator of port forwardings

        :param floating_ip: The value can be the ID of a Floating IP or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``internal_port_id``: The ID of internal port.
            * ``external_port``: The external TCP/UDP/other port number
            * ``protocol``: TCP/UDP/other protocol

        :returns: A generator of port forwarding objects
        :rtype: :class:`~openstack.network.v2.port_forwarding.PortForwarding`
        """
        fip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        return self._list(
            _port_forwarding.PortForwarding, floatingip_id=fip.id, **query
        )

    def update_port_forwarding(self, port_forwarding, floating_ip, **attrs):
        """Update a port forwarding

        :param port_forwarding: The value can be the ID of a port forwarding
            or a :class:`~openstack.network.v2.port_forwarding.PortForwarding`
            instance.
        :param floating_ip: The value can be the ID of a Floating IP or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param attrs: The attributes to update on the ip represented
            by ``value``.

        :returns: The updated port_forwarding
        :rtype: :class:`~openstack.network.v2.port_forwarding.PortForwarding`
        """
        fip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        return self._update(
            _port_forwarding.PortForwarding,
            port_forwarding,
            floatingip_id=fip.id,
            **attrs,
        )

    def create_health_monitor(self, **attrs):
        """Create a new health monitor from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.health_monitor.HealthMonitor`,
            comprised of the properties on the HealthMonitor class.

        :returns: The results of health monitor creation
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._create(_health_monitor.HealthMonitor, **attrs)

    def delete_health_monitor(self, health_monitor, ignore_missing=True):
        """Delete a health monitor

        :param health_monitor: The value can be either the ID of a
            health monitor or a
            :class:`~openstack.network.v2.health_monitor.HealthMonitor`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the health monitor does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent health monitor.

        :returns: ``None``
        """
        self._delete(
            _health_monitor.HealthMonitor,
            health_monitor,
            ignore_missing=ignore_missing,
        )

    def find_health_monitor(self, name_or_id, ignore_missing=True, **query):
        """Find a single health monitor

        :param name_or_id: The name or ID of a health monitor.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.health_monitor.HealthMonitor`
            or None
        """
        return self._find(
            _health_monitor.HealthMonitor,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_health_monitor(self, health_monitor):
        """Get a single health monitor

        :param health_monitor: The value can be the ID of a health monitor or a
            :class:`~openstack.network.v2.health_monitor.HealthMonitor`
            instance.

        :returns: One
            :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_health_monitor.HealthMonitor, health_monitor)

    def health_monitors(self, **query):
        """Return a generator of health monitors

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``delay``: the time in milliseconds between sending probes.
            * ``expected_codes``: The expected HTTP codes for a pssing HTTP(S)
              monitor.
            * ``http_method``: The HTTP method a monitor uses for requests.
            * ``is_admin_state_up``: The administrative state of a health
              monitor.
            * ``max_retries``: The maximum consecutive health probe attempts.
            * ``project_id``: The ID of the project this health monitor is
              associated with.
            * ``timeout``: The maximum number of milliseconds for a monitor to
              wait for a connection to be established before it
              times out.
            * ``type``: The type of probe sent by the load balancer for health
              check, which can be ``PING``, ``TCP``, ``HTTP`` or
              ``HTTPS``.
            * ``url_path``: The path portion of a URI that will be probed.

        :returns: A generator of health monitor objects
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._list(_health_monitor.HealthMonitor, **query)

    def update_health_monitor(self, health_monitor, **attrs):
        """Update a health monitor

        :param health_monitor: Either the id of a health monitor or a
            :class:`~openstack.network.v2.health_monitor.HealthMonitor`
            instance.
        :param attrs: The attributes to update on the health monitor
            represented by ``value``.

        :returns: The updated health monitor
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._update(
            _health_monitor.HealthMonitor, health_monitor, **attrs
        )

    def create_listener(self, **attrs):
        """Create a new listener from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.listener.Listener`,
            comprised of the properties on the Listener class.

        :returns: The results of listener creation
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._create(_listener.Listener, **attrs)

    def delete_listener(self, listener, ignore_missing=True):
        """Delete a listener

        :param listener: The value can be either the ID of a listner or a
            :class:`~openstack.network.v2.listener.Listener` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the listner does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent listener.

        :returns: ``None``
        """
        self._delete(
            _listener.Listener, listener, ignore_missing=ignore_missing
        )

    def find_listener(self, name_or_id, ignore_missing=True, **query):
        """Find a single listener

        :param name_or_id: The name or ID of a listener.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.listener.Listener` or None
        """
        return self._find(
            _listener.Listener,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_listener(self, listener):
        """Get a single listener

        :param listener: The value can be the ID of a listener or a
            :class:`~openstack.network.v2.listener.Listener`
            instance.

        :returns: One :class:`~openstack.network.v2.listener.Listener`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_listener.Listener, listener)

    def listeners(self, **query):
        """Return a generator of listeners

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``connection_limit``: The maximum number of connections
              permitted for the load-balancer.
            * ``default_pool_id``: The ID of the default pool.
            * ``default_tls_container_ref``: A reference to a container of TLS
              secret.
            * ``description``: The description of a listener.
            * ``is_admin_state_up``: The administrative state of the listener.
            * ``name``: The name of a listener.
            * ``project_id``: The ID of the project associated with a listener.
            * ``protocol``: The protocol of the listener.
            * ``protocol_port``: Port the listener will listen to.

        :returns: A generator of listener objects
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._list(_listener.Listener, **query)

    def update_listener(self, listener, **attrs):
        """Update a listener

        :param listener: Either the id of a listener or a
            :class:`~openstack.network.v2.listener.Listener`
            instance.
        :param attrs: The attributes to update on the listener
            represented by ``listener``.

        :returns: The updated listener
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._update(_listener.Listener, listener, **attrs)

    def create_load_balancer(self, **attrs):
        """Create a new load balancer from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.load_balancer.LoadBalancer`,
            comprised of the properties on the LoadBalancer class.

        :returns: The results of load balancer creation
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._create(_load_balancer.LoadBalancer, **attrs)

    def delete_load_balancer(self, load_balancer, ignore_missing=True):
        """Delete a load balancer

        :param load_balancer: The value can be the ID of a load balancer or a
            :class:`~openstack.network.v2.load_balancer.LoadBalancer`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the load balancer does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent load balancer.

        :returns: ``None``
        """
        self._delete(
            _load_balancer.LoadBalancer,
            load_balancer,
            ignore_missing=ignore_missing,
        )

    def find_load_balancer(self, name_or_id, ignore_missing=True, **query):
        """Find a single load balancer

        :param name_or_id: The name or ID of a load balancer.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.load_balancer.LoadBalancer`
            or None
        """
        return self._find(
            _load_balancer.LoadBalancer,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_load_balancer(self, load_balancer):
        """Get a single load balancer

        :param load_balancer: The value can be the ID of a load balancer or a
            :class:`~openstack.network.v2.load_balancer.LoadBalancer`
            instance.

        :returns: One :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_load_balancer.LoadBalancer, load_balancer)

    def load_balancers(self, **query):
        """Return a generator of load balancers

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of load balancer objects
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._list(_load_balancer.LoadBalancer, **query)

    def update_load_balancer(self, load_balancer, **attrs):
        """Update a load balancer

        :param load_balancer: Either the id of a load balancer or a
            :class:`~openstack.network.v2.load_balancer.LoadBalancer`
            instance.
        :param attrs: The attributes to update on the load balancer
            represented by ``load_balancer``.

        :returns: The updated load balancer
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._update(
            _load_balancer.LoadBalancer, load_balancer, **attrs
        )

    def create_metering_label(self, **attrs):
        """Create a new metering label from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.metering_label.MeteringLabel`,
            comprised of the properties on the MeteringLabel class.

        :returns: The results of metering label creation
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._create(_metering_label.MeteringLabel, **attrs)

    def delete_metering_label(self, metering_label, ignore_missing=True):
        """Delete a metering label

        :param metering_label:
            The value can be either the ID of a metering label or a
            :class:`~openstack.network.v2.metering_label.MeteringLabel`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the metering label does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent metering label.

        :returns: ``None``
        """
        self._delete(
            _metering_label.MeteringLabel,
            metering_label,
            ignore_missing=ignore_missing,
        )

    def find_metering_label(self, name_or_id, ignore_missing=True, **query):
        """Find a single metering label

        :param name_or_id: The name or ID of a metering label.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.metering_label.MeteringLabel`
            or None
        """
        return self._find(
            _metering_label.MeteringLabel,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_metering_label(self, metering_label):
        """Get a single metering label

        :param metering_label: The value can be the ID of a metering label or a
            :class:`~openstack.network.v2.metering_label.MeteringLabel`
            instance.

        :returns: One
            :class:`~openstack.network.v2.metering_label.MeteringLabel`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_metering_label.MeteringLabel, metering_label)

    def metering_labels(self, **query):
        """Return a generator of metering labels

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``description``: Description of a metering label.
            * ``name``: Name of a metering label.
            * ``is_shared``: Boolean indicating whether a metering label is
              shared.
            * ``project_id``: The ID of the project a metering label is
              associated with.

        :returns: A generator of metering label objects
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._list(_metering_label.MeteringLabel, **query)

    def update_metering_label(self, metering_label, **attrs):
        """Update a metering label

        :param metering_label: Either the id of a metering label or a
            :class:`~openstack.network.v2.metering_label.MeteringLabel`
            instance.
        :param attrs: The attributes to update on the metering label
            represented by ``metering_label``.

        :returns: The updated metering label
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._update(
            _metering_label.MeteringLabel, metering_label, **attrs
        )

    def create_metering_label_rule(self, **attrs):
        """Create a new metering label rule from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`,
            comprised of the properties on the MeteringLabelRule class.

        :returns: The results of metering label rule creation
        :rtype:
            :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`
        """
        return self._create(_metering_label_rule.MeteringLabelRule, **attrs)

    def delete_metering_label_rule(
        self, metering_label_rule, ignore_missing=True
    ):
        """Delete a metering label rule

        :param metering_label_rule:
            The value can be either the ID of a metering label rule
            or a
            :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the metering label rule does not exist.  When set to ``True``,
            no exception will be set when attempting to delete a nonexistent
            metering label rule.

        :returns: ``None``
        """
        self._delete(
            _metering_label_rule.MeteringLabelRule,
            metering_label_rule,
            ignore_missing=ignore_missing,
        )

    def find_metering_label_rule(
        self, name_or_id, ignore_missing=True, **query
    ):
        """Find a single metering label rule

        :param name_or_id: The name or ID of a metering label rule.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`
            or None
        """
        return self._find(
            _metering_label_rule.MeteringLabelRule,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_metering_label_rule(self, metering_label_rule):
        """Get a single metering label rule

        :param metering_label_rule:
            The value can be the ID of a metering label rule or a
            :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`
            instance.

        :returns: One
            :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metering_label_rule.MeteringLabelRule, metering_label_rule
        )

    def metering_label_rules(self, **query):
        """Return a generator of metering label rules

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``direction``: The direction in which metering label rule is
              applied.
            * ``metering_label_id``: The ID of a metering label this rule is
              associated with.
            * ``project_id``: The ID of the project the metering label rule is
              associated with.
            * ``remote_ip_prefix``: The remote IP prefix to be associated with
              this metering label rule.

        :returns: A generator of metering label rule objects
        :rtype:
            :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`
        """
        return self._list(_metering_label_rule.MeteringLabelRule, **query)

    def update_metering_label_rule(self, metering_label_rule, **attrs):
        """Update a metering label rule

        :param metering_label_rule:
            Either the id of a metering label rule or a
            :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`
            instance.
        :param attrs: The attributes to update on the metering label rule
            represented by ``metering_label_rule``.

        :returns: The updated metering label rule
        :rtype:
            :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`
        """
        return self._update(
            _metering_label_rule.MeteringLabelRule,
            metering_label_rule,
            **attrs,
        )

    def create_network(self, **attrs):
        """Create a new network from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.network.Network`,
            comprised of the properties on the Network class.

        :returns: The results of network creation
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._create(_network.Network, **attrs)

    def delete_network(self, network, ignore_missing=True, if_revision=None):
        """Delete a network

        :param network:
            The value can be either the ID of a network or a
            :class:`~openstack.network.v2.network.Network` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the network does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent network.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.

        :returns: ``None``
        """
        self._delete(
            _network.Network,
            network,
            ignore_missing=ignore_missing,
            if_revision=if_revision,
        )

    def find_network(self, name_or_id, ignore_missing=True, **query):
        """Find a single network

        :param name_or_id: The name or ID of a network.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.network.Network` or None
        """
        return self._find(
            _network.Network,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_network(self, network):
        """Get a single network

        :param network:
            The value can be the ID of a network or a
            :class:`~openstack.network.v2.network.Network` instance.

        :returns: One :class:`~openstack.network.v2.network.Network`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_network.Network, network)

    def networks(self, **query):
        """Return a generator of networks

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``description``: The network description.
            * ``ipv4_address_scope_id``: The ID of the IPv4 address scope for
              the network.
            * ``ipv6_address_scope_id``: The ID of the IPv6 address scope for
              the network.
            * ``is_admin_state_up``: Network administrative state
            * ``is_port_security_enabled``: The port security status.
            * ``is_router_external``: Network is external or not.
            * ``is_shared``: Whether the network is shared across projects.
            * ``name``: The name of the network.
            * ``status``: Network status
            * ``project_id``: Owner tenant ID
            * ``provider_network_type``: Network physical mechanism
            * ``provider_physical_network``: Physical network
            * ``provider_segmentation_id``: VLAN ID for VLAN networks or Tunnel
              ID for GENEVE/GRE/VXLAN networks

        :returns: A generator of network objects
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._list(_network.Network, **query)

    def update_network(self, network, if_revision=None, **attrs):
        """Update a network

        :param network: Either the id of a network or an instance of type
            :class:`~openstack.network.v2.network.Network`.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.
        :param attrs: The attributes to update on the network represented
            by ``network``.

        :returns: The updated network
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._update(
            _network.Network, network, if_revision=if_revision, **attrs
        )

    def find_network_ip_availability(
        self, name_or_id, ignore_missing=True, **query
    ):
        """Find IP availability of a network

        :param name_or_id: The name or ID of a network.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.network_ip_availability.NetworkIPAvailability`
            or None
        """
        return self._find(
            network_ip_availability.NetworkIPAvailability,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_network_ip_availability(self, network):
        """Get IP availability of a network

        :param network:
            The value can be the ID of a network or a
            :class:`~openstack.network.v2.network.Network` instance.

        :returns: One
            :class:`~openstack.network.v2.network_ip_availability.NetworkIPAvailability`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            network_ip_availability.NetworkIPAvailability, network
        )

    def network_ip_availabilities(self, **query):
        """Return a generator of network ip availabilities

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``ip_version``: IP version of the network
            * ``network_id``: ID of network to use when listening network IP
              availability.
            * ``network_name``: The name of the network for the particular
              network IP availability.
            * ``project_id``: Owner tenant ID

        :returns: A generator of network ip availability objects
        :rtype:
            :class:`~openstack.network.v2.network_ip_availability.NetworkIPAvailability`
        """
        return self._list(
            network_ip_availability.NetworkIPAvailability, **query
        )

    def create_network_segment_range(self, **attrs):
        """Create a new network segment range from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.network_segment_range.NetworkSegmentRange`,
            comprised of the properties on the
            NetworkSegmentRange class.

        :returns: The results of network segment range creation
        :rtype:
            :class:`~openstack.network.v2.network_segment_range.NetworkSegmentRange`
        """
        return self._create(
            _network_segment_range.NetworkSegmentRange, **attrs
        )

    def delete_network_segment_range(
        self, network_segment_range, ignore_missing=True
    ):
        """Delete a network segment range

        :param network_segment_range: The value can be either the ID of a
            network segment range or a
            :class:`~openstack.network.v2.network_segment_range.NetworkSegmentRange`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the network segment range does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent network segment range.

        :returns: ``None``
        """
        self._delete(
            _network_segment_range.NetworkSegmentRange,
            network_segment_range,
            ignore_missing=ignore_missing,
        )

    def find_network_segment_range(
        self, name_or_id, ignore_missing=True, **query
    ):
        """Find a single network segment range

        :param name_or_id: The name or ID of a network segment range.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.network_segment_range.NetworkSegmentRange`
            or None
        """
        return self._find(
            _network_segment_range.NetworkSegmentRange,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_network_segment_range(self, network_segment_range):
        """Get a single network segment range

        :param network_segment_range: The value can be the ID of a network
            segment range or a
            :class:`~openstack.network.v2.network_segment_range.NetworkSegmentRange`
            instance.

        :returns: One
            :class:`~openstack.network.v2._network_segment_range.NetworkSegmentRange`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _network_segment_range.NetworkSegmentRange, network_segment_range
        )

    def network_segment_ranges(self, **query):
        """Return a generator of network segment ranges

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``name``: Name of the segments
            * ``default``: The network segment range is loaded from the host
              configuration file.
            * ``shared``: The network segment range is shared with other
              projects
            * ``project_id``: ID of the project that owns the network
              segment range
            * ``network_type``: Network type for the network segment ranges
            * ``physical_network``: Physical network name for the network
              segment ranges
            * ``minimum``: Minimum segmentation ID for the network segment
              ranges
            * ``maximum``: Maximum Segmentation ID for the network segment
              ranges
            * ``used``: Mapping of which segmentation ID in the range is
              used by which tenant
            * ``available``: List of available segmentation IDs in this
              network segment range

        :returns: A generator of network segment range objects
        :rtype:
            :class:`~openstack.network.v2._network_segment_range.NetworkSegmentRange`
        """
        return self._list(_network_segment_range.NetworkSegmentRange, **query)

    def update_network_segment_range(self, network_segment_range, **attrs):
        """Update a network segment range

        :param network_segment_range: Either the ID of a network segment range
            or a
            :class:`~openstack.network.v2._network_segment_range.NetworkSegmentRange`
            instance.
        :param attrs: The attributes to update on the network segment range
            represented by ``network_segment_range``.

        :returns: The updated network segment range
        :rtype:
            :class:`~openstack.network.v2._network_segment_range.NetworkSegmentRange`
        """
        return self._update(
            _network_segment_range.NetworkSegmentRange,
            network_segment_range,
            **attrs,
        )

    def create_pool(self, **attrs):
        """Create a new pool from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.pool.Pool`,
            comprised of the properties on the Pool class.

        :returns: The results of pool creation
        :rtype: :class:`~openstack.network.v2.pool.Pool`
        """
        return self._create(_pool.Pool, **attrs)

    def delete_pool(self, pool, ignore_missing=True):
        """Delete a pool

        :param pool: The value can be either the ID of a pool or a
            :class:`~openstack.network.v2.pool.Pool` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the pool does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent pool.

        :returns: ``None``
        """
        self._delete(_pool.Pool, pool, ignore_missing=ignore_missing)

    def find_pool(self, name_or_id, ignore_missing=True, **query):
        """Find a single pool

        :param name_or_id: The name or ID of a pool.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.pool.Pool` or None
        """
        return self._find(
            _pool.Pool, name_or_id, ignore_missing=ignore_missing, **query
        )

    def get_pool(self, pool):
        """Get a single pool

        :param pool: The value can be the ID of a pool or a
            :class:`~openstack.network.v2.pool.Pool` instance.

        :returns: One :class:`~openstack.network.v2.pool.Pool`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_pool.Pool, pool)

    def pools(self, **query):
        """Return a generator of pools

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``description``: The description for the pool.
            * ``is_admin_state_up``: The administrative state of the pool.
            * ``lb_algorithm``: The load-balancer algorithm used, which is one
              of ``round-robin``, ``least-connections`` and so on.
            * ``name``: The name of the node pool.
            * ``project_id``: The ID of the project the pool is associated
              with.
            * ``protocol``: The protocol used by the pool, which is one of
              ``TCP``, ``HTTP`` or ``HTTPS``.
            * ``provider``: The name of the provider of the load balancer
              service.
            * ``subnet_id``: The subnet on which the members of the pool are
              located.
            * ``virtual_ip_id``: The ID of the virtual IP used.

        :returns: A generator of pool objects
        :rtype: :class:`~openstack.network.v2.pool.Pool`
        """
        return self._list(_pool.Pool, **query)

    def update_pool(self, pool, **attrs):
        """Update a pool

        :param pool: Either the id of a pool or a
            :class:`~openstack.network.v2.pool.Pool` instance.
        :param attrs: The attributes to update on the pool represented
            by ``pool``.

        :returns: The updated pool
        :rtype: :class:`~openstack.network.v2.pool.Pool`
        """
        return self._update(_pool.Pool, pool, **attrs)

    def create_pool_member(self, pool, **attrs):
        """Create a new pool member from attributes

        :param pool: The pool can be either the ID of a pool or a
            :class:`~openstack.network.v2.pool.Pool` instance that
            the member will be created in.
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.pool_member.PoolMember`,
            comprised of the properties on the PoolMember class.

        :returns: The results of pool member creation
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._create(
            _pool_member.PoolMember, pool_id=poolobj.id, **attrs
        )

    def delete_pool_member(self, pool_member, pool, ignore_missing=True):
        """Delete a pool member

        :param pool_member:
            The member can be either the ID of a pool member or a
            :class:`~openstack.network.v2.pool_member.PoolMember` instance.
        :param pool: The pool can be either the ID of a pool or a
            :class:`~openstack.network.v2.pool.Pool` instance that
            the member belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the pool member does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent pool member.

        :returns: ``None``
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        self._delete(
            _pool_member.PoolMember,
            pool_member,
            ignore_missing=ignore_missing,
            pool_id=poolobj.id,
        )

    def find_pool_member(self, name_or_id, pool, ignore_missing=True, **query):
        """Find a single pool member

        :param str name_or_id: The name or ID of a pool member.
        :param pool: The pool can be either the ID of a pool or a
            :class:`~openstack.network.v2.pool.Pool` instance that
            the member belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.pool_member.PoolMember`
            or None
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._find(
            _pool_member.PoolMember,
            name_or_id,
            ignore_missing=ignore_missing,
            pool_id=poolobj.id,
            **query,
        )

    def get_pool_member(self, pool_member, pool):
        """Get a single pool member

        :param pool_member: The member can be the ID of a pool member or a
            :class:`~openstack.network.v2.pool_member.PoolMember`
            instance.
        :param pool: The pool can be either the ID of a pool or a
            :class:`~openstack.network.v2.pool.Pool` instance that
            the member belongs to.

        :returns: One :class:`~openstack.network.v2.pool_member.PoolMember`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._get(
            _pool_member.PoolMember, pool_member, pool_id=poolobj.id
        )

    def pool_members(self, pool, **query):
        """Return a generator of pool members

        :param pool: The pool can be either the ID of a pool or a
            :class:`~openstack.network.v2.pool.Pool` instance that
            the member belongs to.
        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``address``: The IP address of the pool member.
            * ``is_admin_state_up``: The administrative state of the pool
              member.
            * ``name``: Name of the pool member.
            * ``project_id``: The ID of the project this pool member is
              associated with.
            * ``protocol_port``: The port on which the application is hosted.
            * ``subnet_id``: Subnet ID in which to access this pool member.
            * ``weight``: A positive integer value that indicates the relative
              portion of traffic that this member should receive from the
              pool.

        :returns: A generator of pool member objects
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._list(_pool_member.PoolMember, pool_id=poolobj.id, **query)

    def update_pool_member(self, pool_member, pool, **attrs):
        """Update a pool member

        :param pool_member: Either the ID of a pool member or a
            :class:`~openstack.network.v2.pool_member.PoolMember`
            instance.
        :param pool: The pool can be either the ID of a pool or a
            :class:`~openstack.network.v2.pool.Pool` instance that
            the member belongs to.
        :param attrs: The attributes to update on the pool member
            represented by ``pool_member``.

        :returns: The updated pool member
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._update(
            _pool_member.PoolMember, pool_member, pool_id=poolobj.id, **attrs
        )

    def create_port(self, **attrs):
        """Create a new port from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.port.Port`,
            comprised of the properties on the Port class.

        :returns: The results of port creation
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._create(_port.Port, **attrs)

    def create_ports(self, data):
        """Create ports from the list of attributes

        :param list data: List of dicts of attributes which will be used to
            create a :class:`~openstack.network.v2.port.Port`,
            comprised of the properties on the Port class.

        :returns: A generator of port objects
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._bulk_create(_port.Port, data)

    def delete_port(self, port, ignore_missing=True, if_revision=None):
        """Delete a port

        :param port: The value can be either the ID of a port or a
            :class:`~openstack.network.v2.port.Port` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the port does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent port.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.

        :returns: ``None``
        """
        self._delete(
            _port.Port,
            port,
            ignore_missing=ignore_missing,
            if_revision=if_revision,
        )

    def find_port(self, name_or_id, ignore_missing=True, **query):
        """Find a single port

        :param name_or_id: The name or ID of a port.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.port.Port` or None
        """
        return self._find(
            _port.Port, name_or_id, ignore_missing=ignore_missing, **query
        )

    def get_port(self, port):
        """Get a single port

        :param port: The value can be the ID of a port or a
            :class:`~openstack.network.v2.port.Port` instance.

        :returns: One :class:`~openstack.network.v2.port.Port`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_port.Port, port)

    def ports(self, **query):
        """Return a generator of ports

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``description``: The port description.
            * ``device_id``: Port device ID.
            * ``device_owner``: Port device owner (e.g. ``network:dhcp``).
            * ``ip_address``: IP addresses of an allowed address pair.
            * ``is_admin_state_up``: The administrative state of the port.
            * ``is_port_security_enabled``: The port security status.
            * ``mac_address``: Port MAC address.
            * ``name``: The port name.
            * ``network_id``: ID of network that owns the ports.
            * ``project_id``: The ID of the project who owns the network.
            * ``status``: The port status. Value is ``ACTIVE`` or ``DOWN``.
            * ``subnet_id``: The ID of the subnet.

        :returns: A generator of port objects
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._list(_port.Port, **query)

    def update_port(
        self,
        port: ty.Union[str, _port.Port],
        if_revision: ty.Optional[int] = None,
        **attrs: ty.Any,
    ) -> _port.Port:
        """Update a port

        :param port: Either the id of a port or a
            :class:`~openstack.network.v2.port.Port` instance.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.
        :param attrs: The attributes to update on the port represented
            by ``port``.

        :returns: The updated port
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._update(_port.Port, port, if_revision=if_revision, **attrs)

    def add_ip_to_port(self, port, ip):
        ip.port_id = port.id
        return ip.commit(self)

    def remove_ip_from_port(self, ip):
        ip.port_id = None
        return ip.commit(self)

    def get_subnet_ports(self, subnet_id):
        result = []
        ports = self.ports()
        for puerta in ports:
            for fixed_ip in puerta.fixed_ips:
                if fixed_ip['subnet_id'] == subnet_id:
                    result.append(puerta)
        return result

    def create_port_binding(self, port, **attrs):
        """Create a port binding

        :param port: The value can be the ID of a port or a
            :class:`~openstack.network.v2.port.Port` instance.
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.port.Port`,
            comprised of the properties on the Port class.

        :returns: The results of port binding creation
        :rtype: :class:`~openstack.network.v2.port_binding.PortBinding`
        """
        port_id = self._get(_port.Port, port).id
        return self._create(
            _port_binding.PortBinding,
            port_id=port_id,
            **attrs,
        )

    def activate_port_binding(
        self,
        port,
        **attrs,
    ):
        """Activate a port binding

        :param port: The value can be the ID of a port or a
            :class:`~openstack.network.v2.port.Port` instance.
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.port.Port`,
            comprised of the properties on the Port class.

        :returns: The results of port binding creation
        :rtype: :class:`~openstack.network.v2.port_binding.PortBinding`
        """
        port_id = self._get(_port.Port, port).id
        host = attrs['host']
        bindings_on_host = self.port_bindings(port=port_id, host=host)
        # There can be only 1 binding on a host at a time
        for binding in bindings_on_host:
            return binding.activate_port_binding(self, **attrs)

    def port_bindings(self, port, **query):
        """Get a single port binding

        :param port: The value can be the ID of a port or a
            :class:`~openstack.network.v2.port.Port` instance.
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``host``: The host on which the port is bound.
            * ``vif_type``: The mechanism used for the port like bridge or ovs.
            * ``vnic_type``: The type of the vnic, like normal or baremetal.
            * ``status``: The port status. Value is ``ACTIVE`` or ``DOWN``.

        :returns: A generator of PortBinding objects
        :rtype: :class:`~openstack.network.v2.port_binding.PortBinding`
        """
        port_id = self._get(_port.Port, port).id
        return self._list(
            _port_binding.PortBinding,
            port_id=port_id,
            **query,
        )

    def delete_port_binding(self, port, host):
        """Delete a Port Binding

        :param port: The value can be either the ID of a port or a
            :class:`~openstack.network.v2.port.Port` instance.
        :param host: The host on which the port is bound.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the port does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent port.

        :returns: ``None``
        """
        port_id = self._get(_port.Port, port).id
        bindings_on_host = self.port_bindings(port=port_id, host=host)
        # There can be only 1 binding on a host at a time
        for binding in bindings_on_host:
            return binding.delete_port_binding(self, host=host)

    def create_qos_bandwidth_limit_rule(self, qos_policy, **attrs):
        """Create a new bandwidth limit rule

        :param attrs: Keyword arguments which will be used to create
            a
            :class:`~openstack.network.v2.qos_bandwidth_limit_rule.QoSBandwidthLimitRule`,
            comprised of the properties on the
            QoSBandwidthLimitRule class.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.

        :returns: The results of resource creation
        :rtype:
            :class:`~openstack.network.v2.qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._create(
            _qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def delete_qos_bandwidth_limit_rule(
        self, qos_rule, qos_policy, ignore_missing=True
    ):
        """Delete a bandwidth limit rule

        :param qos_rule: The value can be either the ID of a bandwidth limit
            rule or a
            :class:`~openstack.network.v2.qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent bandwidth limit rule.

        :returns: ``None``
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        self._delete(
            _qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            qos_rule,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
        )

    def find_qos_bandwidth_limit_rule(
        self, qos_rule_id, qos_policy, ignore_missing=True, **query
    ):
        """Find a bandwidth limit rule

        :param qos_rule_id: The ID of a bandwidth limit rule.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
            or None
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._find(
            _qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            qos_rule_id,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
            **query,
        )

    def get_qos_bandwidth_limit_rule(self, qos_rule, qos_policy):
        """Get a single bandwidth limit rule

        :param qos_rule: The value can be the ID of a minimum bandwidth rule or
            a
            :class:`~openstack.network.v2.qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :returns: One
            :class:`~openstack.network.v2.qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._get(
            _qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            qos_rule,
            qos_policy_id=policy.id,
        )

    def qos_bandwidth_limit_rules(self, qos_policy, **query):
        """Return a generator of bandwidth limit rules

        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of bandwidth limit rule objects
        :rtype:
            :class:`~openstack.network.v2.qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._list(
            _qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            qos_policy_id=policy.id,
            **query,
        )

    def update_qos_bandwidth_limit_rule(
        self,
        qos_rule,
        qos_policy,
        **attrs,
    ):
        """Update a bandwidth limit rule

        :param qos_rule: Either the id of a bandwidth limit rule or a
            :class:`~openstack.network.v2.qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param attrs: The attributes to update on the bandwidth limit rule
            represented by ``qos_rule``.

        :returns: The updated minimum bandwidth rule
        :rtype:
            :class:`~openstack.network.v2.qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._update(
            _qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            qos_rule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def create_qos_dscp_marking_rule(self, qos_policy, **attrs):
        """Create a new QoS DSCP marking rule

        :param attrs: Keyword arguments which will be used to create
            a
            :class:`~openstack.network.v2.qos_dscp_marking_rule.QoSDSCPMarkingRule`,
            comprised of the properties on the
            QosDscpMarkingRule class.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.

        :returns: The results of router creation
        :rtype:
            :class:`~openstack.network.v2.qos_dscp_marking_rule.QoSDSCPMarkingRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._create(
            _qos_dscp_marking_rule.QoSDSCPMarkingRule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def delete_qos_dscp_marking_rule(
        self, qos_rule, qos_policy, ignore_missing=True
    ):
        """Delete a QoS DSCP marking rule

        :param qos_rule: The value can be either the ID of a minimum bandwidth
            rule or a
            :class:`~openstack.network.v2.qos_dscp_marking_rule.QoSDSCPMarkingRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent minimum bandwidth rule.

        :returns: ``None``
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        self._delete(
            _qos_dscp_marking_rule.QoSDSCPMarkingRule,
            qos_rule,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
        )

    def find_qos_dscp_marking_rule(
        self, qos_rule_id, qos_policy, ignore_missing=True, **query
    ):
        """Find a QoS DSCP marking rule

        :param qos_rule_id: The ID of a QoS DSCP marking rule.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.qos_dscp_marking_rule.QoSDSCPMarkingRule`
            or None
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._find(
            _qos_dscp_marking_rule.QoSDSCPMarkingRule,
            qos_rule_id,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
            **query,
        )

    def get_qos_dscp_marking_rule(self, qos_rule, qos_policy):
        """Get a single QoS DSCP marking rule

        :param qos_rule: The value can be the ID of a minimum bandwidth rule or
            a
            :class:`~openstack.network.v2.qos_dscp_marking_rule.QoSDSCPMarkingRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :returns: One
            :class:`~openstack.network.v2.qos_dscp_marking_rule.QoSDSCPMarkingRule`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._get(
            _qos_dscp_marking_rule.QoSDSCPMarkingRule,
            qos_rule,
            qos_policy_id=policy.id,
        )

    def qos_dscp_marking_rules(self, qos_policy, **query):
        """Return a generator of QoS DSCP marking rules

        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of QoS DSCP marking rule objects
        :rtype:
            :class:`~openstack.network.v2.qos_dscp_marking_rule.QoSDSCPMarkingRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._list(
            _qos_dscp_marking_rule.QoSDSCPMarkingRule,
            qos_policy_id=policy.id,
            **query,
        )

    def update_qos_dscp_marking_rule(self, qos_rule, qos_policy, **attrs):
        """Update a QoS DSCP marking rule

        :param qos_rule: Either the id of a minimum bandwidth rule or a
            :class:`~openstack.network.v2.qos_dscp_marking_rule.QoSDSCPMarkingRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param attrs: The attributes to update on the QoS DSCP marking rule
            represented by ``qos_rule``.

        :returns: The updated QoS DSCP marking rule
        :rtype:
            :class:`~openstack.network.v2.qos_dscp_marking_rule.QoSDSCPMarkingRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._update(
            _qos_dscp_marking_rule.QoSDSCPMarkingRule,
            qos_rule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def create_qos_minimum_bandwidth_rule(self, qos_policy, **attrs):
        """Create a new minimum bandwidth rule

        :param attrs: Keyword arguments which will be used to create
            a
            :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`,
            comprised of the properties on the
            QoSMinimumBandwidthRule class.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.

        :returns: The results of resource creation
        :rtype:
            :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._create(
            _qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def delete_qos_minimum_bandwidth_rule(
        self, qos_rule, qos_policy, ignore_missing=True
    ):
        """Delete a minimum bandwidth rule

        :param qos_rule: The value can be either the ID of a minimum bandwidth
            rule or a
            :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent minimum bandwidth rule.

        :returns: ``None``
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        self._delete(
            _qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            qos_rule,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
        )

    def find_qos_minimum_bandwidth_rule(
        self, qos_rule_id, qos_policy, ignore_missing=True, **query
    ):
        """Find a minimum bandwidth rule

        :param qos_rule_id: The ID of a minimum bandwidth rule.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
            or None
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._find(
            _qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            qos_rule_id,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
            **query,
        )

    def get_qos_minimum_bandwidth_rule(self, qos_rule, qos_policy):
        """Get a single minimum bandwidth rule

        :param qos_rule: The value can be the ID of a minimum bandwidth rule or
            a
            :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy`
            instance.
        :returns: One
            :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
        :raises:
            :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._get(
            _qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            qos_rule,
            qos_policy_id=policy.id,
        )

    def qos_minimum_bandwidth_rules(self, qos_policy, **query):
        """Return a generator of minimum bandwidth rules

        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of minimum bandwidth rule objects
        :rtype:
            :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._list(
            _qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            qos_policy_id=policy.id,
            **query,
        )

    def update_qos_minimum_bandwidth_rule(self, qos_rule, qos_policy, **attrs):
        """Update a minimum bandwidth rule

        :param qos_rule: Either the id of a minimum bandwidth rule or a
            :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy`
            instance.
        :param attrs: The attributes to update on the minimum bandwidth rule
            represented by ``qos_rule``.

        :returns: The updated minimum bandwidth rule
        :rtype:
            :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._update(
            _qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            qos_rule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def create_qos_minimum_packet_rate_rule(self, qos_policy, **attrs):
        """Create a new minimum packet rate rule

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule`,
            comprised of the properties on the QoSMinimumPacketRateRule class.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.

        :returns: The results of resource creation
        :rtype:
            :class:`~openstack.network.v2.qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._create(
            _qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def delete_qos_minimum_packet_rate_rule(
        self, qos_rule, qos_policy, ignore_missing=True
    ):
        """Delete a minimum packet rate rule

        :param qos_rule: The value can be either the ID of a minimum packet
            rate rule or a
            :class:`~openstack.network.v2.qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            minimum packet rate rule.

        :returns: ``None``
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        self._delete(
            _qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            qos_rule,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
        )

    def find_qos_minimum_packet_rate_rule(
        self, qos_rule_id, qos_policy, ignore_missing=True, **query
    ):
        """Find a minimum packet rate rule

        :param qos_rule_id: The ID of a minimum packet rate rule.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the resource does not exist. When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule`
            or None
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._find(
            _qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            qos_rule_id,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
            **query,
        )

    def get_qos_minimum_packet_rate_rule(self, qos_rule, qos_policy):
        """Get a single minimum packet rate rule

        :param qos_rule: The value can be the ID of a minimum packet rate rule
            or a
            :class:`~openstack.network.v2.qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :returns: One
            :class:`~openstack.network.v2.qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._get(
            _qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            qos_rule,
            qos_policy_id=policy.id,
        )

    def qos_minimum_packet_rate_rules(self, qos_policy, **query):
        """Return a generator of minimum packet rate rules

        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param kwargs query: Optional query parameters to be sent to limit the
            resources being returned.
        :returns: A generator of minimum packet rate rule objects
        :rtype:
            :class:`~openstack.network.v2.qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._list(
            _qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            qos_policy_id=policy.id,
            **query,
        )

    def update_qos_minimum_packet_rate_rule(
        self, qos_rule, qos_policy, **attrs
    ):
        """Update a minimum packet rate rule

        :param qos_rule: Either the id of a minimum packet rate rule or a
            :class:`~openstack.network.v2.qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param attrs: The attributes to update on the minimum packet rate rule
            represented by ``qos_rule``.

        :returns: The updated minimum packet rate rule
        :rtype:
            :class:`~openstack.network.v2.qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._update(
            _qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            qos_rule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def create_qos_packet_rate_limit_rule(self, qos_policy, **attrs):
        """Create a new packet rate limit rule

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.qos_packet_rate_limit_rule.QoSPacketRateLimitRule`,
            comprised of the properties on the QoSPacketRateLimitRule class.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.

        :returns: The results of resource creation
        :rtype:
            :class:`~openstack.network.v2.qos_packet_rate_limit_rule.QoSPacketRateLimitRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._create(
            _qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def delete_qos_packet_rate_limit_rule(
        self, qos_rule, qos_policy, ignore_missing=True
    ):
        """Delete a packet rate limit rule

        :param qos_rule: The value can be either the ID of a packet rate limit
            rule or a
            :class:`~openstack.network.v2.qos_packet_rate_limit_rule.QoSPacketRateLimitRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the resource does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent minimum packet
            rate rule.

        :returns: ``None``
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        self._delete(
            _qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            qos_rule,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
        )

    def find_qos_packet_rate_limit_rule(
        self, qos_rule_id, qos_policy, ignore_missing=True, **query
    ):
        """Find a packet rate limit rule

        :param qos_rule_id: The ID of a packet rate limit rule.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the resource does not exist. When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.qos_packet_rate_limit_rule.QoSPacketRateLimitRule`
            or None
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._find(
            _qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            qos_rule_id,
            ignore_missing=ignore_missing,
            qos_policy_id=policy.id,
            **query,
        )

    def get_qos_packet_rate_limit_rule(self, qos_rule, qos_policy):
        """Get a single packet rate limit rule

        :param qos_rule: The value can be the ID of a packet rate limit rule
            or a
            :class:`~openstack.network.v2.qos_packet_rate_limit_rule.QoSPacketRateLimitRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :returns: One
            :class:`~openstack.network.v2.qos_packet_rate_limit_rule.QoSPacketRateLimitRule`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._get(
            _qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            qos_rule,
            qos_policy_id=policy.id,
        )

    def qos_packet_rate_limit_rules(self, qos_policy, **query):
        """Return a generator of packet rate limit rules

        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param kwargs query: Optional query parameters to be sent to limit the
            resources being returned.
        :returns: A generator of minimum packet rate rule objects
        :rtype:
            :class:`~openstack.network.v2.qos_packet_rate_limit_rule.QoSPacketRateLimitRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._list(
            _qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            qos_policy_id=policy.id,
            **query,
        )

    def update_qos_packet_rate_limit_rule(self, qos_rule, qos_policy, **attrs):
        """Update a minimum packet rate rule

        :param qos_rule: Either the id of a minimum packet rate rule or a
            :class:`~openstack.network.v2.qos_packet_rate_limit_rule.QoSPacketRateLimitRule`
            instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
            rule belongs or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param attrs: The attributes to update on the minimum packet rate rule
            represented by ``qos_rule``.

        :returns: The updated minimum packet rate rule
        :rtype:
            :class:`~openstack.network.v2.qos_packet_rate_limit_rule.QoSPacketRateLimitRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._update(
            _qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            qos_rule,
            qos_policy_id=policy.id,
            **attrs,
        )

    def create_qos_policy(self, **attrs):
        """Create a new QoS policy from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.qos_policy.QoSPolicy`,
            comprised of the properties on the
            QoSPolicy class.

        :returns: The results of QoS policy creation
        :rtype: :class:`~openstack.network.v2.qos_policy.QoSPolicy`
        """
        return self._create(_qos_policy.QoSPolicy, **attrs)

    def delete_qos_policy(self, qos_policy, ignore_missing=True):
        """Delete a QoS policy

        :param qos_policy: The value can be either the ID of a QoS policy or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the QoS policy does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent QoS policy.

        :returns: ``None``
        """
        self._delete(
            _qos_policy.QoSPolicy, qos_policy, ignore_missing=ignore_missing
        )

    def find_qos_policy(self, name_or_id, ignore_missing=True, **query):
        """Find a single QoS policy

        :param name_or_id: The name or ID of a QoS policy.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.qos_policy.QoSPolicy` or
            None
        """
        return self._find(
            _qos_policy.QoSPolicy,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_qos_policy(self, qos_policy):
        """Get a single QoS policy

        :param qos_policy: The value can be the ID of a QoS policy or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy`
            instance.

        :returns: One :class:`~openstack.network.v2.qos_policy.QoSPolicy`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_qos_policy.QoSPolicy, qos_policy)

    def qos_policies(self, **query):
        """Return a generator of QoS policies

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``description``: The description of a QoS policy.
            * ``is_shared``: Whether the policy is shared among projects.
            * ``name``: The name of a QoS policy.
            * ``project_id``: The ID of the project who owns the network.

        :returns: A generator of QoS policy objects
        :rtype: :class:`~openstack.network.v2.qos_policy.QoSPolicy`
        """
        return self._list(_qos_policy.QoSPolicy, **query)

    def update_qos_policy(self, qos_policy, **attrs):
        """Update a QoS policy

        :param qos_policy: Either the id of a QoS policy or a
            :class:`~openstack.network.v2.qos_policy.QoSPolicy` instance.
        :param attrs: The attributes to update on the QoS policy represented
            by ``qos_policy``.

        :returns: The updated QoS policy
        :rtype: :class:`~openstack.network.v2.qos_policy.QoSPolicy`
        """
        return self._update(_qos_policy.QoSPolicy, qos_policy, **attrs)

    def find_qos_rule_type(self, rule_type_name, ignore_missing=True):
        """Find a single QoS rule type details

        :param rule_type_name: The name of a QoS rule type.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.qos_rule_type.QoSRuleType`
            or None
        """
        return self._find(
            _qos_rule_type.QoSRuleType,
            rule_type_name,
            ignore_missing=ignore_missing,
        )

    def get_qos_rule_type(self, qos_rule_type):
        """Get details about single QoS rule type

        :param qos_rule_type: The value can be the name of a QoS policy
            rule type or a
            :class:`~openstack.network.v2.qos_rule_type.QoSRuleType`
            instance.

        :returns: One :class:`~openstack.network.v2.qos_rule_type.QoSRuleType`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_qos_rule_type.QoSRuleType, qos_rule_type)

    def qos_rule_types(self, **query):
        """Return a generator of QoS rule types

        :param dict query: Optional query parameters to be sent to limit the
            resources returned. Valid parameters include:

            * ``type``: The type of the QoS rule type.

        :returns: A generator of QoS rule type objects
        :rtype: :class:`~openstack.network.v2.qos_rule_type.QoSRuleType`
        """
        return self._list(_qos_rule_type.QoSRuleType, **query)

    def delete_quota(self, quota, ignore_missing=True):
        """Delete a quota (i.e. reset to the default quota)

        :param quota: The value can be either the ID of a quota or a
            :class:`~openstack.network.v2.quota.Quota` instance.
            The ID of a quota is the same as the project ID
            for the quota.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when quota does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent quota.

        :returns: ``None``
        """
        self._delete(_quota.Quota, quota, ignore_missing=ignore_missing)

    def get_quota(self, quota, details=False):
        """Get a quota

        :param quota: The value can be the ID of a quota or a
            :class:`~openstack.network.v2.quota.Quota` instance.
            The ID of a quota is the same as the project ID
            for the quota.
        :param details: If set to True, details about quota usage will
            be returned.

        :returns: One :class:`~openstack.network.v2.quota.Quota`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        if details:
            quota_obj = self._get_resource(_quota.Quota, quota)
            quota = self._get(
                _quota.QuotaDetails, project=quota_obj.id, requires_id=False
            )
        else:
            quota = self._get(_quota.Quota, quota)
        return quota

    def get_quota_default(self, quota):
        """Get a default quota

        :param quota: The value can be the ID of a default quota or a
            :class:`~openstack.network.v2.quota.QuotaDefault`
            instance. The ID of a default quota is the same
            as the project ID for the default quota.

        :returns: One :class:`~openstack.network.v2.quota.QuotaDefault`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        quota_obj = self._get_resource(_quota.Quota, quota)
        return self._get(
            _quota.QuotaDefault, project=quota_obj.id, requires_id=False
        )

    def quotas(self, **query):
        """Return a generator of quotas

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Currently no query
            parameter is supported.

        :returns: A generator of quota objects
        :rtype: :class:`~openstack.network.v2.quota.Quota`
        """
        return self._list(_quota.Quota, **query)

    def update_quota(self, quota, **attrs):
        """Update a quota

        :param quota: Either the ID of a quota or a
            :class:`~openstack.network.v2.quota.Quota` instance.
            The ID of a quota is the same as the project ID
            for the quota.
        :param attrs: The attributes to update on the quota represented
            by ``quota``.

        :returns: The updated quota
        :rtype: :class:`~openstack.network.v2.quota.Quota`
        """
        return self._update(_quota.Quota, quota, **attrs)

    def create_rbac_policy(self, **attrs):
        """Create a new RBAC policy from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.rbac_policy.RBACPolicy`,
            comprised of the properties on the RBACPolicy class.

        :return: The results of RBAC policy creation
        :rtype: :class:`~openstack.network.v2.rbac_policy.RBACPolicy`
        """
        return self._create(_rbac_policy.RBACPolicy, **attrs)

    def delete_rbac_policy(self, rbac_policy, ignore_missing=True):
        """Delete a RBAC policy

        :param rbac_policy: The value can be either the ID of a RBAC policy or
            a :class:`~openstack.network.v2.rbac_policy.RBACPolicy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the RBAC policy does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent RBAC policy.

        :returns: ``None``
        """
        self._delete(
            _rbac_policy.RBACPolicy, rbac_policy, ignore_missing=ignore_missing
        )

    def find_rbac_policy(self, rbac_policy, ignore_missing=True, **query):
        """Find a single RBAC policy

        :param rbac_policy: The ID of a RBAC policy.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.rbac_policy.RBACPolicy` or None
        """
        return self._find(
            _rbac_policy.RBACPolicy,
            rbac_policy,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_rbac_policy(self, rbac_policy):
        """Get a single RBAC policy

        :param rbac_policy: The value can be the ID of a RBAC policy or a
            :class:`~openstack.network.v2.rbac_policy.RBACPolicy` instance.

        :returns: One :class:`~openstack.network.v2.rbac_policy.RBACPolicy`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_rbac_policy.RBACPolicy, rbac_policy)

    def rbac_policies(self, **query):
        """Return a generator of RBAC policies

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters
            include:

            * ``action``: RBAC policy action
            * ``object_type``: Type of the object that the RBAC policy affects
            * ``target_project_id``: ID of the tenant that the RBAC policy
              affects
            * ``project_id``: Owner tenant ID

        :returns: A generator of rbac objects
        :rtype: :class:`~openstack.network.v2.rbac_policy.RBACPolicy`
        """
        return self._list(_rbac_policy.RBACPolicy, **query)

    def update_rbac_policy(self, rbac_policy, **attrs):
        """Update a RBAC policy

        :param rbac_policy: Either the id of a RBAC policy or a
            :class:`~openstack.network.v2.rbac_policy.RBACPolicy` instance.
        :param attrs: The attributes to update on the RBAC policy
            represented by ``rbac_policy``.

        :returns: The updated RBAC policy
        :rtype: :class:`~openstack.network.v2.rbac_policy.RBACPolicy`
        """
        return self._update(_rbac_policy.RBACPolicy, rbac_policy, **attrs)

    def create_router(self, **attrs):
        """Create a new router from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.router.Router`,
            comprised of the properties on the Router class.

        :returns: The results of router creation
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._create(_router.Router, **attrs)

    def delete_router(self, router, ignore_missing=True, if_revision=None):
        """Delete a router

        :param router: The value can be either the ID of a router or a
            :class:`~openstack.network.v2.router.Router` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the router does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent router.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.

        :returns: ``None``
        """
        self._delete(
            _router.Router,
            router,
            ignore_missing=ignore_missing,
            if_revision=if_revision,
        )

    def find_router(self, name_or_id, ignore_missing=True, **query):
        """Find a single router

        :param name_or_id: The name or ID of a router.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.router.Router` or None
        """
        return self._find(
            _router.Router, name_or_id, ignore_missing=ignore_missing, **query
        )

    def get_router(self, router):
        """Get a single router

        :param router: The value can be the ID of a router or a
            :class:`~openstack.network.v2.router.Router` instance.

        :returns: One :class:`~openstack.network.v2.router.Router`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_router.Router, router)

    def routers(self, **query):
        """Return a generator of routers

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``description``: The description of a router.
            * ``flavor_id``: The ID of the flavor.
            * ``is_admin_state_up``: Router administrative state is up or not
            * ``is_distributed``: The distributed state of a router
            * ``is_ha``: The highly-available state of a router
            * ``name``: Router name
            * ``project_id``: The ID of the project this router is associated
              with.
            * ``status``: The status of the router.

        :returns: A generator of router objects
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._list(_router.Router, **query)

    def update_router(self, router, if_revision=None, **attrs):
        """Update a router

        :param router: Either the id of a router or a
            :class:`~openstack.network.v2.router.Router` instance.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.
        :param attrs: The attributes to update on the router represented
            by ``router``.

        :returns: The updated router
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._update(
            _router.Router, router, if_revision=if_revision, **attrs
        )

    def add_interface_to_router(self, router, subnet_id=None, port_id=None):
        """Add Interface to a router

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param subnet_id: ID of the subnet
        :param port_id: ID of the port
        :returns: Router with updated interface
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        body = {}
        if port_id:
            body = {'port_id': port_id}
        else:
            body = {'subnet_id': subnet_id}
        router = self._get_resource(_router.Router, router)
        return router.add_interface(self, **body)

    def remove_interface_from_router(
        self, router, subnet_id=None, port_id=None
    ):
        """Remove Interface from a router

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param subnet: ID of the subnet
        :param port: ID of the port
        :returns: Router with updated interface
        :rtype: :class:`~openstack.network.v2.router.Router`
        """

        body = {}
        if port_id:
            body = {'port_id': port_id}
        else:
            body = {'subnet_id': subnet_id}
        router = self._get_resource(_router.Router, router)
        return router.remove_interface(self, **body)

    def add_extra_routes_to_router(self, router, body):
        """Add extra routes to a router

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param body: The request body as documented in the api-ref.
        :returns: Router with updated extra routes
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        router = self._get_resource(_router.Router, router)
        return router.add_extra_routes(self, body=body)

    def remove_extra_routes_from_router(self, router, body):
        """Remove extra routes from a router

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param body: The request body as documented in the api-ref.
        :returns: Router with updated extra routes
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        router = self._get_resource(_router.Router, router)
        return router.remove_extra_routes(self, body=body)

    def add_gateway_to_router(self, router, **body):
        """Add Gateway to a router

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param body: Body with the gateway information
        :returns: Router with updated interface
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        router = self._get_resource(_router.Router, router)
        return router.add_gateway(self, **body)

    def remove_gateway_from_router(self, router, **body):
        """Remove Gateway from a router

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param body: Body with the gateway information
        :returns: Router with updated interface
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        router = self._get_resource(_router.Router, router)
        return router.remove_gateway(self, **body)

    def add_external_gateways(self, router, body):
        """Add router external gateways

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param body: Body containing the external_gateways parameter.
        :returns: Router with added gateways
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        router = self._get_resource(_router.Router, router)
        return router.add_external_gateways(self, body)

    def update_external_gateways(self, router, body):
        """Update router external gateways

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param body: Body containing the external_gateways parameter.
        :returns: Router with updated gateways
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        router = self._get_resource(_router.Router, router)
        return router.update_external_gateways(self, body)

    def remove_external_gateways(self, router, body):
        """Remove router external gateways

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param body: Body containing the external_gateways parameter.
        :returns: Router without the removed gateways
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        router = self._get_resource(_router.Router, router)
        return router.remove_external_gateways(self, body)

    def routers_hosting_l3_agents(self, router, **query):
        """Return a generator of L3 agent hosting a router

        :param router: Either the router id or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param kwargs query: Optional query parameters to be sent to limit
            the resources returned

        :returns: A generator of Router L3 Agents
        :rtype: :class:`~openstack.network.v2.router.RouterL3Agents`
        """
        router = self._get_resource(_router.Router, router)
        return self._list(_agent.RouterL3Agent, router_id=router.id, **query)

    def agent_hosted_routers(self, agent, **query):
        """Return a generator of routers hosted by a L3 agent

        :param agent: Either the agent id of an instance of
            :class:`~openstack.network.v2.network_agent.Agent`
        :param kwargs query: Optional query parameters to be sent to limit
            the resources returned

        :returns: A generator of routers
        :rtype: :class:`~openstack.network.v2.agent.L3AgentRouters`
        """
        agent = self._get_resource(_agent.Agent, agent)
        return self._list(_router.L3AgentRouter, agent_id=agent.id, **query)

    def add_router_to_agent(self, agent, router):
        """Add router to L3 agent

        :param agent: Either the id of an agent
            :class:`~openstack.network.v2.agent.Agent` instance
        :param router: A router instance
        :returns: Agent with attached router
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        """
        agent = self._get_resource(_agent.Agent, agent)
        router = self._get_resource(_router.Router, router)
        return agent.add_router_to_agent(self, router.id)

    def remove_router_from_agent(self, agent, router):
        """Remove router from L3 agent

        :param agent: Either the id of an agent or an
            :class:`~openstack.network.v2.agent.Agent` instance
        :param router: A router instance
        :returns: Agent with removed router
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        """
        agent = self._get_resource(_agent.Agent, agent)
        router = self._get_resource(_router.Router, router)
        return agent.remove_router_from_agent(self, router.id)

    def create_ndp_proxy(self, **attrs):
        """Create a new ndp proxy from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.ndp_proxy.NDPProxxy`,
            comprised of the properties on the NDPProxy class.

        :returns: The results of ndp proxy creation
        :rtype: :class:`~openstack.network.v2.ndp_proxy.NDPProxxy`
        """
        return self._create(_ndp_proxy.NDPProxy, **attrs)

    def get_ndp_proxy(self, ndp_proxy):
        """Get a single ndp proxy

        :param ndp_proxy: The value can be the ID of a ndp proxy
            or a :class:`~openstack.network.v2.ndp_proxy.NDPProxy`
            instance.

        :returns: One
            :class:`~openstack.network.v2.ndp_proxy.NDPProxy`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_ndp_proxy.NDPProxy, ndp_proxy)

    def find_ndp_proxy(self, ndp_proxy_id, ignore_missing=True, **query):
        """Find a single ndp proxy

        :param ndp_proxy_id: The ID of a ndp proxy.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the resource does not exist.  When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns:
            One :class:`~openstack.network.v2.ndp_proxy.NDPProxy` or None
        """
        return self._find(
            _ndp_proxy.NDPProxy,
            ndp_proxy_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def delete_ndp_proxy(self, ndp_proxy, ignore_missing=True):
        """Delete a ndp proxy

        :param ndp_proxy: The value can be the ID of a ndp proxy
            or a :class:`~openstack.network.v2.ndp_proxy.NDPProxy`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the router does not exist.  When set to ``True``, no exception will
            be set when attempting to delete a nonexistent ndp proxy.

        :returns: ``None``
        """
        self._delete(
            _ndp_proxy.NDPProxy, ndp_proxy, ignore_missing=ignore_missing
        )

    def ndp_proxies(self, **query):
        """Return a generator of ndp proxies

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``router_id``: The ID fo the router
            * ``port_id``: The ID of internal port.
            * ``ip_address``: The internal IP address

        :returns: A generator of port forwarding objects
        :rtype: :class:`~openstack.network.v2.port_forwarding.PortForwarding`
        """
        return self._list(_ndp_proxy.NDPProxy, paginated=False, **query)

    def update_ndp_proxy(self, ndp_proxy, **attrs):
        """Update a ndp proxy

        :param ndp_proxy: The value can be the ID of a ndp proxy or a
            :class:`~openstack.network.v2.ndp_proxy.NDPProxy` instance.
        :param attrs: The attributes to update on the ip represented
            by ``value``.

        :returns: The updated ndp_proxy
        :rtype: :class:`~openstack.network.v2.ndp_proxy.NDPProxy`
        """
        return self._update(_ndp_proxy.NDPProxy, ndp_proxy, **attrs)

    def create_firewall_group(self, **attrs):
        """Create a new firewall group from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.firewall_group.FirewallGroup`,
            comprised of the properties on the FirewallGroup class.

        :returns: The results of firewall group creation
        :rtype: :class:`~openstack.network.v2.firewall_group.FirewallGroup`
        """
        return self._create(_firewall_group.FirewallGroup, **attrs)

    def delete_firewall_group(self, firewall_group, ignore_missing=True):
        """Delete a firewall group

        :param firewall_group:
            The value can be either the ID of a firewall group or a
            :class:`~openstack.network.v2.firewall_group.FirewallGroup`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the firewall group does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent firewall group.

        :returns: ``None``
        """
        self._delete(
            _firewall_group.FirewallGroup,
            firewall_group,
            ignore_missing=ignore_missing,
        )

    def find_firewall_group(self, name_or_id, ignore_missing=True, **query):
        """Find a single firewall group

        :param name_or_id: The name or ID of a firewall group.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.firewall_group.FirewallGroup` or None
        """
        return self._find(
            _firewall_group.FirewallGroup,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_firewall_group(self, firewall_group):
        """Get a single firewall group

        :param firewall_group: The value can be the ID of a firewall group or a
            :class:`~openstack.network.v2.firewall_group.FirewallGroup`
            instance.

        :returns: One
            :class:`~openstack.network.v2.firewall_group.FirewallGroup`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_firewall_group.FirewallGroup, firewall_group)

    def firewall_groups(self, **query):
        """Return a generator of firewall_groups

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``description``: Firewall group description
            * ``egress_policy_id``: The ID of egress firewall policy
            * ``ingress_policy_id``: The ID of ingress firewall policy
            * ``name``: The name of a firewall group
            * ``shared``: Indicates whether this firewall group is shared
              across all projects.
            * ``status``: The status of the firewall group. Valid values are
              ACTIVE, INACTIVE, ERROR, PENDING_UPDATE, or
              PENDING_DELETE.
            * ``ports``: A list of the IDs of the ports associated with the
              firewall group.
            * ``project_id``: The ID of the project this firewall group is
              associated with.

        :returns: A generator of firewall group objects
        """
        return self._list(_firewall_group.FirewallGroup, **query)

    def update_firewall_group(self, firewall_group, **attrs):
        """Update a firewall group

        :param firewall_group: Either the id of a firewall group or a
            :class:`~openstack.network.v2.firewall_group.FirewallGroup`
            instance.
        :param attrs: The attributes to update on the firewall group
            represented by ``firewall_group``.

        :returns: The updated firewall group
        :rtype: :class:`~openstack.network.v2.firewall_group.FirewallGroup`
        """
        return self._update(
            _firewall_group.FirewallGroup, firewall_group, **attrs
        )

    def create_firewall_policy(self, **attrs):
        """Create a new firewall policy from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`,
            comprised of the properties on the FirewallPolicy class.

        :returns: The results of firewall policy creation
        :rtype: :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`
        """
        return self._create(_firewall_policy.FirewallPolicy, **attrs)

    def delete_firewall_policy(self, firewall_policy, ignore_missing=True):
        """Delete a firewall policy

        :param firewall_policy:
            The value can be either the ID of a firewall policy or a
            :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the firewall policy does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent firewall policy.

        :returns: ``None``
        """
        self._delete(
            _firewall_policy.FirewallPolicy,
            firewall_policy,
            ignore_missing=ignore_missing,
        )

    def find_firewall_policy(self, name_or_id, ignore_missing=True, **query):
        """Find a single firewall policy

        :param name_or_id: The name or ID of a firewall policy.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`
            or None
        """
        return self._find(
            _firewall_policy.FirewallPolicy,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_firewall_policy(self, firewall_policy):
        """Get a single firewall policy

        :param firewall_policy: The value can be the ID of a firewall policy
            or a
            :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`
            instance.

        :returns: One
            :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_firewall_policy.FirewallPolicy, firewall_policy)

    def firewall_policies(self, **query):
        """Return a generator of firewall_policies

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``description``: Firewall policy description
            * ``firewall_rule``: A list of the IDs of the firewall rules
              associated with the firewall policy.
            * ``name``: The name of a firewall policy
            * ``shared``: Indicates whether this firewall policy is shared
              across all projects.
            * ``project_id``: The ID of the project that owns the resource.

        :returns: A generator of firewall policy objects
        """
        return self._list(_firewall_policy.FirewallPolicy, **query)

    def update_firewall_policy(self, firewall_policy, **attrs):
        """Update a firewall policy

        :param firewall_policy: Either the id of a firewall policy or a
            :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`
            instance.
        :param attrs: The attributes to update on the firewall policy
            represented by ``firewall_policy``.

        :returns: The updated firewall policy
        :rtype: :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`
        """
        return self._update(
            _firewall_policy.FirewallPolicy, firewall_policy, **attrs
        )

    def insert_rule_into_policy(
        self,
        firewall_policy_id,
        firewall_rule_id,
        insert_after=None,
        insert_before=None,
    ):
        """Insert a firewall_rule into a firewall_policy in order

        :param firewall_policy_id: The ID of the firewall policy.
        :param firewall_rule_id: The ID of the firewall rule.
        :param insert_after: The ID of the firewall rule to insert the new
            rule after. It will be worked only when
            insert_before is none.
        :param insert_before: The ID of the firewall rule to insert the new
            rule before.

        :returns: The updated firewall policy
        :rtype: :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`
        """
        body = {
            'firewall_rule_id': firewall_rule_id,
            'insert_after': insert_after,
            'insert_before': insert_before,
        }
        policy = self._get_resource(
            _firewall_policy.FirewallPolicy, firewall_policy_id
        )
        return policy.insert_rule(self, **body)

    def remove_rule_from_policy(self, firewall_policy_id, firewall_rule_id):
        """Remove a firewall_rule from a firewall_policy.

        :param firewall_policy_id: The ID of the firewall policy.
        :param firewall_rule_id: The ID of the firewall rule.

        :returns: The updated firewall policy
        :rtype: :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`
        """
        body = {'firewall_rule_id': firewall_rule_id}
        policy = self._get_resource(
            _firewall_policy.FirewallPolicy, firewall_policy_id
        )
        return policy.remove_rule(self, **body)

    def create_firewall_rule(self, **attrs):
        """Create a new firewall rule from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.firewall_rule.FirewallRule`,
            comprised of the properties on the FirewallRule class.

        :returns: The results of firewall rule creation
        :rtype: :class:`~openstack.network.v2.firewall_rule.FirewallRule`
        """
        return self._create(_firewall_rule.FirewallRule, **attrs)

    def delete_firewall_rule(self, firewall_rule, ignore_missing=True):
        """Delete a firewall rule

        :param firewall_rule:
            The value can be either the ID of a firewall rule or a
            :class:`~openstack.network.v2.firewall_rule.FirewallRule`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the firewall rule does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent firewall rule.

        :returns: ``None``
        """
        self._delete(
            _firewall_rule.FirewallRule,
            firewall_rule,
            ignore_missing=ignore_missing,
        )

    def find_firewall_rule(self, name_or_id, ignore_missing=True, **query):
        """Find a single firewall rule

        :param name_or_id: The name or ID of a firewall rule.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.firewall_rule.FirewallRule`
            or None
        """
        return self._find(
            _firewall_rule.FirewallRule,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_firewall_rule(self, firewall_rule):
        """Get a single firewall rule

        :param firewall_rule: The value can be the ID of a firewall rule or a
            :class:`~openstack.network.v2.firewall_rule.FirewallRule`
            instance.

        :returns: One
            :class:`~openstack.network.v2.firewall_rule.FirewallRule`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_firewall_rule.FirewallRule, firewall_rule)

    def firewall_rules(self, **query):
        """Return a generator of firewall_rules

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``action``: The action that the API performs on traffic that
              matches the firewall rule.
            * ``description``: Firewall rule description
            * ``name``: The name of a firewall group
            * ``destination_ip_address``: The destination IPv4 or IPv6 address
              or CIDR for the firewall rule.
            * ``destination_port``: The destination port or port range for
              the firewall rule.
            * ``enabled``: Facilitates selectively turning off rules.
            * ``shared``: Indicates whether this firewall group is shared
              across all projects.
            * ``ip_version``: The IP protocol version for the firewall rule.
            * ``protocol``: The IP protocol for the firewall rule.
            * ``source_ip_address``: The source IPv4 or IPv6 address or CIDR
              for the firewall rule.
            * ``source_port``: The source port or port range for the firewall
              rule.
            * ``project_id``: The ID of the project this firewall group is
              associated with.

        :returns: A generator of firewall rule objects
        """
        return self._list(_firewall_rule.FirewallRule, **query)

    def update_firewall_rule(self, firewall_rule, **attrs):
        """Update a firewall rule

        :param firewall_rule: Either the id of a firewall rule or a
            :class:`~openstack.network.v2.firewall_rule.FirewallRule`
            instance.
        :param attrs: The attributes to update on the firewall rule
            represented by ``firewall_rule``.

        :returns: The updated firewall rule
        :rtype: :class:`~openstack.network.v2.firewall_rule.FirewallRule`
        """
        return self._update(
            _firewall_rule.FirewallRule, firewall_rule, **attrs
        )

    def create_security_group(self, **attrs):
        """Create a new security group from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.security_group.SecurityGroup`,
            comprised of the properties on the SecurityGroup class.

        :returns: The results of security group creation
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._create(_security_group.SecurityGroup, **attrs)

    def delete_security_group(
        self, security_group, ignore_missing=True, if_revision=None
    ):
        """Delete a security group

        :param security_group:
            The value can be either the ID of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the security group does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent security group.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.

        :returns: ``None``
        """
        self._delete(
            _security_group.SecurityGroup,
            security_group,
            ignore_missing=ignore_missing,
            if_revision=if_revision,
        )

    def find_security_group(self, name_or_id, ignore_missing=True, **query):
        """Find a single security group

        :param name_or_id: The name or ID of a security group.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            or None
        """
        return self._find(
            _security_group.SecurityGroup,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_security_group(self, security_group):
        """Get a single security group

        :param security_group: The value can be the ID of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.

        :returns: One
            :class:`~openstack.network.v2.security_group.SecurityGroup`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_security_group.SecurityGroup, security_group)

    def security_groups(self, **query):
        """Return a generator of security groups

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:

            * ``description``: Security group description
            * ``ìd``: The id of a security group, or list of security group ids
            * ``name``: The name of a security group
            * ``project_id``: The ID of the project this security group is
              associated with.

        :returns: A generator of security group objects
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._list(_security_group.SecurityGroup, **query)

    def update_security_group(self, security_group, if_revision=None, **attrs):
        """Update a security group

        :param security_group: Either the id of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.
        :param attrs: The attributes to update on the security group
            represented by ``security_group``.

        :returns: The updated security group
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._update(
            _security_group.SecurityGroup,
            security_group,
            if_revision=if_revision,
            **attrs,
        )

    def create_security_group_rule(self, **attrs):
        """Create a new security group rule from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`,
            comprised of the properties on the
            SecurityGroupRule class.

        :returns: The results of security group rule creation
        :rtype:
            :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
        """
        return self._create(_security_group_rule.SecurityGroupRule, **attrs)

    def create_security_group_rules(self, data):
        """Create new security group rules from the list of attributes

        :param list data: List of dicts of attributes which will be used to
            create a
            :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`,
            comprised of the properties on the SecurityGroupRule
            class.

        :returns: A generator of security group rule objects
        :rtype:
            :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
        """
        return self._bulk_create(_security_group_rule.SecurityGroupRule, data)

    def delete_security_group_rule(
        self, security_group_rule, ignore_missing=True, if_revision=None
    ):
        """Delete a security group rule

        :param security_group_rule:
            The value can be either the ID of a security group rule
            or a
            :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the security group rule does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent security group rule.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.

        :returns: ``None``
        """
        self._delete(
            _security_group_rule.SecurityGroupRule,
            security_group_rule,
            ignore_missing=ignore_missing,
            if_revision=if_revision,
        )

    def find_security_group_rule(
        self, name_or_id, ignore_missing=True, **query
    ):
        """Find a single security group rule

        :param str name_or_id: The ID of a security group rule.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
            or None
        """
        return self._find(
            _security_group_rule.SecurityGroupRule,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_security_group_rule(self, security_group_rule):
        """Get a single security group rule

        :param security_group_rule:
            The value can be the ID of a security group rule or a
            :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
            instance.

        :returns:
            :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _security_group_rule.SecurityGroupRule, security_group_rule
        )

    def security_group_rules(self, **query):
        """Return a generator of security group rules

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``description``: The security group rule description
            * ``direction``: Security group rule direction
            * ``ether_type``: Must be IPv4 or IPv6, and addresses represented
              in CIDR must match the ingress or egress rule.
            * ``project_id``: The ID of the project this security group rule
              is associated with.
            * ``protocol``: Security group rule protocol
            * ``remote_group_id``: ID of a remote security group
            * ``security_group_id``: ID of security group that owns the rules

        :returns: A generator of security group rule objects
        :rtype:
            :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
        """
        return self._list(_security_group_rule.SecurityGroupRule, **query)

    def create_default_security_group_rule(self, **attrs):
        """Create a new default security group rule from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.default_security_group_rule.
            DefaultSecurityGroupRule`,
            comprised of the properties on the DefaultSecurityGroupRule class.

        :returns: The results of default security group rule creation
        :rtype:
            :class:`~openstack.network.v2.default_security_group_rule.
            DefaultSecurityGroupRule`
        """
        return self._create(
            _default_security_group_rule.DefaultSecurityGroupRule, **attrs
        )

    def delete_default_security_group_rule(
        self,
        default_security_group_rule,
        ignore_missing=True,
    ):
        """Delete a default security group rule

        :param default_security_group_rule:
            The value can be either the ID of a default security group rule
            or a
            :class:`~openstack.network.v2.default_security_group_rule.
            DefaultSecurityGroupRule` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the defaul security group rule does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent default security group rule.

        :returns: ``None``
        """
        self._delete(
            _default_security_group_rule.DefaultSecurityGroupRule,
            default_security_group_rule,
            ignore_missing=ignore_missing,
        )

    def find_default_security_group_rule(
        self, name_or_id, ignore_missing=True, **query
    ):
        """Find a single default security group rule

        :param str name_or_id: The ID of a default security group rule.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.default_security_group_rule.
            DefaultSecurityGroupRule` or None
        """
        return self._find(
            _default_security_group_rule.DefaultSecurityGroupRule,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_default_security_group_rule(self, default_security_group_rule):
        """Get a single default security group rule

        :param default_security_group_rule:
            The value can be the ID of a default security group rule or a
            :class:`~openstack.network.v2.default_security_group_rule.
            DefaultSecurityGroupRule` instance.

        :returns:
            :class:`~openstack.network.v2.default_security_group_rule.
            DefaultSecurityGroupRule`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _default_security_group_rule.DefaultSecurityGroupRule,
            default_security_group_rule,
        )

    def default_security_group_rules(self, **query):
        """Return a generator of default security group rules

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``description``: The default security group rule description
            * ``direction``: Default security group rule direction
            * ``ether_type``: Must be IPv4 or IPv6, and addresses represented
              in CIDR must match the ingress or egress rule.
            * ``protocol``: Default security group rule protocol
            * ``remote_group_id``: ID of a remote security group

        :returns: A generator of default security group rule objects
        :rtype:
            :class:`~openstack.network.v2.default_security_group_rule.
            DefaultSecurityGroupRule`
        """
        return self._list(
            _default_security_group_rule.DefaultSecurityGroupRule, **query
        )

    def create_segment(self, **attrs):
        """Create a new segment from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.segment.Segment`,
            comprised of the properties on the Segment class.

        :returns: The results of segment creation
        :rtype: :class:`~openstack.network.v2.segment.Segment`
        """
        return self._create(_segment.Segment, **attrs)

    def delete_segment(self, segment, ignore_missing=True):
        """Delete a segment

        :param segment: The value can be either the ID of a segment or a
            :class:`~openstack.network.v2.segment.Segment`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the segment does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent segment.

        :returns: ``None``
        """
        self._delete(_segment.Segment, segment, ignore_missing=ignore_missing)

    def find_segment(self, name_or_id, ignore_missing=True, **query):
        """Find a single segment

        :param name_or_id: The name or ID of a segment.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.segment.Segment` or None
        """
        return self._find(
            _segment.Segment,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_segment(self, segment):
        """Get a single segment

        :param segment: The value can be the ID of a segment or a
            :class:`~openstack.network.v2.segment.Segment`
            instance.

        :returns: One :class:`~openstack.network.v2.segment.Segment`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_segment.Segment, segment)

    def segments(self, **query):
        """Return a generator of segments

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``description``: The segment description
            * ``name``: Name of the segments
            * ``network_id``: ID of the network that owns the segments
            * ``network_type``: Network type for the segments
            * ``physical_network``: Physical network name for the segments
            * ``segmentation_id``: Segmentation ID for the segments

        :returns: A generator of segment objects
        :rtype: :class:`~openstack.network.v2.segment.Segment`
        """
        return self._list(_segment.Segment, **query)

    def update_segment(self, segment, **attrs):
        """Update a segment

        :param segment: Either the id of a segment or a
            :class:`~openstack.network.v2.segment.Segment` instance.
        :param attrs: The attributes to update on the segment represented
            by ``segment``.

        :returns: The update segment
        :rtype: :class:`~openstack.network.v2.segment.Segment`
        """
        return self._update(_segment.Segment, segment, **attrs)

    def service_providers(self, **query):
        """Return a generator of service providers

        :param kwargs  query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of service provider objects
        :rtype: :class:`~openstack.network.v2.service_provider.ServiceProvider`
        """

        return self._list(_service_provider.ServiceProvider, **query)

    def create_service_profile(self, **attrs):
        """Create a new network service flavor profile from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.service_profile.ServiceProfile`,
            comprised of the properties on the ServiceProfile
            class.

        :returns: The results of service profile creation
        :rtype: :class:`~openstack.network.v2.service_profile.ServiceProfile`
        """
        return self._create(_service_profile.ServiceProfile, **attrs)

    def delete_service_profile(self, service_profile, ignore_missing=True):
        """Delete a network service flavor profile

        :param service_profile: The value can be either the ID of a service
            profile or a
            :class:`~openstack.network.v2.service_profile.ServiceProfile`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the service profile does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent service profile.

        :returns: ``None``
        """
        self._delete(
            _service_profile.ServiceProfile,
            service_profile,
            ignore_missing=ignore_missing,
        )

    def find_service_profile(self, name_or_id, ignore_missing=True, **query):
        """Find a single network service flavor profile

        :param name_or_id: The name or ID of a service profile.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.service_profile.ServiceProfile`
            or None
        """
        return self._find(
            _service_profile.ServiceProfile,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_service_profile(self, service_profile):
        """Get a single network service flavor profile

        :param service_profile: The value can be the ID of a service_profile or
            a :class:`~openstack.network.v2.service_profile.ServiceProfile`
            instance.

        :returns: One
            :class:`~openstack.network.v2.service_profile.ServiceProfile`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_service_profile.ServiceProfile, service_profile)

    def service_profiles(self, **query):
        """Return a generator of network service flavor profiles

        :param dict query: Optional query parameters to be sent to limit the
            resources returned. Available parameters inclue:

            * ``description``: The description of  the service flavor profile
            * ``driver``: Provider driver for the service flavor profile
            * ``is_enabled``: Whether the profile is enabled
            * ``project_id``: The owner project ID

        :returns: A generator of service profile objects
        :rtype: :class:`~openstack.network.v2.service_profile.ServiceProfile`
        """
        return self._list(_service_profile.ServiceProfile, **query)

    def update_service_profile(self, service_profile, **attrs):
        """Update a network flavor service profile

        :param service_profile: Either the id of a service profile or a
            :class:`~openstack.network.v2.service_profile.ServiceProfile`
            instance.
        :param attrs: The attributes to update on the service profile
            represented by ``service_profile``.

        :returns: The updated service profile
        :rtype: :class:`~openstack.network.v2.service_profile.ServiceProfile`
        """
        return self._update(
            _service_profile.ServiceProfile, service_profile, **attrs
        )

    def create_subnet(self, **attrs):
        """Create a new subnet from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.subnet.Subnet`,
            comprised of the properties on the Subnet class.

        :returns: The results of subnet creation
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._create(_subnet.Subnet, **attrs)

    def delete_subnet(self, subnet, ignore_missing=True, if_revision=None):
        """Delete a subnet

        :param subnet: The value can be either the ID of a subnet or a
            :class:`~openstack.network.v2.subnet.Subnet` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the subnet does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent subnet.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.

        :returns: ``None``
        """
        self._delete(
            _subnet.Subnet,
            subnet,
            ignore_missing=ignore_missing,
            if_revision=if_revision,
        )

    def find_subnet(self, name_or_id, ignore_missing=True, **query):
        """Find a single subnet

        :param name_or_id: The name or ID of a subnet.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.subnet.Subnet` or None
        """
        return self._find(
            _subnet.Subnet, name_or_id, ignore_missing=ignore_missing, **query
        )

    def get_subnet(self, subnet):
        """Get a single subnet

        :param subnet: The value can be the ID of a subnet or a
            :class:`~openstack.network.v2.subnet.Subnet` instance.

        :returns: One :class:`~openstack.network.v2.subnet.Subnet`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_subnet.Subnet, subnet)

    def subnets(self, **query):
        """Return a generator of subnets

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``cidr``: Subnet CIDR
            * ``description``: The subnet description
            * ``gateway_ip``: Subnet gateway IP address
            * ``ip_version``: Subnet IP address version
            * ``ipv6_address_mode``: The IPv6 address mode
            * ``ipv6_ra_mode``: The IPv6 router advertisement mode
            * ``is_dhcp_enabled``: Subnet has DHCP enabled (boolean)
            * ``name``: Subnet name
            * ``network_id``: ID of network that owns the subnets
            * ``project_id``: Owner tenant ID
            * ``subnet_pool_id``: The subnet pool ID from which to obtain a
              CIDR.

        :returns: A generator of subnet objects
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._list(_subnet.Subnet, **query)

    def update_subnet(self, subnet, if_revision=None, **attrs):
        """Update a subnet

        :param subnet: Either the id of a subnet or a
            :class:`~openstack.network.v2.subnet.Subnet` instance.
        :param int if_revision: Revision to put in If-Match header of update
            request to perform compare-and-swap update.
        :param attrs: The attributes to update on the subnet represented
            by ``subnet``.

        :returns: The updated subnet
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._update(
            _subnet.Subnet, subnet, if_revision=if_revision, **attrs
        )

    def create_subnet_pool(self, **attrs):
        """Create a new subnet pool from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.subnet_pool.SubnetPool`,
            comprised of the properties on the SubnetPool class.

        :returns: The results of subnet pool creation
        :rtype: :class:`~openstack.network.v2.subnet_pool.SubnetPool`
        """
        return self._create(_subnet_pool.SubnetPool, **attrs)

    def delete_subnet_pool(self, subnet_pool, ignore_missing=True):
        """Delete a subnet pool

        :param subnet_pool: The value can be either the ID of a subnet pool or
            a :class:`~openstack.network.v2.subnet_pool.SubnetPool` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the subnet pool does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent subnet pool.

        :returns: ``None``
        """
        self._delete(
            _subnet_pool.SubnetPool, subnet_pool, ignore_missing=ignore_missing
        )

    def find_subnet_pool(self, name_or_id, ignore_missing=True, **query):
        """Find a single subnet pool

        :param name_or_id: The name or ID of a subnet pool.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.subnet_pool.SubnetPool`
            or None
        """
        return self._find(
            _subnet_pool.SubnetPool,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_subnet_pool(self, subnet_pool):
        """Get a single subnet pool

        :param subnet_pool: The value can be the ID of a subnet pool or a
            :class:`~openstack.network.v2.subnet_pool.SubnetPool` instance.

        :returns: One :class:`~openstack.network.v2.subnet_pool.SubnetPool`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_subnet_pool.SubnetPool, subnet_pool)

    def subnet_pools(self, **query):
        """Return a generator of subnet pools

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``address_scope_id``: Subnet pool address scope ID
            * ``description``: The subnet pool description
            * ``ip_version``: The IP address family
            * ``is_default``: Subnet pool is the default (boolean)
            * ``is_shared``: Subnet pool is shared (boolean)
            * ``name``: Subnet pool name
            * ``project_id``: Owner tenant ID

        :returns: A generator of subnet pool objects
        :rtype: :class:`~openstack.network.v2.subnet_pool.SubnetPool`
        """
        return self._list(_subnet_pool.SubnetPool, **query)

    def update_subnet_pool(self, subnet_pool, **attrs):
        """Update a subnet pool

        :param subnet_pool: Either the ID of a subnet pool or a
            :class:`~openstack.network.v2.subnet_pool.SubnetPool` instance.
        :param attrs: The attributes to update on the subnet pool
            represented by ``subnet_pool``.

        :returns: The updated subnet pool
        :rtype: :class:`~openstack.network.v2.subnet_pool.SubnetPool`
        """
        return self._update(_subnet_pool.SubnetPool, subnet_pool, **attrs)

    @staticmethod
    def _check_tag_support(resource):
        try:
            # Check 'tags' attribute exists
            resource.tags
        except AttributeError:
            raise exceptions.InvalidRequest(
                f'{resource.__class__.__name__} resource does not support tag'
            )

    def get_tags(self, resource):
        """Retrieve the tags of a specified resource

        :param resource: :class:`~openstack.resource.Resource` instance.

        :returns: The resource tags list
        :rtype: "list"
        """
        self._check_tag_support(resource)
        return resource.fetch_tags(self).tags

    def set_tags(self, resource, tags):
        """Replace tags of a specified resource with specified tags

        :param resource:
            :class:`~openstack.resource.Resource` instance.
        :param tags: New tags to be set.
        :type tags: "list"

        :returns: The updated resource
        :rtype: :class:`~openstack.resource.Resource`
        """
        self._check_tag_support(resource)
        return resource.set_tags(self, tags)

    def add_tags(self, resource, tags):
        """Add tags to a specified resource

        :param resource: :class:`~openstack.resource.Resource` instance.
        :param tags: New tags to be set.
        :type tags: "list"

        :returns: The updated resource
        :rtype: :class:`~openstack.resource.Resource`
        """
        self._check_tag_support(resource)
        return resource.add_tags(self, tags)

    def add_tag(self, resource, tag):
        """Add one single tag to a specified resource

        :param resource: :class:`~openstack.resource.Resource` instance.
        :param tag: New tag to be set.
        :type tag: "str"

        :returns: The updated resource
        :rtype: :class:`~openstack.resource.Resource`
        """
        self._check_tag_support(resource)
        return resource.add_tag(self, tag)

    def remove_tag(self, resource, tag):
        """Remove one single tag of a specified resource

        :param resource: :class:`~openstack.resource.Resource` instance.
        :param tag: New tag to be set.
        :type tag: "str"

        :returns: The updated resource
        :rtype: :class:`~openstack.resource.Resource`
        """
        self._check_tag_support(resource)
        return resource.remove_tag(self, tag)

    def remove_all_tags(self, resource):
        """Remove all tags of a specified resource

        :param resource: :class:`~openstack.resource.Resource` instance.

        :returns: The updated resource
        :rtype: :class:`~openstack.resource.Resource`
        """
        self._check_tag_support(resource)
        return resource.remove_all_tags(self)

    def check_tag(self, resource, tag):
        """Checks if tag exists on the specified resource

        :param resource: :class:`~openstack.resource.Resource` instance.
        :param tag: Tag to be tested
        :type tags: "string"

        :returns: If the tag exists in the specified resource
        :rtype: bool
        """
        self._check_tag_support(resource)
        return resource.check_tag(self, tag)

    def create_trunk(self, **attrs):
        """Create a new trunk from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.trunk.Trunk`,
            comprised of the properties on the Trunk class.

        :returns: The results of trunk creation
        :rtype: :class:`~openstack.network.v2.trunk.Trunk`
        """
        return self._create(_trunk.Trunk, **attrs)

    def delete_trunk(self, trunk, ignore_missing=True):
        """Delete a trunk

        :param trunk: The value can be either the ID of trunk or a
            :class:`openstack.network.v2.trunk.Trunk` instance

        :returns: ``None``
        """
        self._delete(_trunk.Trunk, trunk, ignore_missing=ignore_missing)

    def find_trunk(self, name_or_id, ignore_missing=True, **query):
        """Find a single trunk

        :param name_or_id: The name or ID of a trunk.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.trunk.Trunk`
            or None
        """
        return self._find(
            _trunk.Trunk, name_or_id, ignore_missing=ignore_missing, **query
        )

    def get_trunk(self, trunk):
        """Get a single trunk

        :param trunk: The value can be the ID of a trunk or a
            :class:`~openstack.network.v2.trunk.Trunk` instance.

        :returns: One
            :class:`~openstack.network.v2.trunk.Trunk`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_trunk.Trunk, trunk)

    def trunks(self, **query):
        """Return a generator of trunks

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of trunk objects
        :rtype: :class:`~openstack.network.v2.trunk.trunk`
        """
        return self._list(_trunk.Trunk, **query)

    def update_trunk(self, trunk, **attrs):
        """Update a trunk

        :param trunk: Either the id of a trunk or a
            :class:`~openstack.network.v2.trunk.Trunk` instance.
        :param attrs: The attributes to update on the trunk
            represented by ``trunk``.

        :returns: The updated trunk
        :rtype: :class:`~openstack.network.v2.trunk.Trunk`
        """
        return self._update(_trunk.Trunk, trunk, **attrs)

    def add_trunk_subports(self, trunk, subports):
        """Set sub_ports on trunk

        :param trunk: The value can be the ID of a trunk or a
            :class:`~openstack.network.v2.trunk.Trunk` instance.
        :param subports: New subports to be set.
        :type subports: "list"

        :returns: The updated trunk
        :rtype: :class:`~openstack.network.v2.trunk.Trunk`
        """
        trunk = self._get_resource(_trunk.Trunk, trunk)
        return trunk.add_subports(self, subports)

    def delete_trunk_subports(self, trunk, subports):
        """Remove sub_ports from trunk

        :param trunk: The value can be the ID of a trunk or a
            :class:`~openstack.network.v2.trunk.Trunk` instance.
        :param subports: Subports to be removed.
        :type subports: "list"

        :returns: The updated trunk
        :rtype: :class:`~openstack.network.v2.trunk.Trunk`
        """
        trunk = self._get_resource(_trunk.Trunk, trunk)
        return trunk.delete_subports(self, subports)

    def get_trunk_subports(self, trunk):
        """Get sub_ports configured on trunk

        :param trunk: The value can be the ID of a trunk or a
            :class:`~openstack.network.v2.trunk.Trunk` instance.

        :returns: Trunk sub_ports
        :rtype: "list"
        """
        trunk = self._get_resource(_trunk.Trunk, trunk)
        return trunk.get_subports(self)

    # ========== VPNaas ==========
    # ========== VPN Endpoint group ==========

    def create_vpn_endpoint_group(self, **attrs):
        """Create a new vpn endpoint group from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.vpn_endpoint_group.VpnEndpointGroup`,
            comprised of the properties on the VpnEndpointGroup class.

        :returns: The results of vpn endpoint group creation.
        :rtype:
            :class:`~openstack.network.v2.vpn_endpoint_group.VpnEndpointGroup`
        """
        return self._create(_vpn_endpoint_group.VpnEndpointGroup, **attrs)

    def delete_vpn_endpoint_group(
        self, vpn_endpoint_group, ignore_missing=True
    ):
        """Delete a vpn service

        :param vpn_endpoint_group:
            The value can be either the ID of a vpn service or a
            :class:`~openstack.network.v2.vpn_endpoint_group.VpnEndpointGroup`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the vpn service does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent vpn service.

        :returns: ``None``
        """
        self._delete(
            _vpn_endpoint_group.VpnEndpointGroup,
            vpn_endpoint_group,
            ignore_missing=ignore_missing,
        )

    def find_vpn_endpoint_group(
        self, name_or_id, ignore_missing=True, **query
    ):
        """Find a single vpn service

        :param name_or_id: The name or ID of a vpn service.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.vpn_endpoint_group.VpnEndpointGroup`
            or None
        """
        return self._find(
            _vpn_endpoint_group.VpnEndpointGroup,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_vpn_endpoint_group(self, vpn_endpoint_group):
        """Get a single vpn service

        :param vpn_endpoint_group: The value can be the ID of a vpn service
            or a
            :class:`~openstack.network.v2.vpn_endpoint_group.VpnEndpointGroup`
            instance.

        :returns: One
            :class:`~openstack.network.v2.vpn_endpoint_group.VpnEndpointGroup`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _vpn_endpoint_group.VpnEndpointGroup, vpn_endpoint_group
        )

    def vpn_endpoint_groups(self, **query):
        """Return a generator of vpn services

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of vpn service objects
        :rtype:
            :class:`~openstack.network.v2.vpn_endpoint_group.VpnEndpointGroup`
        """
        return self._list(_vpn_endpoint_group.VpnEndpointGroup, **query)

    def update_vpn_endpoint_group(self, vpn_endpoint_group, **attrs):
        """Update a vpn service

        :param vpn_endpoint_group: Either the id of a vpn service or a
            :class:`~openstack.network.v2.vpn_endpoint_group.VpnEndpointGroup`
            instance.
        :param attrs: The attributes to update on the VPN service
            represented by ``vpn_endpoint_group``.

        :returns: The updated vpnservice
        :rtype:
            :class:`~openstack.network.v2.vpn_endpoint_group.VpnEndpointGroup`
        """
        return self._update(
            _vpn_endpoint_group.VpnEndpointGroup, vpn_endpoint_group, **attrs
        )

    # ========== IPsec Site Connection ==========
    def create_vpn_ipsec_site_connection(self, **attrs):
        """Create a new IPsec site connection from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.vpn_ipsec_site_connection.VpnIPSecSiteConnection`,
            comprised of the properties on the IPSecSiteConnection class.

        :returns: The results of IPsec site connection creation
        :rtype:
            :class:`~openstack.network.v2.vpn_ipsec_site_connection.VpnIPSecSiteConnection`
        """
        return self._create(
            _ipsec_site_connection.VpnIPSecSiteConnection, **attrs
        )

    def find_vpn_ipsec_site_connection(
        self, name_or_id, ignore_missing=True, **query
    ):
        """Find a single IPsec site connection

        :param name_or_id: The name or ID of an IPsec site connection.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException`
            will be raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods such as query filters.
        :returns: One
            :class:`~openstack.network.v2.vpn_ipsec_site_connection.VpnIPSecSiteConnection`
            or None
        """
        return self._find(
            _ipsec_site_connection.VpnIPSecSiteConnection,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_vpn_ipsec_site_connection(self, ipsec_site_connection):
        """Get a single IPsec site connection

        :param ipsec_site_connection: The value can be the ID of an IPsec site
            connection or a
            :class:`~openstack.network.v2.vpn_ipsec_site_connection.VpnIPSecSiteConnection`
            instance.

        :returns: One
            :class:`~openstack.network.v2.vpn_ipsec_site_connection.VpnIPSecSiteConnection`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _ipsec_site_connection.VpnIPSecSiteConnection,
            ipsec_site_connection,
        )

    def vpn_ipsec_site_connections(self, **query):
        """Return a generator of IPsec site connections

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

        :returns: A generator of IPsec site connection objects
        :rtype:
            :class:`~openstack.network.v2.vpn_ipsec_site_connection.VpnIPSecSiteConnection`
        """
        return self._list(
            _ipsec_site_connection.VpnIPSecSiteConnection, **query
        )

    def update_vpn_ipsec_site_connection(self, ipsec_site_connection, **attrs):
        """Update a IPsec site connection

        :ipsec_site_connection: Either the id of an IPsec site connection or
            a
            :class:`~openstack.network.v2.vpn_ipsec_site_connection.VpnIPSecSiteConnection`
            instance.
        :param attrs: The attributes to update on the IPsec site
            connection represented by ``ipsec_site_connection``.

        :returns: The updated IPsec site connection
        :rtype:
            :class:`~openstack.network.v2.vpn_ipsec_site_connection.VpnIPSecSiteConnection`
        """
        return self._update(
            _ipsec_site_connection.VpnIPSecSiteConnection,
            ipsec_site_connection,
            **attrs,
        )

    def delete_vpn_ipsec_site_connection(
        self, ipsec_site_connection, ignore_missing=True
    ):
        """Delete a IPsec site connection

        :param ipsec_site_connection: The value can be either the ID of an
            IPsec site connection, or a
            :class:`~openstack.network.v2.vpn_ipsec_site_connection.VpnIPSecSiteConnection`
            instance.
        :param bool ignore_missing:
            When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the IPsec site connection does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent IPsec site connection.

        :returns: ``None``
        """
        self._delete(
            _ipsec_site_connection.VpnIPSecSiteConnection,
            ipsec_site_connection,
            ignore_missing=ignore_missing,
        )

    # ========== IKEPolicy ==========
    def create_vpn_ike_policy(self, **attrs):
        """Create a new ike policy from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.vpn_ike_policy.VpnIkePolicy`,
            comprised of the properties on the VpnIkePolicy class.

        :returns: The results of ike policy creation :rtype:
            :class:`~openstack.network.v2.vpn_ike_policy.VpnIkePolicy`
        """
        return self._create(_ike_policy.VpnIkePolicy, **attrs)

    def find_vpn_ike_policy(self, name_or_id, ignore_missing=True, **query):
        """Find a single ike policy

        :param name_or_id: The name or ID of an IKE policy.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException`
            will be raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods such as query filters.
        :returns: One
            :class:`~openstack.network.v2.vpn_ike_policy.VpnIkePolicy` or None.
        """
        return self._find(
            _ike_policy.VpnIkePolicy,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_vpn_ike_policy(self, ike_policy):
        """Get a single ike policy

        :param ike_policy: The value can be the ID of an IKE policy or a
            :class:`~openstack.network.v2.vpn_ike_policy.VpnIkePolicy`
            instance.

        :returns: One
            :class:`~openstack.network.v2.vpn_ike_policy.VpnIkePolicy`
        :rtype: :class:`~openstack.network.v2.ike_policy.VpnIkePolicy`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(_ike_policy.VpnIkePolicy, ike_policy)

    def vpn_ike_policies(self, **query):
        """Return a generator of IKE policies

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

        :returns: A generator of ike policy objects
        :rtype: :class:`~openstack.network.v2.vpn_ike_policy.VpnIkePolicy`
        """
        return self._list(_ike_policy.VpnIkePolicy, **query)

    def update_vpn_ike_policy(self, ike_policy, **attrs):
        """Update an IKE policy

        :ike_policy: Either the IK of an IKE policy or a
            :class:`~openstack.network.v2.vpn_ike_policy.VpnIkePolicy`
            instance.
        :param attrs: The attributes to update on the ike policy
            represented by ``ike_policy``.

        :returns: The updated ike policy
        :rtype: :class:`~openstack.network.v2.vpn_ike_policy.VpnIkePolicy`
        """
        return self._update(_ike_policy.VpnIkePolicy, ike_policy, **attrs)

    def delete_vpn_ike_policy(self, ike_policy, ignore_missing=True):
        """Delete an IKE policy

        :param ike_policy: The value can be either the ID of an ike policy, or
            a :class:`~openstack.network.v2.vpn_ike_policy.VpnIkePolicy`
            instance.
        :param bool ignore_missing:
            When set to ``False``
            :class:`~openstack.exceptions.NotFoundException`
            will be raised when the ike policy does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent ike policy.

        :returns: ``None``
        """
        self._delete(
            _ike_policy.VpnIkePolicy, ike_policy, ignore_missing=ignore_missing
        )

    # ========== IPSecPolicy ==========
    def create_vpn_ipsec_policy(self, **attrs):
        """Create a new IPsec policy from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.vpn_ipsec_policy.VpnIpsecPolicy`,
            comprised of the properties on the VpnIpsecPolicy class.

        :returns: The results of IPsec policy creation :rtype:
            :class:`~openstack.network.v2.vpn_ipsec_policy.VpnIpsecPolicy`
        """
        return self._create(_ipsec_policy.VpnIpsecPolicy, **attrs)

    def find_vpn_ipsec_policy(self, name_or_id, ignore_missing=True, **query):
        """Find a single IPsec policy

        :param name_or_id: The name or ID of an IPsec policy.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException`
            will be raised when the resource does not exist.  When set to
            ``True``, None will be returned when attempting to find a
            nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods such as query filters.
        :returns: One
            :class:`~openstack.network.v2.vpn_ipsec_policy.VpnIpsecPolicy`
            or None.
        """
        return self._find(
            _ipsec_policy.VpnIpsecPolicy,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_vpn_ipsec_policy(self, ipsec_policy):
        """Get a single IPsec policy

        :param ipsec_policy: The value can be the ID of an IPcec policy or a
            :class:`~openstack.network.v2.vpn_ipsec_policy.VpnIpsecPolicy`
            instance.

        :returns: One
            :class:`~openstack.network.v2.vpn_ipsec_policy.VpnIpsecPolicy`
        :rtype: :class:`~openstack.network.v2.ipsec_policy.VpnIpsecPolicy`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(_ipsec_policy.VpnIpsecPolicy, ipsec_policy)

    def vpn_ipsec_policies(self, **query):
        """Return a generator of IPsec policies

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

        :returns: A generator of IPsec policy objects
        :rtype: :class:`~openstack.network.v2.vpn_ipsec_policy.VpnIpsecPolicy`
        """
        return self._list(_ipsec_policy.VpnIpsecPolicy, **query)

    def update_vpn_ipsec_policy(self, ipsec_policy, **attrs):
        """Update an IPsec policy

        :ipsec_policy: Either the id of an IPsec policy or a
            :class:`~openstack.network.v2.vpn_ipsec_policy.VpnIpsecPolicy`
            instance.
        :param attrs: The attributes to update on the IPsec policy
            represented by ``ipsec_policy``.

        :returns: The updated IPsec policy
        :rtype: :class:`~openstack.network.v2.vpn_ipsec_policy.VpnIpsecPolicy`
        """
        return self._update(
            _ipsec_policy.VpnIpsecPolicy, ipsec_policy, **attrs
        )

    def delete_vpn_ipsec_policy(self, ipsec_policy, ignore_missing=True):
        """Delete an IPsec policy

        :param ipsec_policy: The value can be either the ID of an IPsec policy,
            or a
            :class:`~openstack.network.v2.vpn_ipsec_policy.VpnIpsecPolicy`
            instance.
        :param bool ignore_missing:
            When set to ``False``
            :class:`~openstack.exceptions.NotFoundException`
            will be raised when the IPsec policy does not exist.  When set to
            ``True``, no exception will be set when attempting to delete a
            nonexistent IPsec policy.

        :returns: ``None``
        """
        self._delete(
            _ipsec_policy.VpnIpsecPolicy,
            ipsec_policy,
            ignore_missing=ignore_missing,
        )

    # ========== VPN Service ==========
    def create_vpn_service(self, **attrs):
        """Create a new vpn service from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.vpn_service.VpnService`,
            comprised of the properties on the VpnService class.

        :returns: The results of vpn service creation
        :rtype: :class:`~openstack.network.v2.vpn_service.VpnService`
        """
        return self._create(_vpn_service.VpnService, **attrs)

    def delete_vpn_service(self, vpn_service, ignore_missing=True):
        """Delete a vpn service

        :param vpn_service:
            The value can be either the ID of a vpn service or a
            :class:`~openstack.network.v2.vpn_service.VpnService` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the vpn service does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent vpn service.

        :returns: ``None``
        """
        self._delete(
            _vpn_service.VpnService, vpn_service, ignore_missing=ignore_missing
        )

    def find_vpn_service(self, name_or_id, ignore_missing=True, **query):
        """Find a single vpn service

        :param name_or_id: The name or ID of a vpn service.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.vpn_service.VpnService`
            or None
        """
        return self._find(
            _vpn_service.VpnService,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_vpn_service(self, vpn_service):
        """Get a single vpn service

        :param vpn_service: The value can be the ID of a vpn service or a
            :class:`~openstack.network.v2.vpn_service.VpnService`
            instance.

        :returns: One
            :class:`~openstack.network.v2.vpn_service.VpnService`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_vpn_service.VpnService, vpn_service)

    def vpn_services(self, **query):
        """Return a generator of vpn services

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of vpn service objects
        :rtype: :class:`~openstack.network.v2.vpn_service.VpnService`
        """
        return self._list(_vpn_service.VpnService, **query)

    def update_vpn_service(self, vpn_service, **attrs):
        """Update a vpn service

        :param vpn_service: Either the id of a vpn service or a
            :class:`~openstack.network.v2.vpn_service.VpnService` instance.
        :param attrs: The attributes to update on the VPN service
            represented by ``vpn_service``.

        :returns: The updated vpnservice
        :rtype: :class:`~openstack.network.v2.vpn_service.VpnService`
        """
        return self._update(_vpn_service.VpnService, vpn_service, **attrs)

    def create_floating_ip_port_forwarding(self, floating_ip, **attrs):
        """Create a new floating ip port forwarding from attributes

        :param floating_ip: The value can be either the ID of a floating ip
            or a :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param attrs:Keyword arguments which will be used to create
            a:class:`~openstack.network.v2.port_forwarding.PortForwarding`,
            comprised of the properties on the PortForwarding class.

        :returns: The results of port forwarding creation
        :rtype: :class:`~openstack.network.v2.port_forwarding.PortForwarding`
        """
        floatingip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        return self._create(
            _port_forwarding.PortForwarding,
            floatingip_id=floatingip.id,
            **attrs,
        )

    def delete_floating_ip_port_forwarding(
        self, floating_ip, port_forwarding, ignore_missing=True
    ):
        """Delete a floating IP port forwarding.

        :param floating_ip: The value can be either the ID of a floating ip
            or a :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param port_forwarding: The value can be either the ID of a port
            forwarding or a
            :class:`~openstack.network.v2.port_forwarding.PortForwarding`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the floating ip does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent ip.

        :returns: ``None``
        """
        floatingip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        self._delete(
            _port_forwarding.PortForwarding,
            port_forwarding,
            ignore_missing=ignore_missing,
            floatingip_id=floatingip.id,
        )

    def find_floating_ip_port_forwarding(
        self, floating_ip, port_forwarding_id, ignore_missing=True, **query
    ):
        """Find a floating ip port forwarding

        :param floating_ip: The value can be the ID of the Floating IP that the
            port forwarding  belongs or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP` instance.
        :param port_forwarding_id: The ID of a port forwarding.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.port_forwarding.PortForwarding`
            or None
        """
        floatingip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        return self._find(
            _port_forwarding.PortForwarding,
            port_forwarding_id,
            ignore_missing=ignore_missing,
            floatingip_id=floatingip.id,
            **query,
        )

    def get_floating_ip_port_forwarding(self, floating_ip, port_forwarding):
        """Get a floating ip port forwarding

        :param floating_ip: The value can be the ID of the Floating IP that the
            port forwarding  belongs or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP` instance.
        :param port_forwarding: The value can be the ID of a port forwarding
            or a
            :class:`~openstack.network.v2.port_forwarding.PortForwarding`
            instance.
        :returns: One
            :class:`~openstack.network.v2.port_forwarding.PortForwarding`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        floatingip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        return self._get(
            _port_forwarding.PortForwarding,
            port_forwarding,
            floatingip_id=floatingip.id,
        )

    def floating_ip_port_forwardings(self, floating_ip, **query):
        """Return a generator of floating ip port forwarding

        :param floating_ip: The value can be the ID of the Floating IP that the
            port forwarding  belongs or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param kwargs **query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of floating ip port forwarding objects
        :rtype:
            :class:`~openstack.network.v2.port_forwarding.PortForwarding`
        """
        floatingip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        return self._list(
            _port_forwarding.PortForwarding,
            floatingip_id=floatingip.id,
            **query,
        )

    def update_floating_ip_port_forwarding(
        self, floating_ip, port_forwarding, **attrs
    ):
        """Update a floating ip port forwarding

        :param floating_ip: The value can be the ID of the Floating IP that the
            port forwarding  belongs or a
            :class:`~openstack.network.v2.floating_ip.FloatingIP`
            instance.
        :param port_forwarding: Either the id of a floating ip port forwarding
            or a
            :class:`~openstack.network.v2.port_forwarding.PortForwarding`instance.
        :param attrs: The attributes to update on the floating ip port
            forwarding represented by ``floating_ip``.

        :returns: The updated floating ip port forwarding
        :rtype: :class:`~openstack.network.v2.port_forwarding.PortForwarding`
        """
        floatingip = self._get_resource(_floating_ip.FloatingIP, floating_ip)
        return self._update(
            _port_forwarding.PortForwarding,
            port_forwarding,
            floatingip_id=floatingip.id,
            **attrs,
        )

    def create_conntrack_helper(self, router, **attrs):
        """Create a new L3 conntrack helper from attributes

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.l3_conntrack_helper.ConntrackHelper`,
            comprised of the properties on the ConntrackHelper class.

        :returns: The results of conntrack helper creation
        :rtype:
            :class:`~openstack.network.v2.l3_conntrack_helper.ConntrackHelper`
        """
        router = self._get_resource(_router.Router, router)
        return self._create(
            _l3_conntrack_helper.ConntrackHelper, router_id=router.id, **attrs
        )

    def conntrack_helpers(self, router, **query):
        """Return a generator of conntrack helpers

        :param router: Either the router ID or an instance of
            :class:`~openstack.network.v2.router.Router`
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.
        :returns: A generator of conntrack helper objects
        :rtype:
            :class:`~openstack.network.v2.l3_conntrack_helper.ConntrackHelper`
        """
        router = self._get_resource(_router.Router, router)
        return self._list(
            _l3_conntrack_helper.ConntrackHelper, router_id=router.id, **query
        )

    def get_conntrack_helper(self, conntrack_helper, router):
        """Get a single L3 conntrack helper

        :param conntrack_helper: The value can be the ID of a L3 conntrack
            helper or a
            :class:`~openstack.network.v2.l3_conntrack_helper.ConntrackHelper`,
            instance.
        :param router: The value can be the ID of a Router or a
            :class:`~openstack.network.v2.router.Router` instance.

        :returns: One
            :class:`~openstack.network.v2.l3_conntrack_helper.ConntrackHelper`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        router = self._get_resource(_router.Router, router)
        return self._get(
            _l3_conntrack_helper.ConntrackHelper,
            conntrack_helper,
            router_id=router.id,
        )

    def update_conntrack_helper(self, conntrack_helper, router, **attrs):
        """Update a L3 conntrack_helper

        :param conntrack_helper: The value can be the ID of a L3 conntrack
            helper or a
            :class:`~openstack.network.v2.l3_conntrack_helper.ConntrackHelper`,
            instance.
        :param router: The value can be the ID of a Router or a
            :class:`~openstack.network.v2.router.Router` instance.
        :param attrs: The attributes to update on the L3 conntrack helper
            represented by ``conntrack_helper``.

        :returns: The updated conntrack helper
        :rtype:
            :class:`~openstack.network.v2.l3_conntrack_helper.ConntrackHelper`

        """
        router = self._get_resource(_router.Router, router)
        return self._update(
            _l3_conntrack_helper.ConntrackHelper,
            conntrack_helper,
            router_id=router.id,
            **attrs,
        )

    def delete_conntrack_helper(
        self, conntrack_helper, router, ignore_missing=True
    ):
        """Delete a L3 conntrack_helper

        :param conntrack_helper: The value can be the ID of a L3 conntrack
            helper or a
            :class:`~openstack.network.v2.l3_conntrack_helper.ConntrackHelper`,
            instance.
        :param router: The value can be the ID of a Router or a
            :class:`~openstack.network.v2.router.Router` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the floating ip does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent ip.

        :returns: ``None``
        """
        router = self._get_resource(_router.Router, router)
        self._delete(
            _l3_conntrack_helper.ConntrackHelper,
            conntrack_helper,
            router_id=router.id,
            ignore_missing=ignore_missing,
        )

    def create_tap_flow(self, **attrs):
        """Create a new Tap Flow from attributes"""
        return self._create(_tap_flow.TapFlow, **attrs)

    def delete_tap_flow(self, tap_flow, ignore_missing=True):
        """Delete a Tap Flow"""
        self._delete(
            _tap_flow.TapFlow, tap_flow, ignore_missing=ignore_missing
        )

    def find_tap_flow(self, name_or_id, ignore_missing=True, **query):
        """Find a single Tap Service"""
        return self._find(
            _tap_flow.TapFlow,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_tap_flow(self, tap_flow):
        """Get a signle Tap Flow"""
        return self._get(_tap_flow.TapFlow, tap_flow)

    def update_tap_flow(self, tap_flow, **attrs):
        """Update a Tap Flow"""
        return self._update(_tap_flow.TapFlow, tap_flow, **attrs)

    def tap_flows(self, **query):
        """Return a generator of Tap Flows"""
        return self._list(_tap_flow.TapFlow, **query)

    def create_tap_mirror(self, **attrs):
        """Create a new Tap Mirror from attributes"""
        return self._create(_tap_mirror.TapMirror, **attrs)

    def delete_tap_mirror(self, tap_mirror, ignore_missing=True):
        """Delete a Tap Mirror"""
        self._delete(
            _tap_mirror.TapMirror, tap_mirror, ignore_missing=ignore_missing
        )

    def find_tap_mirror(self, name_or_id, ignore_missing=True, **query):
        """Find a single Tap Mirror"""
        return self._find(
            _tap_mirror.TapMirror,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_tap_mirror(self, tap_mirror):
        """Get a signle Tap Mirror"""
        return self._get(_tap_mirror.TapMirror, tap_mirror)

    def update_tap_mirror(self, tap_mirror, **attrs):
        """Update a Tap Mirror"""
        return self._update(_tap_mirror.TapMirror, tap_mirror, **attrs)

    def tap_mirrors(self, **query):
        """Return a generator of Tap Mirrors"""
        return self._list(_tap_mirror.TapMirror, **query)

    def create_tap_service(self, **attrs):
        """Create a new Tap Service from attributes"""
        return self._create(_tap_service.TapService, **attrs)

    def delete_tap_service(self, tap_service, ignore_missing=True):
        """Delete a Tap Service"""
        self._delete(
            _tap_service.TapService, tap_service, ignore_missing=ignore_missing
        )

    def find_tap_service(self, name_or_id, ignore_missing=True, **query):
        """Find a single Tap Service"""
        return self._find(
            _tap_service.TapService,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_tap_service(self, tap_service):
        """Get a signle Tap Service"""
        return self._get(_tap_service.TapService, tap_service)

    def update_tap_service(self, tap_service, **attrs):
        """Update a Tap Service"""
        return self._update(_tap_service.TapService, tap_service, **attrs)

    def tap_services(self, **query):
        """Return a generator of Tap Services"""
        return self._list(_tap_service.TapService, **query)

    def create_sfc_flow_classifier(self, **attrs):
        """Create a new Flow Classifier from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.sfc_flow_classifier.SfcFlowClassifier`,
            comprised of the properties on the SfcFlowClassifier class.

        :returns: The results of SFC Flow Classifier creation
        :rtype:
            :class:`~openstack.network.v2.sfc_flow_classifier.SfcFlowClassifier`
        """

        return self._create(_sfc_flow_classifier.SfcFlowClassifier, **attrs)

    def delete_sfc_flow_classifier(self, flow_classifier, ignore_missing=True):
        """Delete a Flow Classifier

        :param flow_classifier:
            The value can be either the ID of a flow classifier or a
            :class:`~openstack.network.v2.sfc_flow_classifier.SfcFlowClassifier`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the  flow classifier does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent flow classifier.

        :returns: ``None``
        """
        self._delete(
            _sfc_flow_classifier.SfcFlowClassifier,
            flow_classifier,
            ignore_missing=ignore_missing,
        )

    def find_sfc_flow_classifier(
        self, name_or_id, ignore_missing=True, **query
    ):
        """Find a single Flow Classifier

        :param str name_or_id: The name or ID of an SFC flow classifier.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.sfc_flow_classifier.
            SfcFlowClassifier` or None
        """
        return self._find(
            _sfc_flow_classifier.SfcFlowClassifier,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_sfc_flow_classifier(self, flow_classifier):
        """Get a single Flow Classifier

        :param flow_classifier:
            The value can be the ID of an SFC flow classifier or a
            :class:`~openstack.network.v2.sfc_flow_classifier.SfcFlowClassifier` instance.

        :returns:
            :class:`~openstack.network.v2.sfc_flow_classifier.SfcFlowClassifier`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _sfc_flow_classifier.SfcFlowClassifier, flow_classifier
        )

    def update_sfc_flow_classifier(self, flow_classifier, **attrs):
        """Update a Flow Classifier

        :param flow_classifier: The value can be the ID of a Flow Classifier
            :class:`~openstack.network.v2.sfc_flow_classifier.SfcFlowClassifier`,
            instance.
        :param attrs: The attributes to update on the Flow Classifier

        :returns: The updated Flow Classifier.
        :rtype:
            :class:`~openstack.network.v2.sfc_flow_classifier.SfcFlowClassifier`
        """
        return self._update(
            _sfc_flow_classifier.SfcFlowClassifier, flow_classifier, **attrs
        )

    def sfc_flow_classifiers(self, **query):
        """Return a generator of Flow Classifiers

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``name``: The name of the flow classifier.
            * ``description``: The flow classifier description
            * ``ethertype``: Must be IPv4 or IPv6.
            * ``protocol``: Flow classifier protocol

        :returns: A generator of SFC Flow classifier objects
        :rtype:
            :class:`~openstack.network.v2.sfc_flow_classifier.
            SfcFlowClassifier`
        """
        return self._list(_sfc_flow_classifier.SfcFlowClassifier, **query)

    def create_sfc_port_chain(self, **attrs):
        """Create a new Port Chain from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.sfc_port_chain.SfcPortChain`,
            comprised of the properties on the SfcPortchain class.

        :returns: The results of SFC Port Chain creation
        :rtype:
            :class:`~openstack.network.v2.sfc_port_chain.SfcPortChain`
        """
        return self._create(_sfc_port_chain.SfcPortChain, **attrs)

    def delete_sfc_port_chain(self, port_chain, ignore_missing=True):
        """Delete a Port Chain

        :param port_chain:
            The value can be either the ID of a port chain or a
            :class:`~openstack.network.v2.sfc_port_chain.SfcPortChain`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the port chain does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent port chain.

        :returns: ``None``
        """
        self._delete(
            _sfc_port_chain.SfcPortChain,
            port_chain,
            ignore_missing=ignore_missing,
        )

    def find_sfc_port_chain(self, name_or_id, ignore_missing=True, **query):
        """Find a single Port Chain

        :param str name_or_id: The name or ID of an SFC port chain.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.sfc_port_chain.
            SfcPortChain` or None
        """
        return self._find(
            _sfc_port_chain.SfcPortChain,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_sfc_port_chain(self, port_chain):
        """Get a signle Port Chain

        :param port_chain:
            The value can be the ID of an SFC port chain or a
            :class:`~openstack.network.v2.sfc_port_chain.SfcPortChain`
            instance.

        :returns:
            :class:`~openstack.network.v2.sfc_port_chain.SfcPortchain`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_sfc_port_chain.SfcPortChain, port_chain)

    def update_sfc_port_chain(self, port_chain, **attrs):
        """Update a Port Chain

        :param flow_classifier: The value can be the ID of a Flow Classifier
            :class:`~openstack.network.v2.sfc_flow_classifier.SfcFlowClassifier`,
            instance.
        :param attrs: The attributes to update on the Flow Classifier

        :returns: The updated Flow Classifier.
        :rtype:
            :class:`~openstack.network.v2.sfc_flow_classifier.SfcFlowClassifier`
        """
        return self._update(_sfc_port_chain.SfcPortChain, port_chain, **attrs)

    def sfc_port_chains(self, **query):
        """Return a generator of Port Chains

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``name``: The name of the port chain
            * ``description``: The port chain description

        :returns: A generator of SFC port chain objects
        :rtype:
            :class:`~openstack.network.v2.sfc_port_chain.SfcPortChain`
        """
        return self._list(_sfc_port_chain.SfcPortChain, **query)

    def create_sfc_port_pair(self, **attrs):
        """Create a new Port Pair from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.sfc_port_pair.SfcPortPair`,
            comprised of the properties on the SfcPortPair class.

        :returns: The results of SFC Port Pair creation
        :rtype:
            :class:`~openstack.network.v2.sfc_port_pair.SfPortPair`
        """
        return self._create(_sfc_port_pair.SfcPortPair, **attrs)

    def delete_sfc_port_pair(self, port_pair, ignore_missing=True):
        """Delete a Port Pair

        :param port_pair:
            The value can be either the ID of a port pair or a
            :class:`~openstack.network.v2.sfc_port_pair.SfcPortPair`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the port pair does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent port pair.

        :returns: ``None``
        """
        self._delete(
            _sfc_port_pair.SfcPortPair,
            port_pair,
            ignore_missing=ignore_missing,
        )

    def find_sfc_port_pair(self, name_or_id, ignore_missing=True, **query):
        """Find a single Port Pair

        :param str name_or_id: The name or ID of an SFC port pair.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.sfc_port_pair.SfcPortPair` or None
        """
        return self._find(
            _sfc_port_pair.SfcPortPair,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_sfc_port_pair(self, port_pair):
        """Get a signle Port Pair

        :param port_pair:
            The value can be the ID of an SFC port pair or a
            :class:`~openstack.network.v2.sfc_port_pair.SfcPortPair`
            instance.

        :returns:
            :class:`~openstack.network.v2.sfc_port_pair.SfcPortPair`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_sfc_port_pair.SfcPortPair, port_pair)

    def update_sfc_port_pair(self, port_pair, **attrs):
        """Update a Port Pair

        :param port_pair: The value can be the ID of a Port Pair
            :class:`~openstack.network.v2.sfc_port_pair.SfcPortPair`,
            instance.
        :param attrs: The attributes to update on the Port Pair

        :returns: The updated Port Pair.
        :rtype:
            :class:`~openstack.network.v2.sfc_port_pair.SfcPortPair`
        """
        return self._update(_sfc_port_pair.SfcPortPair, port_pair, **attrs)

    def sfc_port_pairs(self, **query):
        """Return a generator of Port Pairs

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``name``: The name of the port pair.
            * ``description``: The port pair description.

        :returns: A generator of SFC port pair objects
        :rtype:
            :class:`~openstack.network.v2.sfc_port_pair.SfcPortPair`
        """
        return self._list(_sfc_port_pair.SfcPortPair, **query)

    def create_sfc_port_pair_group(self, **attrs):
        """Create a new Port Pair Group from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.sfc_port_pair_group.SfcPortPairGroup`,
            comprised of the properties on the SfcPortPairGroup class.

        :returns: The results of SFC Port Pair Group creation
        :rtype:
            :class:`~openstack.network.v2.sfc_port_pair_group.SfcPortPairGroup`
        """
        return self._create(_sfc_port_pair_group.SfcPortPairGroup, **attrs)

    def delete_sfc_port_pair_group(self, port_pair_group, ignore_missing=True):
        """Delete a Port Pair Group

        :param port_pair_group:
            The value can be either the ID of a port pair group or a
            :class:`~openstack.network.v2.sfc_port_pair_group.
            SfcPortPairGroup` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the port pair group does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent port pair group.

        :returns: ``None``
        """
        self._delete(
            _sfc_port_pair_group.SfcPortPairGroup,
            port_pair_group,
            ignore_missing=ignore_missing,
        )

    def find_sfc_port_pair_group(
        self, name_or_id, ignore_missing=True, **query
    ):
        """Find a single Port Pair Group

        :param str name_or_id: The name or ID of an SFC port pair group.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.sfc_port_pair_group.
            SfcPortPairGroup` or None
        """
        return self._find(
            _sfc_port_pair_group.SfcPortPairGroup,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_sfc_port_pair_group(self, port_pair_group):
        """Get a signle Port Pair Group

        :param port_pair_group:
            The value can be the ID of an SFC port pair group or a
            :class:`~openstack.network.v2.sfc_port_pair_group.SfcPortPairGroup`
            instance.

        :returns:
            :class:`~openstack.network.v2.sfc_port_pair_group.SfcPortPairGroup`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _sfc_port_pair_group.SfcPortPairGroup, port_pair_group
        )

    def update_sfc_port_pair_group(self, port_pair_group, **attrs):
        """Update a Port Pair Group

        :param port_pair_group: The value can be the ID of a Port Pair Group
            :class:`~openstack.network.v2.sfc_port_pair.SfcPortPairGroup`,
            instance.
        :param attrs: The attributes to update on the Port Pair Group

        :returns: The updated Port Pair Group.
        :rtype:
            :class:`~openstack.network.v2.sfc_port_pair_group.SfcPortPairGroup`
        """
        return self._update(
            _sfc_port_pair_group.SfcPortPairGroup, port_pair_group, **attrs
        )

    def sfc_port_pair_groups(self, **query):
        """Return a generator of Port Pair Groups

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``name``: The name of the port pair.
            * ``description``: The port pair description.

        :returns: A generator of SFC port pair group objects
        :rtype:
            :class:`~openstack.network.v2.sfc_port_pair_group.
            SfcPortPairGroup`
        """
        return self._list(_sfc_port_pair_group.SfcPortPairGroup, **query)

    def create_sfc_service_graph(self, **attrs):
        """Create a new Service Graph from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.sfc_service_graph.SfcServiceGraph`,
            comprised of the properties on the SfcServiceGraph class.

        :returns: The results of SFC Service Graph creation
        :rtype:
            :class:`~openstack.network.v2.sfc_service_graph.SfcServiceGraph`
        """
        return self._create(_sfc_sservice_graph.SfcServiceGraph, **attrs)

    def delete_sfc_service_graph(self, service_graph, ignore_missing=True):
        """Delete a Service Graph

        :param service_graph:
            The value can be either the ID of a service graph or a
            :class:`~openstack.network.v2.sfc_service_graph.SfcServiceGraph`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the service graph does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent service graph.

        :returns: ``None``
        """
        self._delete(
            _sfc_sservice_graph.SfcServiceGraph,
            service_graph,
            ignore_missing=ignore_missing,
        )

    def find_sfc_service_graph(self, name_or_id, ignore_missing=True, **query):
        """Find a single Service Graph

        :param str name_or_id: The name or ID of an SFC service graph.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict query: Any additional parameters to be passed into
            underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.sfc_service_graph.
            SfcServiceGraph` or None
        """
        return self._find(
            _sfc_sservice_graph.SfcServiceGraph,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_sfc_service_graph(self, service_graph):
        """Get a signle Service Graph

        :param service_graph:
            The value can be the ID of an SFC service graph or a
            :class:`~openstack.network.v2.sfc_service_graph.SfcServiceGraph`
            instance.

        :returns:
            :class:`~openstack.network.v2.sfc_service_graph.SfcServiceGraph`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_sfc_sservice_graph.SfcServiceGraph, service_graph)

    def update_sfc_service_graph(self, service_graph, **attrs):
        """Update a Service Graph

        :param service_graph: The value can be the ID of a Service Graph
            :class:`~openstack.network.v2.sfc_service_graph.SfcServiceGraph`,
            instance.
        :param attrs: The attributes to update on the Service Graph

        :returns: The updated Service Graph.
        :rtype:
            :class:`~openstack.network.v2.sfc_service_graph.SfcServiceGraph`
        """
        return self._update(
            _sfc_sservice_graph.SfcServiceGraph, service_graph, **attrs
        )

    def sfc_service_graphs(self, **query):
        """Return a generator of Service Graphs

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``name``: The name of the port pair.
            * ``description``: The port pair description.

        :returns: A generator of SFC service graph objects
        :rtype:
            :class:`~openstack.network.v2.sfc_service_graph.SfcServiceGraph`
        """
        return self._list(_sfc_sservice_graph.SfcServiceGraph, **query)

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: ty.Optional[list[str]] = None,
        interval: ty.Union[int, float, None] = 2,
        wait: ty.Optional[int] = None,
        attribute: str = 'status',
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :return: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int = 2,
        wait: int = 120,
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)

    def _get_cleanup_dependencies(self):
        return {'network': {'before': ['identity']}}

    def _service_cleanup(
        self,
        dry_run=True,
        client_status_queue=None,
        identified_resources=None,
        filters=None,
        resource_evaluation_fn=None,
        skip_resources=None,
    ):
        project_id = self.get_project_id()

        # check if the VPN service plugin is configured
        vpn_plugin = list(self.service_providers(service_type="VPN"))
        if vpn_plugin:
            if not self.should_skip_resource_cleanup(
                "vpn_ipsec_site_connection", skip_resources
            ):
                for obj in self.vpn_ipsec_site_connections():
                    self._service_cleanup_del_res(
                        self.delete_vpn_ipsec_site_connection,
                        obj,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=filters,
                        resource_evaluation_fn=resource_evaluation_fn,
                    )

            if not self.should_skip_resource_cleanup(
                "vpn_service", skip_resources
            ):
                for obj in self.vpn_services():
                    self._service_cleanup_del_res(
                        self.delete_vpn_service,
                        obj,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=filters,
                        resource_evaluation_fn=resource_evaluation_fn,
                    )

            if not self.should_skip_resource_cleanup(
                "vpn_endpoint_group", skip_resources
            ):
                for obj in self.vpn_endpoint_groups():
                    self._service_cleanup_del_res(
                        self.delete_vpn_endpoint_group,
                        obj,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=filters,
                        resource_evaluation_fn=resource_evaluation_fn,
                    )

            if not self.should_skip_resource_cleanup(
                "vpn_ike_policy", skip_resources
            ):
                for obj in self.vpn_ike_policies():
                    self._service_cleanup_del_res(
                        self.delete_vpn_ike_policy,
                        obj,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=filters,
                        resource_evaluation_fn=resource_evaluation_fn,
                    )

            if not self.should_skip_resource_cleanup(
                "vpn_ipsec_policy", skip_resources
            ):
                for obj in self.vpn_ipsec_policies():
                    self._service_cleanup_del_res(
                        self.delete_vpn_ipsec_policy,
                        obj,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=filters,
                        resource_evaluation_fn=resource_evaluation_fn,
                    )

        if not self.should_skip_resource_cleanup(
            "floating_ip", skip_resources
        ):
            # Delete floating_ips in the project if no filters defined OR all
            # filters are matching and port_id is empty
            for obj in self.ips(project_id=project_id):
                self._service_cleanup_del_res(
                    self.delete_ip,
                    obj,
                    dry_run=dry_run,
                    client_status_queue=client_status_queue,
                    identified_resources=identified_resources,
                    filters=filters,
                    resource_evaluation_fn=fip_cleanup_evaluation,
                )

        if not self.should_skip_resource_cleanup(
            "security_group", skip_resources
        ):
            # Delete (try to delete) all security groups in the project
            # Let's hope we can't drop SG in use
            for obj in self.security_groups(project_id=project_id):
                if obj.name != 'default':
                    self._service_cleanup_del_res(
                        self.delete_security_group,
                        obj,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=filters,
                        resource_evaluation_fn=resource_evaluation_fn,
                    )

        if not (
            self.should_skip_resource_cleanup("network", skip_resources)
            or self.should_skip_resource_cleanup("router", skip_resources)
            or self.should_skip_resource_cleanup("port", skip_resources)
            or self.should_skip_resource_cleanup("subnet", skip_resources)
        ):
            # Networks are crazy, try to delete router+net+subnet
            # if there are no "other" ports allocated on the net
            for net in self.networks(project_id=project_id):
                network_has_ports_allocated = False
                router_if = list()
                for port in self.ports(
                    project_id=project_id, network_id=net.id
                ):
                    self.log.debug(f'Looking at port {port}')
                    if port.device_owner in [
                        'network:router_interface',
                        'network:router_interface_distributed',
                        'network:ha_router_replicated_interface',
                    ]:
                        router_if.append(port)
                    elif port.device_owner == 'network:dhcp':
                        # we don't treat DHCP as a real port
                        continue
                    elif port.device_owner is None or port.device_owner == '':
                        # Nobody owns the port - go with it
                        continue
                    elif (
                        identified_resources
                        and port.device_id not in identified_resources
                    ):
                        # It seems some no other service identified this resource
                        # to be deleted. We can assume it doesn't count
                        network_has_ports_allocated = True
                if network_has_ports_allocated:
                    # If some ports are on net - we cannot delete it
                    continue
                self.log.debug(f'Network {net} should be deleted')
                # __Check__ if we need to drop network according to filters
                network_must_be_deleted = self._service_cleanup_del_res(
                    self.delete_network,
                    net,
                    dry_run=True,
                    client_status_queue=None,
                    identified_resources=None,
                    filters=filters,
                    resource_evaluation_fn=resource_evaluation_fn,
                )
                if not network_must_be_deleted:
                    # If not - check another net
                    continue
                # otherwise disconnect router, drop net, subnet, router
                # Disconnect
                for port in router_if:
                    if client_status_queue:
                        client_status_queue.put(port)

                    router = self.get_router(port.device_id)
                    if not dry_run:
                        # Router interfaces cannot be deleted when the router has
                        # static routes, so remove those first
                        if len(router.routes) > 0:
                            try:
                                self.remove_extra_routes_from_router(
                                    router,
                                    {"router": {"routes": router.routes}},
                                )
                            except exceptions.SDKException:
                                self.log.error(
                                    f"Cannot delete routes {router.routes} from router {router}"
                                )

                        try:
                            self.remove_interface_from_router(
                                router=port.device_id, port_id=port.id
                            )
                        except exceptions.SDKException:
                            self.log.error(f'Cannot delete object {obj}')
                    # router disconnected, drop it
                    self._service_cleanup_del_res(
                        self.delete_router,
                        router,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=None,
                        resource_evaluation_fn=None,
                    )
                # Drop ports not belonging to anybody
                for port in self.ports(
                    project_id=project_id, network_id=net.id
                ):
                    if port.device_owner is None or port.device_owner == '':
                        self._service_cleanup_del_res(
                            self.delete_port,
                            port,
                            dry_run=dry_run,
                            client_status_queue=client_status_queue,
                            identified_resources=identified_resources,
                            filters=None,
                            resource_evaluation_fn=None,
                        )

                # Drop all subnets in the net (no further conditions)
                for obj in self.subnets(
                    project_id=project_id, network_id=net.id
                ):
                    self._service_cleanup_del_res(
                        self.delete_subnet,
                        obj,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=None,
                        resource_evaluation_fn=None,
                    )

                # And now the network itself (we are here definitely only if we
                # need that)
                self._service_cleanup_del_res(
                    self.delete_network,
                    net,
                    dry_run=dry_run,
                    client_status_queue=client_status_queue,
                    identified_resources=identified_resources,
                    filters=None,
                    resource_evaluation_fn=None,
                )
        else:
            self.log.debug(
                "Skipping cleanup of networks, routers, ports and subnets "
                "as those resources require all of them to be cleaned up"
                "together, but at least one should be kept"
            )

        if not self.should_skip_resource_cleanup("router", skip_resources):
            # It might happen, that we have routers not attached to anything
            for obj in self.routers():
                ports = list(self.ports(device_id=obj.id))
                if len(ports) == 0:
                    self._service_cleanup_del_res(
                        self.delete_router,
                        obj,
                        dry_run=dry_run,
                        client_status_queue=client_status_queue,
                        identified_resources=identified_resources,
                        filters=None,
                        resource_evaluation_fn=None,
                    )


def fip_cleanup_evaluation(obj, identified_resources=None, filters=None):
    """Determine whether Floating IP should be deleted

    :param Resource obj: Floating IP object
    :param dict identified_resources: Optional dictionary with resources
        identified by other services for deletion.
    :param dict filters: dictionary with parameters
    """
    if filters is not None and (
        obj.port_id is not None
        and identified_resources
        and obj.port_id not in identified_resources
    ):
        # If filters are set, but port is not empty and will not be empty -
        # skip
        return False
    else:
        return True
