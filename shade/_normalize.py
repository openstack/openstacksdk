# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
# Copyright (c) 2016 Red Hat, Inc.
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

_IMAGE_FIELDS = (
    'checksum',
    'container_format',
    'created_at',
    'disk_format',
    'file',
    'id',
    'min_disk',
    'min_ram',
    'name',
    'owner',
    'protected',
    'schema',
    'size',
    'status',
    'tags',
    'updated_at',
    'virtual_size',
)


class Normalizer(object):
    '''Mix-in class to provide the normalization functions.

    This is in a separate class just for on-disk source code organization
    reasons.
    '''

    def _normalize_flavors(self, flavors):
        """ Normalize a list of flavor objects """
        ret = []
        for flavor in flavors:
            ret.append(self._normalize_flavor(flavor))
        return ret

    def _normalize_flavor(self, flavor):
        """ Normalize a flavor object """
        flavor.pop('links', None)
        flavor.pop('NAME_ATTR', None)
        flavor.pop('HUMAN_ID', None)
        flavor.pop('human_id', None)
        if 'extra_specs' not in flavor:
            flavor['extra_specs'] = {}
        ephemeral = flavor.pop('OS-FLV-EXT-DATA:ephemeral', 0)
        is_public = flavor.pop('os-flavor-access:is_public', True)
        disabled = flavor.pop('OS-FLV-DISABLED:disabled', False)
        # Make sure both the extension version and a sane version are present
        flavor['OS-FLV-DISABLED:disabled'] = disabled
        flavor['disabled'] = disabled
        flavor['OS-FLV-EXT-DATA:ephemeral'] = ephemeral
        flavor['ephemeral'] = ephemeral
        flavor['os-flavor-access:is_public'] = is_public
        flavor['is_public'] = is_public
        flavor['location'] = self.current_location

        return flavor

    def _normalize_images(self, images):
        ret = []
        for image in images:
            ret.append(self._normalize_image(image))
        return ret

    def _normalize_image(self, image):
        new_image = munch.Munch(
            location=self._get_current_location(project_id=image.get('owner')))
        properties = image.pop('properties', {})
        visibility = image.pop('visibility', None)
        if visibility:
            is_public = (visibility == 'public')
        else:
            is_public = image.pop('is_public', False)
            visibility = 'public' if is_public else 'private'

        for field in _IMAGE_FIELDS:
            new_image[field] = image.pop(field, None)
        for key, val in image.items():
            properties[key] = val
            new_image[key] = val
        new_image['properties'] = properties
        new_image['visibility'] = visibility
        new_image['is_public'] = is_public
        return new_image

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

    def _normalize_secgroup(self, group):

        rules = group.pop('security_group_rules', None)
        if not rules and 'rules' in group:
            rules = group.pop('rules')
        group['security_group_rules'] = self._normalize_secgroup_rules(rules)
        project_id = group.get('project_id', group.get('tenant_id', ''))
        group['location'] = self._get_current_location(project_id=project_id)
        # neutron sets these. we don't care about it, but let's be the same
        group['tenant_id'] = project_id
        group['project_id'] = project_id
        return munch.Munch(group)

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

    def _normalize_secgroup_rule(self, rule):
        ret = munch.Munch()
        ret['id'] = rule['id']
        ret['direction'] = rule.get('direction', 'ingress')
        ret['ethertype'] = rule.get('ethertype', 'IPv4')
        port_range_min = rule.get(
            'port_range_min', rule.get('from_port', None))
        if port_range_min == -1:
            port_range_min = None
        ret['port_range_min'] = port_range_min
        port_range_max = rule.get(
            'port_range_max', rule.get('to_port', None))
        if port_range_max == -1:
            port_range_max = None
        ret['port_range_max'] = port_range_max
        ret['protocol'] = rule.get('protocol', rule.get('ip_protocol'))
        ret['remote_ip_prefix'] = rule.get(
            'remote_ip_prefix', rule.get('ip_range', {}).get('cidr', None))
        ret['security_group_id'] = rule.get(
            'security_group_id', rule.get('parent_group_id'))
        ret['remote_group_id'] = rule.get('remote_group_id')
        project_id = rule.get('project_id', rule.get('tenant_id', ''))
        ret['location'] = self._get_current_location(project_id=project_id)
        # neutron sets these. we don't care about it, but let's be the same
        ret['tenant_id'] = project_id
        ret['project_id'] = project_id
        return ret

    def _normalize_servers(self, servers):
        # Here instead of _utils because we need access to region and cloud
        # name from the cloud object
        ret = []
        for server in servers:
            ret.append(self._normalize_server(server))
        return ret

    def _normalize_server(self, server):
        server.pop('links', None)
        server['flavor'].pop('links', None)
        # OpenStack can return image as a string when you've booted
        # from volume
        if str(server['image']) != server['image']:
            server['image'].pop('links', None)

        server['region'] = self.region_name
        server['cloud'] = self.name
        server['location'] = self._get_current_location(
            project_id=server.get('tenant_id'))

        az = server.get('OS-EXT-AZ:availability_zone', None)
        if az:
            server['az'] = az

        # Ensure volumes is always in the server dict, even if empty
        server['volumes'] = []

        return server

    def _normalize_neutron_floating_ips(self, ips):
        """Normalize the structure of Neutron floating IPs

        Unfortunately, not all the Neutron floating_ip attributes are available
        with Nova and not all Nova floating_ip attributes are available with
        Neutron.
        This function extract attributes that are common to Nova and Neutron
        floating IP resource.
        If the whole structure is needed inside shade, shade provides private
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
                "status": "ACTIVE"
              }, ...
            ]

        """
        return [
            self._normalize_neutron_floating_ip(ip) for ip in ips
        ]

    def _normalize_neutron_floating_ip(self, ip):
        network_id = ip.get('floating_network_id', ip.get('network'))
        project_id = ip.get('project_id', ip.get('tenant_id', ''))
        return munch.Munch(
            attached=ip.get('port_id') is not None and ip.get('port_id') != '',
            fixed_ip_address=ip.get('fixed_ip_address'),
            floating_ip_address=ip['floating_ip_address'],
            floating_network_id=network_id,
            id=ip['id'],
            location=self._get_current_location(project_id=project_id),
            network=network_id,
            port_id=ip.get('port_id'),
            project_id=project_id,
            router_id=ip.get('router_id'),
            status=ip.get('status', 'UNKNOWN'),
            tenant_id=project_id
        )
