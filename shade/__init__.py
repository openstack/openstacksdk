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

import contextlib
import hashlib
import inspect
import logging
import operator

from cinderclient.v1 import client as cinder_client
from designateclient.v1 import Client as designate_client
from decorator import decorator
from dogpile import cache
import glanceclient
import glanceclient.exc
from glanceclient.common import utils as glance_utils
from ironicclient import client as ironic_client
from ironicclient import exceptions as ironic_exceptions
import jsonpatch
import keystoneauth1.exceptions
from keystoneauth1 import plugin as ksa_plugin
from keystoneauth1 import session as ksa_session
from keystoneclient.v2_0 import client as k2_client
from keystoneclient.v3 import client as k3_client
from novaclient import client as nova_client
from novaclient import exceptions as nova_exceptions
from neutronclient.common import exceptions as neutron_exceptions
from neutronclient.v2_0 import client as neutron_client
import os_client_config
import os_client_config.defaults
import pbr.version
import swiftclient.client as swift_client
import swiftclient.service as swift_service
import swiftclient.exceptions as swift_exceptions
import troveclient.client as trove_client

# Disable the Rackspace warnings about deprecated certificates. We are aware
import warnings
warnings.filterwarnings('ignore', 'Certificate has no `subjectAltName`')

from shade.exc import *  # noqa
from shade import _log
from shade import meta
from shade import task_manager
from shade import _tasks
from shade import _utils


__version__ = pbr.version.VersionInfo('shade').version_string()
OBJECT_MD5_KEY = 'x-object-meta-x-shade-md5'
OBJECT_SHA256_KEY = 'x-object-meta-x-shade-sha256'
IMAGE_MD5_KEY = 'owner_specified.shade.md5'
IMAGE_SHA256_KEY = 'owner_specified.shade.sha256'
# Rackspace returns this for intermittent import errors
IMAGE_ERROR_396 = "Image cannot be imported. Error code: '396'"
DEFAULT_OBJECT_SEGMENT_SIZE = 1073741824  # 1GB
# This halves the current default for Swift
DEFAULT_MAX_FILE_SIZE = (5 * 1024 * 1024 * 1024 + 2) / 2


OBJECT_CONTAINER_ACLS = {
    'public': ".r:*,.rlistings",
    'private': '',
}


def valid_kwargs(*valid_args):
    # This decorator checks if argument passed as **kwargs to a function are
    # present in valid_args.
    #
    # Typically, valid_kwargs is used when we want to distinguish between
    # None and omitted arguments and we still want to validate the argument
    # list.
    #
    # Example usage:
    #
    # @valid_kwargs('opt_arg1', 'opt_arg2')
    # def my_func(self, mandatory_arg1, mandatory_arg2, **kwargs):
    #   ...
    #
    @decorator
    def func_wrapper(func, *args, **kwargs):
        argspec = inspect.getargspec(func)
        for k in kwargs:
            if k not in argspec.args[1:] and k not in valid_args:
                raise TypeError(
                    "{f}() got an unexpected keyword argument "
                    "'{arg}'".format(f=inspect.stack()[1][3], arg=k))
        return func(*args, **kwargs)
    return func_wrapper


def simple_logging(debug=False):
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    log = _log.setup_logging('shade')
    log.addHandler(logging.StreamHandler())
    log.setLevel(log_level)


def openstack_clouds(config=None, debug=False):
    if not config:
        config = os_client_config.OpenStackConfig()
    try:
        return [
            OpenStackCloud(
                cloud=f.name, debug=debug,
                cache_interval=config.get_cache_max_age(),
                cache_class=config.get_cache_class(),
                cache_arguments=config.get_cache_arguments(),
                cloud_config=f,
                **f.config)
            for f in config.get_all_clouds()
        ]
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))


def openstack_cloud(config=None, **kwargs):
    if not config:
        config = os_client_config.OpenStackConfig()
    try:
        cloud_config = config.get_one_cloud(**kwargs)
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))
    return OpenStackCloud(
        cache_interval=config.get_cache_max_age(),
        cache_class=config.get_cache_class(),
        cache_arguments=config.get_cache_arguments(),
        cloud_config=cloud_config)


