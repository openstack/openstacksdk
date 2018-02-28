# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
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


import munch
import ipaddress
import six
import socket

from openstack import _log
from openstack.cloud import exc


NON_CALLABLES = (six.string_types, bool, dict, int, float, list, type(None))


def find_nova_interfaces(addresses, ext_tag=None, key_name=None, version=4,
                         mac_addr=None):
    ret = []
    for (k, v) in iter(addresses.items()):
        if key_name is not None and k != key_name:
            # key_name is specified and it doesn't match the current network.
            # Continue with the next one
            continue

        for interface_spec in v:
            if ext_tag is not None:
                if 'OS-EXT-IPS:type' not in interface_spec:
                    # ext_tag is specified, but this interface has no tag
                    # We could actually return right away as this means that
                    # this cloud doesn't support OS-EXT-IPS. Nevertheless,
                    # it would be better to perform an explicit check. e.g.:
                    #   cloud._has_nova_extension('OS-EXT-IPS')
                    # But this needs cloud to be passed to this function.
                    continue
                elif interface_spec['OS-EXT-IPS:type'] != ext_tag:
                    # Type doesn't match, continue with next one
                    continue

            if mac_addr is not None:
                if 'OS-EXT-IPS-MAC:mac_addr' not in interface_spec:
                    # mac_addr is specified, but this interface has no mac_addr
                    # We could actually return right away as this means that
                    # this cloud doesn't support OS-EXT-IPS-MAC. Nevertheless,
                    # it would be better to perform an explicit check. e.g.:
                    #   cloud._has_nova_extension('OS-EXT-IPS-MAC')
                    # But this needs cloud to be passed to this function.
                    continue
                elif interface_spec['OS-EXT-IPS-MAC:mac_addr'] != mac_addr:
                    # MAC doesn't match, continue with next one
                    continue

            if interface_spec['version'] == version:
                ret.append(interface_spec)
    return ret


def find_nova_addresses(addresses, ext_tag=None, key_name=None, version=4,
                        mac_addr=None):
    interfaces = find_nova_interfaces(addresses, ext_tag, key_name, version,
                                      mac_addr)
    floating_addrs = []
    fixed_addrs = []
    for i in interfaces:
        if i.get('OS-EXT-IPS:type') == 'floating':
            floating_addrs.append(i['addr'])
        else:
            fixed_addrs.append(i['addr'])
    return floating_addrs + fixed_addrs


def get_server_ip(server, public=False, cloud_public=True, **kwargs):
    """Get an IP from the Nova addresses dict

    :param server: The server to pull the address from
    :param public: Whether the address we're looking for should be considered
                   'public' and therefore reachabiliity tests should be
                   used. (defaults to False)
    :param cloud_public: Whether the cloud has been configured to use private
                         IPs from servers as the interface_ip. This inverts the
                         public reachability logic, as in this case it's the
                         private ip we expect shade to be able to reach
    """
    addrs = find_nova_addresses(server['addresses'], **kwargs)
    return find_best_address(
        addrs, public=public, cloud_public=cloud_public)


def get_server_private_ip(server, cloud=None):
    """Find the private IP address

    If Neutron is available, search for a port on a network where
    `router:external` is False and `shared` is False. This combination
    indicates a private network with private IP addresses. This port should
    have the private IP.

    If Neutron is not available, or something goes wrong communicating with it,
    as a fallback, try the list of addresses associated with the server dict,
    looking for an IP type tagged as 'fixed' in the network named 'private'.

    Last resort, ignore the IP type and just look for an IP on the 'private'
    network (e.g., Rackspace).
    """
    if cloud and not cloud.use_internal_network():
        return None

    # Try to get a floating IP interface. If we have one then return the
    # private IP address associated with that floating IP for consistency.
    fip_ints = find_nova_interfaces(server['addresses'], ext_tag='floating')
    fip_mac = None
    if fip_ints:
        fip_mac = fip_ints[0].get('OS-EXT-IPS-MAC:mac_addr')

    # Short circuit the ports/networks search below with a heavily cached
    # and possibly pre-configured network name
    if cloud:
        int_nets = cloud.get_internal_ipv4_networks()
        for int_net in int_nets:
            int_ip = get_server_ip(
                server, key_name=int_net['name'],
                ext_tag='fixed',
                cloud_public=not cloud.private,
                mac_addr=fip_mac)
            if int_ip is not None:
                return int_ip
        # Try a second time without the fixed tag. This is for old nova-network
        # results that do not have the fixed/floating tag.
        for int_net in int_nets:
            int_ip = get_server_ip(
                server, key_name=int_net['name'],
                cloud_public=not cloud.private,
                mac_addr=fip_mac)
            if int_ip is not None:
                return int_ip

    ip = get_server_ip(
        server, ext_tag='fixed', key_name='private', mac_addr=fip_mac)
    if ip:
        return ip

    # Last resort, and Rackspace
    return get_server_ip(
        server, key_name='private')


