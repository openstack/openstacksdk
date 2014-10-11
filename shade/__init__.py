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
import os

from cinderclient.v1 import client as cinder_client
from cinderclient import exceptions as cinder_exceptions
import glanceclient
from ironicclient import client as ironic_client
from ironicclient import exceptions as ironic_exceptions
from keystoneclient import client as keystone_client
from novaclient import exceptions as nova_exceptions
from novaclient.v1_1 import client as nova_client
import os_client_config
import troveclient.client as trove_client
from troveclient import exceptions as trove_exceptions
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


def openstack_clouds(config=None):
    if not config:
        config = os_client_config.OpenStackConfig()
    return [OpenStackCloud(f.name, f.region, **f.config)
            for f in config.get_all_clouds()]


def openstack_cloud(**kwargs):
    cloud_config = os_client_config.OpenStackConfig().get_one_cloud(
        **kwargs)
    return OpenStackCloud(
        cloud_config.name, cloud_config.region, **cloud_config.config)


def _get_service_values(kwargs, service_key):
    return { k[:-(len(service_key) + 1)] : kwargs[k]
             for k in kwargs.keys() if k.endswith(service_key) }


class OpenStackCloud(object):

    def __init__(self, cloud, region='',
                 image_cache=None, flavor_cache=None, volume_cache=None,
                 debug=False, **kwargs):

        self.name = cloud
        self.region = region

        self.username = kwargs['username']
        self.password = kwargs['password']
        self.project_name = kwargs['project_name']
        self.auth_url = kwargs['auth_url']

        self.region_name = kwargs.get('region_name', region)
        self.auth_token = kwargs.get('auth_token', None)

        self.service_types = _get_service_values(kwargs, 'service_type')
        self.endpoints = _get_service_values(kwargs, 'endpoint')
        self.api_versions = _get_service_values(kwargs, 'api_version')

        self.user_domain_name = kwargs.get('user_domain_name', None)
        self.project_domain_name = kwargs.get('project_domain_name', None)

        self.insecure = kwargs.get('insecure', False)
        self.endpoint_type = kwargs.get('endpoint_type', 'publicURL')
        self.cert = kwargs.get('cert', None)
        self.cacert = kwargs.get('cacert', None)
        self.private = kwargs.get('private', False)

        self._image_cache = image_cache
        self._flavor_cache = flavor_cache
        self._volume_cache = volume_cache

        self.debug = debug

        self._nova_client = None
        self._glance_client = None
        self._ironic_client = None
        self._keystone_client = None
        self._cinder_client = None
        self._trove_client = None

        self.log = logging.getLogger('shade')
        self.log.setLevel(logging.INFO)
        self.log.addHandler(logging.StreamHandler())

    def get_service_type(self, service):
        return self.service_types.get(service, service)

    @property
    def nova_client(self):
        if self._nova_client is None:
            kwargs = dict(
                region_name=self.region_name,
                service_type=self.get_service_type('compute'),
                insecure=self.insecure,
            )
            # Try to use keystone directly first, for potential token reuse
            try:
                kwargs['auth_token'] = self.keystone_client.auth_token
                kwargs['bypass_url'] = self.get_endpoint(
                    self.get_service_type('compute'))
            except OpenStackCloudException:
                pass

            # Make the connection
            self._nova_client = nova_client.Client(
                self.username,
                self.password,
                self.project_name,
                self.auth_url,
                **kwargs
            )

            self._nova_client.authenticate()
            try:
                self._nova_client.authenticate()
            except nova_exceptions.Unauthorized as e:
                self.log.debug("nova Unauthorized", exc_info=True)
                raise OpenStackCloudException(
                    "Invalid OpenStack Nova credentials: %s" % e.message)
            except nova_exceptions.AuthorizationFailure as e:
                self.log.debug("nova AuthorizationFailure", exc_info=True)
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
                if self.auth_token:
                    self._keystone_client = keystone_client.Client(
                        endpoint=self.auth_url,
                        token=self.auth_token)
                else:
                    self._keystone_client = keystone_client.Client(
                        username=self.username,
                        password=self.password,
                        project_name=self.project_name,
                        region_name=self.region_name,
                        auth_url=self.auth_url,
                        user_domain_name=self.user_domain_name,
                        project_domain_name=self.project_domain_name)
                self._keystone_client.authenticate()
            except Exception as e:
                self.log.debug("keystone unknown issue", exc_info=True)
                raise OpenStackCloudException(
                    "Error authenticating to the keystone: %s " % e.message)
        return self._keystone_client

    def _get_glance_api_version(self, endpoint):
        if 'image' in self.api_versions:
            return self.api_versions['image']
        # Yay. We get to guess ...
        # Get rid of trailing '/' if present
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        url_bits = endpoint.split('/')
        if url_bits[-1].startswith('v'):
            return url_bits[-1][1]
        return '1'  # Who knows? Let's just try 1 ...

    @property
    def glance_client(self):
        if self._glance_client is None:
            token = self.keystone_client.auth_token
            endpoint = self.get_endpoint(
                service_type=self.get_service_type('image'))
            glance_api_version = self._get_glance_api_version(endpoint)
            try:
                self._glance_client = glanceclient.Client(
                    glance_api_version, endpoint, token=token,
                    session=self.keystone_client.session)
            except Exception as e:
                self.log.debug("glance unknown issue", exc_info=True)
                raise OpenStackCloudException(
                    "Error in connecting to glance: %s" % e.message)

            if not self._glance_client:
                raise OpenStackCloudException("Error connecting to glance")
        return self._glance_client

    @property
    def cinder_client(self):

        if self._cinder_client is None:
            # Make the connection
            self._cinder_client = cinder_client.Client(
                self.username,
                self.password,
                self.project_name,
                self.auth_url,
                region_name=self.region_name,
            )

            try:
                self._cinder_client.authenticate()
            except cinder_exceptions.Unauthorized, e:
                self.log.debug("cinder Unauthorized", exc_info=True)
                raise OpenStackCloudException(
                    "Invalid OpenStack Cinder credentials.: %s" % e.message)
            except cinder_exceptions.AuthorizationFailure, e:
                self.log.debug("cinder AuthorizationFailure", exc_info=True)
                raise OpenStackCloudException(
                    "Unable to authorize user: %s" % e.message)

            if self._cinder_client is None:
                raise OpenStackCloudException(
                    "Failed to instantiate cinder client. This could mean that your"
                    " credentials are wrong.")

        return self._cinder_client

    def _get_trove_api_version(self, endpoint):
        if 'database' in self.api_versions:
            return self.api_versions['database']
        # Yay. We get to guess ...
        # Get rid of trailing '/' if present
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        url_bits = endpoint.split('/')
        for bit in url_bits:
            if bit.startswith('v'):
                return bit[1:]
        return '1.0'  # Who knows? Let's just try 1.0 ...

    @property
    def trove_client(self):
        if self._trove_client is None:
            endpoint = self.get_endpoint(
                service_type=self.get_service_type('database'))
            trove_api_version = self._get_trove_api_version(endpoint)
            # Make the connection - can't use keystone session until there
            # is one
            self._trove_client = trove_client.Client(
                trove_api_version,
                self.username,
                self.password,
                self.project_name,
                self.auth_url,
                region_name=self.region_name,
                service_type=self.get_service_type('database'),
                )

            try:
                self._trove_client.authenticate()
            except trove_exceptions.Unauthorized, e:
                self.log.debug("trove Unauthorized", exc_info=True)
                raise OpenStackCloudException(
                    "Invalid OpenStack Trove credentials.: %s" % e.message)
            except trove_exceptions.AuthorizationFailure, e:
                self.log.debug("trove AuthorizationFailure", exc_info=True)
                raise OpenStackCloudException(
                    "Unable to authorize user: %s" % e.message)

            if self._trove_client is None:
                raise OpenStackCloudException(
                    "Failed to instantiate cinder client. This could mean that your"
                    " credentials are wrong.")

        return self._trove_client
        
    @property
    def ironic_client(self):
        if self._ironic_client is None:
            token = self.keystone_client.auth_token
            endpoint = self.get_endpoint(service_type='baremetal')
            try:
                self._ironic_client = ironic_client.Client('1', endpoint, token=token)
            except Exception as e:
                raise OpenStackCloudException("Error in connecting to ironic: %s" % e.message)
        return self._ironic_client

    def get_name(self):
        return self.name

    def get_region(self):
        return self.region_name

    def get_flavor_name(self, flavor_id):
        if not self._flavor_cache:
            self._flavor_cache = dict(
                [(flavor.id, flavor.name)
                    for flavor in self.nova_client.flavors.list()])
        return self._flavor_cache.get(flavor_id, None)

    def get_endpoint(self, service_type):
        if service_type in self.endpoints:
            return self.endpoints[service_type]
        try:
            endpoint = self.keystone_client.service_catalog.url_for(
                service_type=service_type, endpoint_type=self.endpoint_type)
        except Exception as e:
            self.log.debug("keystone cannot get endpoint", exc_info=True)
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
        except (OpenStackCloudException,
                glanceclient.exc.HTTPInternalServerError):
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

    def _get_volumes_from_cloud(self):
        try:
            return self.cinder_client.volumes.list()
        except Exception:
            return []

    def list_volumes(self):
        if self._volume_cache is None:
            self._volume_cache = self._get_volumes_from_cloud()
        return self._volume_cache

    def get_volumes(self, server):
        volumes = []
        for volume in self.list_volumes():
            for attach in volume.attachments:
                if attach['server_id'] == server.id:
                    volumes.append(volume)
        return volumes

    def get_volume_id(self, volume_name):
        for v in self.cinder_client.volumes.list():
            if v.display_name == volume_name:
                return v.id
        return None

    def get_server_id(self, server_name):
        for server in self.nova_client.servers.list():
            if server.name == server_name:
                return server.id
        return None

    def list_ironic_nodes(self):
        return self.ironic_client.node.list()

    def get_ironic_node(self, node_name):
        return self.ironic_client.node.get(node_name)

    def list_ironic_ports(self):
        return self.ironic_client.port.list()

    def get_ironic_port(self, port_name):
        return self.ironic_client.port.get(port_name)

    def list_ironic_ports_for_node(self, node_name):
        return self.ironic_client.node.list_ports(node_name)
