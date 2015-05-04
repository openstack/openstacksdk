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

import hashlib
import logging
import operator
import os
import time

from cinderclient.v1 import client as cinder_client
from dogpile import cache
import glanceclient
import glanceclient.exc
from ironicclient import client as ironic_client
from ironicclient import exceptions as ironic_exceptions
import jsonpatch
from keystoneclient import auth as ksc_auth
from keystoneclient import session as ksc_session
from keystoneclient import client as keystone_client
from novaclient import client as nova_client
from novaclient import exceptions as nova_exceptions
from neutronclient.v2_0 import client as neutron_client
import os_client_config
import pbr.version
import swiftclient.client as swift_client
import swiftclient.exceptions as swift_exceptions
import troveclient.client as trove_client

# Disable the Rackspace warnings about deprecated certificates. We are aware
import warnings
warnings.filterwarnings('ignore', 'Certificate has no `subjectAltName`')

from shade.exc import *  # noqa
from shade import meta
from shade import task_manager
from shade import _tasks

__version__ = pbr.version.VersionInfo('shade').version_string()
OBJECT_MD5_KEY = 'x-object-meta-x-shade-md5'
OBJECT_SHA256_KEY = 'x-object-meta-x-shade-sha256'
IMAGE_MD5_KEY = 'owner_specified.shade.md5'
IMAGE_SHA256_KEY = 'owner_specified.shade.sha256'


OBJECT_CONTAINER_ACLS = {
    'public': ".r:*,.rlistings",
    'private': '',
}


def openstack_clouds(config=None, debug=False):
    if not config:
        config = os_client_config.OpenStackConfig()
    return [
        OpenStackCloud(
            cloud=f.name, debug=debug,
            cache_interval=config.get_cache_max_age(),
            cache_class=config.get_cache_class(),
            cache_arguments=config.get_cache_arguments(),
            **f.config)
        for f in config.get_all_clouds()
    ]


def openstack_cloud(debug=False, **kwargs):
    config = kwargs.get('config')
    if config is None:
        config = os_client_config.OpenStackConfig()
    cloud_config = config.get_one_cloud(**kwargs)
    return OpenStackCloud(
        cloud=cloud_config.name,
        cache_interval=config.get_cache_max_age(),
        cache_class=config.get_cache_class(),
        cache_arguments=config.get_cache_arguments(),
        debug=debug, **cloud_config.config)


def operator_cloud(debug=False, **kwargs):
    config = os_client_config.OpenStackConfig()
    cloud_config = config.get_one_cloud(**kwargs)
    return OperatorCloud(
        cloud_config.name, debug=debug,
        cache_interval=config.get_cache_max_age(),
        cache_class=config.get_cache_class(),
        cache_arguments=config.get_cache_arguments(),
        **cloud_config.config)


def _ssl_args(verify, cacert, cert, key):
    if cacert:
        if not os.path.exists(cacert):
            raise OpenStackCloudException(
                "CA Cert {0} does not exist".format(cacert))
        verify = cacert

    if cert:
        if not os.path.exists(cert):
            raise OpenStackCloudException(
                "Client Cert {0} does not exist".format(cert))
        if key:
            if not os.path.exists(key):
                raise OpenStackCloudException(
                    "Client key {0} does not exist".format(key))
            cert = (cert, key)
    return (verify, cert)


def _get_service_values(kwargs, service_key):
    return {k[:-(len(service_key) + 1)]: kwargs[k]
            for k in kwargs.keys() if k.endswith(service_key)}


def _iterate_timeout(timeout, message):
    """Iterate and raise an exception on timeout.

    This is a generator that will continually yield and sleep for 2
    seconds, and if the timeout is reached, will raise an exception
    with <message>.

    """

    start = time.time()
    count = 0
    while (timeout is None) or (time.time() < start + timeout):
        count += 1
        yield count
        time.sleep(2)
    raise OpenStackCloudTimeout(message)


def _cache_on_arguments(*cache_on_args, **cache_on_kwargs):
    def _inner_cache_on_arguments(func):
        def _cache_decorator(obj, *args, **kwargs):
            the_method = obj._cache.cache_on_arguments(
                *cache_on_args, **cache_on_kwargs)(
                    func.__get__(obj, type(obj)))
            return the_method(*args, **kwargs)

        def invalidate(obj, *args, **kwargs):
            return obj._cache.cache_on_arguments()(func).invalidate(
                *args, **kwargs)

        _cache_decorator.invalidate = invalidate

        return _cache_decorator
    return _inner_cache_on_arguments


def _no_pending_volumes(volumes):
    '''If there are any volumes not in a steady state, don't cache'''
    for volume in volumes:
        if volume['status'] not in ('available', 'error'):
            return False
    return True


def _no_pending_images(images):
    '''If there are any images not in a steady state, don't cache'''
    for image_id, image in iter(images.items()):
        if image.status not in ('active', 'deleted', 'killed'):
            return False
    return True


