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
from openstack.network.v2 import address_scope as _address_scope
from openstack.network.v2 import agent as _agent
from openstack.network.v2 import auto_allocated_topology as \
    _auto_allocated_topology
from openstack.network.v2 import availability_zone
from openstack.network.v2 import extension
from openstack.network.v2 import flavor as _flavor
from openstack.network.v2 import floating_ip as _floating_ip
from openstack.network.v2 import health_monitor as _health_monitor
from openstack.network.v2 import listener as _listener
from openstack.network.v2 import load_balancer as _load_balancer
from openstack.network.v2 import metering_label as _metering_label
from openstack.network.v2 import metering_label_rule as _metering_label_rule
from openstack.network.v2 import network as _network
from openstack.network.v2 import network_ip_availability
from openstack.network.v2 import pool as _pool
from openstack.network.v2 import pool_member as _pool_member
from openstack.network.v2 import port as _port
from openstack.network.v2 import qos_bandwidth_limit_rule as \
    _qos_bandwidth_limit_rule
from openstack.network.v2 import qos_dscp_marking_rule as \
    _qos_dscp_marking_rule
from openstack.network.v2 import qos_minimum_bandwidth_rule as \
    _qos_minimum_bandwidth_rule
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
from openstack.network.v2 import subnet as _subnet
from openstack.network.v2 import subnet_pool as _subnet_pool
from openstack.network.v2 import vpn_service as _vpn_service
from openstack import proxy
from openstack import utils


