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
import datetime
import munch
import six

_IMAGE_FIELDS = (
    'checksum',
    'container_format',
    'direct_url',
    'disk_format',
    'file',
    'id',
    'name',
    'owner',
    'virtual_size',
)

_SERVER_FIELDS = (
    'accessIPv4',
    'accessIPv6',
    'addresses',
    'adminPass',
    'created',
    'key_name',
    'metadata',
    'networks',
    'private_v4',
    'public_v4',
    'public_v6',
    'status',
    'updated',
    'user_id',
)

_KEYPAIR_FIELDS = (
    'fingerprint',
    'name',
    'private_key',
    'public_key',
    'user_id',
)

_KEYPAIR_USELESS_FIELDS = (
    'deleted',
    'deleted_at',
    'id',
    'updated_at',
)

_COMPUTE_LIMITS_FIELDS = (
    ('maxPersonality', 'max_personality'),
    ('maxPersonalitySize', 'max_personality_size'),
    ('maxServerGroupMembers', 'max_server_group_members'),
    ('maxServerGroups', 'max_server_groups'),
    ('maxServerMeta', 'max_server_meta'),
    ('maxTotalCores', 'max_total_cores'),
    ('maxTotalInstances', 'max_total_instances'),
    ('maxTotalKeypairs', 'max_total_keypairs'),
    ('maxTotalRAMSize', 'max_total_ram_size'),
    ('totalCoresUsed', 'total_cores_used'),
    ('totalInstancesUsed', 'total_instances_used'),
    ('totalRAMUsed', 'total_ram_used'),
    ('totalServerGroupsUsed', 'total_server_groups_used'),
)


_pushdown_fields = {
    'project': [
        'domain_id'
    ]
}


def _split_filters(obj_name='', filters=None, **kwargs):
    # Handle jmsepath filters
    if not filters:
        filters = {}
    if not isinstance(filters, dict):
        return {}, filters
    # Filter out None values from extra kwargs, because those are
    # defaults. If you want to search for things with None values,
    # they're going to need to go into the filters dict
    for (key, value) in kwargs.items():
        if value is not None:
            filters[key] = value
    pushdown = {}
    client = {}
    for (key, value) in filters.items():
        if key in _pushdown_fields.get(obj_name, {}):
            pushdown[key] = value
        else:
            client[key] = value
    return pushdown, client


def _to_bool(value):
    if isinstance(value, six.string_types):
        if not value:
            return False
        prospective = value.lower().capitalize()
        return prospective == 'True'
    return bool(value)


def _pop_int(resource, key):
    return int(resource.pop(key, 0) or 0)


def _pop_float(resource, key):
    return float(resource.pop(key, 0) or 0)


def _pop_or_get(resource, key, default, strict):
    if strict:
        return resource.pop(key, default)
    else:
        return resource.get(key, default)