class OpenStackCloud(object):
    """Represent a connection to an OpenStack Cloud.

    OpenStackCloud is the entry point for all cloud operations, regardless
    of which OpenStack service those operations may ultimately come from.
    The operations on an OpenStackCloud are resource oriented rather than
    REST API operation oriented. For instance, one will request a Floating IP
    and that Floating IP will be actualized either via neutron or via nova
    depending on how this particular cloud has decided to arrange itself.

    :param string name: The name of the cloud
    :param dict auth: Dictionary containing authentication information.
                      Depending on the value of auth_type, the contents
                      of this dict can vary wildly.
    :param string region_name: The region of the cloud that all operations
                               should be performed against.
                               (optional, default '')
    :param string auth_type: The name of the keystone auth_type to be used
    :param string endpoint_type: The type of endpoint to get for services
                                 from the service catalog. Valid types are
                                 `public` ,`internal` or `admin`. (optional,
                                 defaults to `public`)
    :param bool private: Whether to return or use private IPs by default for
                         servers. (optional, defaults to False)
    :param float api_timeout: A timeout to pass to REST client constructors
                              indicating network-level timeouts. (optional)
    :param bool verify: The verification arguments to pass to requests. True
                        tells requests to verify SSL requests, False to not
                        verify. (optional, defaults to True)
    :param string cacert: A path to a CA Cert bundle that can be used as part
                          of verifying SSL requests. If this is set, verify
                          is set to True. (optional)
    :param string cert: A path to a client certificate to pass to requests.
                        (optional)
    :param string key: A path to a client key to pass to requests. (optional)
    :param bool debug: Enable or disable debug logging (optional, defaults to
                       False)
    :param int cache_interval: How long to cache items fetched from the cloud.
                               Value will be passed to dogpile.cache. None
                               means do not cache at all.
                               (optional, defaults to None)
    :param string cache_class: What dogpile.cache cache class to use.
                               (optional, defaults to "dogpile.cache.null")
    :param dict cache_arguments: Additional arguments to pass to the cache
                                 constructor (optional, defaults to None)
    :param TaskManager manager: Optional task manager to use for running
                                OpenStack API tasks. Unless you're doing
                                rate limiting client side, you almost
                                certainly don't need this. (optional)
    :param bool image_api_use_tasks: Whether or not this cloud needs to
                                     use the glance task-create interface for
                                     image upload activities instead of direct
                                     calls. (optional, defaults to False)
    """

    def __init__(self, cloud, auth,
                 region_name='',
                 auth_type='password',
                 endpoint_type='public',
                 private=False,
                 verify=True, cacert=None, cert=None, key=None,
                 api_timeout=None,
                 debug=False, cache_interval=None,
                 cache_class='dogpile.cache.null',
                 cache_arguments=None,
                 manager=None,
                 image_api_use_tasks=False,
                 **kwargs):

        self.name = cloud
        self.auth = auth
        self.region_name = region_name
        self.auth_type = auth_type
        self.endpoint_type = endpoint_type
        self.private = private
        self.api_timeout = api_timeout
        if manager is not None:
            self.manager = manager
        else:
            self.manager = task_manager.TaskManager(
                name=self.name, client=self)

        self.service_types = _get_service_values(kwargs, 'service_type')
        self.service_names = _get_service_values(kwargs, 'service_name')
        self.endpoints = _get_service_values(kwargs, 'endpoint')
        self.api_versions = _get_service_values(kwargs, 'api_version')
        self.image_api_use_tasks = image_api_use_tasks

        (self.verify, self.cert) = _ssl_args(verify, cacert, cert, key)

        self._cache = cache.make_region(
            function_key_generator=self._make_cache_key
        ).configure(
            cache_class, expiration_time=cache_interval,
            arguments=cache_arguments)
        self._container_cache = dict()
        self._file_hash_cache = dict()

        self._keystone_session = None
        self._auth_token = None

        self._cinder_client = None
        self._glance_client = None
        self._glance_endpoint = None
        self._ironic_client = None
        self._keystone_client = None
        self._neutron_client = None
        self._nova_client = None
        self._swift_client = None
        self._trove_client = None

        self.log = logging.getLogger('shade')
        log_level = logging.INFO
        if debug:
            log_level = logging.DEBUG
        self.log.setLevel(log_level)
        self.log.addHandler(logging.StreamHandler())

    def _make_cache_key(self, namespace, fn):
        fname = fn.__name__
        if namespace is None:
            name_key = self.name
        else:
            name_key = '%s:%s' % (self.name, namespace)

        def generate_key(*args, **kwargs):
            arg_key = ','.join(args)
            kw_keys = sorted(kwargs.keys())
            kwargs_key = ','.join(
                ['%s:%s' % (k, kwargs[k]) for k in kw_keys if k != 'cache'])
            ans = "_".join(
                [name_key, fname, arg_key, kwargs_key])
            return ans
        return generate_key

    def get_service_type(self, service):
        return self.service_types.get(service, service)

    def get_service_name(self, service):
        return self.service_names.get(service, None)

    def _get_nova_api_version(self):
        return self.api_versions['compute']

    @property
    def nova_client(self):
        if self._nova_client is None:

            # Make the connection
            try:
                # trigger exception on lack of compute. (what?)
                self.get_session_endpoint('compute')
                self._nova_client = nova_client.Client(
                    self._get_nova_api_version(),
                    session=self.keystone_session,
                    service_name=self.get_service_name('compute'),
                    region_name=self.region_name,
                    timeout=self.api_timeout)
            except Exception:
                self.log.debug("Couldn't construct nova object", exc_info=True)
                raise

            if self._nova_client is None:
                raise OpenStackCloudException(
                    "Failed to instantiate nova client."
                    " This could mean that your credentials are wrong.")

        return self._nova_client

    @property
    def keystone_session(self):
        if self._keystone_session is None:
            # keystoneclient does crazy things with logging that are
            # none of them interesting
            keystone_logging = logging.getLogger('keystoneclient')
            keystone_logging.addHandler(logging.NullHandler())

            try:
                auth_plugin = ksc_auth.get_plugin_class(self.auth_type)
            except Exception as e:
                self.log.debug("keystone auth plugin failure", exc_info=True)
                raise OpenStackCloudException(
                    "Could not find auth plugin: {plugin}".format(
                    plugin=self.auth_type))
            try:
                keystone_auth = auth_plugin(**self.auth)
            except Exception as e:
                self.log.debug(
                    "keystone couldn't construct plugin", exc_info=True)
                raise OpenStackCloudException(
                    "Error constructing auth plugin: {plugin}".format(
                        plugin=self.auth_type))

            try:
                self._keystone_session = ksc_session.Session(
                    auth=keystone_auth,
                    verify=self.verify,
                    cert=self.cert)
            except Exception as e:
                self.log.debug("keystone unknown issue", exc_info=True)
                raise OpenStackCloudException(
                    "Error authenticating to the keystone: %s " % str(e))
        return self._keystone_session

    @property
    def keystone_client(self):
        if self._keystone_client is None:
            try:
                self._keystone_client = keystone_client.Client(
                    session=self.keystone_session,
                    auth_url=self.get_session_endpoint('identity'),
                    timeout=self.api_timeout)
            except Exception as e:
                self.log.debug(
                    "Couldn't construct keystone object", exc_info=True)
                raise OpenStackCloudException(
                    "Error constructing keystone client: %s" % str(e))
        return self._keystone_client

    @property
    def service_catalog(self):
        return self.keystone_session.auth.get_access(
            self.keystone_session).service_catalog.get_data()

    @property
    def auth_token(self):
        if not self._auth_token:
            self._auth_token = self.keystone_session.get_token()
        return self._auth_token

    @property
    def project_cache(self):
        return self.get_project_cache()

    @_cache_on_arguments()
    def get_project_cache(self):
        return {project.id: project for project in
                self._project_manager.list()}

    @property
    def _project_manager(self):
        # Keystone v2 calls this attribute tenants
        # Keystone v3 calls it projects
        # Yay for usable APIs!
        return getattr(
            self.keystone_client, 'projects', self.keystone_client.tenants)

    def _get_project(self, name_or_id):
        """Retrieve a project by name or id."""

        # TODO(mordred): This, and other keystone operations, need to have
        #                domain information passed in. When there is no
        #                available domain information, we should default to
        #                the currently scoped domain which we can requset from
        #                the session.
        for id, project in self.project_cache.items():
            if name_or_id in (id, project.name):
                return project
        return None

    def get_project(self, name_or_id):
        """Retrieve a project by name or id."""
        project = self._get_project(name_or_id)
        if project:
            return meta.obj_to_dict(project)
        return None

    def update_project(self, name_or_id, description=None, enabled=True):
        try:
            project = self._get_project(name_or_id)
            return meta.obj_to_dict(
                project.update(description=description, enabled=enabled))
        except Exception as e:
            self.log.debug("keystone update project issue", exc_info=True)
            raise OpenStackCloudException(
                "Error in updating project {project}: {message}".format(
                    project=name_or_id, message=str(e)))

    def create_project(self, name, description=None, enabled=True):
        """Create a project."""
        try:
            self._project_manager.create(
                project_name=name, description=description, enabled=enabled)
        except Exception as e:
            self.log.debug("keystone create project issue", exc_info=True)
            raise OpenStackCloudException(
                "Error in creating project {project}: {message}".format(
                    project=name, message=str(e)))

    def delete_project(self, name_or_id):
        try:
            project = self._get_project(name_or_id)
            self._project_manager.delete(project.id)
        except Exception as e:
            self.log.debug("keystone delete project issue", exc_info=True)
            raise OpenStackCloudException(
                "Error in deleting project {project}: {message}".format(
                    project=name_or_id, message=str(e)))

    @property
    def user_cache(self):
        return self.get_user_cache()

    @_cache_on_arguments()
    def get_user_cache(self):
        user_list = self.manager.submitTask(_tasks.UserList())
        return {user.id: user for user in user_list}

    def _get_user(self, name_or_id):
        """Retrieve a user by name or id."""

        for id, user in self.user_cache.items():
            if name_or_id in (id, user.name):
                return user
        return None

    def get_user(self, name_or_id):
        """Retrieve a user by name or id."""
        user = self._get_user(name_or_id)
        if user:
            return meta.obj_to_dict(user)
        return None

    def update_user(self, name_or_id, email=None, enabled=None):
        self.get_user_cache.invalidate(self)
        user = self._get_user(name_or_id)
        user_args = {}
        if email is not None:
            user_args['email'] = email
        if enabled is not None:
            user_args['enabled'] = enabled
        if not user_args:
            self.log.debug("No user data to update")
            return None
        user_args['user'] = user

        try:
            user = self.manager.submitTask(_tasks.UserUpdate(**user_args))
        except Exception as e:
            self.log.debug("keystone update user issue", exc_info=True)
            raise OpenStackCloudException(
                "Error in updating user {user}: {message}".format(
                    user=name_or_id, message=str(e)))
        self.get_user_cache.invalidate(self)
        return meta.obj_to_dict(user)

    def create_user(
            self, name, password=None, email=None, project=None,
            enabled=True):
        """Create a user."""
        try:
            if project:
                project_id = self._get_project(project).id
            else:
                project_id = None
            user = self.manager.submitTask(_tasks.UserCreate(
                user_name=name, password=password, email=email,
                project=project_id, enabled=enabled))
        except Exception as e:
            self.log.debug("keystone create user issue", exc_info=True)
            raise OpenStackCloudException(
                "Error in creating user {user}: {message}".format(
                    user=name, message=str(e)))
        self.get_user_cache.invalidate(self)
        return meta.obj_to_dict(user)

    def delete_user(self, name_or_id):
        self.get_user_cache.invalidate(self)
        try:
            user = self._get_user(name_or_id)
            self.manager.submitTask(_tasks.UserDelete(user=user))
        except Exception as e:
            self.log.debug("keystone delete user issue", exc_info=True)
            raise OpenStackCloudException(
                "Error in deleting user {user}: {message}".format(
                    user=name_or_id, message=str(e)))
        self.get_user_cache.invalidate(self)

    def _get_glance_api_version(self):
        if 'image' in self.api_versions:
            return self.api_versions['image']
        # Yay. We get to guess ...
        # Get rid of trailing '/' if present
        endpoint = self.get_session_endpoint('image')
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        url_bits = endpoint.split('/')
        if url_bits[-1].startswith('v'):
            return url_bits[-1][1]
        return '1'  # Who knows? Let's just try 1 ...

    @property
    def glance_client(self):
        if self._glance_client is None:
            token = self.auth_token
            endpoint = self.get_session_endpoint('image')
            glance_api_version = self._get_glance_api_version()
            kwargs = dict()
            if self.api_timeout is not None:
                kwargs['timeout'] = self.api_timeout
            try:
                self._glance_client = glanceclient.Client(
                    glance_api_version, endpoint, token=token,
                    session=self.keystone_session,
                    **kwargs)
            except Exception as e:
                self.log.debug("glance unknown issue", exc_info=True)
                raise OpenStackCloudException(
                    "Error in connecting to glance: %s" % str(e))

            if not self._glance_client:
                raise OpenStackCloudException("Error connecting to glance")
        return self._glance_client

    @property
    def swift_client(self):
        if self._swift_client is None:
            token = self.auth_token
            endpoint = self.get_session_endpoint(
                service_key='object-store')
            self._swift_client = swift_client.Connection(
                preauthurl=endpoint,
                preauthtoken=token,
                os_options=dict(region_name=self.region_name),
            )
        return self._swift_client

    @property
    def cinder_client(self):

        if self._cinder_client is None:
            # trigger exception on lack of cinder
            self.get_session_endpoint('volume')
            # Make the connection
            self._cinder_client = cinder_client.Client(
                session=self.keystone_session,
                region_name=self.region_name,
                timeout=self.api_timeout)

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
            endpoint = self.get_session_endpoint(service_key='database')
            trove_api_version = self._get_trove_api_version(endpoint)
            # Make the connection - can't use keystone session until there
            # is one
            self._trove_client = trove_client.Client(
                trove_api_version,
                session=self.keystone_session,
                region_name=self.region_name,
                service_type=self.get_service_type('database'),
                timeout=self.api_timeout,
            )

            if self._trove_client is None:
                raise OpenStackCloudException(
                    "Failed to instantiate Trove client."
                    " This could mean that your credentials are wrong.")

        return self._trove_client

    @property
    def neutron_client(self):
        if self._neutron_client is None:
            # trigger exception on lack of neutron
            self.get_session_endpoint('network')
            self._neutron_client = neutron_client.Client(
                token=self.auth_token,
                session=self.keystone_session,
                region_name=self.region_name,
                timeout=self.api_timeout)
        return self._neutron_client

    def get_name(self):
        return self.name

    def get_region(self):
        return self.region_name

    def get_flavor_name(self, flavor_id):
        flavor = self.get_flavor(flavor_id)
        if flavor:
            return flavor['name']
        return None

    def get_flavor_by_ram(self, ram, include=None):
        """Get a flavor based on amount of RAM available.

        Finds the flavor with the least amount of RAM that is at least
        as much as the specified amount. If `include` is given, further
        filter based on matching flavor name.

        :param int ram: Minimum amount of RAM.
        :param string include: If given, will return a flavor whose name
            contains this string as a substring.
        """
        flavors = self.list_flavors()
        for flavor in sorted(flavors, key=operator.itemgetter('ram')):
            if (flavor['ram'] >= ram and
                    (not include or include in flavor['name'])):
                return flavor
        raise OpenStackCloudException(
            "Could not find a flavor with {ram} and '{include}'".format(
                ram=ram, include=include))

    def get_session_endpoint(self, service_key):
        if service_key in self.endpoints:
            return self.endpoints[service_key]
        try:
            # keystone is a special case in keystone, because what?
            if service_key == 'identity':
                endpoint = self.keystone_session.get_endpoint(
                    interface=ksc_auth.AUTH_INTERFACE)
            else:
                endpoint = self.keystone_session.get_endpoint(
                    service_type=self.get_service_type(service_key),
                    service_name=self.get_service_name(service_key),
                    interface=self.endpoint_type,
                    region_name=self.region_name)
        except Exception as e:
            self.log.debug("keystone cannot get endpoint", exc_info=True)
            raise OpenStackCloudException(
                "Error getting %s endpoint: %s" % (service_key, str(e)))
        if endpoint is None:
            raise OpenStackCloudUnavailableService(
                "Cloud {cloud} does not have a {service} service".format(
                    cloud=self.name, service=service_key))
        return endpoint

    def has_service(self, service_key):
        try:
            self.get_session_endpoint(service_key)
            return True
        except OpenStackCloudException:
            return False

    def list_servers(self):
        return self.manager.submitTask(_tasks.ServerList())

    def list_server_dicts(self):
        return [self.get_openstack_vars(server)
                for server in self.list_servers()]

    def list_keypairs(self):
        return self.manager.submitTask(_tasks.KeypairList())

    def list_keypair_dicts(self):
        return [meta.obj_to_dict(keypair)
                for keypair in self.list_keypairs()]

    def create_keypair(self, name, public_key):
        return self.manager.submitTask(_tasks.KeypairCreate(
            name=name, public_key=public_key))

    def delete_keypair(self, name):
        return self.manager.submitTask(_tasks.KeypairDelete(key=name))

    @property
    def extension_cache(self):
        if not self._extension_cache:
            self._extension_cache = set()

            try:
                resp, body = self.manager.submitTask(
                    _tasks.NovaUrlGet(url='/extensions'))
                if resp.status_code == 200:
                    for x in body['extensions']:
                        self._extension_cache.add(x['alias'])
            except nova_exceptions.NotFound:
                pass
        return self._extension_cache

    def has_extension(self, extension_name):
        return extension_name in self.extension_cache

    def _filter_list(self, data, name_or_id, filters):
        """Filter a list by name/ID and arbitrary meta data.

        :param list data:
            The list of dictionary data to filter. It is expected that
            each dictionary contains an 'id', 'name' (or 'display_name')
            key if a value for name_or_id is given.
        :param string name_or_id:
            The name or ID of the entity being filtered.
        :param dict filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }
        """
        if name_or_id:
            identifier_matches = []
            for e in data:
                e_id = str(e.get('id', None))
                e_name = e.get('name', None)
                # cinder likes to be different and use display_name
                e_display_name = e.get('display_name', None)
                if str(name_or_id) in (e_id, e_name, e_display_name):
                    identifier_matches.append(e)
            data = identifier_matches

        if not filters:
            return data

        def _dict_filter(f, d):
            if not d:
                return False
            for key in f.keys():
                if isinstance(f[key], dict):
                    if not _dict_filter(f[key], d.get(key, None)):
                        return False
                elif d.get(key, None) != f[key]:
                    return False
            return True

        filtered = []
        for e in data:
            filtered.append(e)
            for key in filters.keys():
                if isinstance(filters[key], dict):
                    if not _dict_filter(filters[key], e.get(key, None)):
                        filtered.pop()
                        break
                elif e.get(key, None) != filters[key]:
                    filtered.pop()
                    break
        return filtered

    def _get_entity(self, func, name_or_id, filters):
        """Return a single entity from the list returned by a given method.

        :param callable func:
            A function that takes `name_or_id` and `filters` as parameters
            and returns a list of entities to filter.
        :param string name_or_id:
            The name or ID of the entity being filtered.
        :param dict filters:
            A dictionary of meta data to use for further filtering.
        """
        entities = func(name_or_id, filters)
        if not entities:
            return None
        if len(entities) > 1:
            raise OpenStackCloudException(
                "Multiple matches found for %s" % name_or_id)
        return entities[0]

    def search_networks(self, name_or_id=None, filters=None):
        networks = self.list_networks()
        return self._filter_list(networks, name_or_id, filters)

    def search_routers(self, name_or_id=None, filters=None):
        routers = self.list_routers()
        return self._filter_list(routers, name_or_id, filters)

    def search_subnets(self, name_or_id=None, filters=None):
        subnets = self.list_subnets()
        return self._filter_list(subnets, name_or_id, filters)

    def search_volumes(self, name_or_id=None, filters=None):
        volumes = self.list_volumes()
        return self._filter_list(volumes, name_or_id, filters)

    def search_flavors(self, name_or_id=None, filters=None):
        flavors = self.list_flavors()
        return self._filter_list(flavors, name_or_id, filters)

    def search_security_groups(self, name_or_id=None, filters=None):
        groups = self.list_security_groups()
        return self._filter_list(groups, name_or_id, filters)

    def list_networks(self):
        return self.manager.submitTask(_tasks.NetworkList())['networks']

    def list_routers(self):
        return self.manager.submitTask(_tasks.RouterList())['routers']

    def list_subnets(self):
        return self.manager.submitTask(_tasks.SubnetList())['subnets']

    @_cache_on_arguments(should_cache_fn=_no_pending_volumes)
    def list_volumes(self, cache=True):
        if not cache:
            warnings.warn('cache argument to list_volumes is deprecated. Use '
                          'invalidate instead.')
        try:
            return meta.obj_list_to_dict(
                self.manager.submitTask(_tasks.VolumeList())
            )
        except Exception as e:
            self.log.debug(
                "cinder could not list volumes: {message}".format(
                    message=str(e)),
                exc_info=True)
            raise OpenStackCloudException("Error fetching volume list")

    @_cache_on_arguments()
    def list_flavors(self):
        return meta.obj_list_to_dict(
            self.manager.submitTask(_tasks.FlavorList())
        )

    def list_security_groups(self):
        return meta.obj_list_to_dict(
            self.manager.submitTask(_tasks.SecurityGroupList())
        )

    def get_network(self, name_or_id, filters=None):
        return self._get_entity(self.search_networks, name_or_id, filters)

    def get_router(self, name_or_id, filters=None):
        return self._get_entity(self.search_routers, name_or_id, filters)

    def get_subnet(self, name_or_id, filters=None):
        return self._get_entity(self.search_subnets, name_or_id, filters)

    def get_volume(self, name_or_id, filters=None):
        return self._get_entity(self.search_volumes, name_or_id, filters)

    def get_flavor(self, name_or_id, filters=None):
        return self._get_entity(self.search_flavors, name_or_id, filters)

    def get_security_group(self, name_or_id, filters=None):
        return self._get_entity(self.search_security_groups,
                                name_or_id, filters)

    # TODO(Shrews): This will eventually need to support tenant ID and
    # provider networks, which are admin-level params.
    def create_network(self, name, shared=False, admin_state_up=True):
        """Create a network.

        :param name: Name of the network being created.
        :param shared: Set the network as shared.
        :param admin_state_up: Set the network administrative state to up.

        :returns: The network object.
        :raises: OpenStackCloudException on operation error.
        """

        network = {
            'name': name,
            'shared': shared,
            'admin_state_up': admin_state_up
        }

        try:
            net = self.manager.submitTask(
                _tasks.NetworkCreate(body=dict({'network': network})))
        except Exception as e:
            self.log.debug("Network creation failed", exc_info=True)
            raise OpenStackCloudException(
                "Error in creating network %s: %s" % (name, str(e)))
        # Turns out neutron returns an actual dict, so no need for the
        # use of meta.obj_to_dict() here (which would not work against
        # a dict).
        return net['network']

    def delete_network(self, name_or_id):
        """Delete a network.

        :param name_or_id: Name or ID of the network being deleted.
        :raises: OpenStackCloudException on operation error.
        """
        network = self.get_network(name_or_id)
        if not network:
            raise OpenStackCloudException(
                "Network %s not found." % name_or_id)

        try:
            self.manager.submitTask(
                _tasks.NetworkDelete(network=network['id']))
        except Exception as e:
            self.log.debug("Network deletion failed", exc_info=True)
            raise OpenStackCloudException(
                "Error in deleting network %s: %s" % (name_or_id, str(e)))

    def create_router(self, name=None, admin_state_up=True):
        """Create a logical router.

        :param name: The router name.
        :param admin_state_up: The administrative state of the router.

        :returns: The router object.
        :raises: OpenStackCloudException on operation error.
        """
        router = {
            'admin_state_up': admin_state_up
        }
        if name:
            router['name'] = name

        try:
            new_router = self.manager.submitTask(
                _tasks.RouterCreate(body=dict(router=router)))
        except Exception as e:
            self.log.debug("Router create failed", exc_info=True)
            raise OpenStackCloudException(
                "Error creating router %s: %s" % (name, e))
        # Turns out neutron returns an actual dict, so no need for the
        # use of meta.obj_to_dict() here (which would not work against
        # a dict).
        return new_router['router']

    def update_router(self, name_or_id, name=None, admin_state_up=None,
                      ext_gateway_net_id=None):
        """Update an existing logical router.

        :param name_or_id: The name or UUID of the router to update.
        :param name: The new router name.
        :param admin_state_up: The administrative state of the router.
        :param ext_gateway_net_id: The network ID for the external gateway.

        :returns: The router object.
        :raises: OpenStackCloudException on operation error.
        """
        router = {}
        if name:
            router['name'] = name
        if admin_state_up:
            router['admin_state_up'] = admin_state_up
        if ext_gateway_net_id:
            router['external_gateway_info'] = {
                'network_id': ext_gateway_net_id
            }

        if not router:
            self.log.debug("No router data to update")
            return

        curr_router = self.get_router(name_or_id)
        if not curr_router:
            raise OpenStackCloudException(
                "Router %s not found." % name_or_id)

        try:
            new_router = self.manager.submitTask(
                _tasks.RouterUpdate(
                    router=curr_router['id'], body=dict(router=router)))
        except Exception as e:
            self.log.debug("Router update failed", exc_info=True)
            raise OpenStackCloudException(
                "Error updating router %s: %s" % (name_or_id, e))
        # Turns out neutron returns an actual dict, so no need for the
        # use of meta.obj_to_dict() here (which would not work against
        # a dict).
        return new_router['router']

    def delete_router(self, name_or_id):
        """Delete a logical router.

        If a name, instead of a unique UUID, is supplied, it is possible
        that we could find more than one matching router since names are
        not required to be unique. An error will be raised in this case.

        :param name_or_id: Name or ID of the router being deleted.
        :raises: OpenStackCloudException on operation error.
        """
        router = self.get_router(name_or_id)
        if not router:
            raise OpenStackCloudException(
                "Router %s not found." % name_or_id)

        try:
            self.manager.submitTask(
                _tasks.RouterDelete(router=router['id']))
        except Exception as e:
            self.log.debug("Router delete failed", exc_info=True)
            raise OpenStackCloudException(
                "Error deleting router %s: %s" % (name_or_id, e))

    def _get_images_from_cloud(self, filter_deleted):
        # First, try to actually get images from glance, it's more efficient
        images = dict()
        try:
            # If the cloud does not expose the glance API publically
            image_list = self.manager.submitTask(_tasks.GlanceImageList())
        except (OpenStackCloudException,
                glanceclient.exc.HTTPInternalServerError):
            # We didn't have glance, let's try nova
            # If this doesn't work - we just let the exception propagate
            image_list = self.manager.submitTask(_tasks.NovaImageList())
        for image in image_list:
            # The cloud might return DELETED for invalid images.
            # While that's cute and all, that's an implementation detail.
            if not filter_deleted:
                images[image.id] = image
            elif image.status != 'DELETED':
                images[image.id] = image
        return images

    def _reset_image_cache(self):
        self._image_cache = None

    @_cache_on_arguments(should_cache_fn=_no_pending_images)
    def list_images(self, filter_deleted=True):
        """Get available glance images.

        :param filter_deleted: Control whether deleted images are returned.
        :returns: A dictionary of glance images indexed by image UUID.
        """
        return self._get_images_from_cloud(filter_deleted)

    def get_image_name(self, image_id, exclude=None):
        image = self.get_image(image_id, exclude)
        if image:
            return image.name
        return None

    def get_image_id(self, image_name, exclude=None):
        image = self.get_image(image_name, exclude)
        if image:
            return image.id
        return None

    def get_image(self, name_or_id, exclude=None):
        for (image_id, image) in self.list_images().items():
            if image_id == name_or_id:
                return image
            if (image is not None and
                    name_or_id == image.name and (
                    not exclude or exclude not in image.name)):
                return image
        return None

    def get_image_dict(self, name_or_id, exclude=None):
        image = self.get_image(name_or_id, exclude)
        if not image:
            return image
        if getattr(image, 'validate', None):
            # glanceclient returns a "warlock" object if you use v2
            return meta.warlock_to_dict(image)
        else:
            # glanceclient returns a normal object if you use v1
            return meta.obj_to_dict(image)

    def create_image_snapshot(self, name, **metadata):
        image = self.manager.submitTask(_tasks.ImageSnapshotCreate(
            name=name, **metadata))
        if image:
            return meta.obj_to_dict(image)
        return None

    def delete_image(self, name_or_id, wait=False, timeout=3600):
        image = self.get_image(name_or_id)
        try:
            # Note that in v1, the param name is image, but in v2,
            # it's image_id
            glance_api_version = self._get_glance_api_version()
            if glance_api_version == '2':
                self.manager.submitTask(
                    _tasks.ImageDelete(image_id=image.id))
            elif glance_api_version == '1':
                self.manager.submitTask(
                    _tasks.ImageDelete(image=image.id))
        except Exception as e:
            self.log.debug("Image deletion failed", exc_info=True)
            raise OpenStackCloudException(
                "Error in deleting image: %s" % str(e))

        if wait:
            for count in _iterate_timeout(
                    timeout,
                    "Timeout waiting for the image to be deleted."):
                self._cache.invalidate()
                if self.get_image(image.id) is None:
                    return

    def create_image(
            self, name, filename, container='images',
            md5=None, sha256=None,
            disk_format=None, container_format=None,
            wait=False, timeout=3600, **kwargs):
        if not md5 or not sha256:
            (md5, sha256) = self._get_file_hashes(filename)
        current_image = self.get_image_dict(name)
        if (current_image and current_image.get(IMAGE_MD5_KEY, '') == md5
                and current_image.get(IMAGE_SHA256_KEY, '') == sha256):
            self.log.debug(
                "image {name} exists and is up to date".format(name=name))
            return current_image
        kwargs[IMAGE_MD5_KEY] = md5
        kwargs[IMAGE_SHA256_KEY] = sha256
        # This makes me want to die inside
        if self.image_api_use_tasks:
            return self._upload_image_task(
                name, filename, container,
                current_image=current_image,
                wait=wait, timeout=timeout, **kwargs)
        else:
            image_kwargs = dict(properties=kwargs)
            if disk_format:
                image_kwargs['disk_format'] = disk_format
            if container_format:
                image_kwargs['container_format'] = container_format

            return self._upload_image_put(name, filename, **image_kwargs)

    def _upload_image_put(self, name, filename, **image_kwargs):
        image = self.manager.submitTask(_tasks.ImageCreate(
            name=name, **image_kwargs))
        self.manager.submitTask(_tasks.ImageUpdate(
            image=image, data=open(filename, 'rb')))
        self._cache.invalidate()
        return self.get_image_dict(image.id)

    def _upload_image_task(
            self, name, filename, container, current_image=None,
            wait=True, timeout=None, **image_properties):
        self.create_object(
            container, name, filename,
            md5=image_properties.get('md5', None),
            sha256=image_properties.get('sha256', None))
        if not current_image:
            current_image = self.get_image(name)
        # TODO(mordred): Can we do something similar to what nodepool does
        # using glance properties to not delete then upload but instead make a
        # new "good" image and then mark the old one as "bad"
        # self.glance_client.images.delete(current_image)
        glance_task = self.manager.submitTask(_tasks.ImageTaskCreate(
            type='import', input=dict(
                import_from='{container}/{name}'.format(
                    container=container, name=name),
                image_properties=dict(name=name))))
        if wait:
            image_id = None
            for count in _iterate_timeout(
                    timeout,
                    "Timeout waiting for the image to import."):
                try:
                    if image_id is None:
                        status = self.manager.submitTask(
                            _tasks.ImageTaskGet(task_id=glance_task.id))
                except glanceclient.exc.HTTPServiceUnavailable:
                    # Intermittent failure - catch and try again
                    continue

                if status.status == 'success':
                    image_id = status.result['image_id']
                    self._reset_image_cache()
                    self.list_images.invalidate(self)
                    try:
                        image = self.get_image(image_id)
                    except glanceclient.exc.HTTPServiceUnavailable:
                        # Intermittent failure - catch and try again
                        continue
                    if image is None:
                        continue
                    self.update_image_properties(
                        image=image,
                        **image_properties)
                    self.list_images.invalidate(self)
                    return self.get_image_dict(status.result['image_id'])
                if status.status == 'failure':
                    raise OpenStackCloudException(
                        "Image creation failed: {message}".format(
                            message=status.message),
                        extra_data=status)
        else:
            return meta.warlock_to_dict(glance_task)

    def update_image_properties(
            self, image=None, name_or_id=None, **properties):
        if image is None:
            image = self.get_image(name_or_id)

        img_props = {}
        for k, v in iter(properties.items()):
            if v and k in ['ramdisk', 'kernel']:
                v = self.get_image_id(v)
                k = '{0}_id'.format(k)
            img_props[k] = v

        # This makes me want to die inside
        if self._get_glance_api_version() == '2':
            return self._update_image_properties_v2(image, img_props)
        else:
            return self._update_image_properties_v1(image, img_props)

    def _update_image_properties_v2(self, image, properties):
        img_props = {}
        for k, v in iter(properties.items()):
            if image.get(k, None) != v:
                img_props[k] = str(v)
        if not img_props:
            return False
        self.manager.submitTask(_tasks.ImageUpdate(
            image_id=image.id, **img_props))
        return True

    def _update_image_properties_v1(self, image, properties):
        img_props = {}
        for k, v in iter(properties.items()):
            if image.properties.get(k, None) != v:
                img_props[k] = v
        if not img_props:
            return False
        self.manager.submitTask(_tasks.ImageUpdate(
            image=image, properties=img_props))
        return True

    def create_volume(self, wait=True, timeout=None, **kwargs):
        """Create a volume.

        :param wait: If true, waits for volume to be created.
        :param timeout: Seconds to wait for volume creation. None is forever.
        :param volkwargs: Keyword arguments as expected for cinder client.

        :returns: The created volume object.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        try:
            volume = self.manager.submitTask(_tasks.VolumeCreate(**kwargs))
        except Exception as e:
            self.log.debug("Volume creation failed", exc_info=True)
            raise OpenStackCloudException(
                "Error in creating volume: %s" % str(e))
        self.list_volumes.invalidate(self)

        volume = meta.obj_to_dict(volume)

        if volume['status'] == 'error':
            raise OpenStackCloudException("Error in creating volume")

        if wait:
            vol_id = volume['id']
            for count in _iterate_timeout(
                    timeout,
                    "Timeout waiting for the volume to be available."):
                volume = self.get_volume(vol_id)

                if not volume:
                    continue

                if volume['status'] == 'available':
                    return volume

                if volume['status'] == 'error':
                    raise OpenStackCloudException(
                        "Error in creating volume, please check logs")

    def delete_volume(self, name_or_id=None, wait=True, timeout=None):
        """Delete a volume.

        :param name_or_id: Name or unique ID of the volume.
        :param wait: If true, waits for volume to be deleted.
        :param timeout: Seconds to wait for volume deletion. None is forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        self.list_volumes.invalidate(self)
        volume = self.get_volume(name_or_id)

        try:
            self.manager.submitTask(
                _tasks.VolumeDelete(volume=volume['id']))
        except Exception as e:
            self.log.debug("Volume deletion failed", exc_info=True)
            raise OpenStackCloudException(
                "Error in deleting volume: %s" % str(e))

        self.list_volumes.invalidate(self)
        if wait:
            for count in _iterate_timeout(
                    timeout,
                    "Timeout waiting for the volume to be deleted."):
                if not self.volume_exists(volume['id']):
                    return

    def get_volumes(self, server, cache=True):
        volumes = []
        for volume in self.list_volumes(cache=cache):
            for attach in volume['attachments']:
                if attach['server_id'] == server.id:
                    volumes.append(volume)
        return volumes

    def get_volume_id(self, name_or_id):
        volume = self.get_volume(name_or_id)
        if volume:
            return volume['id']
        return None

    def volume_exists(self, name_or_id):
        return self.get_volume(name_or_id) is not None

    def get_volume_attach_device(self, volume, server_id):
        """Return the device name a volume is attached to for a server.

        This can also be used to verify if a volume is attached to
        a particular server.

        :param volume: Volume object
        :param server_id: ID of server to check

        :returns: Device name if attached, None if volume is not attached.
        """
        for attach in volume['attachments']:
            if server_id == attach['server_id']:
                return attach['device']
        return None

    def detach_volume(self, server, volume, wait=True, timeout=None):
        """Detach a volume from a server.

        :param server: The server object to detach from.
        :param volume: The volume object to detach.
        :param wait: If true, waits for volume to be detached.
        :param timeout: Seconds to wait for volume detachment. None is forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        dev = self.get_volume_attach_device(volume, server.id)
        if not dev:
            raise OpenStackCloudException(
                "Volume %s is not attached to server %s"
                % (volume['id'], server.id)
            )

        try:
            self.manager.submitTask(
                _tasks.VolumeDetach(attachment_id=volume['id'],
                                    server_id=server.id))
        except Exception as e:
            self.log.debug("nova volume detach failed", exc_info=True)
            raise OpenStackCloudException(
                "Error detaching volume %s from server %s: %s" %
                (volume['id'], server.id, e)
            )

        if wait:
            for count in _iterate_timeout(
                    timeout,
                    "Timeout waiting for volume %s to detach." % volume['id']):
                try:
                    vol = self.get_volume(volume['id'])
                except Exception:
                    self.log.debug(
                        "Error getting volume info %s" % volume['id'],
                        exc_info=True)
                    continue

                if vol['status'] == 'available':
                    return

                if vol['status'] == 'error':
                    raise OpenStackCloudException(
                        "Error in detaching volume %s" % volume['id']
                    )

    def attach_volume(self, server, volume, device=None,
                      wait=True, timeout=None):
        """Attach a volume to a server.

        This will attach a volume, described by the passed in volume
        object (as returned by get_volume()), to the server described by
        the passed in server object (as returned by get_server()) on the
        named device on the server.

        If the volume is already attached to the server, or generally not
        available, then an exception is raised. To re-attach to a server,
        but under a different device, the user must detach it first.

        :param server: The server object to attach to.
        :param volume: The volume object to attach.
        :param device: The device name where the volume will attach.
        :param wait: If true, waits for volume to be attached.
        :param timeout: Seconds to wait for volume attachment. None is forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        dev = self.get_volume_attach_device(volume, server.id)
        if dev:
            raise OpenStackCloudException(
                "Volume %s already attached to server %s on device %s"
                % (volume['id'], server.id, dev)
            )

        if volume['status'] != 'available':
            raise OpenStackCloudException(
                "Volume %s is not available. Status is '%s'"
                % (volume['id'], volume['status'])
            )

        try:
            self.manager.submitTask(
                _tasks.VolumeAttach(volume_id=volume['id'],
                                    server_id=server.id,
                                    device=device))
        except Exception as e:
            self.log.debug(
                "nova volume attach of %s failed" % volume['id'],
                exc_info=True)
            raise OpenStackCloudException(
                "Error attaching volume %s to server %s: %s" %
                (volume['id'], server.id, e)
            )

        if wait:
            for count in _iterate_timeout(
                    timeout,
                    "Timeout waiting for volume %s to attach." % volume['id']):
                try:
                    vol = self.get_volume(volume['id'])
                except Exception:
                    self.log.debug(
                        "Error getting volume info %s" % volume['id'],
                        exc_info=True)
                    continue

                if self.get_volume_attach_device(vol, server.id):
                    return

                # TODO(Shrews) check to see if a volume can be in error status
                #              and also attached. If so, we should move this
                #              above the get_volume_attach_device call
                if vol['status'] == 'error':
                    raise OpenStackCloudException(
                        "Error in attaching volume %s" % volume['id']
                    )

    def get_server_id(self, name_or_id):
        server = self.get_server(name_or_id)
        if server:
            return server.id
        return None

    def get_server_private_ip(self, server):
        return meta.get_server_private_ip(server)

    def get_server_public_ip(self, server):
        return meta.get_server_public_ip(server)

    def get_server(self, name_or_id):
        for server in self.list_servers():
            if name_or_id in (server.name, server.id):
                return server
        return None

    def get_server_dict(self, name_or_id):
        server = self.get_server(name_or_id)
        if not server:
            return server
        return self.get_openstack_vars(server)

    def get_server_meta(self, server):
        server_vars = meta.get_hostvars_from_server(self, server)
        groups = meta.get_groups_from_server(self, server, server_vars)
        return dict(server_vars=server_vars, groups=groups)

    def get_openstack_vars(self, server):
        return meta.get_hostvars_from_server(self, server)

    def add_ip_from_pool(self, server, pools):

        # empty dict and list
        usable_floating_ips = {}

        # get the list of all floating IPs. Mileage may
        # vary according to Nova Compute configuration
        # per cloud provider
        all_floating_ips = self.manager.submitTask(_tasks.FloatingIPList())

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
                    new_ip = self.manager.submitTask(
                        _tasks.FloatingIPCreate(pool=pool))
                except Exception:
                    self.log.debug(
                        "nova floating ip create failed", exc_info=True)
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
                self.manager.submitTask(
                    _tasks.FloatingIPAttach(server=server, address=ip))
            except Exception as e:
                self.log.debug(
                    "nova floating ip add failed", exc_info=True)
                raise OpenStackCloudException(
                    "Error attaching IP {ip} to instance {id}: {msg} ".format(
                        ip=ip, id=server.id, msg=str(e)))

    def add_auto_ip(self, server):
        try:
            new_ip = self.manager.submitTask(_tasks.FloatingIPCreate())
        except Exception as e:
            self.log.debug(
                "nova floating ip create failed", exc_info=True)
            raise OpenStackCloudException(
                "Unable to create floating ip: %s" % (str(e)))
        try:
            self.add_ip_list(server, [new_ip])
        except OpenStackCloudException:
            # Clean up - we auto-created this ip, and it's not attached
            # to the server, so the cloud will not know what to do with it
            self.manager.submitTask(
                _tasks.FloatingIPDelete(floating_ip=new_ip))
            raise

    def add_ips_to_server(self, server, auto_ip=True, ips=None, ip_pool=None):
        if ip_pool:
            self.add_ip_from_pool(server, ip_pool)
        elif ips:
            self.add_ip_list(server, ips)
        elif auto_ip:
            if self.get_server_public_ip(server):
                return server
            self.add_auto_ip(server)
        else:
            return server

        # this may look redundant, but if there is now a
        # floating IP, then it needs to be obtained from
        # a recent server object if the above code path exec'd
        try:
            server = self.manager.submitTask(_tasks.ServerGet(server=server))
        except Exception as e:
            self.log.debug("nova info failed", exc_info=True)
            raise OpenStackCloudException(
                "Error in getting info from instance: %s " % str(e))
        return server

    def create_server(self, auto_ip=True, ips=None, ip_pool=None,
                      root_volume=None, terminate_volume=False,
                      wait=False, timeout=180, **bootkwargs):

        if root_volume:
            if terminate_volume:
                suffix = ':::1'
            else:
                suffix = ':::0'
            volume_id = self.get_volume_id(root_volume) + suffix
            if 'block_device_mapping' not in bootkwargs:
                bootkwargs['block_device_mapping'] = dict()
            bootkwargs['block_device_mapping']['vda'] = volume_id

        try:
            server = self.manager.submitTask(_tasks.ServerCreate(**bootkwargs))
            server = self.manager.submitTask(_tasks.ServerGet(server=server))
        except Exception as e:
            self.log.debug("nova instance create failed", exc_info=True)
            raise OpenStackCloudException(
                "Error in creating instance: {0}".format(e))
        if server.status == 'ERROR':
            raise OpenStackCloudException(
                "Error in creating the server.")
        if wait:
            for count in _iterate_timeout(
                    timeout,
                    "Timeout waiting for the server to come up."):
                try:
                    server = self.manager.submitTask(
                        _tasks.ServerGet(server=server))
                except Exception:
                    continue

                if server.status == 'ACTIVE':
                    return self.add_ips_to_server(
                        server, auto_ip, ips, ip_pool)

                if server.status == 'ERROR':
                    raise OpenStackCloudException(
                        "Error in creating the server",
                        extra_data=dict(
                            server=meta.obj_to_dict(server)))
        return server

    def rebuild_server(self, server_id, image_id, wait=False, timeout=180):
        try:
            server = self.manager.submitTask(_tasks.ServerRebuild(
                server=server_id, image=image_id))
        except Exception as e:
            self.log.debug("nova instance rebuild failed", exc_info=True)
            raise OpenStackCloudException(
                "Error in rebuilding instance: {0}".format(e))
        if wait:
            for count in _iterate_timeout(
                    timeout,
                    "Timeout waiting for server {0} to "
                    "rebuild.".format(server_id)):
                try:
                    server = self.manager.submitTask(
                        _tasks.ServerGet(server=server))
                except Exception:
                    continue

                if server.status == 'ACTIVE':
                    break

                if server.status == 'ERROR':
                    raise OpenStackCloudException(
                        "Error in rebuilding the server",
                        extra_data=dict(
                            server=meta.obj_to_dict(server)))
        return server

    def delete_server(self, name, wait=False, timeout=180):
        # TODO(mordred): Why is this not using self.get_server()?
        server_list = self.manager.submitTask(_tasks.ServerList(
            detailed=True, search_opts={'name': name}))
        # TODO(mordred): Why, after searching for a name, are we filtering
        # again?
        if server_list:
            server = [x for x in server_list if x.name == name]
            self.manager.submitTask(_tasks.ServerDelete(server=server.pop()))
        if not wait:
            return
        for count in _iterate_timeout(
                timeout,
                "Timed out waiting for server to get deleted."):
            server = self.manager.submitTask(_tasks.ServerGet(server=server))
            if not server:
                return

    def get_container(self, name, skip_cache=False):
        if skip_cache or name not in self._container_cache:
            try:
                container = self.manager.submitTask(
                    _tasks.ContainerGet(container=name))
                self._container_cache[name] = container
            except swift_exceptions.ClientException as e:
                if e.http_status == 404:
                    return None
                self.log.debug("swift container fetch failed", exc_info=True)
                raise OpenStackCloudException(
                    "Container fetch failed: %s (%s/%s)" % (
                        e.http_reason, e.http_host, e.http_path))
        return self._container_cache[name]

    def create_container(self, name, public=False):
        container = self.get_container(name)
        if container:
            return container
        try:
            self.manager.submitTask(
                _tasks.ContainerCreate(container=name))
            if public:
                self.set_container_access(name, 'public')
            return self.get_container(name, skip_cache=True)
        except swift_exceptions.ClientException as e:
            self.log.debug("swift container create failed", exc_info=True)
            raise OpenStackCloudException(
                "Container creation failed: %s (%s/%s)" % (
                    e.http_reason, e.http_host, e.http_path))

    def delete_container(self, name):
        try:
            self.manager.submitTask(
                _tasks.ContainerDelete(container=name))
        except swift_exceptions.ClientException as e:
            if e.http_status == 404:
                return
            self.log.debug("swift container delete failed", exc_info=True)
            raise OpenStackCloudException(
                "Container deletion failed: %s (%s/%s)" % (
                    e.http_reason, e.http_host, e.http_path))

    def update_container(self, name, headers):
        try:
            self.manager.submitTask(
                _tasks.ContainerUpdate(container=name, headers=headers))
        except swift_exceptions.ClientException as e:
            self.log.debug("swift container update failed", exc_info=True)
            raise OpenStackCloudException(
                "Container update failed: %s (%s/%s)" % (
                    e.http_reason, e.http_host, e.http_path))

    def set_container_access(self, name, access):
        if access not in OBJECT_CONTAINER_ACLS:
            raise OpenStackCloudException(
                "Invalid container access specified: %s.  Must be one of %s"
                % (access, list(OBJECT_CONTAINER_ACLS.keys())))
        header = {'x-container-read': OBJECT_CONTAINER_ACLS[access]}
        self.update_container(name, header)

    def get_container_access(self, name):
        container = self.get_container(name, skip_cache=True)
        if not container:
            raise OpenStackCloudException("Container not found: %s" % name)
        acl = container.get('x-container-read', '')
        try:
            return [p for p, a in OBJECT_CONTAINER_ACLS.items()
                    if acl == a].pop()
        except IndexError:
            raise OpenStackCloudException(
                "Could not determine container access for ACL: %s." % acl)

    def _get_file_hashes(self, filename):
        if filename not in self._file_hash_cache:
            md5 = hashlib.md5()
            sha256 = hashlib.sha256()
            with open(filename, 'rb') as file_obj:
                for chunk in iter(lambda: file_obj.read(8192), b''):
                    md5.update(chunk)
                    sha256.update(chunk)
            self._file_hash_cache[filename] = dict(
                md5=md5.hexdigest(), sha256=sha256.hexdigest())
        return (self._file_hash_cache[filename]['md5'],
                self._file_hash_cache[filename]['sha256'])

    def is_object_stale(
        self, container, name, filename, file_md5=None, file_sha256=None):

        metadata = self.get_object_metadata(container, name)
        if not metadata:
            self.log.debug(
                "swift stale check, no object: {container}/{name}".format(
                    container=container, name=name))
            return True

        if file_md5 is None or file_sha256 is None:
            (file_md5, file_sha256) = self._get_file_hashes(filename)

        if metadata.get(OBJECT_MD5_KEY, '') != file_md5:
            self.log.debug(
                "swift md5 mismatch: {filename}!={container}/{name}".format(
                    filename=filename, container=container, name=name))
            return True
        if metadata.get(OBJECT_SHA256_KEY, '') != file_sha256:
            self.log.debug(
                "swift sha256 mismatch: {filename}!={container}/{name}".format(
                    filename=filename, container=container, name=name))
            return True

        self.log.debug(
            "swift object up to date: {container}/{name}".format(
            container=container, name=name))
        return False

    def create_object(
            self, container, name, filename=None,
            md5=None, sha256=None, **headers):
        if not filename:
            filename = name

        # On some clouds this is not necessary. On others it is. I'm confused.
        self.create_container(container)

        if self.is_object_stale(container, name, filename, md5, sha256):
            with open(filename, 'r') as fileobj:
                self.log.debug(
                    "swift uploading {filename} to {container}/{name}".format(
                        filename=filename, container=container, name=name))
                self.manager.submitTask(_tasks.ObjectCreate(
                    container=container, obj=name, contents=fileobj))

        (md5, sha256) = self._get_file_hashes(filename)
        headers[OBJECT_MD5_KEY] = md5
        headers[OBJECT_SHA256_KEY] = sha256
        self.manager.submitTask(_tasks.ObjectUpdate(
            container=container, obj=name, headers=headers))

    def delete_object(self, container, name):
        if not self.get_object_metadata(container, name):
            return
        try:
            self.manager.submitTask(_tasks.ObjectDelete(
                container=container, obj=name))
        except swift_exceptions.ClientException as e:
            raise OpenStackCloudException(
                "Object deletion failed: %s (%s/%s)" % (
                    e.http_reason, e.http_host, e.http_path))

    def get_object_metadata(self, container, name):
        try:
            return self.manager.submitTask(_tasks.ObjectMetadata(
                container=container, obj=name))
        except swift_exceptions.ClientException as e:
            if e.http_status == 404:
                return None
            self.log.debug("swift metadata fetch failed", exc_info=True)
            raise OpenStackCloudException(
                "Object metadata fetch failed: %s (%s/%s)" % (
                    e.http_reason, e.http_host, e.http_path))

    def create_subnet(self, network_name_or_id, cidr, ip_version=4,
                      enable_dhcp=False, subnet_name=None, tenant_id=None,
                      allocation_pools=None, gateway_ip=None,
                      dns_nameservers=None, host_routes=None,
                      ipv6_ra_mode=None, ipv6_address_mode=None):
        """Create a subnet on a specified network.

        :param string network_name_or_id:
           The unique name or ID of the attached network. If a non-unique
           name is supplied, an exception is raised.
        :param string cidr:
           The CIDR.
        :param int ip_version:
           The IP version, which is 4 or 6.
        :param bool enable_dhcp:
           Set to ``True`` if DHCP is enabled and ``False`` if disabled.
           Default is ``False``.
        :param string subnet_name:
           The name of the subnet.
        :param string tenant_id:
           The ID of the tenant who owns the network. Only administrative users
           can specify a tenant ID other than their own.
        :param list allocation_pools:
           A list of dictionaries of the start and end addresses for the
           allocation pools. For example::

             [
               {
                 "start": "192.168.199.2",
                 "end": "192.168.199.254"
               }
             ]

        :param string gateway_ip:
           The gateway IP address. When you specify both allocation_pools and
           gateway_ip, you must ensure that the gateway IP does not overlap
           with the specified allocation pools.
        :param list dns_nameservers:
           A list of DNS name servers for the subnet. For example::

             [ "8.8.8.7", "8.8.8.8" ]

        :param list host_routes:
           A list of host route dictionaries for the subnet. For example::

             [
               {
                 "destination": "0.0.0.0/0",
                 "nexthop": "123.456.78.9"
               },
               {
                 "destination": "192.168.0.0/24",
                 "nexthop": "192.168.0.1"
               }
             ]

        :param string ipv6_ra_mode:
           IPv6 Router Advertisement mode. Valid values are: 'dhcpv6-stateful',
           'dhcpv6-stateless', or 'slaac'.
        :param string ipv6_address_mode:
           IPv6 address mode. Valid values are: 'dhcpv6-stateful',
           'dhcpv6-stateless', or 'slaac'.

        :returns: The new subnet object.
        :raises: OpenStackCloudException on operation error.
        """

        network = self.get_network(network_name_or_id)
        if not network:
            raise OpenStackCloudException(
                "Network %s not found." % network_name_or_id)

        # The body of the neutron message for the subnet we wish to create.
        # This includes attributes that are required or have defaults.
        subnet = {
            'network_id': network['id'],
            'cidr': cidr,
            'ip_version': ip_version,
            'enable_dhcp': enable_dhcp
        }

        # Add optional attributes to the message.
        if subnet_name:
            subnet['name'] = subnet_name
        if tenant_id:
            subnet['tenant_id'] = tenant_id
        if allocation_pools:
            subnet['allocation_pools'] = allocation_pools
        if gateway_ip:
            subnet['gateway_ip'] = gateway_ip
        if dns_nameservers:
            subnet['dns_nameservers'] = dns_nameservers
        if host_routes:
            subnet['host_routes'] = host_routes
        if ipv6_ra_mode:
            subnet['ipv6_ra_mode'] = ipv6_ra_mode
        if ipv6_address_mode:
            subnet['ipv6_address_mode'] = ipv6_address_mode

        try:
            new_subnet = self.manager.submitTask(
                _tasks.SubnetCreate(body=dict(subnet=subnet)))
        except Exception as e:
            self.log.debug("Subnet creation failed", exc_info=True)
            raise OpenStackCloudException(
                "Error in creating subnet on network %s: %s"
                % (network_name_or_id, e))

        return new_subnet['subnet']

    def delete_subnet(self, name_or_id):
        """Delete a subnet.

        If a name, instead of a unique UUID, is supplied, it is possible
        that we could find more than one matching subnet since names are
        not required to be unique. An error will be raised in this case.

        :param name_or_id: Name or ID of the subnet being deleted.
        :raises: OpenStackCloudException on operation error.
        """
        subnet = self.get_subnet(name_or_id)
        if not subnet:
            raise OpenStackCloudException(
                "Subnet %s not found." % name_or_id)

        try:
            self.manager.submitTask(
                _tasks.SubnetDelete(subnet=subnet['id']))
        except Exception as e:
            self.log.debug("Subnet delete failed", exc_info=True)
            raise OpenStackCloudException(
                "Error deleting subnet %s: %s" % (name_or_id, e))

    def update_subnet(self, name_or_id, subnet_name=None, enable_dhcp=None,
                      gateway_ip=None, allocation_pools=None,
                      dns_nameservers=None, host_routes=None):
        """Update an existing subnet.

        :param string name_or_id:
           Name or ID of the subnet to update.
        :param string subnet_name:
           The new name of the subnet.
        :param bool enable_dhcp:
           Set to ``True`` if DHCP is enabled and ``False`` if disabled.
        :param string gateway_ip:
           The gateway IP address. When you specify both allocation_pools and
           gateway_ip, you must ensure that the gateway IP does not overlap
           with the specified allocation pools.
        :param list allocation_pools:
           A list of dictionaries of the start and end addresses for the
           allocation pools. For example::

             [
               {
                 "start": "192.168.199.2",
                 "end": "192.168.199.254"
               }
             ]

        :param list dns_nameservers:
           A list of DNS name servers for the subnet. For example::

             [ "8.8.8.7", "8.8.8.8" ]

        :param list host_routes:
           A list of host route dictionaries for the subnet. For example::

             [
               {
                 "destination": "0.0.0.0/0",
                 "nexthop": "123.456.78.9"
               },
               {
                 "destination": "192.168.0.0/24",
                 "nexthop": "192.168.0.1"
               }
             ]

        :returns: The updated subnet object.
        :raises: OpenStackCloudException on operation error.
        """
        subnet = {}
        if subnet_name:
            subnet['name'] = subnet_name
        if enable_dhcp is not None:
            subnet['enable_dhcp'] = enable_dhcp
        if gateway_ip:
            subnet['gateway_ip'] = gateway_ip
        if allocation_pools:
            subnet['allocation_pools'] = allocation_pools
        if dns_nameservers:
            subnet['dns_nameservers'] = dns_nameservers
        if host_routes:
            subnet['host_routes'] = host_routes

        if not subnet:
            self.log.debug("No subnet data to update")
            return

        curr_subnet = self.get_subnet(name_or_id)
        if not curr_subnet:
            raise OpenStackCloudException(
                "Subnet %s not found." % name_or_id)

        try:
            new_subnet = self.manager.submitTask(
                _tasks.SubnetUpdate(
                    subnet=curr_subnet['id'], body=dict(subnet=subnet)))
        except Exception as e:
            self.log.debug("Subnet update failed", exc_info=True)
            raise OpenStackCloudException(
                "Error updating subnet %s: %s" % (name_or_id, e))
        # Turns out neutron returns an actual dict, so no need for the
        # use of meta.obj_to_dict() here (which would not work against
        # a dict).
        return new_subnet['subnet']


