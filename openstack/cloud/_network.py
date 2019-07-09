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

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import six
import time
import threading
import types  # noqa

from openstack.cloud import exc
from openstack.cloud import _normalize
from openstack.cloud import _utils
from openstack import exceptions
from openstack import proxy


class NetworkCloudMixin(_normalize.Normalizer):

    def __init__(self):
        self._ports = None
        self._ports_time = 0
        self._ports_lock = threading.Lock()

    @_utils.cache_on_arguments()
    def _neutron_extensions(self):
        extensions = set()
        resp = self.network.get('/extensions.json')
        data = proxy._json_response(
            resp,
            error_message="Error fetching extension list for neutron")
        for extension in self._get_and_munchify('extensions', data):
            extensions.add(extension['alias'])
        return extensions

    def _has_neutron_extension(self, extension_alias):
        return extension_alias in self._neutron_extensions()

    def search_networks(self, name_or_id=None, filters=None):
        """Search networks

        :param name_or_id: Name or ID of the desired network.
        :param filters: a dict containing additional filters to use. e.g.
                        {'router:external': True}

        :returns: a list of ``munch.Munch`` containing the network description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        networks = self.list_networks(
            filters if isinstance(filters, dict) else None)
        return _utils._filter_list(networks, name_or_id, filters)

    def search_routers(self, name_or_id=None, filters=None):
        """Search routers

        :param name_or_id: Name or ID of the desired router.
        :param filters: a dict containing additional filters to use. e.g.
                        {'admin_state_up': True}

        :returns: a list of ``munch.Munch`` containing the router description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        routers = self.list_routers(
            filters if isinstance(filters, dict) else None)
        return _utils._filter_list(routers, name_or_id, filters)

    def search_subnets(self, name_or_id=None, filters=None):
        """Search subnets

        :param name_or_id: Name or ID of the desired subnet.
        :param filters: a dict containing additional filters to use. e.g.
                        {'enable_dhcp': True}

        :returns: a list of ``munch.Munch`` containing the subnet description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        subnets = self.list_subnets(
            filters if isinstance(filters, dict) else None)
        return _utils._filter_list(subnets, name_or_id, filters)

    def search_ports(self, name_or_id=None, filters=None):
        """Search ports

        :param name_or_id: Name or ID of the desired port.
        :param filters: a dict containing additional filters to use. e.g.
                        {'device_id': '2711c67a-b4a7-43dd-ace7-6187b791c3f0'}

        :returns: a list of ``munch.Munch`` containing the port description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        # If port caching is enabled, do not push the filter down to
        # neutron; get all the ports (potentially from the cache) and
        # filter locally.
        if self._PORT_AGE or isinstance(filters, str):
            pushdown_filters = None
        else:
            pushdown_filters = filters
        ports = self.list_ports(pushdown_filters)
        return _utils._filter_list(ports, name_or_id, filters)

    def list_networks(self, filters=None):
        """List all available networks.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of ``munch.Munch`` containing network info.

        """
        # If the cloud is running nova-network, just return an empty list.
        if not self.has_service('network'):
            return []
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        data = self.network.get("/networks.json", params=filters)
        return self._get_and_munchify('networks', data)

    def list_routers(self, filters=None):
        """List all available routers.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of router ``munch.Munch``.

        """
        # If the cloud is running nova-network, just return an empty list.
        if not self.has_service('network'):
            return []
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        resp = self.network.get("/routers.json", params=filters)
        data = proxy._json_response(
            resp,
            error_message="Error fetching router list")
        return self._get_and_munchify('routers', data)

    def list_subnets(self, filters=None):
        """List all available subnets.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of subnet ``munch.Munch``.

        """
        # If the cloud is running nova-network, just return an empty list.
        if not self.has_service('network'):
            return []
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        data = self.network.get("/subnets.json", params=filters)
        return self._get_and_munchify('subnets', data)

    def list_ports(self, filters=None):
        """List all available ports.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of port ``munch.Munch``.

        """
        # If pushdown filters are specified and we do not have batched caching
        # enabled, bypass local caching and push down the filters.
        if filters and self._PORT_AGE == 0:
            return self._list_ports(filters)

        if (time.time() - self._ports_time) >= self._PORT_AGE:
            # Since we're using cached data anyway, we don't need to
            # have more than one thread actually submit the list
            # ports task.  Let the first one submit it while holding
            # a lock, and the non-blocking acquire method will cause
            # subsequent threads to just skip this and use the old
            # data until it succeeds.
            # Initially when we never got data, block to retrieve some data.
            first_run = self._ports is None
            if self._ports_lock.acquire(first_run):
                try:
                    if not (first_run and self._ports is not None):
                        self._ports = self._list_ports({})
                        self._ports_time = time.time()
                finally:
                    self._ports_lock.release()
        # Wrap the return with filter_list so that if filters were passed
        # but we were batching/caching and thus always fetching the whole
        # list from the cloud, we still return a filtered list.
        return _utils._filter_list(self._ports, None, filters or {})

    def _list_ports(self, filters):
        # If the cloud is running nova-network, just return an empty list.
        if not self.has_service('network'):
            return []
        resp = self.network.get("/ports.json", params=filters)
        data = proxy._json_response(
            resp,
            error_message="Error fetching port list")
        return self._get_and_munchify('ports', data)

    def get_qos_policy(self, name_or_id, filters=None):
        """Get a QoS policy by name or ID.

        :param name_or_id: Name or ID of the policy.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A policy ``munch.Munch`` or None if no matching network is
                 found.

        """
        return _utils._get_entity(
            self, 'qos_policie', name_or_id, filters)

    def search_qos_policies(self, name_or_id=None, filters=None):
        """Search QoS policies

        :param name_or_id: Name or ID of the desired policy.
        :param filters: a dict containing additional filters to use. e.g.
                        {'shared': True}

        :returns: a list of ``munch.Munch`` containing the network description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        policies = self.list_qos_policies(filters)
        return _utils._filter_list(policies, name_or_id, filters)

    def list_qos_rule_types(self, filters=None):
        """List all available QoS rule types.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of rule types ``munch.Munch``.

        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        resp = self.network.get("/qos/rule-types.json", params=filters)
        data = proxy._json_response(
            resp,
            error_message="Error fetching QoS rule types list")
        return self._get_and_munchify('rule_types', data)

    def get_qos_rule_type_details(self, rule_type, filters=None):
        """Get a QoS rule type details by rule type name.

        :param string rule_type: Name of the QoS rule type.

        :returns: A rule type details ``munch.Munch`` or None if
            no matching rule type is found.

        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        if not self._has_neutron_extension('qos-rule-type-details'):
            raise exc.OpenStackCloudUnavailableExtension(
                'qos-rule-type-details extension is not available '
                'on target cloud')

        resp = self.network.get(
            "/qos/rule-types/{rule_type}.json".format(rule_type=rule_type))
        data = proxy._json_response(
            resp,
            error_message="Error fetching QoS details of {rule_type} "
                          "rule type".format(rule_type=rule_type))
        return self._get_and_munchify('rule_type', data)

    def list_qos_policies(self, filters=None):
        """List all available QoS policies.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of policies ``munch.Munch``.

        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        resp = self.network.get("/qos/policies.json", params=filters)
        data = proxy._json_response(
            resp,
            error_message="Error fetching QoS policies list")
        return self._get_and_munchify('policies', data)

    def get_network(self, name_or_id, filters=None):
        """Get a network by name or ID.

        :param name_or_id: Name or ID of the network.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A network ``munch.Munch`` or None if no matching network is
                 found.

        """
        return _utils._get_entity(self, 'network', name_or_id, filters)

    def get_network_by_id(self, id):
        """ Get a network by ID

        :param id: ID of the network.
        :returns: A network ``munch.Munch``.
        """
        resp = self.network.get('/networks/{id}'.format(id=id))
        data = proxy._json_response(
            resp,
            error_message="Error getting network with ID {id}".format(id=id)
        )
        network = self._get_and_munchify('network', data)

        return network

    def get_router(self, name_or_id, filters=None):
        """Get a router by name or ID.

        :param name_or_id: Name or ID of the router.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A router ``munch.Munch`` or None if no matching router is
                  found.

        """
        return _utils._get_entity(self, 'router', name_or_id, filters)

    def get_subnet(self, name_or_id, filters=None):
        """Get a subnet by name or ID.

        :param name_or_id: Name or ID of the subnet.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

        :returns: A subnet ``munch.Munch`` or None if no matching subnet is
                  found.

        """
        return _utils._get_entity(self, 'subnet', name_or_id, filters)

    def get_subnet_by_id(self, id):
        """ Get a subnet by ID

        :param id: ID of the subnet.
        :returns: A subnet ``munch.Munch``.
        """
        resp = self.network.get('/subnets/{id}'.format(id=id))
        data = proxy._json_response(
            resp,
            error_message="Error getting subnet with ID {id}".format(id=id)
        )
        subnet = self._get_and_munchify('subnet', data)

        return subnet

    def get_port(self, name_or_id, filters=None):
        """Get a port by name or ID.

        :param name_or_id: Name or ID of the port.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A port ``munch.Munch`` or None if no matching port is found.

        """
        return _utils._get_entity(self, 'port', name_or_id, filters)

    def get_port_by_id(self, id):
        """ Get a port by ID

        :param id: ID of the port.
        :returns: A port ``munch.Munch``.
        """
        resp = self.network.get('/ports/{id}'.format(id=id))
        data = proxy._json_response(
            resp,
            error_message="Error getting port with ID {id}".format(id=id)
        )
        port = self._get_and_munchify('port', data)

        return port

    def create_network(self, name, shared=False, admin_state_up=True,
                       external=False, provider=None, project_id=None,
                       availability_zone_hints=None,
                       port_security_enabled=None,
                       mtu_size=None, dns_domain=None):
        """Create a network.

        :param string name: Name of the network being created.
        :param bool shared: Set the network as shared.
        :param bool admin_state_up: Set the network administrative state to up.
        :param bool external: Whether this network is externally accessible.
        :param dict provider: A dict of network provider options. Example::

           { 'network_type': 'vlan', 'segmentation_id': 'vlan1' }
        :param string project_id: Specify the project ID this network
            will be created on (admin-only).
        :param types.ListType availability_zone_hints: A list of availability
            zone hints.
        :param bool port_security_enabled: Enable / Disable port security
        :param int mtu_size: maximum transmission unit value to address
            fragmentation. Minimum value is 68 for IPv4, and 1280 for IPv6.
        :param string dns_domain: Specify the DNS domain associated with
            this network.

        :returns: The network object.
        :raises: OpenStackCloudException on operation error.
        """
        network = {
            'name': name,
            'admin_state_up': admin_state_up,
        }

        if shared:
            network['shared'] = shared

        if project_id is not None:
            network['tenant_id'] = project_id

        if availability_zone_hints is not None:
            if not isinstance(availability_zone_hints, list):
                raise exc.OpenStackCloudException(
                    "Parameter 'availability_zone_hints' must be a list")
            if not self._has_neutron_extension('network_availability_zone'):
                raise exc.OpenStackCloudUnavailableExtension(
                    'network_availability_zone extension is not available on '
                    'target cloud')
            network['availability_zone_hints'] = availability_zone_hints

        if provider:
            if not isinstance(provider, dict):
                raise exc.OpenStackCloudException(
                    "Parameter 'provider' must be a dict")
            # Only pass what we know
            for attr in ('physical_network', 'network_type',
                         'segmentation_id'):
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
                raise exc.OpenStackCloudException(
                    "Parameter 'port_security_enabled' must be a bool")
            network['port_security_enabled'] = port_security_enabled

        if mtu_size:
            if not isinstance(mtu_size, int):
                raise exc.OpenStackCloudException(
                    "Parameter 'mtu_size' must be an integer.")
            if not mtu_size >= 68:
                raise exc.OpenStackCloudException(
                    "Parameter 'mtu_size' must be greater than 67.")

            network['mtu'] = mtu_size

        if dns_domain:
            network['dns_domain'] = dns_domain

        data = self.network.post("/networks.json", json={'network': network})

        # Reset cache so the new network is picked up
        self._reset_network_caches()
        return self._get_and_munchify('network', data)

    @_utils.valid_kwargs("name", "shared", "admin_state_up", "external",
                         "provider", "mtu_size", "port_security_enabled",
                         "dns_domain")
    def update_network(self, name_or_id, **kwargs):
        """Update a network.

        :param string name_or_id: Name or ID of the network being updated.
        :param string name: New name of the network.
        :param bool shared: Set the network as shared.
        :param bool admin_state_up: Set the network administrative state to up.
        :param bool external: Whether this network is externally accessible.
        :param dict provider: A dict of network provider options. Example::

           { 'network_type': 'vlan', 'segmentation_id': 'vlan1' }
        :param int mtu_size: New maximum transmission unit value to address
            fragmentation. Minimum value is 68 for IPv4, and 1280 for IPv6.
        :param bool port_security_enabled: Enable or disable port security.
        :param string dns_domain: Specify the DNS domain associated with
            this network.

        :returns: The updated network object.
        :raises: OpenStackCloudException on operation error.
        """
        if 'provider' in kwargs:
            if not isinstance(kwargs['provider'], dict):
                raise exc.OpenStackCloudException(
                    "Parameter 'provider' must be a dict")
            # Only pass what we know
            provider = {}
            for key in kwargs['provider']:
                if key in ('physical_network', 'network_type',
                           'segmentation_id'):
                    provider['provider:' + key] = kwargs['provider'][key]
            kwargs['provider'] = provider

        if 'external' in kwargs:
            kwargs['router:external'] = kwargs.pop('external')

        if 'port_security_enabled' in kwargs:
            if not isinstance(kwargs['port_security_enabled'], bool):
                raise exc.OpenStackCloudException(
                    "Parameter 'port_security_enabled' must be a bool")

        if 'mtu_size' in kwargs:
            if not isinstance(kwargs['mtu_size'], int):
                raise exc.OpenStackCloudException(
                    "Parameter 'mtu_size' must be an integer.")
            if kwargs['mtu_size'] < 68:
                raise exc.OpenStackCloudException(
                    "Parameter 'mtu_size' must be greater than 67.")
            kwargs['mtu'] = kwargs.pop('mtu_size')

        network = self.get_network(name_or_id)
        if not network:
            raise exc.OpenStackCloudException(
                "Network %s not found." % name_or_id)

        data = proxy._json_response(self.network.put(
            "/networks/{net_id}.json".format(net_id=network.id),
            json={"network": kwargs}),
            error_message="Error updating network {0}".format(name_or_id))

        self._reset_network_caches()

        return self._get_and_munchify('network', data)

    def delete_network(self, name_or_id):
        """Delete a network.

        :param name_or_id: Name or ID of the network being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        network = self.get_network(name_or_id)
        if not network:
            self.log.debug("Network %s not found for deleting", name_or_id)
            return False

        exceptions.raise_from_response(self.network.delete(
            "/networks/{network_id}.json".format(network_id=network['id'])))

        # Reset cache so the deleted network is removed
        self._reset_network_caches()

        return True

    def set_network_quotas(self, name_or_id, **kwargs):
        """ Set a network quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: OpenStackCloudException if the resource to set the
            quota does not exist.
        """

        proj = self.get_project(name_or_id)
        if not proj:
            raise exc.OpenStackCloudException("project does not exist")

        exceptions.raise_from_response(
            self.network.put(
                '/quotas/{project_id}.json'.format(project_id=proj.id),
                json={'quota': kwargs}),
            error_message=("Error setting Neutron's quota for "
                           "project {0}".format(proj.id)))

    def get_network_quotas(self, name_or_id, details=False):
        """ Get network quotas for a project

        :param name_or_id: project name or id
        :param details: if set to True it will return details about usage
                        of quotas by given project
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise exc.OpenStackCloudException("project does not exist")
        url = '/quotas/{project_id}'.format(project_id=proj.id)
        if details:
            url = url + "/details"
        url = url + ".json"
        data = proxy._json_response(
            self.network.get(url),
            error_message=("Error fetching Neutron's quota for "
                           "project {0}".format(proj.id)))
        return self._get_and_munchify('quota', data)

    def get_network_extensions(self):
        """Get Cloud provided network extensions

        :returns: set of Neutron extension aliases
        """
        return self._neutron_extensions()

    def delete_network_quotas(self, name_or_id):
        """ Delete network quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project or the
                 network client call failed

        :returns: dict with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise exc.OpenStackCloudException("project does not exist")
        exceptions.raise_from_response(
            self.network.delete(
                '/quotas/{project_id}.json'.format(project_id=proj.id)),
            error_message=("Error deleting Neutron's quota for "
                           "project {0}".format(proj.id)))

    @_utils.valid_kwargs(
        'action', 'description', 'destination_firewall_group_id',
        'destination_ip_address', 'destination_port', 'enabled', 'ip_version',
        'name', 'project_id', 'protocol', 'shared', 'source_firewall_group_id',
        'source_ip_address', 'source_port')
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
                             without disassociating them from firewall
                             policies. Defaults to True.
        :param int ip_version: IP Version.
                           Valid values: 4, 6
                           Defaults to 4.
        :param name: Human-readable name.
        :param project_id: Project id.
        :param protocol: IP protocol.
                         Valid values: icmp, tcp, udp, null
        :param bool shared: Visibility to other projects.
                       Defaults to False.
        :param source_firewall_group_id: ID of source firewall group.
        :param source_ip_address: IPv4-, IPv6 address or CIDR.
        :param source_port: Port or port range (e.g. 80:90)
        :raises: BadRequestException if parameters are malformed
        :return: created firewall rule
        :rtype: FirewallRule
        """
        return self.network.create_firewall_rule(**kwargs)

    def delete_firewall_rule(self, name_or_id, filters=None):
        """
        Deletes firewall rule.
        Prints debug message in case to-be-deleted resource was not found.

        :param name_or_id: firewall rule name or id
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :return: True if resource is successfully deleted, False otherwise.
        :rtype: bool
        """
        if not filters:
            filters = {}
        try:
            firewall_rule = self.network.find_firewall_rule(
                name_or_id, ignore_missing=False, **filters)
            self.network.delete_firewall_rule(firewall_rule,
                                              ignore_missing=False)
        except exceptions.ResourceNotFound:
            self.log.debug('Firewall rule %s not found for deleting',
                           name_or_id)
            return False
        return True

    def get_firewall_rule(self, name_or_id, filters=None):
        """
        Retrieves a single firewall rule.

        :param name_or_id: firewall rule name or id
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :return: firewall rule dict or None if not found
        :rtype: FirewallRule
        """
        if not filters:
            filters = {}
        return self.network.find_firewall_rule(name_or_id, **filters)

    def list_firewall_rules(self, filters=None):
        """
        Lists firewall rules.

        :param dict filters: optional filters
        :return: list of firewall rules
        :rtype: list[FirewallRule]
        """
        if not filters:
            filters = {}
        return list(self.network.firewall_rules(**filters))

    @_utils.valid_kwargs(
        'action', 'description', 'destination_firewall_group_id',
        'destination_ip_address', 'destination_port', 'enabled', 'ip_version',
        'name', 'project_id', 'protocol', 'shared', 'source_firewall_group_id',
        'source_ip_address', 'source_port')
    def update_firewall_rule(self, name_or_id, filters=None, **kwargs):
        """
        Updates firewall rule.

        :param name_or_id: firewall rule name or id
        :param dict filters: optional filters
        :param kwargs: firewall rule update parameters.
            See create_firewall_rule docstring for valid parameters.
        :raises: BadRequestException if parameters are malformed
        :raises: NotFoundException if resource is not found
        :return: updated firewall rule
        :rtype: FirewallRule
        """
        if not filters:
            filters = {}
        firewall_rule = self.network.find_firewall_rule(
            name_or_id, ignore_missing=False, **filters)

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
            ids_list.append(self.network.find_firewall_rule(
                name_or_id, ignore_missing=False, **filters)['id'])
        return ids_list

    @_utils.valid_kwargs('audited', 'description', 'firewall_rules', 'name',
                         'project_id', 'shared')
    def create_firewall_policy(self, **kwargs):
        """
        Create firewall policy.

        :param bool audited: Status of audition of firewall policy.
                             Set to False each time the firewall policy or the
                             associated firewall rules are changed.
                             Has to be explicitly set to True.
        :param description: Human-readable description.
        :param list[str] firewall_rules: List of associated firewall rules.
        :param name: Human-readable name.
        :param project_id: Project id.
        :param bool shared: Visibility to other projects.
                       Defaults to False.
        :raises: BadRequestException if parameters are malformed
        :raises: ResourceNotFound if a resource from firewall_list not found
        :return: created firewall policy
        :rtype: FirewallPolicy
        """
        if 'firewall_rules' in kwargs:
            kwargs['firewall_rules'] = self._get_firewall_rule_ids(
                kwargs['firewall_rules'])

        return self.network.create_firewall_policy(**kwargs)

    def delete_firewall_policy(self, name_or_id, filters=None):
        """
        Deletes firewall policy.
        Prints debug message in case to-be-deleted resource was not found.

        :param name_or_id: firewall policy name or id
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :return: True if resource is successfully deleted, False otherwise.
        :rtype: bool
        """
        if not filters:
            filters = {}
        try:
            firewall_policy = self.network.find_firewall_policy(
                name_or_id, ignore_missing=False, **filters)
            self.network.delete_firewall_policy(firewall_policy,
                                                ignore_missing=False)
        except exceptions.ResourceNotFound:
            self.log.debug('Firewall policy %s not found for deleting',
                           name_or_id)
            return False
        return True

    def get_firewall_policy(self, name_or_id, filters=None):
        """
        Retrieves a single firewall policy.

        :param name_or_id: firewall policy name or id
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :return: firewall policy or None if not found
        :rtype: FirewallPolicy
        """
        if not filters:
            filters = {}
        return self.network.find_firewall_policy(name_or_id, **filters)

    def list_firewall_policies(self, filters=None):
        """
        Lists firewall policies.

        :param dict filters: optional filters
        :return: list of firewall policies
        :rtype: list[FirewallPolicy]
        """
        if not filters:
            filters = {}
        return list(self.network.firewall_policies(**filters))

    @_utils.valid_kwargs('audited', 'description', 'firewall_rules', 'name',
                         'project_id', 'shared')
    def update_firewall_policy(self, name_or_id, filters=None, **kwargs):
        """
        Updates firewall policy.

        :param name_or_id: firewall policy name or id
        :param dict filters: optional filters
        :param kwargs: firewall policy update parameters
            See create_firewall_policy docstring for valid parameters.
        :raises: BadRequestException if parameters are malformed
        :raises: DuplicateResource on multiple matches
        :raises: ResourceNotFound if resource is not found
        :return: updated firewall policy
        :rtype: FirewallPolicy
        """
        if not filters:
            filters = {}
        firewall_policy = self.network.find_firewall_policy(
            name_or_id, ignore_missing=False, **filters)

        if 'firewall_rules' in kwargs:
            kwargs['firewall_rules'] = self._get_firewall_rule_ids(
                kwargs['firewall_rules'])

        return self.network.update_firewall_policy(firewall_policy, **kwargs)

    def insert_rule_into_policy(self, name_or_id, rule_name_or_id,
                                insert_after=None, insert_before=None,
                                filters=None):
        """
        Adds firewall rule to the firewall_rules list of a firewall policy.
        Short-circuits and returns the firewall policy early if the firewall
        rule id is already present in the firewall_rules list.
        This method doesn't do re-ordering. If you want to move a firewall rule
        or or down the list, you have to remove and re-add it.

        :param name_or_id: firewall policy name or id
        :param rule_name_or_id: firewall rule name or id
        :param insert_after: rule name or id that should precede added rule
        :param insert_before: rule name or id that should succeed added rule
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :raises: ResourceNotFound if firewall policy or any of the firewall
                 rules (inserted, after, before) is not found.
        :return: updated firewall policy
        :rtype: FirewallPolicy
        """
        if not filters:
            filters = {}
        firewall_policy = self.network.find_firewall_policy(
            name_or_id, ignore_missing=False, **filters)

        firewall_rule = self.network.find_firewall_rule(
            rule_name_or_id, ignore_missing=False)
        # short-circuit if rule already in firewall_rules list
        # the API can't do any re-ordering of existing rules
        if firewall_rule['id'] in firewall_policy['firewall_rules']:
            self.log.debug(
                'Firewall rule %s already associated with firewall policy %s',
                rule_name_or_id, name_or_id)
            return firewall_policy

        pos_params = {}
        if insert_after is not None:
            pos_params['insert_after'] = self.network.find_firewall_rule(
                insert_after, ignore_missing=False)['id']

        if insert_before is not None:
            pos_params['insert_before'] = self.network.find_firewall_rule(
                insert_before, ignore_missing=False)['id']

        return self.network.insert_rule_into_policy(firewall_policy['id'],
                                                    firewall_rule['id'],
                                                    **pos_params)

    def remove_rule_from_policy(self, name_or_id, rule_name_or_id,
                                filters=None):
        """
        Remove firewall rule from firewall policy's firewall_rules list.
        Short-circuits and returns firewall policy early if firewall rule
        is already absent from the firewall_rules list.

        :param name_or_id: firewall policy name or id
        :param rule_name_or_id: firewall rule name or id
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :raises: ResourceNotFound if firewall policy is not found
        :return: updated firewall policy
        :rtype: FirewallPolicy
        """
        if not filters:
            filters = {}
        firewall_policy = self.network.find_firewall_policy(
            name_or_id, ignore_missing=False, **filters)

        firewall_rule = self.network.find_firewall_rule(rule_name_or_id)
        if not firewall_rule:
            # short-circuit: if firewall rule is not found,
            # return current firewall policy
            self.log.debug('Firewall rule %s not found for removing',
                           rule_name_or_id)
            return firewall_policy

        if firewall_rule['id'] not in firewall_policy['firewall_rules']:
            # short-circuit: if firewall rule id is not associated,
            # log it to debug and return current firewall policy
            self.log.debug(
                'Firewall rule %s not associated with firewall policy %s',
                rule_name_or_id, name_or_id)
            return firewall_policy

        return self.network.remove_rule_from_policy(firewall_policy['id'],
                                                    firewall_rule['id'])

    @_utils.valid_kwargs(
        'admin_state_up', 'description', 'egress_firewall_policy',
        'ingress_firewall_policy', 'name', 'ports', 'project_id', 'shared')
    def create_firewall_group(self, **kwargs):
        """
        Creates firewall group. The keys egress_firewall_policy and
        ingress_firewall_policy are looked up and mapped as
        egress_firewall_policy_id and ingress_firewall_policy_id respectively.
        Port name or ids list is transformed to port ids list before the POST
        request.

        :param bool admin_state_up: State of firewall group.
                                    Will block all traffic if set to False.
                                    Defaults to True.
        :param description: Human-readable description.
        :param egress_firewall_policy: Name or id of egress firewall policy.
        :param ingress_firewall_policy: Name or id of ingress firewall policy.
        :param name: Human-readable name.
        :param list[str] ports: List of associated ports (name or id)
        :param project_id: Project id.
        :param shared: Visibility to other projects.
                       Defaults to False.
        :raises: BadRequestException if parameters are malformed
        :raises: DuplicateResource on multiple matches
        :raises: ResourceNotFound if (ingress-, egress-) firewall policy or
                 a port is not found.
        :return: created firewall group
        :rtype: FirewallGroup
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
        :return: True if resource is successfully deleted, False otherwise.
        :rtype: bool
        """
        if not filters:
            filters = {}
        try:
            firewall_group = self.network.find_firewall_group(
                name_or_id, ignore_missing=False, **filters)
            self.network.delete_firewall_group(firewall_group,
                                               ignore_missing=False)
        except exceptions.ResourceNotFound:
            self.log.debug('Firewall group %s not found for deleting',
                           name_or_id)
            return False
        return True

    def get_firewall_group(self, name_or_id, filters=None):
        """
        Retrieves firewall group.

        :param name_or_id: firewall group name or id
        :param dict filters: optional filters
        :raises: DuplicateResource on multiple matches
        :return: firewall group or None if not found
        :rtype: FirewallGroup
        """
        if not filters:
            filters = {}
        return self.network.find_firewall_group(name_or_id, **filters)

    def list_firewall_groups(self, filters=None):
        """
        Lists firewall groups.

        :param dict filters: optional filters
        :return: list of firewall groups
        :rtype: list[FirewallGroup]
        """
        if not filters:
            filters = {}
        return list(self.network.firewall_groups(**filters))

    @_utils.valid_kwargs(
        'admin_state_up', 'description', 'egress_firewall_policy',
        'ingress_firewall_policy', 'name', 'ports', 'project_id', 'shared')
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
        :raises: BadRequestException if parameters are malformed
        :raises: DuplicateResource on multiple matches
        :raises: ResourceNotFound if firewall group, a firewall policy
                 (egress, ingress) or port is not found
        :return: updated firewall group
        :rtype: FirewallGroup
        """
        if not filters:
            filters = {}
        firewall_group = self.network.find_firewall_group(
            name_or_id, ignore_missing=False, **filters)
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
        :raises: ResourceNotFound if a firewall policy is not found
        """
        for key in ('egress_firewall_policy', 'ingress_firewall_policy'):
            if key not in firewall_group:
                continue
            if firewall_group[key] is None:
                val = None
            else:
                val = self.network.find_firewall_policy(
                    firewall_group[key], ignore_missing=False)['id']
            firewall_group[key + '_id'] = val
            del firewall_group[key]

    @_utils.valid_kwargs("name", "description", "shared", "default",
                         "project_id")
    def create_qos_policy(self, **kwargs):
        """Create a QoS policy.

        :param string name: Name of the QoS policy being created.
        :param string description: Description of created QoS policy.
        :param bool shared: Set the QoS policy as shared.
        :param bool default: Set the QoS policy as default for project.
        :param string project_id: Specify the project ID this QoS policy
            will be created on (admin-only).

        :returns: The QoS policy object.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        default = kwargs.pop("default", None)
        if default is not None:
            if self._has_neutron_extension('qos-default'):
                kwargs['is_default'] = default
            else:
                self.log.debug("'qos-default' extension is not available on "
                               "target cloud")

        data = self.network.post("/qos/policies.json", json={'policy': kwargs})
        return self._get_and_munchify('policy', data)

    @_utils.valid_kwargs("name", "description", "shared", "default",
                         "project_id")
    def update_qos_policy(self, name_or_id, **kwargs):
        """Update an existing QoS policy.

        :param string name_or_id:
           Name or ID of the QoS policy to update.
        :param string policy_name:
           The new name of the QoS policy.
        :param string description:
            The new description of the QoS policy.
        :param bool shared:
            If True, the QoS policy will be set as shared.
        :param bool default:
            If True, the QoS policy will be set as default for project.

        :returns: The updated QoS policy object.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        default = kwargs.pop("default", None)
        if default is not None:
            if self._has_neutron_extension('qos-default'):
                kwargs['is_default'] = default
            else:
                self.log.debug("'qos-default' extension is not available on "
                               "target cloud")

        if not kwargs:
            self.log.debug("No QoS policy data to update")
            return

        curr_policy = self.get_qos_policy(name_or_id)
        if not curr_policy:
            raise exc.OpenStackCloudException(
                "QoS policy %s not found." % name_or_id)

        data = self.network.put(
            "/qos/policies/{policy_id}.json".format(
                policy_id=curr_policy['id']),
            json={'policy': kwargs})
        return self._get_and_munchify('policy', data)

    def delete_qos_policy(self, name_or_id):
        """Delete a QoS policy.

        :param name_or_id: Name or ID of the policy being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')
        policy = self.get_qos_policy(name_or_id)
        if not policy:
            self.log.debug("QoS policy %s not found for deleting", name_or_id)
            return False

        exceptions.raise_from_response(self.network.delete(
            "/qos/policies/{policy_id}.json".format(policy_id=policy['id'])))

        return True

    def search_qos_bandwidth_limit_rules(self, policy_name_or_id, rule_id=None,
                                         filters=None):
        """Search QoS bandwidth limit rules

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rules should be associated.
        :param string rule_id: ID of searched rule.
        :param filters: a dict containing additional filters to use. e.g.
                        {'max_kbps': 1000}

        :returns: a list of ``munch.Munch`` containing the bandwidth limit
            rule descriptions.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        rules = self.list_qos_bandwidth_limit_rules(policy_name_or_id, filters)
        return _utils._filter_list(rules, rule_id, filters)

    def list_qos_bandwidth_limit_rules(self, policy_name_or_id, filters=None):
        """List all available QoS bandwidth limit rules.

        :param string policy_name_or_id: Name or ID of the QoS policy from
            from rules should be listed.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of ``munch.Munch`` containing rule info.

        :raises: ``OpenStackCloudResourceNotFound`` if QoS policy will not be
            found.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        resp = self.network.get(
            "/qos/policies/{policy_id}/bandwidth_limit_rules.json".format(
                policy_id=policy['id']),
            params=filters)
        data = proxy._json_response(
            resp,
            error_message="Error fetching QoS bandwidth limit rules from "
                          "{policy}".format(policy=policy['id']))
        return self._get_and_munchify('bandwidth_limit_rules', data)

    def get_qos_bandwidth_limit_rule(self, policy_name_or_id, rule_id):
        """Get a QoS bandwidth limit rule by name or ID.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param rule_id: ID of the rule.

        :returns: A bandwidth limit rule ``munch.Munch`` or None if
            no matching rule is found.

        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        resp = self.network.get(
            "/qos/policies/{policy_id}/bandwidth_limit_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id))
        data = proxy._json_response(
            resp,
            error_message="Error fetching QoS bandwidth limit rule {rule_id} "
                          "from {policy}".format(rule_id=rule_id,
                                                 policy=policy['id']))
        return self._get_and_munchify('bandwidth_limit_rule', data)

    @_utils.valid_kwargs("max_burst_kbps", "direction")
    def create_qos_bandwidth_limit_rule(self, policy_name_or_id, max_kbps,
                                        **kwargs):
        """Create a QoS bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param int max_kbps: Maximum bandwidth limit value
            (in kilobits per second).
        :param int max_burst_kbps: Maximum burst value (in kilobits).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be limited.

        :returns: The QoS bandwidth limit rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        if kwargs.get("direction") is not None:
            if not self._has_neutron_extension('qos-bw-limit-direction'):
                kwargs.pop("direction")
                self.log.debug(
                    "'qos-bw-limit-direction' extension is not available on "
                    "target cloud")

        kwargs['max_kbps'] = max_kbps
        data = self.network.post(
            "/qos/policies/{policy_id}/bandwidth_limit_rules".format(
                policy_id=policy['id']),
            json={'bandwidth_limit_rule': kwargs})
        return self._get_and_munchify('bandwidth_limit_rule', data)

    @_utils.valid_kwargs("max_kbps", "max_burst_kbps", "direction")
    def update_qos_bandwidth_limit_rule(self, policy_name_or_id, rule_id,
                                        **kwargs):
        """Update a QoS bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.
        :param int max_kbps: Maximum bandwidth limit value
            (in kilobits per second).
        :param int max_burst_kbps: Maximum burst value (in kilobits).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be limited.

        :returns: The updated QoS bandwidth limit rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        if kwargs.get("direction") is not None:
            if not self._has_neutron_extension('qos-bw-limit-direction'):
                kwargs.pop("direction")
                self.log.debug(
                    "'qos-bw-limit-direction' extension is not available on "
                    "target cloud")

        if not kwargs:
            self.log.debug("No QoS bandwidth limit rule data to update")
            return

        curr_rule = self.get_qos_bandwidth_limit_rule(
            policy_name_or_id, rule_id)
        if not curr_rule:
            raise exc.OpenStackCloudException(
                "QoS bandwidth_limit_rule {rule_id} not found in policy "
                "{policy_id}".format(rule_id=rule_id,
                                     policy_id=policy['id']))

        data = self.network.put(
            "/qos/policies/{policy_id}/bandwidth_limit_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id),
            json={'bandwidth_limit_rule': kwargs})
        return self._get_and_munchify('bandwidth_limit_rule', data)

    def delete_qos_bandwidth_limit_rule(self, policy_name_or_id, rule_id):
        """Delete a QoS bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.

        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        try:
            exceptions.raise_from_response(self.network.delete(
                "/qos/policies/{policy}/bandwidth_limit_rules/{rule}.json".
                format(policy=policy['id'], rule=rule_id)))
        except exc.OpenStackCloudURINotFound:
            self.log.debug(
                "QoS bandwidth limit rule {rule_id} not found in policy "
                "{policy_id}. Ignoring.".format(rule_id=rule_id,
                                                policy_id=policy['id']))
            return False

        return True

    def search_qos_dscp_marking_rules(self, policy_name_or_id, rule_id=None,
                                      filters=None):
        """Search QoS DSCP marking rules

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rules should be associated.
        :param string rule_id: ID of searched rule.
        :param filters: a dict containing additional filters to use. e.g.
                        {'dscp_mark': 32}

        :returns: a list of ``munch.Munch`` containing the dscp marking
            rule descriptions.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        rules = self.list_qos_dscp_marking_rules(policy_name_or_id, filters)
        return _utils._filter_list(rules, rule_id, filters)

    def list_qos_dscp_marking_rules(self, policy_name_or_id, filters=None):
        """List all available QoS DSCP marking rules.

        :param string policy_name_or_id: Name or ID of the QoS policy from
            from rules should be listed.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of ``munch.Munch`` containing rule info.

        :raises: ``OpenStackCloudResourceNotFound`` if QoS policy will not be
            found.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        resp = self.network.get(
            "/qos/policies/{policy_id}/dscp_marking_rules.json".format(
                policy_id=policy['id']),
            params=filters)
        data = proxy._json_response(
            resp,
            error_message="Error fetching QoS DSCP marking rules from "
                          "{policy}".format(policy=policy['id']))
        return self._get_and_munchify('dscp_marking_rules', data)

    def get_qos_dscp_marking_rule(self, policy_name_or_id, rule_id):
        """Get a QoS DSCP marking rule by name or ID.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param rule_id: ID of the rule.

        :returns: A bandwidth limit rule ``munch.Munch`` or None if
            no matching rule is found.

        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        resp = self.network.get(
            "/qos/policies/{policy_id}/dscp_marking_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id))
        data = proxy._json_response(
            resp,
            error_message="Error fetching QoS DSCP marking rule {rule_id} "
                          "from {policy}".format(rule_id=rule_id,
                                                 policy=policy['id']))
        return self._get_and_munchify('dscp_marking_rule', data)

    def create_qos_dscp_marking_rule(self, policy_name_or_id, dscp_mark):
        """Create a QoS DSCP marking rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param int dscp_mark: DSCP mark value

        :returns: The QoS DSCP marking rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        body = {
            'dscp_mark': dscp_mark
        }
        data = self.network.post(
            "/qos/policies/{policy_id}/dscp_marking_rules".format(
                policy_id=policy['id']),
            json={'dscp_marking_rule': body})
        return self._get_and_munchify('dscp_marking_rule', data)

    @_utils.valid_kwargs("dscp_mark")
    def update_qos_dscp_marking_rule(self, policy_name_or_id, rule_id,
                                     **kwargs):
        """Update a QoS DSCP marking rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.
        :param int dscp_mark: DSCP mark value

        :returns: The updated QoS bandwidth limit rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        if not kwargs:
            self.log.debug("No QoS DSCP marking rule data to update")
            return

        curr_rule = self.get_qos_dscp_marking_rule(
            policy_name_or_id, rule_id)
        if not curr_rule:
            raise exc.OpenStackCloudException(
                "QoS dscp_marking_rule {rule_id} not found in policy "
                "{policy_id}".format(rule_id=rule_id,
                                     policy_id=policy['id']))

        data = self.network.put(
            "/qos/policies/{policy_id}/dscp_marking_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id),
            json={'dscp_marking_rule': kwargs})
        return self._get_and_munchify('dscp_marking_rule', data)

    def delete_qos_dscp_marking_rule(self, policy_name_or_id, rule_id):
        """Delete a QoS DSCP marking rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.

        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        try:
            exceptions.raise_from_response(self.network.delete(
                "/qos/policies/{policy}/dscp_marking_rules/{rule}.json".
                format(policy=policy['id'], rule=rule_id)))
        except exc.OpenStackCloudURINotFound:
            self.log.debug(
                "QoS DSCP marking rule {rule_id} not found in policy "
                "{policy_id}. Ignoring.".format(rule_id=rule_id,
                                                policy_id=policy['id']))
            return False

        return True

    def search_qos_minimum_bandwidth_rules(self, policy_name_or_id,
                                           rule_id=None, filters=None):
        """Search QoS minimum bandwidth rules

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rules should be associated.
        :param string rule_id: ID of searched rule.
        :param filters: a dict containing additional filters to use. e.g.
                        {'min_kbps': 1000}

        :returns: a list of ``munch.Munch`` containing the bandwidth limit
            rule descriptions.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        rules = self.list_qos_minimum_bandwidth_rules(
            policy_name_or_id, filters)
        return _utils._filter_list(rules, rule_id, filters)

    def list_qos_minimum_bandwidth_rules(self, policy_name_or_id,
                                         filters=None):
        """List all available QoS minimum bandwidth rules.

        :param string policy_name_or_id: Name or ID of the QoS policy from
            from rules should be listed.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of ``munch.Munch`` containing rule info.

        :raises: ``OpenStackCloudResourceNotFound`` if QoS policy will not be
            found.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        resp = self.network.get(
            "/qos/policies/{policy_id}/minimum_bandwidth_rules.json".format(
                policy_id=policy['id']),
            params=filters)
        data = proxy._json_response(
            resp,
            error_message="Error fetching QoS minimum bandwidth rules from "
                          "{policy}".format(policy=policy['id']))
        return self._get_and_munchify('minimum_bandwidth_rules', data)

    def get_qos_minimum_bandwidth_rule(self, policy_name_or_id, rule_id):
        """Get a QoS minimum bandwidth rule by name or ID.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param rule_id: ID of the rule.

        :returns: A bandwidth limit rule ``munch.Munch`` or None if
            no matching rule is found.

        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        resp = self.network.get(
            "/qos/policies/{policy_id}/minimum_bandwidth_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id))
        data = proxy._json_response(
            resp,
            error_message="Error fetching QoS minimum_bandwidth rule {rule_id}"
                          " from {policy}".format(rule_id=rule_id,
                                                  policy=policy['id']))
        return self._get_and_munchify('minimum_bandwidth_rule', data)

    @_utils.valid_kwargs("direction")
    def create_qos_minimum_bandwidth_rule(self, policy_name_or_id, min_kbps,
                                          **kwargs):
        """Create a QoS minimum bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param int min_kbps: Minimum bandwidth value (in kilobits per second).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be available.

        :returns: The QoS minimum bandwidth rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        kwargs['min_kbps'] = min_kbps
        data = self.network.post(
            "/qos/policies/{policy_id}/minimum_bandwidth_rules".format(
                policy_id=policy['id']),
            json={'minimum_bandwidth_rule': kwargs})
        return self._get_and_munchify('minimum_bandwidth_rule', data)

    @_utils.valid_kwargs("min_kbps", "direction")
    def update_qos_minimum_bandwidth_rule(self, policy_name_or_id, rule_id,
                                          **kwargs):
        """Update a QoS minimum bandwidth rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.
        :param int min_kbps: Minimum bandwidth value (in kilobits per second).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be available.

        :returns: The updated QoS minimum bandwidth rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        if not kwargs:
            self.log.debug("No QoS minimum bandwidth rule data to update")
            return

        curr_rule = self.get_qos_minimum_bandwidth_rule(
            policy_name_or_id, rule_id)
        if not curr_rule:
            raise exc.OpenStackCloudException(
                "QoS minimum_bandwidth_rule {rule_id} not found in policy "
                "{policy_id}".format(rule_id=rule_id,
                                     policy_id=policy['id']))

        data = self.network.put(
            "/qos/policies/{policy_id}/minimum_bandwidth_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id),
            json={'minimum_bandwidth_rule': kwargs})
        return self._get_and_munchify('minimum_bandwidth_rule', data)

    def delete_qos_minimum_bandwidth_rule(self, policy_name_or_id, rule_id):
        """Delete a QoS minimum bandwidth rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to delete.

        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise exc.OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise exc.OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        try:
            exceptions.raise_from_response(self.network.delete(
                "/qos/policies/{policy}/minimum_bandwidth_rules/{rule}.json".
                format(policy=policy['id'], rule=rule_id)))
        except exc.OpenStackCloudURINotFound:
            self.log.debug(
                "QoS minimum bandwidth rule {rule_id} not found in policy "
                "{policy_id}. Ignoring.".format(rule_id=rule_id,
                                                policy_id=policy['id']))
            return False

        return True

    def add_router_interface(self, router, subnet_id=None, port_id=None):
        """Attach a subnet to an internal router interface.

        Either a subnet ID or port ID must be specified for the internal
        interface. Supplying both will result in an error.

        :param dict router: The dict object of the router being changed
        :param string subnet_id: The ID of the subnet to use for the interface
        :param string port_id: The ID of the port to use for the interface

        :returns: A ``munch.Munch`` with the router ID (ID),
                  subnet ID (subnet_id), port ID (port_id) and tenant ID
                  (tenant_id).

        :raises: OpenStackCloudException on operation error.
        """
        json_body = {}
        if subnet_id:
            json_body['subnet_id'] = subnet_id
        if port_id:
            json_body['port_id'] = port_id

        return proxy._json_response(
            self.network.put(
                "/routers/{router_id}/add_router_interface.json".format(
                    router_id=router['id']),
                json=json_body),
            error_message="Error attaching interface to router {0}".format(
                router['id']))

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

        :raises: OpenStackCloudException on operation error.
        """
        json_body = {}
        if subnet_id:
            json_body['subnet_id'] = subnet_id
        if port_id:
            json_body['port_id'] = port_id

        if not json_body:
            raise ValueError(
                "At least one of subnet_id or port_id must be supplied.")

        exceptions.raise_from_response(
            self.network.put(
                "/routers/{router_id}/remove_router_interface.json".format(
                    router_id=router['id']),
                json=json_body),
            error_message="Error detaching interface from router {0}".format(
                router['id']))

    def list_router_interfaces(self, router, interface_type=None):
        """List all interfaces for a router.

        :param dict router: A router dict object.
        :param string interface_type: One of None, "internal", or "external".
            Controls whether all, internal interfaces or external interfaces
            are returned.

        :returns: A list of port ``munch.Munch`` objects.
        """
        # Find only router interface and gateway ports, ignore L3 HA ports etc.
        router_interfaces = self.search_ports(filters={
            'device_id': router['id'],
            'device_owner': 'network:router_interface'}
        ) + self.search_ports(filters={
            'device_id': router['id'],
            'device_owner': 'network:router_interface_distributed'}
        ) + self.search_ports(filters={
            'device_id': router['id'],
            'device_owner': 'network:ha_router_replicated_interface'})
        router_gateways = self.search_ports(filters={
            'device_id': router['id'],
            'device_owner': 'network:router_gateway'})
        ports = router_interfaces + router_gateways

        if interface_type:
            if interface_type == 'internal':
                return router_interfaces
            if interface_type == 'external':
                return router_gateways
        return ports

    def create_router(self, name=None, admin_state_up=True,
                      ext_gateway_net_id=None, enable_snat=None,
                      ext_fixed_ips=None, project_id=None,
                      availability_zone_hints=None):
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
                  "ip_address": "192.168.10.2"
                }
              ]
        :param string project_id: Project ID for the router.
        :param types.ListType availability_zone_hints:
            A list of availability zone hints.

        :returns: The router object.
        :raises: OpenStackCloudException on operation error.
        """
        router = {
            'admin_state_up': admin_state_up
        }
        if project_id is not None:
            router['tenant_id'] = project_id
        if name:
            router['name'] = name
        ext_gw_info = self._build_external_gateway_info(
            ext_gateway_net_id, enable_snat, ext_fixed_ips
        )
        if ext_gw_info:
            router['external_gateway_info'] = ext_gw_info
        if availability_zone_hints is not None:
            if not isinstance(availability_zone_hints, list):
                raise exc.OpenStackCloudException(
                    "Parameter 'availability_zone_hints' must be a list")
            if not self._has_neutron_extension('router_availability_zone'):
                raise exc.OpenStackCloudUnavailableExtension(
                    'router_availability_zone extension is not available on '
                    'target cloud')
            router['availability_zone_hints'] = availability_zone_hints

        data = proxy._json_response(
            self.network.post("/routers.json", json={"router": router}),
            error_message="Error creating router {0}".format(name))
        return self._get_and_munchify('router', data)

    def update_router(self, name_or_id, name=None, admin_state_up=None,
                      ext_gateway_net_id=None, enable_snat=None,
                      ext_fixed_ips=None, routes=None):
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
                  "ip_address": "192.168.10.2"
                }
              ]
        :param list routes:
            A list of dictionaries with destination and nexthop parameters. To
            clear all routes pass an empty list ([]).

            Example::

              [
                {
                  "destination": "179.24.1.0/24",
                  "nexthop": "172.24.3.99"
                }
              ]
        :returns: The router object.
        :raises: OpenStackCloudException on operation error.
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
                    'extra routes extension is not available on target cloud')

        if not router:
            self.log.debug("No router data to update")
            return

        curr_router = self.get_router(name_or_id)
        if not curr_router:
            raise exc.OpenStackCloudException(
                "Router %s not found." % name_or_id)

        resp = self.network.put(
            "/routers/{router_id}.json".format(router_id=curr_router['id']),
            json={"router": router})
        data = proxy._json_response(
            resp,
            error_message="Error updating router {0}".format(name_or_id))
        return self._get_and_munchify('router', data)

    def delete_router(self, name_or_id):
        """Delete a logical router.

        If a name, instead of a unique UUID, is supplied, it is possible
        that we could find more than one matching router since names are
        not required to be unique. An error will be raised in this case.

        :param name_or_id: Name or ID of the router being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        router = self.get_router(name_or_id)
        if not router:
            self.log.debug("Router %s not found for deleting", name_or_id)
            return False

        exceptions.raise_from_response(self.network.delete(
            "/routers/{router_id}.json".format(router_id=router['id']),
            error_message="Error deleting router {0}".format(name_or_id)))

        return True

    def create_subnet(self, network_name_or_id, cidr=None, ip_version=4,
                      enable_dhcp=False, subnet_name=None, tenant_id=None,
                      allocation_pools=None,
                      gateway_ip=None, disable_gateway_ip=False,
                      dns_nameservers=None, host_routes=None,
                      ipv6_ra_mode=None, ipv6_address_mode=None,
                      prefixlen=None, use_default_subnetpool=False, **kwargs):
        """Create a subnet on a specified network.

        :param string network_name_or_id:
           The unique name or ID of the attached network. If a non-unique
           name is supplied, an exception is raised.
        :param string cidr:
           The CIDR.
        :param int ip_version:
           The IP version, which is 4 or 6.
        :param bool enable_dhcp:
           Set to ``True`` if DHCP is enabled and ``False`` if disabled.
           Default is ``False``.
        :param string subnet_name:
           The name of the subnet.
        :param string tenant_id:
           The ID of the tenant who owns the network. Only administrative users
           can specify a tenant ID other than their own.
        :param allocation_pools:
           A list of dictionaries of the start and end addresses for the
           allocation pools. For example::

             [
               {
                 "start": "192.168.199.2",
                 "end": "192.168.199.254"
               }
             ]

        :param string gateway_ip:
           The gateway IP address. When you specify both allocation_pools and
           gateway_ip, you must ensure that the gateway IP does not overlap
           with the specified allocation pools.
        :param bool disable_gateway_ip:
           Set to ``True`` if gateway IP address is disabled and ``False`` if
           enabled. It is not allowed with gateway_ip.
           Default is ``False``.
        :param dns_nameservers:
           A list of DNS name servers for the subnet. For example::

             [ "8.8.8.7", "8.8.8.8" ]

        :param host_routes:
           A list of host route dictionaries for the subnet. For example::

             [
               {
                 "destination": "0.0.0.0/0",
                 "nexthop": "123.456.78.9"
               },
               {
                 "destination": "192.168.0.0/24",
                 "nexthop": "192.168.0.1"
               }
             ]

        :param string ipv6_ra_mode:
           IPv6 Router Advertisement mode. Valid values are: 'dhcpv6-stateful',
           'dhcpv6-stateless', or 'slaac'.
        :param string ipv6_address_mode:
           IPv6 address mode. Valid values are: 'dhcpv6-stateful',
           'dhcpv6-stateless', or 'slaac'.
        :param string prefixlen:
           The prefix length to use for subnet allocation from a subnet pool.
        :param bool use_default_subnetpool:
           Use the default subnetpool for ``ip_version`` to obtain a CIDR. It
           is required to pass ``None`` to the ``cidr`` argument when enabling
           this option.
        :param kwargs: Key value pairs to be passed to the Neutron API.

        :returns: The new subnet object.
        :raises: OpenStackCloudException on operation error.
        """

        if tenant_id is not None:
            filters = {'tenant_id': tenant_id}
        else:
            filters = None

        network = self.get_network(network_name_or_id, filters)
        if not network:
            raise exc.OpenStackCloudException(
                "Network %s not found." % network_name_or_id)

        if disable_gateway_ip and gateway_ip:
            raise exc.OpenStackCloudException(
                'arg:disable_gateway_ip is not allowed with arg:gateway_ip')

        if not cidr and not use_default_subnetpool:
            raise exc.OpenStackCloudException(
                'arg:cidr is required when a subnetpool is not used')

        if cidr and use_default_subnetpool:
            raise exc.OpenStackCloudException(
                'arg:cidr must be set to None when use_default_subnetpool == '
                'True')

        # Be friendly on ip_version and allow strings
        if isinstance(ip_version, six.string_types):
            try:
                ip_version = int(ip_version)
            except ValueError:
                raise exc.OpenStackCloudException(
                    'ip_version must be an integer')

        # The body of the neutron message for the subnet we wish to create.
        # This includes attributes that are required or have defaults.
        subnet = dict({
            'network_id': network['id'],
            'ip_version': ip_version,
            'enable_dhcp': enable_dhcp,
        }, **kwargs)

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

        response = self.network.post("/subnets.json", json={"subnet": subnet})

        return self._get_and_munchify('subnet', response)

    def delete_subnet(self, name_or_id):
        """Delete a subnet.

        If a name, instead of a unique UUID, is supplied, it is possible
        that we could find more than one matching subnet since names are
        not required to be unique. An error will be raised in this case.

        :param name_or_id: Name or ID of the subnet being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        subnet = self.get_subnet(name_or_id)
        if not subnet:
            self.log.debug("Subnet %s not found for deleting", name_or_id)
            return False

        exceptions.raise_from_response(self.network.delete(
            "/subnets/{subnet_id}.json".format(subnet_id=subnet['id'])))
        return True

    def update_subnet(self, name_or_id, subnet_name=None, enable_dhcp=None,
                      gateway_ip=None, disable_gateway_ip=None,
                      allocation_pools=None, dns_nameservers=None,
                      host_routes=None):
        """Update an existing subnet.

        :param string name_or_id:
           Name or ID of the subnet to update.
        :param string subnet_name:
           The new name of the subnet.
        :param bool enable_dhcp:
           Set to ``True`` if DHCP is enabled and ``False`` if disabled.
        :param string gateway_ip:
           The gateway IP address. When you specify both allocation_pools and
           gateway_ip, you must ensure that the gateway IP does not overlap
           with the specified allocation pools.
        :param bool disable_gateway_ip:
           Set to ``True`` if gateway IP address is disabled and ``False`` if
           enabled. It is not allowed with gateway_ip.
           Default is ``False``.
        :param allocation_pools:
           A list of dictionaries of the start and end addresses for the
           allocation pools. For example::

             [
               {
                 "start": "192.168.199.2",
                 "end": "192.168.199.254"
               }
             ]

        :param dns_nameservers:
           A list of DNS name servers for the subnet. For example::

             [ "8.8.8.7", "8.8.8.8" ]

        :param host_routes:
           A list of host route dictionaries for the subnet. For example::

             [
               {
                 "destination": "0.0.0.0/0",
                 "nexthop": "123.456.78.9"
               },
               {
                 "destination": "192.168.0.0/24",
                 "nexthop": "192.168.0.1"
               }
             ]

        :returns: The updated subnet object.
        :raises: OpenStackCloudException on operation error.
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
            raise exc.OpenStackCloudException(
                'arg:disable_gateway_ip is not allowed with arg:gateway_ip')

        curr_subnet = self.get_subnet(name_or_id)
        if not curr_subnet:
            raise exc.OpenStackCloudException(
                "Subnet %s not found." % name_or_id)

        response = self.network.put(
            "/subnets/{subnet_id}.json".format(subnet_id=curr_subnet['id']),
            json={"subnet": subnet})
        return self._get_and_munchify('subnet', response)

    @_utils.valid_kwargs('name', 'admin_state_up', 'mac_address', 'fixed_ips',
                         'subnet_id', 'ip_address', 'security_groups',
                         'allowed_address_pairs', 'extra_dhcp_opts',
                         'device_owner', 'device_id', 'binding:vnic_type',
                         'binding:profile', 'port_security_enabled',
                         'qos_policy_id')
    def create_port(self, network_id, **kwargs):
        """Create a port

        :param network_id: The ID of the network. (Required)
        :param name: A symbolic name for the port. (Optional)
        :param admin_state_up: The administrative status of the port,
            which is up (true, default) or down (false). (Optional)
        :param mac_address: The MAC address. (Optional)
        :param fixed_ips: List of ip_addresses and subnet_ids. See subnet_id
            and ip_address. (Optional)
            For example::

              [
                {
                  "ip_address": "10.29.29.13",
                  "subnet_id": "a78484c4-c380-4b47-85aa-21c51a2d8cbd"
                }, ...
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
                  "mac_address": "fa:16:3e:c4:cd:3f"
                }, ...
              ]
        :param extra_dhcp_opts: Extra DHCP options. (Optional).
            For example::

              [
                {
                  "opt_name": "opt name1",
                  "opt_value": "value1"
                }, ...
              ]
        :param device_owner: The ID of the entity that uses this port.
            For example, a DHCP agent.  (Optional)
        :param device_id: The ID of the device that uses this port.
            For example, a virtual server. (Optional)
        :param binding vnic_type: The type of the created port. (Optional)
        :param port_security_enabled: The security port state created on
            the network. (Optional)
        :param qos_policy_id: The ID of the QoS policy to apply for port.

        :returns: a ``munch.Munch`` describing the created port.

        :raises: ``OpenStackCloudException`` on operation error.
        """
        kwargs['network_id'] = network_id

        data = proxy._json_response(
            self.network.post("/ports.json", json={'port': kwargs}),
            error_message="Error creating port for network {0}".format(
                network_id))
        return self._get_and_munchify('port', data)

    @_utils.valid_kwargs('name', 'admin_state_up', 'fixed_ips',
                         'security_groups', 'allowed_address_pairs',
                         'extra_dhcp_opts', 'device_owner', 'device_id',
                         'binding:vnic_type', 'binding:profile',
                         'port_security_enabled', 'qos_policy_id')
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
                  "subnet_id": "a78484c4-c380-4b47-85aa-21c51a2d8cbd"
                }, ...
              ]
        :param security_groups: List of security group UUIDs. (Optional)
        :param allowed_address_pairs: Allowed address pairs list (Optional)
            For example::

              [
                {
                  "ip_address": "23.23.23.1",
                  "mac_address": "fa:16:3e:c4:cd:3f"
                }, ...
              ]
        :param extra_dhcp_opts: Extra DHCP options. (Optional).
            For example::

              [
                {
                  "opt_name": "opt name1",
                  "opt_value": "value1"
                }, ...
              ]
        :param device_owner: The ID of the entity that uses this port.
            For example, a DHCP agent.  (Optional)
        :param device_id: The ID of the resource this port is attached to.
        :param binding vnic_type: The type of the created port. (Optional)
        :param port_security_enabled: The security port state created on
            the network. (Optional)
        :param qos_policy_id: The ID of the QoS policy to apply for port.

        :returns: a ``munch.Munch`` describing the updated port.

        :raises: OpenStackCloudException on operation error.
        """
        port = self.get_port(name_or_id=name_or_id)
        if port is None:
            raise exc.OpenStackCloudException(
                "failed to find port '{port}'".format(port=name_or_id))

        data = proxy._json_response(
            self.network.put(
                "/ports/{port_id}.json".format(port_id=port['id']),
                json={"port": kwargs}),
            error_message="Error updating port {0}".format(name_or_id))
        return self._get_and_munchify('port', data)

    def delete_port(self, name_or_id):
        """Delete a port

        :param name_or_id: ID or name of the port to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        port = self.get_port(name_or_id=name_or_id)
        if port is None:
            self.log.debug("Port %s not found for deleting", name_or_id)
            return False

        exceptions.raise_from_response(
            self.network.delete(
                "/ports/{port_id}.json".format(port_id=port['id'])),
            error_message="Error deleting port {0}".format(name_or_id))
        return True

    def _get_port_ids(self, name_or_id_list, filters=None):
        """
        Takes a list of port names or ids, retrieves ports and returns a list
        with port ids only.

        :param list[str] name_or_id_list: list of port names or ids
        :param dict filters: optional filters
        :raises: SDKException on multiple matches
        :raises: ResourceNotFound if a port is not found
        :return: list of port ids
        :rtype: list[str]
        """
        ids_list = []
        for name_or_id in name_or_id_list:
            port = self.get_port(name_or_id, filters)
            if not port:
                raise exceptions.ResourceNotFound(
                    'Port {id} not found'.format(id=name_or_id))
            ids_list.append(port['id'])
        return ids_list

    def _build_external_gateway_info(self, ext_gateway_net_id, enable_snat,
                                     ext_fixed_ips):
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
