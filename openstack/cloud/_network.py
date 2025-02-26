# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from openstack.cloud import _network_common
from openstack.cloud import _utils
from openstack.cloud import exc
from openstack import exceptions


class NetworkCloudMixin(_network_common.NetworkCommonCloudMixin):
    def _neutron_extensions(self):
        extensions = set()
        for extension in self.network.extensions():
            extensions.add(extension['alias'])
        return extensions

    def _has_neutron_extension(self, extension_alias):
        return extension_alias in self._neutron_extensions()

    # TODO(stephenfin): Deprecate this in favour of the 'list' function
    def search_networks(self, name_or_id=None, filters=None):
        """Search networks

        :param name_or_id: Name or ID of the desired network.
        :param filters: A dict containing additional filters to use. e.g.
            {'router:external': True}

        :returns: A list of network ``Network`` objects matching the search
            criteria.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        query = {}
        if name_or_id:
            query['name'] = name_or_id
        if filters:
            query.update(filters)
        return list(self.network.networks(**query))

    # TODO(stephenfin): Deprecate this in favour of the 'list' function
    def search_routers(self, name_or_id=None, filters=None):
        """Search routers

        :param name_or_id: Name or ID of the desired router.
        :param filters: A dict containing additional filters to use. e.g.
            {'admin_state_up': True}

        :returns: A list of network ``Router`` objects matching the search
            criteria.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        query = {}
        if name_or_id:
            query['name'] = name_or_id
        if filters:
            query.update(filters)
        return list(self.network.routers(**query))

    # TODO(stephenfin): Deprecate this in favour of the 'list' function
    def search_subnets(self, name_or_id=None, filters=None):
        """Search subnets

        :param name_or_id: Name or ID of the desired subnet.
        :param filters: A dict containing additional filters to use. e.g.
            {'enable_dhcp': True}

        :returns: A list of network ``Subnet`` objects matching the search
            criteria.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        query = {}
        if name_or_id:
            query['name'] = name_or_id
        if filters:
            query.update(filters)
        return list(self.network.subnets(**query))

    # TODO(stephenfin): Deprecate this in favour of the 'list' function
    def search_ports(self, name_or_id=None, filters=None):
        """Search ports

        :param name_or_id: Name or ID of the desired port.
        :param filters: A dict containing additional filters to use. e.g.
            {'device_id': '2711c67a-b4a7-43dd-ace7-6187b791c3f0'}

        :returns: A list of network ``Port`` objects matching the search
            criteria.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        # If the filter is a string, do not push the filter down to neutron;
        # get all the ports and filter locally.
        # TODO(stephenfin): '_filter_list' can handle a dict - pass it down
        if isinstance(filters, str):
            pushdown_filters = None
        else:
            pushdown_filters = filters
        ports = self.list_ports(pushdown_filters)
        return _utils._filter_list(ports, name_or_id, filters)

    def list_networks(self, filters=None):
        """List all available networks.

        :param filters: (optional) A dict of filter conditions to push down.
        :returns: A list of network ``Network`` objects.
        """
        # If the cloud is running nova-network, just return an empty list.
        if not self.has_service('network'):
            return []

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.network.networks(**filters))

    def list_routers(self, filters=None):
        """List all available routers.

        :param filters: (optional) A dict of filter conditions to push down
        :returns: A list of network ``Router`` objects.
        """
        # If the cloud is running nova-network, just return an empty list.
        if not self.has_service('network'):
            return []

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.network.routers(**filters))

    def list_subnets(self, filters=None):
        """List all available subnets.

        :param filters: (optional) A dict of filter conditions to push down
        :returns: A list of network ``Subnet`` objects.
        """
        # If the cloud is running nova-network, just return an empty list.
        if not self.has_service('network'):
            return []

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.network.subnets(**filters))

    def list_ports(self, filters=None):
        """List all available ports.

        :param filters: (optional) A dict of filter conditions to push down
        :returns: A list of network ``Port`` objects.
        """
        # If the cloud is running nova-network, just return an empty list.
        if not self.has_service('network'):
            return []

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        return list(self.network.ports(**filters))

    # TODO(stephenfin): Deprecate 'filters'; users should use 'list' for this
    def get_qos_policy(self, name_or_id, filters=None):
        """Get a QoS policy by name or ID.

        :param name_or_id: Name or ID of the policy.
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A network ``QoSPolicy`` object if found, else None.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        if not filters:
            filters = {}
        return self.network.find_qos_policy(
            name_or_id=name_or_id, ignore_missing=True, **filters
        )

    # TODO(stephenfin): Deprecate this in favour of the 'list' function
    def search_qos_policies(self, name_or_id=None, filters=None):
        """Search QoS policies

        :param name_or_id: Name or ID of the desired policy.
        :param filters: a dict containing additional filters to use. e.g.
            {'shared': True}

        :returns: A list of network ``QosPolicy`` objects matching the search
            criteria.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        query = {}
        if name_or_id:
            query['name'] = name_or_id
        if filters:
            query.update(filters)
        return list(self.network.qos_policies(**query))

    def list_qos_rule_types(self, filters=None):
        """List all available QoS rule types.

        :param filters: (optional) A dict of filter conditions to push down
        :returns: A list of network ``QosRuleType`` objects.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.network.qos_rule_types(**filters))

    # TODO(stephenfin): Deprecate 'filters'; users should use 'list' for this
    def get_qos_rule_type_details(self, rule_type, filters=None):
        """Get a QoS rule type details by rule type name.

        :param rule_type: Name of the QoS rule type.
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A network ``QoSRuleType`` object if found, else None.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        if not self._has_neutron_extension('qos-rule-type-details'):
            raise exc.OpenStackCloudUnavailableExtension(
                'qos-rule-type-details extension is not available '
                'on target cloud'
            )

        return self.network.get_qos_rule_type(rule_type)

    def list_qos_policies(self, filters=None):
        """List all available QoS policies.

        :param filters: (optional) A dict of filter conditions to push down
        :returns: A list of network ``QosPolicy`` objects.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.network.qos_policies(**filters))

    # TODO(stephenfin): Deprecate 'filters'; users should use 'list' for this
    def get_network(self, name_or_id, filters=None):
        """Get a network by name or ID.

        :param name_or_id: Name or ID of the network.
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A network ``Network`` object if found, else None.
        """
        if not filters:
            filters = {}
        return self.network.find_network(
            name_or_id=name_or_id, ignore_missing=True, **filters
        )

    def get_network_by_id(self, id):
        """Get a network by ID

        :param id: ID of the network.
        :returns: A network ``Network`` object if found, else None.
        """
        return self.network.get_network(id)

    # TODO(stephenfin): Deprecate 'filters'; users should use 'list' for this
    def get_router(self, name_or_id, filters=None):
        """Get a router by name or ID.

        :param name_or_id: Name or ID of the router.
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A network ``Router`` object if found, else None.
        """
        if not filters:
            filters = {}
        return self.network.find_router(
            name_or_id=name_or_id, ignore_missing=True, **filters
        )

    # TODO(stephenfin): Deprecate 'filters'; users should use 'list' for this
    def get_subnet(self, name_or_id, filters=None):
        """Get a subnet by name or ID.

        :param name_or_id: Name or ID of the subnet.
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

        :returns: A network ``Subnet`` object if found, else None.
        """
        if not filters:
            filters = {}
        return self.network.find_subnet(
            name_or_id=name_or_id, ignore_missing=True, **filters
        )

    def get_subnet_by_id(self, id):
        """Get a subnet by ID

        :param id: ID of the subnet.
        :returns: A network ``Subnet`` object if found, else None.
        """
        return self.network.get_subnet(id)

    # TODO(stephenfin): Deprecate 'filters'; users should use 'list' for this
    def get_port(self, name_or_id, filters=None):
        """Get a port by name or ID.

        :param name_or_id: Name or ID of the port.
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A network ``Port`` object if found, else None.
        """
        if not filters:
            filters = {}
        return self.network.find_port(
            name_or_id=name_or_id, ignore_missing=True, **filters
        )

    def get_port_by_id(self, id):
        """Get a port by ID

        :param id: ID of the port.
        :returns: A network ``Port`` object if found, else None.
        """
        return self.network.get_port(id)

    def get_subnetpool(self, name_or_id):
        """Get a subnetpool by name or ID.

        :param name_or_id: Name or ID of the subnetpool.

        :returns: A network ``Subnetpool`` object if found, else None.
        """
        return self.network.find_subnet_pool(
            name_or_id=name_or_id, ignore_missing=True
        )

    def create_network(
        self,
        name,
        shared=False,
        admin_state_up=True,
        external=False,
        provider=None,
        project_id=None,
        availability_zone_hints=None,
        port_security_enabled=None,
        mtu_size=None,
        dns_domain=None,
    ):
        """Create a network.

        :param string name: Name of the network being created.
        :param bool shared: Set the network as shared.
        :param bool admin_state_up: Set the network administrative state to up.
        :param bool external: Whether this network is externally accessible.
        :param dict provider: A dict of network provider options. Example::

            {'network_type': 'vlan', 'segmentation_id': 'vlan1'}

        :param string project_id: Specify the project ID this network
            will be created on (admin-only).
        :param types.ListType availability_zone_hints: A list of availability
            zone hints.
        :param bool port_security_enabled: Enable / Disable port security
        :param int mtu_size: maximum transmission unit value to address
            fragmentation. Minimum value is 68 for IPv4, and 1280 for IPv6.
        :param string dns_domain: Specify the DNS domain associated with
            this network.
        :returns: The created network ``Network`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        network = {
            'name': name,
            'admin_state_up': admin_state_up,
        }

        if shared:
            network['shared'] = shared

        if project_id is not None:
            network['project_id'] = project_id

        if availability_zone_hints is not None:
            if not isinstance(availability_zone_hints, list):
                raise exceptions.SDKException(
                    "Parameter 'availability_zone_hints' must be a list"
                )
            if not self._has_neutron_extension('network_availability_zone'):
                raise exc.OpenStackCloudUnavailableExtension(
                    'network_availability_zone extension is not available on '
                    'target cloud'
                )
            network['availability_zone_hints'] = availability_zone_hints

        if provider:
            if not isinstance(provider, dict):
                raise exceptions.SDKException(
                    "Parameter 'provider' must be a dict"
                )
            # Only pass what we know
            for attr in (
                'physical_network',
                'network_type',
                'segmentation_id',
            ):
                if attr in provider:
                    arg = "provider:" + attr
                    network[arg] = provider[attr]

        # Do not send 'router:external' unless it is explicitly
        # set since sending it *might* cause "Forbidden" errors in
        # some situations. It defaults to False in the client, anyway.
        if external:
            network['router:external'] = True

        if port_security_enabled is not None:
            if not isinstance(port_security_enabled, bool):
                raise exceptions.SDKException(
                    "Parameter 'port_security_enabled' must be a bool"
                )
            network['port_security_enabled'] = port_security_enabled

        if mtu_size:
            if not isinstance(mtu_size, int):
                raise exceptions.SDKException(
                    "Parameter 'mtu_size' must be an integer."
                )
            if not mtu_size >= 68:
                raise exceptions.SDKException(
                    "Parameter 'mtu_size' must be greater than 67."
                )

            network['mtu'] = mtu_size

        if dns_domain:
            network['dns_domain'] = dns_domain

        network = self.network.create_network(**network)

        # Reset cache so the new network is picked up
        self._reset_network_caches()
        return network

    @_utils.valid_kwargs(
        "name",
        "shared",
        "admin_state_up",
        "external",
        "provider",
        "mtu_size",
        "port_security_enabled",
        "dns_domain",
    )
    def update_network(self, name_or_id, **kwargs):
        """Update a network.

        :param string name_or_id: Name or ID of the network being updated.
        :param string name: New name of the network.
        :param bool shared: Set the network as shared.
        :param bool admin_state_up: Set the network administrative state to up.
        :param bool external: Whether this network is externally accessible.
        :param dict provider: A dict of network provider options. Example::

            {'network_type': 'vlan', 'segmentation_id': 'vlan1'}

        :param int mtu_size: New maximum transmission unit value to address
            fragmentation. Minimum value is 68 for IPv4, and 1280 for IPv6.
        :param bool port_security_enabled: Enable or disable port security.
        :param string dns_domain: Specify the DNS domain associated with
            this network.

        :returns: The updated network ``Network`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        provider = kwargs.pop('provider', None)
        if provider:
            if not isinstance(provider, dict):
                raise exceptions.SDKException(
                    "Parameter 'provider' must be a dict"
                )
            for key in ('physical_network', 'network_type', 'segmentation_id'):
                if key in provider:
                    kwargs['provider:' + key] = provider.pop(key)

        if 'external' in kwargs:
            kwargs['router:external'] = kwargs.pop('external')

        if 'port_security_enabled' in kwargs:
            if not isinstance(kwargs['port_security_enabled'], bool):
                raise exceptions.SDKException(
                    "Parameter 'port_security_enabled' must be a bool"
                )

        if 'mtu_size' in kwargs:
            if not isinstance(kwargs['mtu_size'], int):
                raise exceptions.SDKException(
                    "Parameter 'mtu_size' must be an integer."
                )
            if kwargs['mtu_size'] < 68:
                raise exceptions.SDKException(
                    "Parameter 'mtu_size' must be greater than 67."
                )
            kwargs['mtu'] = kwargs.pop('mtu_size')

        network = self.get_network(name_or_id)
        if not network:
            raise exceptions.SDKException(f"Network {name_or_id} not found.")

        network = self.network.update_network(network, **kwargs)

        self._reset_network_caches()

        return network

    def delete_network(self, name_or_id):
        """Delete a network.

        :param name_or_id: Name or ID of the network being deleted.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        network = self.get_network(name_or_id)
        if not network:
            self.log.debug("Network %s not found for deleting", name_or_id)
            return False

        self.network.delete_network(network)

        # Reset cache so the deleted network is removed
        self._reset_network_caches()

        return True

    def set_network_quotas(self, name_or_id, **kwargs):
        """Set a network quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: :class:`~openstack.exceptions.SDKException` if the resource to
            set the quota does not exist.
        """
        proj = self.identity.find_project(name_or_id, ignore_missing=True)
        if not proj:
            raise exceptions.SDKException(
                f"Project {name_or_id} was requested by was not found "
                f"on the cloud"
            )
        self.network.update_quota(proj.id, **kwargs)

    def get_network_quotas(self, name_or_id, details=False):
        """Get network quotas for a project

        :param name_or_id: project name or id
        :param details: if set to True it will return details about usage
            of quotas by given project

        :returns: A network ``Quota`` object if found, else None.
        :raises: :class:`~openstack.exceptions.SDKException` if it's not a
            valid project
        """
        proj = self.identity.find_project(name_or_id, ignore_missing=True)
        if not proj:
            raise exc.OpenStackCloudException(
                f"Project {name_or_id} was requested by was not found "
                f"on the cloud"
            )
        return self.network.get_quota(proj.id, details)

    def get_network_extensions(self):
        """Get Cloud provided network extensions

        :returns: A set of Neutron extension aliases.
        """
        return self._neutron_extensions()

    def delete_network_quotas(self, name_or_id):
        """Delete network quotas for a project

        :param name_or_id: project name or id

        :returns: dict with the quotas
        :raises: :class:`~openstack.exceptions.SDKException` if it's not a
            valid project or the network client call failed
        """
        proj = self.identity.find_project(name_or_id, ignore_missing=True)
        if not proj:
            raise exceptions.SDKException(
                f"Project {name_or_id} was requested by was not found "
                f"on the cloud"
            )
        self.network.delete_quota(proj.id)

    @_utils.valid_kwargs(
        'action',
        'description',
        'destination_firewall_group_id',
        'destination_ip_address',
        'destination_port',
        'enabled',
        'ip_version',
        'name',
        'project_id',
        'protocol',
        'shared',
        'source_firewall_group_id',
        'source_ip_address',
        'source_port',
    )
    def create_firewall_rule(self, **kwargs):
        """
        Creates firewall rule.

        :param action: Action performed on traffic.
            Valid values: allow, deny
            Defaults to deny.
        :param description: Human-readable description.
        :param destination_firewall_group_id: ID of destination firewall group.
        :param destination_ip_address: IPv4-, IPv6 address or CIDR.
        :param destination_port: Port or port range (e.g. 80:90)
        :param bool enabled: Status of firewall rule. You can disable rules
            without disassociating them from firewall policies. Defaults to
            True.
        :param int ip_version: IP Version. Valid values: 4, 6 Defaults to 4.
        :param name: Human-readable name.
        :param project_id: Project id.
        :param protocol: IP protocol. Valid values: icmp, tcp, udp, null
        :param bool shared: Visibility to other projects. Defaults to False.
        :param source_firewall_group_id: ID of source firewall group.
        :param source_ip_address: IPv4-, IPv6 address or CIDR.
        :param source_port: Port or port range (e.g. 80:90)
        :raises: BadRequestException if parameters are malformed
        :returns: The created network ``FirewallRule`` object.
        """
        return self.network.create_firewall_rule(**kwargs)

    def delete_firewall_rule(self, name_or_id, filters=None):
        """
        Deletes firewall rule.

        Prints debug message in case to-be-deleted resource was not found.

        :param name_or_id: firewall rule name or id
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :raises: DuplicateResource on multiple matches
        :returns: True if resource is successfully deleted, False otherwise.
        :rtype: bool
        """
        if not filters:
            filters = {}
        try:
            firewall_rule = self.network.find_firewall_rule(
                name_or_id, ignore_missing=False, **filters
            )
            self.network.delete_firewall_rule(
                firewall_rule, ignore_missing=False
            )
        except exceptions.NotFoundException:
            self.log.debug(
                'Firewall rule %s not found for deleting', name_or_id
            )
            return False
        return True

    # TODO(stephenfin): Deprecate 'filters'; users should use 'list' for this
    def get_firewall_rule(self, name_or_id, filters=None):
        """
        Retrieves a single firewall rule.

        :param name_or_id: firewall rule name or id
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :raises: DuplicateResource on multiple matches
        :returns: A network ``FirewallRule`` object if found, else None.
        """
        if not filters:
            filters = {}
        return self.network.find_firewall_rule(
            name_or_id, ignore_missing=True, **filters
        )

    def list_firewall_rules(self, filters=None):
        """
        Lists firewall rules.

        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of network ``FirewallRule`` objects.
        :rtype: list[FirewallRule]
        """
        if not filters:
            filters = {}
        return list(self.network.firewall_rules(**filters))

    @_utils.valid_kwargs(
        'action',
        'description',
        'destination_firewall_group_id',
        'destination_ip_address',
        'destination_port',
        'enabled',
        'ip_version',
        'name',
        'project_id',
        'protocol',
        'shared',
        'source_firewall_group_id',
        'source_ip_address',
        'source_port',
    )
    def update_firewall_rule(self, name_or_id, filters=None, **kwargs):
        """
        Updates firewall rule.

        :param name_or_id: firewall rule name or id
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :param kwargs: firewall rule update parameters.
            See create_firewall_rule docstring for valid parameters.
        :returns: The updated network ``FirewallRule`` object.
        :raises: BadRequestException if parameters are malformed
        :raises: NotFoundException if resource is not found
        """
        if not filters:
            filters = {}
        firewall_rule = self.network.find_firewall_rule(
            name_or_id, ignore_missing=False, **filters
        )

        return self.network.update_firewall_rule(firewall_rule, **kwargs)

    def _get_firewall_rule_ids(self, name_or_id_list, filters=None):
        """
        Takes a list of firewall rule name or ids, looks them up and returns
        a list of firewall rule ids.

        Used by `create_firewall_policy` and `update_firewall_policy`.

        :param list[str] name_or_id_list: firewall rule name or id list
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :raises: NotFoundException if resource is not found
        :return: list of firewall rule ids
        :rtype: list[str]
        """
        if not filters:
            filters = {}
        ids_list = []
        for name_or_id in name_or_id_list:
            ids_list.append(
                self.network.find_firewall_rule(
                    name_or_id, ignore_missing=False, **filters
                )['id']
            )
        return ids_list

    @_utils.valid_kwargs(
        'audited',
        'description',
        'firewall_rules',
        'name',
        'project_id',
        'shared',
    )
    def create_firewall_policy(self, **kwargs):
        """
        Create firewall policy.

        :param bool audited: Status of audition of firewall policy.
            Set to False each time the firewall policy or the associated
            firewall rules are changed.  Has to be explicitly set to True.
        :param description: Human-readable description.
        :param list[str] firewall_rules: List of associated firewall rules.
        :param name: Human-readable name.
        :param project_id: Project id.
        :param bool shared: Visibility to other projects.
            Defaults to False.
        :raises: BadRequestException if parameters are malformed
        :raises: NotFoundException if a resource from firewall_list not found
        :returns: The created network ``FirewallPolicy`` object.
        """
        if 'firewall_rules' in kwargs:
            kwargs['firewall_rules'] = self._get_firewall_rule_ids(
                kwargs['firewall_rules']
            )

        return self.network.create_firewall_policy(**kwargs)

    def delete_firewall_policy(self, name_or_id, filters=None):
        """
        Deletes firewall policy.
        Prints debug message in case to-be-deleted resource was not found.

        :param name_or_id: firewall policy name or id
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :raises: DuplicateResource on multiple matches
        :returns: True if resource is successfully deleted, False otherwise.
        :rtype: bool
        """
        if not filters:
            filters = {}
        try:
            firewall_policy = self.network.find_firewall_policy(
                name_or_id, ignore_missing=False, **filters
            )
            self.network.delete_firewall_policy(
                firewall_policy, ignore_missing=False
            )
        except exceptions.NotFoundException:
            self.log.debug(
                'Firewall policy %s not found for deleting', name_or_id
            )
            return False
        return True

    # TODO(stephenfin): Deprecate 'filters'; users should use 'list' for this
    def get_firewall_policy(self, name_or_id, filters=None):
        """
        Retrieves a single firewall policy.

        :param name_or_id: firewall policy name or id
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :raises: DuplicateResource on multiple matches
        :returns: A network ``FirewallPolicy`` object if found, else None.
        """
        if not filters:
            filters = {}
        return self.network.find_firewall_policy(
            name_or_id, ignore_missing=True, **filters
        )

    def list_firewall_policies(self, filters=None):
        """
        Lists firewall policies.

        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of network ``FirewallPolicy`` objects.
        :rtype: list[FirewallPolicy]
        """
        if not filters:
            filters = {}
        return list(self.network.firewall_policies(**filters))

    @_utils.valid_kwargs(
        'audited',
        'description',
        'firewall_rules',
        'name',
        'project_id',
        'shared',
    )
    def update_firewall_policy(self, name_or_id, filters=None, **kwargs):
        """
        Updates firewall policy.

        :param name_or_id: firewall policy name or id
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :param kwargs: firewall policy update parameters
            See create_firewall_policy docstring for valid parameters.
        :returns: The updated network ``FirewallPolicy`` object.
        :raises: BadRequestException if parameters are malformed
        :raises: DuplicateResource on multiple matches
        :raises: NotFoundException if resource is not found
        """
        if not filters:
            filters = {}
        firewall_policy = self.network.find_firewall_policy(
            name_or_id, ignore_missing=False, **filters
        )

        if 'firewall_rules' in kwargs:
            kwargs['firewall_rules'] = self._get_firewall_rule_ids(
                kwargs['firewall_rules']
            )

        return self.network.update_firewall_policy(firewall_policy, **kwargs)

    def insert_rule_into_policy(
        self,
        name_or_id,
        rule_name_or_id,
        insert_after=None,
        insert_before=None,
        filters=None,
    ):
        """Add firewall rule to a policy.

        Adds firewall rule to the firewall_rules list of a firewall policy.
        Short-circuits and returns the firewall policy early if the firewall
        rule id is already present in the firewall_rules list.
        This method doesn't do re-ordering. If you want to move a firewall rule
        or down the list, you have to remove and re-add it.

        :param name_or_id: firewall policy name or id
        :param rule_name_or_id: firewall rule name or id
        :param insert_after: rule name or id that should precede added rule
        :param insert_before: rule name or id that should succeed added rule
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :raises: NotFoundException if firewall policy or any of the firewall
            rules (inserted, after, before) is not found.
        :return: updated firewall policy
        :rtype: FirewallPolicy
        """
        if not filters:
            filters = {}
        firewall_policy = self.network.find_firewall_policy(
            name_or_id, ignore_missing=False, **filters
        )

        firewall_rule = self.network.find_firewall_rule(
            rule_name_or_id, ignore_missing=False
        )
        # short-circuit if rule already in firewall_rules list
        # the API can't do any re-ordering of existing rules
        if firewall_rule['id'] in firewall_policy['firewall_rules']:
            self.log.debug(
                'Firewall rule %s already associated with firewall policy %s',
                rule_name_or_id,
                name_or_id,
            )
            return firewall_policy

        pos_params = {}
        if insert_after is not None:
            pos_params['insert_after'] = self.network.find_firewall_rule(
                insert_after, ignore_missing=False
            )['id']

        if insert_before is not None:
            pos_params['insert_before'] = self.network.find_firewall_rule(
                insert_before, ignore_missing=False
            )['id']

        return self.network.insert_rule_into_policy(
            firewall_policy['id'], firewall_rule['id'], **pos_params
        )

    def remove_rule_from_policy(
        self, name_or_id, rule_name_or_id, filters=None
    ):
        """
        Remove firewall rule from firewall policy's firewall_rules list.
        Short-circuits and returns firewall policy early if firewall rule
        is already absent from the firewall_rules list.

        :param name_or_id: firewall policy name or id
        :param rule_name_or_id: firewall rule name or id
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :raises: NotFoundException if firewall policy is not found
        :return: updated firewall policy
        :rtype: FirewallPolicy
        """
        if not filters:
            filters = {}
        firewall_policy = self.network.find_firewall_policy(
            name_or_id, ignore_missing=False, **filters
        )

        firewall_rule = self.network.find_firewall_rule(rule_name_or_id)
        if not firewall_rule:
            # short-circuit: if firewall rule is not found,
            # return current firewall policy
            self.log.debug(
                'Firewall rule %s not found for removing', rule_name_or_id
            )
            return firewall_policy

        if firewall_rule['id'] not in firewall_policy['firewall_rules']:
            # short-circuit: if firewall rule id is not associated,
            # log it to debug and return current firewall policy
            self.log.debug(
                'Firewall rule %s not associated with firewall policy %s',
                rule_name_or_id,
                name_or_id,
            )
            return firewall_policy

        return self.network.remove_rule_from_policy(
            firewall_policy['id'], firewall_rule['id']
        )

    @_utils.valid_kwargs(
        'admin_state_up',
        'description',
        'egress_firewall_policy',
        'ingress_firewall_policy',
        'name',
        'ports',
        'project_id',
        'shared',
    )
    def create_firewall_group(self, **kwargs):
        """
        Creates firewall group. The keys egress_firewall_policy and
        ingress_firewall_policy are looked up and mapped as
        egress_firewall_policy_id and ingress_firewall_policy_id respectively.
        Port name or ids list is transformed to port ids list before the POST
        request.

        :param bool admin_state_up: State of firewall group.
            Will block all traffic if set to False. Defaults to True.
        :param description: Human-readable description.
        :param egress_firewall_policy: Name or id of egress firewall policy.
        :param ingress_firewall_policy: Name or id of ingress firewall policy.
        :param name: Human-readable name.
        :param list[str] ports: List of associated ports (name or id)
        :param project_id: Project id.
        :param shared: Visibility to other projects. Defaults to False.
        :raises: BadRequestException if parameters are malformed
        :raises: DuplicateResource on multiple matches
        :raises: NotFoundException if (ingress-, egress-) firewall policy or
            a port is not found.
        :returns: The created network ``FirewallGroup`` object.
        """
        self._lookup_ingress_egress_firewall_policy_ids(kwargs)
        if 'ports' in kwargs:
            kwargs['ports'] = self._get_port_ids(kwargs['ports'])
        return self.network.create_firewall_group(**kwargs)

    def delete_firewall_group(self, name_or_id, filters=None):
        """
        Deletes firewall group.
        Prints debug message in case to-be-deleted resource was not found.

        :param name_or_id: firewall group name or id
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :returns: True if resource is successfully deleted, False otherwise.
        :rtype: bool
        """
        if not filters:
            filters = {}
        try:
            firewall_group = self.network.find_firewall_group(
                name_or_id, ignore_missing=False, **filters
            )
            self.network.delete_firewall_group(
                firewall_group, ignore_missing=False
            )
        except exceptions.NotFoundException:
            self.log.debug(
                'Firewall group %s not found for deleting', name_or_id
            )
            return False
        return True

    # TODO(stephenfin): Deprecate 'filters'; users should use 'list' for this
    def get_firewall_group(self, name_or_id, filters=None):
        """
        Retrieves firewall group.

        :param name_or_id: firewall group name or id
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :returns: A network ``FirewallGroup`` object if found, else None.
        """
        if not filters:
            filters = {}
        return self.network.find_firewall_group(
            name_or_id, ignore_missing=True, **filters
        )

    def list_firewall_groups(self, filters=None):
        """
        Lists firewall groups.

        :returns: A list of network ``FirewallGroup`` objects.
        """
        if not filters:
            filters = {}
        return list(self.network.firewall_groups(**filters))

    @_utils.valid_kwargs(
        'admin_state_up',
        'description',
        'egress_firewall_policy',
        'ingress_firewall_policy',
        'name',
        'ports',
        'project_id',
        'shared',
    )
    def update_firewall_group(self, name_or_id, filters=None, **kwargs):
        """
        Updates firewall group.
        To unset egress- or ingress firewall policy, set egress_firewall_policy
        or ingress_firewall_policy to None. You can also set
        egress_firewall_policy_id and ingress_firewall_policy_id directly,
        which will skip the policy lookups.

        :param name_or_id: firewall group name or id
        :param dict filters: optional filters
        :param kwargs: firewall group update parameters
            See create_firewall_group docstring for valid parameters.
        :returns: The updated network ``FirewallGroup`` object.
        :raises: BadRequestException if parameters are malformed
        :raises: DuplicateResource on multiple matches
        :raises: NotFoundException if firewall group, a firewall policy
            (egress, ingress) or port is not found
        """
        if not filters:
            filters = {}
        firewall_group = self.network.find_firewall_group(
            name_or_id, ignore_missing=False, **filters
        )
        self._lookup_ingress_egress_firewall_policy_ids(kwargs)

        if 'ports' in kwargs:
            kwargs['ports'] = self._get_port_ids(kwargs['ports'])
        return self.network.update_firewall_group(firewall_group, **kwargs)

    def _lookup_ingress_egress_firewall_policy_ids(self, firewall_group):
        """
        Transforms firewall_group dict IN-PLACE. Takes the value of the keys
        egress_firewall_policy and ingress_firewall_policy, looks up the
        policy ids and maps them to egress_firewall_policy_id and
        ingress_firewall_policy_id. Old keys which were used for the lookup
        are deleted.

        :param dict firewall_group: firewall group dict
        :raises: DuplicateResource on multiple matches
        :raises: NotFoundException if a firewall policy is not found
        """
        for key in ('egress_firewall_policy', 'ingress_firewall_policy'):
            if key not in firewall_group:
                continue
            if firewall_group[key] is None:
                val = None
            else:
                val = self.network.find_firewall_policy(
                    firewall_group[key], ignore_missing=False
                )['id']
            firewall_group[key + '_id'] = val
            del firewall_group[key]

    @_utils.valid_kwargs(
        "name", "description", "shared", "default", "project_id"
    )
    def create_qos_policy(self, **kwargs):
        """Create a QoS policy.

        :param string name: Name of the QoS policy being created.
        :param string description: Description of created QoS policy.
        :param bool shared: Set the QoS policy as shared.
        :param bool default: Set the QoS policy as default for project.
        :param string project_id: Specify the project ID this QoS policy
            will be created on (admin-only).

        :returns: The created network ``QosPolicy`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        default = kwargs.pop("default", None)
        if default is not None:
            if self._has_neutron_extension('qos-default'):
                kwargs['is_default'] = default
            else:
                self.log.debug(
                    "'qos-default' extension is not available on target cloud"
                )

        return self.network.create_qos_policy(**kwargs)

    @_utils.valid_kwargs(
        "name", "description", "shared", "default", "project_id"
    )
    def update_qos_policy(self, name_or_id, **kwargs):
        """Update an existing QoS policy.

        :param string name_or_id: Name or ID of the QoS policy to update.
        :param string policy_name: The new name of the QoS policy.
        :param string description: The new description of the QoS policy.
        :param bool shared: If True, the QoS policy will be set as shared.
        :param bool default: If True, the QoS policy will be set as default for
            project.

        :returns: The updated network ``QosPolicyRule`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        default = kwargs.pop("default", None)
        if default is not None:
            if self._has_neutron_extension('qos-default'):
                kwargs['is_default'] = default
            else:
                self.log.debug(
                    "'qos-default' extension is not available on target cloud"
                )

        if not kwargs:
            self.log.debug("No QoS policy data to update")
            return

        curr_policy = self.network.find_qos_policy(
            name_or_id, ignore_missing=True
        )
        if not curr_policy:
            raise exceptions.SDKException(
                f"QoS policy {name_or_id} not found."
            )

        return self.network.update_qos_policy(curr_policy, **kwargs)

    def delete_qos_policy(self, name_or_id):
        """Delete a QoS policy.

        :param name_or_id: Name or ID of the policy being deleted.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )
        policy = self.network.find_qos_policy(name_or_id, ignore_missing=True)
        if not policy:
            self.log.debug("QoS policy %s not found for deleting", name_or_id)
            return False

        self.network.delete_qos_policy(policy)

        return True

    # TODO(stephenfin): Deprecate this in favour of the 'list' function
    def search_qos_bandwidth_limit_rules(
        self,
        policy_name_or_id,
        rule_id=None,
        filters=None,
    ):
        """Search QoS bandwidth limit rules

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rules should be associated.
        :param string rule_id: ID of searched rule.
        :param filters: a dict containing additional filters to use. e.g.
            {'max_kbps': 1000}

        :returns: A list of network ``QoSBandwidthLimitRule`` objects matching
            the search criteria.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        rules = self.list_qos_bandwidth_limit_rules(policy_name_or_id, filters)
        return _utils._filter_list(rules, rule_id, filters)

    def list_qos_bandwidth_limit_rules(self, policy_name_or_id, filters=None):
        """List all available QoS bandwidth limit rules.

        :param string policy_name_or_id: Name or ID of the QoS policy from
            from rules should be listed.
        :param filters: (optional) A dict of filter conditions to push down
        :returns: A list of network ``QoSBandwidthLimitRule`` objects.
        :raises: ``:class:`~openstack.exceptions.BadRequestException``` if QoS
            policy will not be found.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        return list(
            self.network.qos_bandwidth_limit_rules(
                qos_policy=policy, **filters
            )
        )

    def get_qos_bandwidth_limit_rule(self, policy_name_or_id, rule_id):
        """Get a QoS bandwidth limit rule by name or ID.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param rule_id: ID of the rule.
        :returns: A network ``QoSBandwidthLimitRule`` object if found, else
            None.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        return self.network.get_qos_bandwidth_limit_rule(rule_id, policy)

    @_utils.valid_kwargs("max_burst_kbps", "direction")
    def create_qos_bandwidth_limit_rule(
        self,
        policy_name_or_id,
        max_kbps,
        **kwargs,
    ):
        """Create a QoS bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param int max_kbps: Maximum bandwidth limit value
            (in kilobits per second).
        :param int max_burst_kbps: Maximum burst value (in kilobits).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be limited.

        :returns: The created network ``QoSBandwidthLimitRule`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        if kwargs.get("direction") is not None:
            if not self._has_neutron_extension('qos-bw-limit-direction'):
                kwargs.pop("direction")
                self.log.debug(
                    "'qos-bw-limit-direction' extension is not available on "
                    "target cloud"
                )

        kwargs['max_kbps'] = max_kbps

        return self.network.create_qos_bandwidth_limit_rule(policy, **kwargs)

    @_utils.valid_kwargs("max_kbps", "max_burst_kbps", "direction")
    def update_qos_bandwidth_limit_rule(
        self, policy_name_or_id, rule_id, **kwargs
    ):
        """Update a QoS bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.
        :param int max_kbps: Maximum bandwidth limit value
            (in kilobits per second).
        :param int max_burst_kbps: Maximum burst value (in kilobits).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be limited.

        :returns: The updated network ``QoSBandwidthLimitRule`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        if kwargs.get("direction") is not None:
            if not self._has_neutron_extension('qos-bw-limit-direction'):
                kwargs.pop("direction")
                self.log.debug(
                    "'qos-bw-limit-direction' extension is not available on "
                    "target cloud"
                )

        if not kwargs:
            self.log.debug("No QoS bandwidth limit rule data to update")
            return

        curr_rule = self.network.get_qos_bandwidth_limit_rule(
            qos_rule=rule_id, qos_policy=policy
        )
        if not curr_rule:
            raise exceptions.SDKException(
                "QoS bandwidth_limit_rule {rule_id} not found in policy "
                "{policy_id}".format(rule_id=rule_id, policy_id=policy['id'])
            )

        return self.network.update_qos_bandwidth_limit_rule(
            qos_rule=curr_rule, qos_policy=policy, **kwargs
        )

    def delete_qos_bandwidth_limit_rule(self, policy_name_or_id, rule_id):
        """Delete a QoS bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.

        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        try:
            self.network.delete_qos_bandwidth_limit_rule(
                rule_id, policy, ignore_missing=False
            )
        except exceptions.NotFoundException:
            self.log.debug(
                "QoS bandwidth limit rule {rule_id} not found in policy "
                "{policy_id}. Ignoring.".format(
                    rule_id=rule_id, policy_id=policy['id']
                )
            )
            return False

        return True

    # TODO(stephenfin): Deprecate this in favour of the 'list' function
    def search_qos_dscp_marking_rules(
        self,
        policy_name_or_id,
        rule_id=None,
        filters=None,
    ):
        """Search QoS DSCP marking rules

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rules should be associated.
        :param string rule_id: ID of searched rule.
        :param filters: a dict containing additional filters to use. e.g.
            {'dscp_mark': 32}

        :returns: A list of network ``QoSDSCPMarkingRule`` objects matching the
            search criteria.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        rules = self.list_qos_dscp_marking_rules(policy_name_or_id, filters)
        return _utils._filter_list(rules, rule_id, filters)

    def list_qos_dscp_marking_rules(self, policy_name_or_id, filters=None):
        """List all available QoS DSCP marking rules.

        :param string policy_name_or_id: Name or ID of the QoS policy from
            from rules should be listed.
        :param filters: (optional) A dict of filter conditions to push down
        :returns: A list of network ``QoSDSCPMarkingRule`` objects.
        :raises: ``:class:`~openstack.exceptions.BadRequestException``` if QoS
            policy will not be found.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        return list(self.network.qos_dscp_marking_rules(policy, **filters))

    def get_qos_dscp_marking_rule(self, policy_name_or_id, rule_id):
        """Get a QoS DSCP marking rule by name or ID.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param rule_id: ID of the rule.
        :returns: A network ``QoSDSCPMarkingRule`` object if found, else None.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        return self.network.get_qos_dscp_marking_rule(rule_id, policy)

    def create_qos_dscp_marking_rule(
        self,
        policy_name_or_id,
        dscp_mark,
    ):
        """Create a QoS DSCP marking rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param int dscp_mark: DSCP mark value

        :returns: The created network ``QoSDSCPMarkingRule`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        return self.network.create_qos_dscp_marking_rule(
            policy, dscp_mark=dscp_mark
        )

    @_utils.valid_kwargs("dscp_mark")
    def update_qos_dscp_marking_rule(
        self, policy_name_or_id, rule_id, **kwargs
    ):
        """Update a QoS DSCP marking rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.
        :param int dscp_mark: DSCP mark value

        :returns: The updated network ``QoSDSCPMarkingRule`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        if not kwargs:
            self.log.debug("No QoS DSCP marking rule data to update")
            return

        curr_rule = self.network.get_qos_dscp_marking_rule(rule_id, policy)
        if not curr_rule:
            raise exceptions.SDKException(
                "QoS dscp_marking_rule {rule_id} not found in policy "
                "{policy_id}".format(rule_id=rule_id, policy_id=policy['id'])
            )

        return self.network.update_qos_dscp_marking_rule(
            curr_rule, policy, **kwargs
        )

    def delete_qos_dscp_marking_rule(self, policy_name_or_id, rule_id):
        """Delete a QoS DSCP marking rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.

        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        try:
            self.network.delete_qos_dscp_marking_rule(
                rule_id, policy, ignore_missing=False
            )
        except exceptions.NotFoundException:
            self.log.debug(
                "QoS DSCP marking rule {rule_id} not found in policy "
                "{policy_id}. Ignoring.".format(
                    rule_id=rule_id, policy_id=policy['id']
                )
            )
            return False

        return True

    # TODO(stephenfin): Deprecate this in favour of the 'list' function
    def search_qos_minimum_bandwidth_rules(
        self,
        policy_name_or_id,
        rule_id=None,
        filters=None,
    ):
        """Search QoS minimum bandwidth rules

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rules should be associated.
        :param string rule_id: ID of searched rule.
        :param filters: a dict containing additional filters to use. e.g.
            {'min_kbps': 1000}

        :returns: A list of network ``QoSMinimumBandwidthRule`` objects
            matching the search criteria.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        rules = self.list_qos_minimum_bandwidth_rules(
            policy_name_or_id, filters
        )
        return _utils._filter_list(rules, rule_id, filters)

    def list_qos_minimum_bandwidth_rules(
        self, policy_name_or_id, filters=None
    ):
        """List all available QoS minimum bandwidth rules.

        :param string policy_name_or_id: Name or ID of the QoS policy from
            from rules should be listed.
        :param filters: (optional) A dict of filter conditions to push down
        :returns: A list of network ``QoSMinimumBandwidthRule`` objects.
        :raises: ``:class:`~openstack.exceptions.BadRequestException``` if QoS
            policy will not be found.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=True
        )
        if not policy:
            raise exceptions.NotFoundException(
                f"QoS policy {policy_name_or_id} not Found."
            )

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        return list(
            self.network.qos_minimum_bandwidth_rules(policy, **filters)
        )

    def get_qos_minimum_bandwidth_rule(self, policy_name_or_id, rule_id):
        """Get a QoS minimum bandwidth rule by name or ID.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param rule_id: ID of the rule.
        :returns: A network ``QoSMinimumBandwidthRule`` object if found, else
            None.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=False
        )

        return self.network.get_qos_minimum_bandwidth_rule(rule_id, policy)

    @_utils.valid_kwargs("direction")
    def create_qos_minimum_bandwidth_rule(
        self,
        policy_name_or_id,
        min_kbps,
        **kwargs,
    ):
        """Create a QoS minimum bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param int min_kbps: Minimum bandwidth value (in kilobits per second).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be available.

        :returns: The created network ``QoSMinimumBandwidthRule`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=False
        )

        kwargs['min_kbps'] = min_kbps

        return self.network.create_qos_minimum_bandwidth_rule(policy, **kwargs)

    @_utils.valid_kwargs("min_kbps", "direction")
    def update_qos_minimum_bandwidth_rule(
        self, policy_name_or_id, rule_id, **kwargs
    ):
        """Update a QoS minimum bandwidth rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.
        :param int min_kbps: Minimum bandwidth value (in kilobits per second).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be available.

        :returns: The updated network ``QoSMinimumBandwidthRule`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=False
        )

        if not kwargs:
            self.log.debug("No QoS minimum bandwidth rule data to update")
            return

        curr_rule = self.network.get_qos_minimum_bandwidth_rule(
            rule_id, policy
        )
        if not curr_rule:
            raise exceptions.SDKException(
                "QoS minimum_bandwidth_rule {rule_id} not found in policy "
                "{policy_id}".format(rule_id=rule_id, policy_id=policy['id'])
            )

        return self.network.update_qos_minimum_bandwidth_rule(
            curr_rule, policy, **kwargs
        )

    def delete_qos_minimum_bandwidth_rule(self, policy_name_or_id, rule_id):
        """Delete a QoS minimum bandwidth rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to delete.

        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud'
            )

        policy = self.network.find_qos_policy(
            policy_name_or_id, ignore_missing=False
        )

        try:
            self.network.delete_qos_minimum_bandwidth_rule(
                rule_id, policy, ignore_missing=False
            )
        except exceptions.NotFoundException:
            self.log.debug(
                "QoS minimum bandwidth rule {rule_id} not found in policy "
                "{policy_id}. Ignoring.".format(
                    rule_id=rule_id, policy_id=policy['id']
                )
            )
            return False

        return True

    def add_router_interface(self, router, subnet_id=None, port_id=None):
        """Attach a subnet to an internal router interface.

        Either a subnet ID or port ID must be specified for the internal
        interface. Supplying both will result in an error.

        :param dict router: The dict object of the router being changed
        :param string subnet_id: The ID of the subnet to use for the interface
        :param string port_id: The ID of the port to use for the interface

        :returns: The raw response body from the request.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        return self.network.add_interface_to_router(
            router=router, subnet_id=subnet_id, port_id=port_id
        )

    def remove_router_interface(self, router, subnet_id=None, port_id=None):
        """Detach a subnet from an internal router interface.

        At least one of subnet_id or port_id must be supplied.

        If you specify both subnet and port ID, the subnet ID must
        correspond to the subnet ID of the first IP address on the port
        specified by the port ID. Otherwise an error occurs.

        :param dict router: The dict object of the router being changed
        :param string subnet_id: The ID of the subnet to use for the interface
        :param string port_id: The ID of the port to use for the interface

        :returns: None on success
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if not subnet_id and not port_id:
            raise ValueError(
                "At least one of subnet_id or port_id must be supplied."
            )

        self.network.remove_interface_from_router(
            router=router, subnet_id=subnet_id, port_id=port_id
        )

    def list_router_interfaces(self, router, interface_type=None):
        """List all interfaces for a router.

        :param dict router: A router dict object.
        :param string interface_type: One of None, "internal", or "external".
            Controls whether all, internal interfaces or external interfaces
            are returned.
        :returns: A list of network ``Port`` objects.
        """
        # Find only router interface and gateway ports, ignore L3 HA ports etc.
        ports = list(self.network.ports(device_id=router['id']))

        router_interfaces = (
            [
                port
                for port in ports
                if (
                    port['device_owner']
                    in [
                        'network:router_interface',
                        'network:router_interface_distributed',
                        'network:ha_router_replicated_interface',
                    ]
                )
            ]
            if not interface_type or interface_type == 'internal'
            else []
        )

        router_gateways = (
            [
                port
                for port in ports
                if port['device_owner'] == 'network:router_gateway'
            ]
            if not interface_type or interface_type == 'external'
            else []
        )

        return router_interfaces + router_gateways

    def create_router(
        self,
        name=None,
        admin_state_up=True,
        ext_gateway_net_id=None,
        enable_snat=None,
        ext_fixed_ips=None,
        project_id=None,
        availability_zone_hints=None,
    ):
        """Create a logical router.

        :param string name: The router name.
        :param bool admin_state_up: The administrative state of the router.
        :param string ext_gateway_net_id: Network ID for the external gateway.
        :param bool enable_snat: Enable Source NAT (SNAT) attribute.
        :param ext_fixed_ips:
            List of dictionaries of desired IP and/or subnet on the
            external network. Example::

              [
                  {
                      "subnet_id": "8ca37218-28ff-41cb-9b10-039601ea7e6b",
                      "ip_address": "192.168.10.2",
                  }
              ]

        :param string project_id: Project ID for the router.
        :param types.ListType availability_zone_hints: A list of availability
            zone hints.

        :returns: The created network ``Router`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        router = {'admin_state_up': admin_state_up}
        if project_id is not None:
            router['project_id'] = project_id
        if name:
            router['name'] = name
        ext_gw_info = self._build_external_gateway_info(
            ext_gateway_net_id, enable_snat, ext_fixed_ips
        )
        if ext_gw_info:
            router['external_gateway_info'] = ext_gw_info
        if availability_zone_hints is not None:
            if not isinstance(availability_zone_hints, list):
                raise exceptions.SDKException(
                    "Parameter 'availability_zone_hints' must be a list"
                )
            if not self._has_neutron_extension('router_availability_zone'):
                raise exc.OpenStackCloudUnavailableExtension(
                    'router_availability_zone extension is not available on '
                    'target cloud'
                )
            router['availability_zone_hints'] = availability_zone_hints

        return self.network.create_router(**router)

    def update_router(
        self,
        name_or_id,
        name=None,
        admin_state_up=None,
        ext_gateway_net_id=None,
        enable_snat=None,
        ext_fixed_ips=None,
        routes=None,
    ):
        """Update an existing logical router.

        :param string name_or_id: The name or UUID of the router to update.
        :param string name: The new router name.
        :param bool admin_state_up: The administrative state of the router.
        :param string ext_gateway_net_id:
            The network ID for the external gateway.
        :param bool enable_snat: Enable Source NAT (SNAT) attribute.
        :param ext_fixed_ips:
            List of dictionaries of desired IP and/or subnet on the
            external network. Example::

              [
                  {
                      "subnet_id": "8ca37218-28ff-41cb-9b10-039601ea7e6b",
                      "ip_address": "192.168.10.2",
                  }
              ]

        :param list routes:
            A list of dictionaries with destination and nexthop parameters. To
            clear all routes pass an empty list ([]).

            Example::

              [{"destination": "179.24.1.0/24", "nexthop": "172.24.3.99"}]

        :returns: The updated network ``Router`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        router = {}
        if name:
            router['name'] = name
        if admin_state_up is not None:
            router['admin_state_up'] = admin_state_up
        ext_gw_info = self._build_external_gateway_info(
            ext_gateway_net_id, enable_snat, ext_fixed_ips
        )
        if ext_gw_info:
            router['external_gateway_info'] = ext_gw_info

        if routes is not None:
            if self._has_neutron_extension('extraroute'):
                router['routes'] = routes
            else:
                self.log.warning(
                    'extra routes extension is not available on target cloud'
                )

        if not router:
            self.log.debug("No router data to update")
            return

        curr_router = self.get_router(name_or_id)
        if not curr_router:
            raise exceptions.SDKException(f"Router {name_or_id} not found.")

        return self.network.update_router(curr_router, **router)

    def delete_router(self, name_or_id):
        """Delete a logical router.

        If a name, instead of a unique UUID, is supplied, it is possible
        that we could find more than one matching router since names are
        not required to be unique. An error will be raised in this case.

        :param name_or_id: Name or ID of the router being deleted.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        router = self.network.find_router(name_or_id, ignore_missing=True)
        if not router:
            self.log.debug("Router %s not found for deleting", name_or_id)
            return False

        self.network.delete_router(router)

        return True

    def create_subnet(
        self,
        network_name_or_id,
        cidr=None,
        ip_version=4,
        enable_dhcp=False,
        subnet_name=None,
        tenant_id=None,
        allocation_pools=None,
        gateway_ip=None,
        disable_gateway_ip=False,
        dns_nameservers=None,
        host_routes=None,
        ipv6_ra_mode=None,
        ipv6_address_mode=None,
        prefixlen=None,
        use_default_subnetpool=False,
        subnetpool_name_or_id=None,
        **kwargs,
    ):
        """Create a subnet on a specified network.

        :param string network_name_or_id: The unique name or ID of the attached
            network. If a non-unique name is supplied, an exception is raised.
        :param string cidr: The CIDR.  Only one of ``cidr``,
            ``use_default_subnetpool`` and ``subnetpool_name_or_id`` may be
            specified at the same time.
        :param int ip_version: The IP version, which is 4 or 6.
        :param bool enable_dhcp: Set to ``True`` if DHCP is enabled and
            ``False`` if disabled. Default is ``False``.
        :param string subnet_name: The name of the subnet.
        :param string tenant_id: The ID of the tenant who owns the network.
            Only administrative users can specify a tenant ID other than their
            own.
        :param allocation_pools: A list of dictionaries of the start and end
            addresses for the allocation pools. For example::

                [{"start": "192.168.199.2", "end": "192.168.199.254"}]

        :param string gateway_ip: The gateway IP address. When you specify both
            allocation_pools and gateway_ip, you must ensure that the gateway
            IP does not overlap with the specified allocation pools.
        :param bool disable_gateway_ip: Set to ``True`` if gateway IP address
            is disabled and ``False`` if enabled. It is not allowed with
            gateway_ip. Default is ``False``.
        :param dns_nameservers: A list of DNS name servers for the subnet. For
            example::

              ["8.8.8.7", "8.8.8.8"]

        :param host_routes: A list of host route dictionaries for the subnet.
            For example::

              [
                  {"destination": "0.0.0.0/0", "nexthop": "123.456.78.9"},
                  {"destination": "192.168.0.0/24", "nexthop": "192.168.0.1"},
              ]

        :param string ipv6_ra_mode: IPv6 Router Advertisement mode. Valid
            values are: 'dhcpv6-stateful', 'dhcpv6-stateless', or 'slaac'.
        :param string ipv6_address_mode: IPv6 address mode. Valid values are:
            'dhcpv6-stateful', 'dhcpv6-stateless', or 'slaac'.
        :param string prefixlen: The prefix length to use for subnet allocation
            from a subnetpool.
        :param bool use_default_subnetpool: Use the default subnetpool for
            ``ip_version`` to obtain a CIDR. Only one of ``cidr``,
            ``use_default_subnetpool`` and ``subnetpool_name_or_id`` may be
            specified at the same time.
        :param string subnetpool_name_or_id: The unique name or id of the
            subnetpool to obtain a CIDR from. Only one of ``cidr``,
            ``use_default_subnetpool`` and ``subnetpool_name_or_id`` may be
            specified at the same time.
        :param kwargs: Key value pairs to be passed to the Neutron API.

        :returns: The created network ``Subnet`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """

        if tenant_id is not None:
            filters = {'tenant_id': tenant_id}
        else:
            filters = None

        network = self.get_network(network_name_or_id, filters)
        if not network:
            raise exceptions.SDKException(
                f"Network {network_name_or_id} not found."
            )

        if disable_gateway_ip and gateway_ip:
            raise exceptions.SDKException(
                'arg:disable_gateway_ip is not allowed with arg:gateway_ip'
            )

        uses_subnetpool = use_default_subnetpool or subnetpool_name_or_id
        if not cidr and not uses_subnetpool:
            raise exceptions.SDKException(
                'arg:cidr is required when a subnetpool is not used'
            )

        if cidr and uses_subnetpool:
            raise exceptions.SDKException(
                'arg:cidr and subnetpool may not be used at the same time'
            )

        if use_default_subnetpool and subnetpool_name_or_id:
            raise exceptions.SDKException(
                'arg:use_default_subnetpool and arg:subnetpool_id may not be '
                'used at the same time'
            )

        subnetpool = None
        if subnetpool_name_or_id:
            subnetpool = self.get_subnetpool(subnetpool_name_or_id)
            if not subnetpool:
                raise exceptions.SDKException(
                    f"Subnetpool {subnetpool_name_or_id} not found."
                )

        # Be friendly on ip_version and allow strings
        if isinstance(ip_version, str):
            try:
                ip_version = int(ip_version)
            except ValueError:
                raise exceptions.SDKException('ip_version must be an integer')

        # The body of the neutron message for the subnet we wish to create.
        # This includes attributes that are required or have defaults.
        subnet = dict(
            {
                'network_id': network['id'],
                'ip_version': ip_version,
                'enable_dhcp': enable_dhcp,
            },
            **kwargs,
        )

        # Add optional attributes to the message.
        if cidr:
            subnet['cidr'] = cidr
        if subnet_name:
            subnet['name'] = subnet_name
        if tenant_id:
            subnet['tenant_id'] = tenant_id
        if allocation_pools:
            subnet['allocation_pools'] = allocation_pools
        if gateway_ip:
            subnet['gateway_ip'] = gateway_ip
        if disable_gateway_ip:
            subnet['gateway_ip'] = None
        if dns_nameservers:
            subnet['dns_nameservers'] = dns_nameservers
        if host_routes:
            subnet['host_routes'] = host_routes
        if ipv6_ra_mode:
            subnet['ipv6_ra_mode'] = ipv6_ra_mode
        if ipv6_address_mode:
            subnet['ipv6_address_mode'] = ipv6_address_mode
        if prefixlen:
            subnet['prefixlen'] = prefixlen
        if use_default_subnetpool:
            subnet['use_default_subnetpool'] = True
        if subnetpool:
            subnet['subnetpool_id'] = subnetpool["id"]

        return self.network.create_subnet(**subnet)

    def delete_subnet(self, name_or_id):
        """Delete a subnet.

        If a name, instead of a unique UUID, is supplied, it is possible
        that we could find more than one matching subnet since names are
        not required to be unique. An error will be raised in this case.

        :param name_or_id: Name or ID of the subnet being deleted.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        subnet = self.network.find_subnet(name_or_id, ignore_missing=True)
        if not subnet:
            self.log.debug("Subnet %s not found for deleting", name_or_id)
            return False

        self.network.delete_subnet(subnet)

        return True

    def update_subnet(
        self,
        name_or_id,
        subnet_name=None,
        enable_dhcp=None,
        gateway_ip=None,
        disable_gateway_ip=None,
        allocation_pools=None,
        dns_nameservers=None,
        host_routes=None,
    ):
        """Update an existing subnet.

        :param string name_or_id: Name or ID of the subnet to update.
        :param string subnet_name: The new name of the subnet.
        :param bool enable_dhcp: Set to ``True`` if DHCP is enabled and
            ``False`` if disabled.
        :param string gateway_ip: The gateway IP address. When you specify both
            allocation_pools and gateway_ip, you must ensure that the gateway
            IP does not overlap with the specified allocation pools.
        :param bool disable_gateway_ip: Set to ``True`` if gateway IP address
            is disabled and ``False`` if enabled. It is not allowed with
            gateway_ip. Default is ``False``.
        :param allocation_pools: A list of dictionaries of the start and end
            addresses for the allocation pools. For example::

              [{"start": "192.168.199.2", "end": "192.168.199.254"}]

        :param dns_nameservers: A list of DNS name servers for the subnet. For
            example::

              ["8.8.8.7", "8.8.8.8"]

        :param host_routes: A list of host route dictionaries for the subnet.
            For example::

              [
                  {"destination": "0.0.0.0/0", "nexthop": "123.456.78.9"},
                  {"destination": "192.168.0.0/24", "nexthop": "192.168.0.1"},
              ]

        :returns: The updated network ``Subnet`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        subnet = {}
        if subnet_name:
            subnet['name'] = subnet_name
        if enable_dhcp is not None:
            subnet['enable_dhcp'] = enable_dhcp
        if gateway_ip:
            subnet['gateway_ip'] = gateway_ip
        if disable_gateway_ip:
            subnet['gateway_ip'] = None
        if allocation_pools:
            subnet['allocation_pools'] = allocation_pools
        if dns_nameservers:
            subnet['dns_nameservers'] = dns_nameservers
        if host_routes:
            subnet['host_routes'] = host_routes

        if not subnet:
            self.log.debug("No subnet data to update")
            return

        if disable_gateway_ip and gateway_ip:
            raise exceptions.SDKException(
                'arg:disable_gateway_ip is not allowed with arg:gateway_ip'
            )

        curr_subnet = self.get_subnet(name_or_id)
        if not curr_subnet:
            raise exceptions.SDKException(f"Subnet {name_or_id} not found.")

        return self.network.update_subnet(curr_subnet, **subnet)

    @_utils.valid_kwargs(
        'name',
        'admin_state_up',
        'mac_address',
        'fixed_ips',
        'subnet_id',
        'ip_address',
        'security_groups',
        'allowed_address_pairs',
        'extra_dhcp_opts',
        'device_owner',
        'device_id',
        'binding:vnic_type',
        'binding:profile',
        'port_security_enabled',
        'qos_policy_id',
        'binding:host_id',
        'project_id',
        'description',
        'dns_domain',
        'dns_name',
        'numa_affinity_policy',
        'propagate_uplink_status',
        'mac_learning_enabled',
    )
    def create_port(self, network_id, **kwargs):
        """Create a port

        :param network_id: The ID of the network. (Required)
        :param name: A symbolic name for the port. (Optional)
        :param admin_state_up: The administrative status of the port,
            which is up (true, default) or down (false). (Optional)
        :param mac_address: The MAC address. (Optional)
        :param fixed_ips: List of ip_addresses and subnet_ids. See subnet_id
            and ip_address. (Optional) For example::

              [
                  {
                      "ip_address": "10.29.29.13",
                      "subnet_id": "a78484c4-c380-4b47-85aa-21c51a2d8cbd",
                  },
                  ...,
              ]

        :param subnet_id: If you specify only a subnet ID, OpenStack Networking
            allocates an available IP from that subnet to the port. (Optional)
            If you specify both a subnet ID and an IP address, OpenStack
            Networking tries to allocate the specified address to the port.
        :param ip_address: If you specify both a subnet ID and an IP address,
            OpenStack Networking tries to allocate the specified address to
            the port.
        :param security_groups: List of security group UUIDs. (Optional)
        :param allowed_address_pairs: Allowed address pairs list (Optional)
            For example::

              [
                  {
                      "ip_address": "23.23.23.1",
                      "mac_address": "fa:16:3e:c4:cd:3f",
                  },
                  ...,
              ]

        :param extra_dhcp_opts: Extra DHCP options. (Optional).
            For example::

              [{"opt_name": "opt name1", "opt_value": "value1"}, ...]

        :param device_owner: The ID of the entity that uses this port.
            For example, a DHCP agent.  (Optional)
        :param device_id: The ID of the device that uses this port.
            For example, a virtual server. (Optional)
        :param binding vnic_type: The type of the created port. (Optional)
        :param port_security_enabled: The security port state created on
            the network. (Optional)
        :param qos_policy_id: The ID of the QoS policy to apply for
            port. (Optional)
        :param project_id: The project in which to create the port. (Optional)
        :param description: Description of the port. (Optional)
        :param dns_domain: DNS domain relevant for the port. (Optional)
        :param dns_name: DNS name of the port. (Optional)
        :param numa_affinity_policy: the numa affinitiy policy. May be
            "None", "required", "preferred" or "legacy". (Optional)
        :param propagate_uplink_status: If the uplink status of the port should
            be propagated. (Optional)
        :param mac_learning_enabled: If mac learning should be enabled on the
            port. (Optional)

        :returns: The created network ``Port`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        kwargs['network_id'] = network_id

        return self.network.create_port(**kwargs)

    @_utils.valid_kwargs(
        'name',
        'admin_state_up',
        'fixed_ips',
        'security_groups',
        'allowed_address_pairs',
        'extra_dhcp_opts',
        'device_owner',
        'device_id',
        'binding:vnic_type',
        'binding:profile',
        'port_security_enabled',
        'qos_policy_id',
        'binding:host_id',
    )
    def update_port(self, name_or_id, **kwargs):
        """Update a port

        Note: to unset an attribute use None value. To leave an attribute
        untouched just omit it.

        :param name_or_id: name or ID of the port to update. (Required)
        :param name: A symbolic name for the port. (Optional)
        :param admin_state_up: The administrative status of the port,
            which is up (true) or down (false). (Optional)
        :param fixed_ips: List of ip_addresses and subnet_ids. (Optional)
            If you specify only a subnet ID, OpenStack Networking allocates
            an available IP from that subnet to the port.
            If you specify both a subnet ID and an IP address, OpenStack
            Networking tries to allocate the specified address to the port.
            For example::

              [
                  {
                      "ip_address": "10.29.29.13",
                      "subnet_id": "a78484c4-c380-4b47-85aa-21c51a2d8cbd",
                  },
                  ...,
              ]

        :param security_groups: List of security group UUIDs. (Optional)
        :param allowed_address_pairs: Allowed address pairs list (Optional)
            For example::

              [
                  {
                      "ip_address": "23.23.23.1",
                      "mac_address": "fa:16:3e:c4:cd:3f",
                  },
                  ...,
              ]

        :param extra_dhcp_opts: Extra DHCP options. (Optional).
            For example::

              [{"opt_name": "opt name1", "opt_value": "value1"}, ...]

        :param device_owner: The ID of the entity that uses this port.
            For example, a DHCP agent.  (Optional)
        :param device_id: The ID of the resource this port is attached to.
        :param binding vnic_type: The type of the created port. (Optional)
        :param port_security_enabled: The security port state created on
            the network. (Optional)
        :param qos_policy_id: The ID of the QoS policy to apply for port.

        :returns: The updated network ``Port`` object.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        port = self.get_port(name_or_id=name_or_id)
        if port is None:
            raise exceptions.SDKException(
                f"failed to find port '{name_or_id}'"
            )

        return self.network.update_port(port, **kwargs)

    def delete_port(self, name_or_id):
        """Delete a port

        :param name_or_id: ID or name of the port to delete.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        port = self.network.find_port(name_or_id, ignore_missing=True)
        if port is None:
            self.log.debug("Port %s not found for deleting", name_or_id)
            return False

        self.network.delete_port(port)

        return True

    def _get_port_ids(self, name_or_id_list, filters=None):
        """
        Takes a list of port names or ids, retrieves ports and returns a list
        with port ids only.

        :param list[str] name_or_id_list: list of port names or ids
        :param dict filters: optional filters
        :raises: SDKException on multiple matches
        :raises: NotFoundException if a port is not found
        :return: list of port ids
        :rtype: list[str]
        """
        ids_list = []
        for name_or_id in name_or_id_list:
            port = self.get_port(name_or_id, filters)
            if not port:
                raise exceptions.NotFoundException(
                    f'Port {name_or_id} not found'
                )
            ids_list.append(port['id'])
        return ids_list

    def _build_external_gateway_info(
        self, ext_gateway_net_id, enable_snat, ext_fixed_ips
    ):
        info = {}
        if ext_gateway_net_id:
            info['network_id'] = ext_gateway_net_id
        # Only send enable_snat if it is explicitly set.
        if enable_snat is not None:
            info['enable_snat'] = enable_snat
        if ext_fixed_ips:
            info['external_fixed_ips'] = ext_fixed_ips
        if info:
            return info
        return None
