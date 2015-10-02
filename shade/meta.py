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


import bunch
import six

from shade import exc
from shade import _log
from shade import _utils


NON_CALLABLES = (six.string_types, bool, dict, int, float, list, type(None))

log = _log.setup_logging(__name__)


def find_nova_addresses(addresses, ext_tag=None, key_name=None, version=4):

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

            if interface_spec['version'] == version:
                ret.append(interface_spec['addr'])

    return ret


def get_server_ip(server, **kwargs):
    addrs = find_nova_addresses(server['addresses'], **kwargs)
    if not addrs:
        return None
    return addrs[0]


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

    # Short circuit the ports/networks search below with a heavily cached
    # and possibly pre-configured network name
    if cloud:
        int_net = cloud.get_internal_network()
        if int_net:
            int_ip = get_server_ip(server, key_name=int_net['name'])
            if int_ip is not None:
                return int_ip

    if cloud and cloud.has_service('network'):
        try:
            server_ports = cloud.search_ports(
                filters={'device_id': server['id']})
            nets = cloud.search_networks(
                filters={'router:external': False, 'shared': False})
        except Exception as e:
            log.debug(
                "Something went wrong talking to neutron API: "
                "'{msg}'. Trying with Nova.".format(msg=str(e)))
        else:
            for net in nets:
                for port in server_ports:
                    if net['id'] == port['network_id']:
                        for ip in port['fixed_ips']:
                            if _utils.is_ipv4(ip['ip_address']):
                                return ip['ip_address']

    ip = get_server_ip(server, ext_tag='fixed', key_name='private')
    if ip:
        return ip

    # Last resort, and Rackspace
    return get_server_ip(server, key_name='private')


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
    ext_net = cloud.get_external_network()
    if ext_net:
        ext_ip = get_server_ip(server, key_name=ext_net['name'])
        if ext_ip is not None:
            return ext_ip

    if cloud.has_service('network'):
        try:
            # Search a fixed IP attached to an external net. Unfortunately
            # Neutron ports don't have a 'floating_ips' attribute
            server_ports = cloud.search_ports(
                filters={'device_id': server['id']})
            ext_nets = cloud.search_networks(filters={'router:external': True})
        except Exception as e:
            log.debug(
                "Something went wrong talking to neutron API: "
                "'{msg}'. Trying with Nova.".format(msg=str(e)))
            # Fall-through, trying with Nova
        else:
            for net in ext_nets:
                for port in server_ports:
                    if net['id'] == port['network_id']:
                        for ip in port['fixed_ips']:
                            if _utils.is_ipv4(ip['ip_address']):
                                return ip['ip_address']
            # The server doesn't have an interface on an external network so it
            # can either have a floating IP or have no way to be reached from
            # outside the cloud.
            # Fall-through, trying with Nova

    # The cloud doesn't support Neutron or Neutron can't be contacted. The
    # server might have fixed addresses that are reachable from outside the
    # cloud (e.g. Rax) or have plain ol' floating IPs

    # Try to get an address from a network named 'public'
    ext_ip = get_server_ip(server, key_name='public')
    if ext_ip is not None:
        return ext_ip

    # Try to find a globally routable IP address
    for interfaces in server['addresses'].values():
        for interface in interfaces:
            if _utils.is_ipv4(interface['addr']) and \
                    _utils.is_globally_routable_ipv4(interface['addr']):
                return interface['addr']

    # Last, try to get a floating IP address
    ext_ip = get_server_ip(server, ext_tag='floating')
    if ext_ip is not None:
        return ext_ip

    return None


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
    if addresses:
        return addresses[0]
    return None


def get_groups_from_server(cloud, server, server_vars):
    groups = []

    region = cloud.region_name
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


def get_hostvars_from_server(cloud, server, mounts=None):
    server_vars = server
    server_vars.pop('links', None)

    # First, add an IP address. Set it to '' rather than None if it does
    # not exist to remain consistent with the pre-existing missing values
    server_vars['public_v4'] = get_server_external_ipv4(cloud, server) or ''
    server_vars['public_v6'] = get_server_external_ipv6(server) or ''
    server_vars['private_v4'] = get_server_private_ip(server, cloud) or ''
    if cloud.private:
        interface_ip = server_vars['private_v4']
    else:
        interface_ip = server_vars['public_v4']
    if interface_ip:
        server_vars['interface_ip'] = interface_ip

    # Some clouds do not set these, but they're a regular part of the Nova
    # server record. Since we know them, go ahead and set them. In the case
    # where they were set previous, we use the values, so this will not break
    # clouds that provide the information
    server_vars['accessIPv4'] = server_vars['public_v4']
    server_vars['accessIPv6'] = server_vars['public_v6']

    server_vars['region'] = cloud.region_name
    server_vars['cloud'] = cloud.name

    flavor_id = server['flavor']['id']
    flavor_name = cloud.get_flavor_name(flavor_id)
    if flavor_name:
        server_vars['flavor']['name'] = flavor_name
    server_vars['flavor'].pop('links', None)

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
    server_vars['image'].pop('links', None)

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

    az = server_vars.get('OS-EXT-AZ:availability_zone', None)
    if az:
        server_vars['az'] = az

    return server_vars


def obj_to_dict(obj):
    """ Turn an object with attributes into a dict suitable for serializing.

    Some of the things that are returned in OpenStack are objects with
    attributes. That's awesome - except when you want to expose them as JSON
    structures. We use this as the basis of get_hostvars_from_server above so
    that we can just have a plain dict of all of the values that exist in the
    nova metadata for a server.
    """
    instance = bunch.Bunch()
    for key in dir(obj):
        value = getattr(obj, key)
        if isinstance(value, NON_CALLABLES) and not key.startswith('_'):
            instance[key] = value
    return instance


def obj_list_to_dict(list):
    """Enumerate through lists of objects and return lists of dictonaries.

    Some of the objects returned in OpenStack are actually lists of objects,
    and in order to expose the data structures as JSON, we need to facilitate
    the conversion to lists of dictonaries.
    """
    new_list = []
    for obj in list:
        new_list.append(obj_to_dict(obj))
    return new_list


def warlock_to_dict(obj):
    # glanceclient v2 uses warlock to construct its objects. Warlock does
    # deep black magic to attribute look up to support validation things that
    # means we cannot use normal obj_to_dict
    obj_dict = bunch.Bunch()
    for (key, value) in obj.items():
        if isinstance(value, NON_CALLABLES) and not key.startswith('_'):
            obj_dict[key] = value
    return obj_dict


def warlock_list_to_dict(list):
    new_list = []
    for obj in list:
        new_list.append(warlock_to_dict(obj))
    return new_list