class Normalizer(object):
    '''Mix-in class to provide the normalization functions.

    This is in a separate class just for on-disk source code organization
    reasons.
    '''

    def _normalize_compute_limits(self, limits, project_id=None):
        """ Normalize a limits object.

        Limits modified in this method and shouldn't be modified afterwards.
        """

        # Copy incoming limits because of shared dicts in unittests
        limits = limits['absolute'].copy()

        new_limits = munch.Munch()
        new_limits['location'] = self._get_current_location(
            project_id=project_id)

        for field in _COMPUTE_LIMITS_FIELDS:
            new_limits[field[1]] = limits.pop(field[0], None)

        new_limits['properties'] = limits.copy()

        return new_limits

    def _remove_novaclient_artifacts(self, item):
        # Remove novaclient artifacts
        item.pop('links', None)
        item.pop('NAME_ATTR', None)
        item.pop('HUMAN_ID', None)
        item.pop('human_id', None)
        item.pop('request_ids', None)
        item.pop('x_openstack_request_ids', None)

    def _normalize_flavors(self, flavors):
        """ Normalize a list of flavor objects """
        ret = []
        for flavor in flavors:
            ret.append(self._normalize_flavor(flavor))
        return ret

    def _normalize_flavor(self, flavor):
        """ Normalize a flavor object """
        new_flavor = munch.Munch()

        # Copy incoming group because of shared dicts in unittests
        flavor = flavor.copy()

        # Discard noise
        self._remove_novaclient_artifacts(flavor)
        flavor.pop('links', None)

        ephemeral = int(_pop_or_get(
            flavor, 'OS-FLV-EXT-DATA:ephemeral', 0, self.strict_mode))
        ephemeral = flavor.pop('ephemeral', ephemeral)
        is_public = _to_bool(_pop_or_get(
            flavor, 'os-flavor-access:is_public', True, self.strict_mode))
        is_public = _to_bool(flavor.pop('is_public', is_public))
        is_disabled = _to_bool(_pop_or_get(
            flavor, 'OS-FLV-DISABLED:disabled', False, self.strict_mode))
        extra_specs = _pop_or_get(
            flavor, 'OS-FLV-WITH-EXT-SPECS:extra_specs', {}, self.strict_mode)
        extra_specs = flavor.pop('extra_specs', extra_specs)
        extra_specs = munch.Munch(extra_specs)

        new_flavor['location'] = self.current_location
        new_flavor['id'] = flavor.pop('id')
        new_flavor['name'] = flavor.pop('name')
        new_flavor['is_public'] = is_public
        new_flavor['is_disabled'] = is_disabled
        new_flavor['ram'] = _pop_int(flavor, 'ram')
        new_flavor['vcpus'] = _pop_int(flavor, 'vcpus')
        new_flavor['disk'] = _pop_int(flavor, 'disk')
        new_flavor['ephemeral'] = ephemeral
        new_flavor['swap'] = _pop_int(flavor, 'swap')
        new_flavor['rxtx_factor'] = _pop_float(flavor, 'rxtx_factor')

        new_flavor['properties'] = flavor.copy()
        new_flavor['extra_specs'] = extra_specs

        # Backwards compat with nova - passthrough values
        if not self.strict_mode:
            for (k, v) in new_flavor['properties'].items():
                new_flavor.setdefault(k, v)

        return new_flavor

    def _normalize_keypairs(self, keypairs):
        """Normalize Nova Keypairs"""
        ret = []
        for keypair in keypairs:
            ret.append(self._normalize_keypair(keypair))
        return ret

    def _normalize_keypair(self, keypair):
        """Normalize Ironic Machine"""

        new_keypair = munch.Munch()
        keypair = keypair.copy()

        # Discard noise
        self._remove_novaclient_artifacts(keypair)

        new_keypair['location'] = self.current_location
        for key in _KEYPAIR_FIELDS:
            new_keypair[key] = keypair.pop(key, None)
        # These are completely meaningless fields
        for key in _KEYPAIR_USELESS_FIELDS:
            keypair.pop(key, None)
        new_keypair['type'] = keypair.pop('type', 'ssh')
        # created_at isn't returned from the keypair creation. (what?)
        new_keypair['created_at'] = keypair.pop(
            'created_at', datetime.datetime.now().isoformat())
        # Don't even get me started on this
        new_keypair['id'] = new_keypair['name']

        new_keypair['properties'] = keypair.copy()

        return new_keypair

    def _normalize_images(self, images):
        ret = []
        for image in images:
            ret.append(self._normalize_image(image))
        return ret

    def _normalize_image(self, image):
        new_image = munch.Munch(
            location=self._get_current_location(project_id=image.get('owner')))

        # This copy is to keep things from getting epically weird in tests
        image = image.copy()

        # Discard noise
        self._remove_novaclient_artifacts(image)

        properties = image.pop('properties', {})
        visibility = image.pop('visibility', None)
        protected = _to_bool(image.pop('protected', False))

        if visibility:
            is_public = (visibility == 'public')
        else:
            is_public = image.pop('is_public', False)
            visibility = 'public' if is_public else 'private'

        new_image['size'] = image.pop('OS-EXT-IMG-SIZE:size', 0)
        new_image['size'] = image.pop('size', new_image['size'])

        new_image['min_ram'] = image.pop('minRam', 0)
        new_image['min_ram'] = image.pop('min_ram', new_image['min_ram'])

        new_image['min_disk'] = image.pop('minDisk', 0)
        new_image['min_disk'] = image.pop('min_disk', new_image['min_disk'])

        new_image['created_at'] = image.pop('created', '')
        new_image['created_at'] = image.pop(
            'created_at', new_image['created_at'])

        new_image['updated_at'] = image.pop('updated', '')
        new_image['updated_at'] = image.pop(
            'updated_at', new_image['updated_at'])

        for field in _IMAGE_FIELDS:
            new_image[field] = image.pop(field, None)

        new_image['tags'] = image.pop('tags', [])
        new_image['status'] = image.pop('status').lower()
        for field in ('min_ram', 'min_disk', 'size', 'virtual_size'):
            new_image[field] = _pop_int(new_image, field)
        new_image['is_protected'] = protected
        new_image['locations'] = image.pop('locations', [])

        metadata = image.pop('metadata', {})
        for key, val in metadata.items():
            properties.setdefault(key, val)

        for key, val in image.items():
            properties.setdefault(key, val)
        new_image['properties'] = properties
        new_image['is_public'] = is_public
        new_image['visibility'] = visibility

        # Backwards compat with glance
        if not self.strict_mode:
            for key, val in properties.items():
                new_image[key] = val
            new_image['protected'] = protected
            new_image['metadata'] = properties
            new_image['created'] = new_image['created_at']
            new_image['updated'] = new_image['updated_at']
            new_image['minDisk'] = new_image['min_disk']
            new_image['minRam'] = new_image['min_ram']
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

        ret = munch.Munch()
        # Copy incoming group because of shared dicts in unittests
        group = group.copy()

        # Discard noise
        self._remove_novaclient_artifacts(group)

        rules = self._normalize_secgroup_rules(
            group.pop('security_group_rules', group.pop('rules', [])))
        project_id = group.pop('tenant_id', '')
        project_id = group.pop('project_id', project_id)

        ret['location'] = self._get_current_location(project_id=project_id)
        ret['id'] = group.pop('id')
        ret['name'] = group.pop('name')
        ret['security_group_rules'] = rules
        ret['description'] = group.pop('description')
        ret['properties'] = group

        # Backwards compat with Neutron
        if not self.strict_mode:
            ret['tenant_id'] = project_id
            ret['project_id'] = project_id
            for key, val in ret['properties'].items():
                ret.setdefault(key, val)

        return ret

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
        # Copy incoming rule because of shared dicts in unittests
        rule = rule.copy()

        ret['id'] = rule.pop('id')
        ret['direction'] = rule.pop('direction', 'ingress')
        ret['ethertype'] = rule.pop('ethertype', 'IPv4')
        port_range_min = rule.get(
            'port_range_min', rule.pop('from_port', None))
        if port_range_min == -1:
            port_range_min = None
        if port_range_min is not None:
            port_range_min = int(port_range_min)
        ret['port_range_min'] = port_range_min
        port_range_max = rule.pop(
            'port_range_max', rule.pop('to_port', None))
        if port_range_max == -1:
            port_range_max = None
        if port_range_min is not None:
            port_range_min = int(port_range_min)
        ret['port_range_max'] = port_range_max
        ret['protocol'] = rule.pop('protocol', rule.pop('ip_protocol', None))
        ret['remote_ip_prefix'] = rule.pop(
            'remote_ip_prefix', rule.pop('ip_range', {}).get('cidr', None))
        ret['security_group_id'] = rule.pop(
            'security_group_id', rule.pop('parent_group_id', None))
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

    def _normalize_servers(self, servers):
        # Here instead of _utils because we need access to region and cloud
        # name from the cloud object
        ret = []
        for server in servers:
            ret.append(self._normalize_server(server))
        return ret

    def _normalize_server(self, server):
        ret = munch.Munch()
        # Copy incoming server because of shared dicts in unittests
        server = server.copy()

        self._remove_novaclient_artifacts(server)

        ret['id'] = server.pop('id')
        ret['name'] = server.pop('name')

        server['flavor'].pop('links', None)
        ret['flavor'] = server.pop('flavor')

        # OpenStack can return image as a string when you've booted
        # from volume
        if str(server['image']) != server['image']:
            server['image'].pop('links', None)
        ret['image'] = server.pop('image')

        project_id = server.pop('tenant_id', '')
        project_id = server.pop('project_id', project_id)

        az = _pop_or_get(
            server, 'OS-EXT-AZ:availability_zone', None, self.strict_mode)
        ret['location'] = self._get_current_location(
            project_id=project_id, zone=az)

        # Ensure volumes is always in the server dict, even if empty
        ret['volumes'] = _pop_or_get(
            server, 'os-extended-volumes:volumes_attached',
            [], self.strict_mode)

        config_drive = server.pop('config_drive', False)
        ret['has_config_drive'] = _to_bool(config_drive)

        host_id = server.pop('hostId', None)
        ret['host_id'] = host_id

        ret['progress'] = _pop_int(server, 'progress')

        # Leave these in so that the general properties handling works
        ret['disk_config'] = _pop_or_get(
            server, 'OS-DCF:diskConfig', None, self.strict_mode)
        for key in (
                'OS-EXT-STS:power_state',
                'OS-EXT-STS:task_state',
                'OS-EXT-STS:vm_state',
                'OS-SRV-USG:launched_at',
                'OS-SRV-USG:terminated_at'):
            short_key = key.split(':')[1]
            ret[short_key] = _pop_or_get(server, key, None, self.strict_mode)

        # Protect against security_groups being None
        ret['security_groups'] = server.pop('security_groups', None) or []

        for field in _SERVER_FIELDS:
            ret[field] = server.pop(field, None)
        if not ret['networks']:
            ret['networks'] = {}

        ret['interface_ip'] = ''

        ret['properties'] = server.copy()

        # Backwards compat
        if not self.strict_mode:
            ret['hostId'] = host_id
            ret['config_drive'] = config_drive
            ret['project_id'] = project_id
            ret['tenant_id'] = project_id
            ret['region'] = self.region_name
            ret['cloud'] = self.name
            ret['az'] = az
            for key, val in ret['properties'].items():
                ret.setdefault(key, val)
        return ret

    def _normalize_floating_ips(self, ips):
        """Normalize the structure of floating IPs

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
            self._normalize_floating_ip(ip) for ip in ips
        ]

    def _normalize_floating_ip(self, ip):
        ret = munch.Munch()

        # Copy incoming floating ip because of shared dicts in unittests
        ip = ip.copy()

        fixed_ip_address = ip.pop('fixed_ip_address', ip.pop('fixed_ip', None))
        floating_ip_address = ip.pop('floating_ip_address', ip.pop('ip', None))
        network_id = ip.pop(
            'floating_network_id', ip.pop('network', ip.pop('pool', None)))
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

        ret = munch.Munch(
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

    def _normalize_projects(self, projects):
        """Normalize the structure of projects

        This makes tenants from keystone v2 look like projects from v3.

        :param list projects: A list of projects to normalize

        :returns: A list of normalized dicts.
        """
        ret = []
        for project in projects:
            ret.append(self._normalize_project(project))
        return ret

    def _normalize_project(self, project):

        # Copy incoming project because of shared dicts in unittests
        project = project.copy()

        # Discard noise
        self._remove_novaclient_artifacts(project)

        # In both v2 and v3
        project_id = project.pop('id')
        name = project.pop('name', '')
        description = project.pop('description', '')
        is_enabled = project.pop('enabled', True)

        # Projects are global - strip region
        location = self._get_current_location(project_id=project_id)
        location['region_name'] = None

        # v3 additions
        domain_id = project.pop('domain_id', 'default')
        parent_id = project.pop('parent_id', None)
        is_domain = project.pop('is_domain', False)

        # Projects have a special relationship with location
        location['project']['domain_id'] = domain_id
        location['project']['domain_name'] = None
        location['project']['name'] = None
        location['project']['id'] = parent_id

        ret = munch.Munch(
            location=location,
            id=project_id,
            name=name,
            description=description,
            is_enabled=is_enabled,
            is_domain=is_domain,
            properties=project.copy()
        )

        # Backwards compat
        if not self.strict_mode:
            ret['enabled'] = is_enabled
            ret['domain_id'] = domain_id
            ret['parent_id'] = parent_id
            for key, val in ret['properties'].items():
                ret.setdefault(key, val)

        return ret

    def _normalize_volume_type_access(self, volume_type_access):

        volume_type_access = volume_type_access.copy()

        volume_type_id = volume_type_access.pop('volume_type_id')
        project_id = volume_type_access.pop('project_id')
        ret = munch.Munch(
            location=self.current_location,
            project_id=project_id,
            volume_type_id=volume_type_id,
            properties=volume_type_access.copy(),
        )
        return ret

    def _normalize_volume_type_accesses(self, volume_type_accesses):
        ret = []
        for volume_type_access in volume_type_accesses:
            ret.append(self._normalize_volume_type_access(volume_type_access))
        return ret

    def _normalize_volume_type(self, volume_type):

        volume_type = volume_type.copy()

        volume_id = volume_type.pop('id')
        description = volume_type.pop('description', None)
        name = volume_type.pop('name', None)
        old_is_public = volume_type.pop('os-volume-type-access:is_public',
                                        False)
        is_public = volume_type.pop('is_public', old_is_public)
        qos_specs_id = volume_type.pop('qos_specs_id', None)
        extra_specs = volume_type.pop('extra_specs', {})
        ret = munch.Munch(
            location=self.current_location,
            is_public=is_public,
            id=volume_id,
            name=name,
            description=description,
            qos_specs_id=qos_specs_id,
            extra_specs=extra_specs,
            properties=volume_type.copy(),
        )
        return ret

    def _normalize_volume_types(self, volume_types):
        ret = []
        for volume in volume_types:
            ret.append(self._normalize_volume_type(volume))
        return ret

    def _normalize_volumes(self, volumes):
        """Normalize the structure of volumes

        This makes tenants from cinder v1 look like volumes from v2.

        :param list projects: A list of volumes to normalize

        :returns: A list of normalized dicts.
        """
        ret = []
        for volume in volumes:
            ret.append(self._normalize_volume(volume))
        return ret

    def _normalize_volume(self, volume):

        volume = volume.copy()

        # Discard noise
        self._remove_novaclient_artifacts(volume)

        volume_id = volume.pop('id')

        name = volume.pop('display_name', None)
        name = volume.pop('name', name)

        description = volume.pop('display_description', None)
        description = volume.pop('description', description)

        is_bootable = _to_bool(volume.pop('bootable', True))
        is_encrypted = _to_bool(volume.pop('encrypted', False))
        can_multiattach = _to_bool(volume.pop('multiattach', False))

        project_id = _pop_or_get(
            volume, 'os-vol-tenant-attr:tenant_id', None, self.strict_mode)
        az = volume.pop('availability_zone', None)

        location = self._get_current_location(project_id=project_id, zone=az)

        host = _pop_or_get(
            volume, 'os-vol-host-attr:host', None, self.strict_mode)
        replication_extended_status = _pop_or_get(
            volume, 'os-volume-replication:extended_status',
            None, self.strict_mode)

        migration_status = _pop_or_get(
            volume, 'os-vol-mig-status-attr:migstat', None, self.strict_mode)
        migration_status = volume.pop('migration_status', migration_status)
        _pop_or_get(volume, 'user_id', None, self.strict_mode)
        source_volume_id = _pop_or_get(
            volume, 'source_volid', None, self.strict_mode)
        replication_driver = _pop_or_get(
            volume, 'os-volume-replication:driver_data',
            None, self.strict_mode)

        ret = munch.Munch(
            location=location,
            id=volume_id,
            name=name,
            description=description,
            size=_pop_int(volume, 'size'),
            attachments=volume.pop('attachments', []),
            status=volume.pop('status'),
            migration_status=migration_status,
            host=host,
            replication_driver=replication_driver,
            replication_status=volume.pop('replication_status', None),
            replication_extended_status=replication_extended_status,
            snapshot_id=volume.pop('snapshot_id', None),
            created_at=volume.pop('created_at'),
            updated_at=volume.pop('updated_at', None),
            source_volume_id=source_volume_id,
            consistencygroup_id=volume.pop('consistencygroup_id', None),
            volume_type=volume.pop('volume_type', None),
            metadata=volume.pop('metadata', {}),
            is_bootable=is_bootable,
            is_encrypted=is_encrypted,
            can_multiattach=can_multiattach,
            properties=volume.copy(),
        )

        # Backwards compat
        if not self.strict_mode:
            ret['display_name'] = name
            ret['display_description'] = description
            ret['bootable'] = is_bootable
            ret['encrypted'] = is_encrypted
            ret['multiattach'] = can_multiattach
            ret['availability_zone'] = az
            for key, val in ret['properties'].items():
                ret.setdefault(key, val)
        return ret

    def _normalize_volume_attachment(self, attachment):
        """ Normalize a volume attachment object"""

        attachment = attachment.copy()

        # Discard noise
        self._remove_novaclient_artifacts(attachment)
        return munch.Munch(**attachment)

    def _normalize_volume_backups(self, backups):
        ret = []
        for backup in backups:
            ret.append(self._normalize_volume_backup(backup))
        return ret

    def _normalize_volume_backup(self, backup):
        """ Normalize a valume backup object"""

        backup = backup.copy()
        # Discard noise
        self._remove_novaclient_artifacts(backup)
        return munch.Munch(**backup)

    def _normalize_compute_usage(self, usage):
        """ Normalize a compute usage object """

        usage = usage.copy()

        # Discard noise
        self._remove_novaclient_artifacts(usage)
        project_id = usage.pop('tenant_id', None)

        ret = munch.Munch(
            location=self._get_current_location(project_id=project_id),
        )
        for key in (
                'max_personality',
                'max_personality_size',
                'max_server_group_members',
                'max_server_groups',
                'max_server_meta',
                'max_total_cores',
                'max_total_instances',
                'max_total_keypairs',
                'max_total_ram_size',
                'total_cores_used',
                'total_hours',
                'total_instances_used',
                'total_local_gb_usage',
                'total_memory_mb_usage',
                'total_ram_used',
                'total_server_groups_used',
                'total_vcpus_usage'):
            ret[key] = usage.pop(key, 0)
        ret['started_at'] = usage.pop('start', None)
        ret['stopped_at'] = usage.pop('stop', None)
        ret['server_usages'] = self._normalize_server_usages(
            usage.pop('server_usages', []))
        ret['properties'] = usage
        return ret

    def _normalize_server_usage(self, server_usage):
        """ Normalize a server usage object """

        server_usage = server_usage.copy()
        # TODO(mordred) Right now there is already a location on the usage
        # object. Including one here seems verbose.
        server_usage.pop('tenant_id')
        ret = munch.Munch()

        ret['ended_at'] = server_usage.pop('ended_at', None)
        ret['started_at'] = server_usage.pop('started_at', None)
        for key in (
                'flavor',
                'instance_id',
                'name',
                'state'):
            ret[key] = server_usage.pop(key, '')
        for key in (
                'hours',
                'local_gb',
                'memory_mb',
                'uptime',
                'vcpus'):
            ret[key] = server_usage.pop(key, 0)
        ret['properties'] = server_usage
        return ret

    def _normalize_server_usages(self, server_usages):
        ret = []
        for server_usage in server_usages:
            ret.append(self._normalize_server_usage(server_usage))
        return ret

    def _normalize_cluster_templates(self, cluster_templates):
        ret = []
        for cluster_template in cluster_templates:
            ret.append(self._normalize_cluster_template(cluster_template))
        return ret

    def _normalize_cluster_template(self, cluster_template):
        """Normalize Magnum cluster_templates."""
        cluster_template = cluster_template.copy()

        # Discard noise
        cluster_template.pop('links', None)
        cluster_template.pop('human_id', None)
        # model_name is a magnumclient-ism
        cluster_template.pop('model_name', None)

        ct_id = cluster_template.pop('uuid')

        ret = munch.Munch(
            id=ct_id,
            location=self._get_current_location(),
        )
        ret['is_public'] = cluster_template.pop('public')
        ret['is_registry_enabled'] = cluster_template.pop('registry_enabled')
        ret['is_tls_disabled'] = cluster_template.pop('tls_disabled')
        # pop floating_ip_enabled since we want to hide it in a future patch
        fip_enabled = cluster_template.pop('floating_ip_enabled', None)
        if not self.strict_mode:
            ret['uuid'] = ct_id
            if fip_enabled is not None:
                ret['floating_ip_enabled'] = fip_enabled
            ret['public'] = ret['is_public']
            ret['registry_enabled'] = ret['is_registry_enabled']
            ret['tls_disabled'] = ret['is_tls_disabled']

        # Optional keys
        for (key, default) in (
                ('fixed_network', None),
                ('fixed_subnet', None),
                ('http_proxy', None),
                ('https_proxy', None),
                ('labels', {}),
                ('master_flavor_id', None),
                ('no_proxy', None)):
            if key in cluster_template:
                ret[key] = cluster_template.pop(key, default)

        for key in (
                'apiserver_port',
                'cluster_distro',
                'coe',
                'created_at',
                'dns_nameserver',
                'docker_volume_size',
                'external_network_id',
                'flavor_id',
                'image_id',
                'insecure_registry',
                'keypair_id',
                'name',
                'network_driver',
                'server_type',
                'updated_at',
                'volume_driver'):
            ret[key] = cluster_template.pop(key)

        ret['properties'] = cluster_template
        return ret

    def _normalize_magnum_services(self, magnum_services):
        ret = []
        for magnum_service in magnum_services:
            ret.append(self._normalize_magnum_service(magnum_service))
        return ret

    def _normalize_magnum_service(self, magnum_service):
        """Normalize Magnum magnum_services."""
        magnum_service = magnum_service.copy()

        # Discard noise
        magnum_service.pop('links', None)
        magnum_service.pop('human_id', None)
        # model_name is a magnumclient-ism
        magnum_service.pop('model_name', None)

        ret = munch.Munch(location=self._get_current_location())

        for key in (
                'binary',
                'created_at',
                'disabled_reason',
                'host',
                'id',
                'report_count',
                'state',
                'updated_at'):
            ret[key] = magnum_service.pop(key)
        ret['properties'] = magnum_service
        return ret

    def _normalize_stacks(self, stacks):
        """Normalize Heat Stacks"""
        ret = []
        for stack in stacks:
            ret.append(self._normalize_stack(stack))
        return ret

    def _normalize_stack(self, stack):
        """Normalize Heat Stack"""
        stack = stack.copy()

        # Discard noise
        self._remove_novaclient_artifacts(stack)

        # Discard things heatclient adds that aren't in the REST
        stack.pop('action', None)
        stack.pop('status', None)
        stack.pop('identifier', None)

        stack_status = stack.pop('stack_status')
        (action, status) = stack_status.split('_', 1)

        ret = munch.Munch(
            id=stack.pop('id'),
            location=self._get_current_location(),
            action=action,
            status=status,
        )
        if not self.strict_mode:
            ret['stack_status'] = stack_status

        for (new_name, old_name) in (
                ('name', 'stack_name'),
                ('created_at', 'creation_time'),
                ('deleted_at', 'deletion_time'),
                ('updated_at', 'updated_time'),
                ('description', 'description'),
                ('is_rollback_enabled', 'disable_rollback'),
                ('parent', 'parent'),
                ('notification_topics', 'notification_topics'),
                ('parameters', 'parameters'),
                ('outputs', 'outputs'),
                ('owner', 'stack_owner'),
                ('status_reason', 'stack_status_reason'),
                ('stack_user_project_id', 'stack_user_project_id'),
                ('tempate_description', 'template_description'),
                ('timeout_mins', 'timeout_mins'),
                ('tags', 'tags')):
            value = stack.pop(old_name, None)
            ret[new_name] = value
            if not self.strict_mode:
                ret[old_name] = value
        ret['identifier'] = '{name}/{id}'.format(
            name=ret['name'], id=ret['id'])
        ret['properties'] = stack
        return ret

    def _normalize_machines(self, machines):
        """Normalize Ironic Machines"""
        ret = []
        for machine in machines:
            ret.append(self._normalize_machine(machine))
        return ret

    def _normalize_machine(self, machine):
        """Normalize Ironic Machine"""
        machine = machine.copy()

        # Discard noise
        self._remove_novaclient_artifacts(machine)

        # TODO(mordred) Normalize this resource

        return machine
