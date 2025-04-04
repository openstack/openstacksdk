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

import ipaddress
import threading
import time
import warnings

from openstack.cloud import _utils
from openstack.cloud import exc
from openstack.cloud import meta
from openstack.cloud import openstackcloud
from openstack import exceptions
from openstack import proxy
from openstack import utils
from openstack import warnings as os_warnings


class NetworkCommonCloudMixin(openstackcloud._OpenStackCloudMixin):
    """Shared networking functions used by Network and Compute classes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._external_ipv4_names = self.config.get_external_ipv4_networks()
        self._internal_ipv4_names = self.config.get_internal_ipv4_networks()
        self._external_ipv6_names = self.config.get_external_ipv6_networks()
        self._internal_ipv6_names = self.config.get_internal_ipv6_networks()
        self._nat_destination = self.config.get_nat_destination()
        self._nat_source = self.config.get_nat_source()
        self._default_network = self.config.get_default_network()

        self._use_external_network = self.config.config.get(
            'use_external_network', True
        )
        self._use_internal_network = self.config.config.get(
            'use_internal_network', True
        )

        self._networks_lock = threading.Lock()
        self._reset_network_caches()

        self.private = self.config.config.get('private', False)

        self._floating_ip_source = self.config.config.get('floating_ip_source')
        if self._floating_ip_source:
            if self._floating_ip_source.lower() == 'none':
                self._floating_ip_source = None
            else:
                self._floating_ip_source = self._floating_ip_source.lower()

        self.secgroup_source = self.config.config['secgroup_source']

    # networks

    def use_external_network(self):
        return self._use_external_network

    def use_internal_network(self):
        return self._use_internal_network

    def _reset_network_caches(self):
        # Variables to prevent us from going through the network finding
        # logic again if we've done it once. This is different from just
        # the cached value, since "None" is a valid value to find.
        with self._networks_lock:
            self._external_ipv4_networks = []
            self._external_ipv4_floating_networks = []
            self._internal_ipv4_networks = []
            self._external_ipv6_networks = []
            self._internal_ipv6_networks = []
            self._nat_destination_network = None
            self._nat_source_network = None
            self._default_network_network = None
            self._network_list_stamp = False

    def _set_interesting_networks(self):
        external_ipv4_networks = []
        external_ipv4_floating_networks = []
        internal_ipv4_networks = []
        external_ipv6_networks = []
        internal_ipv6_networks = []
        nat_destination = None
        nat_source = None
        default_network = None

        all_subnets = None

        # Filter locally because we have an or condition
        try:
            # TODO(mordred): Rackspace exposes neutron but it does not
            # work. I think that overriding what the service catalog
            # reports should be a thing os-client-config should handle
            # in a vendor profile - but for now it does not. That means
            # this search_networks can just totally fail. If it does
            # though, that's fine, clearly the neutron introspection is
            # not going to work.
            if self.has_service('network'):
                all_networks = list(self.network.networks())
            else:
                all_networks = []
        except exceptions.SDKException:
            self._network_list_stamp = True
            return

        for network in all_networks:
            # External IPv4 networks
            if (
                network['name'] in self._external_ipv4_names
                or network['id'] in self._external_ipv4_names
            ):
                external_ipv4_networks.append(network)
            elif (
                (
                    network.is_router_external
                    or network.provider_physical_network
                )
                and network['name'] not in self._internal_ipv4_names
                and network['id'] not in self._internal_ipv4_names
            ):
                external_ipv4_networks.append(network)

            # Internal networks
            if (
                network['name'] in self._internal_ipv4_names
                or network['id'] in self._internal_ipv4_names
            ):
                internal_ipv4_networks.append(network)
            elif (
                not network.is_router_external
                and not network.provider_physical_network
                and network['name'] not in self._external_ipv4_names
                and network['id'] not in self._external_ipv4_names
            ):
                internal_ipv4_networks.append(network)

            # External networks
            if (
                network['name'] in self._external_ipv6_names
                or network['id'] in self._external_ipv6_names
            ):
                external_ipv6_networks.append(network)
            elif (
                network.is_router_external
                and network['name'] not in self._internal_ipv6_names
                and network['id'] not in self._internal_ipv6_names
            ):
                external_ipv6_networks.append(network)

            # Internal networks
            if (
                network['name'] in self._internal_ipv6_names
                or network['id'] in self._internal_ipv6_names
            ):
                internal_ipv6_networks.append(network)
            elif (
                not network.is_router_external
                and network['name'] not in self._external_ipv6_names
                and network['id'] not in self._external_ipv6_names
            ):
                internal_ipv6_networks.append(network)

            # External Floating IPv4 networks
            if self._nat_source in (network['name'], network['id']):
                if nat_source:
                    raise exceptions.SDKException(
                        'Multiple networks were found matching '
                        f'{self._nat_source} which is the network configured '
                        'to be the NAT source. Please check your '
                        'cloud resources. It is probably a good idea '
                        'to configure this network by ID rather than '
                        'by name.'
                    )
                external_ipv4_floating_networks.append(network)
                nat_source = network
            elif self._nat_source is None:
                if network.is_router_external:
                    external_ipv4_floating_networks.append(network)
                    nat_source = nat_source or network

            # NAT Destination
            if self._nat_destination in (network['name'], network['id']):
                if nat_destination:
                    raise exceptions.SDKException(
                        'Multiple networks were found matching '
                        f'{self._nat_destination} which is the network configured '
                        'to be the NAT destination. Please check your '
                        'cloud resources. It is probably a good idea '
                        'to configure this network by ID rather than '
                        'by name.'
                    )
                nat_destination = network
            elif self._nat_destination is None:
                # TODO(mordred) need a config value for floating
                # ips for this cloud so that we can skip this
                # No configured nat destination, we have to figured
                # it out.
                if all_subnets is None:
                    try:
                        if self.has_service('network'):
                            all_subnets = list(self.network.subnets())
                        else:
                            all_subnets = []
                    except exceptions.SDKException:
                        # Thanks Rackspace broken neutron
                        all_subnets = []

                for subnet in all_subnets:
                    # TODO(mordred) trap for detecting more than
                    # one network with a gateway_ip without a config
                    if (
                        'gateway_ip' in subnet
                        and subnet['gateway_ip']
                        and network['id'] == subnet['network_id']
                    ):
                        nat_destination = network
                        break

            # Default network
            if self._default_network in (network['name'], network['id']):
                if default_network:
                    raise exceptions.SDKException(
                        'Multiple networks were found matching '
                        f'{self._default_network} which is the network '
                        'configured to be the default interface '
                        'network. Please check your cloud resources. '
                        'It is probably a good idea '
                        'to configure this network by ID rather than '
                        'by name.'
                    )
                default_network = network

        # Validate config vs. reality
        for net_name in self._external_ipv4_names:
            if net_name not in [net['name'] for net in external_ipv4_networks]:
                raise exceptions.SDKException(
                    f"Networks: {net_name} was provided for external IPv4 "
                    "access and those networks could not be found"
                )

        for net_name in self._internal_ipv4_names:
            if net_name not in [net['name'] for net in internal_ipv4_networks]:
                raise exceptions.SDKException(
                    f"Networks: {net_name} was provided for internal IPv4 "
                    "access and those networks could not be found"
                )

        for net_name in self._external_ipv6_names:
            if net_name not in [net['name'] for net in external_ipv6_networks]:
                raise exceptions.SDKException(
                    f"Networks: {net_name} was provided for external IPv6 "
                    "access and those networks could not be found"
                )

        for net_name in self._internal_ipv6_names:
            if net_name not in [net['name'] for net in internal_ipv6_networks]:
                raise exceptions.SDKException(
                    f"Networks: {net_name} was provided for internal IPv6 "
                    "access and those networks could not be found"
                )

        if self._nat_destination and not nat_destination:
            raise exceptions.SDKException(
                f'Network {self._nat_destination} was configured to be the '
                'destination for inbound NAT but it could not be '
                'found'
            )

        if self._nat_source and not nat_source:
            raise exceptions.SDKException(
                f'Network {self._nat_source} was configured to be the '
                'source for inbound NAT but it could not be '
                'found'
            )

        if self._default_network and not default_network:
            raise exceptions.SDKException(
                f'Network {self._default_network} was configured to be the '
                'default network interface but it could not be '
                'found'
            )

        self._external_ipv4_networks = external_ipv4_networks
        self._external_ipv4_floating_networks = external_ipv4_floating_networks
        self._internal_ipv4_networks = internal_ipv4_networks
        self._external_ipv6_networks = external_ipv6_networks
        self._internal_ipv6_networks = internal_ipv6_networks
        self._nat_destination_network = nat_destination
        self._nat_source_network = nat_source
        self._default_network_network = default_network

    def _find_interesting_networks(self):
        if self._networks_lock.acquire():
            try:
                if self._network_list_stamp:
                    return
                if (
                    not self._use_external_network
                    and not self._use_internal_network
                ):
                    # Both have been flagged as skip - don't do a list
                    return
                if not self.has_service('network'):
                    return
                self._set_interesting_networks()
                self._network_list_stamp = True
            finally:
                self._networks_lock.release()

    def get_nat_destination(self):
        """Return the network that is configured to be the NAT destination.

        :returns: A network ``Network`` object if one is found
        """
        self._find_interesting_networks()
        return self._nat_destination_network

    def get_nat_source(self):
        """Return the network that is configured to be the NAT destination.

        :returns: A network ``Network`` object if one is found
        """
        self._find_interesting_networks()
        return self._nat_source_network

    def get_default_network(self):
        """Return the network that is configured to be the default interface.

        :returns: A network ``Network`` object if one is found
        """
        self._find_interesting_networks()
        return self._default_network_network

    def get_external_networks(self):
        """Return the networks that are configured to route northbound.

        This should be avoided in favor of the specific ipv4/ipv6 method,
        but is here for backwards compatibility.

        :returns: A list of network ``Network`` objects if any are found
        """
        self._find_interesting_networks()
        return list(self._external_ipv4_networks) + list(
            self._external_ipv6_networks
        )

    def get_internal_networks(self):
        """Return the networks that are configured to not route northbound.

        This should be avoided in favor of the specific ipv4/ipv6 method,
        but is here for backwards compatibility.

        :returns: A list of network ``Network`` objects if any are found
        """
        self._find_interesting_networks()
        return list(self._internal_ipv4_networks) + list(
            self._internal_ipv6_networks
        )

    def get_external_ipv4_networks(self):
        """Return the networks that are configured to route northbound.

        :returns: A list of network ``Network`` objects if any are found
        """
        self._find_interesting_networks()
        return self._external_ipv4_networks

    def get_external_ipv4_floating_networks(self):
        """Return the networks that are configured to route northbound.

        :returns: A list of network ``Network`` objects if any are found
        """
        self._find_interesting_networks()
        return self._external_ipv4_floating_networks

    def get_internal_ipv4_networks(self):
        """Return the networks that are configured to not route northbound.

        :returns: A list of network ``Network`` objects if any are found
        """
        self._find_interesting_networks()
        return self._internal_ipv4_networks

    def get_external_ipv6_networks(self):
        """Return the networks that are configured to route northbound.

        :returns: A list of network ``Network`` objects if any are found
        """
        self._find_interesting_networks()
        return self._external_ipv6_networks

    def get_internal_ipv6_networks(self):
        """Return the networks that are configured to not route northbound.

        :returns: A list of network ``Network`` objects if any are found
        """
        self._find_interesting_networks()
        return self._internal_ipv6_networks

    # floating IPs

    def search_floating_ip_pools(self, name=None, filters=None):
        pools = self.list_floating_ip_pools()
        return _utils._filter_list(pools, name, filters)

    # With Neutron, there are some cases in which full server side filtering is
    # not possible (e.g. nested attributes or list of objects) so we also need
    # to use the client-side filtering
    # The same goes for all neutron-related search/get methods!
    def search_floating_ips(self, id=None, filters=None):
        # `filters` could be a jmespath expression which Neutron server doesn't
        # understand, obviously.
        warnings.warn(
            "search_floating_ips is deprecated. Use search_resource instead.",
            os_warnings.RemovedInSDK50Warning,
        )
        if self._use_neutron_floating() and isinstance(filters, dict):
            return list(self.network.ips(**filters))
        else:
            floating_ips = self.list_floating_ips()
            return _utils._filter_list(floating_ips, id, filters)

    def _neutron_list_floating_ips(self, filters=None):
        if not filters:
            filters = {}
        data = list(self.network.ips(**filters))
        return data

    def _nova_list_floating_ips(self):
        try:
            data = proxy._json_response(self.compute.get('/os-floating-ips'))
        except exceptions.NotFoundException:
            return []
        return self._get_and_munchify('floating_ips', data)

    def get_floating_ip(self, id, filters=None):
        """Get a floating IP by ID

        :param id: ID of the floating IP.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A floating IP ``openstack.network.v2.floating_ip.FloatingIP``
            or None if no matching floating IP is found.

        """
        return _utils._get_entity(self, 'floating_ip', id, filters)

    def list_floating_ips(self, filters=None):
        """List all available floating IPs.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of floating IP
            ``openstack.network.v2.floating_ip.FloatingIP``.
        """
        if not filters:
            filters = {}

        if self._use_neutron_floating():
            try:
                return self._neutron_list_floating_ips(filters)
            except exceptions.NotFoundException as e:
                # Nova-network don't support server-side floating ips
                # filtering, so it's safer to return an empty list than
                # to fallback to Nova which may return more results that
                # expected.
                if filters:
                    self.log.error(
                        "Neutron returned NotFound for floating IPs, which "
                        "means this cloud doesn't have neutron floating ips. "
                        "openstacksdk can't fallback to trying Nova since "
                        "nova doesn't support server-side filtering when "
                        "listing floating ips and filters were given. "
                        "If you do not think openstacksdk should be "
                        "attempting to list floating IPs on neutron, it is "
                        "possible to control the behavior by setting "
                        "floating_ip_source to 'nova' or None for cloud "
                        "%(cloud)r in 'clouds.yaml'.",
                        {
                            'cloud': self.name,
                        },
                    )
                    # We can't fallback to nova because we push-down filters.
                    # We got a 404 which means neutron doesn't exist. If the
                    # user
                    return []

                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.",
                    {'msg': str(e)},
                )
                # Fall-through, trying with Nova
        else:
            if filters:
                raise ValueError(
                    "nova-network doesn't support server-side floating IPs "
                    "filtering. Use the 'search_floating_ips' method instead"
                )

        floating_ips = self._nova_list_floating_ips()
        return self._normalize_floating_ips(floating_ips)

    def list_floating_ip_pools(self):
        """List all available floating IP pools.

        NOTE: This function supports the nova-net view of the world. nova-net
        has been deprecated, so it's highly recommended to switch to using
        neutron. `get_external_ipv4_floating_networks` is what you should
        almost certainly be using.

        :returns: A list of floating IP pool objects
        """
        data = proxy._json_response(
            self.compute.get('os-floating-ip-pools'),
            error_message="Error fetching floating IP pool list",
        )
        pools = self._get_and_munchify('floating_ip_pools', data)
        return [{'name': p['name']} for p in pools]

    def get_floating_ip_by_id(self, id):
        """Get a floating ip by ID

        :param id: ID of the floating ip.
        :returns: A floating ip
            `:class:`~openstack.network.v2.floating_ip.FloatingIP`.
        """
        error_message = f"Error getting floating ip with ID {id}"

        if self._use_neutron_floating():
            fip = self.network.get_ip(id)
            return fip
        else:
            data = proxy._json_response(
                self.compute.get(f'/os-floating-ips/{id}'),
                error_message=error_message,
            )
            return self._normalize_floating_ip(
                self._get_and_munchify('floating_ip', data)
            )

    def _neutron_available_floating_ips(
        self, network=None, project_id=None, server=None
    ):
        """Get a floating IP from a network.

        Return a list of available floating IPs or allocate a new one and
        return it in a list of 1 element.

        :param network: A single network name or ID, or a list of them.
        :param server: (server) Server the Floating IP is for

        :returns: a list of floating IP addresses.
        :raises: :class:`~openstack.exceptions.BadRequestException` if an
            external network that meets the specified criteria cannot be found.
        """
        if project_id is None:
            # Make sure we are only listing floatingIPs allocated the current
            # tenant. This is the default behaviour of Nova
            project_id = self.current_project_id

        if network:
            if isinstance(network, str):
                network = [network]

            # Use given list to get first matching external network
            floating_network_id = None
            for net in network:
                for ext_net in self.get_external_ipv4_floating_networks():
                    if net in (ext_net['name'], ext_net['id']):
                        floating_network_id = ext_net['id']
                        break
                if floating_network_id:
                    break

            if floating_network_id is None:
                raise exceptions.NotFoundException(
                    f"unable to find external network {network}"
                )
        else:
            floating_network_id = self._get_floating_network_id()

        filters = {
            'port_id': None,
            'floating_network_id': floating_network_id,
            'project_id': project_id,
        }

        floating_ips = self.list_floating_ips()
        available_ips = _utils._filter_list(
            floating_ips, name_or_id=None, filters=filters
        )
        if available_ips:
            return available_ips

        # No available IP found or we didn't try
        # allocate a new Floating IP
        f_ip = self._neutron_create_floating_ip(
            network_id=floating_network_id, server=server
        )

        return [f_ip]

    def _nova_available_floating_ips(self, pool=None):
        """Get available floating IPs from a floating IP pool.

        Return a list of available floating IPs or allocate a new one and
        return it in a list of 1 element.

        :param pool: Nova floating IP pool name.

        :returns: a list of floating IP addresses.
        :raises: :class:`~openstack.exceptions.BadRequestException` if a
            floating IP pool is not specified and cannot be found.
        """

        with _utils.openstacksdk_exceptions(
            f"Unable to create floating IP in pool {pool}"
        ):
            if pool is None:
                pools = self.list_floating_ip_pools()
                if not pools:
                    raise exceptions.NotFoundException(
                        "unable to find a floating ip pool"
                    )
                pool = pools[0]['name']

            filters = {'instance_id': None, 'pool': pool}

            floating_ips = self._nova_list_floating_ips()
            available_ips = _utils._filter_list(
                floating_ips, name_or_id=None, filters=filters
            )
            if available_ips:
                return available_ips

            # No available IP found or we did not try.
            # Allocate a new Floating IP
            f_ip = self._nova_create_floating_ip(pool=pool)

            return [f_ip]

    def _find_floating_network_by_router(self):
        """Find the network providing floating ips by looking at routers."""
        for router in self.network.routers():
            if router['admin_state_up']:
                network_id = router.get('external_gateway_info', {}).get(
                    'network_id'
                )
                if network_id:
                    return network_id

    def available_floating_ip(self, network=None, server=None):
        """Get a floating IP from a network or a pool.

        Return the first available floating IP or allocate a new one.

        :param network: Name or ID of the network.
        :param server: Server the IP is for if known

        :returns: a (normalized) structure with a floating IP address
                  description.
        """
        if self._use_neutron_floating():
            try:
                f_ips = self._neutron_available_floating_ips(
                    network=network, server=server
                )
                return f_ips[0]
            except exceptions.NotFoundException as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.",
                    {'msg': str(e)},
                )
                # Fall-through, trying with Nova

        f_ips = self._normalize_floating_ips(
            self._nova_available_floating_ips(pool=network)
        )
        return f_ips[0]

    def _get_floating_network_id(self):
        # Get first existing external IPv4 network
        networks = self.get_external_ipv4_floating_networks()
        if networks:
            floating_network_id = networks[0]['id']
        else:
            floating_network = self._find_floating_network_by_router()
            if floating_network:
                floating_network_id = floating_network
            else:
                raise exceptions.NotFoundException(
                    "unable to find an external network"
                )
        return floating_network_id

    def create_floating_ip(
        self,
        network=None,
        server=None,
        fixed_address=None,
        nat_destination=None,
        port=None,
        wait=False,
        timeout=60,
    ):
        """Allocate a new floating IP from a network or a pool.

        :param network: Name or ID of the network
                        that the floating IP should come from.
        :param server: (optional) Server dict for the server to create
                       the IP for and to which it should be attached.
        :param fixed_address: (optional) Fixed IP to attach the floating
                              ip to.
        :param nat_destination: (optional) Name or ID of the network
                                that the fixed IP to attach the floating
                                IP to should be on.
        :param port: (optional) The port ID that the floating IP should be
                                attached to. Specifying a port conflicts
                                with specifying a server, fixed_address or
                                nat_destination.
        :param wait: (optional) Whether to wait for the IP to be active.
                     Defaults to False. Only applies if a server is
                     provided.
        :param timeout: (optional) How long to wait for the IP to be active.
                        Defaults to 60. Only applies if a server is
                        provided.

        :returns: a floating IP address
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if self._use_neutron_floating():
            try:
                return self._neutron_create_floating_ip(
                    network_name_or_id=network,
                    server=server,
                    fixed_address=fixed_address,
                    nat_destination=nat_destination,
                    port=port,
                    wait=wait,
                    timeout=timeout,
                )
            except exceptions.NotFoundException as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.",
                    {'msg': str(e)},
                )
                # Fall-through, trying with Nova

        if port:
            raise exceptions.SDKException(
                "This cloud uses nova-network which does not support "
                "arbitrary floating-ip/port mappings. Please nudge "
                "your cloud provider to upgrade the networking stack "
                "to neutron, or alternately provide the server, "
                "fixed_address and nat_destination arguments as appropriate"
            )
        # Else, we are using Nova network
        f_ips = self._normalize_floating_ips(
            [self._nova_create_floating_ip(pool=network)]
        )
        return f_ips[0]

    def _submit_create_fip(self, kwargs):
        # Split into a method to aid in test mocking
        return self.network.create_ip(**kwargs)

    def _neutron_create_floating_ip(
        self,
        network_name_or_id=None,
        server=None,
        fixed_address=None,
        nat_destination=None,
        port=None,
        wait=False,
        timeout=60,
        network_id=None,
    ):
        if not network_id:
            if network_name_or_id:
                try:
                    network = self.network.find_network(
                        network_name_or_id, ignore_missing=False
                    )
                except exceptions.NotFoundException:
                    raise exceptions.NotFoundException(
                        "unable to find network for floating ips with ID "
                        f"{network_name_or_id}"
                    )
                network_id = network['id']
            else:
                network_id = self._get_floating_network_id()
        kwargs = {
            'floating_network_id': network_id,
        }
        if not port:
            if server:
                (port_obj, fixed_ip_address) = self._nat_destination_port(
                    server,
                    fixed_address=fixed_address,
                    nat_destination=nat_destination,
                )
                if port_obj:
                    port = port_obj['id']
                if fixed_ip_address:
                    kwargs['fixed_ip_address'] = fixed_ip_address
        if port:
            kwargs['port_id'] = port

        fip = self._submit_create_fip(kwargs)
        fip_id = fip['id']

        if port:
            # The FIP is only going to become active in this context
            # when we've attached it to something, which only occurs
            # if we've provided a port as a parameter
            if wait:
                try:
                    for count in utils.iterate_timeout(
                        timeout,
                        "Timeout waiting for the floating IP to be ACTIVE",
                        wait=min(5, timeout),
                    ):
                        fip = self.get_floating_ip(fip_id)
                        if fip and fip['status'] == 'ACTIVE':
                            break
                except exceptions.ResourceTimeout:
                    self.log.error(
                        "Timed out on floating ip %(fip)s becoming active. "
                        "Deleting",
                        {'fip': fip_id},
                    )
                    try:
                        self.delete_floating_ip(fip_id)
                    except Exception as e:
                        self.log.error(
                            "FIP LEAK: Attempted to delete floating ip "
                            "%(fip)s but received %(exc)s exception: "
                            "%(err)s",
                            {'fip': fip_id, 'exc': e.__class__, 'err': str(e)},
                        )
                    raise
            if fip['port_id'] != port:
                if server:
                    raise exceptions.SDKException(
                        "Attempted to create FIP on port {port} for server "
                        "{server} but FIP has port {port_id}".format(
                            port=port,
                            port_id=fip['port_id'],
                            server=server['id'],
                        )
                    )
                else:
                    raise exceptions.SDKException(
                        f"Attempted to create FIP on port {port} "
                        "but something went wrong"
                    )
        return fip

    def _nova_create_floating_ip(self, pool=None):
        with _utils.openstacksdk_exceptions(
            f"Unable to create floating IP in pool {pool}"
        ):
            if pool is None:
                pools = self.list_floating_ip_pools()
                if not pools:
                    raise exceptions.NotFoundException(
                        "unable to find a floating ip pool"
                    )
                pool = pools[0]['name']

            data = proxy._json_response(
                self.compute.post('/os-floating-ips', json=dict(pool=pool))
            )
            pool_ip = self._get_and_munchify('floating_ip', data)
            # TODO(mordred) Remove this - it's just for compat
            data = proxy._json_response(
                self.compute.get(
                    '/os-floating-ips/{id}'.format(id=pool_ip['id'])
                )
            )
            return self._get_and_munchify('floating_ip', data)

    def delete_floating_ip(self, floating_ip_id, retry=1):
        """Deallocate a floating IP from a project.

        :param floating_ip_id: a floating IP address ID.
        :param retry: number of times to retry. Optional, defaults to 1,
            which is in addition to the initial delete call.
            A value of 0 will also cause no checking of results to
            occur.

        :returns: True if the IP address has been deleted, False if the IP
            address was not found.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        for count in range(0, max(0, retry) + 1):
            result = self._delete_floating_ip(floating_ip_id)

            if (retry == 0) or not result:
                return result

            # neutron sometimes returns success when deleting a floating
            # ip. That's awesome. SO - verify that the delete actually
            # worked. Some clouds will set the status to DOWN rather than
            # deleting the IP immediately. This is, of course, a bit absurd.
            f_ip = self.get_floating_ip(id=floating_ip_id)
            if not f_ip or f_ip['status'] == 'DOWN':
                return True

        raise exceptions.SDKException(
            "Attempted to delete Floating IP {ip} with ID {id} a total of "
            "{retry} times. Although the cloud did not indicate any errors "
            "the floating IP is still in existence. Aborting further "
            "operations.".format(
                id=floating_ip_id,
                ip=f_ip['floating_ip_address'],
                retry=retry + 1,
            )
        )

    def _delete_floating_ip(self, floating_ip_id):
        if self._use_neutron_floating():
            try:
                return self._neutron_delete_floating_ip(floating_ip_id)
            except exceptions.NotFoundException as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.",
                    {'msg': str(e)},
                )
        return self._nova_delete_floating_ip(floating_ip_id)

    def _neutron_delete_floating_ip(self, floating_ip_id):
        try:
            self.network.delete_ip(floating_ip_id, ignore_missing=False)
        except exceptions.NotFoundException:
            return False
        return True

    def _nova_delete_floating_ip(self, floating_ip_id):
        try:
            proxy._json_response(
                self.compute.delete(f'/os-floating-ips/{floating_ip_id}'),
                error_message=f'Unable to delete floating IP {floating_ip_id}',
            )
        except exceptions.NotFoundException:
            return False
        return True

    def delete_unattached_floating_ips(self, retry=1):
        """Safely delete unattached floating ips.

        If the cloud can safely purge any unattached floating ips without
        race conditions, do so.

        Safely here means a specific thing. It means that you are not running
        this while another process that might do a two step create/attach
        is running. You can safely run this  method while another process
        is creating servers and attaching floating IPs to them if either that
        process is using add_auto_ip from shade, or is creating the floating
        IPs by passing in a server to the create_floating_ip call.

        :param retry: number of times to retry. Optional, defaults to 1,
            which is in addition to the initial delete call.
            A value of 0 will also cause no checking of results to occur.

        :returns: Number of Floating IPs deleted, False if none
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        processed = []
        if self._use_neutron_floating():
            for ip in self.list_floating_ips():
                if not bool(ip.port_id):
                    processed.append(
                        self.delete_floating_ip(
                            floating_ip_id=ip['id'], retry=retry
                        )
                    )
        return len(processed) if all(processed) else False

    def _attach_ip_to_server(
        self,
        server,
        floating_ip,
        fixed_address=None,
        wait=False,
        timeout=60,
        skip_attach=False,
        nat_destination=None,
    ):
        """Attach a floating IP to a server.

        :param server: Server dict
        :param floating_ip: Floating IP dict to attach
        :param fixed_address: (optional) fixed address to which attach the
            floating IP to.
        :param wait: (optional) Wait for the address to appear as assigned
            to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
            See the ``wait`` parameter.
        :param skip_attach: (optional) Skip the actual attach and just do
            the wait. Defaults to False.
        :param nat_destination: The fixed network the server's port for the
            FIP to attach to will come from.

        :returns: The server ``openstack.compute.v2.server.Server``
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        # Short circuit if we're asking to attach an IP that's already
        # attached
        ext_ip = meta.get_server_ip(server, ext_tag='floating', public=True)
        if not ext_ip and floating_ip['port_id']:
            # When we came here from reuse_fip and created FIP it might be
            # already attached, but the server info might be also
            # old to check whether it belongs to us now, thus refresh
            # the server data and try again. There are some clouds, which
            # explicitely forbids FIP assign call if it is already assigned.
            server = self.compute.get_server(server['id'])
            ext_ip = meta.get_server_ip(
                server, ext_tag='floating', public=True
            )
        if ext_ip == floating_ip['floating_ip_address']:
            return server

        if self._use_neutron_floating():
            if not skip_attach:
                try:
                    self._neutron_attach_ip_to_server(
                        server=server,
                        floating_ip=floating_ip,
                        fixed_address=fixed_address,
                        nat_destination=nat_destination,
                    )
                except exceptions.NotFoundException as e:
                    self.log.debug(
                        "Something went wrong talking to neutron API: "
                        "'%(msg)s'. Trying with Nova.",
                        {'msg': str(e)},
                    )
                    # Fall-through, trying with Nova
        else:
            # Nova network
            self._nova_attach_ip_to_server(
                server_id=server['id'],
                floating_ip_id=floating_ip['id'],
                fixed_address=fixed_address,
            )

        if wait:
            # Wait for the address to be assigned to the server
            server_id = server['id']
            for _ in utils.iterate_timeout(
                timeout,
                "Timeout waiting for the floating IP to be attached.",
                wait=min(5, timeout),
            ):
                server = self.compute.get_server(server_id)
                ext_ip = meta.get_server_ip(
                    server, ext_tag='floating', public=True
                )
                if ext_ip == floating_ip['floating_ip_address']:
                    return server
        return server

    def _neutron_attach_ip_to_server(
        self, server, floating_ip, fixed_address=None, nat_destination=None
    ):
        # Find an available port
        (port, fixed_address) = self._nat_destination_port(
            server,
            fixed_address=fixed_address,
            nat_destination=nat_destination,
        )
        if not port:
            raise exceptions.SDKException(
                "unable to find a port for server {}".format(server['id'])
            )

        floating_ip_args = {'port_id': port['id']}
        if fixed_address is not None:
            floating_ip_args['fixed_ip_address'] = fixed_address

        return self.network.update_ip(floating_ip, **floating_ip_args)

    def _nova_attach_ip_to_server(
        self, server_id, floating_ip_id, fixed_address=None
    ):
        f_ip = self.get_floating_ip(id=floating_ip_id)
        if f_ip is None:
            raise exceptions.SDKException(
                f"unable to find floating IP {floating_ip_id}"
            )
        error_message = (
            f"Error attaching IP {floating_ip_id} to instance {server_id}"
        )
        body = {'address': f_ip['floating_ip_address']}
        if fixed_address:
            body['fixed_address'] = fixed_address
        return proxy._json_response(
            self.compute.post(
                f'/servers/{server_id}/action',
                json=dict(addFloatingIp=body),
            ),
            error_message=error_message,
        )

    def detach_ip_from_server(self, server_id, floating_ip_id):
        """Detach a floating IP from a server.

        :param server_id: ID of a server.
        :param floating_ip_id: Id of the floating IP to detach.

        :returns: True if the IP has been detached, or False if the IP wasn't
            attached to any server.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if self._use_neutron_floating():
            try:
                return self._neutron_detach_ip_from_server(
                    server_id=server_id, floating_ip_id=floating_ip_id
                )
            except exceptions.NotFoundException as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.",
                    {'msg': str(e)},
                )
                # Fall-through, trying with Nova

        # Nova network
        self._nova_detach_ip_from_server(
            server_id=server_id, floating_ip_id=floating_ip_id
        )

    def _neutron_detach_ip_from_server(self, server_id, floating_ip_id):
        f_ip = self.get_floating_ip(id=floating_ip_id)
        if f_ip is None or not bool(f_ip.port_id):
            return False
        try:
            self.network.update_ip(floating_ip_id, port_id=None)
        except exceptions.SDKException:
            raise exceptions.SDKException(
                f"Error detaching IP {floating_ip_id} from server {server_id}"
            )

        return True

    def _nova_detach_ip_from_server(self, server_id, floating_ip_id):
        f_ip = self.get_floating_ip(id=floating_ip_id)
        if f_ip is None:
            raise exceptions.SDKException(
                f"unable to find floating IP {floating_ip_id}"
            )
        error_message = (
            f"Error detaching IP {floating_ip_id} from instance {server_id}"
        )
        return proxy._json_response(
            self.compute.post(
                f'/servers/{server_id}/action',
                json=dict(
                    removeFloatingIp=dict(address=f_ip['floating_ip_address'])
                ),
            ),
            error_message=error_message,
        )

        return True

    def _add_ip_from_pool(
        self,
        server,
        network,
        fixed_address=None,
        reuse=True,
        wait=False,
        timeout=60,
        nat_destination=None,
    ):
        """Add a floating IP to a server from a given pool

        This method reuses available IPs, when possible, or allocate new IPs
        to the current tenant.
        The floating IP is attached to the given fixed address or to the
        first server port/fixed address

        :param server: Server dict
        :param network: Name or ID of the network.
        :param fixed_address: a fixed address
        :param reuse: Try to reuse existing ips. Defaults to True.
        :param wait: (optional) Wait for the address to appear as assigned
            to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
            See the ``wait`` parameter.
        :param nat_destination: (optional) the name of the network of the
            port to associate with the floating ip.

        :returns: the updated server ``openstack.compute.v2.server.Server``
        """
        if reuse:
            f_ip = self.available_floating_ip(network=network)
        else:
            start_time = time.time()
            f_ip = self.create_floating_ip(
                server=server,
                network=network,
                nat_destination=nat_destination,
                fixed_address=fixed_address,
                wait=wait,
                timeout=timeout,
            )
            timeout = timeout - (time.time() - start_time)
            server = self.compute.get_server(server.id)

        # We run attach as a second call rather than in the create call
        # because there are code flows where we will not have an attached
        # FIP yet. However, even if it was attached in the create, we run
        # the attach function below to get back the server dict refreshed
        # with the FIP information.
        return self._attach_ip_to_server(
            server=server,
            floating_ip=f_ip,
            fixed_address=fixed_address,
            wait=wait,
            timeout=timeout,
            nat_destination=nat_destination,
        )

    def add_ip_list(
        self,
        server,
        ips,
        wait=False,
        timeout=60,
        fixed_address=None,
        nat_destination=None,
    ):
        """Attach a list of IPs to a server.

        :param server: a server object
        :param ips: list of floating IP addresses or a single address
        :param wait: (optional) Wait for the address to appear as assigned
            to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
            See the ``wait`` parameter.
        :param fixed_address: (optional) Fixed address of the server to
            attach the IP to
        :param nat_destination: (optional) Name or ID of the network that
            the fixed IP to attach the floating IP should be on

        :returns: The updated server ``openstack.compute.v2.server.Server``
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """

        if type(ips) is not list:
            ips = [ips]

        for ip in ips:
            f_ip = self.get_floating_ip(
                id=None, filters={'floating_ip_address': ip}
            )
            server = self._attach_ip_to_server(
                server=server,
                floating_ip=f_ip,
                wait=wait,
                timeout=timeout,
                fixed_address=fixed_address,
                nat_destination=nat_destination,
            )
        return server

    def add_auto_ip(self, server, wait=False, timeout=60, reuse=True):
        """Add a floating IP to a server.

        This method is intended for basic usage. For advanced network
        architecture (e.g. multiple external networks or servers with multiple
        interfaces), use other floating IP methods.

        This method can reuse available IPs, or allocate new IPs to the current
        project.

        :param server: a server dictionary.
        :param reuse: Whether or not to attempt to reuse IPs, defaults
            to True.
        :param wait: (optional) Wait for the address to appear as assigned
            to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
            See the ``wait`` parameter.
        :param reuse: Try to reuse existing ips. Defaults to True.

        :returns: Floating IP address attached to server.
        """
        server = self._add_auto_ip(
            server, wait=wait, timeout=timeout, reuse=reuse
        )
        return server['interface_ip'] or None

    def _add_auto_ip(self, server, wait=False, timeout=60, reuse=True):
        skip_attach = False
        created = False
        if reuse:
            f_ip = self.available_floating_ip(server=server)
        else:
            start_time = time.time()
            f_ip = self.create_floating_ip(
                server=server, wait=wait, timeout=timeout
            )
            timeout = timeout - (time.time() - start_time)
            if server:
                # This gets passed in for both nova and neutron
                # but is only meaningful for the neutron logic branch
                skip_attach = True
            created = True

        try:
            # We run attach as a second call rather than in the create call
            # because there are code flows where we will not have an attached
            # FIP yet. However, even if it was attached in the create, we run
            # the attach function below to get back the server dict refreshed
            # with the FIP information.
            return self._attach_ip_to_server(
                server=server,
                floating_ip=f_ip,
                wait=wait,
                timeout=timeout,
                skip_attach=skip_attach,
            )
        except exceptions.ResourceTimeout:
            if self._use_neutron_floating() and created:
                # We are here because we created an IP on the port
                # It failed. Delete so as not to leak an unmanaged
                # resource
                self.log.error(
                    "Timeout waiting for floating IP to become "
                    "active. Floating IP %(ip)s:%(id)s was created for "
                    "server %(server)s but is being deleted due to "
                    "activation failure.",
                    {
                        'ip': f_ip['floating_ip_address'],
                        'id': f_ip['id'],
                        'server': server['id'],
                    },
                )
                try:
                    self.delete_floating_ip(f_ip['id'])
                except Exception as e:
                    self.log.error(
                        "FIP LEAK: Attempted to delete floating ip "
                        "%(fip)s but received %(exc)s exception: %(err)s",
                        {'fip': f_ip['id'], 'exc': e.__class__, 'err': str(e)},
                    )
                    raise e
            raise

    def add_ips_to_server(
        self,
        server,
        auto_ip=True,
        ips=None,
        ip_pool=None,
        wait=False,
        timeout=60,
        reuse=True,
        fixed_address=None,
        nat_destination=None,
    ):
        if ip_pool:
            server = self._add_ip_from_pool(
                server,
                ip_pool,
                reuse=reuse,
                wait=wait,
                timeout=timeout,
                fixed_address=fixed_address,
                nat_destination=nat_destination,
            )
        elif ips:
            server = self.add_ip_list(
                server,
                ips,
                wait=wait,
                timeout=timeout,
                fixed_address=fixed_address,
                nat_destination=nat_destination,
            )
        elif auto_ip:
            if self._needs_floating_ip(server, nat_destination):
                server = self._add_auto_ip(
                    server, wait=wait, timeout=timeout, reuse=reuse
                )
        return server

    def _needs_floating_ip(self, server, nat_destination):
        """Figure out if auto_ip should add a floating ip to this server.

        If the server has a floating ip it does not need another one.

        If the server does not have a fixed ip address it does not need a
        floating ip.

        If self.private then the server does not need a floating ip.

        If the cloud runs nova, and the server has a private address and not a
        public address, then the server needs a floating ip.

        If the server has a fixed ip address and no floating ip address and the
        cloud has a network from which floating IPs come that is connected via
        a router to the network from which the fixed ip address came,
        then the server needs a floating ip.

        If the server has a fixed ip address and no floating ip address and the
        cloud does not have a network from which floating ips come, or it has
        one but that network is not connected to the network from which
        the server's fixed ip address came via a router, then the
        server does not need a floating ip.
        """
        if not self._has_floating_ips():
            return False

        if server['addresses'] is None:
            # fetch missing server details, e.g. because
            # meta.add_server_interfaces() was not called
            server = self.compute.get_server(server)

        if server['public_v4'] or any(
            [
                any(
                    [
                        address['OS-EXT-IPS:type'] == 'floating'
                        for address in addresses
                    ]
                )
                for addresses in (server['addresses'] or {}).values()
            ]
        ):
            return False

        if not server['private_v4'] and not any(
            [
                any(
                    [
                        address['OS-EXT-IPS:type'] == 'fixed'
                        for address in addresses
                    ]
                )
                for addresses in (server['addresses'] or {}).values()
            ]
        ):
            return False

        if self.private:
            return False

        if not self.has_service('network'):
            return True

        # No floating ip network - no FIPs
        try:
            self._get_floating_network_id()
        except exceptions.SDKException:
            return False

        (port_obj, fixed_ip_address) = self._nat_destination_port(
            server, nat_destination=nat_destination
        )

        if not port_obj or not fixed_ip_address:
            return False

        return True

    def _nat_destination_port(
        self, server, fixed_address=None, nat_destination=None
    ):
        """Returns server port that is on a nat_destination network

        Find a port attached to the server which is on a network which
        has a subnet which can be the destination of NAT. Such a network
        is referred to in shade as a "nat_destination" network. So this
        then is a function which returns a port on such a network that is
        associated with the given server.

        :param server: Server dict.
        :param fixed_address: Fixed ip address of the port
        :param nat_destination: Name or ID of the network of the port.
        """
        ports = list(self.network.ports(device_id=server['id']))
        if not ports:
            return (None, None)

        port = None
        if not fixed_address:
            if len(ports) > 1:
                if nat_destination:
                    nat_network = self.network.find_network(
                        nat_destination, ignore_missing=True
                    )
                    if not nat_network:
                        raise exceptions.SDKException(
                            f'NAT Destination {nat_destination} was '
                            f'configured but not found on the cloud. Please '
                            f'check your config and your cloud and try again.'
                        )
                else:
                    nat_network = self.get_nat_destination()

                if not nat_network:
                    raise exceptions.SDKException(
                        f'Multiple ports were found for server {server["id"]} '
                        f'but none of the networks are a valid NAT '
                        f'destination, so it is impossible to add a '
                        f'floating IP. If you have a network that is a valid '
                        f'destination for NAT and we could not find it, '
                        f'please file a bug. But also configure the '
                        f'nat_destination property of the networks list in '
                        f'your clouds.yaml file. If you do not have a '
                        f'clouds.yaml file, please make one - your setup '
                        f'is complicated.'
                    )

                maybe_ports = []
                for maybe_port in ports:
                    if maybe_port['network_id'] == nat_network['id']:
                        maybe_ports.append(maybe_port)
                if not maybe_ports:
                    raise exceptions.SDKException(
                        f'No port on server {server["id"]} was found matching '
                        f'your NAT destination network {nat_network["name"]}.'
                        f'Please check your config'
                    )
                ports = maybe_ports

            # Select the most recent available IPv4 address
            # To do this, sort the ports in reverse order by the created_at
            # field which is a string containing an ISO DateTime (which
            # thankfully sort properly) This way the most recent port created,
            # if there are more than one, will be the arbitrary port we
            # select.
            for port in sorted(
                ports, key=lambda p: p.get('created_at', 0), reverse=True
            ):
                for address in port.get('fixed_ips', list()):
                    try:
                        ip = ipaddress.ip_address(address['ip_address'])
                    except Exception:  # noqa: S112
                        # the address might be unset; ignore if so
                        continue
                    if ip.version == 4:
                        fixed_address = address['ip_address']
                        return port, fixed_address
            raise exceptions.SDKException(
                "unable to find a free fixed IPv4 address for server "
                "{}".format(server['id'])
            )
        # unfortunately a port can have more than one fixed IP:
        # we can't use the search_ports filtering for fixed_address as
        # they are contained in a list. e.g.
        #
        #   "fixed_ips": [
        #     {
        #       "subnet_id": "008ba151-0b8c-4a67-98b5-0d2b87666062",
        #       "ip_address": "172.24.4.2"
        #     }
        #   ]
        #
        # Search fixed_address
        for p in ports:
            for fixed_ip in p['fixed_ips']:
                if fixed_address == fixed_ip['ip_address']:
                    return (p, fixed_address)
        return (None, None)

    def _has_floating_ips(self):
        if not self._floating_ip_source:
            return False
        else:
            return self._floating_ip_source in ('nova', 'neutron')

    def _use_neutron_floating(self):
        return (
            self.has_service('network')
            and self._floating_ip_source == 'neutron'
        )

    def _normalize_floating_ips(self, ips):
        """Normalize the structure of floating IPs

        Unfortunately, not all the Neutron floating_ip attributes are available
        with Nova and not all Nova floating_ip attributes are available with
        Neutron.
        This function extract attributes that are common to Nova and Neutron
        floating IP resource.
        If the whole structure is needed inside openstacksdk there are private
        methods that returns "original" objects (e.g.
        _neutron_allocate_floating_ip)

        :param list ips: A list of Neutron floating IPs.

        :returns:
            A list of normalized dicts with the following attributes::

                [
                    {
                        "id": "this-is-a-floating-ip-id",
                        "fixed_ip_address": "192.0.2.10",
                        "floating_ip_address": "198.51.100.10",
                        "network": "this-is-a-net-or-pool-id",
                        "attached": True,
                        "status": "ACTIVE",
                    },
                    ...,
                ]

        """
        return [self._normalize_floating_ip(ip) for ip in ips]

    def _normalize_floating_ip(self, ip):
        # Copy incoming floating ip because of shared dicts in unittests
        # Only import munch when we really need it

        location = self._get_current_location(project_id=ip.get('owner'))
        # This copy is to keep things from getting epically weird in tests
        ip = ip.copy()

        ret = utils.Munch(location=location)

        fixed_ip_address = ip.pop('fixed_ip_address', ip.pop('fixed_ip', None))
        floating_ip_address = ip.pop('floating_ip_address', ip.pop('ip', None))
        network_id = ip.pop(
            'floating_network_id', ip.pop('network', ip.pop('pool', None))
        )
        project_id = ip.pop('tenant_id', '')
        project_id = ip.pop('project_id', project_id)

        instance_id = ip.pop('instance_id', None)
        router_id = ip.pop('router_id', None)
        id = ip.pop('id')
        port_id = ip.pop('port_id', None)
        created_at = ip.pop('created_at', None)
        updated_at = ip.pop('updated_at', None)
        # Note - description may not always be on the underlying cloud.
        # Normalizing it here is easy - what do we do when people want to
        # set a description?
        description = ip.pop('description', '')
        revision_number = ip.pop('revision_number', None)

        if self._use_neutron_floating():
            attached = bool(port_id)
            status = ip.pop('status', 'UNKNOWN')
        else:
            attached = bool(instance_id)
            # In neutron's terms, Nova floating IPs are always ACTIVE
            status = 'ACTIVE'

        ret = utils.Munch(
            attached=attached,
            fixed_ip_address=fixed_ip_address,
            floating_ip_address=floating_ip_address,
            id=id,
            location=self._get_current_location(project_id=project_id),
            network=network_id,
            port=port_id,
            router=router_id,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            revision_number=revision_number,
            properties=ip.copy(),
        )
        # Backwards compat
        if not self.strict_mode:
            ret['port_id'] = port_id
            ret['router_id'] = router_id
            ret['project_id'] = project_id
            ret['tenant_id'] = project_id
            ret['floating_network_id'] = network_id
            for key, val in ret['properties'].items():
                ret.setdefault(key, val)

        return ret

    # security groups

    def search_security_groups(self, name_or_id=None, filters=None):
        # `filters` could be a dict or a jmespath (str)
        groups = self.list_security_groups(
            filters=filters if isinstance(filters, dict) else None
        )
        return _utils._filter_list(groups, name_or_id, filters)

    def list_security_groups(self, filters=None):
        """List all available security groups.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of security group
            ``openstack.network.v2.security_group.SecurityGroup``.

        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        if not filters:
            filters = {}

        # Handle neutron security groups
        if self._use_neutron_secgroups():
            # pass filters dict to the list to filter as much as possible on
            # the server side
            return list(self.network.security_groups(**filters))
        # Handle nova security groups
        else:
            data = proxy._json_response(
                self.compute.get('/os-security-groups', params=filters)
            )
            return self._normalize_secgroups(
                self._get_and_munchify('security_groups', data)
            )

    def get_security_group(self, name_or_id, filters=None):
        """Get a security group by name or ID.

        :param name_or_id: Name or ID of the security group.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A security group
            ``openstack.network.v2.security_group.SecurityGroup``
            or None if no matching security group is found.

        """
        return _utils._get_entity(self, 'security_group', name_or_id, filters)

    def get_security_group_by_id(self, id):
        """Get a security group by ID

        :param id: ID of the security group.
        :returns: A security group
            ``openstack.network.v2.security_group.SecurityGroup``.
        """
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )
        error_message = f"Error getting security group with ID {id}"
        if self._use_neutron_secgroups():
            return self.network.get_security_group(id)
        else:
            data = proxy._json_response(
                self.compute.get(f'/os-security-groups/{id}'),
                error_message=error_message,
            )
            return self._normalize_secgroup(
                self._get_and_munchify('security_group', data)
            )

    def create_security_group(
        self, name, description, project_id=None, stateful=None
    ):
        """Create a new security group

        :param string name: A name for the security group.
        :param string description: Describes the security group.
        :param string project_id:
            Specify the project ID this security group will be created
            on (admin-only).
        :param string stateful: Whether the security group is stateful or not.

        :returns: A ``openstack.network.v2.security_group.SecurityGroup``
            representing the new security group.

        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
            not supported on this cloud.
        """

        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        security_group_json = {'name': name, 'description': description}
        if stateful is not None:
            security_group_json['stateful'] = stateful
        if project_id is not None:
            security_group_json['tenant_id'] = project_id
        if self._use_neutron_secgroups():
            return self.network.create_security_group(**security_group_json)
        else:
            data = proxy._json_response(
                self.compute.post(
                    '/os-security-groups',
                    json={'security_group': security_group_json},
                )
            )
            return self._normalize_secgroup(
                self._get_and_munchify('security_group', data)
            )

    def delete_security_group(self, name_or_id):
        """Delete a security group

        :param string name_or_id: The name or unique ID of the security group.

        :returns: True if delete succeeded, False otherwise.

        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
            not supported on this cloud.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        # TODO(mordred): Let's come back and stop doing a GET before we do
        #                the delete.
        secgroup = self.get_security_group(name_or_id)
        if secgroup is None:
            self.log.debug(
                'Security group %s not found for deleting', name_or_id
            )
            return False

        if self._use_neutron_secgroups():
            self.network.delete_security_group(
                secgroup['id'], ignore_missing=False
            )
            return True

        else:
            proxy._json_response(
                self.compute.delete(
                    '/os-security-groups/{id}'.format(id=secgroup['id'])
                )
            )
            return True

    @_utils.valid_kwargs('name', 'description', 'stateful')
    def update_security_group(self, name_or_id, **kwargs):
        """Update a security group

        :param string name_or_id: Name or ID of the security group to update.
        :param string name: New name for the security group.
        :param string description: New description for the security group.

        :returns: A ``openstack.network.v2.security_group.SecurityGroup``
            describing the updated security group.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        group = self.get_security_group(name_or_id)

        if group is None:
            raise exceptions.SDKException(
                f"Security group {name_or_id} not found."
            )

        if self._use_neutron_secgroups():
            return self.network.update_security_group(group['id'], **kwargs)
        else:
            for key in ('name', 'description'):
                kwargs.setdefault(key, group[key])
            data = proxy._json_response(
                self.compute.put(
                    '/os-security-groups/{id}'.format(id=group['id']),
                    json={'security_group': kwargs},
                )
            )
            return self._normalize_secgroup(
                self._get_and_munchify('security_group', data)
            )

    def create_security_group_rule(
        self,
        secgroup_name_or_id,
        port_range_min=None,
        port_range_max=None,
        protocol=None,
        remote_ip_prefix=None,
        remote_group_id=None,
        remote_address_group_id=None,
        direction='ingress',
        ethertype='IPv4',
        project_id=None,
        description=None,
    ):
        """Create a new security group rule

        :param string secgroup_name_or_id:
            The security group name or ID to associate with this security
            group rule. If a non-unique group name is given, an exception
            is raised.
        :param int port_range_min:
            The minimum port number in the range that is matched by the
            security group rule. If the protocol is TCP or UDP, this value
            must be less than or equal to the port_range_max attribute value.
            If nova is used by the cloud provider for security groups, then
            a value of None will be transformed to -1.
        :param int port_range_max:
            The maximum port number in the range that is matched by the
            security group rule. The port_range_min attribute constrains the
            port_range_max attribute. If nova is used by the cloud provider
            for security groups, then a value of None will be transformed
            to -1.
        :param string protocol:
            The protocol that is matched by the security group rule. Valid
            values are None, tcp, udp, and icmp.
        :param string remote_ip_prefix:
            The remote IP prefix to be associated with this security group
            rule. This attribute matches the specified IP prefix as the
            source IP address of the IP packet.
        :param string remote_group_id:
            The remote group ID to be associated with this security group
            rule.
        :param string remote_address_group_id:
            The remote address group ID to be associated with this security
            group rule.
        :param string direction:
            Ingress or egress: The direction in which the security group
            rule is applied. For a compute instance, an ingress security
            group rule is applied to incoming (ingress) traffic for that
            instance. An egress rule is applied to traffic leaving the
            instance.
        :param string ethertype:
            Must be IPv4 or IPv6, and addresses represented in CIDR must
            match the ingress or egress rules.
        :param string project_id:
            Specify the project ID this security group will be created
            on (admin-only).
        :param string description:
            Description of the rule, max 255 characters.

        :returns: A ``openstack.network.v2.security_group.SecurityGroup``
            representing the new security group rule.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        secgroup = self.get_security_group(secgroup_name_or_id)
        if not secgroup:
            raise exceptions.SDKException(
                f"Security group {secgroup_name_or_id} not found."
            )

        if self._use_neutron_secgroups():
            # NOTE: Nova accepts -1 port numbers, but Neutron accepts None
            # as the equivalent value.
            rule_def = {
                'security_group_id': secgroup['id'],
                'port_range_min': (
                    None if port_range_min == -1 else port_range_min
                ),
                'port_range_max': (
                    None if port_range_max == -1 else port_range_max
                ),
                'protocol': protocol,
                'remote_ip_prefix': remote_ip_prefix,
                'remote_group_id': remote_group_id,
                'remote_address_group_id': remote_address_group_id,
                'direction': direction,
                'ethertype': ethertype,
            }
            if project_id is not None:
                rule_def['tenant_id'] = project_id
            if description is not None:
                rule_def["description"] = description
            return self.network.create_security_group_rule(**rule_def)
        else:
            # NOTE: Neutron accepts None for protocol. Nova does not.
            if protocol is None:
                raise exceptions.SDKException('Protocol must be specified')

            if direction == 'egress':
                self.log.debug(
                    'Rule creation failed: Nova does not support egress rules'
                )
                raise exceptions.SDKException('No support for egress rules')

            # NOTE: Neutron accepts None for ports, but Nova requires -1
            # as the equivalent value for ICMP.
            #
            # For TCP/UDP, if both are None, Neutron allows this and Nova
            # represents this as all ports (1-65535). Nova does not accept
            # None values, so to hide this difference, we will automatically
            # convert to the full port range. If only a single port value is
            # specified, it will error as normal.
            if protocol == 'icmp':
                if port_range_min is None:
                    port_range_min = -1
                if port_range_max is None:
                    port_range_max = -1
            elif protocol in ['tcp', 'udp']:
                if port_range_min is None and port_range_max is None:
                    port_range_min = 1
                    port_range_max = 65535

            security_group_rule_dict = dict(
                security_group_rule=dict(
                    parent_group_id=secgroup['id'],
                    ip_protocol=protocol,
                    from_port=port_range_min,
                    to_port=port_range_max,
                    cidr=remote_ip_prefix,
                    group_id=remote_group_id,
                )
            )
            if project_id is not None:
                security_group_rule_dict['security_group_rule'][
                    'tenant_id'
                ] = project_id
            data = proxy._json_response(
                self.compute.post(
                    '/os-security-group-rules', json=security_group_rule_dict
                )
            )
            return self._normalize_secgroup_rule(
                self._get_and_munchify('security_group_rule', data)
            )

    def delete_security_group_rule(self, rule_id):
        """Delete a security group rule

        :param string rule_id: The unique ID of the security group rule.

        :returns: True if delete succeeded, False otherwise.

        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
            not supported on this cloud.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        if self._use_neutron_secgroups():
            self.network.delete_security_group_rule(
                rule_id, ignore_missing=False
            )
            return True

        else:
            try:
                exceptions.raise_from_response(
                    self.compute.delete(f'/os-security-group-rules/{rule_id}')
                )
            except exceptions.NotFoundException:
                return False

            return True

    def _has_secgroups(self):
        if not self.secgroup_source:
            return False
        else:
            return self.secgroup_source.lower() in ('nova', 'neutron')

    def _use_neutron_secgroups(self):
        return (
            self.has_service('network') and self.secgroup_source == 'neutron'
        )

    def _normalize_secgroups(self, groups):
        """Normalize the structure of security groups

        This makes security group dicts, as returned from nova, look like the
        security group dicts as returned from neutron. This does not make them
        look exactly the same, but it's pretty close.

        :param list groups: A list of security group dicts.

        :returns: A list of normalized dicts.
        """
        ret = []
        for group in groups:
            ret.append(self._normalize_secgroup(group))
        return ret

    # TODO(stephenfin): Remove this once we get rid of support for nova
    # secgroups
    def _normalize_secgroup(self, group):
        ret = utils.Munch()
        # Copy incoming group because of shared dicts in unittests
        group = group.copy()

        # Discard noise
        self._remove_novaclient_artifacts(group)

        rules = self._normalize_secgroup_rules(
            group.pop('security_group_rules', group.pop('rules', []))
        )
        project_id = group.pop('tenant_id', '')
        project_id = group.pop('project_id', project_id)

        ret['location'] = self._get_current_location(project_id=project_id)
        ret['id'] = group.pop('id')
        ret['name'] = group.pop('name')
        ret['security_group_rules'] = rules
        ret['description'] = group.pop('description')
        ret['properties'] = group

        if self._use_neutron_secgroups():
            ret['stateful'] = group.pop('stateful', True)

        # Backwards compat with Neutron
        if not self.strict_mode:
            ret['tenant_id'] = project_id
            ret['project_id'] = project_id
            for key, val in ret['properties'].items():
                ret.setdefault(key, val)

        return ret

    # TODO(stephenfin): Remove this once we get rid of support for nova
    # secgroups
    def _normalize_secgroup_rules(self, rules):
        """Normalize the structure of nova security group rules

        Note that nova uses -1 for non-specific port values, but neutron
        represents these with None.

        :param list rules: A list of security group rule dicts.

        :returns: A list of normalized dicts.
        """
        ret = []
        for rule in rules:
            ret.append(self._normalize_secgroup_rule(rule))
        return ret

    # TODO(stephenfin): Remove this once we get rid of support for nova
    # secgroups
    def _normalize_secgroup_rule(self, rule):
        ret = utils.Munch()
        # Copy incoming rule because of shared dicts in unittests
        rule = rule.copy()

        ret['id'] = rule.pop('id')
        ret['direction'] = rule.pop('direction', 'ingress')
        ret['ethertype'] = rule.pop('ethertype', 'IPv4')
        port_range_min = rule.get(
            'port_range_min', rule.pop('from_port', None)
        )
        if port_range_min == -1:
            port_range_min = None
        if port_range_min is not None:
            port_range_min = int(port_range_min)
        ret['port_range_min'] = port_range_min
        port_range_max = rule.pop('port_range_max', rule.pop('to_port', None))
        if port_range_max == -1:
            port_range_max = None
        if port_range_min is not None:
            port_range_min = int(port_range_min)
        ret['port_range_max'] = port_range_max
        ret['protocol'] = rule.pop('protocol', rule.pop('ip_protocol', None))
        ret['remote_ip_prefix'] = rule.pop(
            'remote_ip_prefix', rule.pop('ip_range', {}).get('cidr', None)
        )
        ret['security_group_id'] = rule.pop(
            'security_group_id', rule.pop('parent_group_id', None)
        )
        ret['remote_group_id'] = rule.pop('remote_group_id', None)
        project_id = rule.pop('tenant_id', '')
        project_id = rule.pop('project_id', project_id)
        ret['location'] = self._get_current_location(project_id=project_id)
        ret['properties'] = rule

        # Backwards compat with Neutron
        if not self.strict_mode:
            ret['tenant_id'] = project_id
            ret['project_id'] = project_id
            for key, val in ret['properties'].items():
                ret.setdefault(key, val)
        return ret

    def _remove_novaclient_artifacts(self, item):
        # Remove novaclient artifacts
        item.pop('links', None)
        item.pop('NAME_ATTR', None)
        item.pop('HUMAN_ID', None)
        item.pop('human_id', None)
        item.pop('request_ids', None)
        item.pop('x_openstack_request_ids', None)