def get_server_external_ipv4(cloud, server):
    """Find an externally routable IP for the server.

    There are 5 different scenarios we have to account for:

    * Cloud has externally routable IP from neutron but neutron APIs don't
      work (only info available is in nova server record) (rackspace)
    * Cloud has externally routable IP from neutron (runabove, ovh)
    * Cloud has externally routable IP from neutron AND supports optional
      private tenant networks (vexxhost, unitedstack)
    * Cloud only has private tenant network provided by neutron and requires
      floating-ip for external routing (dreamhost, hp)
    * Cloud only has private tenant network provided by nova-network and
      requires floating-ip for external routing (auro)

    :param cloud: the cloud we're working with
    :param server: the server dict from which we want to get an IPv4 address
    :return: a string containing the IPv4 address or None
    """

    if not cloud.use_external_network():
        return None

    if server['accessIPv4']:
        return server['accessIPv4']

    # Short circuit the ports/networks search below with a heavily cached
    # and possibly pre-configured network name
    ext_nets = cloud.get_external_ipv4_networks()
    for ext_net in ext_nets:
        ext_ip = get_server_ip(
            server, key_name=ext_net['name'], public=True,
            cloud_public=not cloud.private)
        if ext_ip is not None:
            return ext_ip

    # Try to get a floating IP address
    # Much as I might find floating IPs annoying, if it has one, that's
    # almost certainly the one that wants to be used
    ext_ip = get_server_ip(
        server, ext_tag='floating', public=True,
        cloud_public=not cloud.private)
    if ext_ip is not None:
        return ext_ip

    # The cloud doesn't support Neutron or Neutron can't be contacted. The
    # server might have fixed addresses that are reachable from outside the
    # cloud (e.g. Rax) or have plain ol' floating IPs

    # Try to get an address from a network named 'public'
    ext_ip = get_server_ip(
        server, key_name='public', public=True,
        cloud_public=not cloud.private)
    if ext_ip is not None:
        return ext_ip

    # Nothing else works, try to find a globally routable IP address
    for interfaces in server['addresses'].values():
        for interface in interfaces:
            try:
                ip = ipaddress.ip_address(interface['addr'])
            except Exception:
                # Skip any error, we're looking for a working ip - if the
                # cloud returns garbage, it wouldn't be the first weird thing
                # but it still doesn't meet the requirement of "be a working
                # ip address"
                continue
            if ip.version == 4 and not ip.is_private:
                return str(ip)

    return None


def find_best_address(addresses, public=False, cloud_public=True):
    do_check = public == cloud_public
    if not addresses:
        return None
    if len(addresses) == 1:
        return addresses[0]
    if len(addresses) > 1 and do_check:
        # We only want to do this check if the address is supposed to be
        # reachable. Otherwise we're just debug log spamming on every listing
        # of private ip addresses
        for address in addresses:
            # Return the first one that is reachable
            try:
                for res in socket.getaddrinfo(
                        address, 22, socket.AF_UNSPEC, socket.SOCK_STREAM, 0):
                    family, socktype, proto, _, sa = res
                    connect_socket = socket.socket(family, socktype, proto)
                    connect_socket.settimeout(1)
                    connect_socket.connect(sa)
                    return address
            except Exception:
                pass
    # Give up and return the first - none work as far as we can tell
    if do_check:
        log = _log.setup_logging('openstack')
        log.debug(
            'The cloud returned multiple addresses, and none of them seem'
            ' to work. That might be what you wanted, but we have no clue'
            " what's going on, so we just picked one at random")
    return addresses[0]


def get_server_external_ipv6(server):
    """ Get an IPv6 address reachable from outside the cloud.

    This function assumes that if a server has an IPv6 address, that address
    is reachable from outside the cloud.

    :param server: the server from which we want to get an IPv6 address
    :return: a string containing the IPv6 address or None
    """
    if server['accessIPv6']:
        return server['accessIPv6']
    addresses = find_nova_addresses(addresses=server['addresses'], version=6)
    return find_best_address(addresses, public=True)