class OperatorCloud(OpenStackCloud):
    """Represent a privileged/operator connection to an OpenStack Cloud.

    `OperatorCloud` is the entry point for all admin operations, regardless
    of which OpenStack service those operations are for.

    See the :class:`OpenStackCloud` class for a description of most options.
    `OperatorCloud` overrides the default value of `endpoint_type` from
    `public` to `admin`.

    :param string endpoint_type: The type of endpoint to get for services
                                 from the service catalog. Valid types are
                                 `public` ,`internal` or `admin`. (optional,
                                 defaults to `admin`)
    """

    def __init__(self, *args, **kwargs):
        super(OperatorCloud, self).__init__(*args, **kwargs)
        if 'endpoint_type' not in kwargs:
            self.endpoint_type = 'admin'

    @property
    def auth_token(self):
        if self.auth_type in (None, "None", ''):
            return self._auth_token
        if not self._auth_token:
            self._auth_token = self.keystone_session.get_token()
        return self._auth_token

    @property
    def ironic_client(self):
        if self._ironic_client is None:
            ironic_logging = logging.getLogger('ironicclient')
            ironic_logging.addHandler(logging.NullHandler())
            token = self.auth_token
            if self.auth_type in (None, "None", ''):
                # TODO: This needs to be improved logic wise, perhaps a list,
                # or enhancement of the data stuctures with-in the library
                # to allow for things aside password authentication, or no
                # authentication if so desired by the user.
                #
                # Attempt to utilize a pre-stored endpoint in the auth
                # dict as the endpoint.
                endpoint = self.auth['endpoint']
            else:
                endpoint = self.get_session_endpoint(service_key='baremetal')
            try:
                self._ironic_client = ironic_client.Client(
                    '1', endpoint, token=token,
                    timeout=self.api_timeout)
            except Exception as e:
                self.log.debug("ironic auth failed", exc_info=True)
                raise OpenStackCloudException(
                    "Error in connecting to ironic: %s" % str(e))
        return self._ironic_client

    def list_nics(self):
        return meta.obj_list_to_dict(self.ironic_client.port.list())

    def list_nics_for_machine(self, uuid):
        return meta.obj_list_to_dict(self.ironic_client.node.list_ports(uuid))

    def get_nic_by_mac(self, mac):
        try:
            return meta.obj_to_dict(self.ironic_client.port.get(mac))
        except ironic_exceptions.ClientException:
            return None

    def list_machines(self):
        return meta.obj_list_to_dict(self.ironic_client.node.list())

    def get_machine(self, name_or_id):
        """Get Machine by name or uuid

        Search the baremetal host out by utilizing the supplied id value
        which can consist of a name or UUID.

        :param name_or_id: A node name or UUID that will be looked up.

        :returns: Dictonary representing the node found or None if no nodes
                  are found.
        """
        try:
            return meta.obj_to_dict(self.ironic_client.node.get(name_or_id))
        except ironic_exceptions.ClientException:
            return None

    def get_machine_by_mac(self, mac):
        try:
            port = self.ironic_client.port.get(mac)
            return meta.obj_to_dict(
                self.ironic_client.node.get(port.node_uuid))
        except ironic_exceptions.ClientException:
            return None

    def register_machine(self, nics, **kwargs):
        """Register Baremetal with Ironic

        Allows for the registration of Baremetal nodes with Ironic
        and population of pertinant node information or configuration
        to be passed to the Ironic API for the node.

        This method also creates ports for a list of MAC addresses passed
        in to be utilized for boot and potentially network configuration.

        If a failure is detected creating the network ports, any ports
        created are deleted, and the node is removed from Ironic.

        :param list nics: An array of MAC addresses that represent the
                          network interfaces for the node to be created.

                          Example:
                          [
                          {'mac': 'aa:bb:cc:dd:ee:01'},
                          {'mac': 'aa:bb:cc:dd:ee:02'}
                          ]

        :param **kwargs: Key value pairs to be passed to the Ironic API,
                         including uuid, name, chassis_uuid, driver_info,
                         parameters.

        :raises: OpenStackCloudException on operation error.

        :returns: Returns a dictonary representing the new
                  baremetal node.
        """
        try:
            machine = self.manager.submitTask(
                _tasks.MachineCreate(**kwargs))
        except Exception as e:
            self.log.debug("ironic machine registration failed", exc_info=True)
            raise OpenStackCloudException(
                "Error registering machine with Ironic: %s" % str(e))

        created_nics = []
        try:
            for row in nics:
                nic = self.manager.submitTask(
                    _tasks.MachinePortCreate(address=row['mac'],
                                             node_uuid=machine.uuid))
                created_nics.append(nic.uuid)

        except Exception as e:
            self.log.debug("ironic NIC registration failed", exc_info=True)
            # TODO(mordred) Handle failures here
            try:
                for uuid in created_nics:
                    try:
                        self.manager.submitTask(
                            _tasks.MachinePortDelete(
                                port_id=uuid))
                    except:
                        pass
            finally:
                self.manager.submitTask(
                    _tasks.MachineDelete(node_id=machine.uuid))
            raise OpenStackCloudException(
                "Error registering NICs with the baremetal service: %s"
                % str(e))
        return meta.obj_to_dict(machine)

    def unregister_machine(self, nics, uuid):
        """Unregister Baremetal from Ironic

        Removes entries for Network Interfaces and baremetal nodes
        from an Ironic API

        :param list nics: An array of strings that consist of MAC addresses
        to be removed.
        :param string uuid: The UUID of the node to be deleted.

        :raises: OpenStackCloudException on operation failure.
        """

        # TODO(TheJulia): Change to lookup the MAC addresses and/or block any
        # the action if the node is in an Active state as the API would.
        for nic in nics:
            try:
                self.manager.submitTask(
                    _tasks.MachinePortDelete(
                        port_id=(
                            self.ironic_client.port.get_by_address(nic['mac'])
                    )))

            except Exception as e:
                self.log.debug(
                    "baremetal NIC unregistration failed", exc_info=True)
                raise OpenStackCloudException(
                    "Error removing NIC '%s' from baremetal API for "
                    "node '%s'. Error: %s" % (nic, uuid, str(e)))
        try:
            self.manager.submitTask(
                _tasks.MachineDelete(node_id=uuid))

        except Exception as e:
            self.log.debug(
                "baremetal machine unregistration failed", exc_info=True)
            raise OpenStackCloudException(
                "Error unregistering machine %s from the baremetal API. "
                "Error: %s" % (uuid, str(e)))

    def patch_machine(self, name_or_id, patch):
        """Patch Machine Information

        This method allows for an interface to manipulate node entries
        within Ironic.  Specifically, it is a pass-through for the
        ironicclient.nodes.update interface which allows the Ironic Node
        properties to be updated.

        :param node_id: The server object to attach to.
        :param patch: The JSON Patch document is a list of dictonary objects
                      that comply with RFC 6902 which can be found at
                      https://tools.ietf.org/html/rfc6902.

                      Example patch construction:

                      patch=[]
                      patch.append({
                          'op': 'remove',
                          'path': '/instance_info'
                      })
                      patch.append({
                          'op': 'replace',
                          'path': '/name',
                          'value': 'newname'
                      })
                      patch.append({
                          'op': 'add',
                          'path': '/driver_info/username',
                          'value': 'administrator'
                      })

        :raises: OpenStackCloudException on operation error.

        :returns: Dictonary representing the newly updated node.
        """

        try:
            return meta.obj_to_dict(
                self.manager.submitTask(
                    _tasks.MachinePatch(node_id=name_or_id,
                                        patch=patch,
                                        http_method='PATCH')))
        except Exception as e:
            self.log.debug(
                "Machine patch update failed", exc_info=True)
            raise OpenStackCloudException(
                "Error updating machine via patch operation. node: %s. "
                "%s" % (name_or_id, str(e)))

    def update_machine(self, name_or_id, chassis_uuid=None, driver=None,
                       driver_info=None, name=None, instance_info=None,
                       instance_uuid=None, properties=None):
        """Update a machine with new configuration information

        A user-friendly method to perform updates of a machine, in whole or
        part.

        :param string name_or_id: A machine name or UUID to be updated.
        :param string chassis_uuid: Assign a chassis UUID to the machine.
                                    NOTE: As of the Kilo release, this value
                                    cannot be changed once set. If a user
                                    attempts to change this value, then the
                                    Ironic API, as of Kilo, will reject the
                                    request.
        :param string driver: The driver name for controlling the machine.
        :param dict driver_info: The dictonary defining the configuration
                                 that the driver will utilize to control
                                 the machine.  Permutations of this are
                                 dependent upon the specific driver utilized.
        :param string name: A human relatable name to represent the machine.
        :param dict instance_info: A dictonary of configuration information
                                   that conveys to the driver how the host
                                   is to be configured when deployed.
                                   be deployed to the machine.
        :param string instance_uuid: A UUID value representing the instance
                                     that the deployed machine represents.
        :param dict properties: A dictonary defining the properties of a
                                machine.

        :raises: OpenStackCloudException on operation error.

        :returns: Dictonary containing a machine sub-dictonary consisting
                  of the updated data returned from the API update operation,
                  and a list named changes which contains all of the API paths
                  that received updates.
        """
        machine = self.get_machine(name_or_id)
        if not machine:
            raise OpenStackCloudException(
                "Machine update failed to find Machine: %s. " % name_or_id)

        machine_config = {}
        new_config = {}

        try:
            if chassis_uuid:
                machine_config['chassis_uuid'] = machine['chassis_uuid']
                new_config['chassis_uuid'] = chassis_uuid

            if driver:
                machine_config['driver'] = machine['driver']
                new_config['driver'] = driver

            if driver_info:
                machine_config['driver_info'] = machine['driver_info']
                new_config['driver_info'] = driver_info

            if name:
                machine_config['name'] = machine['name']
                new_config['name'] = name

            if instance_info:
                machine_config['instance_info'] = machine['instance_info']
                new_config['instance_info'] = instance_info

            if instance_uuid:
                machine_config['instance_uuid'] = machine['instance_uuid']
                new_config['instance_uuid'] = instance_uuid

            if properties:
                machine_config['properties'] = machine['properties']
                new_config['properties'] = properties
        except KeyError as e:
            self.log.debug(
                "Unexpected machine response missing key %s [%s]" % (
                    e.args[0], name_or_id))
            self.log.debug(
                "Machine update failed - update value preparation failed. "
                "Potential API failure or change has been encountered",
                exc_info=True)
            raise OpenStackCloudException(
                "Machine update failed - machine [%s] missing key %s. "
                "Potential API issue."
                % (name_or_id, e.args[0]))

        try:
            patch = jsonpatch.JsonPatch.from_diff(machine_config, new_config)
        except Exception as e:
            self.log.debug(
                "Machine update failed - patch object generation failed",
                exc_info=True)
            raise OpenStackCloudException(
                "Machine update failed - Error generating JSON patch object "
                "for submission to the API. Machine: %s Error: %s"
                % (name_or_id, str(e)))

        try:
            if not patch:
                return dict(
                    node=machine,
                    changes=None
                )
            else:
                machine = self.patch_machine(machine['uuid'], list(patch))
                change_list = []
                for change in list(patch):
                    change_list.append(change['path'])
                return dict(
                    node=machine,
                    changes=change_list
                )
        except Exception as e:
            self.log.debug(
                "Machine update failed - patch operation failed",
                exc_info=True)
            raise OpenStackCloudException(
                "Machine update failed - patch operation failed Machine: %s "
                "Error: %s" % (name_or_id, str(e)))

    def validate_node(self, uuid):
        try:
            ifaces = self.ironic_client.node.validate(uuid)
        except Exception as e:
            self.log.debug(
                "ironic node validation call failed", exc_info=True)
            raise OpenStackCloudException(str(e))

        if not ifaces.deploy or not ifaces.power:
            raise OpenStackCloudException(
                "ironic node %s failed to validate. "
                "(deploy: %s, power: %s)" % (ifaces.deploy, ifaces.power))

    def node_set_provision_state(self, name_or_id, state, configdrive=None):
        """Set Node Provision State

        Enables a user to provision a Machine and optionally define a
        config drive to be utilized.

        :param string name_or_id: The Name or UUID value representing the
                              baremetal node.
        :param string state: The desired provision state for the
                             baremetal node.
        :param string configdrive: An optional URL or file or path
                                   representing the configdrive. In the
                                   case of a directory, the client API
                                   will create a properly formatted
                                   configuration drive file and post the
                                   file contents to the API for
                                   deployment.

        :raises: OpenStackCloudException on operation error.

        :returns: Per the API, no value should be returned with a successful
                  operation.
        """
        try:
            return meta.obj_to_dict(
                self.manager.submitTask(
                    _tasks.MachineSetProvision(node_uuid=name_or_id,
                                               state=state,
                                               configdrive=configdrive))
                )
        except Exception as e:
            self.log.debug(
                "Baremetal machine node failed change provision state to %s"
                % state,
                exc_info=True)
            raise OpenStackCloudException(str(e))

    def set_machine_maintenance_state(
            self,
            name_or_id,
            state=True,
            reason=None):
        """Set Baremetal Machine Maintenance State

        Sets Baremetal maintenance state and maintenance reason.

        :param string name_or_id: The Name or UUID value representing the
                                  baremetal node.
        :param boolean state: The desired state of the node.  True being in
                              maintenance where as False means the machine
                              is not in maintenance mode.  This value
                              defaults to True if not explicitly set.
        :param string reason: An optional freeform string that is supplied to
                              the baremetal API to allow for notation as to why
                              the node is in maintenance state.

        :raises: OpenStackCloudException on operation error.

        :returns: None
        """
        try:
            if state:
                result = self.manager.submitTask(
                    _tasks.MachineSetMaintenance(node_id=name_or_id,
                                                 state='true',
                                                 maint_reason=reason))
            else:
                result = self.manager.submitTask(
                    _tasks.MachineSetMaintenance(node_id=name_or_id,
                                                 state='false'))
            if result is not None:
                self.log.debug(
                    "Failed setting machine maintenance state on node %s. "
                    "User requested '%s'.' Received: %s" % (
                        name_or_id, state, result))
                raise OpenStackCloudException(
                    "Failed setting machine maintenance state on node %s. "
                    "Received: %s" % (name_or_id, result))
            return None
        except Exception as e:
            self.log.debug(
                "failed setting maintenance state on node %s" % name_or_id,
                exc_info=True)
            raise OpenStackCloudException(
                "Error setting machine maintenance on node %s. "
                "state: %s" % (name_or_id, str(e)))

    def remove_machine_from_maintenance(self, name_or_id):
        """Remove Baremetal Machine from Maintenance State

        Similarly to set_machine_maintenance_state, this method
        removes a machine from maintenance state.  It must be noted
        that this method simpily calls set_machine_maintenace_state
        for the name_or_id requested and sets the state to False.

        :param string name_or_id: The Name or UUID value representing the
                                  baremetal node.

        :raises: OpenStackCloudException on operation error.

        :returns: None
        """
        self.set_machine_maintenance_state(name_or_id, False)

    def _set_machine_power_state(self, name_or_id, state):
        """Set machine power state to on or off

        This private method allows a user to turn power on or off to
        a node via the Baremetal API.

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "on"
                                   state.
        :params string state: A value of "on", "off", or "reboot" that is
                              passed to the baremetal API to be asserted to
                              the machine.  In the case of the "reboot" state,
                              Ironic will return the host to the "on" state.

        :raises: OpenStackCloudException on operation error or.

        :returns: None
        """
        try:
            power = self.manager.submitTask(
                _tasks.MachineSetPower(node_id=name_or_id,
                                       state=state))
            if power is not None:
                self.log.debug(
                    "Failed setting machine power state on node %s. User "
                    "requested '%s'.' Received: %s" % (
                        name_or_id, state, power))
                raise OpenStackCloudException(
                    "Failed setting machine power state on node %s. "
                    "Received: %s" % (name_or_id, power))
            return None
        except Exception as e:
            self.log.debug(
                "Error setting machine power state on node %s. User "
                "requested '%s'.'" % (name_or_id, state),
                exc_info=True)
            raise OpenStackCloudException(
                "Error setting machine power state on node %s. "
                "Error: %s" % (name_or_id, str(e)))

    def set_machine_power_on(self, name_or_id):
        """Activate baremetal machine power

        This is a method that sets the node power state to "on".

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "on"
                                   state.

        :raises: OpenStackCloudException on operation error.

        :returns: None
        """
        self._set_machine_power_state(name_or_id, 'on')

    def set_machine_power_off(self, name_or_id):
        """De-activate baremetal machine power

        This is a method that sets the node power state to "off".

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "off"
                                   state.

        :raises: OpenStackCloudException on operation error.

        :returns:
        """
        self._set_machine_power_state(name_or_id, 'off')

    def set_machine_power_reboot(self, name_or_id):
        """De-activate baremetal machine power

        This is a method that sets the node power state to "reboot", which
        in essence changes the machine power state to "off", and that back
        to "on".

        :params string name_or_id: A string representing the baremetal
                                   node to have power turned to an "off"
                                   state.

        :raises: OpenStackCloudException on operation error.

        :returns: None
        """
        self._set_machine_power_state(name_or_id, 'reboot')

    def activate_node(self, uuid, configdrive=None):
        self.node_set_provision_state(uuid, 'active', configdrive)

    def deactivate_node(self, uuid):
        self.node_set_provision_state(uuid, 'deleted')

    def set_node_instance_info(self, uuid, patch):
        try:
            return meta.obj_to_dict(
                self.ironic_client.node.update(uuid, patch))
        except Exception as e:
            self.log.debug(
                "Failed to update instance_info", exc_info=True)
            raise OpenStackCloudException(str(e))

    def purge_node_instance_info(self, uuid):
        patch = []
        patch.append({'op': 'remove', 'path': '/instance_info'})
        try:
            return meta.obj_to_dict(
                self.ironic_client.node.update(uuid, patch))
        except Exception as e:
            self.log.debug(
                "Failed to delete instance_info", exc_info=True)
            raise OpenStackCloudException(str(e))
