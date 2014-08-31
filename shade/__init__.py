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

import logging

import glanceclient
from keystoneclient.v2_0 import client as keystone_client
from novaclient import exceptions as nova_exceptions
from novaclient.v1_1 import client as nova_client
import pbr.version


__version__ = pbr.version.VersionInfo('shade').version_string()


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


class OpenStackCloudException(Exception):
    pass


class OpenStackCloud(object):

    def __init__(self, name, username, password, project_id, auth_url,
                 region_name, nova_service_type='compute', insecure=False,
                 endpoint_type='publicURL', token=None, image_cache=None,
                 flavor_cache=None, debug=False):

        self.name = name
        self.username = username
        self.password = password
        self.project_id = project_id
        self.auth_url = auth_url
        self.region_name = region_name
        self.nova_service_type = nova_service_type
        self.insecure = insecure
        self.endpoint_type = endpoint_type
        self.token = token
        self._image_cache = image_cache
        self.flavor_cache = flavor_cache
        self.debug = debug

        self._nova_client = None
        self._glance_client = None
        self._keystone_client = None

        self.log = logging.getLogger('shade')
        self.log.setLevel(logging.INFO)
        self.log.addHandler(logging.StreamHandler())

    @property
    def nova_client(self):
        if self._nova_client is None:
            kwargs = dict(
                region_name=self.region_name,
                service_type=self.nova_service_type,
                insecure=self.insecure,
            )
            # Try to use keystone directly first, for potential token reuse
            try:
                kwargs['auth_token'] = self.keystone_client.auth_token
                kwargs['bypass_url'] = self.get_endpoint(
                    self.nova_service_type)
            except OpenStackCloudException:
                pass

            # Make the connection
            self._nova_client = nova_client.Client(
                self.username,
                self.password,
                self.project_id,
                self.auth_url,
                **kwargs
            )

            try:
                self._nova_client.authenticate()
            except nova_exceptions.Unauthorized as e:
                self.logger.debug("nova Unauthorized", exc_info=True)
                raise OpenStackCloudException(
                    "Invalid OpenStack Nova credentials.: %s" % e.message)
            except nova_exceptions.AuthorizationFailure as e:
                self.logger.debug("nova AuthorizationFailure", exc_info=True)
                raise OpenStackCloudException(
                    "Unable to authorize user: %s" % e.message)

            if self._nova_client is None:
                raise OpenStackCloudException(
                    "Failed to instantiate nova client."
                    " This could mean that your credentials are wrong.")

        return self._nova_client

    @property
    def keystone_client(self):
        if self._keystone_client is None:
            # keystoneclient does crazy things with logging that are
            # none of them interesting
            keystone_logging = logging.getLogger('keystoneclient')
            keystone_logging.addHandler(logging.NullHandler())

            try:
                if self.token:
                    self._keystone_client = keystone_client.Client(
                        endpoint=self.auth_url,
                        token=self.token)
                else:
                    self._keystone_client = keystone_client.Client(
                        username=self.username,
                        password=self.password,
                        tenant_name=self.project_id,
                        region_name=self.region_name,
                        auth_url=self.auth_url)
            except Exception as e:
                self.logger.debug("keystone unknown issue", exc_info=True)
                raise OpenStackCloudException(
                    "Error authenticating to the keystone: %s " % e.message)
        return self._keystone_client

    @property
    def glance_client(self):
        if self._glance_client is None:
            token = self.keystone_client.auth_token
            endpoint = self.get_endpoint(service_type='image')
            try:
                # Seriously. I'm not kidding. The first argument is '1'. And
                # no, it's not a version that's discoverable from keystone
                self._glance_client = glanceclient.Client(
                    '1', endpoint, token=token)
            except Exception as e:
                self.logger.debug("glance unknown issue", exc_info=True)
                raise OpenStackCloudException(
                    "Error in connecting to glance: %s" % e.message)

            if not self._glance_client:
                raise OpenStackCloudException("Error connecting to glance")
        return self._glance_client

    def get_name(self):
        return self.name

    def get_region(self):
        return self.region_name

    def get_flavor_name(self, flavor_id):
        if not self.flavor_cache:
            self.flavor_cache = dict(
                [(flavor.id, flavor.name)
                    for flavor in self.nova_client.flavors.list()])
        return self.flavor_cache.get(flavor_id, None)

    def get_endpoint(self, service_type):
        try:
            endpoint = self.keystone_client.service_catalog.url_for(
                service_type=service_type, endpoint_type=self.endpoint_type)
        except Exception as e:
            self.logger.debug("keystone cannot get endpoint", exc_info=True)
            raise OpenStackCloudException(
                "Error getting %s endpoint: %s" % (service_type, e.message))
        return endpoint

    def list_servers(self):
        return self.nova_client.servers.list()

    def list_keypairs(self):
        return self.nova_client.keypairs.list()

    def create_keypair(self, name, public_key):
        return self.nova_client.keypairs.create(name, public_key)

    def delete_keypair(self, name):
        return self.nova_client.keypairs.delete(name)

    def _get_images_from_cloud(self):
        # First, try to actually get images from glance, it's more efficient
        images = dict()
        try:
            # This can fail both because we don't have glanceclient installed
            # and because the cloud may not expose the glance API publically
            for image in self.glance_client.images.list():
                images[image.id] = image.name
        except OpenStackCloudException:
            # We didn't have glance, let's try nova
            # If this doesn't work - we just let the exception propagate
            for image in self.nova_client.images.list():
                images[image.id] = image.name
        return images

    def list_images(self):
        if self._image_cache is None:
            self._image_cache = self._get_images_from_cloud()
        return self._image_cache

    def get_image_name(self, image_id):
        if image_id not in self.list_images():
            self._image_cache[image_id] = None
        return self._image_cache[image_id]

    def get_image_id(self, image_name):
        for (image_id, name) in self.list_images().items():
            if name == image_name:
                return image_id
        return None