def get_server_default_ip(cloud, server):
    """ Get the configured 'default' address

    It is possible in clouds.yaml to configure for a cloud a network that
    is the 'default_interface'. This is the network that should be used
    to talk to instances on the network.

    :param cloud: the cloud we're working with
    :param server: the server dict from which we want to get the default
                   IPv4 address
    :return: a string containing the IPv4 address or None
    """
    ext_net = cloud.get_default_network()
    if ext_net:
        if (cloud._local_ipv6 and not cloud.force_ipv4):
            # try 6 first, fall back to four
            versions = [6, 4]
        else:
            versions = [4]
        for version in versions:
            ext_ip = get_server_ip(
                server, key_name=ext_net['name'], version=version, public=True,
                cloud_public=not cloud.private)
            if ext_ip is not None:
                return ext_ip
    return None


def _get_interface_ip(cloud, server):
    """ Get the interface IP for the server

    Interface IP is the IP that should be used for communicating with the
    server. It is:
    - the IP on the configured default_interface network
    - if cloud.private, the private ip if it exists
    - if the server has a public ip, the public ip
    """
    default_ip = get_server_default_ip(cloud, server)
    if default_ip:
        return default_ip

    if cloud.private and server['private_v4']:
        return server['private_v4']

    if (server['public_v6'] and cloud._local_ipv6 and not cloud.force_ipv4):
        return server['public_v6']
    else:
        return server['public_v4']


def get_groups_from_server(cloud, server, server_vars):
    groups = []

    region = cloud.config.region_name
    cloud_name = cloud.name

    # Create a group for the cloud
    groups.append(cloud_name)

    # Create a group on region
    groups.append(region)

    # And one by cloud_region
    groups.append("%s_%s" % (cloud_name, region))

    # Check if group metadata key in servers' metadata
    group = server['metadata'].get('group')
    if group:
        groups.append(group)

    for extra_group in server['metadata'].get('groups', '').split(','):
        if extra_group:
            groups.append(extra_group)

    groups.append('instance-%s' % server['id'])

    for key in ('flavor', 'image'):
        if 'name' in server_vars[key]:
            groups.append('%s-%s' % (key, server_vars[key]['name']))

    for key, value in iter(server['metadata'].items()):
        groups.append('meta-%s_%s' % (key, value))

    az = server_vars.get('az', None)
    if az:
        # Make groups for az, region_az and cloud_region_az
        groups.append(az)
        groups.append('%s_%s' % (region, az))
        groups.append('%s_%s_%s' % (cloud.name, region, az))
    return groups


def expand_server_vars(cloud, server):
    """Backwards compatibility function."""
    return add_server_interfaces(cloud, server)


def _make_address_dict(fip, port):
    address = dict(version=4, addr=fip['floating_ip_address'])
    address['OS-EXT-IPS:type'] = 'floating'
    address['OS-EXT-IPS-MAC:mac_addr'] = port['mac_address']
    return address


def _get_supplemental_addresses(cloud, server):
    fixed_ip_mapping = {}
    for name, network in server['addresses'].items():
        for address in network:
            if address['version'] == 6:
                continue
            if address.get('OS-EXT-IPS:type') == 'floating':
                # We have a floating IP that nova knows about, do nothing
                return server['addresses']
            fixed_ip_mapping[address['addr']] = name
    try:
        # Don't bother doing this before the server is active, it's a waste
        # of an API call while polling for a server to come up
        if (cloud.has_service('network') and cloud._has_floating_ips() and
                server['status'] == 'ACTIVE'):
            for port in cloud.search_ports(
                    filters=dict(device_id=server['id'])):
                for fip in cloud.search_floating_ips(
                        filters=dict(port_id=port['id'])):
                        # This SHOULD return one and only one FIP - but doing
                        # it as a search/list lets the logic work regardless
                    if fip['fixed_ip_address'] not in fixed_ip_mapping:
                        log = _log.setup_logging('openstack')
                        log.debug(
                            "The cloud returned floating ip %(fip)s attached"
                            " to server %(server)s but the fixed ip associated"
                            " with the floating ip in the neutron listing"
                            " does not exist in the nova listing. Something"
                            " is exceptionally broken.",
                            dict(fip=fip['id'], server=server['id']))
                    fixed_net = fixed_ip_mapping[fip['fixed_ip_address']]
                    server['addresses'][fixed_net].append(
                        _make_address_dict(fip, port))
    except exc.OpenStackCloudException:
        # If something goes wrong with a cloud call, that's cool - this is
        # an attempt to provide additional data and should not block forward
        # progress
        pass
    return server['addresses']


