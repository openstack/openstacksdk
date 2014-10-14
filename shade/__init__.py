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
import operator
import time

from cinderclient import exceptions as cinder_exceptions
from cinderclient.v1 import client as cinder_client
import glanceclient
from ironicclient import client as ironic_client
from ironicclient import exceptions as ironic_exceptions
from keystoneclient import client as keystone_client
from novaclient import exceptions as nova_exceptions
from novaclient.v1_1 import client as nova_client
import os_client_config
import pbr.version
import troveclient.client as trove_client
from troveclient import exceptions as trove_exceptions


from shade import meta

__version__ = pbr.version.VersionInfo('shade').version_string()


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


def operator_cloud(**kwargs):
    cloud_config = os_client_config.OpenStackConfig().get_one_cloud(**kwargs)
    return OperatorCloud(
        cloud_config.name, cloud_config.region, **cloud_config.config)


def _get_service_values(kwargs, service_key):
    return {k[:-(len(service_key) + 1)]: kwargs[k]
            for k in kwargs.keys() if k.endswith(service_key)}


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
            except cinder_exceptions.Unauthorized as e:
                self.log.debug("cinder Unauthorized", exc_info=True)
                raise OpenStackCloudException(
                    "Invalid OpenStack Cinder credentials.: %s" % e.message)
            except cinder_exceptions.AuthorizationFailure as e:
                self.log.debug("cinder AuthorizationFailure", exc_info=True)
                raise OpenStackCloudException(
                    "Unable to authorize user: %s" % e.message)

            if self._cinder_client is None:
                raise OpenStackCloudException(
                    "Failed to instantiate cinder client."
                    " This could mean that your credentials are wrong.")

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
            except trove_exceptions.Unauthorized as e:
                self.log.debug("trove Unauthorized", exc_info=True)
                raise OpenStackCloudException(
                    "Invalid OpenStack Trove credentials.: %s" % e.message)
            except trove_exceptions.AuthorizationFailure as e:
                self.log.debug("trove AuthorizationFailure", exc_info=True)
                raise OpenStackCloudException(
                    "Unable to authorize user: %s" % e.message)

            if self._trove_client is None:
                raise OpenStackCloudException(
                    "Failed to instantiate Trove client."
                    " This could mean that your credentials are wrong.")

        return self._trove_client

    def get_name(self):
        return self.name

    def get_region(self):
        return self.region_name

    @property
    def flavor_cache(self):
        if not self._flavor_cache:
            self._flavor_cache = {
                flavor.id: flavor
                for flavor in self.nova_client.flavors.list()}
        return self._flavor_cache

    def get_flavor_name(self, flavor_id):
        flavor = self.flavor_cache.get(flavor_id, None)
        if flavor:
            return flavor.name
        return None

    def get_flavor_by_ram(self, ram, include=None):
        for flavor in sorted(
                self.flavor_cache.values(),
                key=operator.attrgetter('ram')):
            if (flavor.ram >= ram and
                    (not include or include in flavor.name)):
                return flavor
        raise OpenStackCloudException(
            "Cloud not find a flavor with {ram} and '{include}'".format(
                ram=ram, include=include))

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
                images[image.id] = image
        except (OpenStackCloudException,
                glanceclient.exc.HTTPInternalServerError):
            # We didn't have glance, let's try nova
            # If this doesn't work - we just let the exception propagate
            for image in self.nova_client.images.list():
                images[image.id] = image
        return images

    def list_images(self):
        if self._image_cache is None:
            self._image_cache = self._get_images_from_cloud()
        return self._image_cache

    def get_image_name(self, image_id):
        if image_id not in self.list_images():
            self._image_cache[image_id] = None
        if self._image_cache[image_id]:
            return self._image_cache[image_id].name
        return None

    def get_image_id(self, image_name, exclude=None):
        image = self.get_image_by_name(image_name, exclude)
        if image:
            return image.id
        return None

    def get_image_by_name(self, name, exclude=None):
        for (image_id, image) in self.list_images().items():
            if (name in image.name and (
                    not exclude or exclude not in image.name)):
                return image
        raise OpenStackCloudException(
            "Error finding image id from name(%s)" % name)

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

    def get_server_by_id(self, server_id):
        for server in self.nova_client.servers.list():
            if server.id == server_id:
                return server
        return None

    def get_server_by_name(self, server_name):
        for server in self.nova_client.servers.list():
            if server.name == server_name:
                return server
        return None

    def get_server_id(self, server_name):
        server = get_server_by_name(server_name)
        if server:
            return server.id
        return None

    def get_server_meta(self, server):
        server_vars = meta.get_hostvars_from_server(self, server)
        groups = meta.get_groups_from_server(self, server, server_vars)
        return dict(server_vars=server_vars, groups=groups)

    def add_ip_from_pool(self, server, pools):

        # instantiate FloatingIPManager object
        floating_ip_obj = floating_ips.FloatingIPManager(self.nova_client)

        # empty dict and list
        usable_floating_ips = {}

        # get the list of all floating IPs. Mileage may
        # vary according to Nova Compute configuration
        # per cloud provider
        all_floating_ips = floating_ip_obj.list()

        # iterate through all pools of IP address. Empty
        # string means all and is the default value
        for pool in pools:
            # temporary list per pool
            pool_ips = []
            # loop through all floating IPs
            for f_ip in all_floating_ips:
                # if not reserved and the correct pool, add
                if f_ip.instance_id is None and (f_ip.pool == pool):
                    pool_ips.append(f_ip.ip)
                    # only need one
                    break

            # if the list is empty, add for this pool
            if not pool_ips:
                try:
                    new_ip = self.nova_client.floating_ips.create(pool)
                except Exception as e:
                    raise OpenStackCloudException(
                        "Unable to create floating ip in pool %s" % pool)
                pool_ips.append(new_ip.ip)
            # Add to the main list
            usable_floating_ips[pool] = pool_ips

        # finally, add ip(s) to instance for each pool
        for pool in usable_floating_ips:
            for ip in usable_floating_ips[pool]:
                self.add_ip_list(server, [ip])
                # We only need to assign one ip - but there is an inherent
                # race condition and some other cloud operation may have
                # stolen an available floating ip
                break

    def add_ip_list(self, server, ips):
        # add ip(s) to instance
        for ip in ips:
            try:
                server.add_floating_ip(ip)
            except Exception as e:
                raise OpenStackCloudException(
                    "Error attaching IP {ip} to instance {id}: {msg} ".format(
                        ip=ip, id=server.id, msg=e.message))

    def add_auto_ip(self, server):
        try:
            new_ip = self.nova_client.floating_ips.create()
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to create floating ip: %s" % (e.message))
        try:
            self.add_ip_list(server, [new_ip])
        except OpenStackCloudException:
            # Clean up - we auto-created this ip, and it's not attached
            # to the server, so the cloud will not know what to do with it
            self.nova_client.floating_ips.delete(new_ip)
            raise

    def add_ips_to_server(self, server, auto_ip=True, ips=None, ip_pool=None):
        if ip_pool:
            self.add_ip_from_pool(server, ip_pool)
        elif ips:
            self.add_ip_list(server, ips)
        elif auto_ip:
            self.add_auto_ip(server)
        else:
            return server

        # this may look redundant, but if there is now a
        # floating IP, then it needs to be obtained from
        # a recent server object if the above code path exec'd
        try:
            server = self.nova_client.servers.get(server.id)
        except Exception as e:
            raise OpenStackCloudException(
                "Error in getting info from instance: %s " % e.message)
        return server

    def create_server(self, bootargs, bootkwargs,
                      auto_ip=True, ips=None, ip_pool=None,
                      wait=False, timeout=180):
        try:
            server = self.nova_client.servers.create(*bootargs, **bootkwargs)
            server = self.nova_client.servers.get(server.id)
        except Exception as e:
            raise OpenStackCloudException(
                "Error in creating instance: %s" % e.message)
        if server.status == 'ERROR':
            raise OpenStackCloudException(
                "Error in creating the server.")
        if wait:
            expire = time.time() + timeout
            while time.time() < expire:
                try:
                    server = self.nova_client.servers.get(server.id)
                except Exception:
                    continue

                if server.status == 'ACTIVE':
                    return self.add_ips_to_server(server, auto_ip, ips, ip_pool)

                if server.status == 'ERROR':
                    raise OpenStackCloudException(
                        "Error in creating the server, please check logs")
                time.sleep(2)

            raise OpenStackCloudException(
                "Timeout waiting for the server to come up.")
        return server

    def delete_server(self, name, wait=False, timeout=180):
        server_list = self.nova_client.servers.list(True, {'name': name})
        if server_list:
            server = [x for x in server_list if x.name == module.params['name']]
            self.nova_client.servers.delete(server.pop())
        if not wait:
            return
        expire = time.time() + timeout
        while time.time() < expire:
            server = nova.servers.list(True, {'name': name})
            if not server:
                return
            time.sleep(5)
        raise OpenStackCloudException(
            "Timed out waiting for server to get deleted.")