def operator_cloud(config=None, **kwargs):
    if 'interface' not in kwargs:
        kwargs['interface'] = 'admin'
    if not config:
        config = os_client_config.OpenStackConfig()
    try:
        cloud_config = config.get_one_cloud(**kwargs)
    except keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin as e:
        raise OpenStackCloudException(
            "Invalid cloud configuration: {exc}".format(exc=str(e)))
    return OperatorCloud(
        cache_interval=config.get_cache_max_age(),
        cache_class=config.get_cache_class(),
        cache_arguments=config.get_cache_arguments(),
        cloud_config=cloud_config)


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
    for image in images:
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
    :param CloudConfig cloud_config: Cloud config object from os-client-config
                                     In the future, this will be the only way
                                     to pass in cloud configuration, but is
                                     being phased in currently.
    """

    def __init__(
            self,
            cloud_config=None,
            cache_interval=None,
            cache_class='dogpile.cache.null',
            cache_arguments=None,
            manager=None, **kwargs):

        self.log = _log.setup_logging('shade')
        if not cloud_config:
            config = os_client_config.OpenStackConfig()
            cloud_config = config.get_one_cloud(**kwargs)

        self.name = cloud_config.name
        self.auth = cloud_config.get_auth_args()
        self.region_name = cloud_config.region_name
        self.default_interface = cloud_config.get_interface()
        self.private = cloud_config.config.get('private', False)
        self.api_timeout = cloud_config.config['api_timeout']
        self.image_api_use_tasks = cloud_config.config['image_api_use_tasks']
        self.secgroup_source = cloud_config.config['secgroup_source']

        self._external_network = None
        self._external_network_name_or_id = cloud_config.config.get(
            'external_network', None)
        self._use_external_network = cloud_config.config.get(
            'use_external_network', True)

        self._internal_network = None
        self._internal_network_name_or_id = cloud_config.config.get(
            'internal_network', None)
        self._use_internal_network = cloud_config.config.get(
            'use_internal_network', True)

        # Variables to prevent us from going through the network finding
        # logic again if we've done it once. This is different from just
        # the cached value, since "None" is a valid value to find.
        self._external_network_stamp = False
        self._internal_network_stamp = False

        if manager is not None:
            self.manager = manager
        else:
            self.manager = task_manager.TaskManager(
                name=self.name, client=self)

        (self.verify, self.cert) = cloud_config.get_requests_verify_args()

        self._cache = cache.make_region(
            function_key_generator=self._make_cache_key
        ).configure(
            cache_class, expiration_time=cache_interval,
            arguments=cache_arguments)
        self._container_cache = dict()
        self._file_hash_cache = dict()

        self._keystone_session = None

        self._cinder_client = None
        self._designate_client = None
        self._glance_client = None
        self._glance_endpoint = None
        self._ironic_client = None
        self._keystone_client = None
        self._neutron_client = None
        self._nova_client = None
        self._swift_client = None
        self._swift_service = None
        self._trove_client = None

        self.cloud_config = cloud_config

    @contextlib.contextmanager
    def _neutron_exceptions(self, error_message):
        try:
            yield
        except neutron_exceptions.NotFound as e:
            raise OpenStackCloudResourceNotFound(
                "{msg}: {exc}".format(msg=error_message, exc=str(e)))
        except neutron_exceptions.NeutronClientException as e:
            if e.status_code == 404:
                raise OpenStackCloudURINotFound(
                    "{msg}: {exc}".format(msg=error_message, exc=str(e)))
            else:
                raise OpenStackCloudException(
                    "{msg}: {exc}".format(msg=error_message, exc=str(e)))
        except Exception as e:
            raise OpenStackCloudException(
                "{msg}: {exc}".format(msg=error_message, exc=str(e)))

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
                [str(name_key), fname, arg_key, kwargs_key])
            return ans
        return generate_key

    def _get_client(
            self, service_key, client_class, interface_key='endpoint_type',
            pass_version_arg=True, **kwargs):
        try:
            interface = self.cloud_config.get_interface(service_key)
            # trigger exception on lack of service
            self.get_session_endpoint(service_key)
            constructor_args = dict(
                session=self.keystone_session,
                service_name=self.cloud_config.get_service_name(service_key),
                service_type=self.cloud_config.get_service_type(service_key),
                region_name=self.region_name)
            constructor_args.update(kwargs)
            constructor_args[interface_key] = interface
            if pass_version_arg:
                version = self.cloud_config.get_api_version(service_key)
                constructor_args['version'] = version
            client = client_class(**constructor_args)
        except Exception:
            self.log.debug(
                "Couldn't construct {service} object".format(
                    service=service_key), exc_info=True)
            raise
        if client is None:
            raise OpenStackCloudException(
                "Failed to instantiate {service} client."
                " This could mean that your credentials are wrong.".format(
                    service=service_key))
        return client

    @property
    def nova_client(self):
        if self._nova_client is None:
            self._nova_client = self._get_client(
                'compute', nova_client.Client)
        return self._nova_client

    def _get_identity_client_class(self):
        if self.cloud_config.get_api_version('identity') == '3':
            return k3_client.Client
        elif self.cloud_config.get_api_version('identity') in ('2', '2.0'):
            return k2_client.Client
        raise OpenStackCloudException(
            "Unknown identity API version: {version}".format(
                version=self.cloud_config.get_api_version('identity')))

    @property
    def keystone_session(self):
        if self._keystone_session is None:

            try:
                keystone_auth = self.cloud_config.get_auth()
                if not keystone_auth:
                    raise OpenStackCloudException(
                        "Problem with auth parameters")
                self._keystone_session = ksa_session.Session(
                    auth=keystone_auth,
                    verify=self.verify,
                    cert=self.cert,
                    timeout=self.api_timeout)
            except Exception as e:
                raise OpenStackCloudException(
                    "Error authenticating to keystone: %s " % str(e))
        return self._keystone_session

    @property
    def keystone_client(self):
        if self._keystone_client is None:
            self._keystone_client = self._get_client(
                'identity', self._get_identity_client_class())
        return self._keystone_client

    @property
    def service_catalog(self):
        return self.keystone_session.auth.get_access(
            self.keystone_session).service_catalog.catalog

    @property
    def auth_token(self):
        # Keystone's session will reuse a token if it is still valid.
        # We don't need to track validity here, just get_token() each time.
        return self.keystone_session.get_token()

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

    def _get_project_param_dict(self, name_or_id):
        project_dict = dict()
        if name_or_id:
            project_id = self._get_project(name_or_id).id
            if self.cloud_config.get_api_version('identity') == '3':
                project_dict['default_project'] = project_id
            else:
                project_dict['tenant_id'] = project_id
        return project_dict

    def _get_domain_param_dict(self, domain_id):
        """Get a useable domain."""

        # Keystone v3 requires domains for user and project creation. v2 does
        # not. However, keystone v2 does not allow user creation by non-admin
        # users, so we can throw an error to the user that does not need to
        # mention api versions
        if self.cloud_config.get_api_version('identity') == '3':
            if not domain_id:
                raise OpenStackCloudException(
                    "User creation requires an explicit domain_id argument.")
            else:
                return {'domain': domain_id}
        else:
            return {}

    def _get_identity_params(self, domain_id=None, project=None):
        """Get the domain and project/tenant parameters if needed.

        keystone v2 and v3 are divergent enough that we need to pass or not
        pass project or tenant_id or domain or nothing in a sane manner.
        """
        ret = {}
        ret.update(self._get_domain_param_dict(domain_id))
        ret.update(self._get_project_param_dict(project))
        return ret

    def _get_project(self, name_or_id):
        """Retrieve a project by name or id."""

        # TODO(mordred): This, and other keystone operations, need to have
        #                domain information passed in. When there is no
        #                available domain information, we should default to
        #                the currently scoped domain which we can request from
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
            raise OpenStackCloudException(
                "Error in updating project {project}: {message}".format(
                    project=name_or_id, message=str(e)))

    def create_project(
            self, name, description=None, domain_id=None, enabled=True):
        """Create a project."""
        try:
            domain_params = self._get_domain_param_dict(domain_id)
            self._project_manager.create(
                project_name=name, description=description, enabled=enabled,
                **domain_params)
        except Exception as e:
            raise OpenStackCloudException(
                "Error in creating project {project}: {message}".format(
                    project=name, message=str(e)))

    def delete_project(self, name_or_id):
        try:
            project = self.update_project(name_or_id, enabled=False)
            self._project_manager.delete(project.id)
        except Exception as e:
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
            raise OpenStackCloudException(
                "Error in updating user {user}: {message}".format(
                    user=name_or_id, message=str(e)))
        self.get_user_cache.invalidate(self)
        return meta.obj_to_dict(user)

    def create_user(
            self, name, password=None, email=None, default_project=None,
            enabled=True, domain_id=None):
        """Create a user."""
        try:
            identity_params = self._get_identity_params(
                domain_id, default_project)
            user = self.manager.submitTask(_tasks.UserCreate(
                user_name=name, password=password, email=email,
                enabled=enabled, **identity_params))
        except Exception as e:
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
            raise OpenStackCloudException(
                "Error in deleting user {user}: {message}".format(
                    user=name_or_id, message=str(e)))
        self.get_user_cache.invalidate(self)

    @property
    def glance_client(self):
        if self._glance_client is None:
            endpoint, version = glance_utils.strip_version(
                self.get_session_endpoint(service_key='image'))
            # TODO(mordred): Put check detected vs. configured version
            # and warn if they're different.
            self._glance_client = self._get_client(
                'image', glanceclient.Client, interface_key='interface',
                endpoint=endpoint)
        return self._glance_client

    @property
    def swift_client(self):
        if self._swift_client is None:
            try:
                token = self.keystone_session.get_token()
                endpoint = self.get_session_endpoint(
                    service_key='object-store')
                self._swift_client = swift_client.Connection(
                    preauthurl=endpoint,
                    preauthtoken=token,
                    auth_version=self.cloud_config.get_api_version('identity'),
                    os_options=dict(
                        auth_token=token,
                        object_storage_url=endpoint,
                        region_name=self.region_name),
                    timeout=self.api_timeout,
                )
            except OpenStackCloudException:
                raise
            except Exception as e:
                raise OpenStackCloudException(
                    "Error constructing swift client: %s", str(e))
        return self._swift_client

    @property
    def swift_service(self):
        if self._swift_service is None:
            try:
                endpoint = self.get_session_endpoint(
                    service_key='object-store')
                options = dict(os_auth_token=self.auth_token,
                               os_storage_url=endpoint,
                               os_region_name=self.region_name)
                self._swift_service = swift_service.SwiftService(
                    options=options)
            except OpenStackCloudException:
                raise
            except Exception as e:
                raise OpenStackCloudException(
                    "Error constructing swift client: %s", str(e))
        return self._swift_service

    @property
    def cinder_client(self):

        if self._cinder_client is None:
            self._cinder_client = self._get_client(
                'volume', cinder_client.Client)
        return self._cinder_client

    @property
    def trove_client(self):
        if self._trove_client is None:
            self.get_session_endpoint(service_key='database')
            # Make the connection - can't use keystone session until there
            # is one
            self._trove_client = trove_client.Client(
                self.cloud_config.get_api_version('database'),
                session=self.keystone_session,
                region_name=self.region_name,
                service_type=self.cloud_config.get_service_type('database'),
            )

            if self._trove_client is None:
                raise OpenStackCloudException(
                    "Failed to instantiate Trove client."
                    " This could mean that your credentials are wrong.")

            self._trove_client = self._get_client(
                'database', trove_client.Client)
        return self._trove_client

    @property
    def neutron_client(self):
        if self._neutron_client is None:
            self._neutron_client = self._get_client(
                'network', neutron_client.Client, pass_version_arg=False)
        return self._neutron_client

    @property
    def designate_client(self):
        if self._designate_client is None:
            self._designate_client = self._get_client(
                'dns', designate_client.Client)
        return self._designate_client

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
        override_endpoint = self.cloud_config.get_endpoint(service_key)
        if override_endpoint:
            return override_endpoint
        try:
            # keystone is a special case in keystone, because what?
            if service_key == 'identity':
                endpoint = self.keystone_session.get_endpoint(
                    interface=ksa_plugin.AUTH_INTERFACE)
            else:
                endpoint = self.keystone_session.get_endpoint(
                    service_type=self.cloud_config.get_service_type(
                        service_key),
                    service_name=self.cloud_config.get_service_name(
                        service_key),
                    interface=self.cloud_config.get_interface(service_key),
                    region_name=self.region_name)
        except keystoneauth1.exceptions.catalog.EndpointNotFound as e:
            self.log.debug(
                "Endpoint not found in %s cloud: %s", self.name, str(e))
            endpoint = None
        except Exception as e:
            raise OpenStackCloudException(
                "Error getting %s endpoint: %s" % (service_key, str(e)))
        return endpoint

    def has_service(self, service_key):
        if not self.cloud_config.config.get('has_%s' % service_key, True):
            self.log.debug(
                "Overriding {service_key} entry in catalog per config".format(
                    service_key=service_key))
            return False
        try:
            endpoint = self.get_session_endpoint(service_key)
        except OpenStackCloudException:
            return False
        if endpoint:
            return True
        else:
            return False

    @_cache_on_arguments()
    def _nova_extensions(self):
        extensions = set()

        try:
            resp, body = self.manager.submitTask(
                _tasks.NovaUrlGet(url='/extensions'))
            for x in body['extensions']:
                extensions.add(x['alias'])
        except Exception as e:
            raise OpenStackCloudException(
                "error fetching extension list for nova: {msg}".format(
                    msg=str(e)))

        return extensions

    def _has_nova_extension(self, extension_name):
        return extension_name in self._nova_extensions()

    def search_keypairs(self, name_or_id=None, filters=None):
        keypairs = self.list_keypairs()
        return _utils._filter_list(keypairs, name_or_id, filters)

    def search_networks(self, name_or_id=None, filters=None):
        networks = self.list_networks()
        return _utils._filter_list(networks, name_or_id, filters)

    def search_routers(self, name_or_id=None, filters=None):
        routers = self.list_routers()
        return _utils._filter_list(routers, name_or_id, filters)

    def search_subnets(self, name_or_id=None, filters=None):
        subnets = self.list_subnets()
        return _utils._filter_list(subnets, name_or_id, filters)

    def search_ports(self, name_or_id=None, filters=None):
        ports = self.list_ports()
        return _utils._filter_list(ports, name_or_id, filters)

    def search_volumes(self, name_or_id=None, filters=None):
        volumes = self.list_volumes()
        return _utils._filter_list(volumes, name_or_id, filters)

    def search_flavors(self, name_or_id=None, filters=None):
        flavors = self.list_flavors()
        return _utils._filter_list(flavors, name_or_id, filters)

    def search_security_groups(self, name_or_id=None, filters=None):
        groups = self.list_security_groups()
        return _utils._filter_list(groups, name_or_id, filters)

    def search_servers(self, name_or_id=None, filters=None):
        servers = self.list_servers()
        return _utils._filter_list(servers, name_or_id, filters)

    def search_images(self, name_or_id=None, filters=None):
        images = self.list_images()
        return _utils._filter_list(images, name_or_id, filters)

    def search_floating_ip_pools(self, name=None, filters=None):
        pools = self.list_floating_ip_pools()
        return _utils._filter_list(pools, name, filters)

    # Note (dguerri): when using Neutron, this can be optimized using
    # server-side search.
    # There are some cases in which such optimization is not possible (e.g.
    # nested attributes or list of objects) so we need to use the client-side
    # filtering when we can't do otherwise.
    # The same goes for all neutron-related search/get methods!
    def search_floating_ips(self, id=None, filters=None):
        floating_ips = self.list_floating_ips()
        return _utils._filter_list(floating_ips, id, filters)

    def search_domains(self, name_or_id=None, filters=None):
        domains = self.list_domains()
        return _utils._filter_list(domains, name_or_id, filters)

    def search_records(self, domain_id, name_or_id=None, filters=None):
        records = self.list_records(domain_id=domain_id)
        return _utils._filter_list(records, name_or_id, filters)

    def list_keypairs(self):
        try:
            return meta.obj_list_to_dict(
                self.manager.submitTask(_tasks.KeypairList())
            )
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching keypair list: %s" % str(e))

    def list_networks(self):
        with self._neutron_exceptions("Error fetching network list"):
            return self.manager.submitTask(_tasks.NetworkList())['networks']

    def list_routers(self):
        with self._neutron_exceptions("Error fetching router list"):
            return self.manager.submitTask(_tasks.RouterList())['routers']

    def list_subnets(self):
        with self._neutron_exceptions("Error fetching subnet list"):
            return self.manager.submitTask(_tasks.SubnetList())['subnets']

    def list_ports(self):
        with self._neutron_exceptions("Error fetching port list"):
            return self.manager.submitTask(_tasks.PortList())['ports']

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
            raise OpenStackCloudException(
                "Error fetching volume list: %s" % e)

    @_cache_on_arguments()
    def list_flavors(self):
        try:
            return meta.obj_list_to_dict(
                self.manager.submitTask(_tasks.FlavorList(is_public=None))
            )
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching flavor list: %s" % e)

    def list_security_groups(self):
        # Handle neutron security groups
        if self.secgroup_source == 'neutron':
            # Neutron returns dicts, so no need to convert objects here.
            with self._neutron_exceptions(
                    "Error fetching security group list"):
                return self.manager.submitTask(
                    _tasks.NeutronSecurityGroupList())['security_groups']

        # Handle nova security groups
        elif self.secgroup_source == 'nova':
            try:
                groups = meta.obj_list_to_dict(
                    self.manager.submitTask(_tasks.NovaSecurityGroupList())
                )
            except Exception:
                raise OpenStackCloudException(
                    "Error fetching security group list"
                )
            return _utils.normalize_nova_secgroups(groups)

        # Security groups not supported
        else:
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

    def list_servers(self):
        try:
            return meta.obj_list_to_dict(
                self.manager.submitTask(_tasks.ServerList())
            )
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching server list: %s" % e)

    @_cache_on_arguments(should_cache_fn=_no_pending_images)
    def list_images(self, filter_deleted=True):
        """Get available glance images.

        :param filter_deleted: Control whether deleted images are returned.
        :returns: A list of glance images.
        """
        # First, try to actually get images from glance, it's more efficient
        images = []
        try:

            # Creates a generator - does not actually talk to the cloud API
            # hardcoding page size for now. We'll have to get MUCH smarter
            # if we want to deal with page size per unit of rate limiting
            image_gen = self.glance_client.images.list(page_size=1000)
            # Deal with the generator to make a list
            image_list = self.manager.submitTask(
                _tasks.GlanceImageList(image_gen=image_gen))

            if image_list:
                if getattr(image_list[0], 'validate', None):
                    # glanceclient returns a "warlock" object if you use v2
                    image_list = meta.warlock_list_to_dict(image_list)
                else:
                    # glanceclient returns a normal object if you use v1
                    image_list = meta.obj_list_to_dict(image_list)

        except glanceclient.exc.HTTPInternalServerError:
            # We didn't have glance, let's try nova
            # If this doesn't work - we just let the exception propagate
            try:
                image_list = meta.obj_list_to_dict(
                    self.manager.submitTask(_tasks.NovaImageList())
                )
            except Exception as e:
                raise OpenStackCloudException(
                    "Error fetching image list: %s" % e)

        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching image list: %s" % e)

        for image in image_list:
            # The cloud might return DELETED for invalid images.
            # While that's cute and all, that's an implementation detail.
            if not filter_deleted:
                images.append(image)
            elif image.status != 'DELETED':
                images.append(image)
        return images

    def list_floating_ip_pools(self):
        if not self._has_nova_extension('os-floating-ip-pools'):
            raise OpenStackCloudUnavailableExtension(
                'Floating IP pools extension is not available on target cloud')

        try:
            return meta.obj_list_to_dict(
                self.manager.submitTask(_tasks.FloatingIPPoolList())
            )
        except Exception as e:
            raise OpenStackCloudException(
                "error fetching floating IP pool list: {msg}".format(
                    msg=str(e)))

    def list_floating_ips(self):
        if self.has_service('network'):
            try:
                return _utils.normalize_neutron_floating_ips(
                    self._neutron_list_floating_ips())
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'{msg}'. Trying with Nova.".format(msg=str(e)))
                # Fall-through, trying with Nova

        floating_ips = self._nova_list_floating_ips()
        return _utils.normalize_nova_floating_ips(floating_ips)

    def _neutron_list_floating_ips(self):
        with self._neutron_exceptions("error fetching floating IPs list"):
            return self.manager.submitTask(
                _tasks.NeutronFloatingIPList())['floatingips']

    def _nova_list_floating_ips(self):
        try:
            return meta.obj_list_to_dict(
                self.manager.submitTask(_tasks.NovaFloatingIPList()))
        except Exception as e:
            raise OpenStackCloudException(
                "error fetching floating IPs list: {msg}".format(msg=str(e)))

    def list_domains(self):
        try:
            return self.manager.submitTask(_tasks.DomainList())
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching domain list: %s" % e)

    def list_records(self, domain_id):
        try:
            return self.manager.submitTask(_tasks.RecordList(domain=domain_id))
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching record list: %s" % e)

    def use_external_network(self):
        return self._use_external_network

    def use_internal_network(self):
        return self._use_internal_network

    def _get_network(
            self,
            name_or_id,
            use_network_func,
            network_cache,
            network_stamp,
            filters):
        if not use_network_func():
            return None
        if network_cache:
            return network_cache
        if network_stamp:
            return None
        if not self.has_service('network'):
            return None
        if name_or_id:
            ext_net = self.get_network(name_or_id)
            if not ext_net:
                raise OpenStackCloudException(
                    "Network {network} was provided for external"
                    " access and that network could not be found".format(
                        network=name_or_id))
            else:
                return ext_net
        try:
            # TODO(mordred): Rackspace exposes neutron but it does not
            # work. I think that overriding what the service catalog
            # reports should be a thing os-client-config should handle
            # in a vendor profile - but for now it does not. That means
            # this search_networks can just totally fail. If it does though,
            # that's fine, clearly the neutron introspection is not going
            # to work.
            ext_nets = self.search_networks(filters=filters)
            if len(ext_nets) == 1:
                return ext_nets[0]
        except OpenStackCloudException:
            pass
        return None

    def get_external_network(self):
        """Return the network that is configured to route northbound.

        :returns: A network dict if one is found, None otherwise.
        """
        self._external_network = self._get_network(
            self._external_network_name_or_id,
            self.use_external_network,
            self._external_network,
            self._external_network_stamp,
            filters={'router:external': True})
        self._external_network_stamp = True

    def get_internal_network(self):
        """Return the network that is configured to not route northbound.

        :returns: A network dict if one is found, None otherwise.
        """
        self._internal_network = self._get_network(
            self._internal_network_name_or_id,
            self.use_internal_network,
            self._internal_network,
            self._internal_network_stamp,
            filters={
                'router:external': False,
                'shared': False
            })
        self._internal_network_stamp = True
        return self._internal_network

    def get_keypair(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_keypairs, name_or_id, filters)

    def get_network(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_networks, name_or_id, filters)

    def get_router(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_routers, name_or_id, filters)

    def get_subnet(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_subnets, name_or_id, filters)

    def get_port(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_ports, name_or_id, filters)

    def get_volume(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_volumes, name_or_id, filters)

    def get_flavor(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_flavors, name_or_id, filters)

    def get_security_group(self, name_or_id, filters=None):
        return _utils._get_entity(
            self.search_security_groups, name_or_id, filters)

    def get_server(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_servers, name_or_id, filters)

    def get_image(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_images, name_or_id, filters)

    def get_floating_ip(self, id, filters=None):
        return _utils._get_entity(self.search_floating_ips, id, filters)

    def get_domain(self, name_or_id, filters=None):
        return _utils._get_entity(self.search_domains, name_or_id, filters)

    def get_record(self, domain_id, name_or_id, filters=None):
        f = lambda name_or_id, filters: self.search_records(
            domain_id, name_or_id, filters)
        return _utils._get_entity(f, name_or_id, filters)

    def create_keypair(self, name, public_key):
        """Create a new keypair.

        :param name: Name of the keypair being created.
        :param public_key: Public key for the new keypair.

        :raises: OpenStackCloudException on operation error.
        """
        try:
            return meta.obj_to_dict(
                self.manager.submitTask(_tasks.KeypairCreate(
                    name=name, public_key=public_key))
            )
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to create keypair %s: %s" % (name, e)
            )

    def delete_keypair(self, name):
        """Delete a keypair.

        :param name: Name of the keypair to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        try:
            self.manager.submitTask(_tasks.KeypairDelete(key=name))
        except nova_exceptions.NotFound:
            self.log.debug("Keypair %s not found for deleting" % name)
            return False
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to delete keypair %s: %s" % (name, e)
            )
        return True

    # TODO(Shrews): This will eventually need to support tenant ID and
    # provider networks, which are admin-level params.
    def create_network(self, name, shared=False, admin_state_up=True,
                       external=False):
        """Create a network.

        :param string name: Name of the network being created.
        :param bool shared: Set the network as shared.
        :param bool admin_state_up: Set the network administrative state to up.
        :param bool external: Whether this network is externally accessible.

        :returns: The network object.
        :raises: OpenStackCloudException on operation error.
        """

        network = {
            'name': name,
            'shared': shared,
            'admin_state_up': admin_state_up,
            'router:external': external
        }

        with self._neutron_exceptions(
                "Error creating network {0}".format(name)):
            net = self.manager.submitTask(
                _tasks.NetworkCreate(body=dict({'network': network})))
        # Turns out neutron returns an actual dict, so no need for the
        # use of meta.obj_to_dict() here (which would not work against
        # a dict).
        return net['network']

    def delete_network(self, name_or_id):
        """Delete a network.

        :param name_or_id: Name or ID of the network being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        network = self.get_network(name_or_id)
        if not network:
            self.log.debug("Network %s not found for deleting" % name_or_id)
            return False

        with self._neutron_exceptions(
                "Error deleting network {0}".format(name_or_id)):
            self.manager.submitTask(
                _tasks.NetworkDelete(network=network['id']))

        return True

    def _build_external_gateway_info(self, ext_gateway_net_id, enable_snat,
                                     ext_fixed_ips):
        info = {}
        if ext_gateway_net_id:
            info['network_id'] = ext_gateway_net_id
        if enable_snat is not None:
            info['enable_snat'] = enable_snat
        if ext_fixed_ips:
            info['external_fixed_ips'] = ext_fixed_ips
        if info:
            return info
        return None

    def create_router(self, name=None, admin_state_up=True,
                      ext_gateway_net_id=None, enable_snat=None,
                      ext_fixed_ips=None):
        """Create a logical router.

        :param string name: The router name.
        :param bool admin_state_up: The administrative state of the router.
        :param string ext_gateway_net_id: Network ID for the external gateway.
        :param bool enable_snat: Enable Source NAT (SNAT) attribute.
        :param list ext_fixed_ips:
            List of dictionaries of desired IP and/or subnet on the
            external network. Example::

              [
                {
                  "subnet_id": "8ca37218-28ff-41cb-9b10-039601ea7e6b",
                  "ip_address": "192.168.10.2"
                }
              ]

        :returns: The router object.
        :raises: OpenStackCloudException on operation error.
        """
        router = {
            'admin_state_up': admin_state_up
        }
        if name:
            router['name'] = name
        ext_gw_info = self._build_external_gateway_info(
            ext_gateway_net_id, enable_snat, ext_fixed_ips
        )
        if ext_gw_info:
            router['external_gateway_info'] = ext_gw_info

        with self._neutron_exceptions(
                "Error creating router {0}".format(name)):
            new_router = self.manager.submitTask(
                _tasks.RouterCreate(body=dict(router=router)))
        # Turns out neutron returns an actual dict, so no need for the
        # use of meta.obj_to_dict() here (which would not work against
        # a dict).
        return new_router['router']

    def update_router(self, name_or_id, name=None, admin_state_up=None,
                      ext_gateway_net_id=None, enable_snat=None,
                      ext_fixed_ips=None):
        """Update an existing logical router.

        :param string name_or_id: The name or UUID of the router to update.
        :param string name: The new router name.
        :param bool admin_state_up: The administrative state of the router.
        :param string ext_gateway_net_id:
            The network ID for the external gateway.
        :param bool enable_snat: Enable Source NAT (SNAT) attribute.
        :param list ext_fixed_ips:
            List of dictionaries of desired IP and/or subnet on the
            external network. Example::

              [
                {
                  "subnet_id": "8ca37218-28ff-41cb-9b10-039601ea7e6b",
                  "ip_address": "192.168.10.2"
                }
              ]

        :returns: The router object.
        :raises: OpenStackCloudException on operation error.
        """
        router = {}
        if name:
            router['name'] = name
        if admin_state_up is not None:
            router['admin_state_up'] = admin_state_up
        ext_gw_info = self._build_external_gateway_info(
            ext_gateway_net_id, enable_snat, ext_fixed_ips
        )
        if ext_gw_info:
            router['external_gateway_info'] = ext_gw_info

        if not router:
            self.log.debug("No router data to update")
            return

        curr_router = self.get_router(name_or_id)
        if not curr_router:
            raise OpenStackCloudException(
                "Router %s not found." % name_or_id)

        with self._neutron_exceptions(
                "Error updating router {0}".format(name_or_id)):
            new_router = self.manager.submitTask(
                _tasks.RouterUpdate(
                    router=curr_router['id'], body=dict(router=router)))

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

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        router = self.get_router(name_or_id)
        if not router:
            self.log.debug("Router %s not found for deleting" % name_or_id)
            return False

        with self._neutron_exceptions(
                "Error deleting router {0}".format(name_or_id)):
            self.manager.submitTask(
                _tasks.RouterDelete(router=router['id']))

        return True

    def _reset_image_cache(self):
        self._image_cache = None

    def get_image_exclude(self, name_or_id, exclude):
        for image in self.search_images(name_or_id):
            if exclude:
                if exclude not in image.name:
                    return image
            else:
                return image
        return None

    def get_image_name(self, image_id, exclude=None):
        image = self.get_image_exclude(image_id, exclude)
        if image:
            return image.name
        return None

    def get_image_id(self, image_name, exclude=None):
        image = self.get_image_exclude(image_name, exclude)
        if image:
            return image.id
        return None

    def create_image_snapshot(self, name, server, **metadata):
        image = self.manager.submitTask(_tasks.ImageSnapshotCreate(
            image_name=name, server=server, metadata=metadata))
        if image:
            return meta.obj_to_dict(image)
        return None

    def delete_image(self, name_or_id, wait=False, timeout=3600):
        image = self.get_image(name_or_id)
        try:
            # Note that in v1, the param name is image, but in v2,
            # it's image_id
            glance_api_version = self.cloud_config.get_api_version('image')
            if glance_api_version == '2':
                self.manager.submitTask(
                    _tasks.ImageDelete(image_id=image.id))
            elif glance_api_version == '1':
                self.manager.submitTask(
                    _tasks.ImageDelete(image=image.id))
        except Exception as e:
            raise OpenStackCloudException(
                "Error in deleting image: %s" % str(e))

        if wait:
            for count in _utils._iterate_timeout(
                    timeout,
                    "Timeout waiting for the image to be deleted."):
                self._cache.invalidate()
                if self.get_image(image.id) is None:
                    return

    def create_image(
            self, name, filename, container='images',
            md5=None, sha256=None,
            disk_format=None, container_format=None,
            disable_vendor_agent=True,
            wait=False, timeout=3600, **kwargs):

        if not disk_format:
            disk_format = self.cloud_config.config['image_format']
        if not container_format:
            if disk_format == 'vhd':
                container_format = 'ovf'
            else:
                container_format = 'bare'
        if not md5 or not sha256:
            (md5, sha256) = self._get_file_hashes(filename)
        current_image = self.get_image(name)
        if (current_image and current_image.get(IMAGE_MD5_KEY, '') == md5
                and current_image.get(IMAGE_SHA256_KEY, '') == sha256):
            self.log.debug(
                "image {name} exists and is up to date".format(name=name))
            return current_image
        kwargs[IMAGE_MD5_KEY] = md5
        kwargs[IMAGE_SHA256_KEY] = sha256

        if disable_vendor_agent:
            kwargs.update(self.cloud_config.config['disable_vendor_agent'])

        # We can never have nice things. Glance v1 took "is_public" as a
        # boolean. Glance v2 takes "visibility". If the user gives us
        # is_public, we know what they mean. If they give us visibility, they
        # know that they mean.
        if self.cloud_config.get_api_version('image') == '2':
            if 'is_public' in kwargs:
                is_public = kwargs.pop('is_public')
                if is_public:
                    kwargs['visibility'] = 'public'
                else:
                    kwargs['visibility'] = 'private'

        try:
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
        except OpenStackCloudException:
            self.log.debug("Image creation failed", exc_info=True)
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Image creation failed: {message}".format(message=str(e)))

    def _upload_image_put_v2(self, name, image_data, **image_kwargs):
        if 'properties' in image_kwargs:
            img_props = image_kwargs.pop('properties')
            for k, v in iter(img_props.items()):
                image_kwargs[k] = str(v)
        image = self.manager.submitTask(_tasks.ImageCreate(
            name=name, **image_kwargs))
        self.manager.submitTask(_tasks.ImageUpload(
            image_id=image.id, image_data=image_data))
        return image

    def _upload_image_put_v1(self, name, image_data, **image_kwargs):
        image = self.manager.submitTask(_tasks.ImageCreate(
            name=name, **image_kwargs))
        self.manager.submitTask(_tasks.ImageUpdate(
            image=image, data=image_data))
        return image

    def _upload_image_put(self, name, filename, **image_kwargs):
        image_data = open(filename, 'rb')
        # Because reasons and crying bunnies
        if self.cloud_config.get_api_version('image') == '2':
            image = self._upload_image_put_v2(name, image_data, **image_kwargs)
        else:
            image = self._upload_image_put_v1(name, image_data, **image_kwargs)
        self._cache.invalidate()
        return self.get_image(image.id)

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
        task_args = dict(
            type='import', input=dict(
                import_from='{container}/{name}'.format(
                    container=container, name=name),
                image_properties=dict(name=name)))
        glance_task = self.manager.submitTask(
            _tasks.ImageTaskCreate(**task_args))
        if wait:
            image_id = None
            for count in _utils._iterate_timeout(
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
                    return self.get_image(status.result['image_id'])
                if status.status == 'failure':
                    if status.message == IMAGE_ERROR_396:
                        glance_task = self.manager.submitTask(
                            _tasks.ImageTaskCreate(**task_args))
                    else:
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
        if self.cloud_config.get_api_version('image') == '2':
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
            raise OpenStackCloudException(
                "Error in creating volume: %s" % str(e))
        self.list_volumes.invalidate(self)

        volume = meta.obj_to_dict(volume)

        if volume['status'] == 'error':
            raise OpenStackCloudException("Error in creating volume")

        if wait:
            vol_id = volume['id']
            for count in _utils._iterate_timeout(
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
            raise OpenStackCloudException(
                "Error in deleting volume: %s" % str(e))

        self.list_volumes.invalidate(self)
        if wait:
            for count in _utils._iterate_timeout(
                    timeout,
                    "Timeout waiting for the volume to be deleted."):
                if not self.volume_exists(volume['id']):
                    return

    def get_volumes(self, server, cache=True):
        volumes = []
        for volume in self.list_volumes(cache=cache):
            for attach in volume['attachments']:
                if attach['server_id'] == server['id']:
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

        :param volume: Volume dict
        :param server_id: ID of server to check

        :returns: Device name if attached, None if volume is not attached.
        """
        for attach in volume['attachments']:
            if server_id == attach['server_id']:
                return attach['device']
        return None

    def detach_volume(self, server, volume, wait=True, timeout=None):
        """Detach a volume from a server.

        :param server: The server dict to detach from.
        :param volume: The volume dict to detach.
        :param wait: If true, waits for volume to be detached.
        :param timeout: Seconds to wait for volume detachment. None is forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        dev = self.get_volume_attach_device(volume, server['id'])
        if not dev:
            raise OpenStackCloudException(
                "Volume %s is not attached to server %s"
                % (volume['id'], server['id'])
            )

        try:
            self.manager.submitTask(
                _tasks.VolumeDetach(attachment_id=volume['id'],
                                    server_id=server['id']))
        except Exception as e:
            raise OpenStackCloudException(
                "Error detaching volume %s from server %s: %s" %
                (volume['id'], server['id'], e)
            )

        if wait:
            for count in _utils._iterate_timeout(
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
        dict (as returned by get_volume()), to the server described by
        the passed in server dict (as returned by get_server()) on the
        named device on the server.

        If the volume is already attached to the server, or generally not
        available, then an exception is raised. To re-attach to a server,
        but under a different device, the user must detach it first.

        :param server: The server dict to attach to.
        :param volume: The volume dict to attach.
        :param device: The device name where the volume will attach.
        :param wait: If true, waits for volume to be attached.
        :param timeout: Seconds to wait for volume attachment. None is forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        dev = self.get_volume_attach_device(volume, server['id'])
        if dev:
            raise OpenStackCloudException(
                "Volume %s already attached to server %s on device %s"
                % (volume['id'], server['id'], dev)
            )

        if volume['status'] != 'available':
            raise OpenStackCloudException(
                "Volume %s is not available. Status is '%s'"
                % (volume['id'], volume['status'])
            )

        try:
            self.manager.submitTask(
                _tasks.VolumeAttach(volume_id=volume['id'],
                                    server_id=server['id'],
                                    device=device))
        except Exception as e:
            raise OpenStackCloudException(
                "Error attaching volume %s to server %s: %s" %
                (volume['id'], server['id'], e)
            )

        if wait:
            for count in _utils._iterate_timeout(
                    timeout,
                    "Timeout waiting for volume %s to attach." % volume['id']):
                try:
                    vol = self.get_volume(volume['id'])
                except Exception:
                    self.log.debug(
                        "Error getting volume info %s" % volume['id'],
                        exc_info=True)
                    continue

                if self.get_volume_attach_device(vol, server['id']):
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
            return server['id']
        return None

    def get_server_private_ip(self, server):
        return meta.get_server_private_ip(server, self)

    def get_server_public_ip(self, server):
        return meta.get_server_external_ipv4(self, server)

    def get_server_meta(self, server):
        # TODO(mordred) remove once ansible has moved to Inventory interface
        server_vars = meta.get_hostvars_from_server(self, server)
        groups = meta.get_groups_from_server(self, server, server_vars)
        return dict(server_vars=server_vars, groups=groups)

    def get_openstack_vars(self, server):
        return meta.get_hostvars_from_server(self, server)

    def available_floating_ip(self, network=None):
        """Get a floating IP from a network or a pool.

        Return the first available floating IP or allocate a new one.

        :param network: Nova pool name or Neutron network name or id.

        :returns: a (normalized) structure with a floating IP address
                  description.
        """
        if self.has_service('network'):
            try:
                f_ips = _utils.normalize_neutron_floating_ips(
                    self._neutron_available_floating_ips(
                        network=network))
                return f_ips[0]
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'{msg}'. Trying with Nova.".format(msg=str(e)))
                # Fall-through, trying with Nova

        f_ips = _utils.normalize_nova_floating_ips(
            self._nova_available_floating_ips(pool=network)
        )
        return f_ips[0]

    def _neutron_available_floating_ips(self, network=None, project_id=None):
        """Get a floating IP from a Neutron network.

        Return a list of available floating IPs or allocate a new one and
        return it in a list of 1 element.

        :param network: Nova pool name or Neutron network name or id.

        :returns: a list of floating IP addresses.

        :raises: ``OpenStackCloudResourceNotFound``, if an external network
                 that meets the specified criteria cannot be found.
        """
        if project_id is None:
            # Make sure we are only listing floatingIPs allocated the current
            # tenant. This is the default behaviour of Nova
            project_id = self.keystone_session.get_project_id()

        with self._neutron_exceptions("unable to get available floating IPs"):
            networks = self.search_networks(
                name_or_id=network,
                filters={'router:external': True})
            if not networks:
                raise OpenStackCloudResourceNotFound(
                    "unable to find an external network")

            filters = {
                'port_id': None,
                'floating_network_id': networks[0]['id'],
                'tenant_id': project_id

            }
            floating_ips = self._neutron_list_floating_ips()
            available_ips = _utils._filter_list(
                floating_ips, name_or_id=None, filters=filters)
            if available_ips:
                return available_ips

            # No available IP found, allocate a new Floating IP
            f_ip = self._neutron_create_floating_ip(
                network_name_or_id=networks[0]['id'])

            return [f_ip]

    def _nova_available_floating_ips(self, pool=None):
        """Get available floating IPs from a floating IP pool.

        Return a list of available floating IPs or allocate a new one and
        return it in a list of 1 element.

        :param pool: Nova floating IP pool name.

        :returns: a list of floating IP addresses.

        :raises: ``OpenStackCloudResourceNotFound``, if a floating IP pool
                 is not specified and cannot be found.
        """

        try:
            if pool is None:
                pools = self.list_floating_ip_pools()
                if not pools:
                    raise OpenStackCloudResourceNotFound(
                        "unable to find a floating ip pool")
                pool = pools[0]['name']

            filters = {
                'instance_id': None,
                'pool': pool
            }

            floating_ips = self._nova_list_floating_ips()
            available_ips = _utils._filter_list(
                floating_ips, name_or_id=None, filters=filters)
            if available_ips:
                return available_ips

            # No available IP found, allocate a new Floating IP
            f_ip = self._nova_create_floating_ip(pool=pool)

            return [f_ip]

        except Exception as e:
            raise OpenStackCloudException(
                "unable to create floating IP in pool {pool}: {msg}".format(
                    pool=pool, msg=str(e)))

    def create_floating_ip(self, network=None):
        """Allocate a new floating IP from a network or a pool.

        :param network: Nova pool name or Neutron network name or id.

        :returns: a floating IP address

        :raises: ``OpenStackCloudException``, on operation error.
        """
        if self.has_service('network'):
            try:
                f_ips = _utils.normalize_neutron_floating_ips(
                    [self._neutron_create_floating_ip(
                        network_name_or_id=network)]
                )
                return f_ips[0]
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'{msg}'. Trying with Nova.".format(msg=str(e)))
                # Fall-through, trying with Nova

        # Else, we are using Nova network
        f_ips = _utils.normalize_nova_floating_ips(
            [self._nova_create_floating_ip(pool=network)])
        return f_ips[0]

    def _neutron_create_floating_ip(self, network_name_or_id=None):
        with self._neutron_exceptions(
                "unable to create floating IP for net "
                "{0}".format(network_name_or_id)):
            networks = self.search_networks(
                name_or_id=network_name_or_id,
                filters={'router:external': True})
            if not networks:
                raise OpenStackCloudResourceNotFound(
                    "unable to find an external network with id "
                    "{0}".format(network_name_or_id or "(no id specified)"))
            kwargs = {
                'floating_network_id': networks[0]['id'],
            }
            return self.manager.submitTask(_tasks.NeutronFloatingIPCreate(
                body={'floatingip': kwargs}))['floatingip']

    def _nova_create_floating_ip(self, pool=None):
        try:
            if pool is None:
                pools = self.list_floating_ip_pools()
                if not pools:
                    raise OpenStackCloudResourceNotFound(
                        "unable to find a floating ip pool")
                pool = pools[0]['name']

            pool_ip = self.manager.submitTask(
                _tasks.NovaFloatingIPCreate(pool=pool))
            return meta.obj_to_dict(pool_ip)

        except Exception as e:
            raise OpenStackCloudException(
                "unable to create floating IP in pool {pool}: {msg}".format(
                    pool=pool, msg=str(e)))

    def delete_floating_ip(self, floating_ip_id):
        """Deallocate a floating IP from a tenant.

        :param floating_ip_id: a floating IP address id.

        :returns: True if the IP address has been deleted, False if the IP
                  address was not found.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        if self.has_service('network'):
            try:
                return self._neutron_delete_floating_ip(floating_ip_id)
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'{msg}'. Trying with Nova.".format(msg=str(e)))
                # Fall-through, trying with Nova

        # Else, we are using Nova network
        return self._nova_delete_floating_ip(floating_ip_id)

    def _neutron_delete_floating_ip(self, floating_ip_id):
        try:
            with self._neutron_exceptions("unable to delete floating IP"):
                self.manager.submitTask(
                    _tasks.NeutronFloatingIPDelete(floatingip=floating_ip_id))
        except OpenStackCloudResourceNotFound:
            return False

        return True

    def _nova_delete_floating_ip(self, floating_ip_id):
        try:
            self.manager.submitTask(
                _tasks.NovaFloatingIPDelete(floating_ip=floating_ip_id))
        except nova_exceptions.NotFound:
            return False
        except Exception as e:
            raise OpenStackCloudException(
                "unable to delete floating IP id {fip_id}: {msg}".format(
                    fip_id=floating_ip_id, msg=str(e)))

        return True

    def attach_ip_to_server(
            self, server_id, floating_ip_id, fixed_address=None, wait=False,
            timeout=60):
        """Attach a floating IP to a server.

        :param server_id: id of a server.
        :param floating_ip_id: id of the floating IP to attach.
        :param fixed_address: (optional) fixed address to which attach the
                              floating IP to.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server in Nova. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.

        :returns: None

        :raises: OpenStackCloudException, on operation error.
        """
        if self.has_service('network'):
            try:
                self._neutron_attach_ip_to_server(
                    server_id=server_id, floating_ip_id=floating_ip_id,
                    fixed_address=fixed_address)
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'{msg}'. Trying with Nova.".format(msg=str(e)))
                # Fall-through, trying with Nova
        else:
            # Nova network
            self._nova_attach_ip_to_server(
                server_id=server_id, floating_ip_id=floating_ip_id,
                fixed_address=fixed_address)

        if wait:
            # Wait for the address to be assigned to the server
            f_ip = self.get_floating_ip(id=floating_ip_id)
            for _ in _utils._iterate_timeout(
                    timeout,
                    "Timeout waiting for the floating IP to be attached."):
                server = self.get_server(name_or_id=server_id)
                for k, v in server['addresses'].items():
                    for interface_spec in v:
                        if interface_spec['addr'] == \
                                f_ip['floating_ip_address']:
                            return

    def _neutron_attach_ip_to_server(self, server_id, floating_ip_id,
                                     fixed_address=None):
        with self._neutron_exceptions(
                "unable to bind a floating ip to server "
                "{0}".format(server_id)):
            # Find an available port
            ports = self.search_ports(filters={'device_id': server_id})
            port = None
            if ports and fixed_address is None:
                port = ports[0]
                # Select the first available IPv4 address
                for address in port.get('fixed_ips', list()):
                    if _utils.is_ipv4(address['ip_address']):
                        fixed_address = address['ip_address']
                        break
                if fixed_address is None:
                    raise OpenStackCloudException(
                        "unable to find a suitable IPv4 address for server "
                        "{0}".format(server_id))
            elif ports:
                # unfortunately a port can have more than one fixed IP:
                # we can't use the search_ports filtering for fixed_address as
                # they are contained in a list. e.g.
                #
                #   "fixed_ips": [
                #     {
                #       "subnet_id": "008ba151-0b8c-4a67-98b5-0d2b87666062",
                #       "ip_address": "172.24.4.2"
                #     }
                #   ]
                #
                # Search fixed_address
                for p in ports:
                    for fixed_ip in p['fixed_ips']:
                        if fixed_address == fixed_ip['ip_address']:
                            port = p
                            break
                    else:
                        continue
                    break

            if not port:
                raise OpenStackCloudException(
                    "unable to find a port for server {0}".format(server_id))

            floating_ip = {'port_id': port['id']}
            if fixed_address is not None:
                floating_ip['fixed_ip_address'] = fixed_address

            return self.manager.submitTask(_tasks.NeutronFloatingIPUpdate(
                floatingip=floating_ip_id,
                body={'floatingip': floating_ip}
            ))['floatingip']

    def _nova_attach_ip_to_server(self, server_id, floating_ip_id,
                                  fixed_address=None):
        try:
            f_ip = self.get_floating_ip(id=floating_ip_id)
            return self.manager.submitTask(_tasks.NovaFloatingIPAttach(
                server=server_id, address=f_ip['floating_ip_address'],
                fixed_address=fixed_address))
        except Exception as e:
            raise OpenStackCloudException(
                "error attaching IP {ip} to instance {id}: {msg}".format(
                    ip=floating_ip_id, id=server_id, msg=str(e)))

    def detach_ip_from_server(self, server_id, floating_ip_id):
        """Detach a floating IP from a server.

        :param server_id: id of a server.
        :param floating_ip_id: Id of the floating IP to detach.

        :returns: True if the IP has been detached, or False if the IP wasn't
                  attached to any server.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        if self.has_service('network'):
            try:
                return self._neutron_detach_ip_from_server(
                    server_id=server_id, floating_ip_id=floating_ip_id)
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'{msg}'. Trying with Nova.".format(msg=str(e)))
                # Fall-through, trying with Nova

        # Nova network
        self._nova_detach_ip_from_server(
            server_id=server_id, floating_ip_id=floating_ip_id)

    def _neutron_detach_ip_from_server(self, server_id, floating_ip_id):
        with self._neutron_exceptions(
                "unable to detach a floating ip from server "
                "{0}".format(server_id)):
            f_ip = self.get_floating_ip(id=floating_ip_id)
            if f_ip is None or not f_ip['attached']:
                return False
            self.manager.submitTask(_tasks.NeutronFloatingIPUpdate(
                floatingip=floating_ip_id,
                body={'floatingip': {'port_id': None}}))

            return True

    def _nova_detach_ip_from_server(self, server_id, floating_ip_id):
        try:
            f_ip = self.get_floating_ip(id=floating_ip_id)
            if f_ip is None:
                raise OpenStackCloudException(
                    "unable to find floating IP {0}".format(floating_ip_id))
            self.manager.submitTask(_tasks.NovaFloatingIPDetach(
                server=server_id, address=f_ip['floating_ip_address']))
        except nova_exceptions.Conflict as e:
            self.log.debug(
                "nova floating IP detach failed: {msg}".format(msg=str(e)),
                exc_info=True)
            return False
        except Exception as e:
            raise OpenStackCloudException(
                "error detaching IP {ip} from instance {id}: {msg}".format(
                    ip=floating_ip_id, id=server_id, msg=str(e)))

        return True

    def add_ip_from_pool(self, server_id, network, fixed_address=None):
        """Add a floating IP to a sever from a given pool

        This method reuses available IPs, when possible, or allocate new IPs
        to the current tenant.
        The floating IP is attached to the given fixed address or to the
        first server port/fixed address

        :param server_id: Id of a server
        :param network: Nova pool name or Neutron network name or id.
        :param fixed_address: a fixed address

        :returns: the floating IP assigned
        """
        f_ip = self.available_floating_ip(network=network)

        self.attach_ip_to_server(
            server_id=server_id, floating_ip_id=f_ip['id'],
            fixed_address=fixed_address)

        return f_ip

    def add_ip_list(self, server, ips):
        """Attach a list of IPs to a server.

        :param server: a server object
        :param ips: list of IP addresses (floating IPs)

        :returns: None

        :raises: ``OpenStackCloudException``, on operation error.
        """
        # ToDo(dguerri): this makes no sense as we cannot attach multiple
        # floating IPs to a single fixed_address (this is true for both
        # neutron and nova). I will leave this here for the moment as we are
        # refactoring floating IPs methods.
        for ip in ips:
            f_ip = self.get_floating_ip(
                id=None, filters={'floating_ip_address': ip})
            self.attach_ip_to_server(
                server_id=server['id'], floating_ip_id=f_ip['id'])

    def add_auto_ip(self, server, wait=False, timeout=60):
        """Add a floating IP to a server.

        This method is intended for basic usage. For advanced network
        architecture (e.g. multiple external networks or servers with multiple
        interfaces), use other floating IP methods.

        This method reuses available IPs, when possible, or allocate new IPs
        to the current tenant.

        :param server: a server dictionary.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server in Nova. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.

        :returns: Floating IP address attached to server.

        """
        f_ip = self.available_floating_ip()
        self.attach_ip_to_server(
            server_id=server['id'], floating_ip_id=f_ip['id'], wait=wait,
            timeout=timeout)

        return self.get_floating_ip(id=f_ip['id'])

    def add_ips_to_server(
            self, server, auto_ip=True, ips=None, ip_pool=None,
            wait=False, timeout=60):
        if ip_pool:
            self.add_ip_from_pool(server['id'], ip_pool)
        elif ips:
            self.add_ip_list(server, ips)
        elif auto_ip:
            if self.get_server_public_ip(server):
                return server
            self.add_auto_ip(server, wait=wait, timeout=timeout)
        else:
            return server

        # this may look redundant, but if there is now a
        # floating IP, then it needs to be obtained from
        # a recent server object if the above code path exec'd
        try:
            server = meta.obj_to_dict(
                self.manager.submitTask(_tasks.ServerGet(server=server)))
        except Exception as e:
            raise OpenStackCloudException(
                "Error in getting info from instance: %s " % str(e))
        return server

    def create_server(self, auto_ip=True, ips=None, ip_pool=None,
                      root_volume=None, terminate_volume=False,
                      wait=False, timeout=180, **bootkwargs):
        """Create a virtual server instance.

        :returns: A dict representing the created server.
        :raises: OpenStackCloudException on operation error.
        """
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
            raise OpenStackCloudException(
                "Error in creating instance: {0}".format(e))
        if server.status == 'ERROR':
            raise OpenStackCloudException(
                "Error in creating the server.")
        if wait:
            for count in _utils._iterate_timeout(
                    timeout,
                    "Timeout waiting for the server to come up."):
                try:
                    server = meta.obj_to_dict(
                        self.manager.submitTask(
                            _tasks.ServerGet(server=server))
                    )
                except Exception:
                    continue

                if server['status'] == 'ACTIVE':
                    if not server['addresses']:
                        self.log.debug(
                            'Server {server} reached ACTIVE state without'
                            ' being allocated an IP address.'
                            ' Deleting server.'.format(
                                server=server['id']))
                        try:
                            self._delete_server(
                                server=server, wait=wait, timeout=timeout)
                        except Exception as e:
                            self.log.debug(
                                "Failed deleting server {server} that booted"
                                " without an IP address. Manual cleanup is"
                                " required.".format(server=server['id']),
                                exc_info=True)
                            raise OpenStackCloudException(
                                "Server reached ACTIVE state without being"
                                " allocated an IP address AND then could not"
                                " be deleted: {0}".format(e),
                                extra_data=dict(server=server))
                        raise OpenStackCloudException(
                            'Server reached ACTIVE state without being'
                            ' allocated an IP address.',
                            extra_data=dict(server=server))
                    return self.add_ips_to_server(
                        server, auto_ip, ips, ip_pool)

                if server['status'] == 'ERROR':
                    raise OpenStackCloudException(
                        "Error in creating the server",
                        extra_data=dict(server=server))
        return meta.obj_to_dict(server)

    def rebuild_server(self, server_id, image_id, wait=False, timeout=180):
        try:
            server = self.manager.submitTask(_tasks.ServerRebuild(
                server=server_id, image=image_id))
        except Exception as e:
            raise OpenStackCloudException(
                "Error in rebuilding instance: {0}".format(e))
        if wait:
            for count in _utils._iterate_timeout(
                    timeout,
                    "Timeout waiting for server {0} to "
                    "rebuild.".format(server_id)):
                try:
                    server = meta.obj_to_dict(
                        self.manager.submitTask(
                            _tasks.ServerGet(server=server))
                    )
                except Exception:
                    continue

                if server['status'] == 'ACTIVE':
                    return server

                if server['status'] == 'ERROR':
                    raise OpenStackCloudException(
                        "Error in rebuilding the server",
                        extra_data=dict(server=server))
        return meta.obj_to_dict(server)

    def delete_server(self, name_or_id, wait=False, timeout=180):
        server = self.get_server(name_or_id)
        return self._delete_server(server, wait=wait, timeout=timeout)

    def _delete_server(self, server, wait=False, timeout=180):
        if server:
            try:
                self.manager.submitTask(
                    _tasks.ServerDelete(server=server['id']))
            except nova_exceptions.NotFound:
                return
            except Exception as e:
                raise OpenStackCloudException(
                    "Error in deleting server: {0}".format(e))
        else:
            return
        if not wait:
            return
        for count in _utils._iterate_timeout(
                timeout,
                "Timed out waiting for server to get deleted."):
            try:
                server = self.manager.submitTask(
                    _tasks.ServerGet(server=server['id']))
                if not server:
                    return
                server = meta.obj_to_dict(server)
            except nova_exceptions.NotFound:
                return
            except Exception as e:
                raise OpenStackCloudException(
                    "Error in deleting server: {0}".format(e))

    def get_container(self, name, skip_cache=False):
        if skip_cache or name not in self._container_cache:
            try:
                container = self.manager.submitTask(
                    _tasks.ContainerGet(container=name))
                self._container_cache[name] = container
            except swift_exceptions.ClientException as e:
                if e.http_status == 404:
                    return None
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
            raise OpenStackCloudException(
                "Container deletion failed: %s (%s/%s)" % (
                    e.http_reason, e.http_host, e.http_path))

    def update_container(self, name, headers):
        try:
            self.manager.submitTask(
                _tasks.ContainerUpdate(container=name, headers=headers))
        except swift_exceptions.ClientException as e:
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

    @_cache_on_arguments()
    def get_object_capabilities(self):
        return self.manager.submitTask(_tasks.ObjectCapabilities())

    def get_object_segment_size(self, segment_size):
        '''get a segment size that will work given capabilities'''
        if segment_size is None:
            segment_size = DEFAULT_OBJECT_SEGMENT_SIZE
        try:
            caps = self.get_object_capabilities()
        except swift_exceptions.ClientException as e:
            if e.http_status == 412:
                server_max_file_size = DEFAULT_MAX_FILE_SIZE
                self.log.info(
                    "Swift capabilities not supported. "
                    "Using default max file size.")
            else:
                raise OpenStackCloudException(
                    "Could not determine capabilities")
        else:
            server_max_file_size = caps.get('swift', {}).get('max_file_size',
                                                             0)

        if segment_size > server_max_file_size:
            return server_max_file_size
        return segment_size

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
            md5=None, sha256=None, segment_size=None,
            **headers):
        """Create a file object

        :param container: The name of the container to store the file in.
            This container will be created if it does not exist already.
        :param name: Name for the object within the container.
        :param filename: The path to the local file whose contents will be
            uploaded.
        :param md5: A hexadecimal md5 of the file. (Optional), if it is known
            and can be passed here, it will save repeating the expensive md5
            process. It is assumed to be accurate.
        :param sha256: A hexadecimal sha256 of the file. (Optional) See md5.
        :param segment_size: Break the uploaded object into segments of this
            many bytes. (Optional) Shade will attempt to discover the maximum
            value for this from the server if it is not specified, or will use
            a reasonable default.
        :param headers: These will be passed through to the object creation
            API as HTTP Headers.

        :raises: ``OpenStackCloudException`` on operation error.
        """
        if not filename:
            filename = name

        segment_size = self.get_object_segment_size(segment_size)

        if not md5 or not sha256:
            (md5, sha256) = self._get_file_hashes(filename)
        headers[OBJECT_MD5_KEY] = md5
        headers[OBJECT_SHA256_KEY] = sha256
        header_list = sorted([':'.join([k, v]) for (k, v) in headers.items()])

        # On some clouds this is not necessary. On others it is. I'm confused.
        self.create_container(container)

        if self.is_object_stale(container, name, filename, md5, sha256):
            self.log.debug(
                "swift uploading {filename} to {container}/{name}".format(
                    filename=filename, container=container, name=name))
            upload = swift_service.SwiftUploadObject(source=filename,
                                                     object_name=name)
            for r in self.manager.submitTask(_tasks.ObjectCreate(
                container=container, objects=[upload],
                options=dict(header=header_list,
                             segment_size=segment_size))):
                if not r['success']:
                    raise OpenStackCloudException(
                        'Failed at action ({action}) [{error}]:'.format(**r))

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

        with self._neutron_exceptions(
                "Error creating subnet on network "
                "{0}".format(network_name_or_id)):
            new_subnet = self.manager.submitTask(
                _tasks.SubnetCreate(body=dict(subnet=subnet)))

        return new_subnet['subnet']

    def delete_subnet(self, name_or_id):
        """Delete a subnet.

        If a name, instead of a unique UUID, is supplied, it is possible
        that we could find more than one matching subnet since names are
        not required to be unique. An error will be raised in this case.

        :param name_or_id: Name or ID of the subnet being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        subnet = self.get_subnet(name_or_id)
        if not subnet:
            self.log.debug("Subnet %s not found for deleting" % name_or_id)
            return False

        with self._neutron_exceptions(
                "Error deleting subnet {0}".format(name_or_id)):
            self.manager.submitTask(
                _tasks.SubnetDelete(subnet=subnet['id']))
        return True

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

        with self._neutron_exceptions(
                "Error updating subnet {0}".format(name_or_id)):
            new_subnet = self.manager.submitTask(
                _tasks.SubnetUpdate(
                    subnet=curr_subnet['id'], body=dict(subnet=subnet)))
        # Turns out neutron returns an actual dict, so no need for the
        # use of meta.obj_to_dict() here (which would not work against
        # a dict).
        return new_subnet['subnet']

    @valid_kwargs('name', 'admin_state_up', 'mac_address', 'fixed_ips',
                  'subnet_id', 'ip_address', 'security_groups',
                  'allowed_address_pairs', 'extra_dhcp_opts', 'device_owner',
                  'device_id')
    def create_port(self, network_id, **kwargs):
        """Create a port

        :param network_id: The ID of the network. (Required)
        :param name: A symbolic name for the port. (Optional)
        :param admin_state_up: The administrative status of the port,
            which is up (true, default) or down (false). (Optional)
        :param mac_address: The MAC address. (Optional)
        :param fixed_ips: List of ip_addresses and subnet_ids. See subnet_id
            and ip_address. (Optional)
            For example::

              [
                {
                  "ip_address": "10.29.29.13",
                  "subnet_id": "a78484c4-c380-4b47-85aa-21c51a2d8cbd"
                }, ...
              ]
        :param subnet_id: If you specify only a subnet ID, OpenStack Networking
            allocates an available IP from that subnet to the port. (Optional)
            If you specify both a subnet ID and an IP address, OpenStack
            Networking tries to allocate the specified address to the port.
        :param ip_address: If you specify both a subnet ID and an IP address,
            OpenStack Networking tries to allocate the specified address to
            the port.
        :param security_groups: List of security group UUIDs. (Optional)
        :param allowed_address_pairs: Allowed address pairs list (Optional)
            For example::

              [
                {
                  "ip_address": "23.23.23.1",
                  "mac_address": "fa:16:3e:c4:cd:3f"
                }, ...
              ]
        :param extra_dhcp_opts: Extra DHCP options. (Optional).
            For example::

              [
                {
                  "opt_name": "opt name1",
                  "opt_value": "value1"
                }, ...
              ]
        :param device_owner: The ID of the entity that uses this port.
            For example, a DHCP agent.  (Optional)
        :param device_id: The ID of the device that uses this port.
            For example, a virtual server. (Optional)

        :returns: a dictionary describing the created port.

        :raises: ``OpenStackCloudException`` on operation error.
        """
        kwargs['network_id'] = network_id

        with self._neutron_exceptions(
                "Error creating port for network {0}".format(network_id)):
            return self.manager.submitTask(
                _tasks.PortCreate(body={'port': kwargs}))['port']

    @valid_kwargs('name', 'admin_state_up', 'fixed_ips', 'security_groups',
                  'allowed_address_pairs', 'extra_dhcp_opts', 'device_owner')
    def update_port(self, name_or_id, **kwargs):
        """Update a port

        Note: to unset an attribute use None value. To leave an attribute
        untouched just omit it.

        :param name_or_id: name or id of the port to update. (Required)
        :param name: A symbolic name for the port. (Optional)
        :param admin_state_up: The administrative status of the port,
            which is up (true) or down (false). (Optional)
        :param fixed_ips: List of ip_addresses and subnet_ids. (Optional)
            If you specify only a subnet ID, OpenStack Networking allocates
            an available IP from that subnet to the port.
            If you specify both a subnet ID and an IP address, OpenStack
            Networking tries to allocate the specified address to the port.
            For example::

              [
                {
                  "ip_address": "10.29.29.13",
                  "subnet_id": "a78484c4-c380-4b47-85aa-21c51a2d8cbd"
                }, ...
              ]
        :param security_groups: List of security group UUIDs. (Optional)
        :param allowed_address_pairs: Allowed address pairs list (Optional)
            For example::

              [
                {
                  "ip_address": "23.23.23.1",
                  "mac_address": "fa:16:3e:c4:cd:3f"
                }, ...
              ]
        :param extra_dhcp_opts: Extra DHCP options. (Optional).
            For example::

              [
                {
                  "opt_name": "opt name1",
                  "opt_value": "value1"
                }, ...
              ]
        :param device_owner: The ID of the entity that uses this port.
            For example, a DHCP agent.  (Optional)

        :returns: a dictionary describing the updated port.

        :raises: OpenStackCloudException on operation error.
        """
        port = self.get_port(name_or_id=name_or_id)
        if port is None:
            raise OpenStackCloudException(
                "failed to find port '{port}'".format(port=name_or_id))

        with self._neutron_exceptions(
                "Error updating port {0}".format(name_or_id)):
            return self.manager.submitTask(
                _tasks.PortUpdate(
                    port=port['id'], body={'port': kwargs}))['port']

    def delete_port(self, name_or_id):
        """Delete a port

        :param name_or_id: id or name of the port to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        port = self.get_port(name_or_id=name_or_id)
        if port is None:
            self.log.debug("Port %s not found for deleting" % name_or_id)
            return False

        with self._neutron_exceptions(
                "Error deleting port {0}".format(name_or_id)):
            self.manager.submitTask(_tasks.PortDelete(port=port['id']))
        return True

    def create_security_group(self, name, description):
        """Create a new security group

        :param string name: A name for the security group.
        :param string description: Describes the security group.

        :returns: A dict representing the new security group.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
                 not supported on this cloud.
        """
        if self.secgroup_source == 'neutron':
            with self._neutron_exceptions(
                    "Error creating security group {0}".format(name)):
                group = self.manager.submitTask(
                    _tasks.NeutronSecurityGroupCreate(
                        body=dict(security_group=dict(name=name,
                                                      description=description))
                    )
                )
            return group['security_group']

        elif self.secgroup_source == 'nova':
            try:
                group = meta.obj_to_dict(
                    self.manager.submitTask(
                        _tasks.NovaSecurityGroupCreate(
                            name=name, description=description
                        )
                    )
                )
            except Exception as e:
                raise OpenStackCloudException(
                    "failed to create security group '{name}': {msg}".format(
                        name=name, msg=str(e)))
            return _utils.normalize_nova_secgroups([group])[0]

        # Security groups not supported
        else:
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

    def delete_security_group(self, name_or_id):
        """Delete a security group

        :param string name_or_id: The name or unique ID of the security group.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
                 not supported on this cloud.
        """
        secgroup = self.get_security_group(name_or_id)
        if secgroup is None:
            self.log.debug('Security group %s not found for deleting' %
                           name_or_id)
            return False

        if self.secgroup_source == 'neutron':
            with self._neutron_exceptions(
                    "Error deleting security group {0}".format(name_or_id)):
                self.manager.submitTask(
                    _tasks.NeutronSecurityGroupDelete(
                        security_group=secgroup['id']
                    )
                )
            return True

        elif self.secgroup_source == 'nova':
            try:
                self.manager.submitTask(
                    _tasks.NovaSecurityGroupDelete(group=secgroup['id'])
                )
            except Exception as e:
                raise OpenStackCloudException(
                    "failed to delete security group '{group}': {msg}".format(
                        group=name_or_id, msg=str(e)))
            return True

        # Security groups not supported
        else:
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

    @valid_kwargs('name', 'description')
    def update_security_group(self, name_or_id, **kwargs):
        """Update a security group

        :param string name_or_id: Name or ID of the security group to update.
        :param string name: New name for the security group.
        :param string description: New description for the security group.

        :returns: A dictionary describing the updated security group.

        :raises: OpenStackCloudException on operation error.
        """
        secgroup = self.get_security_group(name_or_id)

        if secgroup is None:
            raise OpenStackCloudException(
                "Security group %s not found." % name_or_id)

        if self.secgroup_source == 'neutron':
            with self._neutron_exceptions(
                    "Error updating security group {0}".format(name_or_id)):
                group = self.manager.submitTask(
                    _tasks.NeutronSecurityGroupUpdate(
                        security_group=secgroup['id'],
                        body={'security_group': kwargs})
                )
            return group['security_group']

        elif self.secgroup_source == 'nova':
            try:
                group = meta.obj_to_dict(
                    self.manager.submitTask(
                        _tasks.NovaSecurityGroupUpdate(
                            group=secgroup['id'], **kwargs)
                    )
                )
            except Exception as e:
                raise OpenStackCloudException(
                    "failed to update security group '{group}': {msg}".format(
                        group=name_or_id, msg=str(e)))
            return _utils.normalize_nova_secgroups([group])[0]

        # Security groups not supported
        else:
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

    def create_security_group_rule(self,
                                   secgroup_name_or_id,
                                   port_range_min=None,
                                   port_range_max=None,
                                   protocol=None,
                                   remote_ip_prefix=None,
                                   remote_group_id=None,
                                   direction='ingress',
                                   ethertype='IPv4'):
        """Create a new security group rule

        :param string secgroup_name_or_id:
            The security group name or ID to associate with this security
            group rule. If a non-unique group name is given, an exception
            is raised.
        :param int port_range_min:
            The minimum port number in the range that is matched by the
            security group rule. If the protocol is TCP or UDP, this value
            must be less than or equal to the port_range_max attribute value.
            If nova is used by the cloud provider for security groups, then
            a value of None will be transformed to -1.
        :param int port_range_max:
            The maximum port number in the range that is matched by the
            security group rule. The port_range_min attribute constrains the
            port_range_max attribute. If nova is used by the cloud provider
            for security groups, then a value of None will be transformed
            to -1.
        :param string protocol:
            The protocol that is matched by the security group rule. Valid
            values are None, tcp, udp, and icmp.
        :param string remote_ip_prefix:
            The remote IP prefix to be associated with this security group
            rule. This attribute matches the specified IP prefix as the
            source IP address of the IP packet.
        :param string remote_group_id:
            The remote group ID to be associated with this security group
            rule.
        :param string direction:
            Ingress or egress: The direction in which the security group
            rule is applied. For a compute instance, an ingress security
            group rule is applied to incoming (ingress) traffic for that
            instance. An egress rule is applied to traffic leaving the
            instance.
        :param string ethertype:
            Must be IPv4 or IPv6, and addresses represented in CIDR must
            match the ingress or egress rules.

        :returns: A dict representing the new security group rule.

        :raises: OpenStackCloudException on operation error.
        """

        secgroup = self.get_security_group(secgroup_name_or_id)
        if not secgroup:
            raise OpenStackCloudException(
                "Security group %s not found." % secgroup_name_or_id)

        if self.secgroup_source == 'neutron':
            # NOTE: Nova accepts -1 port numbers, but Neutron accepts None
            # as the equivalent value.
            rule_def = {
                'security_group_id': secgroup['id'],
                'port_range_min':
                    None if port_range_min == -1 else port_range_min,
                'port_range_max':
                    None if port_range_max == -1 else port_range_max,
                'protocol': protocol,
                'remote_ip_prefix': remote_ip_prefix,
                'remote_group_id': remote_group_id,
                'direction': direction,
                'ethertype': ethertype
            }

            with self._neutron_exceptions(
                    "Error creating security group rule"):
                rule = self.manager.submitTask(
                    _tasks.NeutronSecurityGroupRuleCreate(
                        body={'security_group_rule': rule_def})
                )
            return rule['security_group_rule']

        elif self.secgroup_source == 'nova':
            # NOTE: Neutron accepts None for protocol. Nova does not.
            if protocol is None:
                raise OpenStackCloudException('Protocol must be specified')

            if direction == 'egress':
                self.log.debug(
                    'Rule creation failed: Nova does not support egress rules'
                )
                raise OpenStackCloudException('No support for egress rules')

            # NOTE: Neutron accepts None for ports, but Nova requires -1
            # as the equivalent value for ICMP.
            #
            # For TCP/UDP, if both are None, Neutron allows this and Nova
            # represents this as all ports (1-65535). Nova does not accept
            # None values, so to hide this difference, we will automatically
            # convert to the full port range. If only a single port value is
            # specified, it will error as normal.
            if protocol == 'icmp':
                if port_range_min is None:
                    port_range_min = -1
                if port_range_max is None:
                    port_range_max = -1
            elif protocol in ['tcp', 'udp']:
                if port_range_min is None and port_range_max is None:
                    port_range_min = 1
                    port_range_max = 65535

            try:
                rule = meta.obj_to_dict(
                    self.manager.submitTask(
                        _tasks.NovaSecurityGroupRuleCreate(
                            parent_group_id=secgroup['id'],
                            ip_protocol=protocol,
                            from_port=port_range_min,
                            to_port=port_range_max,
                            cidr=remote_ip_prefix,
                            group_id=remote_group_id
                        )
                    )
                )
            except Exception as e:
                raise OpenStackCloudException(
                    "failed to create security group rule: {msg}".format(
                        msg=str(e)))
            return _utils.normalize_nova_secgroup_rules([rule])[0]

        # Security groups not supported
        else:
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

    def delete_security_group_rule(self, rule_id):
        """Delete a security group rule

        :param string rule_id: The unique ID of the security group rule.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
                 not supported on this cloud.
        """

        if self.secgroup_source == 'neutron':
            try:
                with self._neutron_exceptions(
                        "Error deleting security group rule "
                        "{0}".format(rule_id)):
                    self.manager.submitTask(
                        _tasks.NeutronSecurityGroupRuleDelete(
                            security_group_rule=rule_id)
                    )
            except OpenStackCloudResourceNotFound:
                return False
            return True

        elif self.secgroup_source == 'nova':
            try:
                self.manager.submitTask(
                    _tasks.NovaSecurityGroupRuleDelete(rule=rule_id)
                )
            except nova_exceptions.NotFound:
                return False
            except Exception as e:
                raise OpenStackCloudException(
                    "failed to delete security group rule {id}: {msg}".format(
                        id=rule_id, msg=str(e)))
            return True

        # Security groups not supported
        else:
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )


class OperatorCloud(OpenStackCloud):
    """Represent a privileged/operator connection to an OpenStack Cloud.

    `OperatorCloud` is the entry point for all admin operations, regardless
    of which OpenStack service those operations are for.

    See the :class:`OpenStackCloud` class for a description of most options.
    """

    # Set the ironic API microversion to a known-good
    # supported/tested with the contents of shade.
    #
    # Note(TheJulia): Defaulted to version 1.6 as the ironic
    # state machine changes which will increment the version
    # and break an automatic transition of an enrolled node
    # to an available state. Locking the version is intended
    # to utilize the original transition until shade supports
    # calling for node inspection to allow the transition to
    # take place automatically.
    ironic_api_microversion = '1.6'

    @property
    def ironic_client(self):
        if self._ironic_client is None:
            self._ironic_client = self._get_client(
                'baremetal', ironic_client.Client,
                os_ironic_api_version=self.ironic_api_microversion)
        return self._ironic_client

    def list_nics(self):
        try:
            return meta.obj_list_to_dict(
                self.manager.submitTask(_tasks.MachinePortList())
            )
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching machine port list: %s" % e)

    def list_nics_for_machine(self, uuid):
        try:
            return meta.obj_list_to_dict(
                self.manager.submitTask(
                    _tasks.MachineNodePortList(node_id=uuid))
            )
        except Exception as e:
            raise OpenStackCloudException(
                "Error fetching port list for node %s: %s" % (uuid, e))

    def get_nic_by_mac(self, mac):
        try:
            return meta.obj_to_dict(
                self.manager.submitTask(
                    _tasks.MachineNodePortGet(port_id=mac))
            )
        except ironic_exceptions.ClientException:
            return None

    def list_machines(self):
        return meta.obj_list_to_dict(
            self.manager.submitTask(_tasks.MachineNodeList())
        )

    def get_machine(self, name_or_id):
        """Get Machine by name or uuid

        Search the baremetal host out by utilizing the supplied id value
        which can consist of a name or UUID.

        :param name_or_id: A node name or UUID that will be looked up.

        :returns: Dictonary representing the node found or None if no nodes
                  are found.
        """
        try:
            return meta.obj_to_dict(
                self.manager.submitTask(
                    _tasks.MachineNodeGet(node_id=name_or_id))
            )
        except ironic_exceptions.ClientException:
            return None

    def get_machine_by_mac(self, mac):
        """Get machine by port MAC address

        :param mac: Port MAC address to query in order to return a node.

        :returns: Dictonary representing the node found or None
                  if the node is not found.
        """
        try:
            port = self.manager.submitTask(
                _tasks.MachinePortGetByAddress(address=mac))
            return meta.obj_to_dict(
                self.manager.submitTask(
                    _tasks.MachineNodeGet(node_id=port.node_uuid))
            )
        except ironic_exceptions.ClientException:
            return None

    def register_machine(self, nics, wait=False, timeout=3600,
                         lock_timeout=600, **kwargs):
        """Register Baremetal with Ironic

        Allows for the registration of Baremetal nodes with Ironic
        and population of pertinant node information or configuration
        to be passed to the Ironic API for the node.

        This method also creates ports for a list of MAC addresses passed
        in to be utilized for boot and potentially network configuration.

        If a failure is detected creating the network ports, any ports
        created are deleted, and the node is removed from Ironic.

        :param list nics:
           An array of MAC addresses that represent the
           network interfaces for the node to be created.

           Example::

              [
                  {'mac': 'aa:bb:cc:dd:ee:01'},
                  {'mac': 'aa:bb:cc:dd:ee:02'}
              ]

        :param wait: Boolean value, defaulting to false, to wait for the
                     node to reach the available state where the node can be
                     provisioned. It must be noted, when set to false, the
                     method will still wait for locks to clear before sending
                     the next required command.

        :param timeout: Integer value, defautling to 3600 seconds, for the
                        wait state to reach completion.

        :param lock_timeout: Integer value, defaulting to 600 seconds, for
                             locks to clear.

        :param kwargs: Key value pairs to be passed to the Ironic API,
                       including uuid, name, chassis_uuid, driver_info,
                       parameters.

        :raises: OpenStackCloudException on operation error.

        :returns: Returns a dictonary representing the new
                  baremetal node.
        """
        try:
            machine = meta.obj_to_dict(
                self.manager.submitTask(_tasks.MachineCreate(**kwargs)))

        except Exception as e:
            raise OpenStackCloudException(
                "Error registering machine with Ironic: %s" % str(e))

        created_nics = []
        try:
            for row in nics:
                nic = self.manager.submitTask(
                    _tasks.MachinePortCreate(address=row['mac'],
                                             node_uuid=machine['uuid']))
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
                    _tasks.MachineDelete(node_id=machine['uuid']))
            raise OpenStackCloudException(
                "Error registering NICs with the baremetal service: %s"
                % str(e))

        try:
            if wait:
                for count in _utils._iterate_timeout(
                        timeout,
                        "Timeout waiting for node transition to "
                        "available state"):

                    machine = self.get_machine(machine['uuid'])

                    # Note(TheJulia): Per the Ironic state code, a node
                    # that fails returns to enroll state, which means a failed
                    # node cannot be determined at this point in time.
                    if machine['provision_state'] in ['enroll']:
                        self.node_set_provision_state(
                            machine['uuid'], 'manage')
                    elif machine['provision_state'] in ['manageable']:
                        self.node_set_provision_state(
                            machine['uuid'], 'provide')
                    elif machine['last_error'] is not None:
                        raise OpenStackCloudException(
                            "Machine encountered a failure: %s"
                            % machine['last_error'])

                    # Note(TheJulia): Earlier versions of Ironic default to
                    # None and later versions default to available up until
                    # the introduction of enroll state.
                    # Note(TheJulia): The node will transition through
                    # cleaning if it is enabled, and we will wait for
                    # completion.
                    elif machine['provision_state'] in ['available', None]:
                        break

            else:
                if machine['provision_state'] in ['enroll']:
                    self.node_set_provision_state(machine['uuid'], 'manage')
                    # Note(TheJulia): We need to wait for the lock to clear
                    # before we attempt to set the machine into provide state
                    # which allows for the transition to available.
                    for count in _utils._iterate_timeout(
                            lock_timeout,
                            "Timeout waiting for reservation to clear "
                            "before setting provide state"):
                        machine = self.get_machine(machine['uuid'])
                        if (machine['reservation'] is None and
                           machine['provision_state'] is not 'enroll'):

                            self.node_set_provision_state(
                                machine['uuid'], 'provide')
                            machine = self.get_machine(machine['uuid'])
                            break

                        elif machine['provision_state'] in [
                                'cleaning',
                                'available']:
                            break

                        elif machine['last_error'] is not None:
                            raise OpenStackCloudException(
                                "Machine encountered a failure: %s"
                                % machine['last_error'])

        except Exception as e:
            raise OpenStackCloudException(
                "Error transitioning node to available state: %s"
                % e)
        return machine

    def unregister_machine(self, nics, uuid, wait=False, timeout=600):
        """Unregister Baremetal from Ironic

        Removes entries for Network Interfaces and baremetal nodes
        from an Ironic API

        :param list nics: An array of strings that consist of MAC addresses
                          to be removed.
        :param string uuid: The UUID of the node to be deleted.

        :param wait: Boolean value, defaults to false, if to block the method
                     upon the final step of unregistering the machine.

        :param timeout: Integer value, representing seconds with a default
                        value of 600, which controls the maximum amount of
                        time to block the method's completion on.

        :raises: OpenStackCloudException on operation failure.
        """

        machine = self.get_machine(uuid)
        invalid_states = ['active', 'cleaning', 'clean wait', 'clean failed']
        if machine['provision_state'] in invalid_states:
            raise OpenStackCloudException(
                "Error unregistering node '%s' due to current provision "
                "state '%s'" % (uuid, machine['provision_state']))

        for nic in nics:
            try:
                port = self.manager.submitTask(
                    _tasks.MachinePortGetByAddress(address=nic['mac']))
                self.manager.submitTask(
                    _tasks.MachinePortDelete(port_id=port.uuid))
            except Exception as e:
                raise OpenStackCloudException(
                    "Error removing NIC '%s' from baremetal API for "
                    "node '%s'. Error: %s" % (nic, uuid, str(e)))
        try:
            self.manager.submitTask(
                _tasks.MachineDelete(node_id=uuid))
            if wait:
                for count in _utils._iterate_timeout(
                        timeout,
                        "Timeout waiting for machine to be deleted"):
                    if not self.get_machine(uuid):
                        break

        except Exception as e:
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
        :param patch:
           The JSON Patch document is a list of dictonary objects
           that comply with RFC 6902 which can be found at
           https://tools.ietf.org/html/rfc6902.

           Example patch construction::

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
            raise OpenStackCloudException(
                "Machine update failed - machine [%s] missing key %s. "
                "Potential API issue."
                % (name_or_id, e.args[0]))

        try:
            patch = jsonpatch.JsonPatch.from_diff(machine_config, new_config)
        except Exception as e:
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
            raise OpenStackCloudException(
                "Machine update failed - patch operation failed Machine: %s "
                "Error: %s" % (name_or_id, str(e)))

    def validate_node(self, uuid):
        try:
            ifaces = self.manager.submitTask(
                _tasks.MachineNodeValidate(node_uuid=uuid))
        except Exception as e:
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
            raise OpenStackCloudException(
                "Baremetal machine node failed change provision"
                " state to {state}: {msg}".format(state=state,
                                                  msg=str(e)))

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
                raise OpenStackCloudException(
                    "Failed setting machine maintenance state to %s "
                    "on node %s. Received: %s" % (
                        state, name_or_id, result))
            return None
        except Exception as e:
            raise OpenStackCloudException(
                "Error setting machine maintenance state to %s "
                "on node %s: %s" % (state, name_or_id, str(e)))

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
                raise OpenStackCloudException(
                    "Failed setting machine power state %s on node %s. "
                    "Received: %s" % (state, name_or_id, power))
            return None
        except Exception as e:
            raise OpenStackCloudException(
                "Error setting machine power state %s on node %s. "
                "Error: %s" % (state, name_or_id, str(e)))

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
                self.manager.submitTask(
                    _tasks.MachineNodeUpdate(node_id=uuid, patch=patch))
            )
        except Exception as e:
            raise OpenStackCloudException(str(e))

    def purge_node_instance_info(self, uuid):
        patch = []
        patch.append({'op': 'remove', 'path': '/instance_info'})
        try:
            return meta.obj_to_dict(
                self.manager.submitTask(
                    _tasks.MachineNodeUpdate(node_id=uuid, patch=patch))
            )
        except Exception as e:
            raise OpenStackCloudException(str(e))

    def create_service(self, name, service_type, description=None):
        """Create a service.

        :param name: Service name.
        :param service_type: Service type.
        :param description: Service description (optional).

        :returns: a dict containing the services description, i.e. the
            following attributes::
            - id: <service id>
            - name: <service name>
            - service_type: <service type>
            - description: <service description>

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.

        """
        try:
            service = self.manager.submitTask(_tasks.ServiceCreate(
                name=name, service_type=service_type,
                description=description))
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to create service {name}: {msg}".format(
                    name=name, msg=str(e)))
        return meta.obj_to_dict(service)

    def list_services(self):
        """List all Keystone services.

        :returns: a list of dict containing the services description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.
        """
        try:
            services = self.manager.submitTask(_tasks.ServiceList())
        except Exception as e:
            raise OpenStackCloudException(str(e))
        return meta.obj_list_to_dict(services)

    def search_services(self, name_or_id=None, filters=None):
        """Search Keystone services.

        :param name_or_id: Name or id of the desired service.
        :param filters: a dict containing additional filters to use. e.g.
                        {'service_type': 'network'}.

        :returns: a list of dict containing the services description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.
        """
        services = self.list_services()
        return _utils._filter_list(services, name_or_id, filters)

    def get_service(self, name_or_id, filters=None):
        """Get exactly one Keystone service.

        :param name_or_id: Name or id of the desired service.
        :param filters: a dict containing additional filters to use. e.g.
                {'service_type': 'network'}

        :returns: a dict containing the services description, i.e. the
            following attributes::
            - id: <service id>
            - name: <service name>
            - service_type: <service type>
            - description: <service description>

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call or if multiple matches are found.
        """
        return _utils._get_entity(self.search_services, name_or_id, filters)

    def delete_service(self, name_or_id):
        """Delete a Keystone service.

        :param name_or_id: Service name or id.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call
        """
        service = self.get_service(name_or_id=name_or_id)
        if service is None:
            self.log.debug("Service %s not found for deleting" % name_or_id)
            return False

        try:
            self.manager.submitTask(_tasks.ServiceDelete(id=service['id']))
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to delete service {id}: {msg}".format(
                    id=service['id'],
                    msg=str(e)))
        return True

    def create_endpoint(self, service_name_or_id, public_url,
                        internal_url=None, admin_url=None, region=None):
        """Create a Keystone endpoint.

        :param service_name_or_id: Service name or id for this endpoint.
        :param public_url: Endpoint public URL.
        :param internal_url: Endpoint internal URL.
        :param admin_url: Endpoint admin URL.
        :param region: Endpoint region.

        :returns: a dict containing the endpoint description.

        :raises: OpenStackCloudException if the service cannot be found or if
            something goes wrong during the openstack API call.
        """
        # ToDo: support v3 api (dguerri)
        service = self.get_service(name_or_id=service_name_or_id)
        if service is None:
            raise OpenStackCloudException("service {service} not found".format(
                service=service_name_or_id))
        try:
            endpoint = self.manager.submitTask(_tasks.EndpointCreate(
                service_id=service['id'],
                region=region,
                publicurl=public_url,
                internalurl=internal_url,
                adminurl=admin_url
            ))
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to create endpoint for service {service}: "
                "{msg}".format(service=service['name'],
                               msg=str(e)))
        return meta.obj_to_dict(endpoint)

    def list_endpoints(self):
        """List Keystone endpoints.

        :returns: a list of dict containing the endpoint description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        # ToDo: support v3 api (dguerri)
        try:
            endpoints = self.manager.submitTask(_tasks.EndpointList())
        except Exception as e:
            raise OpenStackCloudException("Failed to list endpoints: {msg}"
                                          .format(msg=str(e)))
        return meta.obj_list_to_dict(endpoints)

    def search_endpoints(self, id=None, filters=None):
        """List Keystone endpoints.

        :param id: endpoint id.
        :param filters: a dict containing additional filters to use. e.g.
                {'region': 'region-a.geo-1'}

        :returns: a list of dict containing the endpoint description. Each dict
            contains the following attributes::
            - id: <endpoint id>
            - region: <endpoint region>
            - public_url: <endpoint public url>
            - internal_url: <endpoint internal url> (optional)
            - admin_url: <endpoint admin url> (optional)

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        endpoints = self.list_endpoints()
        return _utils._filter_list(endpoints, id, filters)

    def get_endpoint(self, id, filters=None):
        """Get exactly one Keystone endpoint.

        :param id: endpoint id.
        :param filters: a dict containing additional filters to use. e.g.
                {'region': 'region-a.geo-1'}

        :returns: a dict containing the endpoint description. i.e. a dict
            containing the following attributes::
            - id: <endpoint id>
            - region: <endpoint region>
            - public_url: <endpoint public url>
            - internal_url: <endpoint internal url> (optional)
            - admin_url: <endpoint admin url> (optional)
        """
        return _utils._get_entity(self.search_endpoints, id, filters)

    def delete_endpoint(self, id):
        """Delete a Keystone endpoint.

        :param id: Id of the endpoint to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call.
        """
        # ToDo: support v3 api (dguerri)
        endpoint = self.get_endpoint(id=id)
        if endpoint is None:
            self.log.debug("Endpoint %s not found for deleting" % id)
            return False

        try:
            self.manager.submitTask(_tasks.EndpointDelete(id=id))
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to delete endpoint {id}: {msg}".format(
                    id=id,
                    msg=str(e)))
        return True

    def create_identity_domain(
            self, name, description=None, enabled=True):
        """Create a Keystone domain.

        :param name: The name of the domain.
        :param description: A description of the domain.
        :param enabled: Is the domain enabled or not (default True).

        :returns: a dict containing the domain description

        :raise OpenStackCloudException: if the domain cannot be created
        """
        try:
            domain = self.manager.submitTask(_tasks.IdentityDomainCreate(
                name=name,
                description=description,
                enabled=enabled))
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to create domain {name}".format(name=name,
                                                        msg=str(e)))
        return meta.obj_to_dict(domain)

    def update_identity_domain(
            self, domain_id, name=None, description=None, enabled=None):
        try:
            return meta.obj_to_dict(
                self.manager.submitTask(_tasks.IdentityDomainUpdate(
                    domain=domain_id, description=description,
                    enabled=enabled)))
        except Exception as e:
            raise OpenStackCloudException(
                "Error in updating domain {domain}: {message}".format(
                    domain=domain_id, message=str(e)))

    def delete_identity_domain(self, domain_id):
        """Delete a Keystone domain.

        :param domain_id: ID of the domain to delete.

        :returns: None

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call.
        """
        try:
            # Deleting a domain is expensive, so disabling it first increases
            # the changes of success
            domain = self.update_identity_domain(domain_id, enabled=False)
            self.manager.submitTask(_tasks.IdentityDomainDelete(
                domain=domain['id']))
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to delete domain {id}: {msg}".format(id=domain_id,
                                                             msg=str(e)))

    def list_identity_domains(self):
        """List Keystone domains.

        :returns: a list of dicts containing the domain description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        try:
            domains = self.manager.submitTask(_tasks.IdentityDomainList())
        except Exception as e:
            raise OpenStackCloudException("Failed to list domains: {msg}"
                                          .format(msg=str(e)))
        return meta.obj_list_to_dict(domains)

    def search_identity_domains(self, **filters):
        """Seach Keystone domains.

        :param filters: a dict containing additional filters to use.
                keys to search on are id, name, enabled and description.

        :returns: a list of dicts containing the domain description. Each dict
            contains the following attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        try:
            domains = self.manager.submitTask(
                _tasks.IdentityDomainList(**filters))
        except Exception as e:
            raise OpenStackCloudException("Failed to list domains: {msg}"
                                          .format(msg=str(e)))
        return meta.obj_list_to_dict(domains)

    def get_identity_domain(self, domain_id):
        """Get exactly one Keystone domain.

        :param domain_id: domain id.

        :returns: a dict containing the domain description, or None if not
            found. Each dict contains the following attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        try:
            domain = self.manager.submitTask(
                _tasks.IdentityDomainGet(domain=domain_id))
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to get domain {domain_id}: {msg}".format(
                    domain_id=domain_id,
                    msg=str(e)))
            raise OpenStackCloudException(str(e))
        return meta.obj_to_dict(domain)

    def create_flavor(self, name, ram, vcpus, disk, flavorid="auto",
                      ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True):
        """Create a new flavor.

        :param name: Descriptive name of the flavor
        :param ram: Memory in MB for the flavor
        :param vcpus: Number of VCPUs for the flavor
        :param disk: Size of local disk in GB
        :param flavorid: ID for the flavor (optional)
        :param ephemeral: Ephemeral space size in GB
        :param swap: Swap space in MB
        :param rxtx_factor: RX/TX factor
        :param is_public: Make flavor accessible to the public

        :returns: A dict describing the new flavor.

        :raises: OpenStackCloudException on operation error.
        """
        try:
            flavor = self.manager.submitTask(
                _tasks.FlavorCreate(name=name, ram=ram, vcpus=vcpus, disk=disk,
                                    flavorid=flavorid, ephemeral=ephemeral,
                                    swap=swap, rxtx_factor=rxtx_factor,
                                    is_public=is_public)
            )
        except Exception as e:
            raise OpenStackCloudException(
                "Failed to create flavor {name}: {msg}".format(
                    name=name,
                    msg=str(e)))
        return meta.obj_to_dict(flavor)

    def delete_flavor(self, name_or_id):
        """Delete a flavor

        :param name_or_id: ID or name of the flavor to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        flavor = self.get_flavor(name_or_id)
        if flavor is None:
            self.log.debug(
                "Flavor {0} not found for deleting".format(name_or_id))
            return False

        try:
            self.manager.submitTask(_tasks.FlavorDelete(flavor=flavor['id']))
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to delete flavor {0}: {1}".format(name_or_id, e)
            )

        return True

    def _mod_flavor_specs(self, action, flavor_id, specs):
        """Common method for modifying flavor extra specs.

        Nova (very sadly) doesn't expose this with a public API, so we
        must get the actual flavor object and make a method call on it.

        Two separate try-except blocks are used because Nova can raise
        a NotFound exception if FlavorGet() is given an invalid flavor ID,
        or if the unset_keys() method of the flavor object is given an
        invalid spec key. We need to be able to differentiate between these
        actions, thus the separate blocks.
        """
        try:
            flavor = self.manager.submitTask(
                _tasks.FlavorGet(flavor=flavor_id)
            )
        except nova_exceptions.NotFound:
            self.log.debug(
                "Flavor ID {0} not found. "
                "Cannot {1} extra specs.".format(flavor_id, action)
            )
            raise OpenStackCloudResourceNotFound(
                "Flavor ID {0} not found".format(flavor_id)
            )
        except Exception as e:
            raise OpenStackCloudException(
                "Error getting flavor ID {0}: {1}".format(flavor_id, e)
            )

        try:
            if action == 'set':
                flavor.set_keys(specs)
            elif action == 'unset':
                flavor.unset_keys(specs)
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to {0} flavor specs: {1}".format(action, e)
            )

    def set_flavor_specs(self, flavor_id, extra_specs):
        """Add extra specs to a flavor

        :param string flavor_id: ID of the flavor to update.
        :param dict extra_specs: Dictionary of key-value pairs.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        self._mod_flavor_specs('set', flavor_id, extra_specs)

    def unset_flavor_specs(self, flavor_id, keys):
        """Delete extra specs from a flavor

        :param string flavor_id: ID of the flavor to update.
        :param list keys: List of spec keys to delete.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        self._mod_flavor_specs('unset', flavor_id, keys)

    def _mod_flavor_access(self, action, flavor_id, project_id):
        """Common method for adding and removing flavor access
        """
        try:
            if action == 'add':
                self.manager.submitTask(
                    _tasks.FlavorAddAccess(flavor=flavor_id,
                                           tenant=project_id)
                )
            elif action == 'remove':
                self.manager.submitTask(
                    _tasks.FlavorRemoveAccess(flavor=flavor_id,
                                              tenant=project_id)
                )
        except Exception as e:
            raise OpenStackCloudException(
                "Error trying to {0} access from flavor ID {1}: {2}".format(
                    action, flavor_id, e)
            )

    def add_flavor_access(self, flavor_id, project_id):
        """Grant access to a private flavor for a project/tenant.

        :param string flavor_id: ID of the private flavor.
        :param string project_id: ID of the project/tenant.

        :raises: OpenStackCloudException on operation error.
        """
        self._mod_flavor_access('add', flavor_id, project_id)

    def remove_flavor_access(self, flavor_id, project_id):
        """Revoke access from a private flavor for a project/tenant.

        :param string flavor_id: ID of the private flavor.
        :param string project_id: ID of the project/tenant.

        :raises: OpenStackCloudException on operation error.
        """
        self._mod_flavor_access('remove', flavor_id, project_id)
