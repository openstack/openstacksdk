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
        new_image = munch.Munch(location=self.current_location)
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
        server['location'] = self.current_location

        az = server.get('OS-EXT-AZ:availability_zone', None)
        if az:
            server['az'] = az

        # Ensure volumes is always in the server dict, even if empty
        server['volumes'] = []

        return server
