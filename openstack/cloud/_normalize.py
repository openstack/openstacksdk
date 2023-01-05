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

# TODO(shade) The normalize functions here should get merged in to
#             the sdk resource objects.

import munch

from openstack import resource

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
    'description',
    'key_name',
    'metadata',
    'networks',
    'personality',
    'private_v4',
    'public_v4',
    'public_v6',
    'server_groups',
    'status',
    'updated',
    'user_id',
    'tags',
)

_pushdown_fields = {
    'project': [
        'domain_id'
    ]
}


def _to_bool(value):
    if isinstance(value, str):
        if not value:
            return False
        prospective = value.lower().capitalize()
        return prospective == 'True'
    return bool(value)


def _pop_int(resource, key):
    return int(resource.pop(key, 0) or 0)


def _pop_or_get(resource, key, default, strict):
    if strict:
        return resource.pop(key, default)
    else:
        return resource.get(key, default)


class Normalizer:
    '''Mix-in class to provide the normalization functions.

    This is in a separate class just for on-disk source code organization
    reasons.
    '''

    def _remove_novaclient_artifacts(self, item):
        # Remove novaclient artifacts
        item.pop('links', None)
        item.pop('NAME_ATTR', None)
        item.pop('HUMAN_ID', None)
        item.pop('human_id', None)
        item.pop('request_ids', None)
        item.pop('x_openstack_request_ids', None)

    def _normalize_image(self, image):
        if isinstance(image, resource.Resource):
            image = image.to_dict(ignore_none=True, original_names=True)
            location = image.pop(
                'location',
                self._get_current_location(project_id=image.get('owner')))
        else:
            location = self._get_current_location(
                project_id=image.get('owner'))
            # This copy is to keep things from getting epically weird in tests
            image = image.copy()

        new_image = munch.Munch(location=location)

        # Discard noise
        self._remove_novaclient_artifacts(image)

        # If someone made a property called "properties" that contains a
        # string (this has happened at least one time in the wild), the
        # the rest of the normalization here goes belly up.
        properties = image.pop('properties', {})
        if not isinstance(properties, dict):
            properties = {'properties': properties}

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

        metadata = image.pop('metadata', {}) or {}
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
                if key != 'properties':
                    new_image[key] = val
            new_image['protected'] = protected
            new_image['metadata'] = properties
            new_image['created'] = new_image['created_at']
            new_image['updated'] = new_image['updated_at']
            new_image['minDisk'] = new_image['min_disk']
            new_image['minRam'] = new_image['min_ram']
        return new_image

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

    def _normalize_coe_clusters(self, coe_clusters):
        ret = []
        for coe_cluster in coe_clusters:
            ret.append(self._normalize_coe_cluster(coe_cluster))
        return ret

    def _normalize_coe_cluster(self, coe_cluster):
        """Normalize Magnum COE cluster."""
        coe_cluster = coe_cluster.copy()

        # Discard noise
        coe_cluster.pop('links', None)

        c_id = coe_cluster.pop('uuid')

        ret = munch.Munch(
            id=c_id,
            location=self._get_current_location(),
        )

        if not self.strict_mode:
            ret['uuid'] = c_id

        for key in (
                'status',
                'cluster_template_id',
                'stack_id',
                'keypair',
                'master_count',
                'create_timeout',
                'node_count',
                'name'):
            if key in coe_cluster:
                ret[key] = coe_cluster.pop(key)

        ret['properties'] = coe_cluster
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

    def _normalize_machines(self, machines):
        """Normalize Ironic Machines"""
        ret = []
        for machine in machines:
            ret.append(self._normalize_machine(machine))
        return ret

    def _normalize_machine(self, machine):
        """Normalize Ironic Machine"""
        if isinstance(machine, resource.Resource):
            machine = machine._to_munch()
        else:
            machine = machine.copy()

        # Discard noise
        self._remove_novaclient_artifacts(machine)

        return machine
