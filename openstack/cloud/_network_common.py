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
import threading
import types  # noqa

from openstack.cloud import exc
from openstack.cloud import _normalize


class NetworkCommonCloudMixin(_normalize.Normalizer):
    """Shared networking functions used by FloatingIP, Network, Compute classes
    """

    def __init__(self):
        self._external_ipv4_names = self.config.get_external_ipv4_networks()
        self._internal_ipv4_names = self.config.get_internal_ipv4_networks()
        self._external_ipv6_names = self.config.get_external_ipv6_networks()
        self._internal_ipv6_names = self.config.get_internal_ipv6_networks()
        self._nat_destination = self.config.get_nat_destination()
        self._nat_source = self.config.get_nat_source()
        self._default_network = self.config.get_default_network()

        self._use_external_network = self.config.config.get(
            'use_external_network', True)
        self._use_internal_network = self.config.config.get(
            'use_internal_network', True)

        self._networks_lock = threading.Lock()
        self._reset_network_caches()

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
            all_networks = self.list_networks()
        except exc.OpenStackCloudException:
            self._network_list_stamp = True
            return

        for network in all_networks:

            # External IPv4 networks
            if (network['name'] in self._external_ipv4_names
                    or network['id'] in self._external_ipv4_names):
                external_ipv4_networks.append(network)
            elif ((('router:external' in network
                    and network['router:external'])
                   or network.get('provider:physical_network'))
                  and network['name'] not in self._internal_ipv4_names
                  and network['id'] not in self._internal_ipv4_names):
                external_ipv4_networks.append(network)

            # Internal networks
            if (network['name'] in self._internal_ipv4_names
                    or network['id'] in self._internal_ipv4_names):
                internal_ipv4_networks.append(network)
            elif (not network.get('router:external', False)
                  and not network.get('provider:physical_network')
                  and network['name'] not in self._external_ipv4_names
                  and network['id'] not in self._external_ipv4_names):
                internal_ipv4_networks.append(network)

            # External networks
            if (network['name'] in self._external_ipv6_names
                    or network['id'] in self._external_ipv6_names):
                external_ipv6_networks.append(network)
            elif (network.get('router:external')
                  and network['name'] not in self._internal_ipv6_names
                  and network['id'] not in self._internal_ipv6_names):
                external_ipv6_networks.append(network)

            # Internal networks
            if (network['name'] in self._internal_ipv6_names
                    or network['id'] in self._internal_ipv6_names):
                internal_ipv6_networks.append(network)
            elif (not network.get('router:external', False)
                  and network['name'] not in self._external_ipv6_names
                  and network['id'] not in self._external_ipv6_names):
                internal_ipv6_networks.append(network)

            # External Floating IPv4 networks
            if self._nat_source in (
                    network['name'], network['id']):
                if nat_source:
                    raise exc.OpenStackCloudException(
                        'Multiple networks were found matching'
                        ' {nat_net} which is the network configured'
                        ' to be the NAT source. Please check your'
                        ' cloud resources. It is probably a good idea'
                        ' to configure this network by ID rather than'
                        ' by name.'.format(
                            nat_net=self._nat_source))
                external_ipv4_floating_networks.append(network)
                nat_source = network
            elif self._nat_source is None:
                if network.get('router:external'):
                    external_ipv4_floating_networks.append(network)
                    nat_source = nat_source or network

            # NAT Destination
            if self._nat_destination in (
                    network['name'], network['id']):
                if nat_destination:
                    raise exc.OpenStackCloudException(
                        'Multiple networks were found matching'
                        ' {nat_net} which is the network configured'
                        ' to be the NAT destination. Please check your'
                        ' cloud resources. It is probably a good idea'
                        ' to configure this network by ID rather than'
                        ' by name.'.format(
                            nat_net=self._nat_destination))
                nat_destination = network
            elif self._nat_destination is None:
                # TODO(mordred) need a config value for floating
                # ips for this cloud so that we can skip this
                # No configured nat destination, we have to figured
                # it out.
                if all_subnets is None:
                    try:
                        all_subnets = self.list_subnets()
                    except exc.OpenStackCloudException:
                        # Thanks Rackspace broken neutron
                        all_subnets = []

                for subnet in all_subnets:
                    # TODO(mordred) trap for detecting more than
                    # one network with a gateway_ip without a config
                    if ('gateway_ip' in subnet and subnet['gateway_ip']
                            and network['id'] == subnet['network_id']):
                        nat_destination = network
                        break

            # Default network
            if self._default_network in (
                    network['name'], network['id']):
                if default_network:
                    raise exc.OpenStackCloudException(
                        'Multiple networks were found matching'
                        ' {default_net} which is the network'
                        ' configured to be the default interface'
                        ' network. Please check your cloud resources.'
                        ' It is probably a good idea'
                        ' to configure this network by ID rather than'
                        ' by name.'.format(
                            default_net=self._default_network))
                default_network = network

        # Validate config vs. reality
        for net_name in self._external_ipv4_names:
            if net_name not in [net['name'] for net in external_ipv4_networks]:
                raise exc.OpenStackCloudException(
                    "Networks: {network} was provided for external IPv4"
                    " access and those networks could not be found".format(
                        network=net_name))

        for net_name in self._internal_ipv4_names:
            if net_name not in [net['name'] for net in internal_ipv4_networks]:
                raise exc.OpenStackCloudException(
                    "Networks: {network} was provided for internal IPv4"
                    " access and those networks could not be found".format(
                        network=net_name))

        for net_name in self._external_ipv6_names:
            if net_name not in [net['name'] for net in external_ipv6_networks]:
                raise exc.OpenStackCloudException(
                    "Networks: {network} was provided for external IPv6"
                    " access and those networks could not be found".format(
                        network=net_name))

        for net_name in self._internal_ipv6_names:
            if net_name not in [net['name'] for net in internal_ipv6_networks]:
                raise exc.OpenStackCloudException(
                    "Networks: {network} was provided for internal IPv6"
                    " access and those networks could not be found".format(
                        network=net_name))

        if self._nat_destination and not nat_destination:
            raise exc.OpenStackCloudException(
                'Network {network} was configured to be the'
                ' destination for inbound NAT but it could not be'
                ' found'.format(
                    network=self._nat_destination))

        if self._nat_source and not nat_source:
            raise exc.OpenStackCloudException(
                'Network {network} was configured to be the'
                ' source for inbound NAT but it could not be'
                ' found'.format(
                    network=self._nat_source))

        if self._default_network and not default_network:
            raise exc.OpenStackCloudException(
                'Network {network} was configured to be the'
                ' default network interface but it could not be'
                ' found'.format(
                    network=self._default_network))

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
                if (not self._use_external_network
                        and not self._use_internal_network):
                    # Both have been flagged as skip - don't do a list
                    return
                if not self.has_service('network'):
                    return
                self._set_interesting_networks()
                self._network_list_stamp = True
            finally:
                self._networks_lock.release()

    # def get_nat_destination(self):
    #     """Return the network that is configured to be the NAT destination.
    #
    #     :returns: A network dict if one is found
    #     """
    #     self._find_interesting_networks()
    #     return self._nat_destination_network

    def get_nat_source(self):
        """Return the network that is configured to be the NAT destination.

        :returns: A network dict if one is found
        """
        self._find_interesting_networks()
        return self._nat_source_network

    def get_default_network(self):
        """Return the network that is configured to be the default interface.

        :returns: A network dict if one is found
        """
        self._find_interesting_networks()
        return self._default_network_network

    def get_nat_destination(self):
        """Return the network that is configured to be the NAT destination.

        :returns: A network dict if one is found
        """
        self._find_interesting_networks()
        return self._nat_destination_network

    def get_external_networks(self):
        """Return the networks that are configured to route northbound.

        This should be avoided in favor of the specific ipv4/ipv6 method,
        but is here for backwards compatibility.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return list(
            set(self._external_ipv4_networks)
            | set(self._external_ipv6_networks))

    def get_internal_networks(self):
        """Return the networks that are configured to not route northbound.

        This should be avoided in favor of the specific ipv4/ipv6 method,
        but is here for backwards compatibility.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return list(
            set(self._internal_ipv4_networks)
            | set(self._internal_ipv6_networks))

    def get_external_ipv4_networks(self):
        """Return the networks that are configured to route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._external_ipv4_networks

    def get_external_ipv4_floating_networks(self):
        """Return the networks that are configured to route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._external_ipv4_floating_networks

    def get_internal_ipv4_networks(self):
        """Return the networks that are configured to not route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._internal_ipv4_networks

    def get_external_ipv6_networks(self):
        """Return the networks that are configured to route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._external_ipv6_networks

    def get_internal_ipv6_networks(self):
        """Return the networks that are configured to not route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._internal_ipv6_networks