class OperatorCloud(OpenStackCloud):

    @property
    def ironic_client(self):
        if self._ironic_client is None:
            ironic_logging = logging.getLogger('ironicclient')
            ironic_logging.addHandler(logging.NullHandler())
            token = self.keystone_client.auth_token
            endpoint = self.get_endpoint(service_type='baremetal')
            try:
                self._ironic_client = ironic_client.Client(
                    '1', endpoint, token=token)
            except Exception as e:
                raise OpenStackCloudException(
                    "Error in connecting to ironic: %s" % e.message)
        return self._ironic_client

    def list_nics(self):
        return self.ironic_client.port.list()

    def list_nics_for_machine(self, uuid):
        return self.ironic_client.node.list_ports(uuid)

    def get_nic_by_mac(self, mac):
        try:
            return self.ironic_client.port.get(mac)
        except ironic_exceptions.ClientException:
            return None

    def list_machines(self):
        return self.ironic_client.node.list()

    def get_machine_by_uuid(self, uuid):
        try:
            return self.ironic_client.node.get(uuid)
        except ironic_exceptions.ClientException:
            return None

    def get_machine_by_mac(self, mac):
        try:
            port = self.ironic_client.port.get(mac)
            return self.ironic_client.node.get(port.node_uuid)
        except ironic_exceptions.ClientException:
            return None

    def register_machine(self, nics, **kwargs):
        try:
            machine = self.ironic_client.node.create(**kwargs)
        except Exception as e:
            raise OpenStackCloudException(
                    "Error registering machine with Ironic: %s" % e.message)

        created_nics = []
        try:
            for row in nics:
                nic = self.ironic_client.port.create(address=row['mac'],
                                                     node_uuid=machine.uuid)
                created_nics.append(nic.uuid)
        except Exception as e:
            for uuid in created_nics:
                self.ironic_client.port.delete(uuid)
            self.ironic_client.node.delete(machine.uuid)
            raise OpenStackCloudException(
                    "Error registering NICs with Ironic: %s" % e.message)
        return machine

    def unregister_machine(self, nics, uuid):
        for nic in nics:
            try:
                self.ironic_client.port.delete(
                        self.ironic_client.port.get_by_address(nic['mac']))
            except Exception as e:
                raise OpenStackCloudException(e.message)
        try:
            self.ironic_client.node.delete(uuid)
        except Exception as e:
            raise OpenStackCloudException(
                    "Error unregistering machine from Ironic: %s" % e.message)
