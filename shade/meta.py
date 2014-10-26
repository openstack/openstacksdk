# Copyright (c) 2014 Monty Taylor
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

import re
import types

NON_CALLABLES = (basestring, bool, dict, int, list, types.NoneType)


def find_nova_addresses(addresses, ext_tag, key_name=None):

    ret = []
    for (k, v) in addresses.iteritems():
        if key_name and k == key_name:
            ret.extend([addrs['addr'] for addrs in v])
        else:
            for interface_spec in v:
                if ('OS-EXT-IPS:type' in interface_spec
                        and interface_spec['OS-EXT-IPS:type'] == ext_tag):
                    ret.append(interface_spec['addr'])
    return ret


def get_groups_from_server(cloud, server, server_vars):
    groups = []

    region = cloud.region
    cloud_name = cloud.name

    # Create a group for the cloud
    groups.append(cloud_name)

    # Create a group on region
    groups.append(region)

    # And one by cloud_region
    groups.append("%s_%s" % (cloud_name, region))

    # Check if group metadata key in servers' metadata
    group = server.metadata.get('group')
    if group:
        groups.append(group)

    for extra_group in server.metadata.get('groups', '').split(','):
        if extra_group:
            groups.append(extra_group)

    groups.append('instance-%s' % server.id)

    for key in ('flavor', 'image'):
        if 'name' in server_vars[key]:
            groups.append('%s-%s' % (key, server_vars[key]['name']))

    for key, value in server.metadata.iteritems():
        groups.append('meta-%s_%s' % (key, value))

    az = server_vars.get('az', None)
    if az:
        # Make groups for az, region_az and cloud_region_az
        groups.append(az)
        groups.append('%s_%s' % (region, az))
        groups.append('%s_%s_%s' % (cloud.name, region, az))
    return groups


def get_hostvars_from_server(cloud, server, mounts=None):
    server_vars = dict()
    # Fist, add an IP address
    if (cloud.private):
        interface_ips = find_nova_addresses(
            getattr(server, 'addresses'), 'fixed', 'private')
    else:
        interface_ips = find_nova_addresses(
            getattr(server, 'addresses'), 'floating', 'public')

    if interface_ips:
        # TODO(mordred): I want this to be richer, "first" is not best
        server_vars['interface_ip'] = interface_ips[0]

    server_vars.update(obj_to_dict(server))

    server_vars['region'] = cloud.region
    server_vars['cloud'] = cloud.name

    flavor_id = server.flavor['id']
    flavor_name = cloud.get_flavor_name(flavor_id)
    if flavor_name:
        server_vars['flavor']['name'] = flavor_name

    image_id = server.image['id']
    image_name = cloud.get_image_name(image_id)
    if image_name:
        server_vars['image']['name'] = image_name

    volumes = []
    for vol in cloud.get_volumes(server):
        volume = obj_to_dict(vol)
        # Make things easier to consume elsewhere
        volume['device'] = volume['attachments'][0]['device']
        volumes.append(volume)
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
    instance = {}
    for key in dir(obj):
        value = getattr(obj, key)
        if (isinstance(value, NON_CALLABLES) and not key.startswith('_')):
            instance[key] = value
    return instance