def add_server_interfaces(cloud, server):
    """Add network interface information to server.

    Query the cloud as necessary to add information to the server record
    about the network information needed to interface with the server.

    Ensures that public_v4, public_v6, private_v4, private_v6, interface_ip,
                 accessIPv4 and accessIPv6 are always set.
    """
    # First, add an IP address. Set it to '' rather than None if it does
    # not exist to remain consistent with the pre-existing missing values
    server['addresses'] = _get_supplemental_addresses(cloud, server)
    server['public_v4'] = get_server_external_ipv4(cloud, server) or ''
    server['public_v6'] = get_server_external_ipv6(server) or ''
    server['private_v4'] = get_server_private_ip(server, cloud) or ''
    server['interface_ip'] = _get_interface_ip(cloud, server) or ''

    # Some clouds do not set these, but they're a regular part of the Nova
    # server record. Since we know them, go ahead and set them. In the case
    # where they were set previous, we use the values, so this will not break
    # clouds that provide the information
    if cloud.private and server['private_v4']:
        server['accessIPv4'] = server['private_v4']
    else:
        server['accessIPv4'] = server['public_v4']
    server['accessIPv6'] = server['public_v6']

    return server


def expand_server_security_groups(cloud, server):
    try:
        groups = cloud.list_server_security_groups(server)
    except exc.OpenStackCloudException:
        groups = []
    server['security_groups'] = groups or []


def get_hostvars_from_server(cloud, server, mounts=None):
    """Expand additional server information useful for ansible inventory.

    Variables in this function may make additional cloud queries to flesh out
    possibly interesting info, making it more expensive to call than
    expand_server_vars if caching is not set up. If caching is set up,
    the extra cost should be minimal.
    """
    server_vars = add_server_interfaces(cloud, server)

    flavor_id = server['flavor']['id']
    flavor_name = cloud.get_flavor_name(flavor_id)
    if flavor_name:
        server_vars['flavor']['name'] = flavor_name

    expand_server_security_groups(cloud, server)

    # OpenStack can return image as a string when you've booted from volume
    if str(server['image']) == server['image']:
        image_id = server['image']
        server_vars['image'] = dict(id=image_id)
    else:
        image_id = server['image'].get('id', None)
    if image_id:
        image_name = cloud.get_image_name(image_id)
        if image_name:
            server_vars['image']['name'] = image_name

    volumes = []
    if cloud.has_service('volume'):
        try:
            for volume in cloud.get_volumes(server):
                # Make things easier to consume elsewhere
                volume['device'] = volume['attachments'][0]['device']
                volumes.append(volume)
        except exc.OpenStackCloudException:
            pass
    server_vars['volumes'] = volumes
    if mounts:
        for mount in mounts:
            for vol in server_vars['volumes']:
                if vol['display_name'] == mount['display_name']:
                    if 'mount' in mount:
                        vol['mount'] = mount['mount']

    return server_vars


def obj_to_munch(obj):
    """ Turn an object with attributes into a dict suitable for serializing.

    Some of the things that are returned in OpenStack are objects with
    attributes. That's awesome - except when you want to expose them as JSON
    structures. We use this as the basis of get_hostvars_from_server above so
    that we can just have a plain dict of all of the values that exist in the
    nova metadata for a server.
    """
    if obj is None:
        return None
    elif isinstance(obj, munch.Munch) or hasattr(obj, 'mock_add_spec'):
        # If we obj_to_munch twice, don't fail, just return the munch
        # Also, don't try to modify Mock objects - that way lies madness
        return obj
    elif isinstance(obj, dict):
        # The new request-id tracking spec:
        # https://specs.openstack.org/openstack/nova-specs/specs/juno/approved/log-request-id-mappings.html
        # adds a request-ids attribute to returned objects. It does this even
        # with dicts, which now become dict subclasses. So we want to convert
        # the dict we get, but we also want it to fall through to object
        # attribute processing so that we can also get the request_ids
        # data into our resulting object.
        instance = munch.Munch(obj)
    else:
        instance = munch.Munch()

    for key in dir(obj):
        try:
            value = getattr(obj, key)
        # some attributes can be defined as a @propierty, so we can't assure
        # to have a valid value
        # e.g. id in python-novaclient/tree/novaclient/v2/quotas.py
        except AttributeError:
            continue
        if isinstance(value, NON_CALLABLES) and not key.startswith('_'):
            instance[key] = value
    return instance


obj_to_dict = obj_to_munch


def obj_list_to_munch(obj_list):
    """Enumerate through lists of objects and return lists of dictonaries.

    Some of the objects returned in OpenStack are actually lists of objects,
    and in order to expose the data structures as JSON, we need to facilitate
    the conversion to lists of dictonaries.
    """
    return [obj_to_munch(obj) for obj in obj_list]


obj_list_to_dict = obj_list_to_munch


def get_and_munchify(key, data):
    """Get the value associated to key and convert it.

    The value will be converted in a Munch object or a list of Munch objects
    based on the type
    """
    result = data.get(key, []) if key else data
    if isinstance(result, list):
        return obj_list_to_munch(result)
    elif isinstance(result, dict):
        return obj_to_munch(result)
    return result