class Proxy(proxy.Proxy):

    def create_address_scope(self, **attrs):
        """Create a new address scope from attributes

        :param dict attrs: Keyword arguments which will be used to create
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the address scope does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent address scope.

        :returns: ``None``
        """
        self._delete(_address_scope.AddressScope, address_scope,
                     ignore_missing=ignore_missing)

    def find_address_scope(self, name_or_id, ignore_missing=True, **args):
        """Find a single address scope

        :param name_or_id: The name or ID of an address scope.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.address_scope.AddressScope`
                  or None
        """
        return self._find(_address_scope.AddressScope, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_address_scope(self, address_scope):
        """Get a single address scope

        :param address_scope: The value can be the ID of an address scope or a
            :class:`~openstack.network.v2.address_scope.AddressScope` instance.

        :returns: One :class:`~openstack.network.v2.address_scope.AddressScope`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_address_scope.AddressScope, paginated=False,
                          **query)

    def update_address_scope(self, address_scope, **attrs):
        """Update an address scope

        :param address_scope: Either the ID of an address scope or a
            :class:`~openstack.network.v2.address_scope.AddressScope` instance.
        :param dict attrs: The attributes to update on the address scope
                           represented by ``value``.

        :returns: The updated address scope
        :rtype: :class:`~openstack.network.v2.address_scope.AddressScope`
        """
        return self._update(_address_scope.AddressScope, address_scope,
                            **attrs)

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
        return self._list(_agent.Agent, paginated=False, **query)

    def delete_agent(self, agent, ignore_missing=True):
        """Delete a network agent

        :param agent: The value can be the ID of a agent or a
                     :class:`~openstack.network.v2.agent.Agent` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
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
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_agent.Agent, agent)

    def update_agent(self, agent, **attrs):
        """Update a network agent

        :param agent: The value can be the ID of a agent or a
                     :class:`~openstack.network.v2.agent.Agent` instance.
        :param dict attrs: The attributes to update on the agent represented
                           by ``value``.

        :returns: One :class:`~openstack.network.v2.agent.Agent`
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        """
        return self._update(_agent.Agent, agent, **attrs)

    def dhcp_agent_hosting_networks(self, agent, **query):
        """A generator of networks hosted by a DHCP agent.

        :param agent: Either the agent id of an instance of
                      :class:`~openstack.network.v2.network_agent.Agent`
        :param query: kwargs \*\*query: Optional query parameters to be sent
                                        to limit the resources being returned.
        :return: A generator of networks
        """
        agent_obj = self._get_resource(_agent.Agent, agent)
        return self._list(_network.DHCPAgentHostingNetwork, paginated=False,
                          agent_id=agent_obj.id, **query)

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
        return self._list(_agent.NetworkHostingDHCPAgent, paginated=False,
                          network_id=net.id, **query)

    def get_auto_allocated_topology(self, project=None):
        """Get the auto-allocated topology of a given tenant

        :param project:
               The value is the ID or name of a project

        :returns: The auto-allocated topology
        :rtype: :class:`~openstack.network.v2.\
                auto_allocated_topology.AutoAllocatedTopology`
        """

        # If project option is not given, grab project id from session
        if project is None:
            project = self.get_project_id()
        return self._get(_auto_allocated_topology.AutoAllocatedTopology,
                         project)

    def delete_auto_allocated_topology(self, project=None,
                                       ignore_missing=False):
        """Delete auto-allocated topology

        :param project:
            The value is the ID or name of a project
        :param ignore_missing: When set to ``False``
               :class:`~openstack.exceptions.ResourceNotFound` will be
               raised when the topology does not exist.
               When set to ``True``, no exception will be raised when
               attempting to delete nonexistant topology

        :returns: ``None``
        """

        # If project option is not given, grab project id from session
        if project is None:
            project = self.get_project_id()
        self._delete(_auto_allocated_topology.AutoAllocatedTopology,
                     project, ignore_missing=ignore_missing)

    def validate_auto_allocated_topology(self, project=None):
        """Validate the resources for auto allocation

        :param project:
               The value is the ID or name of a project

        :returns: Whether all resources are correctly configured or not
        :rtype: :class:`~openstack.network.v2.\
                auto_allocated_topology.ValidateTopology`
        """

        # If project option is not given, grab project id from session
        if project is None:
            project = self.get_project_id()
        return self._get(_auto_allocated_topology.ValidateTopology,
                         project=project, requires_id=False)

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
        return self._list(availability_zone.AvailabilityZone, paginated=False)

    def find_extension(self, name_or_id, ignore_missing=True, **args):
        """Find a single extension

        :param name_or_id: The name or ID of a extension.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.extension.Extension`
                  or None
        """
        return self._find(extension.Extension, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def extensions(self, **query):
        """Return a generator of extensions

        :param dict query: Optional query parameters to be sent to limit
                           the resources being returned. Currently no
                           parameter is supported.

        :returns: A generator of extension objects
        :rtype: :class:`~openstack.network.v2.extension.Extension`
        """
        return self._list(extension.Extension, paginated=False, **query)

    def create_flavor(self, **attrs):
        """Create a new network service flavor from attributes

        :param dict attrs: Keyword arguments which will be used to create
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the flavor does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent flavor.

        :returns: ``None``
        """
        self._delete(_flavor.Flavor, flavor, ignore_missing=ignore_missing)

    def find_flavor(self, name_or_id, ignore_missing=True, **args):
        """Find a single network service flavor

        :param name_or_id: The name or ID of a flavor.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.flavor.Flavor` or None
        """
        return self._find(_flavor.Flavor, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_flavor(self, flavor):
        """Get a single network service flavor

        :param flavor:
            The value can be the ID of a flavor or a
            :class:`~openstack.network.v2.flavor.Flavor` instance.

        :returns: One :class:`~openstack.network.v2.flavor.Flavor`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_flavor.Flavor, flavor)

    def update_flavor(self, flavor, **attrs):
        """Update a network service flavor

        :param flavor:
            Either the id of a flavor or a
            :class:`~openstack.network.v2.flavor.Flavor` instance.
        :attrs kwargs: The attributes to update on the flavor represented
                       by ``value``.

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
        return self._list(_flavor.Flavor, paginated=True, **query)

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
            _service_profile.ServiceProfile, service_profile)
        return flavor.associate_flavor_with_service_profile(
            self, service_profile.id)

    def disassociate_flavor_from_service_profile(
            self, flavor, service_profile):
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
            _service_profile.ServiceProfile, service_profile)
        return flavor.disassociate_flavor_from_service_profile(
            self, service_profile.id)

    def create_ip(self, **attrs):
        """Create a new floating ip from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.floating_ip.FloatingIP`,
            comprised of the properties on the FloatingIP class.

        :returns: The results of floating ip creation
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._create(_floating_ip.FloatingIP, **attrs)

    def delete_ip(self, floating_ip, ignore_missing=True):
        """Delete a floating ip

        :param floating_ip: The value can be either the ID of a floating ip
                    or a :class:`~openstack.network.v2.floating_ip.FloatingIP`
                    instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the floating ip does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent ip.

        :returns: ``None``
        """
        self._delete(_floating_ip.FloatingIP, floating_ip,
                     ignore_missing=ignore_missing)

    def find_available_ip(self):
        """Find an available IP

        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
                  or None
        """
        return _floating_ip.FloatingIP.find_available(self)

    def find_ip(self, name_or_id, ignore_missing=True, **args):
        """Find a single IP

        :param name_or_id: The name or ID of an IP.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
                  or None
        """
        return self._find(_floating_ip.FloatingIP, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_ip(self, floating_ip):
        """Get a single floating ip

        :param floating_ip: The value can be the ID of a floating ip or a
                      :class:`~openstack.network.v2.floating_ip.FloatingIP`
                      instance.

        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_floating_ip.FloatingIP, paginated=False, **query)

    def update_ip(self, floating_ip, **attrs):
        """Update a ip

        :param floating_ip: Either the id of a ip or a
                      :class:`~openstack.network.v2.floating_ip.FloatingIP`
                      instance.
        :param dict attrs: The attributes to update on the ip represented
                           by ``value``.

        :returns: The updated ip
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._update(_floating_ip.FloatingIP, floating_ip, **attrs)

    def create_health_monitor(self, **attrs):
        """Create a new health monitor from attributes

        :param dict attrs: Keyword arguments which will be used to create
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the health monitor does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent health monitor.

        :returns: ``None``
        """
        self._delete(_health_monitor.HealthMonitor, health_monitor,
                     ignore_missing=ignore_missing)

    def find_health_monitor(self, name_or_id, ignore_missing=True, **args):
        """Find a single health monitor

        :param name_or_id: The name or ID of a health monitor.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.health_monitor.
                  HealthMonitor` or None
        """
        return self._find(_health_monitor.HealthMonitor,
                          name_or_id, ignore_missing=ignore_missing, **args)

    def get_health_monitor(self, health_monitor):
        """Get a single health monitor

        :param health_monitor: The value can be the ID of a health monitor or a
               :class:`~openstack.network.v2.health_monitor.HealthMonitor`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_health_monitor.HealthMonitor, paginated=False,
                          **query)

    def update_health_monitor(self, health_monitor, **attrs):
        """Update a health monitor

        :param health_monitor: Either the id of a health monitor or a
                      :class:`~openstack.network.v2.health_monitor.
                      HealthMonitor` instance.
        :param dict attrs: The attributes to update on the health monitor
                       represented by ``value``.

        :returns: The updated health monitor
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._update(_health_monitor.HealthMonitor, health_monitor,
                            **attrs)

    def create_listener(self, **attrs):
        """Create a new listener from attributes

        :param dict attrs: Keyword arguments which will be used to create
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the listner does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent listener.

        :returns: ``None``
        """
        self._delete(_listener.Listener, listener,
                     ignore_missing=ignore_missing)

    def find_listener(self, name_or_id, ignore_missing=True, **args):
        """Find a single listener

        :param name_or_id: The name or ID of a listener.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.listener.Listener` or None
        """
        return self._find(_listener.Listener, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_listener(self, listener):
        """Get a single listener

        :param listener: The value can be the ID of a listener or a
               :class:`~openstack.network.v2.listener.Listener`
               instance.

        :returns: One :class:`~openstack.network.v2.listener.Listener`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_listener.Listener, paginated=False, **query)

    def update_listener(self, listener, **attrs):
        """Update a listener

        :param listener: Either the id of a listener or a
                      :class:`~openstack.network.v2.listener.Listener`
                      instance.
        :param dict attrs: The attributes to update on the listener
                           represented by ``listener``.

        :returns: The updated listener
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._update(_listener.Listener, listener, **attrs)

    def create_load_balancer(self, **attrs):
        """Create a new load balancer from attributes

        :param dict attrs: Keyword arguments which will be used to create
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the load balancer does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent load balancer.

        :returns: ``None``
        """
        self._delete(_load_balancer.LoadBalancer, load_balancer,
                     ignore_missing=ignore_missing)

    def find_load_balancer(self, name_or_id, ignore_missing=True, **args):
        """Find a single load balancer

        :param name_or_id: The name or ID of a load balancer.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.load_balancer.LoadBalancer`
                  or None
        """
        return self._find(_load_balancer.LoadBalancer, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_load_balancer(self, load_balancer):
        """Get a single load balancer

        :param load_balancer: The value can be the ID of a load balancer or a
               :class:`~openstack.network.v2.load_balancer.LoadBalancer`
               instance.

        :returns: One :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_load_balancer.LoadBalancer, paginated=False,
                          **query)

    def update_load_balancer(self, load_balancer, **attrs):
        """Update a load balancer

        :param load_balancer: Either the id of a load balancer or a
                      :class:`~openstack.network.v2.load_balancer.LoadBalancer`
                      instance.
        :param dict attrs: The attributes to update on the load balancer
                           represented by ``load_balancer``.

        :returns: The updated load balancer
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._update(_load_balancer.LoadBalancer, load_balancer,
                            **attrs)

    def create_metering_label(self, **attrs):
        """Create a new metering label from attributes

        :param dict attrs: Keyword arguments which will be used to create
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the metering label does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent metering label.

        :returns: ``None``
        """
        self._delete(_metering_label.MeteringLabel, metering_label,
                     ignore_missing=ignore_missing)

    def find_metering_label(self, name_or_id, ignore_missing=True, **args):
        """Find a single metering label

        :param name_or_id: The name or ID of a metering label.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.metering_label.
                  MeteringLabel` or None
        """
        return self._find(_metering_label.MeteringLabel, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_metering_label(self, metering_label):
        """Get a single metering label

        :param metering_label: The value can be the ID of a metering label or a
               :class:`~openstack.network.v2.metering_label.MeteringLabel`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.metering_label.MeteringLabel`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_metering_label.MeteringLabel, paginated=False,
                          **query)

    def update_metering_label(self, metering_label, **attrs):
        """Update a metering label

        :param metering_label: Either the id of a metering label or a
                      :class:`~openstack.network.v2.metering_label.
                      MeteringLabel` instance.
        :param dict attrs: The attributes to update on the metering label
                           represented by ``metering_label``.

        :returns: The updated metering label
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._update(_metering_label.MeteringLabel, metering_label,
                            **attrs)

    def create_metering_label_rule(self, **attrs):
        """Create a new metering label rule from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule`, comprised of the properties on
            the MeteringLabelRule class.

        :returns: The results of metering label rule creation
        :rtype: :class:`~openstack.network.v2.metering_label_rule.\
                MeteringLabelRule`
        """
        return self._create(_metering_label_rule.MeteringLabelRule, **attrs)

    def delete_metering_label_rule(self, metering_label_rule,
                                   ignore_missing=True):
        """Delete a metering label rule

        :param metering_label_rule:
            The value can be either the ID of a metering label rule
            or a :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the metering label rule does not exist.  When set to ``True``,
            no exception will be set when attempting to delete a nonexistent
            metering label rule.

        :returns: ``None``
        """
        self._delete(_metering_label_rule.MeteringLabelRule,
                     metering_label_rule, ignore_missing=ignore_missing)

    def find_metering_label_rule(self, name_or_id, ignore_missing=True,
                                 **args):
        """Find a single metering label rule

        :param name_or_id: The name or ID of a metering label rule.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.metering_label_rule.
                  MeteringLabelRule` or None
        """
        return self._find(_metering_label_rule.MeteringLabelRule, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_metering_label_rule(self, metering_label_rule):
        """Get a single metering label rule

        :param metering_label_rule:
            The value can be the ID of a metering label rule or a
            :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule` instance.

        :returns: One
            :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_metering_label_rule.MeteringLabelRule,
                         metering_label_rule)

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
        :rtype: :class:`~openstack.network.v2.metering_label_rule.
                MeteringLabelRule`
        """
        return self._list(_metering_label_rule.MeteringLabelRule,
                          paginated=False, **query)

    def update_metering_label_rule(self, metering_label_rule, **attrs):
        """Update a metering label rule

        :param metering_label_rule:
                      Either the id of a metering label rule or a
                      :class:`~openstack.network.v2.metering_label_rule.
                      MeteringLabelRule` instance.
        :param dict attrs: The attributes to update on the metering label rule
                           represented by ``metering_label_rule``.

        :returns: The updated metering label rule
        :rtype: :class:`~openstack.network.v2.metering_label_rule.
                       MeteringLabelRule`
        """
        return self._update(_metering_label_rule.MeteringLabelRule,
                            metering_label_rule, **attrs)

    def create_network(self, **attrs):
        """Create a new network from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.network.Network`,
                           comprised of the properties on the Network class.

        :returns: The results of network creation
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._create(_network.Network, **attrs)

    def delete_network(self, network, ignore_missing=True):
        """Delete a network

        :param network:
            The value can be either the ID of a network or a
            :class:`~openstack.network.v2.network.Network` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the network does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent network.

        :returns: ``None``
        """
        self._delete(_network.Network, network, ignore_missing=ignore_missing)

    def find_network(self, name_or_id, ignore_missing=True, **args):
        """Find a single network

        :param name_or_id: The name or ID of a network.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.network.Network` or None
        """
        return self._find(_network.Network, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_network(self, network):
        """Get a single network

        :param network:
            The value can be the ID of a network or a
            :class:`~openstack.network.v2.network.Network` instance.

        :returns: One :class:`~openstack.network.v2.network.Network`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_network.Network, network)

    def networks(self, **query):
        """Return a generator of networks

        :param kwargs \*\*query: Optional query parameters to be sent to limit
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
        return self._list(_network.Network, paginated=False, **query)

    def update_network(self, network, **attrs):
        """Update a network

        :param network: Either the id of a network or an instance of type
                        :class:`~openstack.network.v2.network.Network`.
        :param dict attrs: The attributes to update on the network represented
                           by ``network``.

        :returns: The updated network
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._update(_network.Network, network, **attrs)

    def find_network_ip_availability(self, name_or_id, ignore_missing=True,
                                     **args):
        """Find IP availability of a network

        :param name_or_id: The name or ID of a network.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.network_ip_availability.
                       NetworkIPAvailability` or None
        """
        return self._find(network_ip_availability.NetworkIPAvailability,
                          name_or_id, ignore_missing=ignore_missing, **args)

    def get_network_ip_availability(self, network):
        """Get IP availability of a network

        :param network:
            The value can be the ID of a network or a
            :class:`~openstack.network.v2.network.Network` instance.

        :returns: One :class:`~openstack.network.v2.network_ip_availability.
                      NetworkIPAvailability`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(network_ip_availability.NetworkIPAvailability,
                         network)

    def network_ip_availabilities(self, **query):
        """Return a generator of network ip availabilities

        :param kwargs \*\*query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * ``ip_version``: IP version of the network
            * ``network_id``: ID of network to use when listening network IP
                availability.
            * ``network_name``: The name of the network for the particular
                network IP availability.
            * ``project_id``: Owner tenant ID

        :returns: A generator of network ip availability objects
        :rtype: :class:`~openstack.network.v2.network_ip_availability.
                NetworkIPAvailability`
        """
        return self._list(network_ip_availability.NetworkIPAvailability,
                          paginated=False, **query)

    def create_pool(self, **attrs):
        """Create a new pool from attributes

        :param dict attrs: Keyword arguments which will be used to create
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the pool does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent pool.

        :returns: ``None``
        """
        self._delete(_pool.Pool, pool, ignore_missing=ignore_missing)

    def find_pool(self, name_or_id, ignore_missing=True, **args):
        """Find a single pool

        :param name_or_id: The name or ID of a pool.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.pool.Pool` or None
        """
        return self._find(_pool.Pool, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_pool(self, pool):
        """Get a single pool

        :param pool: The value can be the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance.

        :returns: One :class:`~openstack.network.v2.pool.Pool`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_pool.Pool, paginated=False, **query)

    def update_pool(self, pool, **attrs):
        """Update a pool

        :param pool: Either the id of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance.
        :param dict attrs: The attributes to update on the pool represented
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
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.pool_member.PoolMember`,
            comprised of the properties on the PoolMember class.

        :returns: The results of pool member creation
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._create(_pool_member.PoolMember, pool_id=poolobj.id,
                            **attrs)

    def delete_pool_member(self, pool_member, pool, ignore_missing=True):
        """Delete a pool member

        :param pool_member:
            The member can be either the ID of a pool member or a
            :class:`~openstack.network.v2.pool_member.PoolMember` instance.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the pool member does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent pool member.

        :returns: ``None``
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        self._delete(_pool_member.PoolMember, pool_member,
                     ignore_missing=ignore_missing, pool_id=poolobj.id)

    def find_pool_member(self, name_or_id, pool, ignore_missing=True, **args):
        """Find a single pool member

        :param str name_or_id: The name or ID of a pool member.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.pool_member.PoolMember`
                  or None
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._find(_pool_member.PoolMember, name_or_id,
                          ignore_missing=ignore_missing, pool_id=poolobj.id,
                          **args)

    def get_pool_member(self, pool_member, pool):
        """Get a single pool member

        :param pool_member: The member can be the ID of a pool member or a
                       :class:`~openstack.network.v2.pool_member.PoolMember`
                       instance.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member belongs to.

        :returns: One :class:`~openstack.network.v2.pool_member.PoolMember`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._get(_pool_member.PoolMember, pool_member,
                         pool_id=poolobj.id)

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
        return self._list(_pool_member.PoolMember, paginated=False,
                          pool_id=poolobj.id, **query)

    def update_pool_member(self, pool_member, pool, **attrs):
        """Update a pool member

        :param pool_member: Either the ID of a pool member or a
                       :class:`~openstack.network.v2.pool_member.PoolMember`
                       instance.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member belongs to.
        :param dict attrs: The attributes to update on the pool member
                           represented by ``pool_member``.

        :returns: The updated pool member
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._update(_pool_member.PoolMember, pool_member,
                            pool_id=poolobj.id, **attrs)

    def create_port(self, **attrs):
        """Create a new port from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.port.Port`,
                           comprised of the properties on the Port class.

        :returns: The results of port creation
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._create(_port.Port, **attrs)

    def delete_port(self, port, ignore_missing=True):
        """Delete a port

        :param port: The value can be either the ID of a port or a
                     :class:`~openstack.network.v2.port.Port` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the port does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent port.

        :returns: ``None``
        """
        self._delete(_port.Port, port, ignore_missing=ignore_missing)

    def find_port(self, name_or_id, ignore_missing=True, **args):
        """Find a single port

        :param name_or_id: The name or ID of a port.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.port.Port` or None
        """
        return self._find(_port.Port, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_port(self, port):
        """Get a single port

        :param port: The value can be the ID of a port or a
                     :class:`~openstack.network.v2.port.Port` instance.

        :returns: One :class:`~openstack.network.v2.port.Port`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_port.Port, port)

    def ports(self, **query):
        """Return a generator of ports

        :param kwargs \*\*query: Optional query parameters to be sent to limit
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
        return self._list(_port.Port, paginated=False, **query)

    def update_port(self, port, **attrs):
        """Update a port

        :param port: Either the id of a port or a
                     :class:`~openstack.network.v2.port.Port` instance.
        :param dict attrs: The attributes to update on the port represented
                           by ``port``.

        :returns: The updated port
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._update(_port.Port, port, **attrs)

    def add_ip_to_port(self, port, ip):
        ip['port_id'] = port.id
        return ip.update(self)

    def remove_ip_from_port(self, ip):
        ip['port_id'] = None
        return ip.update(self)

    def get_subnet_ports(self, subnet_id):
        result = []
        ports = self.ports()
        for puerta in ports:
            for fixed_ip in puerta.fixed_ips:
                if fixed_ip['subnet_id'] == subnet_id:
                    result.append(puerta)
        return result

    def create_qos_bandwidth_limit_rule(self, qos_policy, **attrs):
        """Create a new bandwidth limit rule

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.
                           qos_bandwidth_limit_rule.QoSBandwidthLimitRule`,
                           comprised of the properties on the
                           QoSBandwidthLimitRule class.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.

        :returns: The results of resource creation
        :rtype: :class:`~openstack.network.v2.qos_bandwidth_limit_rule.
                    QoSBandwidthLimitRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._create(_qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
                            qos_policy_id=policy.id, **attrs)

    def delete_qos_bandwidth_limit_rule(self, qos_rule, qos_policy,
                                        ignore_missing=True):
        """Delete a bandwidth limit rule

        :param qos_rule: The value can be either the ID of a bandwidth limit
                         rule or a :class:`~openstack.network.v2.
                         qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
                         instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent bandwidth limit rule.

        :returns: ``None``
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        self._delete(_qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
                     qos_rule, ignore_missing=ignore_missing,
                     qos_policy_id=policy.id)

    def find_qos_bandwidth_limit_rule(self, qos_rule_id, qos_policy,
                                      ignore_missing=True, **args):
        """Find a bandwidth limit rule

        :param qos_rule_id: The ID of a bandwidth limit rule.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.qos_bandwidth_limit_rule.
                    QoSBandwidthLimitRule` or None
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._find(_qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
                          qos_rule_id, ignore_missing=ignore_missing,
                          qos_policy_id=policy.id, **args)

    def get_qos_bandwidth_limit_rule(self, qos_rule, qos_policy):
        """Get a single bandwidth limit rule

        :param qos_rule: The value can be the ID of a minimum bandwidth rule or
                         a :class:`~openstack.network.v2.
                         qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
                         instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :returns: One :class:`~openstack.network.v2.qos_bandwidth_limit_rule.
                       QoSBandwidthLimitRule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                       when no resource can be found.
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._get(_qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
                         qos_rule, qos_policy_id=policy.id)

    def qos_bandwidth_limit_rules(self, qos_policy, **query):
        """Return a generator of bandwidth limit rules

        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.
        :returns: A generator of bandwidth limit rule objects
        :rtype: :class:`~openstack.network.v2.qos_bandwidth_limit_rule.
                       QoSBandwidthLimitRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._list(_qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
                          paginated=False, qos_policy_id=policy.id, **query)

    def update_qos_bandwidth_limit_rule(self, qos_rule, qos_policy,
                                        **attrs):
        """Update a bandwidth limit rule

        :param qos_rule: Either the id of a bandwidth limit rule or a
                         :class:`~openstack.network.v2.
                         qos_bandwidth_limit_rule.QoSBandwidthLimitRule`
                         instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :attrs kwargs: The attributes to update on the bandwidth limit rule
                       represented by ``value``.

        :returns: The updated minimum bandwidth rule
        :rtype: :class:`~openstack.network.v2.qos_bandwidth_limit_rule.
                       QoSBandwidthLimitRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._update(_qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
                            qos_rule, qos_policy_id=policy.id, **attrs)

    def create_qos_dscp_marking_rule(self, qos_policy, **attrs):
        """Create a new QoS DSCP marking rule

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.
                           qos_dscp_marking_rule.QoSDSCPMarkingRule`,
                           comprised of the properties on the
                           QosDscpMarkingRule class.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.

        :returns: The results of router creation
        :rtype: :class:`~openstack.network.v2.qos_dscp_marking_rule.
                    QoSDSCPMarkingRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._create(_qos_dscp_marking_rule.QoSDSCPMarkingRule,
                            qos_policy_id=policy.id, **attrs)

    def delete_qos_dscp_marking_rule(self, qos_rule, qos_policy,
                                     ignore_missing=True):
        """Delete a QoS DSCP marking rule

        :param qos_rule: The value can be either the ID of a minimum bandwidth
                         rule or a :class:`~openstack.network.v2.
                         qos_dscp_marking_rule.QoSDSCPMarkingRule`
                         instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent minimum bandwidth rule.

        :returns: ``None``
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        self._delete(_qos_dscp_marking_rule.QoSDSCPMarkingRule,
                     qos_rule, ignore_missing=ignore_missing,
                     qos_policy_id=policy.id)

    def find_qos_dscp_marking_rule(self, qos_rule_id, qos_policy,
                                   ignore_missing=True, **args):
        """Find a QoS DSCP marking rule

        :param qos_rule_id: The ID of a QoS DSCP marking rule.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.qos_dscp_marking_rule.
                    QoSDSCPMarkingRule` or None
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._find(_qos_dscp_marking_rule.QoSDSCPMarkingRule,
                          qos_rule_id, ignore_missing=ignore_missing,
                          qos_policy_id=policy.id, **args)

    def get_qos_dscp_marking_rule(self, qos_rule, qos_policy):
        """Get a single QoS DSCP marking rule

        :param qos_rule: The value can be the ID of a minimum bandwidth rule or
                         a :class:`~openstack.network.v2.qos_dscp_marking_rule.
                         QoSDSCPMarkingRule` instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :returns: One :class:`~openstack.network.v2.qos_dscp_marking_rule.
                       QoSDSCPMarkingRule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                       when no resource can be found.
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._get(_qos_dscp_marking_rule.QoSDSCPMarkingRule,
                         qos_rule, qos_policy_id=policy.id)

    def qos_dscp_marking_rules(self, qos_policy, **query):
        """Return a generator of QoS DSCP marking rules

        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.
        :returns: A generator of QoS DSCP marking rule objects
        :rtype: :class:`~openstack.network.v2.qos_dscp_marking_rule.
                       QoSDSCPMarkingRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._list(_qos_dscp_marking_rule.QoSDSCPMarkingRule,
                          paginated=False, qos_policy_id=policy.id, **query)

    def update_qos_dscp_marking_rule(self, qos_rule, qos_policy, **attrs):
        """Update a QoS DSCP marking rule

        :param qos_rule: Either the id of a minimum bandwidth rule or a
                         :class:`~openstack.network.v2.qos_dscp_marking_rule.
                         QoSDSCPMarkingRule` instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :attrs kwargs: The attributes to update on the QoS DSCP marking rule
                       represented by ``value``.

        :returns: The updated QoS DSCP marking rule
        :rtype: :class:`~openstack.network.v2.qos_dscp_marking_rule.
                       QoSDSCPMarkingRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._update(_qos_dscp_marking_rule.QoSDSCPMarkingRule,
                            qos_rule, qos_policy_id=policy.id, **attrs)

    def create_qos_minimum_bandwidth_rule(self, qos_policy, **attrs):
        """Create a new minimum bandwidth rule

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.
                           qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`,
                           comprised of the properties on the
                           QoSMinimumBandwidthRule class.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.

        :returns: The results of resource creation
        :rtype: :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.
                    QoSMinimumBandwidthRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._create(
            _qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            qos_policy_id=policy.id, **attrs)

    def delete_qos_minimum_bandwidth_rule(self, qos_rule, qos_policy,
                                          ignore_missing=True):
        """Delete a minimum bandwidth rule

        :param qos_rule: The value can be either the ID of a minimum bandwidth
                         rule or a :class:`~openstack.network.v2.
                         qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
                         instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent minimum bandwidth rule.

        :returns: ``None``
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        self._delete(_qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
                     qos_rule, ignore_missing=ignore_missing,
                     qos_policy_id=policy.id)

    def find_qos_minimum_bandwidth_rule(self, qos_rule_id, qos_policy,
                                        ignore_missing=True, **args):
        """Find a minimum bandwidth rule

        :param qos_rule_id: The ID of a minimum bandwidth rule.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.
                    QoSMinimumBandwidthRule` or None
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._find(_qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
                          qos_rule_id, ignore_missing=ignore_missing,
                          qos_policy_id=policy.id, **args)

    def get_qos_minimum_bandwidth_rule(self, qos_rule, qos_policy):
        """Get a single minimum bandwidth rule

        :param qos_rule: The value can be the ID of a minimum bandwidth rule or
                         a :class:`~openstack.network.v2.
                         qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
                         instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :returns: One :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.
                       QoSMinimumBandwidthRule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                       when no resource can be found.
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._get(_qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
                         qos_rule, qos_policy_id=policy.id)

    def qos_minimum_bandwidth_rules(self, qos_policy, **query):
        """Return a generator of minimum bandwidth rules

        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.
        :returns: A generator of minimum bandwidth rule objects
        :rtype: :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.
                       QoSMinimumBandwidthRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._list(_qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
                          paginated=False, qos_policy_id=policy.id, **query)

    def update_qos_minimum_bandwidth_rule(self, qos_rule, qos_policy,
                                          **attrs):
        """Update a minimum bandwidth rule

        :param qos_rule: Either the id of a minimum bandwidth rule or a
                         :class:`~openstack.network.v2.
                         qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule`
                         instance.
        :param qos_policy: The value can be the ID of the QoS policy that the
                           rule belongs or a :class:`~openstack.network.v2.
                           qos_policy.QoSPolicy` instance.
        :attrs kwargs: The attributes to update on the minimum bandwidth rule
                       represented by ``value``.

        :returns: The updated minimum bandwidth rule
        :rtype: :class:`~openstack.network.v2.qos_minimum_bandwidth_rule.
                       QoSMinimumBandwidthRule`
        """
        policy = self._get_resource(_qos_policy.QoSPolicy, qos_policy)
        return self._update(_qos_minimum_bandwidth_rule.
                            QoSMinimumBandwidthRule, qos_rule,
                            qos_policy_id=policy.id, **attrs)

    def create_qos_policy(self, **attrs):
        """Create a new QoS policy from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.qos_policy.
                           QoSPolicy`, comprised of the properties on the
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the QoS policy does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent QoS policy.

        :returns: ``None``
        """
        self._delete(_qos_policy.QoSPolicy, qos_policy,
                     ignore_missing=ignore_missing)

    def find_qos_policy(self, name_or_id, ignore_missing=True, **args):
        """Find a single QoS policy

        :param name_or_id: The name or ID of a QoS policy.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.qos_policy.QoSPolicy` or
                  None
        """
        return self._find(_qos_policy.QoSPolicy, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_qos_policy(self, qos_policy):
        """Get a single QoS policy

        :param qos_policy: The value can be the ID of a QoS policy or a
                           :class:`~openstack.network.v2.qos_policy.QoSPolicy`
                           instance.

        :returns: One :class:`~openstack.network.v2.qos_policy.QoSPolicy`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_qos_policy.QoSPolicy, paginated=False, **query)

    def update_qos_policy(self, qos_policy, **attrs):
        """Update a QoS policy

        :param qos_policy: Either the id of a QoS policy or a
                           :class:`~openstack.network.v2.qos_policy.QoSPolicy`
                           instance.
        :attrs kwargs: The attributes to update on the QoS policy represented
                       by ``value``.

        :returns: The updated QoS policy
        :rtype: :class:`~openstack.network.v2.qos_policy.QoSPolicy`
        """
        return self._update(_qos_policy.QoSPolicy, qos_policy, **attrs)

    def find_qos_rule_type(self, rule_type_name, ignore_missing=True):
        """Find a single QoS rule type details

        :param rule_type_name: The name of a QoS rule type.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.qos_rule_type.QoSRuleType`
                  or None
        """
        return self._find(_qos_rule_type.QoSRuleType, rule_type_name,
                          ignore_missing=ignore_missing)

    def get_qos_rule_type(self, qos_rule_type):
        """Get details about single QoS rule type

        :param qos_rule_type: The value can be the name of a QoS policy
                              rule type or a
                              :class:`~openstack.network.v2.
                              qos_rule_type.QoSRuleType`
                              instance.

        :returns: One :class:`~openstack.network.v2.qos_rule_type.QoSRuleType`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_qos_rule_type.QoSRuleType, paginated=False, **query)

    def delete_quota(self, quota, ignore_missing=True):
        """Delete a quota (i.e. reset to the default quota)

        :param quota: The value can be either the ID of a quota or a
                      :class:`~openstack.network.v2.quota.Quota` instance.
                      The ID of a quota is the same as the project ID
                      for the quota.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
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
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        if details:
            quota_obj = self._get_resource(_quota.Quota, quota)
            quota = self._get(_quota.QuotaDetails, project=quota_obj.id,
                              requires_id=False)
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
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        quota_obj = self._get_resource(_quota.Quota, quota)
        return self._get(_quota.QuotaDefault, project=quota_obj.id,
                         requires_id=False)

    def quotas(self, **query):
        """Return a generator of quotas

        :param dict query: Optional query parameters to be sent to limit
                           the resources being returned. Currently no query
                           parameter is supported.

        :returns: A generator of quota objects
        :rtype: :class:`~openstack.network.v2.quota.Quota`
        """
        return self._list(_quota.Quota, paginated=False, **query)

    def update_quota(self, quota, **attrs):
        """Update a quota

        :param quota: Either the ID of a quota or a
                      :class:`~openstack.network.v2.quota.Quota` instance.
                      The ID of a quota is the same as the project ID
                      for the quota.
        :param dict attrs: The attributes to update on the quota represented
                           by ``quota``.

        :returns: The updated quota
        :rtype: :class:`~openstack.network.v2.quota.Quota`
        """
        return self._update(_quota.Quota, quota, **attrs)

    def create_rbac_policy(self, **attrs):
        """Create a new RBAC policy from attributes

        :param dict attrs: Keyword arguments which will be used to create a
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
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the RBAC policy does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent RBAC policy.

        :returns: ``None``
        """
        self._delete(_rbac_policy.RBACPolicy, rbac_policy,
                     ignore_missing=ignore_missing)

    def find_rbac_policy(self, rbac_policy, ignore_missing=True, **args):
        """Find a single RBAC policy

        :param rbac_policy: The ID of a RBAC policy.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One
            :class:`~openstack.network.v2.rbac_policy.RBACPolicy` or None
        """
        return self._find(_rbac_policy.RBACPolicy, rbac_policy,
                          ignore_missing=ignore_missing, **args)

    def get_rbac_policy(self, rbac_policy):
        """Get a single RBAC policy

        :param rbac_policy: The value can be the ID of a RBAC policy or a
            :class:`~openstack.network.v2.rbac_policy.RBACPolicy` instance.

        :returns: One :class:`~openstack.network.v2.rbac_policy.RBACPolicy`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_rbac_policy.RBACPolicy, paginated=False, **query)

    def update_rbac_policy(self, rbac_policy, **attrs):
        """Update a RBAC policy

        :param rbac_policy: Either the id of a RBAC policy or a
            :class:`~openstack.network.v2.rbac_policy.RBACPolicy` instance.
        :param dict attrs: The attributes to update on the RBAC policy
                           represented by ``rbac_policy``.

        :returns: The updated RBAC policy
        :rtype: :class:`~openstack.network.v2.rbac_policy.RBACPolicy`
        """
        return self._update(_rbac_policy.RBACPolicy, rbac_policy, **attrs)

    def create_router(self, **attrs):
        """Create a new router from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.router.Router`,
                           comprised of the properties on the Router class.

        :returns: The results of router creation
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._create(_router.Router, **attrs)

    def delete_router(self, router, ignore_missing=True):
        """Delete a router

        :param router: The value can be either the ID of a router or a
                       :class:`~openstack.network.v2.router.Router` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the router does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent router.

        :returns: ``None``
        """
        self._delete(_router.Router, router, ignore_missing=ignore_missing)

    def find_router(self, name_or_id, ignore_missing=True, **args):
        """Find a single router

        :param name_or_id: The name or ID of a router.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.router.Router` or None
        """
        return self._find(_router.Router, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_router(self, router):
        """Get a single router

        :param router: The value can be the ID of a router or a
                       :class:`~openstack.network.v2.router.Router` instance.

        :returns: One :class:`~openstack.network.v2.router.Router`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_router.Router, paginated=False, **query)

    def update_router(self, router, **attrs):
        """Update a router

        :param router: Either the id of a router or a
                       :class:`~openstack.network.v2.router.Router` instance.
        :param dict attrs: The attributes to update on the router represented
                           by ``router``.

        :returns: The updated router
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._update(_router.Router, router, **attrs)

    def add_interface_to_router(self, router, subnet_id=None, port_id=None):
        """Add Interface to a router

        :param router: Either the router ID or an instance of
                       :class:`~openstack.network.v2.router.Router`
        :param subnet_id: ID of the subnet
        :param port_id: ID of the port
        :returns: Router with updated interface
        :rtype: :class: `~openstack.network.v2.router.Router`
        """
        body = {}
        if port_id:
            body = {'port_id': port_id}
        else:
            body = {'subnet_id': subnet_id}
        router = self._get_resource(_router.Router, router)
        return router.add_interface(self, **body)

    def remove_interface_from_router(self, router, subnet_id=None,
                                     port_id=None):
        """Remove Interface from a router

        :param router: Either the router ID or an instance of
                       :class:`~openstack.network.v2.router.Router`
        :param subnet: ID of the subnet
        :param port: ID of the port
        :returns: Router with updated interface
        :rtype: :class: `~openstack.network.v2.router.Router`
        """

        body = {}
        if port_id:
            body = {'port_id': port_id}
        else:
            body = {'subnet_id': subnet_id}
        router = self._get_resource(_router.Router, router)
        return router.remove_interface(self, **body)

    def add_gateway_to_router(self, router, **body):
        """Add Gateway to a router

        :param router: Either the router ID or an instance of
                       :class:`~openstack.network.v2.router.Router`
        :param body: Body with the gateway information
        :returns: Router with updated interface
        :rtype: :class: `~openstack.network.v2.router.Router`
        """
        router = self._get_resource(_router.Router, router)
        return router.add_gateway(self, **body)

    def remove_gateway_from_router(self, router, **body):
        """Remove Gateway from a router

        :param router: Either the router ID or an instance of
                       :class:`~openstack.network.v2.router.Router`
        :param body: Body with the gateway information
        :returns: Router with updated interface
        :rtype: :class: `~openstack.network.v2.router.Router`
        """
        router = self._get_resource(_router.Router, router)
        return router.remove_gateway(self, **body)

    def routers_hosting_l3_agents(self, router, **query):
        """Return a generator of L3 agent hosting a router

        :param router: Either the router id or an instance of
                        :class:`~openstack.network.v2.router.Router`
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources returned

        :returns: A generator of Router L3 Agents
        :rtype: :class:`~openstack.network.v2.router.RouterL3Agents`
        """
        router = self._get_resource(_router.Router, router)
        return self._list(_agent.RouterL3Agent, paginated=False,
                          router_id=router.id, **query)

    def agent_hosted_routers(self, agent, **query):
        """Return a generator of routers hosted by a L3 agent

        :param agent: Either the agent id of an instance of
                      :class:`~openstack.network.v2.network_agent.Agent`
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources returned

        :returns: A generator of routers
        :rtype: :class:`~openstack.network.v2.agent.L3AgentRouters`
        """
        agent = self._get_resource(_agent.Agent, agent)
        return self._list(_router.L3AgentRouter, paginated=False,
                          agent_id=agent.id, **query)

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

    def create_security_group(self, **attrs):
        """Create a new security group from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.security_group.SecurityGroup`,
            comprised of the properties on the SecurityGroup class.

        :returns: The results of security group creation
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._create(_security_group.SecurityGroup, **attrs)

    def delete_security_group(self, security_group, ignore_missing=True):
        """Delete a security group

        :param security_group:
            The value can be either the ID of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the security group does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent security group.

        :returns: ``None``
        """
        self._delete(_security_group.SecurityGroup, security_group,
                     ignore_missing=ignore_missing)

    def find_security_group(self, name_or_id, ignore_missing=True, **args):
        """Find a single security group

        :param name_or_id: The name or ID of a security group.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.security_group.
                  SecurityGroup` or None
        """
        return self._find(_security_group.SecurityGroup, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_security_group(self, security_group):
        """Get a single security group

        :param security_group: The value can be the ID of a security group or a
               :class:`~openstack.network.v2.security_group.SecurityGroup`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.security_group.SecurityGroup`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_security_group.SecurityGroup, security_group)

    def security_groups(self, **query):
        """Return a generator of security groups

        :param dict query: Optional query parameters to be sent to limit
                           the resources being returned. Valid parameters are:

            * ``description``: Security group description
            * ``name``: The name of a security group
            * ``project_id``: The ID of the project this security group is
                              associated with.

        :returns: A generator of security group objects
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._list(_security_group.SecurityGroup, paginated=False,
                          **query)

    def update_security_group(self, security_group, **attrs):
        """Update a security group

        :param security_group: Either the id of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.
        :param dict attrs: The attributes to update on the security group
                           represented by ``security_group``.

        :returns: The updated security group
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._update(_security_group.SecurityGroup, security_group,
                            **attrs)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="See the Network user guide for an example")
    def security_group_open_port(self, sgid, port, protocol='tcp'):
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': protocol,
            'port_range_max': port,
            'port_range_min': port,
            'security_group_id': sgid,
            'ethertype': 'IPv4'
        }
        return self.create_security_group_rule(**rule)

    @utils.deprecated(deprecated_in="0.9.14", removed_in="1.0",
                      details="See the Network user guide for an example")
    def security_group_allow_ping(self, sgid):
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': 'icmp',
            'port_range_max': None,
            'port_range_min': None,
            'security_group_id': sgid,
            'ethertype': 'IPv4'
        }
        return self.create_security_group_rule(**rule)

    def create_security_group_rule(self, **attrs):
        """Create a new security group rule from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.security_group_rule.
            SecurityGroupRule`, comprised of the properties on the
            SecurityGroupRule class.

        :returns: The results of security group rule creation
        :rtype: :class:`~openstack.network.v2.security_group_rule.\
            SecurityGroupRule`
        """
        return self._create(_security_group_rule.SecurityGroupRule, **attrs)

    def delete_security_group_rule(self, security_group_rule,
                                   ignore_missing=True):
        """Delete a security group rule

        :param security_group_rule:
            The value can be either the ID of a security group rule
            or a :class:`~openstack.network.v2.security_group_rule.
            SecurityGroupRule` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the security group rule does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent security group rule.

        :returns: ``None``
        """
        self._delete(_security_group_rule.SecurityGroupRule,
                     security_group_rule, ignore_missing=ignore_missing)

    def find_security_group_rule(self, name_or_id, ignore_missing=True,
                                 **args):
        """Find a single security group rule

        :param str name_or_id: The ID of a security group rule.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.security_group_rule.
                  SecurityGroupRule` or None
        """
        return self._find(_security_group_rule.SecurityGroupRule,
                          name_or_id, ignore_missing=ignore_missing, **args)

    def get_security_group_rule(self, security_group_rule):
        """Get a single security group rule

        :param security_group_rule:
            The value can be the ID of a security group rule or a
            :class:`~openstack.network.v2.security_group_rule.\
            SecurityGroupRule` instance.

        :returns: :class:`~openstack.network.v2.security_group_rule.\
            SecurityGroupRule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_security_group_rule.SecurityGroupRule,
                         security_group_rule)

    def security_group_rules(self, **query):
        """Return a generator of security group rules

        :param kwargs \*\*query: Optional query parameters to be sent to limit
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
        :rtype: :class:`~openstack.network.v2.security_group_rule.
                SecurityGroupRule`
        """
        return self._list(_security_group_rule.SecurityGroupRule,
                          paginated=False, **query)

    def create_segment(self, **attrs):
        """Create a new segment from attributes

        :param dict attrs: Keyword arguments which will be used to create
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the segment does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent segment.

        :returns: ``None``
        """
        self._delete(_segment.Segment, segment, ignore_missing=ignore_missing)

    def find_segment(self, name_or_id, ignore_missing=True, **args):
        """Find a single segment

        :param name_or_id: The name or ID of a segment.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.segment.Segment` or None
        """
        return self._find(_segment.Segment, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_segment(self, segment):
        """Get a single segment

        :param segment: The value can be the ID of a segment or a
                        :class:`~openstack.network.v2.segment.Segment`
                        instance.

        :returns: One :class:`~openstack.network.v2.segment.Segment`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_segment.Segment, segment)

    def segments(self, **query):
        """Return a generator of segments

        :param kwargs \*\*query: Optional query parameters to be sent to limit
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
        return self._list(_segment.Segment, paginated=False, **query)

    def update_segment(self, segment, **attrs):
        """Update a segment

        :param segment: Either the id of a segment or a
                        :class:`~openstack.network.v2.segment.Segment`
                        instance.
        :attrs kwargs: The attributes to update on the segment represented
                       by ``value``.

        :returns: The update segment
        :rtype: :class:`~openstack.network.v2.segment.Segment`
        """
        return self._update(_segment.Segment, segment, **attrs)

    def service_providers(self, **query):
        """Return a generator of service providers

        :param kwargs \*\* query: Optional query parameters to be sent to limit
                                  the resources being returned.

        :returns: A generator of service provider objects
        :rtype: :class:`~openstack.network.v2.service_provider.ServiceProvider`
        """

        return self._list(_service_provider.ServiceProvider,
                          paginated=False, **query)

    def create_service_profile(self, **attrs):
        """Create a new network service flavor profile from attributes

        :param dict attrs: Keyword arguments which will be used to create
                       a :class:`~openstack.network.v2.service_profile
                       .ServiceProfile`,
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
                       :class:`~openstack.network.v2.service_profile
                       .ServiceProfile` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the service profile does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent service profile.

        :returns: ``None``
        """
        self._delete(_service_profile.ServiceProfile, service_profile,
                     ignore_missing=ignore_missing)

    def find_service_profile(self, name_or_id, ignore_missing=True, **args):
        """Find a single network service flavor profile

        :param name_or_id: The name or ID of a service profile.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.service_profile
                      .ServiceProfile` or None
        """
        return self._find(_service_profile.ServiceProfile, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_service_profile(self, service_profile):
        """Get a single network service flavor profile

        :param service_profile: The value can be the ID of a service_profile or
            a :class:`~openstack.network.v2.service_profile.ServiceProfile`
            instance.

        :returns: One :class:`~openstack.network.v2.service_profile
                      .ServiceProfile`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_service_profile.ServiceProfile, paginated=True,
                          **query)

    def update_service_profile(self, service_profile, **attrs):
        """Update a network flavor service profile

        :param service_profile: Either the id of a service profile or a
                       :class:`~openstack.network.v2.service_profile
                       .ServiceProfile` instance.
        :attrs kwargs: The attributes to update on the service profile
                       represented by ``value``.

        :returns: The updated service profile
        :rtype: :class:`~openstack.network.v2.service_profile.ServiceProfile`
        """
        return self._update(_service_profile.ServiceProfile, service_profile,
                            **attrs)

    def create_subnet(self, **attrs):
        """Create a new subnet from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.subnet.Subnet`,
                           comprised of the properties on the Subnet class.

        :returns: The results of subnet creation
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._create(_subnet.Subnet, **attrs)

    def delete_subnet(self, subnet, ignore_missing=True):
        """Delete a subnet

        :param subnet: The value can be either the ID of a subnet or a
                       :class:`~openstack.network.v2.subnet.Subnet` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the subnet does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent subnet.

        :returns: ``None``
        """
        self._delete(_subnet.Subnet, subnet, ignore_missing=ignore_missing)

    def find_subnet(self, name_or_id, ignore_missing=True, **args):
        """Find a single subnet

        :param name_or_id: The name or ID of a subnet.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.subnet.Subnet` or None
        """
        return self._find(_subnet.Subnet, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_subnet(self, subnet):
        """Get a single subnet

        :param subnet: The value can be the ID of a subnet or a
                       :class:`~openstack.network.v2.subnet.Subnet` instance.

        :returns: One :class:`~openstack.network.v2.subnet.Subnet`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        return self._list(_subnet.Subnet, paginated=False, **query)

    def update_subnet(self, subnet, **attrs):
        """Update a subnet

        :param subnet: Either the id of a subnet or a
                       :class:`~openstack.network.v2.subnet.Subnet` instance.
        :param dict attrs: The attributes to update on the subnet represented
                           by ``subnet``.

        :returns: The updated subnet
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._update(_subnet.Subnet, subnet, **attrs)

    def create_subnet_pool(self, **attrs):
        """Create a new subnet pool from attributes

        :param dict attrs: Keyword arguments which will be used to create
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the subnet pool does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent subnet pool.

        :returns: ``None``
        """
        self._delete(_subnet_pool.SubnetPool, subnet_pool,
                     ignore_missing=ignore_missing)

    def find_subnet_pool(self, name_or_id, ignore_missing=True, **args):
        """Find a single subnet pool

        :param name_or_id: The name or ID of a subnet pool.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.subnet_pool.SubnetPool`
                  or None
        """
        return self._find(_subnet_pool.SubnetPool, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_subnet_pool(self, subnet_pool):
        """Get a single subnet pool

        :param subnet_pool: The value can be the ID of a subnet pool or a
            :class:`~openstack.network.v2.subnet_pool.SubnetPool` instance.

        :returns: One :class:`~openstack.network.v2.subnet_pool.SubnetPool`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_subnet_pool.SubnetPool, subnet_pool)

    def subnet_pools(self, **query):
        """Return a generator of subnet pools

        :param kwargs \*\*query: Optional query parameters to be sent to limit
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
        return self._list(_subnet_pool.SubnetPool, paginated=False, **query)

    def update_subnet_pool(self, subnet_pool, **attrs):
        """Update a subnet pool

        :param subnet_pool: Either the ID of a subnet pool or a
            :class:`~openstack.network.v2.subnet_pool.SubnetPool` instance.
        :param dict attrs: The attributes to update on the subnet pool
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
                '%s resource does not support tag' %
                resource.__class__.__name__)

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

    def create_vpn_service(self, **attrs):
        """Create a new vpn service from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.vpn_service.VPNService`,
            comprised of the properties on the VPNService class.

        :returns: The results of vpn service creation
        :rtype: :class:`~openstack.network.v2.vpn_service.VPNService`
        """
        return self._create(_vpn_service.VPNService, **attrs)

    def delete_vpn_service(self, vpn_service, ignore_missing=True):
        """Delete a vpn service

        :param vpn_service:
            The value can be either the ID of a vpn service or a
            :class:`~openstack.network.v2.vpn_service.VPNService` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the vpn service does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent vpn service.

        :returns: ``None``
        """
        self._delete(_vpn_service.VPNService, vpn_service,
                     ignore_missing=ignore_missing)

    def find_vpn_service(self, name_or_id, ignore_missing=True, **args):
        """Find a single vpn service

        :param name_or_id: The name or ID of a vpn service.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~openstack.network.v2.vpn_service.VPNService`
                  or None
        """
        return self._find(_vpn_service.VPNService, name_or_id,
                          ignore_missing=ignore_missing, **args)

    def get_vpn_service(self, vpn_service):
        """Get a single vpn service

        :param vpn_service: The value can be the ID of a vpn service or a
               :class:`~openstack.network.v2.vpn_service.VPNService`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.vpn_service.VPNService`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_vpn_service.VPNService, vpn_service)

    def vpn_services(self, **query):
        """Return a generator of vpn services

        :param dict query: Optional query parameters to be sent to limit
                           the resources being returned.

        :returns: A generator of vpn service objects
        :rtype: :class:`~openstack.network.v2.vpn_service.VPNService`
        """
        return self._list(_vpn_service.VPNService, paginated=False, **query)

    def update_vpn_service(self, vpn_service, **attrs):
        """Update a vpn service

        :param vpn_service: Either the id of a vpn service or a
            :class:`~openstack.network.v2.vpn_service.VPNService` instance.
        :param dict attrs: The attributes to update on the VPN service
                           represented by ``vpn_service``.

        :returns: The updated vpnservice
        :rtype: :class:`~openstack.network.v2.vpn_service.VPNService`
        """
        return self._update(_vpn_service.VPNService, vpn_service, **attrs)
