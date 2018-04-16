# Licensed under the Apache License, Version 3.0 (the "License");
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

import base64
import collections
import copy
import datetime
import functools
import hashlib
import ipaddress
import iso8601
import json
import jsonpatch
import operator
import os
import six
import threading
import time
# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import types  # noqa
import warnings

import dogpile.cache
import munch
import requestsexceptions
from six.moves import urllib

import keystoneauth1.exceptions
import keystoneauth1.session

from openstack import _adapter
from openstack import _log
from openstack.cloud.exc import *  # noqa
from openstack.cloud._heat import event_utils
from openstack.cloud._heat import template_utils
from openstack.cloud import _normalize
from openstack.cloud import meta
from openstack.cloud import _utils
import openstack.config
import openstack.config.defaults
from openstack import task_manager
from openstack import utils

# TODO(shade) shade keys were x-object-meta-x-sdk-md5 - we need to add those
#             to freshness checks so that a shade->sdk transition doens't
#             result in a re-upload
OBJECT_MD5_KEY = 'x-object-meta-x-sdk-md5'
OBJECT_SHA256_KEY = 'x-object-meta-x-sdk-sha256'
OBJECT_AUTOCREATE_KEY = 'x-object-meta-x-sdk-autocreated'
OBJECT_AUTOCREATE_CONTAINER = 'images'
# TODO(shade) shade keys were owner_specified.shade.md5 - we need to add those
#             to freshness checks so that a shade->sdk transition doens't
#             result in a re-upload
IMAGE_MD5_KEY = 'owner_specified.openstack.md5'
IMAGE_SHA256_KEY = 'owner_specified.openstack.sha256'
IMAGE_OBJECT_KEY = 'owner_specified.openstack.object'
# Rackspace returns this for intermittent import errors
IMAGE_ERROR_396 = "Image cannot be imported. Error code: '396'"
DEFAULT_OBJECT_SEGMENT_SIZE = 1073741824  # 1GB
# This halves the current default for Swift
DEFAULT_MAX_FILE_SIZE = (5 * 1024 * 1024 * 1024 + 2) / 2
DEFAULT_SERVER_AGE = 5
DEFAULT_PORT_AGE = 5
DEFAULT_FLOAT_AGE = 5
_OCC_DOC_URL = "https://docs.openstack.org/os-client-config/latest/"


OBJECT_CONTAINER_ACLS = {
    'public': '.r:*,.rlistings',
    'private': '',
}


def _no_pending_volumes(volumes):
    """If there are any volumes not in a steady state, don't cache"""
    for volume in volumes:
        if volume['status'] not in ('available', 'error', 'in-use'):
            return False
    return True


def _no_pending_images(images):
    """If there are any images not in a steady state, don't cache"""
    for image in images:
        if image.status not in ('active', 'deleted', 'killed'):
            return False
    return True


def _no_pending_stacks(stacks):
    """If there are any stacks not in a steady state, don't cache"""
    for stack in stacks:
        status = stack['stack_status']
        if '_COMPLETE' not in status and '_FAILED' not in status:
            return False
    return True


class OpenStackCloud(_normalize.Normalizer):
    """Represent a connection to an OpenStack Cloud.

    OpenStackCloud is the entry point for all cloud operations, regardless
    of which OpenStack service those operations may ultimately come from.
    The operations on an OpenStackCloud are resource oriented rather than
    REST API operation oriented. For instance, one will request a Floating IP
    and that Floating IP will be actualized either via neutron or via nova
    depending on how this particular cloud has decided to arrange itself.

    :param bool strict: Only return documented attributes for each resource
                        as per the Data Model contract. (Default False)
    """

    def __init__(self):

        self.log = _log.setup_logging('openstack')

        self.name = self.config.name
        self.auth = self.config.get_auth_args()
        self.default_interface = self.config.get_interface()
        self.private = self.config.config.get('private', False)
        self.image_api_use_tasks = self.config.config['image_api_use_tasks']
        self.secgroup_source = self.config.config['secgroup_source']
        self.force_ipv4 = self.config.force_ipv4

        self._external_ipv4_names = self.config.get_external_ipv4_networks()
        self._internal_ipv4_names = self.config.get_internal_ipv4_networks()
        self._external_ipv6_names = self.config.get_external_ipv6_networks()
        self._internal_ipv6_names = self.config.get_internal_ipv6_networks()
        self._nat_destination = self.config.get_nat_destination()
        self._default_network = self.config.get_default_network()

        self._floating_ip_source = self.config.config.get(
            'floating_ip_source')
        if self._floating_ip_source:
            if self._floating_ip_source.lower() == 'none':
                self._floating_ip_source = None
            else:
                self._floating_ip_source = self._floating_ip_source.lower()

        self._use_external_network = self.config.config.get(
            'use_external_network', True)
        self._use_internal_network = self.config.config.get(
            'use_internal_network', True)

        (self.verify, self.cert) = self.config.get_requests_verify_args()
        # Turn off urllib3 warnings about insecure certs if we have
        # explicitly configured requests to tell it we do not want
        # cert verification
        if not self.verify:
            self.log.debug(
                "Turning off Insecure SSL warnings since verify=False")
            category = requestsexceptions.InsecureRequestWarning
            if category:
                # InsecureRequestWarning references a Warning class or is None
                warnings.filterwarnings('ignore', category=category)

        self._disable_warnings = {}

        self._servers = None
        self._servers_time = 0
        self._servers_lock = threading.Lock()

        self._ports = None
        self._ports_time = 0
        self._ports_lock = threading.Lock()

        self._floating_ips = None
        self._floating_ips_time = 0
        self._floating_ips_lock = threading.Lock()

        self._floating_network_by_router = None
        self._floating_network_by_router_run = False
        self._floating_network_by_router_lock = threading.Lock()

        self._networks_lock = threading.Lock()
        self._reset_network_caches()

        cache_expiration_time = int(self.config.get_cache_expiration_time())
        cache_class = self.config.get_cache_class()
        cache_arguments = self.config.get_cache_arguments()

        self._resource_caches = {}

        if cache_class != 'dogpile.cache.null':
            self.cache_enabled = True
            self._cache = self._make_cache(
                cache_class, cache_expiration_time, cache_arguments)
            expirations = self.config.get_cache_expirations()
            for expire_key in expirations.keys():
                # Only build caches for things we have list operations for
                if getattr(
                        self, 'list_{0}'.format(expire_key), None):
                    self._resource_caches[expire_key] = self._make_cache(
                        cache_class, expirations[expire_key], cache_arguments)

            self._SERVER_AGE = DEFAULT_SERVER_AGE
            self._PORT_AGE = DEFAULT_PORT_AGE
            self._FLOAT_AGE = DEFAULT_FLOAT_AGE
        else:
            self.cache_enabled = False

            def _fake_invalidate(unused):
                pass

            class _FakeCache(object):
                def invalidate(self):
                    pass

            # Don't cache list_servers if we're not caching things.
            # Replace this with a more specific cache configuration
            # soon.
            self._SERVER_AGE = 0
            self._PORT_AGE = 0
            self._FLOAT_AGE = 0
            self._cache = _FakeCache()
            # Undecorate cache decorated methods. Otherwise the call stacks
            # wind up being stupidly long and hard to debug
            for method in _utils._decorated_methods:
                meth_obj = getattr(self, method, None)
                if not meth_obj:
                    continue
                if (hasattr(meth_obj, 'invalidate')
                        and hasattr(meth_obj, 'func')):
                    new_func = functools.partial(meth_obj.func, self)
                    new_func.invalidate = _fake_invalidate
                    setattr(self, method, new_func)

        # If server expiration time is set explicitly, use that. Otherwise
        # fall back to whatever it was before
        self._SERVER_AGE = self.config.get_cache_resource_expiration(
            'server', self._SERVER_AGE)
        self._PORT_AGE = self.config.get_cache_resource_expiration(
            'port', self._PORT_AGE)
        self._FLOAT_AGE = self.config.get_cache_resource_expiration(
            'floating_ip', self._FLOAT_AGE)

        self._container_cache = dict()
        self._file_hash_cache = dict()

        self._raw_clients = {}

        self._local_ipv6 = (
            _utils.localhost_supports_ipv6() if not self.force_ipv4 else False)

    def connect_as(self, **kwargs):
        """Make a new OpenStackCloud object with new auth context.

        Take the existing settings from the current cloud and construct a new
        OpenStackCloud object with some of the auth settings overridden. This
        is useful for getting an object to perform tasks with as another user,
        or in the context of a different project.

        .. code-block:: python

          conn = openstack.connect(cloud='example')
          # Work normally
          servers = conn.list_servers()
          conn2 = conn.connect_as(username='different-user', password='')
          # Work as different-user
          servers = conn2.list_servers()

        :param kwargs: keyword arguments can contain anything that would
                       normally go in an auth dict. They will override the same
                       settings from the parent cloud as appropriate. Entries
                       that do not want to be overridden can be ommitted.
        """

        if self.config._openstack_config:
            config = self.config._openstack_config
        else:
            # TODO(mordred) Replace this with from_session
            config = openstack.config.OpenStackConfig(
                app_name=self.config._app_name,
                app_version=self.config._app_version,
                load_yaml_config=False)
        params = copy.deepcopy(self.config.config)
        # Remove profile from current cloud so that overridding works
        params.pop('profile', None)

        # Utility function to help with the stripping below.
        def pop_keys(params, auth, name_key, id_key):
            if name_key in auth or id_key in auth:
                params['auth'].pop(name_key, None)
                params['auth'].pop(id_key, None)

        # If there are user, project or domain settings in the incoming auth
        # dict, strip out both id and name so that a user can say:
        #     cloud.connect_as(project_name='foo')
        # and have that work with clouds that have a project_id set in their
        # config.
        for prefix in ('user', 'project'):
            if prefix == 'user':
                name_key = 'username'
            else:
                name_key = 'project_name'
            id_key = '{prefix}_id'.format(prefix=prefix)
            pop_keys(params, kwargs, name_key, id_key)
            id_key = '{prefix}_domain_id'.format(prefix=prefix)
            name_key = '{prefix}_domain_name'.format(prefix=prefix)
            pop_keys(params, kwargs, name_key, id_key)

        for key, value in kwargs.items():
            params['auth'][key] = value

        # TODO(mordred) Replace this chunk with the next patch that allows
        # passing a Session to CloudRegion.
        # Closure to pass to OpenStackConfig to ensure the new cloud shares
        # the Session with the current cloud. This will ensure that version
        # discovery cache will be re-used.
        def session_constructor(*args, **kwargs):
            # We need to pass our current keystone session to the Session
            # Constructor, otherwise the new auth plugin doesn't get used.
            return keystoneauth1.session.Session(
                session=self.session,
                discovery_cache=self.config._discovery_cache)

        cloud_config = config.get_one(
            session_constructor=session_constructor,
            **params)
        # Override the cloud name so that logging/location work right
        cloud_config._name = self.name
        cloud_config.config['profile'] = self.name
        # Use self.__class__ so that we return whatever this if, like if it's
        # a subclass in the case of shade wrapping sdk.
        return self.__class__(config=cloud_config)

    def connect_as_project(self, project):
        """Make a new OpenStackCloud object with a new project.

        Take the existing settings from the current cloud and construct a new
        OpenStackCloud object with the project settings overridden. This
        is useful for getting an object to perform tasks with as another user,
        or in the context of a different project.

        .. code-block:: python

          cloud = openstack.connect(cloud='example')
          # Work normally
          servers = cloud.list_servers()
          cloud2 = cloud.connect_as_project('different-project')
          # Work in different-project
          servers = cloud2.list_servers()

        :param project: Either a project name or a project dict as returned by
                        `list_projects`.
        """
        auth = {}
        if isinstance(project, dict):
            auth['project_id'] = project.get('id')
            auth['project_name'] = project.get('name')
            if project.get('domain_id'):
                auth['project_domain_id'] = project['domain_id']
        else:
            auth['project_name'] = project
        return self.connect_as(**auth)

    def _make_cache(self, cache_class, expiration_time, arguments):
        return dogpile.cache.make_region(
            function_key_generator=self._make_cache_key
        ).configure(
            cache_class,
            expiration_time=expiration_time,
            arguments=arguments)

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

    def _get_cache(self, resource_name):
        if resource_name and resource_name in self._resource_caches:
            return self._resource_caches[resource_name]
        else:
            return self._cache

    def _get_major_version_id(self, version):
        if isinstance(version, int):
            return version
        elif isinstance(version, six.string_types + (tuple,)):
            return int(version[0])
        return version

    def _get_versioned_client(
            self, service_type, min_version=None, max_version=None):
        config_version = self.config.get_api_version(service_type)
        config_major = self._get_major_version_id(config_version)
        max_major = self._get_major_version_id(max_version)
        min_major = self._get_major_version_id(min_version)
        # TODO(shade) This should be replaced with use of Connection. However,
        #             we need to find a sane way to deal with this additional
        #             logic - or we need to give up on it. If we give up on it,
        #             we need to make sure we can still support it in the shade
        #             compat layer.
        # NOTE(mordred) This logic for versions is slightly different
        # than the ksa Adapter constructor logic. openstack.cloud knows the
        # versions it knows, and uses them when it detects them. However, if
        # a user requests a version, and it's not found, and a different one
        # openstack.cloud does know about is found, that's a warning in
        # openstack.cloud.
        if config_version:
            if min_major and config_major < min_major:
                raise OpenStackCloudException(
                    "Version {config_version} requested for {service_type}"
                    " but shade understands a minimum of {min_version}".format(
                        config_version=config_version,
                        service_type=service_type,
                        min_version=min_version))
            elif max_major and config_major > max_major:
                raise OpenStackCloudException(
                    "Version {config_version} requested for {service_type}"
                    " but openstack.cloud understands a maximum of"
                    " {max_version}".format(
                        config_version=config_version,
                        service_type=service_type,
                        max_version=max_version))
            request_min_version = config_version
            request_max_version = '{version}.latest'.format(
                version=config_major)
            adapter = _adapter.ShadeAdapter(
                session=self.session,
                task_manager=self.task_manager,
                service_type=self.config.get_service_type(service_type),
                service_name=self.config.get_service_name(service_type),
                interface=self.config.get_interface(service_type),
                endpoint_override=self.config.get_endpoint(service_type),
                region_name=self.config.region_name,
                min_version=request_min_version,
                max_version=request_max_version)
            if adapter.get_endpoint():
                return adapter

        adapter = _adapter.ShadeAdapter(
            session=self.session,
            task_manager=self.task_manager,
            service_type=self.config.get_service_type(service_type),
            service_name=self.config.get_service_name(service_type),
            interface=self.config.get_interface(service_type),
            endpoint_override=self.config.get_endpoint(service_type),
            region_name=self.config.region_name,
            min_version=min_version,
            max_version=max_version)

        # data.api_version can be None if no version was detected, such
        # as with neutron
        api_version = adapter.get_api_major_version(
            endpoint_override=self.config.get_endpoint(service_type))
        api_major = self._get_major_version_id(api_version)

        # If we detect a different version that was configured, warn the user.
        # shade still knows what to do - but if the user gave us an explicit
        # version and we couldn't find it, they may want to investigate.
        if api_version and (api_major != config_major):
            warning_msg = (
                '{service_type} is configured for {config_version}'
                ' but only {api_version} is available. shade is happy'
                ' with this version, but if you were trying to force an'
                ' override, that did not happen. You may want to check'
                ' your cloud, or remove the version specification from'
                ' your config.'.format(
                    service_type=service_type,
                    config_version=config_version,
                    api_version='.'.join([str(f) for f in api_version])))
            self.log.debug(warning_msg)
            warnings.warn(warning_msg)
        return adapter

    # TODO(shade) This should be replaced with using openstack Connection
    #             object.
    def _get_raw_client(
            self, service_type, api_version=None, endpoint_override=None):
        return _adapter.ShadeAdapter(
            session=self.session,
            task_manager=self.task_manager,
            service_type=self.config.get_service_type(service_type),
            service_name=self.config.get_service_name(service_type),
            interface=self.config.get_interface(service_type),
            endpoint_override=self.config.get_endpoint(
                service_type) or endpoint_override,
            region_name=self.config.region_name)

    def _is_client_version(self, client, version):
        client_name = '_{client}_client'.format(client=client)
        client = getattr(self, client_name)
        return client._version_matches(version)

    @property
    def _application_catalog_client(self):
        if 'application-catalog' not in self._raw_clients:
            self._raw_clients['application-catalog'] = self._get_raw_client(
                'application-catalog')
        return self._raw_clients['application-catalog']

    @property
    def _baremetal_client(self):
        if 'baremetal' not in self._raw_clients:
            client = self._get_raw_client('baremetal')
            # Do this to force version discovery. We need to do that, because
            # the endpoint-override trick we do for neutron because
            # ironicclient just appends a /v1 won't work and will break
            # keystoneauth - because ironic's versioned discovery endpoint
            # is non-compliant and doesn't return an actual version dict.
            client = self._get_versioned_client(
                'baremetal', min_version=1, max_version='1.latest')
            self._raw_clients['baremetal'] = client
        return self._raw_clients['baremetal']

    @property
    def _container_infra_client(self):
        if 'container-infra' not in self._raw_clients:
            self._raw_clients['container-infra'] = self._get_raw_client(
                'container-infra')
        return self._raw_clients['container-infra']

    @property
    def _database_client(self):
        if 'database' not in self._raw_clients:
            self._raw_clients['database'] = self._get_raw_client('database')
        return self._raw_clients['database']

    @property
    def _dns_client(self):
        if 'dns' not in self._raw_clients:
            dns_client = self._get_versioned_client(
                'dns', min_version=2, max_version='2.latest')
            self._raw_clients['dns'] = dns_client
        return self._raw_clients['dns']

    @property
    def _identity_client(self):
        if 'identity' not in self._raw_clients:
            self._raw_clients['identity'] = self._get_versioned_client(
                'identity', min_version=2, max_version='3.latest')
        return self._raw_clients['identity']

    @property
    def _raw_image_client(self):
        if 'raw-image' not in self._raw_clients:
            image_client = self._get_raw_client('image')
            self._raw_clients['raw-image'] = image_client
        return self._raw_clients['raw-image']

    @property
    def _image_client(self):
        if 'image' not in self._raw_clients:
            self._raw_clients['image'] = self._get_versioned_client(
                'image', min_version=1, max_version='2.latest')
        return self._raw_clients['image']

    @property
    def _network_client(self):
        if 'network' not in self._raw_clients:
            client = self._get_raw_client('network')
            # TODO(mordred) I don't care if this is what neutronclient does,
            # fix this.
            # Don't bother with version discovery - there is only one version
            # of neutron. This is what neutronclient does, fwiw.
            endpoint = client.get_endpoint()
            if not endpoint.rstrip().rsplit('/')[1] == 'v2.0':
                if not endpoint.endswith('/'):
                    endpoint += '/'
                endpoint = urllib.parse.urljoin(
                    endpoint, 'v2.0')
            client.endpoint_override = endpoint
            self._raw_clients['network'] = client
        return self._raw_clients['network']

    @property
    def _object_store_client(self):
        if 'object-store' not in self._raw_clients:
            raw_client = self._get_raw_client('object-store')
            self._raw_clients['object-store'] = raw_client
        return self._raw_clients['object-store']

    @property
    def _orchestration_client(self):
        if 'orchestration' not in self._raw_clients:
            raw_client = self._get_raw_client('orchestration')
            self._raw_clients['orchestration'] = raw_client
        return self._raw_clients['orchestration']

    @property
    def _volume_client(self):
        if 'volume' not in self._raw_clients:
            self._raw_clients['volume'] = self._get_raw_client('volume')
        return self._raw_clients['volume']

    def pprint(self, resource):
        """Wrapper aroud pprint that groks munch objects"""
        # import late since this is a utility function
        import pprint
        new_resource = _utils._dictify_resource(resource)
        pprint.pprint(new_resource)

    def pformat(self, resource):
        """Wrapper aroud pformat that groks munch objects"""
        # import late since this is a utility function
        import pprint
        new_resource = _utils._dictify_resource(resource)
        return pprint.pformat(new_resource)

    @property
    def _keystone_catalog(self):
        return self.session.auth.get_access(self.session).service_catalog

    @property
    def service_catalog(self):
        return self._keystone_catalog.catalog

    def endpoint_for(self, service_type, interface='public'):
        return self._keystone_catalog.url_for(
            service_type=service_type, interface=interface)

    @property
    def auth_token(self):
        # Keystone's session will reuse a token if it is still valid.
        # We don't need to track validity here, just get_token() each time.
        return self.session.get_token()

    @property
    def current_user_id(self):
        """Get the id of the currently logged-in user from the token."""
        return self.session.auth.get_access(self.session).user_id

    @property
    def current_project_id(self):
        """Get the current project ID.

        Returns the project_id of the current token scope. None means that
        the token is domain scoped or unscoped.

        :raises keystoneauth1.exceptions.auth.AuthorizationFailure:
            if a new token fetch fails.
        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin:
            if a plugin is not available.
        """
        return self.session.get_project_id()

    @property
    def current_project(self):
        """Return a ``munch.Munch`` describing the current project"""
        return self._get_project_info()

    def _get_project_info(self, project_id=None):
        project_info = munch.Munch(
            id=project_id,
            name=None,
            domain_id=None,
            domain_name=None,
        )
        if not project_id or project_id == self.current_project_id:
            # If we don't have a project_id parameter, it means a user is
            # directly asking what the current state is.
            # Alternately, if we have one, that means we're calling this
            # from within a normalize function, which means the object has
            # a project_id associated with it. If the project_id matches
            # the project_id of our current token, that means we can supplement
            # the info with human readable info about names if we have them.
            # If they don't match, that means we're an admin who has pulled
            # an object from a different project, so adding info from the
            # current token would be wrong.
            auth_args = self.config.config.get('auth', {})
            project_info['id'] = self.current_project_id
            project_info['name'] = auth_args.get('project_name')
            project_info['domain_id'] = auth_args.get('project_domain_id')
            project_info['domain_name'] = auth_args.get('project_domain_name')
        return project_info

    @property
    def current_location(self):
        """Return a ``munch.Munch`` explaining the current cloud location."""
        return self._get_current_location()

    def _get_current_location(self, project_id=None, zone=None):
        return munch.Munch(
            cloud=self.name,
            region_name=self.config.region_name,
            zone=zone,
            project=self._get_project_info(project_id),
        )

    def _get_identity_location(self):
        '''Identity resources do not exist inside of projects.'''
        return munch.Munch(
            cloud=self.name,
            region_name=None,
            zone=None,
            project=munch.Munch(
                id=None,
                name=None,
                domain_id=None,
                domain_name=None))

    def _get_project_id_param_dict(self, name_or_id):
        if name_or_id:
            project = self.get_project(name_or_id)
            if not project:
                return {}
            if self._is_client_version('identity', 3):
                return {'default_project_id': project['id']}
            else:
                return {'tenant_id': project['id']}
        else:
            return {}

    def _get_domain_id_param_dict(self, domain_id):
        """Get a useable domain."""

        # Keystone v3 requires domains for user and project creation. v2 does
        # not. However, keystone v2 does not allow user creation by non-admin
        # users, so we can throw an error to the user that does not need to
        # mention api versions
        if self._is_client_version('identity', 3):
            if not domain_id:
                raise OpenStackCloudException(
                    "User or project creation requires an explicit"
                    " domain_id argument.")
            else:
                return {'domain_id': domain_id}
        else:
            return {}

    def _get_identity_params(self, domain_id=None, project=None):
        """Get the domain and project/tenant parameters if needed.

        keystone v2 and v3 are divergent enough that we need to pass or not
        pass project or tenant_id or domain or nothing in a sane manner.
        """
        ret = {}
        ret.update(self._get_domain_id_param_dict(domain_id))
        ret.update(self._get_project_id_param_dict(project))
        return ret

    def range_search(self, data, filters):
        """Perform integer range searches across a list of dictionaries.

        Given a list of dictionaries, search across the list using the given
        dictionary keys and a range of integer values for each key. Only
        dictionaries that match ALL search filters across the entire original
        data set will be returned.

        It is not a requirement that each dictionary contain the key used
        for searching. Those without the key will be considered non-matching.

        The range values must be string values and is either a set of digits
        representing an integer for matching, or a range operator followed by
        a set of digits representing an integer for matching. If a range
        operator is not given, exact value matching will be used. Valid
        operators are one of: <,>,<=,>=

        :param data: List of dictionaries to be searched.
        :param filters: Dict describing the one or more range searches to
            perform. If more than one search is given, the result will be the
            members of the original data set that match ALL searches. An
            example of filtering by multiple ranges::

                {"vcpus": "<=5", "ram": "<=2048", "disk": "1"}

        :returns: A list subset of the original data set.
        :raises: OpenStackCloudException on invalid range expressions.
        """
        filtered = []

        for key, range_value in filters.items():
            # We always want to operate on the full data set so that
            # calculations for minimum and maximum are correct.
            results = _utils.range_filter(data, key, range_value)

            if not filtered:
                # First set of results
                filtered = results
            else:
                # The combination of all searches should be the intersection of
                # all result sets from each search. So adjust the current set
                # of filtered data by computing its intersection with the
                # latest result set.
                filtered = [r for r in results for f in filtered if r == f]

        return filtered

    def _get_and_munchify(self, key, data):
        """Wrapper around meta.get_and_munchify.

        Some of the methods expect a `meta` attribute to be passed in as
        part of the method signature. In those methods the meta param is
        overriding the meta module making the call to meta.get_and_munchify
        to fail.
        """
        return meta.get_and_munchify(key, data)

    @_utils.cache_on_arguments()
    def list_projects(self, domain_id=None, name_or_id=None, filters=None):
        """List projects.

        With no parameters, returns a full listing of all visible projects.

        :param domain_id: domain ID to scope the searched projects.
        :param name_or_id: project name or ID.
        :param filters: a dict containing additional filters to use
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a list of ``munch.Munch`` containing the projects

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        kwargs = dict(
            filters=filters,
            domain_id=domain_id)
        if self._is_client_version('identity', 3):
            kwargs['obj_name'] = 'project'

        pushdown, filters = _normalize._split_filters(**kwargs)

        try:
            if self._is_client_version('identity', 3):
                key = 'projects'
            else:
                key = 'tenants'
            data = self._identity_client.get(
                '/{endpoint}'.format(endpoint=key), params=pushdown)
            projects = self._normalize_projects(
                self._get_and_munchify(key, data))
        except Exception as e:
            self.log.debug("Failed to list projects", exc_info=True)
            raise OpenStackCloudException(str(e))
        return _utils._filter_list(projects, name_or_id, filters)

    def search_projects(self, name_or_id=None, filters=None, domain_id=None):
        '''Backwards compatibility method for search_projects

        search_projects originally had a parameter list that was name_or_id,
        filters and list had domain_id first. This method exists in this form
        to allow code written with positional parameter to still work. But
        really, use keyword arguments.
        '''
        return self.list_projects(
            domain_id=domain_id, name_or_id=name_or_id, filters=filters)

    def get_project(self, name_or_id, filters=None, domain_id=None):
        """Get exactly one project.

        :param name_or_id: project name or ID.
        :param filters: a dict containing additional filters to use.
        :param domain_id: domain ID (identity v3 only).

        :returns: a list of ``munch.Munch`` containing the project description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        return _utils._get_entity(self, 'project', name_or_id, filters,
                                  domain_id=domain_id)

    @_utils.valid_kwargs('description')
    def update_project(self, name_or_id, enabled=None, domain_id=None,
                       **kwargs):
        with _utils.shade_exceptions(
                "Error in updating project {project}".format(
                    project=name_or_id)):
            proj = self.get_project(name_or_id, domain_id=domain_id)
            if not proj:
                raise OpenStackCloudException(
                    "Project %s not found." % name_or_id)
            if enabled is not None:
                kwargs.update({'enabled': enabled})
            # NOTE(samueldmq): Current code only allow updates of description
            # or enabled fields.
            if self._is_client_version('identity', 3):
                data = self._identity_client.patch(
                    '/projects/' + proj['id'], json={'project': kwargs})
                project = self._get_and_munchify('project', data)
            else:
                data = self._identity_client.post(
                    '/tenants/' + proj['id'], json={'tenant': kwargs})
                project = self._get_and_munchify('tenant', data)
            project = self._normalize_project(project)
        self.list_projects.invalidate(self)
        return project

    def create_project(
            self, name, description=None, domain_id=None, enabled=True):
        """Create a project."""
        with _utils.shade_exceptions(
                "Error in creating project {project}".format(project=name)):
            project_ref = self._get_domain_id_param_dict(domain_id)
            project_ref.update({'name': name,
                                'description': description,
                                'enabled': enabled})
            endpoint, key = ('tenants', 'tenant')
            if self._is_client_version('identity', 3):
                endpoint, key = ('projects', 'project')
            data = self._identity_client.post(
                '/{endpoint}'.format(endpoint=endpoint),
                json={key: project_ref})
            project = self._normalize_project(
                self._get_and_munchify(key, data))
        self.list_projects.invalidate(self)
        return project

    def delete_project(self, name_or_id, domain_id=None):
        """Delete a project.

        :param string name_or_id: Project name or ID.
        :param string domain_id: Domain ID containing the project(identity v3
            only).

        :returns: True if delete succeeded, False if the project was not found.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """

        with _utils.shade_exceptions(
                "Error in deleting project {project}".format(
                    project=name_or_id)):
            project = self.get_project(name_or_id, domain_id=domain_id)
            if project is None:
                self.log.debug(
                    "Project %s not found for deleting", name_or_id)
                return False

            if self._is_client_version('identity', 3):
                self._identity_client.delete('/projects/' + project['id'])
            else:
                self._identity_client.delete('/tenants/' + project['id'])

        return True

    @_utils.valid_kwargs('domain_id')
    @_utils.cache_on_arguments()
    def list_users(self, **kwargs):
        """List users.

        :param domain_id: Domain ID. (v3)

        :returns: a list of ``munch.Munch`` containing the user description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        data = self._identity_client.get('/users', params=kwargs)
        return _utils.normalize_users(
            self._get_and_munchify('users', data))

    @_utils.valid_kwargs('domain_id')
    def search_users(self, name_or_id=None, filters=None, **kwargs):
        """Search users.

        :param string name_or_id: user name or ID.
        :param domain_id: Domain ID. (v3)
        :param filters: a dict containing additional filters to use.
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a list of ``munch.Munch`` containing the users

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        users = self.list_users(**kwargs)
        return _utils._filter_list(users, name_or_id, filters)

    @_utils.valid_kwargs('domain_id')
    def get_user(self, name_or_id, filters=None, **kwargs):
        """Get exactly one user.

        :param string name_or_id: user name or ID.
        :param domain_id: Domain ID. (v3)
        :param filters: a dict containing additional filters to use.
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a single ``munch.Munch`` containing the user description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        return _utils._get_entity(self, 'user', name_or_id, filters, **kwargs)

    def get_user_by_id(self, user_id, normalize=True):
        """Get a user by ID.

        :param string user_id: user ID
        :param bool normalize: Flag to control dict normalization

        :returns: a single ``munch.Munch`` containing the user description
        """
        data = self._identity_client.get(
            '/users/{user}'.format(user=user_id),
            error_message="Error getting user with ID {user_id}".format(
                user_id=user_id))

        user = self._get_and_munchify('user', data)
        if user and normalize:
            user = _utils.normalize_users(user)
        return user

    # NOTE(Shrews): Keystone v2 supports updating only name, email and enabled.
    @_utils.valid_kwargs('name', 'email', 'enabled', 'domain_id', 'password',
                         'description', 'default_project')
    def update_user(self, name_or_id, **kwargs):
        self.list_users.invalidate(self)
        user_kwargs = {}
        if 'domain_id' in kwargs and kwargs['domain_id']:
            user_kwargs['domain_id'] = kwargs['domain_id']
        user = self.get_user(name_or_id, **user_kwargs)

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call if it's an admin force call (and figure out how
        # to make that disctinction)
        if self._is_client_version('identity', 2):
            # Do not pass v3 args to a v2 keystone.
            kwargs.pop('domain_id', None)
            kwargs.pop('description', None)
            kwargs.pop('default_project', None)
            password = kwargs.pop('password', None)
            if password is not None:
                with _utils.shade_exceptions(
                        "Error updating password for {user}".format(
                            user=name_or_id)):
                    error_msg = "Error updating password for user {}".format(
                        name_or_id)
                    data = self._identity_client.put(
                        '/users/{u}/OS-KSADM/password'.format(u=user['id']),
                        json={'user': {'password': password}},
                        error_message=error_msg)

            # Identity v2.0 implements PUT. v3 PATCH. Both work as PATCH.
            data = self._identity_client.put(
                '/users/{user}'.format(user=user['id']), json={'user': kwargs},
                error_message="Error in updating user {}".format(name_or_id))
        else:
            # NOTE(samueldmq): now this is a REST call and domain_id is dropped
            # if None. keystoneclient drops keys with None values.
            if 'domain_id' in kwargs and kwargs['domain_id'] is None:
                del kwargs['domain_id']
            data = self._identity_client.patch(
                '/users/{user}'.format(user=user['id']), json={'user': kwargs},
                error_message="Error in updating user {}".format(name_or_id))

        user = self._get_and_munchify('user', data)
        self.list_users.invalidate(self)
        return _utils.normalize_users([user])[0]

    def create_user(
            self, name, password=None, email=None, default_project=None,
            enabled=True, domain_id=None, description=None):
        """Create a user."""
        params = self._get_identity_params(domain_id, default_project)
        params.update({'name': name, 'password': password, 'email': email,
                       'enabled': enabled})
        if self._is_client_version('identity', 3):
            params['description'] = description
        elif description is not None:
            self.log.info(
                "description parameter is not supported on Keystone v2")

        error_msg = "Error in creating user {user}".format(user=name)
        data = self._identity_client.post('/users', json={'user': params},
                                          error_message=error_msg)
        user = self._get_and_munchify('user', data)

        self.list_users.invalidate(self)
        return _utils.normalize_users([user])[0]

    @_utils.valid_kwargs('domain_id')
    def delete_user(self, name_or_id, **kwargs):
        # TODO(mordred) Why are we invalidating at the TOP?
        self.list_users.invalidate(self)
        user = self.get_user(name_or_id, **kwargs)
        if not user:
            self.log.debug(
                "User {0} not found for deleting".format(name_or_id))
            return False

        # TODO(mordred) Extra GET only needed to support keystoneclient.
        #               Can be removed as a follow-on.
        user = self.get_user_by_id(user['id'], normalize=False)
        self._identity_client.delete(
            '/users/{user}'.format(user=user['id']),
            error_message="Error in deleting user {user}".format(
                user=name_or_id))

        self.list_users.invalidate(self)
        return True

    def _get_user_and_group(self, user_name_or_id, group_name_or_id):
        user = self.get_user(user_name_or_id)
        if not user:
            raise OpenStackCloudException(
                'User {user} not found'.format(user=user_name_or_id))

        group = self.get_group(group_name_or_id)
        if not group:
            raise OpenStackCloudException(
                'Group {user} not found'.format(user=group_name_or_id))

        return (user, group)

    def add_user_to_group(self, name_or_id, group_name_or_id):
        """Add a user to a group.

        :param string name_or_id: User name or ID
        :param string group_name_or_id: Group name or ID

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        user, group = self._get_user_and_group(name_or_id, group_name_or_id)

        error_msg = "Error adding user {user} to group {group}".format(
            user=name_or_id, group=group_name_or_id)
        self._identity_client.put(
            '/groups/{g}/users/{u}'.format(g=group['id'], u=user['id']),
            error_message=error_msg)

    def is_user_in_group(self, name_or_id, group_name_or_id):
        """Check to see if a user is in a group.

        :param string name_or_id: User name or ID
        :param string group_name_or_id: Group name or ID

        :returns: True if user is in the group, False otherwise

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        user, group = self._get_user_and_group(name_or_id, group_name_or_id)

        try:
            self._identity_client.head(
                '/groups/{g}/users/{u}'.format(g=group['id'], u=user['id']))
            return True
        except OpenStackCloudURINotFound:
            # NOTE(samueldmq): knowing this URI exists, let's interpret this as
            # user not found in group rather than URI not found.
            return False

    def remove_user_from_group(self, name_or_id, group_name_or_id):
        """Remove a user from a group.

        :param string name_or_id: User name or ID
        :param string group_name_or_id: Group name or ID

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        user, group = self._get_user_and_group(name_or_id, group_name_or_id)

        error_msg = "Error removing user {user} from group {group}".format(
            user=name_or_id, group=group_name_or_id)
        self._identity_client.delete(
            '/groups/{g}/users/{u}'.format(g=group['id'], u=user['id']),
            error_message=error_msg)

    def get_template_contents(
            self, template_file=None, template_url=None,
            template_object=None, files=None):
        try:
            return template_utils.get_template_contents(
                template_file=template_file, template_url=template_url,
                template_object=template_object, files=files)
        except Exception as e:
            raise OpenStackCloudException(
                "Error in processing template files: %s" % str(e))

    def create_stack(
            self, name, tags=None,
            template_file=None, template_url=None,
            template_object=None, files=None,
            rollback=True,
            wait=False, timeout=3600,
            environment_files=None,
            **parameters):
        """Create a stack.

        :param string name: Name of the stack.
        :param tags: List of tag(s) of the stack. (optional)
        :param string template_file: Path to the template.
        :param string template_url: URL of template.
        :param string template_object: URL to retrieve template object.
        :param dict files: dict of additional file content to include.
        :param boolean rollback: Enable rollback on create failure.
        :param boolean wait: Whether to wait for the delete to finish.
        :param int timeout: Stack create timeout in seconds.
        :param environment_files: Paths to environment files to apply.

        Other arguments will be passed as stack parameters which will take
        precedence over any parameters specified in the environments.

        Only one of template_file, template_url, template_object should be
        specified.

        :returns: a dict containing the stack description

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        envfiles, env = template_utils.process_multiple_environments_and_files(
            env_paths=environment_files)
        tpl_files, template = template_utils.get_template_contents(
            template_file=template_file,
            template_url=template_url,
            template_object=template_object,
            files=files)
        params = dict(
            stack_name=name,
            tags=tags,
            disable_rollback=not rollback,
            parameters=parameters,
            template=template,
            files=dict(list(tpl_files.items()) + list(envfiles.items())),
            environment=env,
            timeout_mins=timeout // 60,
        )
        self._orchestration_client.post('/stacks', json=params)
        if wait:
            event_utils.poll_for_events(self, stack_name=name,
                                        action='CREATE')
        return self.get_stack(name)

    def update_stack(
            self, name_or_id,
            template_file=None, template_url=None,
            template_object=None, files=None,
            rollback=True,
            wait=False, timeout=3600,
            environment_files=None,
            **parameters):
        """Update a stack.

        :param string name_or_id: Name or ID of the stack to update.
        :param string template_file: Path to the template.
        :param string template_url: URL of template.
        :param string template_object: URL to retrieve template object.
        :param dict files: dict of additional file content to include.
        :param boolean rollback: Enable rollback on update failure.
        :param boolean wait: Whether to wait for the delete to finish.
        :param int timeout: Stack update timeout in seconds.
        :param environment_files: Paths to environment files to apply.

        Other arguments will be passed as stack parameters which will take
        precedence over any parameters specified in the environments.

        Only one of template_file, template_url, template_object should be
        specified.

        :returns: a dict containing the stack description

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API calls
        """
        envfiles, env = template_utils.process_multiple_environments_and_files(
            env_paths=environment_files)
        tpl_files, template = template_utils.get_template_contents(
            template_file=template_file,
            template_url=template_url,
            template_object=template_object,
            files=files)
        params = dict(
            disable_rollback=not rollback,
            parameters=parameters,
            template=template,
            files=dict(list(tpl_files.items()) + list(envfiles.items())),
            environment=env,
            timeout_mins=timeout // 60,
        )
        if wait:
            # find the last event to use as the marker
            events = event_utils.get_events(
                self, name_or_id, event_args={'sort_dir': 'desc', 'limit': 1})
            marker = events[0].id if events else None

        self._orchestration_client.put(
            '/stacks/{name_or_id}'.format(name_or_id=name_or_id), json=params)
        if wait:
            event_utils.poll_for_events(self,
                                        name_or_id,
                                        action='UPDATE',
                                        marker=marker)
        return self.get_stack(name_or_id)

    def delete_stack(self, name_or_id, wait=False):
        """Delete a stack

        :param string name_or_id: Stack name or ID.
        :param boolean wait: Whether to wait for the delete to finish

        :returns: True if delete succeeded, False if the stack was not found.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        stack = self.get_stack(name_or_id, resolve_outputs=False)
        if stack is None:
            self.log.debug("Stack %s not found for deleting", name_or_id)
            return False

        if wait:
            # find the last event to use as the marker
            events = event_utils.get_events(
                self, name_or_id, event_args={'sort_dir': 'desc', 'limit': 1})
            marker = events[0].id if events else None

        self._orchestration_client.delete(
            '/stacks/{id}'.format(id=stack['id']))

        if wait:
            try:
                event_utils.poll_for_events(self,
                                            stack_name=name_or_id,
                                            action='DELETE',
                                            marker=marker)
            except OpenStackCloudHTTPError:
                pass
            stack = self.get_stack(name_or_id, resolve_outputs=False)
            if stack and stack['stack_status'] == 'DELETE_FAILED':
                raise OpenStackCloudException(
                    "Failed to delete stack {id}: {reason}".format(
                        id=name_or_id, reason=stack['stack_status_reason']))

        return True

    def get_name(self):
        return self.name

    def get_region(self):
        return self.config.region_name

    def get_flavor_name(self, flavor_id):
        flavor = self.get_flavor(flavor_id, get_extra=False)
        if flavor:
            return flavor['name']
        return None

    def get_flavor_by_ram(self, ram, include=None, get_extra=True):
        """Get a flavor based on amount of RAM available.

        Finds the flavor with the least amount of RAM that is at least
        as much as the specified amount. If `include` is given, further
        filter based on matching flavor name.

        :param int ram: Minimum amount of RAM.
        :param string include: If given, will return a flavor whose name
            contains this string as a substring.
        """
        flavors = self.list_flavors(get_extra=get_extra)
        for flavor in sorted(flavors, key=operator.itemgetter('ram')):
            if (flavor['ram'] >= ram and
                    (not include or include in flavor['name'])):
                return flavor
        raise OpenStackCloudException(
            "Could not find a flavor with {ram} and '{include}'".format(
                ram=ram, include=include))

    def get_session_endpoint(self, service_key):
        try:
            return self.config.get_session_endpoint(service_key)
        except keystoneauth1.exceptions.catalog.EndpointNotFound as e:
            self.log.debug(
                "Endpoint not found in %s cloud: %s", self.name, str(e))
            endpoint = None
        except OpenStackCloudException:
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Error getting {service} endpoint on {cloud}:{region}:"
                " {error}".format(
                    service=service_key,
                    cloud=self.name,
                    region=self.config.region_name,
                    error=str(e)))
        return endpoint

    def has_service(self, service_key):
        if not self.config.config.get('has_%s' % service_key, True):
            # TODO(mordred) add a stamp here so that we only report this once
            if not (service_key in self._disable_warnings
                    and self._disable_warnings[service_key]):
                self.log.debug(
                    "Disabling %(service_key)s entry in catalog"
                    " per config", {'service_key': service_key})
                self._disable_warnings[service_key] = True
            return False
        try:
            endpoint = self.get_session_endpoint(service_key)
        except OpenStackCloudException:
            return False
        if endpoint:
            return True
        else:
            return False

    @_utils.cache_on_arguments()
    def _nova_extensions(self):
        extensions = set()
        data = _adapter._json_response(
            self.compute.get('/extensions'),
            error_message="Error fetching extension list for nova")

        for extension in self._get_and_munchify('extensions', data):
            extensions.add(extension['alias'])
        return extensions

    def _has_nova_extension(self, extension_name):
        return extension_name in self._nova_extensions()

    def search_keypairs(self, name_or_id=None, filters=None):
        keypairs = self.list_keypairs()
        return _utils._filter_list(keypairs, name_or_id, filters)

    @_utils.cache_on_arguments()
    def _neutron_extensions(self):
        extensions = set()
        data = self._network_client.get(
            '/extensions.json',
            error_message="Error fetching extension list for neutron")
        for extension in self._get_and_munchify('extensions', data):
            extensions.add(extension['alias'])
        return extensions

    def _has_neutron_extension(self, extension_alias):
        return extension_alias in self._neutron_extensions()

    def search_networks(self, name_or_id=None, filters=None):
        """Search networks

        :param name_or_id: Name or ID of the desired network.
        :param filters: a dict containing additional filters to use. e.g.
                        {'router:external': True}

        :returns: a list of ``munch.Munch`` containing the network description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        networks = self.list_networks(filters)
        return _utils._filter_list(networks, name_or_id, filters)

    def search_routers(self, name_or_id=None, filters=None):
        """Search routers

        :param name_or_id: Name or ID of the desired router.
        :param filters: a dict containing additional filters to use. e.g.
                        {'admin_state_up': True}

        :returns: a list of ``munch.Munch`` containing the router description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        routers = self.list_routers(filters)
        return _utils._filter_list(routers, name_or_id, filters)

    def search_subnets(self, name_or_id=None, filters=None):
        """Search subnets

        :param name_or_id: Name or ID of the desired subnet.
        :param filters: a dict containing additional filters to use. e.g.
                        {'enable_dhcp': True}

        :returns: a list of ``munch.Munch`` containing the subnet description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        subnets = self.list_subnets(filters)
        return _utils._filter_list(subnets, name_or_id, filters)

    def search_ports(self, name_or_id=None, filters=None):
        """Search ports

        :param name_or_id: Name or ID of the desired port.
        :param filters: a dict containing additional filters to use. e.g.
                        {'device_id': '2711c67a-b4a7-43dd-ace7-6187b791c3f0'}

        :returns: a list of ``munch.Munch`` containing the port description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        # If port caching is enabled, do not push the filter down to
        # neutron; get all the ports (potentially from the cache) and
        # filter locally.
        if self._PORT_AGE:
            pushdown_filters = None
        else:
            pushdown_filters = filters
        ports = self.list_ports(pushdown_filters)
        return _utils._filter_list(ports, name_or_id, filters)

    def search_qos_policies(self, name_or_id=None, filters=None):
        """Search QoS policies

        :param name_or_id: Name or ID of the desired policy.
        :param filters: a dict containing additional filters to use. e.g.
                        {'shared': True}

        :returns: a list of ``munch.Munch`` containing the network description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        policies = self.list_qos_policies(filters)
        return _utils._filter_list(policies, name_or_id, filters)

    def search_volumes(self, name_or_id=None, filters=None):
        volumes = self.list_volumes()
        return _utils._filter_list(
            volumes, name_or_id, filters)

    def search_volume_snapshots(self, name_or_id=None, filters=None):
        volumesnapshots = self.list_volume_snapshots()
        return _utils._filter_list(
            volumesnapshots, name_or_id, filters)

    def search_volume_backups(self, name_or_id=None, filters=None):
        volume_backups = self.list_volume_backups()
        return _utils._filter_list(
            volume_backups, name_or_id, filters)

    def search_volume_types(
            self, name_or_id=None, filters=None, get_extra=True):
        volume_types = self.list_volume_types(get_extra=get_extra)
        return _utils._filter_list(volume_types, name_or_id, filters)

    def search_flavors(self, name_or_id=None, filters=None, get_extra=True):
        flavors = self.list_flavors(get_extra=get_extra)
        return _utils._filter_list(flavors, name_or_id, filters)

    def search_security_groups(self, name_or_id=None, filters=None):
        # `filters` could be a dict or a jmespath (str)
        groups = self.list_security_groups(
            filters=filters if isinstance(filters, dict) else None
        )
        return _utils._filter_list(groups, name_or_id, filters)

    def search_servers(
            self, name_or_id=None, filters=None, detailed=False,
            all_projects=False, bare=False):
        servers = self.list_servers(
            detailed=detailed, all_projects=all_projects, bare=bare)
        return _utils._filter_list(servers, name_or_id, filters)

    def search_server_groups(self, name_or_id=None, filters=None):
        """Seach server groups.

        :param name: server group name or ID.
        :param filters: a dict containing additional filters to use.

        :returns: a list of dicts containing the server groups

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        server_groups = self.list_server_groups()
        return _utils._filter_list(server_groups, name_or_id, filters)

    def search_images(self, name_or_id=None, filters=None):
        images = self.list_images()
        return _utils._filter_list(images, name_or_id, filters)

    def search_floating_ip_pools(self, name=None, filters=None):
        pools = self.list_floating_ip_pools()
        return _utils._filter_list(pools, name, filters)

    # With Neutron, there are some cases in which full server side filtering is
    # not possible (e.g. nested attributes or list of objects) so we also need
    # to use the client-side filtering
    # The same goes for all neutron-related search/get methods!
    def search_floating_ips(self, id=None, filters=None):
        # `filters` could be a jmespath expression which Neutron server doesn't
        # understand, obviously.
        if self._use_neutron_floating() and isinstance(filters, dict):
            kwargs = {'filters': filters}
        else:
            kwargs = {}
        floating_ips = self.list_floating_ips(**kwargs)
        return _utils._filter_list(floating_ips, id, filters)

    def search_stacks(self, name_or_id=None, filters=None):
        """Search stacks.

        :param name_or_id: Name or ID of the desired stack.
        :param filters: a dict containing additional filters to use. e.g.
                {'stack_status': 'CREATE_COMPLETE'}

        :returns: a list of ``munch.Munch`` containing the stack description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        stacks = self.list_stacks()
        return _utils._filter_list(stacks, name_or_id, filters)

    def list_keypairs(self):
        """List all available keypairs.

        :returns: A list of ``munch.Munch`` containing keypair info.

        """
        data = _adapter._json_response(
            self.compute.get('/os-keypairs'),
            error_message="Error fetching keypair list")
        return self._normalize_keypairs([
            k['keypair'] for k in self._get_and_munchify('keypairs', data)])

    def list_networks(self, filters=None):
        """List all available networks.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of ``munch.Munch`` containing network info.

        """
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        data = self._network_client.get("/networks.json", params=filters)
        return self._get_and_munchify('networks', data)

    def list_routers(self, filters=None):
        """List all available routers.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of router ``munch.Munch``.

        """
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        data = self._network_client.get(
            "/routers.json", params=filters,
            error_message="Error fetching router list")
        return self._get_and_munchify('routers', data)

    def list_subnets(self, filters=None):
        """List all available subnets.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of subnet ``munch.Munch``.

        """
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        data = self._network_client.get("/subnets.json", params=filters)
        return self._get_and_munchify('subnets', data)

    def list_ports(self, filters=None):
        """List all available ports.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of port ``munch.Munch``.

        """
        # If pushdown filters are specified and we do not have batched caching
        # enabled, bypass local caching and push down the filters.
        if filters and self._PORT_AGE == 0:
            return self._list_ports(filters)

        # Translate None from search interface to empty {} for kwargs below
        filters = {}
        if (time.time() - self._ports_time) >= self._PORT_AGE:
            # Since we're using cached data anyway, we don't need to
            # have more than one thread actually submit the list
            # ports task.  Let the first one submit it while holding
            # a lock, and the non-blocking acquire method will cause
            # subsequent threads to just skip this and use the old
            # data until it succeeds.
            # Initially when we never got data, block to retrieve some data.
            first_run = self._ports is None
            if self._ports_lock.acquire(first_run):
                try:
                    if not (first_run and self._ports is not None):
                        self._ports = self._list_ports(filters)
                        self._ports_time = time.time()
                finally:
                    self._ports_lock.release()
        return self._ports

    def _list_ports(self, filters):
        data = self._network_client.get(
            "/ports.json", params=filters,
            error_message="Error fetching port list")
        return self._get_and_munchify('ports', data)

    def list_qos_rule_types(self, filters=None):
        """List all available QoS rule types.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of rule types ``munch.Munch``.

        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        data = self._network_client.get(
            "/qos/rule-types.json", params=filters,
            error_message="Error fetching QoS rule types list")
        return self._get_and_munchify('rule_types', data)

    def get_qos_rule_type_details(self, rule_type, filters=None):
        """Get a QoS rule type details by rule type name.

        :param string rule_type: Name of the QoS rule type.

        :returns: A rule type details ``munch.Munch`` or None if
            no matching rule type is found.

        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        if not self._has_neutron_extension('qos-rule-type-details'):
            raise OpenStackCloudUnavailableExtension(
                'qos-rule-type-details extension is not available '
                'on target cloud')

        data = self._network_client.get(
            "/qos/rule-types/{rule_type}.json".format(rule_type=rule_type),
            error_message="Error fetching QoS details of {rule_type} "
                          "rule type".format(rule_type=rule_type))
        return self._get_and_munchify('rule_type', data)

    def list_qos_policies(self, filters=None):
        """List all available QoS policies.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of policies ``munch.Munch``.

        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        data = self._network_client.get(
            "/qos/policies.json", params=filters,
            error_message="Error fetching QoS policies list")
        return self._get_and_munchify('policies', data)

    @_utils.cache_on_arguments(should_cache_fn=_no_pending_volumes)
    def list_volumes(self, cache=True):
        """List all available volumes.

        :returns: A list of volume ``munch.Munch``.

        """
        def _list(data):
            volumes.extend(data.get('volumes', []))
            endpoint = None
            for l in data.get('volumes_links', []):
                if 'rel' in l and 'next' == l['rel']:
                    endpoint = l['href']
                    break
            if endpoint:
                try:
                    _list(self._volume_client.get(endpoint))
                except OpenStackCloudURINotFound:
                    # Catch and re-raise here because we are making recursive
                    # calls and we just have context for the log here
                    self.log.debug(
                        "While listing volumes, could not find next link"
                        " {link}.".format(link=data))
                    raise

        if not cache:
            warnings.warn('cache argument to list_volumes is deprecated. Use '
                          'invalidate instead.')

        # Fetching paginated volumes can fails for several reasons, if
        # something goes wrong we'll have to start fetching volumes from
        # scratch
        attempts = 5
        for _ in range(attempts):
            volumes = []
            data = self._volume_client.get('/volumes/detail')
            if 'volumes_links' not in data:
                # no pagination needed
                volumes.extend(data.get('volumes', []))
                break

            try:
                _list(data)
                break
            except OpenStackCloudURINotFound:
                pass
        else:
            self.log.debug(
                "List volumes failed to retrieve all volumes after"
                " {attempts} attempts. Returning what we found.".format(
                    attempts=attempts))
        # list volumes didn't complete succesfully so just return what
        # we found
        return self._normalize_volumes(
            self._get_and_munchify(key=None, data=volumes))

    @_utils.cache_on_arguments()
    def list_volume_types(self, get_extra=True):
        """List all available volume types.

        :returns: A list of volume ``munch.Munch``.

        """
        data = self._volume_client.get(
            '/types',
            params=dict(is_public='None'),
            error_message='Error fetching volume_type list')
        return self._normalize_volume_types(
            self._get_and_munchify('volume_types', data))

    @_utils.cache_on_arguments()
    def list_availability_zone_names(self, unavailable=False):
        """List names of availability zones.

        :param bool unavailable: Whether or not to include unavailable zones
                                 in the output. Defaults to False.

        :returns: A list of availability zone names, or an empty list if the
                  list could not be fetched.
        """
        try:
            data = _adapter._json_response(
                self.compute.get('/os-availability-zone'))
        except OpenStackCloudHTTPError:
            self.log.debug(
                "Availability zone list could not be fetched",
                exc_info=True)
            return []
        zones = self._get_and_munchify('availabilityZoneInfo', data)
        ret = []
        for zone in zones:
            if zone['zoneState']['available'] or unavailable:
                ret.append(zone['zoneName'])
        return ret

    @_utils.cache_on_arguments()
    def list_flavors(self, get_extra=False):
        """List all available flavors.

        :param get_extra: Whether or not to fetch extra specs for each flavor.
                          Defaults to True. Default behavior value can be
                          overridden in clouds.yaml by setting
                          openstack.cloud.get_extra_specs to False.
        :returns: A list of flavor ``munch.Munch``.

        """
        data = _adapter._json_response(
            self.compute.get(
                '/flavors/detail', params=dict(is_public='None')),
            error_message="Error fetching flavor list")
        flavors = self._normalize_flavors(
            self._get_and_munchify('flavors', data))

        for flavor in flavors:
            if not flavor.extra_specs and get_extra:
                endpoint = "/flavors/{id}/os-extra_specs".format(
                    id=flavor.id)
                try:
                    data = _adapter._json_response(
                        self.compute.get(endpoint),
                        error_message="Error fetching flavor extra specs")
                    flavor.extra_specs = self._get_and_munchify(
                        'extra_specs', data)
                except OpenStackCloudHTTPError as e:
                    flavor.extra_specs = {}
                    self.log.debug(
                        'Fetching extra specs for flavor failed:'
                        ' %(msg)s', {'msg': str(e)})

        return flavors

    @_utils.cache_on_arguments(should_cache_fn=_no_pending_stacks)
    def list_stacks(self):
        """List all stacks.

        :returns: a list of ``munch.Munch`` containing the stack description.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        data = self._orchestration_client.get(
            '/stacks', error_message="Error fetching stack list")
        return self._normalize_stacks(
            self._get_and_munchify('stacks', data))

    def list_server_security_groups(self, server):
        """List all security groups associated with the given server.

        :returns: A list of security group ``munch.Munch``.
        """

        # Don't even try if we're a cloud that doesn't have them
        if not self._has_secgroups():
            return []

        data = _adapter._json_response(
            self.compute.get(
                '/servers/{server_id}/os-security-groups'.format(
                    server_id=server['id'])))
        return self._normalize_secgroups(
            self._get_and_munchify('security_groups', data))

    def _get_server_security_groups(self, server, security_groups):
        if not self._has_secgroups():
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        if not isinstance(server, dict):
            server = self.get_server(server, bare=True)

            if server is None:
                self.log.debug('Server %s not found', server)
                return None, None

        if not isinstance(security_groups, (list, tuple)):
            security_groups = [security_groups]

        sec_group_objs = []

        for sg in security_groups:
            if not isinstance(sg, dict):
                sg = self.get_security_group(sg)

                if sg is None:
                    self.log.debug('Security group %s not found for adding',
                                   sg)

                    return None, None

            sec_group_objs.append(sg)

        return server, sec_group_objs

    def add_server_security_groups(self, server, security_groups):
        """Add security groups to a server.

        Add existing security groups to an existing server. If the security
        groups are already present on the server this will continue unaffected.

        :returns: False if server or security groups are undefined, True
            otherwise.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        server, security_groups = self._get_server_security_groups(
            server, security_groups)

        if not (server and security_groups):
            return False

        for sg in security_groups:
            _adapter._json_response(self.compute.post(
                '/servers/%s/action' % server['id'],
                json={'addSecurityGroup': {'name': sg.name}}))

        return True

    def remove_server_security_groups(self, server, security_groups):
        """Remove security groups from a server

        Remove existing security groups from an existing server. If the
        security groups are not present on the server this will continue
        unaffected.

        :returns: False if server or security groups are undefined, True
            otherwise.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        server, security_groups = self._get_server_security_groups(
            server, security_groups)

        if not (server and security_groups):
            return False

        ret = True

        for sg in security_groups:
            try:
                _adapter._json_response(self.compute.post(
                    '/servers/%s/action' % server['id'],
                    json={'removeSecurityGroup': {'name': sg.name}}))

            except OpenStackCloudURINotFound:
                # NOTE(jamielennox): Is this ok? If we remove something that
                # isn't present should we just conclude job done or is that an
                # error? Nova returns ok if you try to add a group twice.
                self.log.debug(
                    "The security group %s was not present on server %s so "
                    "no action was performed", sg.name, server.name)
                ret = False

        return ret

    def list_security_groups(self, filters=None):
        """List all available security groups.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of security group ``munch.Munch``.

        """
        # Security groups not supported
        if not self._has_secgroups():
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        if not filters:
            filters = {}

        data = []
        # Handle neutron security groups
        if self._use_neutron_secgroups():
            # Neutron returns dicts, so no need to convert objects here.
            data = self._network_client.get(
                '/security-groups.json', params=filters,
                error_message="Error fetching security group list")
            return self._get_and_munchify('security_groups', data)

        # Handle nova security groups
        else:
            data = _adapter._json_response(self.compute.get(
                '/os-security-groups', params=filters))
        return self._normalize_secgroups(
            self._get_and_munchify('security_groups', data))

    def list_servers(self, detailed=False, all_projects=False, bare=False,
                     filters=None):
        """List all available servers.

        :param detailed: Whether or not to add detailed additional information.
                         Defaults to False.
        :param all_projects: Whether to list servers from all projects or just
                             the current auth scoped project.
        :param bare: Whether to skip adding any additional information to the
                     server record. Defaults to False, meaning the addresses
                     dict will be populated as needed from neutron. Setting
                     to True implies detailed = False.
        :param filters: Additional query parameters passed to the API server.

        :returns: A list of server ``munch.Munch``.

        """
        if (time.time() - self._servers_time) >= self._SERVER_AGE:
            # Since we're using cached data anyway, we don't need to
            # have more than one thread actually submit the list
            # servers task.  Let the first one submit it while holding
            # a lock, and the non-blocking acquire method will cause
            # subsequent threads to just skip this and use the old
            # data until it succeeds.
            # Initially when we never got data, block to retrieve some data.
            first_run = self._servers is None
            if self._servers_lock.acquire(first_run):
                try:
                    if not (first_run and self._servers is not None):
                        self._servers = self._list_servers(
                            detailed=detailed,
                            all_projects=all_projects,
                            bare=bare,
                            filters=filters)
                        self._servers_time = time.time()
                finally:
                    self._servers_lock.release()
        return self._servers

    def _list_servers(self, detailed=False, all_projects=False, bare=False,
                      filters=None):
        error_msg = "Error fetching server list on {cloud}:{region}:".format(
            cloud=self.name,
            region=self.config.region_name)

        params = filters or {}
        if all_projects:
            params['all_tenants'] = True
        data = _adapter._json_response(
            self.compute.get(
                '/servers/detail', params=params),
            error_message=error_msg)
        servers = self._normalize_servers(
            self._get_and_munchify('servers', data))
        return [
            self._expand_server(server, detailed, bare)
            for server in servers
        ]

    def list_server_groups(self):
        """List all available server groups.

        :returns: A list of server group dicts.

        """
        data = _adapter._json_response(
            self.compute.get('/os-server-groups'),
            error_message="Error fetching server group list")
        return self._get_and_munchify('server_groups', data)

    def get_compute_limits(self, name_or_id=None):
        """ Get compute limits for a project

        :param name_or_id: (optional) project name or ID to get limits for
                           if different from the current project
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the limits
        """
        params = {}
        project_id = None
        error_msg = "Failed to get limits"
        if name_or_id:

            proj = self.get_project(name_or_id)
            if not proj:
                raise OpenStackCloudException("project does not exist")
            project_id = proj.id
            params['tenant_id'] = project_id
            error_msg = "{msg} for the project: {project} ".format(
                msg=error_msg, project=name_or_id)

        data = _adapter._json_response(
            self.compute.get('/limits', params=params))
        limits = self._get_and_munchify('limits', data)
        return self._normalize_compute_limits(limits, project_id=project_id)

    @_utils.cache_on_arguments(should_cache_fn=_no_pending_images)
    def list_images(self, filter_deleted=True, show_all=False):
        """Get available images.

        :param filter_deleted: Control whether deleted images are returned.
        :param show_all: Show all images, including images that are shared
            but not accepted. (By default in glance v2 shared image that
            have not been accepted are not shown) show_all will override the
            value of filter_deleted to False.
        :returns: A list of glance images.
        """
        if show_all:
            filter_deleted = False
        # First, try to actually get images from glance, it's more efficient
        images = []
        params = {}
        image_list = []
        try:
            if self._is_client_version('image', 2):
                endpoint = '/images'
                if show_all:
                    params['member_status'] = 'all'
            else:
                endpoint = '/images/detail'

            response = self._image_client.get(endpoint, params=params)

        except keystoneauth1.exceptions.catalog.EndpointNotFound:
            # We didn't have glance, let's try nova
            # If this doesn't work - we just let the exception propagate
            response = _adapter._json_response(
                self.compute.get('/images/detail'))
        while 'next' in response:
            image_list.extend(meta.obj_list_to_munch(response['images']))
            endpoint = response['next']
            # next links from glance have the version prefix. If the catalog
            # has a versioned endpoint, then we can't append the next link to
            # it. Strip the absolute prefix (/v1/ or /v2/ to turn it into
            # a proper relative link.
            if endpoint.startswith('/v'):
                endpoint = endpoint[4:]
            response = self._image_client.get(endpoint)
        if 'images' in response:
            image_list.extend(meta.obj_list_to_munch(response['images']))
        else:
            image_list.extend(response)

        for image in image_list:
            # The cloud might return DELETED for invalid images.
            # While that's cute and all, that's an implementation detail.
            if not filter_deleted:
                images.append(image)
            elif image.status.lower() != 'deleted':
                images.append(image)
        return self._normalize_images(images)

    def list_floating_ip_pools(self):
        """List all available floating IP pools.

        NOTE: This function supports the nova-net view of the world. nova-net
        has been deprecated, so it's highly recommended to switch to using
        neutron. `get_external_ipv4_floating_networks` is what you should
        almost certainly be using.

        :returns: A list of floating IP pool ``munch.Munch``.

        """
        if not self._has_nova_extension('os-floating-ip-pools'):
            raise OpenStackCloudUnavailableExtension(
                'Floating IP pools extension is not available on target cloud')

        data = _adapter._json_response(
            self.compute.get('os-floating-ip-pools'),
            error_message="Error fetching floating IP pool list")
        pools = self._get_and_munchify('floating_ip_pools', data)
        return [{'name': p['name']} for p in pools]

    def _list_floating_ips(self, filters=None):
        if self._use_neutron_floating():
            try:
                return self._normalize_floating_ips(
                    self._neutron_list_floating_ips(filters))
            except OpenStackCloudURINotFound as e:
                # Nova-network don't support server-side floating ips
                # filtering, so it's safer to return and empty list than
                # to fallback to Nova which may return more results that
                # expected.
                if filters:
                    self.log.error(
                        "Neutron returned NotFound for floating IPs, which"
                        " means this cloud doesn't have neutron floating ips."
                        " shade can't fallback to trying Nova since nova"
                        " doesn't support server-side filtering when listing"
                        " floating ips and filters were given. If you do not"
                        " think shade should be attempting to list floating"
                        " ips on neutron, it is possible to control the"
                        " behavior by setting floating_ip_source to 'nova' or"
                        " None for cloud: %(cloud)s. If you are not already"
                        " using clouds.yaml to configure settings for your"
                        " cloud(s), and you want to configure this setting,"
                        " you will need a clouds.yaml file. For more"
                        " information, please see %(doc_url)s", {
                            'cloud': self.name,
                            'doc_url': _OCC_DOC_URL,
                        }
                    )
                    # We can't fallback to nova because we push-down filters.
                    # We got a 404 which means neutron doesn't exist. If the
                    # user
                    return []
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                # Fall-through, trying with Nova
        else:
            if filters:
                raise ValueError(
                    "Nova-network don't support server-side floating ips "
                    "filtering. Use the search_floatting_ips method instead"
                )

        floating_ips = self._nova_list_floating_ips()
        return self._normalize_floating_ips(floating_ips)

    def list_floating_ips(self, filters=None):
        """List all available floating IPs.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of floating IP ``munch.Munch``.

        """
        # If pushdown filters are specified and we do not have batched caching
        # enabled, bypass local caching and push down the filters.
        if filters and self._FLOAT_AGE == 0:
            return self._list_floating_ips(filters)

        if (time.time() - self._floating_ips_time) >= self._FLOAT_AGE:
            # Since we're using cached data anyway, we don't need to
            # have more than one thread actually submit the list
            # floating ips task.  Let the first one submit it while holding
            # a lock, and the non-blocking acquire method will cause
            # subsequent threads to just skip this and use the old
            # data until it succeeds.
            # Initially when we never got data, block to retrieve some data.
            first_run = self._floating_ips is None
            if self._floating_ips_lock.acquire(first_run):
                try:
                    if not (first_run and self._floating_ips is not None):
                        self._floating_ips = self._list_floating_ips()
                        self._floating_ips_time = time.time()
                finally:
                    self._floating_ips_lock.release()
        return self._floating_ips

    def _neutron_list_floating_ips(self, filters=None):
        if not filters:
            filters = {}
        data = self._network_client.get('/floatingips.json', params=filters)
        return self._get_and_munchify('floatingips', data)

    def _nova_list_floating_ips(self):
        try:
            data = _adapter._json_response(
                self.compute.get('/os-floating-ips'))
        except OpenStackCloudURINotFound:
            return []
        return self._get_and_munchify('floating_ips', data)

    def use_external_network(self):
        return self._use_external_network

    def use_internal_network(self):
        return self._use_internal_network

    def _reset_network_caches(self):
        # Variables to prevent us from going through the network finding
        # logic again if we've done it once. This is different from just
        # the cached value, since "None" is a valid value to find.
        with self._networks_lock:
            self._external_ipv4_networks = []
            self._external_ipv4_floating_networks = []
            self._internal_ipv4_networks = []
            self._external_ipv6_networks = []
            self._internal_ipv6_networks = []
            self._nat_destination_network = None
            self._default_network_network = None
            self._network_list_stamp = False

    def _set_interesting_networks(self):
        external_ipv4_networks = []
        external_ipv4_floating_networks = []
        internal_ipv4_networks = []
        external_ipv6_networks = []
        internal_ipv6_networks = []
        nat_destination = None
        default_network = None

        all_subnets = None

        # Filter locally because we have an or condition
        try:
            # TODO(mordred): Rackspace exposes neutron but it does not
            # work. I think that overriding what the service catalog
            # reports should be a thing os-client-config should handle
            # in a vendor profile - but for now it does not. That means
            # this search_networks can just totally fail. If it does
            # though, that's fine, clearly the neutron introspection is
            # not going to work.
            all_networks = self.list_networks()
        except OpenStackCloudException:
            self._network_list_stamp = True
            return

        for network in all_networks:

            # External IPv4 networks
            if (network['name'] in self._external_ipv4_names
                    or network['id'] in self._external_ipv4_names):
                external_ipv4_networks.append(network)
            elif ((('router:external' in network
                    and network['router:external']) or
                    network.get('provider:physical_network')) and
                    network['name'] not in self._internal_ipv4_names and
                    network['id'] not in self._internal_ipv4_names):
                external_ipv4_networks.append(network)

            # External Floating IPv4 networks
            if ('router:external' in network and network['router:external']):
                external_ipv4_floating_networks.append(network)

            # Internal networks
            if (network['name'] in self._internal_ipv4_names
                    or network['id'] in self._internal_ipv4_names):
                internal_ipv4_networks.append(network)
            elif (not network.get('router:external', False) and
                    not network.get('provider:physical_network') and
                    network['name'] not in self._external_ipv4_names and
                    network['id'] not in self._external_ipv4_names):
                internal_ipv4_networks.append(network)

            # External networks
            if (network['name'] in self._external_ipv6_names
                    or network['id'] in self._external_ipv6_names):
                external_ipv6_networks.append(network)
            elif (network.get('router:external') and
                    network['name'] not in self._internal_ipv6_names and
                    network['id'] not in self._internal_ipv6_names):
                external_ipv6_networks.append(network)

            # Internal networks
            if (network['name'] in self._internal_ipv6_names
                    or network['id'] in self._internal_ipv6_names):
                internal_ipv6_networks.append(network)
            elif (not network.get('router:external', False) and
                    network['name'] not in self._external_ipv6_names and
                    network['id'] not in self._external_ipv6_names):
                internal_ipv6_networks.append(network)

            # NAT Destination
            if self._nat_destination in (
                    network['name'], network['id']):
                if nat_destination:
                    raise OpenStackCloudException(
                        'Multiple networks were found matching'
                        ' {nat_net} which is the network configured'
                        ' to be the NAT destination. Please check your'
                        ' cloud resources. It is probably a good idea'
                        ' to configure this network by ID rather than'
                        ' by name.'.format(
                            nat_net=self._nat_destination))
                nat_destination = network
            elif self._nat_destination is None:
                # TODO(mordred) need a config value for floating
                # ips for this cloud so that we can skip this
                # No configured nat destination, we have to figured
                # it out.
                if all_subnets is None:
                    try:
                        all_subnets = self.list_subnets()
                    except OpenStackCloudException:
                        # Thanks Rackspace broken neutron
                        all_subnets = []

                for subnet in all_subnets:
                    # TODO(mordred) trap for detecting more than
                    # one network with a gateway_ip without a config
                    if ('gateway_ip' in subnet and subnet['gateway_ip']
                            and network['id'] == subnet['network_id']):
                        nat_destination = network
                        break

            # Default network
            if self._default_network in (
                    network['name'], network['id']):
                if default_network:
                    raise OpenStackCloudException(
                        'Multiple networks were found matching'
                        ' {default_net} which is the network'
                        ' configured to be the default interface'
                        ' network. Please check your cloud resources.'
                        ' It is probably a good idea'
                        ' to configure this network by ID rather than'
                        ' by name.'.format(
                            default_net=self._default_network))
                default_network = network

        # Validate config vs. reality
        for net_name in self._external_ipv4_names:
            if net_name not in [net['name'] for net in external_ipv4_networks]:
                raise OpenStackCloudException(
                    "Networks: {network} was provided for external IPv4"
                    " access and those networks could not be found".format(
                        network=net_name))

        for net_name in self._internal_ipv4_names:
            if net_name not in [net['name'] for net in internal_ipv4_networks]:
                raise OpenStackCloudException(
                    "Networks: {network} was provided for internal IPv4"
                    " access and those networks could not be found".format(
                        network=net_name))

        for net_name in self._external_ipv6_names:
            if net_name not in [net['name'] for net in external_ipv6_networks]:
                raise OpenStackCloudException(
                    "Networks: {network} was provided for external IPv6"
                    " access and those networks could not be found".format(
                        network=net_name))

        for net_name in self._internal_ipv6_names:
            if net_name not in [net['name'] for net in internal_ipv6_networks]:
                raise OpenStackCloudException(
                    "Networks: {network} was provided for internal IPv6"
                    " access and those networks could not be found".format(
                        network=net_name))

        if self._nat_destination and not nat_destination:
            raise OpenStackCloudException(
                'Network {network} was configured to be the'
                ' destination for inbound NAT but it could not be'
                ' found'.format(
                    network=self._nat_destination))

        if self._default_network and not default_network:
            raise OpenStackCloudException(
                'Network {network} was configured to be the'
                ' default network interface but it could not be'
                ' found'.format(
                    network=self._default_network))

        self._external_ipv4_networks = external_ipv4_networks
        self._external_ipv4_floating_networks = external_ipv4_floating_networks
        self._internal_ipv4_networks = internal_ipv4_networks
        self._external_ipv6_networks = external_ipv6_networks
        self._internal_ipv6_networks = internal_ipv6_networks
        self._nat_destination_network = nat_destination
        self._default_network_network = default_network

    def _find_interesting_networks(self):
        if self._networks_lock.acquire():
            try:
                if self._network_list_stamp:
                    return
                if (not self._use_external_network
                        and not self._use_internal_network):
                    # Both have been flagged as skip - don't do a list
                    return
                if not self.has_service('network'):
                    return
                self._set_interesting_networks()
                self._network_list_stamp = True
            finally:
                self._networks_lock.release()

    def get_nat_destination(self):
        """Return the network that is configured to be the NAT destination.

        :returns: A network dict if one is found
        """
        self._find_interesting_networks()
        return self._nat_destination_network

    def get_default_network(self):
        """Return the network that is configured to be the default interface.

        :returns: A network dict if one is found
        """
        self._find_interesting_networks()
        return self._default_network_network

    def get_external_networks(self):
        """Return the networks that are configured to route northbound.

        This should be avoided in favor of the specific ipv4/ipv6 method,
        but is here for backwards compatibility.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return list(
            set(self._external_ipv4_networks) |
            set(self._external_ipv6_networks))

    def get_internal_networks(self):
        """Return the networks that are configured to not route northbound.

        This should be avoided in favor of the specific ipv4/ipv6 method,
        but is here for backwards compatibility.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return list(
            set(self._internal_ipv4_networks) |
            set(self._internal_ipv6_networks))

    def get_external_ipv4_networks(self):
        """Return the networks that are configured to route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._external_ipv4_networks

    def get_external_ipv4_floating_networks(self):
        """Return the networks that are configured to route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._external_ipv4_floating_networks

    def get_internal_ipv4_networks(self):
        """Return the networks that are configured to not route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._internal_ipv4_networks

    def get_external_ipv6_networks(self):
        """Return the networks that are configured to route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._external_ipv6_networks

    def get_internal_ipv6_networks(self):
        """Return the networks that are configured to not route northbound.

        :returns: A list of network ``munch.Munch`` if one is found
        """
        self._find_interesting_networks()
        return self._internal_ipv6_networks

    def _has_floating_ips(self):
        if not self._floating_ip_source:
            return False
        else:
            return self._floating_ip_source in ('nova', 'neutron')

    def _use_neutron_floating(self):
        return (self.has_service('network')
                and self._floating_ip_source == 'neutron')

    def _has_secgroups(self):
        if not self.secgroup_source:
            return False
        else:
            return self.secgroup_source.lower() in ('nova', 'neutron')

    def _use_neutron_secgroups(self):
        return (self.has_service('network')
                and self.secgroup_source == 'neutron')

    def get_keypair(self, name_or_id, filters=None):
        """Get a keypair by name or ID.

        :param name_or_id: Name or ID of the keypair.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A keypair ``munch.Munch`` or None if no matching keypair is
                  found.
        """
        return _utils._get_entity(self, 'keypair', name_or_id, filters)

    def get_network(self, name_or_id, filters=None):
        """Get a network by name or ID.

        :param name_or_id: Name or ID of the network.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A network ``munch.Munch`` or None if no matching network is
                 found.

        """
        return _utils._get_entity(self, 'network', name_or_id, filters)

    def get_network_by_id(self, id):
        """ Get a network by ID

        :param id: ID of the network.
        :returns: A network ``munch.Munch``.
        """
        data = self._network_client.get(
            '/networks/{id}'.format(id=id),
            error_message="Error getting network with ID {id}".format(id=id)
        )
        network = self._get_and_munchify('network', data)

        return network

    def get_router(self, name_or_id, filters=None):
        """Get a router by name or ID.

        :param name_or_id: Name or ID of the router.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A router ``munch.Munch`` or None if no matching router is
                  found.

        """
        return _utils._get_entity(self, 'router', name_or_id, filters)

    def get_subnet(self, name_or_id, filters=None):
        """Get a subnet by name or ID.

        :param name_or_id: Name or ID of the subnet.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

        :returns: A subnet ``munch.Munch`` or None if no matching subnet is
                  found.

        """
        return _utils._get_entity(self, 'subnet', name_or_id, filters)

    def get_subnet_by_id(self, id):
        """ Get a subnet by ID

        :param id: ID of the subnet.
        :returns: A subnet ``munch.Munch``.
        """
        data = self._network_client.get(
            '/subnets/{id}'.format(id=id),
            error_message="Error getting subnet with ID {id}".format(id=id)
        )
        subnet = self._get_and_munchify('subnet', data)

        return subnet

    def get_port(self, name_or_id, filters=None):
        """Get a port by name or ID.

        :param name_or_id: Name or ID of the port.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A port ``munch.Munch`` or None if no matching port is found.

        """
        return _utils._get_entity(self, 'port', name_or_id, filters)

    def get_port_by_id(self, id):
        """ Get a port by ID

        :param id: ID of the port.
        :returns: A port ``munch.Munch``.
        """
        data = self._network_client.get(
            '/ports/{id}'.format(id=id),
            error_message="Error getting port with ID {id}".format(id=id)
        )
        port = self._get_and_munchify('port', data)

        return port

    def get_qos_policy(self, name_or_id, filters=None):
        """Get a QoS policy by name or ID.

        :param name_or_id: Name or ID of the policy.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A policy ``munch.Munch`` or None if no matching network is
                 found.

        """
        return _utils._get_entity(
            self, 'qos_policie', name_or_id, filters)

    def get_volume(self, name_or_id, filters=None):
        """Get a volume by name or ID.

        :param name_or_id: Name or ID of the volume.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``munch.Munch`` or None if no matching volume is
                  found.

        """
        return _utils._get_entity(self, 'volume', name_or_id, filters)

    def get_volume_by_id(self, id):
        """ Get a volume by ID

        :param id: ID of the volume.
        :returns: A volume ``munch.Munch``.
        """
        data = self._volume_client.get(
            '/volumes/{id}'.format(id=id),
            error_message="Error getting volume with ID {id}".format(id=id)
        )
        volume = self._normalize_volume(
            self._get_and_munchify('volume', data))

        return volume

    def get_volume_type(self, name_or_id, filters=None):
        """Get a volume type by name or ID.

        :param name_or_id: Name or ID of the volume.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``munch.Munch`` or None if no matching volume is
                  found.

        """
        return _utils._get_entity(
            self, 'volume_type', name_or_id, filters)

    def get_flavor(self, name_or_id, filters=None, get_extra=True):
        """Get a flavor by name or ID.

        :param name_or_id: Name or ID of the flavor.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :param get_extra:
             Whether or not the list_flavors call should get the extra flavor
             specs.

        :returns: A flavor ``munch.Munch`` or None if no matching flavor is
            found.

        """
        search_func = functools.partial(
            self.search_flavors, get_extra=get_extra)
        return _utils._get_entity(self, search_func, name_or_id, filters)

    def get_flavor_by_id(self, id, get_extra=False):
        """ Get a flavor by ID

        :param id: ID of the flavor.
        :param get_extra:
             Whether or not the list_flavors call should get the extra flavor
             specs.
        :returns: A flavor ``munch.Munch``.
        """
        data = _adapter._json_response(
            self.compute.get('/flavors/{id}'.format(id=id)),
            error_message="Error getting flavor with ID {id}".format(id=id)
        )
        flavor = self._normalize_flavor(
            self._get_and_munchify('flavor', data))

        if not flavor.extra_specs and get_extra:
            endpoint = "/flavors/{id}/os-extra_specs".format(
                id=flavor.id)
            try:
                data = _adapter._json_response(
                    self.compute.get(endpoint),
                    error_message="Error fetching flavor extra specs")
                flavor.extra_specs = self._get_and_munchify(
                    'extra_specs', data)
            except OpenStackCloudHTTPError as e:
                flavor.extra_specs = {}
                self.log.debug(
                    'Fetching extra specs for flavor failed:'
                    ' %(msg)s', {'msg': str(e)})

        return flavor

    def get_security_group(self, name_or_id, filters=None):
        """Get a security group by name or ID.

        :param name_or_id: Name or ID of the security group.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A security group ``munch.Munch`` or None if no matching
                  security group is found.

        """
        return _utils._get_entity(
            self, 'security_group', name_or_id, filters)

    def get_security_group_by_id(self, id):
        """ Get a security group by ID

        :param id: ID of the security group.
        :returns: A security group ``munch.Munch``.
        """
        if not self._has_secgroups():
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )
        error_message = ("Error getting security group with"
                         " ID {id}".format(id=id))
        if self._use_neutron_secgroups():
            data = self._network_client.get(
                '/security-groups/{id}'.format(id=id),
                error_message=error_message)
        else:
            data = _adapter._json_response(
                self.compute.get(
                    '/os-security-groups/{id}'.format(id=id)),
                error_message=error_message)
        return self._normalize_secgroup(
            self._get_and_munchify('security_group', data))

    def get_server_console(self, server, length=None):
        """Get the console log for a server.

        :param server: The server to fetch the console log for. Can be either
                       a server dict or the Name or ID of the server.
        :param int length: The number of lines you would like to retrieve from
                           the end of the log. (optional, defaults to all)

        :returns: A string containing the text of the console log or an
                  empty string if the cloud does not support console logs.
        :raises: OpenStackCloudException if an invalid server argument is given
                 or if something else unforseen happens
        """

        if not isinstance(server, dict):
            server = self.get_server(server, bare=True)

        if not server:
            raise OpenStackCloudException(
                "Console log requested for invalid server")

        try:
            return self._get_server_console_output(server['id'], length)
        except OpenStackCloudBadRequest:
            return ""

    def _get_server_console_output(self, server_id, length=None):
            data = _adapter._json_response(self.compute.post(
                '/servers/{server_id}/action'.format(server_id=server_id),
                json={'os-getConsoleOutput': {'length': length}}))
            return self._get_and_munchify('output', data)

    def get_server(
            self, name_or_id=None, filters=None, detailed=False, bare=False,
            all_projects=False):
        """Get a server by name or ID.

        :param name_or_id: Name or ID of the server.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :param detailed: Whether or not to add detailed additional information.
                         Defaults to False.
        :param bare: Whether to skip adding any additional information to the
                     server record. Defaults to False, meaning the addresses
                     dict will be populated as needed from neutron. Setting
                     to True implies detailed = False.
        :param all_projects: Whether to get server from all projects or just
                             the current auth scoped project.

        :returns: A server ``munch.Munch`` or None if no matching server is
                  found.

        """
        searchfunc = functools.partial(self.search_servers,
                                       detailed=detailed, bare=True,
                                       all_projects=all_projects)
        server = _utils._get_entity(self, searchfunc, name_or_id, filters)
        return self._expand_server(server, detailed, bare)

    def _expand_server(self, server, detailed, bare):
        if bare or not server:
            return server
        elif detailed:
            return meta.get_hostvars_from_server(self, server)
        else:
            return meta.add_server_interfaces(self, server)

    def get_server_by_id(self, id):
        data = _adapter._json_response(
            self.compute.get('/servers/{id}'.format(id=id)))
        server = self._get_and_munchify('server', data)
        return meta.add_server_interfaces(self, self._normalize_server(server))

    def get_server_group(self, name_or_id=None, filters=None):
        """Get a server group by name or ID.

        :param name_or_id: Name or ID of the server group.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'policy': 'affinity',
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A server groups dict or None if no matching server group
                  is found.

        """
        return _utils._get_entity(self, 'server_group', name_or_id,
                                  filters)

    def get_image(self, name_or_id, filters=None):
        """Get an image by name or ID.

        :param name_or_id: Name or ID of the image.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: An image ``munch.Munch`` or None if no matching image
                  is found

        """
        return _utils._get_entity(self, 'image', name_or_id, filters)

    def get_image_by_id(self, id):
        """ Get a image by ID

        :param id: ID of the image.
        :returns: An image ``munch.Munch``.
        """
        data = self._image_client.get(
            '/images/{id}'.format(id=id),
            error_message="Error getting image with ID {id}".format(id=id)
        )
        key = 'image' if 'image' in data else None
        image = self._normalize_image(
            self._get_and_munchify(key, data))

        return image

    def download_image(
            self, name_or_id, output_path=None, output_file=None,
            chunk_size=1024):
        """Download an image by name or ID

        :param str name_or_id: Name or ID of the image.
        :param output_path: the output path to write the image to. Either this
            or output_file must be specified
        :param output_file: a file object (or file-like object) to write the
            image data to. Only write() will be called on this object. Either
            this or output_path must be specified
        :param int chunk_size: size in bytes to read from the wire and buffer
            at one time. Defaults to 1024

        :raises: OpenStackCloudException in the event download_image is called
            without exactly one of either output_path or output_file
        :raises: OpenStackCloudResourceNotFound if no images are found matching
            the name or ID provided
        """
        if output_path is None and output_file is None:
            raise OpenStackCloudException('No output specified, an output path'
                                          ' or file object is necessary to '
                                          'write the image data to')
        elif output_path is not None and output_file is not None:
            raise OpenStackCloudException('Both an output path and file object'
                                          ' were provided, however only one '
                                          'can be used at once')

        image = self.search_images(name_or_id)
        if len(image) == 0:
            raise OpenStackCloudResourceNotFound(
                "No images with name or ID %s were found" % name_or_id, None)
        if self._is_client_version('image', 2):
            endpoint = '/images/{id}/file'.format(id=image[0]['id'])
        else:
            endpoint = '/images/{id}'.format(id=image[0]['id'])

        response = self._image_client.get(endpoint, stream=True)

        with _utils.shade_exceptions("Unable to download image"):
            if output_path:
                with open(output_path, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        fd.write(chunk)
                return
            elif output_file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    output_file.write(chunk)
                return

    def get_floating_ip(self, id, filters=None):
        """Get a floating IP by ID

        :param id: ID of the floating IP.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A floating IP ``munch.Munch`` or None if no matching floating
                  IP is found.

        """
        return _utils._get_entity(self, 'floating_ip', id, filters)

    def get_floating_ip_by_id(self, id):
        """ Get a floating ip by ID

        :param id: ID of the floating ip.
        :returns: A floating ip ``munch.Munch``.
        """
        error_message = "Error getting floating ip with ID {id}".format(id=id)

        if self._use_neutron_floating():
            data = self._network_client.get(
                '/floatingips/{id}'.format(id=id),
                error_message=error_message)
            return self._normalize_floating_ip(
                self._get_and_munchify('floatingip', data))
        else:
            data = _adapter._json_response(
                self.compute.get('/os-floating-ips/{id}'.format(id=id)),
                error_message=error_message)
            return self._normalize_floating_ip(
                self._get_and_munchify('floating_ip', data))

    def get_stack(self, name_or_id, filters=None, resolve_outputs=True):
        """Get exactly one stack.

        :param name_or_id: Name or ID of the desired stack.
        :param filters: a dict containing additional filters to use. e.g.
                {'stack_status': 'CREATE_COMPLETE'}
        :param resolve_outputs: If True, then outputs for this
                stack will be resolved

        :returns: a ``munch.Munch`` containing the stack description

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call or if multiple matches are found.
        """

        def _search_one_stack(name_or_id=None, filters=None):
            # stack names are mandatory and enforced unique in the project
            # so a StackGet can always be used for name or ID.
            try:
                url = '/stacks/{name_or_id}'.format(name_or_id=name_or_id)
                if not resolve_outputs:
                    url = '{url}?resolve_outputs=False'.format(url=url)
                data = self._orchestration_client.get(
                    url,
                    error_message="Error fetching stack")
                stack = self._get_and_munchify('stack', data)
                # Treat DELETE_COMPLETE stacks as a NotFound
                if stack['stack_status'] == 'DELETE_COMPLETE':
                    return []
            except OpenStackCloudURINotFound:
                return []
            stack = self._normalize_stack(stack)
            return _utils._filter_list([stack], name_or_id, filters)

        return _utils._get_entity(
            self, _search_one_stack, name_or_id, filters)

    def create_keypair(self, name, public_key=None):
        """Create a new keypair.

        :param name: Name of the keypair being created.
        :param public_key: Public key for the new keypair.

        :raises: OpenStackCloudException on operation error.
        """
        keypair = {
            'name': name,
        }
        if public_key:
            keypair['public_key'] = public_key
        data = _adapter._json_response(
            self.compute.post(
                '/os-keypairs',
                json={'keypair': keypair}),
            error_message="Unable to create keypair {name}".format(name=name))
        return self._normalize_keypair(
            self._get_and_munchify('keypair', data))

    def delete_keypair(self, name):
        """Delete a keypair.

        :param name: Name of the keypair to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        try:
            _adapter._json_response(self.compute.delete(
                '/os-keypairs/{name}'.format(name=name)))
        except OpenStackCloudURINotFound:
            self.log.debug("Keypair %s not found for deleting", name)
            return False
        return True

    def create_network(self, name, shared=False, admin_state_up=True,
                       external=False, provider=None, project_id=None,
                       availability_zone_hints=None):
        """Create a network.

        :param string name: Name of the network being created.
        :param bool shared: Set the network as shared.
        :param bool admin_state_up: Set the network administrative state to up.
        :param bool external: Whether this network is externally accessible.
        :param dict provider: A dict of network provider options. Example::

           { 'network_type': 'vlan', 'segmentation_id': 'vlan1' }
        :param string project_id: Specify the project ID this network
            will be created on (admin-only).
        :param types.ListType availability_zone_hints: A list of availability
            zone hints.

        :returns: The network object.
        :raises: OpenStackCloudException on operation error.
        """
        network = {
            'name': name,
            'admin_state_up': admin_state_up,
        }

        if shared:
            network['shared'] = shared

        if project_id is not None:
            network['tenant_id'] = project_id

        if availability_zone_hints is not None:
            if not isinstance(availability_zone_hints, list):
                raise OpenStackCloudException(
                    "Parameter 'availability_zone_hints' must be a list")
            if not self._has_neutron_extension('network_availability_zone'):
                raise OpenStackCloudUnavailableExtension(
                    'network_availability_zone extension is not available on '
                    'target cloud')
            network['availability_zone_hints'] = availability_zone_hints

        if provider:
            if not isinstance(provider, dict):
                raise OpenStackCloudException(
                    "Parameter 'provider' must be a dict")
            # Only pass what we know
            for attr in ('physical_network', 'network_type',
                         'segmentation_id'):
                if attr in provider:
                    arg = "provider:" + attr
                    network[arg] = provider[attr]

        # Do not send 'router:external' unless it is explicitly
        # set since sending it *might* cause "Forbidden" errors in
        # some situations. It defaults to False in the client, anyway.
        if external:
            network['router:external'] = True

        data = self._network_client.post("/networks.json",
                                         json={'network': network})

        # Reset cache so the new network is picked up
        self._reset_network_caches()
        return self._get_and_munchify('network', data)

    def delete_network(self, name_or_id):
        """Delete a network.

        :param name_or_id: Name or ID of the network being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        network = self.get_network(name_or_id)
        if not network:
            self.log.debug("Network %s not found for deleting", name_or_id)
            return False

        self._network_client.delete(
            "/networks/{network_id}.json".format(network_id=network['id']))

        # Reset cache so the deleted network is removed
        self._reset_network_caches()

        return True

    @_utils.valid_kwargs("name", "description", "shared", "default",
                         "project_id")
    def create_qos_policy(self, **kwargs):
        """Create a QoS policy.

        :param string name: Name of the QoS policy being created.
        :param string description: Description of created QoS policy.
        :param bool shared: Set the QoS policy as shared.
        :param bool default: Set the QoS policy as default for project.
        :param string project_id: Specify the project ID this QoS policy
            will be created on (admin-only).

        :returns: The QoS policy object.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        default = kwargs.pop("default", None)
        if default is not None:
            if self._has_neutron_extension('qos-default'):
                kwargs['is_default'] = default
            else:
                self.log.debug("'qos-default' extension is not available on "
                               "target cloud")

        data = self._network_client.post("/qos/policies.json",
                                         json={'policy': kwargs})
        return self._get_and_munchify('policy', data)

    @_utils.valid_kwargs("name", "description", "shared", "default",
                         "project_id")
    def update_qos_policy(self, name_or_id, **kwargs):
        """Update an existing QoS policy.

        :param string name_or_id:
           Name or ID of the QoS policy to update.
        :param string policy_name:
           The new name of the QoS policy.
        :param string description:
            The new description of the QoS policy.
        :param bool shared:
            If True, the QoS policy will be set as shared.
        :param bool default:
            If True, the QoS policy will be set as default for project.

        :returns: The updated QoS policy object.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        default = kwargs.pop("default", None)
        if default is not None:
            if self._has_neutron_extension('qos-default'):
                kwargs['is_default'] = default
            else:
                self.log.debug("'qos-default' extension is not available on "
                               "target cloud")

        if not kwargs:
            self.log.debug("No QoS policy data to update")
            return

        curr_policy = self.get_qos_policy(name_or_id)
        if not curr_policy:
            raise OpenStackCloudException(
                "QoS policy %s not found." % name_or_id)

        data = self._network_client.put(
            "/qos/policies/{policy_id}.json".format(
                policy_id=curr_policy['id']),
            json={'policy': kwargs})
        return self._get_and_munchify('policy', data)

    def delete_qos_policy(self, name_or_id):
        """Delete a QoS policy.

        :param name_or_id: Name or ID of the policy being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')
        policy = self.get_qos_policy(name_or_id)
        if not policy:
            self.log.debug("QoS policy %s not found for deleting", name_or_id)
            return False

        self._network_client.delete(
            "/qos/policies/{policy_id}.json".format(policy_id=policy['id']))

        return True

    def search_qos_bandwidth_limit_rules(self, policy_name_or_id, rule_id=None,
                                         filters=None):
        """Search QoS bandwidth limit rules

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rules should be associated.
        :param string rule_id: ID of searched rule.
        :param filters: a dict containing additional filters to use. e.g.
                        {'max_kbps': 1000}

        :returns: a list of ``munch.Munch`` containing the bandwidth limit
            rule descriptions.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        rules = self.list_qos_bandwidth_limit_rules(policy_name_or_id, filters)
        return _utils._filter_list(rules, rule_id, filters)

    def list_qos_bandwidth_limit_rules(self, policy_name_or_id, filters=None):
        """List all available QoS bandwith limit rules.

        :param string policy_name_or_id: Name or ID of the QoS policy from
            from rules should be listed.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of ``munch.Munch`` containing rule info.

        :raises: ``OpenStackCloudResourceNotFound`` if QoS policy will not be
            found.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        data = self._network_client.get(
            "/qos/policies/{policy_id}/bandwidth_limit_rules.json".format(
                policy_id=policy['id']),
            params=filters,
            error_message="Error fetching QoS bandwith limit rules from "
                          "{policy}".format(policy=policy['id']))
        return self._get_and_munchify('bandwidth_limit_rules', data)

    def get_qos_bandwidth_limit_rule(self, policy_name_or_id, rule_id):
        """Get a QoS bandwidth limit rule by name or ID.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param rule_id: ID of the rule.

        :returns: A bandwidth limit rule ``munch.Munch`` or None if
            no matching rule is found.

        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        data = self._network_client.get(
            "/qos/policies/{policy_id}/bandwidth_limit_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id),
            error_message="Error fetching QoS bandwith limit rule {rule_id} "
                          "from {policy}".format(rule_id=rule_id,
                                                 policy=policy['id']))
        return self._get_and_munchify('bandwidth_limit_rule', data)

    @_utils.valid_kwargs("max_burst_kbps", "direction")
    def create_qos_bandwidth_limit_rule(self, policy_name_or_id, max_kbps,
                                        **kwargs):
        """Create a QoS bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param int max_kbps: Maximum bandwidth limit value
            (in kilobits per second).
        :param int max_burst_kbps: Maximum burst value (in kilobits).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be limited.

        :returns: The QoS bandwidth limit rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        if kwargs.get("direction") is not None:
            if not self._has_neutron_extension('qos-bw-limit-direction'):
                kwargs.pop("direction")
                self.log.debug(
                    "'qos-bw-limit-direction' extension is not available on "
                    "target cloud")

        kwargs['max_kbps'] = max_kbps
        data = self._network_client.post(
            "/qos/policies/{policy_id}/bandwidth_limit_rules".format(
                policy_id=policy['id']),
            json={'bandwidth_limit_rule': kwargs})
        return self._get_and_munchify('bandwidth_limit_rule', data)

    @_utils.valid_kwargs("max_kbps", "max_burst_kbps", "direction")
    def update_qos_bandwidth_limit_rule(self, policy_name_or_id, rule_id,
                                        **kwargs):
        """Update a QoS bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.
        :param int max_kbps: Maximum bandwidth limit value
            (in kilobits per second).
        :param int max_burst_kbps: Maximum burst value (in kilobits).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be limited.

        :returns: The updated QoS bandwidth limit rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        if kwargs.get("direction") is not None:
            if not self._has_neutron_extension('qos-bw-limit-direction'):
                kwargs.pop("direction")
                self.log.debug(
                    "'qos-bw-limit-direction' extension is not available on "
                    "target cloud")

        if not kwargs:
            self.log.debug("No QoS bandwidth limit rule data to update")
            return

        curr_rule = self.get_qos_bandwidth_limit_rule(
            policy_name_or_id, rule_id)
        if not curr_rule:
            raise OpenStackCloudException(
                "QoS bandwidth_limit_rule {rule_id} not found in policy "
                "{policy_id}".format(rule_id=rule_id,
                                     policy_id=policy['id']))

        data = self._network_client.put(
            "/qos/policies/{policy_id}/bandwidth_limit_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id),
            json={'bandwidth_limit_rule': kwargs})
        return self._get_and_munchify('bandwidth_limit_rule', data)

    def delete_qos_bandwidth_limit_rule(self, policy_name_or_id, rule_id):
        """Delete a QoS bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.

        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        try:
            self._network_client.delete(
                "/qos/policies/{policy}/bandwidth_limit_rules/{rule}.json".
                format(policy=policy['id'], rule=rule_id))
        except OpenStackCloudURINotFound:
            self.log.debug(
                "QoS bandwidth limit rule {rule_id} not found in policy "
                "{policy_id}. Ignoring.".format(rule_id=rule_id,
                                                policy_id=policy['id']))
            return False

        return True

    def search_qos_dscp_marking_rules(self, policy_name_or_id, rule_id=None,
                                      filters=None):
        """Search QoS DSCP marking rules

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rules should be associated.
        :param string rule_id: ID of searched rule.
        :param filters: a dict containing additional filters to use. e.g.
                        {'dscp_mark': 32}

        :returns: a list of ``munch.Munch`` containing the dscp marking
            rule descriptions.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        rules = self.list_qos_dscp_marking_rules(policy_name_or_id, filters)
        return _utils._filter_list(rules, rule_id, filters)

    def list_qos_dscp_marking_rules(self, policy_name_or_id, filters=None):
        """List all available QoS DSCP marking rules.

        :param string policy_name_or_id: Name or ID of the QoS policy from
            from rules should be listed.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of ``munch.Munch`` containing rule info.

        :raises: ``OpenStackCloudResourceNotFound`` if QoS policy will not be
            found.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        data = self._network_client.get(
            "/qos/policies/{policy_id}/dscp_marking_rules.json".format(
                policy_id=policy['id']),
            params=filters,
            error_message="Error fetching QoS DSCP marking rules from "
                          "{policy}".format(policy=policy['id']))
        return meta.get_and_munchify('dscp_marking_rules', data)

    def get_qos_dscp_marking_rule(self, policy_name_or_id, rule_id):
        """Get a QoS DSCP marking rule by name or ID.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param rule_id: ID of the rule.

        :returns: A bandwidth limit rule ``munch.Munch`` or None if
            no matching rule is found.

        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        data = self._network_client.get(
            "/qos/policies/{policy_id}/dscp_marking_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id),
            error_message="Error fetching QoS DSCP marking rule {rule_id} "
                          "from {policy}".format(rule_id=rule_id,
                                                 policy=policy['id']))
        return meta.get_and_munchify('dscp_marking_rule', data)

    def create_qos_dscp_marking_rule(self, policy_name_or_id, dscp_mark):
        """Create a QoS DSCP marking rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param int dscp_mark: DSCP mark value

        :returns: The QoS DSCP marking rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        body = {
            'dscp_mark': dscp_mark
        }
        data = self._network_client.post(
            "/qos/policies/{policy_id}/dscp_marking_rules".format(
                policy_id=policy['id']),
            json={'dscp_marking_rule': body})
        return meta.get_and_munchify('dscp_marking_rule', data)

    @_utils.valid_kwargs("dscp_mark")
    def update_qos_dscp_marking_rule(self, policy_name_or_id, rule_id,
                                     **kwargs):
        """Update a QoS DSCP marking rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.
        :param int dscp_mark: DSCP mark value

        :returns: The updated QoS bandwidth limit rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        if not kwargs:
            self.log.debug("No QoS DSCP marking rule data to update")
            return

        curr_rule = self.get_qos_dscp_marking_rule(
            policy_name_or_id, rule_id)
        if not curr_rule:
            raise OpenStackCloudException(
                "QoS dscp_marking_rule {rule_id} not found in policy "
                "{policy_id}".format(rule_id=rule_id,
                                     policy_id=policy['id']))

        data = self._network_client.put(
            "/qos/policies/{policy_id}/dscp_marking_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id),
            json={'dscp_marking_rule': kwargs})
        return meta.get_and_munchify('dscp_marking_rule', data)

    def delete_qos_dscp_marking_rule(self, policy_name_or_id, rule_id):
        """Delete a QoS DSCP marking rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.

        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        try:
            self._network_client.delete(
                "/qos/policies/{policy}/dscp_marking_rules/{rule}.json".
                format(policy=policy['id'], rule=rule_id))
        except OpenStackCloudURINotFound:
            self.log.debug(
                "QoS DSCP marking rule {rule_id} not found in policy "
                "{policy_id}. Ignoring.".format(rule_id=rule_id,
                                                policy_id=policy['id']))
            return False

        return True

    def search_qos_minimum_bandwidth_rules(self, policy_name_or_id,
                                           rule_id=None, filters=None):
        """Search QoS minimum bandwidth rules

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rules should be associated.
        :param string rule_id: ID of searched rule.
        :param filters: a dict containing additional filters to use. e.g.
                        {'min_kbps': 1000}

        :returns: a list of ``munch.Munch`` containing the bandwidth limit
            rule descriptions.

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        rules = self.list_qos_minimum_bandwidth_rules(
            policy_name_or_id, filters)
        return _utils._filter_list(rules, rule_id, filters)

    def list_qos_minimum_bandwidth_rules(self, policy_name_or_id,
                                         filters=None):
        """List all available QoS minimum bandwith rules.

        :param string policy_name_or_id: Name or ID of the QoS policy from
            from rules should be listed.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of ``munch.Munch`` containing rule info.

        :raises: ``OpenStackCloudResourceNotFound`` if QoS policy will not be
            found.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}

        data = self._network_client.get(
            "/qos/policies/{policy_id}/minimum_bandwidth_rules.json".format(
                policy_id=policy['id']),
            params=filters,
            error_message="Error fetching QoS minimum bandwith rules from "
                          "{policy}".format(policy=policy['id']))
        return self._get_and_munchify('minimum_bandwidth_rules', data)

    def get_qos_minimum_bandwidth_rule(self, policy_name_or_id, rule_id):
        """Get a QoS minimum bandwidth rule by name or ID.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param rule_id: ID of the rule.

        :returns: A bandwidth limit rule ``munch.Munch`` or None if
            no matching rule is found.

        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        data = self._network_client.get(
            "/qos/policies/{policy_id}/minimum_bandwidth_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id),
            error_message="Error fetching QoS minimum_bandwith rule {rule_id} "
                          "from {policy}".format(rule_id=rule_id,
                                                 policy=policy['id']))
        return self._get_and_munchify('minimum_bandwidth_rule', data)

    @_utils.valid_kwargs("direction")
    def create_qos_minimum_bandwidth_rule(self, policy_name_or_id, min_kbps,
                                          **kwargs):
        """Create a QoS minimum bandwidth limit rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule should be associated.
        :param int min_kbps: Minimum bandwidth value (in kilobits per second).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be available.

        :returns: The QoS minimum bandwidth rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        kwargs['min_kbps'] = min_kbps
        data = self._network_client.post(
            "/qos/policies/{policy_id}/minimum_bandwidth_rules".format(
                policy_id=policy['id']),
            json={'minimum_bandwidth_rule': kwargs})
        return self._get_and_munchify('minimum_bandwidth_rule', data)

    @_utils.valid_kwargs("min_kbps", "direction")
    def update_qos_minimum_bandwidth_rule(self, policy_name_or_id, rule_id,
                                          **kwargs):
        """Update a QoS minimum bandwidth rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to update.
        :param int min_kbps: Minimum bandwidth value (in kilobits per second).
        :param string direction: Ingress or egress.
            The direction in which the traffic will be available.

        :returns: The updated QoS minimum bandwidth rule.
        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        if not kwargs:
            self.log.debug("No QoS minimum bandwidth rule data to update")
            return

        curr_rule = self.get_qos_minimum_bandwidth_rule(
            policy_name_or_id, rule_id)
        if not curr_rule:
            raise OpenStackCloudException(
                "QoS minimum_bandwidth_rule {rule_id} not found in policy "
                "{policy_id}".format(rule_id=rule_id,
                                     policy_id=policy['id']))

        data = self._network_client.put(
            "/qos/policies/{policy_id}/minimum_bandwidth_rules/{rule_id}.json".
            format(policy_id=policy['id'], rule_id=rule_id),
            json={'minimum_bandwidth_rule': kwargs})
        return self._get_and_munchify('minimum_bandwidth_rule', data)

    def delete_qos_minimum_bandwidth_rule(self, policy_name_or_id, rule_id):
        """Delete a QoS minimum bandwidth rule.

        :param string policy_name_or_id: Name or ID of the QoS policy to which
            rule is associated.
        :param string rule_id: ID of rule to delete.

        :raises: OpenStackCloudException on operation error.
        """
        if not self._has_neutron_extension('qos'):
            raise OpenStackCloudUnavailableExtension(
                'QoS extension is not available on target cloud')

        policy = self.get_qos_policy(policy_name_or_id)
        if not policy:
            raise OpenStackCloudResourceNotFound(
                "QoS policy {name_or_id} not Found.".format(
                    name_or_id=policy_name_or_id))

        try:
            self._network_client.delete(
                "/qos/policies/{policy}/minimum_bandwidth_rules/{rule}.json".
                format(policy=policy['id'], rule=rule_id))
        except OpenStackCloudURINotFound:
            self.log.debug(
                "QoS minimum bandwidth rule {rule_id} not found in policy "
                "{policy_id}. Ignoring.".format(rule_id=rule_id,
                                                policy_id=policy['id']))
            return False

        return True

    def _build_external_gateway_info(self, ext_gateway_net_id, enable_snat,
                                     ext_fixed_ips):
        info = {}
        if ext_gateway_net_id:
            info['network_id'] = ext_gateway_net_id
        # Only send enable_snat if it is different from the Neutron
        # default of True. Sending it can cause a policy violation error
        # on some clouds.
        if enable_snat is not None and not enable_snat:
            info['enable_snat'] = False
        if ext_fixed_ips:
            info['external_fixed_ips'] = ext_fixed_ips
        if info:
            return info
        return None

    def add_router_interface(self, router, subnet_id=None, port_id=None):
        """Attach a subnet to an internal router interface.

        Either a subnet ID or port ID must be specified for the internal
        interface. Supplying both will result in an error.

        :param dict router: The dict object of the router being changed
        :param string subnet_id: The ID of the subnet to use for the interface
        :param string port_id: The ID of the port to use for the interface

        :returns: A ``munch.Munch`` with the router ID (ID),
                  subnet ID (subnet_id), port ID (port_id) and tenant ID
                  (tenant_id).

        :raises: OpenStackCloudException on operation error.
        """
        json_body = {}
        if subnet_id:
            json_body['subnet_id'] = subnet_id
        if port_id:
            json_body['port_id'] = port_id

        return self._network_client.put(
            "/routers/{router_id}/add_router_interface.json".format(
                router_id=router['id']),
            json=json_body,
            error_message="Error attaching interface to router {0}".format(
                router['id']))

    def remove_router_interface(self, router, subnet_id=None, port_id=None):
        """Detach a subnet from an internal router interface.

        At least one of subnet_id or port_id must be supplied.

        If you specify both subnet and port ID, the subnet ID must
        correspond to the subnet ID of the first IP address on the port
        specified by the port ID. Otherwise an error occurs.

        :param dict router: The dict object of the router being changed
        :param string subnet_id: The ID of the subnet to use for the interface
        :param string port_id: The ID of the port to use for the interface

        :returns: None on success

        :raises: OpenStackCloudException on operation error.
        """
        json_body = {}
        if subnet_id:
            json_body['subnet_id'] = subnet_id
        if port_id:
            json_body['port_id'] = port_id

        if not json_body:
            raise ValueError(
                "At least one of subnet_id or port_id must be supplied.")

        self._network_client.put(
            "/routers/{router_id}/remove_router_interface.json".format(
                router_id=router['id']),
            json=json_body,
            error_message="Error detaching interface from router {0}".format(
                router['id']))

    def list_router_interfaces(self, router, interface_type=None):
        """List all interfaces for a router.

        :param dict router: A router dict object.
        :param string interface_type: One of None, "internal", or "external".
            Controls whether all, internal interfaces or external interfaces
            are returned.

        :returns: A list of port ``munch.Munch`` objects.
        """
        # Find only router interface and gateway ports, ignore L3 HA ports etc.
        router_interfaces = self.search_ports(filters={
            'device_id': router['id'],
            'device_owner': 'network:router_interface'}
        ) + self.search_ports(filters={
            'device_id': router['id'],
            'device_owner': 'network:router_interface_distributed'}
        ) + self.search_ports(filters={
            'device_id': router['id'],
            'device_owner': 'network:ha_router_replicated_interface'})
        router_gateways = self.search_ports(filters={
            'device_id': router['id'],
            'device_owner': 'network:router_gateway'})
        ports = router_interfaces + router_gateways

        if interface_type:
            if interface_type == 'internal':
                return router_interfaces
            if interface_type == 'external':
                return router_gateways
        return ports

    def create_router(self, name=None, admin_state_up=True,
                      ext_gateway_net_id=None, enable_snat=None,
                      ext_fixed_ips=None, project_id=None,
                      availability_zone_hints=None):
        """Create a logical router.

        :param string name: The router name.
        :param bool admin_state_up: The administrative state of the router.
        :param string ext_gateway_net_id: Network ID for the external gateway.
        :param bool enable_snat: Enable Source NAT (SNAT) attribute.
        :param ext_fixed_ips:
            List of dictionaries of desired IP and/or subnet on the
            external network. Example::

              [
                {
                  "subnet_id": "8ca37218-28ff-41cb-9b10-039601ea7e6b",
                  "ip_address": "192.168.10.2"
                }
              ]
        :param string project_id: Project ID for the router.
        :param types.ListType availability_zone_hints:
            A list of availability zone hints.

        :returns: The router object.
        :raises: OpenStackCloudException on operation error.
        """
        router = {
            'admin_state_up': admin_state_up
        }
        if project_id is not None:
            router['tenant_id'] = project_id
        if name:
            router['name'] = name
        ext_gw_info = self._build_external_gateway_info(
            ext_gateway_net_id, enable_snat, ext_fixed_ips
        )
        if ext_gw_info:
            router['external_gateway_info'] = ext_gw_info
        if availability_zone_hints is not None:
            if not isinstance(availability_zone_hints, list):
                raise OpenStackCloudException(
                    "Parameter 'availability_zone_hints' must be a list")
            if not self._has_neutron_extension('router_availability_zone'):
                raise OpenStackCloudUnavailableExtension(
                    'router_availability_zone extension is not available on '
                    'target cloud')
            router['availability_zone_hints'] = availability_zone_hints

        data = self._network_client.post(
            "/routers.json", json={"router": router},
            error_message="Error creating router {0}".format(name))
        return self._get_and_munchify('router', data)

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
        :param ext_fixed_ips:
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

        data = self._network_client.put(
            "/routers/{router_id}.json".format(router_id=curr_router['id']),
            json={"router": router},
            error_message="Error updating router {0}".format(name_or_id))
        return self._get_and_munchify('router', data)

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
            self.log.debug("Router %s not found for deleting", name_or_id)
            return False

        self._network_client.delete(
            "/routers/{router_id}.json".format(router_id=router['id']),
            error_message="Error deleting router {0}".format(name_or_id))

        return True

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

    def create_image_snapshot(
            self, name, server, wait=False, timeout=3600, **metadata):
        """Create an image by snapshotting an existing server.

        ..note::
            On most clouds this is a cold snapshot - meaning that the server
            in question will be shutdown before taking the snapshot. It is
            possible that it's a live snapshot - but there is no way to know
            as a user, so caveat emptor.

        :param name: Name of the image to be created
        :param server: Server name or ID or dict representing the server
                       to be snapshotted
        :param wait: If true, waits for image to be created.
        :param timeout: Seconds to wait for image creation. None is forever.
        :param metadata: Metadata to give newly-created image entity

        :returns: A ``munch.Munch`` of the Image object

        :raises: OpenStackCloudException if there are problems uploading
        """
        if not isinstance(server, dict):
            server_obj = self.get_server(server, bare=True)
            if not server_obj:
                raise OpenStackCloudException(
                    "Server {server} could not be found and therefore"
                    " could not be snapshotted.".format(server=server))
            server = server_obj
        response = _adapter._json_response(
            self.compute.post(
                '/servers/{server_id}/action'.format(server_id=server['id']),
                json={
                    "createImage": {
                        "name": name,
                        "metadata": metadata,
                    }
                }))
        # You won't believe it - wait, who am I kidding - of course you will!
        # Nova returns the URL of the image created in the Location
        # header of the response. (what?) But, even better, the URL it responds
        # with has a very good chance of being wrong (it is built from
        # nova.conf values that point to internal API servers in any cloud
        # large enough to have both public and internal endpoints.
        # However, nobody has ever noticed this because novaclient doesn't
        # actually use that URL - it extracts the id from the end of
        # the url, then returns the id. This leads us to question:
        #   a) why Nova is going to return a value in a header
        #   b) why it's going to return data that probably broken
        #   c) indeed the very nature of the fabric of reality
        # Although it fills us with existential dread, we have no choice but
        # to follow suit like a lemming being forced over a cliff by evil
        # producers from Disney.
        # TODO(mordred) Update this to consume json microversion when it is
        #               available.
        #               blueprint:remove-create-image-location-header-response
        image_id = response.headers['Location'].rsplit('/', 1)[1]
        self.list_images.invalidate(self)
        image = self.get_image(image_id)

        if not wait:
            return image
        return self.wait_for_image(image, timeout=timeout)

    def wait_for_image(self, image, timeout=3600):
        image_id = image['id']
        for count in utils.iterate_timeout(
                timeout, "Timeout waiting for image to snapshot"):
            self.list_images.invalidate(self)
            image = self.get_image(image_id)
            if not image:
                continue
            if image['status'] == 'active':
                return image
            elif image['status'] == 'error':
                raise OpenStackCloudException(
                    'Image {image} hit error state'.format(image=image_id))

    def delete_image(
            self, name_or_id, wait=False, timeout=3600, delete_objects=True):
        """Delete an existing image.

        :param name_or_id: Name of the image to be deleted.
        :param wait: If True, waits for image to be deleted.
        :param timeout: Seconds to wait for image deletion. None is forever.
        :param delete_objects: If True, also deletes uploaded swift objects.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException if there are problems deleting.
        """
        image = self.get_image(name_or_id)
        if not image:
            return False
        self._image_client.delete(
            '/images/{id}'.format(id=image.id),
            error_message="Error in deleting image")
        self.list_images.invalidate(self)

        # Task API means an image was uploaded to swift
        if self.image_api_use_tasks and IMAGE_OBJECT_KEY in image:
            (container, objname) = image[IMAGE_OBJECT_KEY].split('/', 1)
            self.delete_object(container=container, name=objname)

        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the image to be deleted."):
                self._get_cache(None).invalidate()
                if self.get_image(image.id) is None:
                    break
        return True

    def _get_name_and_filename(self, name):
        # See if name points to an existing file
        if os.path.exists(name):
            # Neat. Easy enough
            return (os.path.splitext(os.path.basename(name))[0], name)

        # Try appending the disk format
        name_with_ext = '.'.join((
            name, self.config.config['image_format']))
        if os.path.exists(name_with_ext):
            return (os.path.basename(name), name_with_ext)

        raise OpenStackCloudException(
            'No filename parameter was given to create_image,'
            ' and {name} was not the path to an existing file.'
            ' Please provide either a path to an existing file'
            ' or a name and a filename'.format(name=name))

    def _hashes_up_to_date(self, md5, sha256, md5_key, sha256_key):
        '''Compare md5 and sha256 hashes for being up to date

        md5 and sha256 are the current values.
        md5_key and sha256_key are the previous values.
        '''
        up_to_date = False
        if md5 and md5_key == md5:
            up_to_date = True
        if sha256 and sha256_key == sha256:
            up_to_date = True
        if md5 and md5_key != md5:
            up_to_date = False
        if sha256 and sha256_key != sha256:
            up_to_date = False
        return up_to_date

    def create_image(
            self, name, filename=None, container=OBJECT_AUTOCREATE_CONTAINER,
            md5=None, sha256=None,
            disk_format=None, container_format=None,
            disable_vendor_agent=True,
            wait=False, timeout=3600,
            allow_duplicates=False, meta=None, volume=None, **kwargs):
        """Upload an image.

        :param str name: Name of the image to create. If it is a pathname
                         of an image, the name will be constructed from the
                         extensionless basename of the path.
        :param str filename: The path to the file to upload, if needed.
                             (optional, defaults to None)
        :param str container: Name of the container in swift where images
                              should be uploaded for import if the cloud
                              requires such a thing. (optiona, defaults to
                              'images')
        :param str md5: md5 sum of the image file. If not given, an md5 will
                        be calculated.
        :param str sha256: sha256 sum of the image file. If not given, an md5
                           will be calculated.
        :param str disk_format: The disk format the image is in. (optional,
                                defaults to the os-client-config config value
                                for this cloud)
        :param str container_format: The container format the image is in.
                                     (optional, defaults to the
                                     os-client-config config value for this
                                     cloud)
        :param bool disable_vendor_agent: Whether or not to append metadata
                                          flags to the image to inform the
                                          cloud in question to not expect a
                                          vendor agent to be runing.
                                          (optional, defaults to True)
        :param bool wait: If true, waits for image to be created. Defaults to
                          true - however, be aware that one of the upload
                          methods is always synchronous.
        :param timeout: Seconds to wait for image creation. None is forever.
        :param allow_duplicates: If true, skips checks that enforce unique
                                 image name. (optional, defaults to False)
        :param meta: A dict of key/value pairs to use for metadata that
                     bypasses automatic type conversion.
        :param volume: Name or ID or volume object of a volume to create an
                       image from. Mutually exclusive with (optional, defaults
                       to None)

        Additional kwargs will be passed to the image creation as additional
        metadata for the image and will have all values converted to string
        except for min_disk, min_ram, size and virtual_size which will be
        converted to int.

        If you are sure you have all of your data types correct or have an
        advanced need to be explicit, use meta. If you are just a normal
        consumer, using kwargs is likely the right choice.

        If a value is in meta and kwargs, meta wins.

        :returns: A ``munch.Munch`` of the Image object

        :raises: OpenStackCloudException if there are problems uploading
        """
        if not meta:
            meta = {}

        if not disk_format:
            disk_format = self.config.config['image_format']
        if not container_format:
            # https://docs.openstack.org/image-guide/image-formats.html
            container_format = 'bare'

        if volume:
            if 'id' in volume:
                volume_id = volume['id']
            else:
                volume_obj = self.get_volume(volume)
                if not volume_obj:
                    raise OpenStackCloudException(
                        "Volume {volume} given to create_image could"
                        " not be foud".format(volume=volume))
                volume_id = volume_obj['id']
            return self._upload_image_from_volume(
                name=name, volume_id=volume_id,
                allow_duplicates=allow_duplicates,
                container_format=container_format, disk_format=disk_format,
                wait=wait, timeout=timeout)

        # If there is no filename, see if name is actually the filename
        if not filename:
            name, filename = self._get_name_and_filename(name)
        if not (md5 or sha256):
            (md5, sha256) = self._get_file_hashes(filename)
        if allow_duplicates:
            current_image = None
        else:
            current_image = self.get_image(name)
            if current_image:
                md5_key = current_image.get(IMAGE_MD5_KEY, '')
                sha256_key = current_image.get(IMAGE_SHA256_KEY, '')
                up_to_date = self._hashes_up_to_date(
                    md5=md5, sha256=sha256,
                    md5_key=md5_key, sha256_key=sha256_key)
                if up_to_date:
                    self.log.debug(
                        "image %(name)s exists and is up to date",
                        {'name': name})
                    return current_image
        kwargs[IMAGE_MD5_KEY] = md5 or ''
        kwargs[IMAGE_SHA256_KEY] = sha256 or ''
        kwargs[IMAGE_OBJECT_KEY] = '/'.join([container, name])

        if disable_vendor_agent:
            kwargs.update(self.config.config['disable_vendor_agent'])

        # We can never have nice things. Glance v1 took "is_public" as a
        # boolean. Glance v2 takes "visibility". If the user gives us
        # is_public, we know what they mean. If they give us visibility, they
        # know that they mean.
        if self._is_client_version('image', 2):
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
                    wait=wait, timeout=timeout,
                    md5=md5, sha256=sha256,
                    meta=meta, **kwargs)
            else:
                # If a user used the v1 calling format, they will have
                # passed a dict called properties along
                properties = kwargs.pop('properties', {})
                kwargs.update(properties)
                image_kwargs = dict(properties=kwargs)
                if disk_format:
                    image_kwargs['disk_format'] = disk_format
                if container_format:
                    image_kwargs['container_format'] = container_format

                return self._upload_image_put(
                    name, filename, meta=meta,
                    wait=wait, timeout=timeout,
                    **image_kwargs)
        except OpenStackCloudException:
            self.log.debug("Image creation failed", exc_info=True)
            raise
        except Exception as e:
            raise OpenStackCloudException(
                "Image creation failed: {message}".format(message=str(e)))

    def _make_v2_image_params(self, meta, properties):
        ret = {}
        for k, v in iter(properties.items()):
            if k in ('min_disk', 'min_ram', 'size', 'virtual_size'):
                ret[k] = int(v)
            elif k == 'protected':
                ret[k] = v
            else:
                if v is None:
                    ret[k] = None
                else:
                    ret[k] = str(v)
        ret.update(meta)
        return ret

    def _upload_image_from_volume(
            self, name, volume_id, allow_duplicates,
            container_format, disk_format, wait, timeout):
        data = self._volume_client.post(
            '/volumes/{id}/action'.format(id=volume_id),
            json={
                'os-volume_upload_image': {
                    'force': allow_duplicates,
                    'image_name': name,
                    'container_format': container_format,
                    'disk_format': disk_format}})
        response = self._get_and_munchify('os-volume_upload_image', data)

        if not wait:
            return self.get_image(response['image_id'])
        try:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the image to finish."):
                image_obj = self.get_image(response['image_id'])
                if image_obj and image_obj.status not in ('queued', 'saving'):
                    return image_obj
        except OpenStackCloudTimeout:
            self.log.debug(
                "Timeout waiting for image to become ready. Deleting.")
            self.delete_image(response['image_id'], wait=True)
            raise

    def _upload_image_put_v2(self, name, image_data, meta, **image_kwargs):
        properties = image_kwargs.pop('properties', {})

        image_kwargs.update(self._make_v2_image_params(meta, properties))
        image_kwargs['name'] = name

        data = self._image_client.post('/images', json=image_kwargs)
        image = self._get_and_munchify(key=None, data=data)

        try:
            self._image_client.put(
                '/images/{id}/file'.format(id=image.id),
                headers={'Content-Type': 'application/octet-stream'},
                data=image_data)

        except Exception:
            self.log.debug("Deleting failed upload of image %s", name)
            try:
                self._image_client.delete(
                    '/images/{id}'.format(id=image.id))
            except OpenStackCloudHTTPError:
                # We're just trying to clean up - if it doesn't work - shrug
                self.log.debug(
                    "Failed deleting image after we failed uploading it.",
                    exc_info=True)
            raise

        return image

    def _upload_image_put_v1(
            self, name, image_data, meta, **image_kwargs):

        image_kwargs['properties'].update(meta)
        image_kwargs['name'] = name

        image = self._image_client.post('/images', json=image_kwargs)
        checksum = image_kwargs['properties'].get(IMAGE_MD5_KEY, '')

        try:
            # Let us all take a brief moment to be grateful that this
            # is not actually how OpenStack APIs work anymore
            headers = {
                'x-glance-registry-purge-props': 'false',
            }
            if checksum:
                headers['x-image-meta-checksum'] = checksum

            image = self._image_client.put(
                '/images/{id}'.format(id=image.id),
                headers=headers, data=image_data)

        except OpenStackCloudHTTPError:
            self.log.debug("Deleting failed upload of image %s", name)
            try:
                self._image_client.delete('/images/{id}'.format(id=image.id))
            except OpenStackCloudHTTPError:
                # We're just trying to clean up - if it doesn't work - shrug
                self.log.debug(
                    "Failed deleting image after we failed uploading it.",
                    exc_info=True)
            raise
        return image

    def _upload_image_put(
            self, name, filename, meta, wait, timeout, **image_kwargs):
        image_data = open(filename, 'rb')
        # Because reasons and crying bunnies
        if self._is_client_version('image', 2):
            image = self._upload_image_put_v2(
                name, image_data, meta, **image_kwargs)
        else:
            image = self._upload_image_put_v1(
                name, image_data, meta, **image_kwargs)
        self._get_cache(None).invalidate()
        if not wait:
            return image
        try:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the image to finish."):
                image_obj = self.get_image(image.id)
                if image_obj and image_obj.status not in ('queued', 'saving'):
                    return image_obj
        except OpenStackCloudTimeout:
            self.log.debug(
                "Timeout waiting for image to become ready. Deleting.")
            self.delete_image(image.id, wait=True)
            raise

    def _upload_image_task(
            self, name, filename, container, current_image,
            wait, timeout, meta, md5=None, sha256=None, **image_kwargs):

        parameters = image_kwargs.pop('parameters', {})
        image_kwargs.update(parameters)

        self.create_object(
            container, name, filename,
            md5=md5, sha256=sha256,
            metadata={OBJECT_AUTOCREATE_KEY: 'true'},
            **{'content-type': 'application/octet-stream'})
        if not current_image:
            current_image = self.get_image(name)
        # TODO(mordred): Can we do something similar to what nodepool does
        # using glance properties to not delete then upload but instead make a
        # new "good" image and then mark the old one as "bad"
        task_args = dict(
            type='import', input=dict(
                import_from='{container}/{name}'.format(
                    container=container, name=name),
                image_properties=dict(name=name)))
        data = self._image_client.post('/tasks', json=task_args)
        glance_task = self._get_and_munchify(key=None, data=data)
        self.list_images.invalidate(self)
        if wait:
            start = time.time()
            image_id = None
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the image to import."):
                try:
                    if image_id is None:
                        status = self._image_client.get(
                            '/tasks/{id}'.format(id=glance_task.id))
                except OpenStackCloudHTTPError as e:
                    if e.response.status_code == 503:
                        # Clear the exception so that it doesn't linger
                        # and get reported as an Inner Exception later
                        _utils._exc_clear()
                        # Intermittent failure - catch and try again
                        continue
                    raise

                if status['status'] == 'success':
                    image_id = status['result']['image_id']
                    try:
                        image = self.get_image(image_id)
                    except OpenStackCloudHTTPError as e:
                        if e.response.status_code == 503:
                            # Clear the exception so that it doesn't linger
                            # and get reported as an Inner Exception later
                            _utils._exc_clear()
                            # Intermittent failure - catch and try again
                            continue
                        raise
                    if image is None:
                        continue
                    self.update_image_properties(
                        image=image, meta=meta, **image_kwargs)
                    self.log.debug(
                        "Image Task %s imported %s in %s",
                        glance_task.id, image_id, (time.time() - start))
                    # Clean up after ourselves. The object we created is not
                    # needed after the import is done.
                    self.delete_object(container, name)
                    return self.get_image(image_id)
                elif status['status'] == 'failure':
                    if status['message'] == IMAGE_ERROR_396:
                        glance_task = self._image_client.post(
                            '/tasks', data=task_args)
                        self.list_images.invalidate(self)
                    else:
                        # Clean up after ourselves. The image did not import
                        # and this isn't a 'just retry' error - glance didn't
                        # like the content. So we don't want to keep it for
                        # next time.
                        self.delete_object(container, name)
                        raise OpenStackCloudException(
                            "Image creation failed: {message}".format(
                                message=status['message']),
                            extra_data=status)
        else:
            return glance_task

    def update_image_properties(
            self, image=None, name_or_id=None, meta=None, **properties):
        if image is None:
            image = self.get_image(name_or_id)

        if not meta:
            meta = {}

        img_props = {}
        for k, v in iter(properties.items()):
            if v and k in ['ramdisk', 'kernel']:
                v = self.get_image_id(v)
                k = '{0}_id'.format(k)
            img_props[k] = v

        # This makes me want to die inside
        if self._is_client_version('image', 2):
            return self._update_image_properties_v2(image, meta, img_props)
        else:
            return self._update_image_properties_v1(image, meta, img_props)

    def _update_image_properties_v2(self, image, meta, properties):
        img_props = image.properties.copy()
        for k, v in iter(self._make_v2_image_params(meta, properties).items()):
            if image.get(k, None) != v:
                img_props[k] = v
        if not img_props:
            return False
        headers = {
            'Content-Type': 'application/openstack-images-v2.1-json-patch'}
        patch = sorted(list(jsonpatch.JsonPatch.from_diff(
            image.properties, img_props)), key=operator.itemgetter('value'))

        # No need to fire an API call if there is an empty patch
        if patch:
            self._image_client.patch(
                '/images/{id}'.format(id=image.id),
                headers=headers,
                data=json.dumps(patch))

        self.list_images.invalidate(self)
        return True

    def _update_image_properties_v1(self, image, meta, properties):
        properties.update(meta)
        img_props = {}
        for k, v in iter(properties.items()):
            if image.properties.get(k, None) != v:
                img_props['x-image-meta-{key}'.format(key=k)] = v
        if not img_props:
            return False
        self._image_client.put(
            '/images/{id}'.format(image.id), headers=img_props)
        self.list_images.invalidate(self)
        return True

    def create_volume(
            self, size,
            wait=True, timeout=None, image=None, bootable=None, **kwargs):
        """Create a volume.

        :param size: Size, in GB of the volume to create.
        :param name: (optional) Name for the volume.
        :param description: (optional) Name for the volume.
        :param wait: If true, waits for volume to be created.
        :param timeout: Seconds to wait for volume creation. None is forever.
        :param image: (optional) Image name, ID or object from which to create
                      the volume
        :param bootable: (optional) Make this volume bootable. If set, wait
                         will also be set to true.
        :param kwargs: Keyword arguments as expected for cinder client.

        :returns: The created volume object.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        if bootable is not None:
            wait = True

        if image:
            image_obj = self.get_image(image)
            if not image_obj:
                raise OpenStackCloudException(
                    "Image {image} was requested as the basis for a new"
                    " volume, but was not found on the cloud".format(
                        image=image))
            kwargs['imageRef'] = image_obj['id']
        kwargs = self._get_volume_kwargs(kwargs)
        kwargs['size'] = size
        payload = dict(volume=kwargs)
        if 'scheduler_hints' in kwargs:
            payload['OS-SCH-HNT:scheduler_hints'] = kwargs.pop(
                'scheduler_hints', None)
        data = self._volume_client.post(
            '/volumes',
            json=dict(payload),
            error_message='Error in creating volume')
        volume = self._get_and_munchify('volume', data)
        self.list_volumes.invalidate(self)

        if volume['status'] == 'error':
            raise OpenStackCloudException("Error in creating volume")

        if wait:
            vol_id = volume['id']
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the volume to be available."):
                volume = self.get_volume(vol_id)

                if not volume:
                    continue

                if volume['status'] == 'available':
                    if bootable is not None:
                        self.set_volume_bootable(volume, bootable=bootable)
                        # no need to re-fetch to update the flag, just set it.
                        volume['bootable'] = bootable
                    return volume

                if volume['status'] == 'error':
                    raise OpenStackCloudException("Error in creating volume")

        return self._normalize_volume(volume)

    def set_volume_bootable(self, name_or_id, bootable=True):
        """Set a volume's bootable flag.

        :param name_or_id: Name, unique ID of the volume or a volume dict.
        :param bool bootable: Whether the volume should be bootable.
                              (Defaults to True)

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        volume = self.get_volume(name_or_id)

        if not volume:
            raise OpenStackCloudException(
                "Volume {name_or_id} does not exist".format(
                    name_or_id=name_or_id))

        self._volume_client.post(
            'volumes/{id}/action'.format(id=volume['id']),
            json={'os-set_bootable': {'bootable': bootable}},
            error_message="Error setting bootable on volume {volume}".format(
                volume=volume['id'])
        )

    def delete_volume(self, name_or_id=None, wait=True, timeout=None,
                      force=False):
        """Delete a volume.

        :param name_or_id: Name or unique ID of the volume.
        :param wait: If true, waits for volume to be deleted.
        :param timeout: Seconds to wait for volume deletion. None is forever.
        :param force: Force delete volume even if the volume is in deleting
            or error_deleting state.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        self.list_volumes.invalidate(self)
        volume = self.get_volume(name_or_id)

        if not volume:
            self.log.debug(
                "Volume %(name_or_id)s does not exist",
                {'name_or_id': name_or_id},
                exc_info=True)
            return False

        with _utils.shade_exceptions("Error in deleting volume"):
            try:
                if force:
                    self._volume_client.post(
                        'volumes/{id}/action'.format(id=volume['id']),
                        json={'os-force_delete': None})
                else:
                    self._volume_client.delete(
                        'volumes/{id}'.format(id=volume['id']))
            except OpenStackCloudURINotFound:
                self.log.debug(
                    "Volume {id} not found when deleting. Ignoring.".format(
                        id=volume['id']))
                return False

        self.list_volumes.invalidate(self)
        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the volume to be deleted."):

                if not self.get_volume(volume['id']):
                    break

        return True

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

        _adapter._json_response(self.compute.delete(
            '/servers/{server_id}/os-volume_attachments/{volume_id}'.format(
                server_id=server['id'], volume_id=volume['id'])),
            error_message=(
                "Error detaching volume {volume} from server {server}".format(
                    volume=volume['id'], server=server['id'])))

        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for volume %s to detach." % volume['id']):
                try:
                    vol = self.get_volume(volume['id'])
                except Exception:
                    self.log.debug(
                        "Error getting volume info %s", volume['id'],
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

        :returns: a volume attachment object.

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

        payload = {'volumeId': volume['id']}
        if device:
            payload['device'] = device
        data = _adapter._json_response(
            self.compute.post(
                '/servers/{server_id}/os-volume_attachments'.format(
                    server_id=server['id']),
                json=dict(volumeAttachment=payload)),
            error_message="Error attaching volume {volume_id} to server "
                          "{server_id}".format(volume_id=volume['id'],
                                               server_id=server['id']))

        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for volume %s to attach." % volume['id']):
                try:
                    self.list_volumes.invalidate(self)
                    vol = self.get_volume(volume['id'])
                except Exception:
                    self.log.debug(
                        "Error getting volume info %s", volume['id'],
                        exc_info=True)
                    continue

                if self.get_volume_attach_device(vol, server['id']):
                    break

                # TODO(Shrews) check to see if a volume can be in error status
                #              and also attached. If so, we should move this
                #              above the get_volume_attach_device call
                if vol['status'] == 'error':
                    raise OpenStackCloudException(
                        "Error in attaching volume %s" % volume['id']
                    )
        return self._normalize_volume_attachment(
            self._get_and_munchify('volumeAttachment', data))

    def _get_volume_kwargs(self, kwargs):
        name = kwargs.pop('name', kwargs.pop('display_name', None))
        description = kwargs.pop('description',
                                 kwargs.pop('display_description', None))
        if name:
            if self._is_client_version('volume', 2):
                kwargs['name'] = name
            else:
                kwargs['display_name'] = name
        if description:
            if self._is_client_version('volume', 2):
                kwargs['description'] = description
            else:
                kwargs['display_description'] = description
        return kwargs

    @_utils.valid_kwargs('name', 'display_name',
                         'description', 'display_description')
    def create_volume_snapshot(self, volume_id, force=False,
                               wait=True, timeout=None, **kwargs):
        """Create a volume.

        :param volume_id: the ID of the volume to snapshot.
        :param force: If set to True the snapshot will be created even if the
                      volume is attached to an instance, if False it will not
        :param name: name of the snapshot, one will be generated if one is
                     not provided
        :param description: description of the snapshot, one will be generated
                            if one is not provided
        :param wait: If true, waits for volume snapshot to be created.
        :param timeout: Seconds to wait for volume snapshot creation. None is
                        forever.

        :returns: The created volume object.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        kwargs = self._get_volume_kwargs(kwargs)
        payload = {'volume_id': volume_id, 'force': force}
        payload.update(kwargs)
        data = self._volume_client.post(
            '/snapshots',
            json=dict(snapshot=payload),
            error_message="Error creating snapshot of volume "
                          "{volume_id}".format(volume_id=volume_id))
        snapshot = self._get_and_munchify('snapshot', data)
        if wait:
            snapshot_id = snapshot['id']
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the volume snapshot to be available."
            ):
                snapshot = self.get_volume_snapshot_by_id(snapshot_id)

                if snapshot['status'] == 'available':
                    break

                if snapshot['status'] == 'error':
                    raise OpenStackCloudException(
                        "Error in creating volume snapshot")

        # TODO(mordred) need to normalize snapshots. We were normalizing them
        # as volumes, which is an error. They need to be normalized as
        # volume snapshots, which are completely different objects
        return snapshot

    def get_volume_snapshot_by_id(self, snapshot_id):
        """Takes a snapshot_id and gets a dict of the snapshot
        that maches that ID.

        Note: This is more efficient than get_volume_snapshot.

        param: snapshot_id: ID of the volume snapshot.

        """
        data = self._volume_client.get(
            '/snapshots/{snapshot_id}'.format(snapshot_id=snapshot_id),
            error_message="Error getting snapshot "
                          "{snapshot_id}".format(snapshot_id=snapshot_id))
        return self._normalize_volume(
            self._get_and_munchify('snapshot', data))

    def get_volume_snapshot(self, name_or_id, filters=None):
        """Get a volume by name or ID.

        :param name_or_id: Name or ID of the volume snapshot.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A volume ``munch.Munch`` or None if no matching volume is
                  found.
        """
        return _utils._get_entity(self, 'volume_snapshot', name_or_id,
                                  filters)

    def create_volume_backup(self, volume_id, name=None, description=None,
                             force=False, wait=True, timeout=None):
        """Create a volume backup.

        :param volume_id: the ID of the volume to backup.
        :param name: name of the backup, one will be generated if one is
                     not provided
        :param description: description of the backup, one will be generated
                            if one is not provided
        :param force: If set to True the backup will be created even if the
                      volume is attached to an instance, if False it will not
        :param wait: If true, waits for volume backup to be created.
        :param timeout: Seconds to wait for volume backup creation. None is
                        forever.

        :returns: The created volume backup object.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        payload = {
            'name': name,
            'volume_id': volume_id,
            'description': description,
            'force': force,
        }

        data = self._volume_client.post(
            '/backups', json=dict(backup=payload),
            error_message="Error creating backup of volume "
                          "{volume_id}".format(volume_id=volume_id))
        backup = self._get_and_munchify('backup', data)

        if wait:
            backup_id = backup['id']
            msg = ("Timeout waiting for the volume backup {} to be "
                   "available".format(backup_id))
            for _ in utils.iterate_timeout(timeout, msg):
                backup = self.get_volume_backup(backup_id)

                if backup['status'] == 'available':
                    break

                if backup['status'] == 'error':
                    raise OpenStackCloudException(
                        "Error in creating volume backup {id}".format(
                            id=backup_id))

        return backup

    def get_volume_backup(self, name_or_id, filters=None):
        """Get a volume backup by name or ID.

        :returns: A backup ``munch.Munch`` or None if no matching backup is
                  found.
        """
        return _utils._get_entity(self, 'volume_backup', name_or_id,
                                  filters)

    def list_volume_snapshots(self, detailed=True, search_opts=None):
        """List all volume snapshots.

        :returns: A list of volume snapshots ``munch.Munch``.

        """
        endpoint = '/snapshots/detail' if detailed else '/snapshots'
        data = self._volume_client.get(
            endpoint,
            params=search_opts,
            error_message="Error getting a list of snapshots")
        return self._get_and_munchify('snapshots', data)

    def list_volume_backups(self, detailed=True, search_opts=None):
        """
        List all volume backups.

        :param bool detailed: Also list details for each entry
        :param dict search_opts: Search options
            A dictionary of meta data to use for further filtering. Example::

                {
                    'name': 'my-volume-backup',
                    'status': 'available',
                    'volume_id': 'e126044c-7b4c-43be-a32a-c9cbbc9ddb56',
                    'all_tenants': 1
                }

        :returns: A list of volume backups ``munch.Munch``.
        """
        endpoint = '/backups/detail' if detailed else '/backups'
        data = self._volume_client.get(
            endpoint, params=search_opts,
            error_message="Error getting a list of backups")
        return self._get_and_munchify('backups', data)

    def delete_volume_backup(self, name_or_id=None, force=False, wait=False,
                             timeout=None):
        """Delete a volume backup.

        :param name_or_id: Name or unique ID of the volume backup.
        :param force: Allow delete in state other than error or available.
        :param wait: If true, waits for volume backup to be deleted.
        :param timeout: Seconds to wait for volume backup deletion. None is
                        forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        volume_backup = self.get_volume_backup(name_or_id)

        if not volume_backup:
            return False

        msg = "Error in deleting volume backup"
        if force:
            self._volume_client.post(
                '/backups/{backup_id}/action'.format(
                    backup_id=volume_backup['id']),
                json={'os-force_delete': None},
                error_message=msg)
        else:
            self._volume_client.delete(
                '/backups/{backup_id}'.format(
                    backup_id=volume_backup['id']),
                error_message=msg)
        if wait:
            msg = "Timeout waiting for the volume backup to be deleted."
            for count in utils.iterate_timeout(timeout, msg):
                if not self.get_volume_backup(volume_backup['id']):
                    break

        return True

    def delete_volume_snapshot(self, name_or_id=None, wait=False,
                               timeout=None):
        """Delete a volume snapshot.

        :param name_or_id: Name or unique ID of the volume snapshot.
        :param wait: If true, waits for volume snapshot to be deleted.
        :param timeout: Seconds to wait for volume snapshot deletion. None is
                        forever.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        volumesnapshot = self.get_volume_snapshot(name_or_id)

        if not volumesnapshot:
            return False

        self._volume_client.delete(
            '/snapshots/{snapshot_id}'.format(
                snapshot_id=volumesnapshot['id']),
            error_message="Error in deleting volume snapshot")

        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the volume snapshot to be deleted."):
                if not self.get_volume_snapshot(volumesnapshot['id']):
                    break

        return True

    def get_server_id(self, name_or_id):
        server = self.get_server(name_or_id, bare=True)
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

    def _expand_server_vars(self, server):
        # Used by nodepool
        # TODO(mordred) remove after these make it into what we
        # actually want the API to be.
        return meta.expand_server_vars(self, server)

    def _find_floating_network_by_router(self):
        """Find the network providing floating ips by looking at routers."""

        if self._floating_network_by_router_lock.acquire(
                not self._floating_network_by_router_run):
            if self._floating_network_by_router_run:
                self._floating_network_by_router_lock.release()
                return self._floating_network_by_router
            try:
                for router in self.list_routers():
                    if router['admin_state_up']:
                        network_id = router.get(
                            'external_gateway_info', {}).get('network_id')
                        if network_id:
                            self._floating_network_by_router = network_id
            finally:
                self._floating_network_by_router_run = True
                self._floating_network_by_router_lock.release()
        return self._floating_network_by_router

    def available_floating_ip(self, network=None, server=None):
        """Get a floating IP from a network or a pool.

        Return the first available floating IP or allocate a new one.

        :param network: Name or ID of the network.
        :param server: Server the IP is for if known

        :returns: a (normalized) structure with a floating IP address
                  description.
        """
        if self._use_neutron_floating():
            try:
                f_ips = self._normalize_floating_ips(
                    self._neutron_available_floating_ips(
                        network=network, server=server))
                return f_ips[0]
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                # Fall-through, trying with Nova

        f_ips = self._normalize_floating_ips(
            self._nova_available_floating_ips(pool=network)
        )
        return f_ips[0]

    def _get_floating_network_id(self):
        # Get first existing external IPv4 network
        networks = self.get_external_ipv4_floating_networks()
        if networks:
            floating_network_id = networks[0]['id']
        else:
            floating_network = self._find_floating_network_by_router()
            if floating_network:
                floating_network_id = floating_network
            else:
                raise OpenStackCloudResourceNotFound(
                    "unable to find an external network")
        return floating_network_id

    def _neutron_available_floating_ips(
            self, network=None, project_id=None, server=None):
        """Get a floating IP from a network.

        Return a list of available floating IPs or allocate a new one and
        return it in a list of 1 element.

        :param network: A single network name or ID, or a list of them.
        :param server: (server) Server the Floating IP is for

        :returns: a list of floating IP addresses.

        :raises: ``OpenStackCloudResourceNotFound``, if an external network
                 that meets the specified criteria cannot be found.
        """
        if project_id is None:
            # Make sure we are only listing floatingIPs allocated the current
            # tenant. This is the default behaviour of Nova
            project_id = self.current_project_id

        if network:
            if isinstance(network, six.string_types):
                network = [network]

            # Use given list to get first matching external network
            floating_network_id = None
            for net in network:
                for ext_net in self.get_external_ipv4_floating_networks():
                    if net in (ext_net['name'], ext_net['id']):
                        floating_network_id = ext_net['id']
                        break
                if floating_network_id:
                    break

            if floating_network_id is None:
                raise OpenStackCloudResourceNotFound(
                    "unable to find external network {net}".format(
                        net=network)
                )
        else:
            floating_network_id = self._get_floating_network_id()

        filters = {
            'port': None,
            'network': floating_network_id,
            'location': {'project': {'id': project_id}},
        }

        floating_ips = self._list_floating_ips()
        available_ips = _utils._filter_list(
            floating_ips, name_or_id=None, filters=filters)
        if available_ips:
            return available_ips

        # No available IP found or we didn't try
        # allocate a new Floating IP
        f_ip = self._neutron_create_floating_ip(
            network_id=floating_network_id, server=server)

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

        with _utils.shade_exceptions(
                "Unable to create floating IP in pool {pool}".format(
                    pool=pool)):
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

            # No available IP found or we did not try.
            # Allocate a new Floating IP
            f_ip = self._nova_create_floating_ip(pool=pool)

            return [f_ip]

    def create_floating_ip(self, network=None, server=None,
                           fixed_address=None, nat_destination=None,
                           port=None, wait=False, timeout=60):
        """Allocate a new floating IP from a network or a pool.

        :param network: Name or ID of the network
                        that the floating IP should come from.
        :param server: (optional) Server dict for the server to create
                       the IP for and to which it should be attached.
        :param fixed_address: (optional) Fixed IP to attach the floating
                              ip to.
        :param nat_destination: (optional) Name or ID of the network
                                that the fixed IP to attach the floating
                                IP to should be on.
        :param port: (optional) The port ID that the floating IP should be
                                attached to. Specifying a port conflicts
                                with specifying a server, fixed_address or
                                nat_destination.
        :param wait: (optional) Whether to wait for the IP to be active.
                     Defaults to False. Only applies if a server is
                     provided.
        :param timeout: (optional) How long to wait for the IP to be active.
                        Defaults to 60. Only applies if a server is
                        provided.

        :returns: a floating IP address

        :raises: ``OpenStackCloudException``, on operation error.
        """
        if self._use_neutron_floating():
            try:
                return self._neutron_create_floating_ip(
                    network_name_or_id=network, server=server,
                    fixed_address=fixed_address,
                    nat_destination=nat_destination,
                    port=port,
                    wait=wait, timeout=timeout)
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                # Fall-through, trying with Nova

        if port:
            raise OpenStackCloudException(
                "This cloud uses nova-network which does not support"
                " arbitrary floating-ip/port mappings. Please nudge"
                " your cloud provider to upgrade the networking stack"
                " to neutron, or alternately provide the server,"
                " fixed_address and nat_destination arguments as appropriate")
        # Else, we are using Nova network
        f_ips = self._normalize_floating_ips(
            [self._nova_create_floating_ip(pool=network)])
        return f_ips[0]

    def _submit_create_fip(self, kwargs):
        # Split into a method to aid in test mocking
        data = self._network_client.post(
            "/floatingips.json", json={"floatingip": kwargs})
        return self._normalize_floating_ip(
            self._get_and_munchify('floatingip', data))

    def _neutron_create_floating_ip(
            self, network_name_or_id=None, server=None,
            fixed_address=None, nat_destination=None,
            port=None,
            wait=False, timeout=60, network_id=None):

        if not network_id:
            if network_name_or_id:
                network = self.get_network(network_name_or_id)
                if not network:
                    raise OpenStackCloudResourceNotFound(
                        "unable to find network for floating ips with ID "
                        "{0}".format(network_name_or_id))
                network_id = network['id']
            else:
                network_id = self._get_floating_network_id()
        kwargs = {
            'floating_network_id': network_id,
        }
        if not port:
            if server:
                (port_obj, fixed_ip_address) = self._nat_destination_port(
                    server, fixed_address=fixed_address,
                    nat_destination=nat_destination)
                if port_obj:
                    port = port_obj['id']
                if fixed_ip_address:
                    kwargs['fixed_ip_address'] = fixed_ip_address
        if port:
            kwargs['port_id'] = port

        fip = self._submit_create_fip(kwargs)
        fip_id = fip['id']

        if port:
            # The FIP is only going to become active in this context
            # when we've attached it to something, which only occurs
            # if we've provided a port as a parameter
            if wait:
                try:
                    for count in utils.iterate_timeout(
                            timeout,
                            "Timeout waiting for the floating IP"
                            " to be ACTIVE",
                            wait=self._FLOAT_AGE):
                        fip = self.get_floating_ip(fip_id)
                        if fip and fip['status'] == 'ACTIVE':
                            break
                except OpenStackCloudTimeout:
                    self.log.error(
                        "Timed out on floating ip %(fip)s becoming active."
                        " Deleting", {'fip': fip_id})
                    try:
                        self.delete_floating_ip(fip_id)
                    except Exception as e:
                        self.log.error(
                            "FIP LEAK: Attempted to delete floating ip "
                            "%(fip)s but received %(exc)s exception: "
                            "%(err)s", {'fip': fip_id, 'exc': e.__class__,
                                        'err': str(e)})
                    raise
            if fip['port_id'] != port:
                if server:
                    raise OpenStackCloudException(
                        "Attempted to create FIP on port {port} for server"
                        " {server} but FIP has port {port_id}".format(
                            port=port, port_id=fip['port_id'],
                            server=server['id']))
                else:
                    raise OpenStackCloudException(
                        "Attempted to create FIP on port {port}"
                        " but something went wrong".format(port=port))
        return fip

    def _nova_create_floating_ip(self, pool=None):
        with _utils.shade_exceptions(
                "Unable to create floating IP in pool {pool}".format(
                    pool=pool)):
            if pool is None:
                pools = self.list_floating_ip_pools()
                if not pools:
                    raise OpenStackCloudResourceNotFound(
                        "unable to find a floating ip pool")
                pool = pools[0]['name']

            data = _adapter._json_response(self.compute.post(
                '/os-floating-ips', json=dict(pool=pool)))
            pool_ip = self._get_and_munchify('floating_ip', data)
            # TODO(mordred) Remove this - it's just for compat
            data = _adapter._json_response(
                self.compute.get('/os-floating-ips/{id}'.format(
                    id=pool_ip['id'])))
            return self._get_and_munchify('floating_ip', data)

    def delete_floating_ip(self, floating_ip_id, retry=1):
        """Deallocate a floating IP from a project.

        :param floating_ip_id: a floating IP address ID.
        :param retry: number of times to retry. Optional, defaults to 1,
                      which is in addition to the initial delete call.
                      A value of 0 will also cause no checking of results to
                      occur.

        :returns: True if the IP address has been deleted, False if the IP
                  address was not found.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        for count in range(0, max(0, retry) + 1):
            result = self._delete_floating_ip(floating_ip_id)

            if (retry == 0) or not result:
                return result

            # Wait for the cached floating ip list to be regenerated
            if self._FLOAT_AGE:
                time.sleep(self._FLOAT_AGE)

            # neutron sometimes returns success when deleting a floating
            # ip. That's awesome. SO - verify that the delete actually
            # worked. Some clouds will set the status to DOWN rather than
            # deleting the IP immediately. This is, of course, a bit absurd.
            f_ip = self.get_floating_ip(id=floating_ip_id)
            if not f_ip or f_ip['status'] == 'DOWN':
                return True

        raise OpenStackCloudException(
            "Attempted to delete Floating IP {ip} with ID {id} a total of"
            " {retry} times. Although the cloud did not indicate any errors"
            " the floating ip is still in existence. Aborting further"
            " operations.".format(
                id=floating_ip_id, ip=f_ip['floating_ip_address'],
                retry=retry + 1))

    def _delete_floating_ip(self, floating_ip_id):
        if self._use_neutron_floating():
            try:
                return self._neutron_delete_floating_ip(floating_ip_id)
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
        return self._nova_delete_floating_ip(floating_ip_id)

    def _neutron_delete_floating_ip(self, floating_ip_id):
        try:
            self._network_client.delete(
                "/floatingips/{fip_id}.json".format(fip_id=floating_ip_id),
                error_message="unable to delete floating IP")
        except OpenStackCloudResourceNotFound:
            return False
        except Exception as e:
            raise OpenStackCloudException(
                "Unable to delete floating IP ID {fip_id}: {msg}".format(
                    fip_id=floating_ip_id, msg=str(e)))
        return True

    def _nova_delete_floating_ip(self, floating_ip_id):
        try:
            _adapter._json_response(
                self.compute.delete(
                    '/os-floating-ips/{id}'.format(id=floating_ip_id)),
                error_message='Unable to delete floating IP {fip_id}'.format(
                    fip_id=floating_ip_id))
        except OpenStackCloudURINotFound:
            return False
        return True

    def delete_unattached_floating_ips(self, retry=1):
        """Safely delete unattached floating ips.

        If the cloud can safely purge any unattached floating ips without
        race conditions, do so.

        Safely here means a specific thing. It means that you are not running
        this while another process that might do a two step create/attach
        is running. You can safely run this  method while another process
        is creating servers and attaching floating IPs to them if either that
        process is using add_auto_ip from shade, or is creating the floating
        IPs by passing in a server to the create_floating_ip call.

        :param retry: number of times to retry. Optional, defaults to 1,
                      which is in addition to the initial delete call.
                      A value of 0 will also cause no checking of results to
                      occur.

        :returns: True if Floating IPs have been deleted, False if not

        :raises: ``OpenStackCloudException``, on operation error.
        """
        processed = []
        if self._use_neutron_floating():
            for ip in self.list_floating_ips():
                if not ip['attached']:
                    processed.append(self.delete_floating_ip(
                        floating_ip_id=ip['id'], retry=retry))
        return all(processed) if processed else False

    def _attach_ip_to_server(
            self, server, floating_ip,
            fixed_address=None, wait=False,
            timeout=60, skip_attach=False, nat_destination=None):
        """Attach a floating IP to a server.

        :param server: Server dict
        :param floating_ip: Floating IP dict to attach
        :param fixed_address: (optional) fixed address to which attach the
                              floating IP to.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param skip_attach: (optional) Skip the actual attach and just do
                            the wait. Defaults to False.
        :param nat_destination: The fixed network the server's port for the
                                FIP to attach to will come from.

        :returns: The server ``munch.Munch``

        :raises: OpenStackCloudException, on operation error.
        """
        # Short circuit if we're asking to attach an IP that's already
        # attached
        ext_ip = meta.get_server_ip(server, ext_tag='floating', public=True)
        if ext_ip == floating_ip['floating_ip_address']:
            return server

        if self._use_neutron_floating():
            if not skip_attach:
                try:
                    self._neutron_attach_ip_to_server(
                        server=server, floating_ip=floating_ip,
                        fixed_address=fixed_address,
                        nat_destination=nat_destination)
                except OpenStackCloudURINotFound as e:
                    self.log.debug(
                        "Something went wrong talking to neutron API: "
                        "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                    # Fall-through, trying with Nova
        else:
            # Nova network
            self._nova_attach_ip_to_server(
                server_id=server['id'], floating_ip_id=floating_ip['id'],
                fixed_address=fixed_address)

        if wait:
            # Wait for the address to be assigned to the server
            server_id = server['id']
            for _ in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the floating IP to be attached.",
                    wait=self._SERVER_AGE):
                server = self.get_server(server_id)
                ext_ip = meta.get_server_ip(
                    server, ext_tag='floating', public=True)
                if ext_ip == floating_ip['floating_ip_address']:
                    return server
        return server

    def _nat_destination_port(
            self, server, fixed_address=None, nat_destination=None):
        """Returns server port that is on a nat_destination network

        Find a port attached to the server which is on a network which
        has a subnet which can be the destination of NAT. Such a network
        is referred to in shade as a "nat_destination" network. So this
        then is a function which returns a port on such a network that is
        associated with the given server.

        :param server: Server dict.
        :param fixed_address: Fixed ip address of the port
        :param nat_destination: Name or ID of the network of the port.
        """
        # If we are caching port lists, we may not find the port for
        # our server if the list is old.  Try for at least 2 cache
        # periods if that is the case.
        if self._PORT_AGE:
            timeout = self._PORT_AGE * 2
        else:
            timeout = None
        for count in utils.iterate_timeout(
                timeout,
                "Timeout waiting for port to show up in list",
                wait=self._PORT_AGE):
            try:
                port_filter = {'device_id': server['id']}
                ports = self.search_ports(filters=port_filter)
                break
            except OpenStackCloudTimeout:
                ports = None
        if not ports:
            return (None, None)
        port = None
        if not fixed_address:
            if len(ports) > 1:
                if nat_destination:
                    nat_network = self.get_network(nat_destination)
                    if not nat_network:
                        raise OpenStackCloudException(
                            'NAT Destination {nat_destination} was configured'
                            ' but not found on the cloud. Please check your'
                            ' config and your cloud and try again.'.format(
                                nat_destination=nat_destination))
                else:
                    nat_network = self.get_nat_destination()

                if not nat_network:
                    raise OpenStackCloudException(
                        'Multiple ports were found for server {server}'
                        ' but none of the networks are a valid NAT'
                        ' destination, so it is impossible to add a'
                        ' floating IP. If you have a network that is a valid'
                        ' destination for NAT and we could not find it,'
                        ' please file a bug. But also configure the'
                        ' nat_destination property of the networks list in'
                        ' your clouds.yaml file. If you do not have a'
                        ' clouds.yaml file, please make one - your setup'
                        ' is complicated.'.format(server=server['id']))

                maybe_ports = []
                for maybe_port in ports:
                    if maybe_port['network_id'] == nat_network['id']:
                        maybe_ports.append(maybe_port)
                if not maybe_ports:
                    raise OpenStackCloudException(
                        'No port on server {server} was found matching'
                        ' your NAT destination network {dest}. Please '
                        ' check your config'.format(
                            server=server['id'], dest=nat_network['name']))
                ports = maybe_ports

            # Select the most recent available IPv4 address
            # To do this, sort the ports in reverse order by the created_at
            # field which is a string containing an ISO DateTime (which
            # thankfully sort properly) This way the most recent port created,
            # if there are more than one, will be the arbitrary port we
            # select.
            for port in sorted(
                    ports,
                    key=lambda p: p.get('created_at', 0),
                    reverse=True):
                for address in port.get('fixed_ips', list()):
                    try:
                        ip = ipaddress.ip_address(address['ip_address'])
                    except Exception:
                        continue
                    if ip.version == 4:
                        fixed_address = address['ip_address']
                        return port, fixed_address
            raise OpenStackCloudException(
                "unable to find a free fixed IPv4 address for server "
                "{0}".format(server['id']))
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
                    return (p, fixed_address)
        return (None, None)

    def _neutron_attach_ip_to_server(
            self, server, floating_ip, fixed_address=None,
            nat_destination=None):

        # Find an available port
        (port, fixed_address) = self._nat_destination_port(
            server, fixed_address=fixed_address,
            nat_destination=nat_destination)
        if not port:
            raise OpenStackCloudException(
                "unable to find a port for server {0}".format(
                    server['id']))

        floating_ip_args = {'port_id': port['id']}
        if fixed_address is not None:
            floating_ip_args['fixed_ip_address'] = fixed_address

        return self._network_client.put(
            "/floatingips/{fip_id}.json".format(fip_id=floating_ip['id']),
            json={'floatingip': floating_ip_args},
            error_message=("Error attaching IP {ip} to "
                           "server {server_id}".format(
                               ip=floating_ip['id'],
                               server_id=server['id'])))

    def _nova_attach_ip_to_server(self, server_id, floating_ip_id,
                                  fixed_address=None):
        f_ip = self.get_floating_ip(
            id=floating_ip_id)
        if f_ip is None:
            raise OpenStackCloudException(
                "unable to find floating IP {0}".format(floating_ip_id))
        error_message = "Error attaching IP {ip} to instance {id}".format(
            ip=floating_ip_id, id=server_id)
        body = {
            'address': f_ip['floating_ip_address']
        }
        if fixed_address:
            body['fixed_address'] = fixed_address
        return _adapter._json_response(
            self.compute.post(
                '/servers/{server_id}/action'.format(server_id=server_id),
                json=dict(addFloatingIp=body)),
            error_message=error_message)

    def detach_ip_from_server(self, server_id, floating_ip_id):
        """Detach a floating IP from a server.

        :param server_id: ID of a server.
        :param floating_ip_id: Id of the floating IP to detach.

        :returns: True if the IP has been detached, or False if the IP wasn't
                  attached to any server.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        if self._use_neutron_floating():
            try:
                return self._neutron_detach_ip_from_server(
                    server_id=server_id, floating_ip_id=floating_ip_id)
            except OpenStackCloudURINotFound as e:
                self.log.debug(
                    "Something went wrong talking to neutron API: "
                    "'%(msg)s'. Trying with Nova.", {'msg': str(e)})
                # Fall-through, trying with Nova

        # Nova network
        self._nova_detach_ip_from_server(
            server_id=server_id, floating_ip_id=floating_ip_id)

    def _neutron_detach_ip_from_server(self, server_id, floating_ip_id):
        f_ip = self.get_floating_ip(id=floating_ip_id)
        if f_ip is None or not f_ip['attached']:
            return False
        self._network_client.put(
            "/floatingips/{fip_id}.json".format(fip_id=floating_ip_id),
            json={"floatingip": {"port_id": None}},
            error_message=("Error detaching IP {ip} from "
                           "server {server_id}".format(
                               ip=floating_ip_id, server_id=server_id)))

        return True

    def _nova_detach_ip_from_server(self, server_id, floating_ip_id):

        f_ip = self.get_floating_ip(id=floating_ip_id)
        if f_ip is None:
            raise OpenStackCloudException(
                "unable to find floating IP {0}".format(floating_ip_id))
        error_message = "Error detaching IP {ip} from instance {id}".format(
            ip=floating_ip_id, id=server_id)
        return _adapter._json_response(
            self.compute.post(
                '/servers/{server_id}/action'.format(server_id=server_id),
                json=dict(removeFloatingIp=dict(
                    address=f_ip['floating_ip_address']))),
            error_message=error_message)

        return True

    def _add_ip_from_pool(
            self, server, network, fixed_address=None, reuse=True,
            wait=False, timeout=60, nat_destination=None):
        """Add a floating IP to a server from a given pool

        This method reuses available IPs, when possible, or allocate new IPs
        to the current tenant.
        The floating IP is attached to the given fixed address or to the
        first server port/fixed address

        :param server: Server dict
        :param network: Name or ID of the network.
        :param fixed_address: a fixed address
        :param reuse: Try to reuse existing ips. Defaults to True.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param nat_destination: (optional) the name of the network of the
                                port to associate with the floating ip.

        :returns: the updated server ``munch.Munch``
        """
        if reuse:
            f_ip = self.available_floating_ip(network=network)
        else:
            start_time = time.time()
            f_ip = self.create_floating_ip(
                server=server,
                network=network, nat_destination=nat_destination,
                wait=wait, timeout=timeout)
            timeout = timeout - (time.time() - start_time)
            # Wait for cache invalidation time so that we don't try
            # to attach the FIP a second time below
            time.sleep(self._SERVER_AGE)
            server = self.get_server(server.id)

        # We run attach as a second call rather than in the create call
        # because there are code flows where we will not have an attached
        # FIP yet. However, even if it was attached in the create, we run
        # the attach function below to get back the server dict refreshed
        # with the FIP information.
        return self._attach_ip_to_server(
            server=server, floating_ip=f_ip, fixed_address=fixed_address,
            wait=wait, timeout=timeout, nat_destination=nat_destination)

    def add_ip_list(
            self, server, ips, wait=False, timeout=60,
            fixed_address=None):
        """Attach a list of IPs to a server.

        :param server: a server object
        :param ips: list of floating IP addresses or a single address
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param fixed_address: (optional) Fixed address of the server to
                                         attach the IP to

        :returns: The updated server ``munch.Munch``

        :raises: ``OpenStackCloudException``, on operation error.
        """
        if type(ips) == list:
            ip = ips[0]
        else:
            ip = ips
        f_ip = self.get_floating_ip(
            id=None, filters={'floating_ip_address': ip})
        return self._attach_ip_to_server(
            server=server, floating_ip=f_ip, wait=wait, timeout=timeout,
            fixed_address=fixed_address)

    def add_auto_ip(self, server, wait=False, timeout=60, reuse=True):
        """Add a floating IP to a server.

        This method is intended for basic usage. For advanced network
        architecture (e.g. multiple external networks or servers with multiple
        interfaces), use other floating IP methods.

        This method can reuse available IPs, or allocate new IPs to the current
        project.

        :param server: a server dictionary.
        :param reuse: Whether or not to attempt to reuse IPs, defaults
                      to True.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param reuse: Try to reuse existing ips. Defaults to True.

        :returns: Floating IP address attached to server.

        """
        server = self._add_auto_ip(
            server, wait=wait, timeout=timeout, reuse=reuse)
        return server['interface_ip'] or None

    def _add_auto_ip(self, server, wait=False, timeout=60, reuse=True):
        skip_attach = False
        created = False
        if reuse:
            f_ip = self.available_floating_ip()
        else:
            start_time = time.time()
            f_ip = self.create_floating_ip(
                server=server, wait=wait, timeout=timeout)
            timeout = timeout - (time.time() - start_time)
            if server:
                # This gets passed in for both nova and neutron
                # but is only meaningful for the neutron logic branch
                skip_attach = True
            created = True

        try:
            # We run attach as a second call rather than in the create call
            # because there are code flows where we will not have an attached
            # FIP yet. However, even if it was attached in the create, we run
            # the attach function below to get back the server dict refreshed
            # with the FIP information.
            return self._attach_ip_to_server(
                server=server, floating_ip=f_ip, wait=wait, timeout=timeout,
                skip_attach=skip_attach)
        except OpenStackCloudTimeout:
            if self._use_neutron_floating() and created:
                # We are here because we created an IP on the port
                # It failed. Delete so as not to leak an unmanaged
                # resource
                self.log.error(
                    "Timeout waiting for floating IP to become"
                    " active. Floating IP %(ip)s:%(id)s was created for"
                    " server %(server)s but is being deleted due to"
                    " activation failure.", {
                        'ip': f_ip['floating_ip_address'],
                        'id': f_ip['id'],
                        'server': server['id']})
                try:
                    self.delete_floating_ip(f_ip['id'])
                except Exception as e:
                    self.log.error(
                        "FIP LEAK: Attempted to delete floating ip "
                        "%(fip)s but received %(exc)s exception: %(err)s",
                        {'fip': f_ip['id'], 'exc': e.__class__, 'err': str(e)})
                    raise e
            raise

    def add_ips_to_server(
            self, server, auto_ip=True, ips=None, ip_pool=None,
            wait=False, timeout=60, reuse=True, fixed_address=None,
            nat_destination=None):
        if ip_pool:
            server = self._add_ip_from_pool(
                server, ip_pool, reuse=reuse, wait=wait, timeout=timeout,
                fixed_address=fixed_address, nat_destination=nat_destination)
        elif ips:
            server = self.add_ip_list(
                server, ips, wait=wait, timeout=timeout,
                fixed_address=fixed_address)
        elif auto_ip:
            if self._needs_floating_ip(server, nat_destination):
                server = self._add_auto_ip(
                    server, wait=wait, timeout=timeout, reuse=reuse)
        return server

    def _needs_floating_ip(self, server, nat_destination):
        """Figure out if auto_ip should add a floating ip to this server.

        If the server has a public_v4 it does not need a floating ip.

        If the server does not have a private_v4 it does not need a
        floating ip.

        If self.private then the server does not need a floating ip.

        If the cloud runs nova, and the server has a private_v4 and not
        a public_v4, then the server needs a floating ip.

        If the server has a private_v4 and no public_v4 and the cloud has
        a network from which floating IPs come that is connected via a
        router to the network from which the private_v4 address came,
        then the server needs a floating ip.

        If the server has a private_v4 and no public_v4 and the cloud
        does not have a network from which floating ips come, or it has
        one but that network is not connected to the network from which
        the server's private_v4 address came via a router, then the
        server does not need a floating ip.
        """
        if not self._has_floating_ips():
            return False

        if server['public_v4']:
            return False

        if not server['private_v4']:
            return False

        if self.private:
            return False

        if not self.has_service('network'):
            return True

        # No floating ip network - no FIPs
        try:
            self._get_floating_network_id()
        except OpenStackCloudException:
            return False

        (port_obj, fixed_ip_address) = self._nat_destination_port(
            server, nat_destination=nat_destination)

        if not port_obj or not fixed_ip_address:
            return False

        return True

    def _get_boot_from_volume_kwargs(
            self, image, boot_from_volume, boot_volume, volume_size,
            terminate_volume, volumes, kwargs):
        """Return block device mappings

        :param image: Image dict, name or id to boot with.

        """
        # TODO(mordred) We're only testing this in functional tests. We need
        # to add unit tests for this too.
        if boot_volume or boot_from_volume or volumes:
            kwargs.setdefault('block_device_mapping_v2', [])
        else:
            return kwargs

        # If we have boot_from_volume but no root volume, then we're
        # booting an image from volume
        if boot_volume:
            volume = self.get_volume(boot_volume)
            if not volume:
                raise OpenStackCloudException(
                    'Volume {boot_volume} is not a valid volume'
                    ' in {cloud}:{region}'.format(
                        boot_volume=boot_volume,
                        cloud=self.name, region=self.config.region_name))
            block_mapping = {
                'boot_index': '0',
                'delete_on_termination': terminate_volume,
                'destination_type': 'volume',
                'uuid': volume['id'],
                'source_type': 'volume',
            }
            kwargs['block_device_mapping_v2'].append(block_mapping)
            kwargs['imageRef'] = ''
        elif boot_from_volume:

            if isinstance(image, dict):
                image_obj = image
            else:
                image_obj = self.get_image(image)
            if not image_obj:
                raise OpenStackCloudException(
                    'Image {image} is not a valid image in'
                    ' {cloud}:{region}'.format(
                        image=image,
                        cloud=self.name, region=self.config.region_name))

            block_mapping = {
                'boot_index': '0',
                'delete_on_termination': terminate_volume,
                'destination_type': 'volume',
                'uuid': image_obj['id'],
                'source_type': 'image',
                'volume_size': volume_size,
            }
            kwargs['imageRef'] = ''
            kwargs['block_device_mapping_v2'].append(block_mapping)
        if volumes and kwargs['imageRef']:
            # If we're attaching volumes on boot but booting from an image,
            # we need to specify that in the BDM.
            block_mapping = {
                u'boot_index': 0,
                u'delete_on_termination': True,
                u'destination_type': u'local',
                u'source_type': u'image',
                u'uuid': kwargs['imageRef'],
            }
            kwargs['block_device_mapping_v2'].append(block_mapping)
        for volume in volumes:
            volume_obj = self.get_volume(volume)
            if not volume_obj:
                raise OpenStackCloudException(
                    'Volume {volume} is not a valid volume'
                    ' in {cloud}:{region}'.format(
                        volume=volume,
                        cloud=self.name, region=self.config.region_name))
            block_mapping = {
                'boot_index': '-1',
                'delete_on_termination': False,
                'destination_type': 'volume',
                'uuid': volume_obj['id'],
                'source_type': 'volume',
            }
            kwargs['block_device_mapping_v2'].append(block_mapping)
        if boot_volume or boot_from_volume or volumes:
            self.list_volumes.invalidate(self)
        return kwargs

    def _encode_server_userdata(self, userdata):
        if hasattr(userdata, 'read'):
            userdata = userdata.read()

        if not isinstance(userdata, six.binary_type):
            # If the userdata passed in is bytes, just send it unmodified
            if not isinstance(userdata, six.string_types):
                raise TypeError("%s can't be encoded" % type(text))
            # If it's not bytes, make it bytes
            userdata = userdata.encode('utf-8', 'strict')

        # Once we have base64 bytes, make them into a utf-8 string for REST
        return base64.b64encode(userdata).decode('utf-8')

    @_utils.valid_kwargs(
        'meta', 'files', 'userdata',
        'reservation_id', 'return_raw', 'min_count',
        'max_count', 'security_groups', 'key_name',
        'availability_zone', 'block_device_mapping',
        'block_device_mapping_v2', 'nics', 'scheduler_hints',
        'config_drive', 'admin_pass', 'disk_config')
    def create_server(
            self, name, image=None, flavor=None,
            auto_ip=True, ips=None, ip_pool=None,
            root_volume=None, terminate_volume=False,
            wait=False, timeout=180, reuse_ips=True,
            network=None, boot_from_volume=False, volume_size='50',
            boot_volume=None, volumes=None, nat_destination=None,
            group=None,
            **kwargs):
        """Create a virtual server instance.

        :param name: Something to name the server.
        :param image: Image dict, name or ID to boot with. image is required
                      unless boot_volume is given.
        :param flavor: Flavor dict, name or ID to boot onto.
        :param auto_ip: Whether to take actions to find a routable IP for
                        the server. (defaults to True)
        :param ips: List of IPs to attach to the server (defaults to None)
        :param ip_pool: Name of the network or floating IP pool to get an
                        address from. (defaults to None)
        :param root_volume: Name or ID of a volume to boot from
                            (defaults to None - deprecated, use boot_volume)
        :param boot_volume: Name or ID of a volume to boot from
                            (defaults to None)
        :param terminate_volume: If booting from a volume, whether it should
                                 be deleted when the server is destroyed.
                                 (defaults to False)
        :param volumes: (optional) A list of volumes to attach to the server
        :param meta: (optional) A dict of arbitrary key/value metadata to
                     store for this server. Both keys and values must be
                     <=255 characters.
        :param files: (optional, deprecated) A dict of files to overwrite
                      on the server upon boot. Keys are file names (i.e.
                      ``/etc/passwd``) and values
                      are the file contents (either as a string or as a
                      file-like object). A maximum of five entries is allowed,
                      and each file must be 10k or less.
        :param reservation_id: a UUID for the set of servers being requested.
        :param min_count: (optional extension) The minimum number of
                          servers to launch.
        :param max_count: (optional extension) The maximum number of
                          servers to launch.
        :param security_groups: A list of security group names
        :param userdata: user data to pass to be exposed by the metadata
                      server this can be a file type object as well or a
                      string.
        :param key_name: (optional extension) name of previously created
                      keypair to inject into the instance.
        :param availability_zone: Name of the availability zone for instance
                                  placement.
        :param block_device_mapping: (optional) A dict of block
                      device mappings for this server.
        :param block_device_mapping_v2: (optional) A dict of block
                      device mappings for this server.
        :param nics:  (optional extension) an ordered list of nics to be
                      added to this server, with information about
                      connected networks, fixed IPs, port etc.
        :param scheduler_hints: (optional extension) arbitrary key-value pairs
                            specified by the client to help boot an instance
        :param config_drive: (optional extension) value for config drive
                            either boolean, or volume-id
        :param disk_config: (optional extension) control how the disk is
                            partitioned when the server is created.  possible
                            values are 'AUTO' or 'MANUAL'.
        :param admin_pass: (optional extension) add a user supplied admin
                           password.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param reuse_ips: (optional) Whether to attempt to reuse pre-existing
                                     floating ips should a floating IP be
                                     needed (defaults to True)
        :param network: (optional) Network dict or name or ID to attach the
                        server to.  Mutually exclusive with the nics parameter.
                        Can also be be a list of network names or IDs or
                        network dicts.
        :param boot_from_volume: Whether to boot from volume. 'boot_volume'
                                 implies True, but boot_from_volume=True with
                                 no boot_volume is valid and will create a
                                 volume from the image and use that.
        :param volume_size: When booting an image from volume, how big should
                            the created volume be? Defaults to 50.
        :param nat_destination: Which network should a created floating IP
                                be attached to, if it's not possible to
                                infer from the cloud's configuration.
                                (Optional, defaults to None)
        :param group: ServerGroup dict, name or id to boot the server in.
                      If a group is provided in both scheduler_hints and in
                      the group param, the group param will win.
                      (Optional, defaults to None)
        :returns: A ``munch.Munch`` representing the created server.
        :raises: OpenStackCloudException on operation error.
        """
        # TODO(shade) Image is optional but flavor is not - yet flavor comes
        # after image in the argument list. Doh.
        if not flavor:
            raise TypeError(
                "create_server() missing 1 required argument: 'flavor'")
        if not image and not boot_volume:
            raise TypeError(
                "create_server() requires either 'image' or 'boot_volume'")
        # TODO(mordred) Add support for description starting in 2.19
        security_groups = kwargs.get('security_groups', [])
        if security_groups and not isinstance(kwargs['security_groups'], list):
            security_groups = [security_groups]
        if security_groups:
            kwargs['security_groups'] = []
            for sec_group in security_groups:
                kwargs['security_groups'].append(dict(name=sec_group))
        if 'userdata' in kwargs:
            user_data = kwargs.pop('userdata')
            if user_data:
                kwargs['user_data'] = self._encode_server_userdata(user_data)
        for (desired, given) in (
                ('OS-DCF:diskConfig', 'disk_config'),
                ('config_drive', 'config_drive'),
                ('key_name', 'key_name'),
                ('metadata', 'meta'),
                ('adminPass', 'admin_pass')):
            value = kwargs.pop(given, None)
            if value:
                kwargs[desired] = value

        hints = kwargs.pop('scheduler_hints', {})
        if group:
            group_obj = self.get_server_group(group)
            if not group_obj:
                raise OpenStackCloudException(
                    "Server Group {group} was requested but was not found"
                    " on the cloud".format(group=group))
            hints['group'] = group_obj['id']
        if hints:
            kwargs['os:scheduler_hints'] = hints
        kwargs.setdefault('max_count', kwargs.get('max_count', 1))
        kwargs.setdefault('min_count', kwargs.get('min_count', 1))

        if 'nics' in kwargs and not isinstance(kwargs['nics'], list):
            if isinstance(kwargs['nics'], dict):
                # Be nice and help the user out
                kwargs['nics'] = [kwargs['nics']]
            else:
                raise OpenStackCloudException(
                    'nics parameter to create_server takes a list of dicts.'
                    ' Got: {nics}'.format(nics=kwargs['nics']))

        if network and ('nics' not in kwargs or not kwargs['nics']):
            nics = []
            if not isinstance(network, list):
                network = [network]
            for net_name in network:
                if isinstance(net_name, dict) and 'id' in net_name:
                    network_obj = net_name
                else:
                    network_obj = self.get_network(name_or_id=net_name)
                if not network_obj:
                    raise OpenStackCloudException(
                        'Network {network} is not a valid network in'
                        ' {cloud}:{region}'.format(
                            network=network,
                            cloud=self.name, region=self.config.region_name))
                nics.append({'net-id': network_obj['id']})

            kwargs['nics'] = nics
        if not network and ('nics' not in kwargs or not kwargs['nics']):
            default_network = self.get_default_network()
            if default_network:
                kwargs['nics'] = [{'net-id': default_network['id']}]

        networks = []
        for nic in kwargs.pop('nics', []):
            net = {}
            if 'net-id' in nic:
                # TODO(mordred) Make sure this is in uuid format
                net['uuid'] = nic.pop('net-id')
                # If there's a net-id, ignore net-name
                nic.pop('net-name', None)
            elif 'net-name' in nic:
                nic_net = self.get_network(nic['net-name'])
                if not nic_net:
                    raise OpenStackCloudException(
                        "Requested network {net} could not be found.".format(
                            net=nic['net-name']))
                net['uuid'] = nic_net['id']
            # TODO(mordred) Add support for tag if server supports microversion
            # 2.32-2.36 or >= 2.42
            for key in ('port', 'fixed_ip'):
                if key in nic:
                    net[key] = nic.pop(key)
            if 'port-id' in nic:
                net['port'] = nic.pop('port-id')
            if nic:
                raise OpenStackCloudException(
                    "Additional unsupported keys given for server network"
                    " creation: {keys}".format(keys=nic.keys()))
            networks.append(net)
        if networks:
            kwargs['networks'] = networks

        if image:
            if isinstance(image, dict):
                kwargs['imageRef'] = image['id']
            else:
                kwargs['imageRef'] = self.get_image(image).id
        if isinstance(flavor, dict):
            kwargs['flavorRef'] = flavor['id']
        else:
            kwargs['flavorRef'] = self.get_flavor(flavor, get_extra=False).id

        if volumes is None:
            volumes = []

        # nova cli calls this boot_volume. Let's be the same
        if root_volume and not boot_volume:
            boot_volume = root_volume

        kwargs = self._get_boot_from_volume_kwargs(
            image=image, boot_from_volume=boot_from_volume,
            boot_volume=boot_volume, volume_size=str(volume_size),
            terminate_volume=terminate_volume,
            volumes=volumes, kwargs=kwargs)

        kwargs['name'] = name
        endpoint = '/servers'
        # TODO(mordred) We're only testing this in functional tests. We need
        # to add unit tests for this too.
        if 'block_device_mapping_v2' in kwargs:
            endpoint = '/os-volumes_boot'
        with _utils.shade_exceptions("Error in creating instance"):
            data = _adapter._json_response(
                self.compute.post(endpoint, json={'server': kwargs}))
            server = self._get_and_munchify('server', data)
            admin_pass = server.get('adminPass') or kwargs.get('admin_pass')
            if not wait:
                # This is a direct get call to skip the list_servers
                # cache which has absolutely no chance of containing the
                # new server.
                # Only do this if we're not going to wait for the server
                # to complete booting, because the only reason we do it
                # is to get a server record that is the return value from
                # get/list rather than the return value of create. If we're
                # going to do the wait loop below, this is a waste of a call
                server = self.get_server_by_id(server.id)
                if server.status == 'ERROR':
                    raise OpenStackCloudCreateException(
                        resource='server', resource_id=server.id)

        if wait:
            server = self.wait_for_server(
                server,
                auto_ip=auto_ip, ips=ips, ip_pool=ip_pool,
                reuse=reuse_ips, timeout=timeout,
                nat_destination=nat_destination,
            )

        server.adminPass = admin_pass
        return server

    def wait_for_server(
            self, server, auto_ip=True, ips=None, ip_pool=None,
            reuse=True, timeout=180, nat_destination=None):
        """
        Wait for a server to reach ACTIVE status.
        """
        server_id = server['id']
        timeout_message = "Timeout waiting for the server to come up."
        start_time = time.time()

        # There is no point in iterating faster than the list_servers cache
        for count in utils.iterate_timeout(
                timeout,
                timeout_message,
                # if _SERVER_AGE is 0 we still want to wait a bit
                # to be friendly with the server.
                wait=self._SERVER_AGE or 2):
            try:
                # Use the get_server call so that the list_servers
                # cache can be leveraged
                server = self.get_server(server_id)
            except Exception:
                continue
            if not server:
                continue

            # We have more work to do, but the details of that are
            # hidden from the user. So, calculate remaining timeout
            # and pass it down into the IP stack.
            remaining_timeout = timeout - int(time.time() - start_time)
            if remaining_timeout <= 0:
                raise OpenStackCloudTimeout(timeout_message)

            server = self.get_active_server(
                server=server, reuse=reuse,
                auto_ip=auto_ip, ips=ips, ip_pool=ip_pool,
                wait=True, timeout=remaining_timeout,
                nat_destination=nat_destination)

            if server is not None and server['status'] == 'ACTIVE':
                return server

    def get_active_server(
            self, server, auto_ip=True, ips=None, ip_pool=None,
            reuse=True, wait=False, timeout=180, nat_destination=None):

        if server['status'] == 'ERROR':
            if 'fault' in server and 'message' in server['fault']:
                raise OpenStackCloudException(
                    "Error in creating the server: {reason}".format(
                        reason=server['fault']['message']),
                    extra_data=dict(server=server))

            raise OpenStackCloudException(
                "Error in creating the server", extra_data=dict(server=server))

        if server['status'] == 'ACTIVE':
            if 'addresses' in server and server['addresses']:
                return self.add_ips_to_server(
                    server, auto_ip, ips, ip_pool, reuse=reuse,
                    nat_destination=nat_destination,
                    wait=wait, timeout=timeout)

            self.log.debug(
                'Server %(server)s reached ACTIVE state without'
                ' being allocated an IP address.'
                ' Deleting server.', {'server': server['id']})
            try:
                self._delete_server(
                    server=server, wait=wait, timeout=timeout)
            except Exception as e:
                raise OpenStackCloudException(
                    'Server reached ACTIVE state without being'
                    ' allocated an IP address AND then could not'
                    ' be deleted: {0}'.format(e),
                    extra_data=dict(server=server))
            raise OpenStackCloudException(
                'Server reached ACTIVE state without being'
                ' allocated an IP address.',
                extra_data=dict(server=server))
        return None

    def rebuild_server(self, server_id, image_id, admin_pass=None,
                       detailed=False, bare=False,
                       wait=False, timeout=180):
        kwargs = {}
        if image_id:
            kwargs['imageRef'] = image_id
        if admin_pass:
            kwargs['adminPass'] = admin_pass

        data = _adapter._json_response(
            self.compute.post(
                '/servers/{server_id}/action'.format(server_id=server_id),
                json={'rebuild': kwargs}),
            error_message="Error in rebuilding instance")
        server = self._get_and_munchify('server', data)
        if not wait:
            return self._expand_server(
                self._normalize_server(server), bare=bare, detailed=detailed)

        admin_pass = server.get('adminPass') or admin_pass
        for count in utils.iterate_timeout(
                timeout,
                "Timeout waiting for server {0} to "
                "rebuild.".format(server_id),
                wait=self._SERVER_AGE):
            try:
                server = self.get_server(server_id, bare=True)
            except Exception:
                continue
            if not server:
                continue

            if server['status'] == 'ERROR':
                raise OpenStackCloudException(
                    "Error in rebuilding the server",
                    extra_data=dict(server=server))

            if server['status'] == 'ACTIVE':
                server.adminPass = admin_pass
                break

        return self._expand_server(server, detailed=detailed, bare=bare)

    def set_server_metadata(self, name_or_id, metadata):
        """Set metadata in a server instance.

        :param str name_or_id: The name or ID of the server instance
            to update.
        :param dict metadata: A dictionary with the key=value pairs
            to set in the server instance. It only updates the key=value
            pairs provided. Existing ones will remain untouched.

        :raises: OpenStackCloudException on operation error.
        """
        server = self.get_server(name_or_id, bare=True)
        if not server:
            raise OpenStackCloudException(
                'Invalid Server {server}'.format(server=name_or_id))

        _adapter._json_response(
            self.compute.post(
                '/servers/{server_id}/metadata'.format(server_id=server['id']),
                json={'metadata': metadata}),
            error_message='Error updating server metadata')

    def delete_server_metadata(self, name_or_id, metadata_keys):
        """Delete metadata from a server instance.

        :param str name_or_id: The name or ID of the server instance
            to update.
        :param metadata_keys: A list with the keys to be deleted
            from the server instance.

        :raises: OpenStackCloudException on operation error.
        """
        server = self.get_server(name_or_id, bare=True)
        if not server:
            raise OpenStackCloudException(
                'Invalid Server {server}'.format(server=name_or_id))

        for key in metadata_keys:
            error_message = 'Error deleting metadata {key} on {server}'.format(
                key=key, server=name_or_id)
            _adapter._json_response(
                self.compute.delete(
                    '/servers/{server_id}/metadata/{key}'.format(
                        server_id=server['id'],
                        key=key)),
                error_message=error_message)

    def delete_server(
            self, name_or_id, wait=False, timeout=180, delete_ips=False,
            delete_ip_retry=1):
        """Delete a server instance.

        :param name_or_id: name or ID of the server to delete
        :param bool wait: If true, waits for server to be deleted.
        :param int timeout: Seconds to wait for server deletion.
        :param bool delete_ips: If true, deletes any floating IPs
            associated with the instance.
        :param int delete_ip_retry: Number of times to retry deleting
            any floating ips, should the first try be unsuccessful.

        :returns: True if delete succeeded, False otherwise if the
            server does not exist.

        :raises: OpenStackCloudException on operation error.
        """
        # If delete_ips is True, we need the server to not be bare.
        server = self.get_server(name_or_id, bare=True)
        if not server:
            return False

        # This portion of the code is intentionally left as a separate
        # private method in order to avoid an unnecessary API call to get
        # a server we already have.
        return self._delete_server(
            server, wait=wait, timeout=timeout, delete_ips=delete_ips,
            delete_ip_retry=delete_ip_retry)

    def _delete_server_floating_ips(self, server, delete_ip_retry):
        # Does the server have floating ips in its
        # addresses dict? If not, skip this.
        server_floats = meta.find_nova_interfaces(
            server['addresses'], ext_tag='floating')
        for fip in server_floats:
            try:
                ip = self.get_floating_ip(id=None, filters={
                    'floating_ip_address': fip['addr']})
            except OpenStackCloudURINotFound:
                # We're deleting. If it doesn't exist - awesome
                # NOTE(mordred) If the cloud is a nova FIP cloud but
                #               floating_ip_source is set to neutron, this
                #               can lead to a FIP leak.
                continue
            if not ip:
                continue
            deleted = self.delete_floating_ip(
                ip['id'], retry=delete_ip_retry)
            if not deleted:
                raise OpenStackCloudException(
                    "Tried to delete floating ip {floating_ip}"
                    " associated with server {id} but there was"
                    " an error deleting it. Not deleting server.".format(
                        floating_ip=ip['floating_ip_address'],
                        id=server['id']))

    def _delete_server(
            self, server, wait=False, timeout=180, delete_ips=False,
            delete_ip_retry=1):
        if not server:
            return False

        if delete_ips and self._has_floating_ips():
            self._delete_server_floating_ips(server, delete_ip_retry)

        try:
            _adapter._json_response(
                self.compute.delete(
                    '/servers/{id}'.format(id=server['id'])),
                error_message="Error in deleting server")
        except OpenStackCloudURINotFound:
            return False
        except Exception:
            raise

        if not wait:
            return True

        # If the server has volume attachments, or if it has booted
        # from volume, deleting it will change volume state so we will
        # need to invalidate the cache. Avoid the extra API call if
        # caching is not enabled.
        reset_volume_cache = False
        if (self.cache_enabled
                and self.has_service('volume')
                and self.get_volumes(server)):
            reset_volume_cache = True

        for count in utils.iterate_timeout(
                timeout,
                "Timed out waiting for server to get deleted.",
                # if _SERVER_AGE is 0 we still want to wait a bit
                # to be friendly with the server.
                wait=self._SERVER_AGE or 2):
            with _utils.shade_exceptions("Error in deleting server"):
                server = self.get_server(server['id'], bare=True)
                if not server:
                    break

        if reset_volume_cache:
            self.list_volumes.invalidate(self)

        # Reset the list servers cache time so that the next list server
        # call gets a new list
        self._servers_time = self._servers_time - self._SERVER_AGE
        return True

    @_utils.valid_kwargs(
        'name', 'description')
    def update_server(self, name_or_id, detailed=False, bare=False, **kwargs):
        """Update a server.

        :param name_or_id: Name of the server to be updated.
        :param detailed: Whether or not to add detailed additional information.
                         Defaults to False.
        :param bare: Whether to skip adding any additional information to the
                     server record. Defaults to False, meaning the addresses
                     dict will be populated as needed from neutron. Setting
                     to True implies detailed = False.
        :name: New name for the server
        :description: New description for the server

        :returns: a dictionary representing the updated server.

        :raises: OpenStackCloudException on operation error.
        """
        server = self.get_server(name_or_id=name_or_id, bare=True)
        if server is None:
            raise OpenStackCloudException(
                "failed to find server '{server}'".format(server=name_or_id))

        data = _adapter._json_response(
            self.compute.put(
                '/servers/{server_id}'.format(server_id=server['id']),
                json={'server': kwargs}),
            error_message="Error updating server {0}".format(name_or_id))
        server = self._normalize_server(
            self._get_and_munchify('server', data))
        return self._expand_server(server, bare=bare, detailed=detailed)

    def create_server_group(self, name, policies):
        """Create a new server group.

        :param name: Name of the server group being created
        :param policies: List of policies for the server group.

        :returns: a dict representing the new server group.

        :raises: OpenStackCloudException on operation error.
        """
        data = _adapter._json_response(
            self.compute.post(
                '/os-server-groups',
                json={
                    'server_group': {
                        'name': name,
                        'policies': policies}}),
            error_message="Unable to create server group {name}".format(
                name=name))
        return self._get_and_munchify('server_group', data)

    def delete_server_group(self, name_or_id):
        """Delete a server group.

        :param name_or_id: Name or ID of the server group to delete

        :returns: True if delete succeeded, False otherwise

        :raises: OpenStackCloudException on operation error.
        """
        server_group = self.get_server_group(name_or_id)
        if not server_group:
            self.log.debug("Server group %s not found for deleting",
                           name_or_id)
            return False

        _adapter._json_response(
            self.compute.delete(
                '/os-server-groups/{id}'.format(id=server_group['id'])),
            error_message="Error deleting server group {name}".format(
                name=name_or_id))

        return True

    def list_containers(self, full_listing=True):
        """List containers.

        :param full_listing: Ignored. Present for backwards compat

        :returns: list of Munch of the container objects

        :raises: OpenStackCloudException on operation error.
        """
        return self._object_store_client.get('/', params=dict(format='json'))

    def get_container(self, name, skip_cache=False):
        if skip_cache or name not in self._container_cache:
            try:
                container = self._object_store_client.head(name)
                self._container_cache[name] = container.headers
            except OpenStackCloudHTTPError as e:
                if e.response.status_code == 404:
                    return None
                raise
        return self._container_cache[name]

    def create_container(self, name, public=False):
        container = self.get_container(name)
        if container:
            return container
        self._object_store_client.put(name)
        if public:
            self.set_container_access(name, 'public')
        return self.get_container(name, skip_cache=True)

    def delete_container(self, name):
        try:
            self._object_store_client.delete(name)
            return True
        except OpenStackCloudHTTPError as e:
            if e.response.status_code == 404:
                return False
            if e.response.status_code == 409:
                raise OpenStackCloudException(
                    'Attempt to delete container {container} failed. The'
                    ' container is not empty. Please delete the objects'
                    ' inside it before deleting the container'.format(
                        container=name))
            raise

    def update_container(self, name, headers):
        self._object_store_client.post(name, headers=headers)

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
        for key, value in OBJECT_CONTAINER_ACLS.items():
            # Convert to string for the comparison because swiftclient
            # returns byte values as bytes sometimes and apparently ==
            # on bytes doesn't work like you'd think
            if str(acl) == str(value):
                return key
        raise OpenStackCloudException(
            "Could not determine container access for ACL: %s." % acl)

    def _get_file_hashes(self, filename):
        file_key = "{filename}:{mtime}".format(
            filename=filename,
            mtime=os.stat(filename).st_mtime)
        if file_key not in self._file_hash_cache:
            self.log.debug(
                'Calculating hashes for %(filename)s', {'filename': filename})
            md5 = hashlib.md5()
            sha256 = hashlib.sha256()
            with open(filename, 'rb') as file_obj:
                for chunk in iter(lambda: file_obj.read(8192), b''):
                    md5.update(chunk)
                    sha256.update(chunk)
            self._file_hash_cache[file_key] = dict(
                md5=md5.hexdigest(), sha256=sha256.hexdigest())
            self.log.debug(
                "Image file %(filename)s md5:%(md5)s sha256:%(sha256)s",
                {'filename': filename,
                 'md5': self._file_hash_cache[file_key]['md5'],
                 'sha256': self._file_hash_cache[file_key]['sha256']})
        return (self._file_hash_cache[file_key]['md5'],
                self._file_hash_cache[file_key]['sha256'])

    @_utils.cache_on_arguments()
    def get_object_capabilities(self):
        # The endpoint in the catalog has version and project-id in it
        # To get capabilities, we have to disassemble and reassemble the URL
        # This logic is taken from swiftclient
        endpoint = urllib.parse.urlparse(
            self._object_store_client.get_endpoint())
        url = "{scheme}://{netloc}/info".format(
            scheme=endpoint.scheme, netloc=endpoint.netloc)

        return self._object_store_client.get(url)

    def get_object_segment_size(self, segment_size):
        """Get a segment size that will work given capabilities"""
        if segment_size is None:
            segment_size = DEFAULT_OBJECT_SEGMENT_SIZE
        min_segment_size = 0
        try:
            caps = self.get_object_capabilities()
        except OpenStackCloudHTTPError as e:
            if e.response.status_code in (404, 412):
                # Clear the exception so that it doesn't linger
                # and get reported as an Inner Exception later
                _utils._exc_clear()
                server_max_file_size = DEFAULT_MAX_FILE_SIZE
                self.log.info(
                    "Swift capabilities not supported. "
                    "Using default max file size.")
            else:
                raise
        else:
            server_max_file_size = caps.get('swift', {}).get('max_file_size',
                                                             0)
            min_segment_size = caps.get('slo', {}).get('min_segment_size', 0)

        if segment_size > server_max_file_size:
            return server_max_file_size
        if segment_size < min_segment_size:
            return min_segment_size
        return segment_size

    def is_object_stale(
            self, container, name, filename, file_md5=None, file_sha256=None):

        metadata = self.get_object_metadata(container, name)
        if not metadata:
            self.log.debug(
                "swift stale check, no object: {container}/{name}".format(
                    container=container, name=name))
            return True

        if not (file_md5 or file_sha256):
            (file_md5, file_sha256) = self._get_file_hashes(filename)
        md5_key = metadata.get(OBJECT_MD5_KEY, '')
        sha256_key = metadata.get(OBJECT_SHA256_KEY, '')
        up_to_date = self._hashes_up_to_date(
            md5=file_md5, sha256=file_sha256,
            md5_key=md5_key, sha256_key=sha256_key)

        if not up_to_date:
            self.log.debug(
                "swift checksum mismatch: "
                " %(filename)s!=%(container)s/%(name)s",
                {'filename': filename, 'container': container, 'name': name})
            return True

        self.log.debug(
            "swift object up to date: %(container)s/%(name)s",
            {'container': container, 'name': name})
        return False

    def create_object(
            self, container, name, filename=None,
            md5=None, sha256=None, segment_size=None,
            use_slo=True, metadata=None,
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
        :param use_slo: If the object is large enough to need to be a Large
            Object, use a static rather than dynamic object. Static Objects
            will delete segment objects when the manifest object is deleted.
            (optional, defaults to True)
        :param metadata: This dict will get changed into headers that set
            metadata of the object

        :raises: ``OpenStackCloudException`` on operation error.
        """
        if not metadata:
            metadata = {}

        if not filename:
            filename = name

        # segment_size gets used as a step value in a range call, so needs
        # to be an int
        if segment_size:
            segment_size = int(segment_size)
        segment_size = self.get_object_segment_size(segment_size)
        file_size = os.path.getsize(filename)

        if not (md5 or sha256):
            (md5, sha256) = self._get_file_hashes(filename)
        headers[OBJECT_MD5_KEY] = md5 or ''
        headers[OBJECT_SHA256_KEY] = sha256 or ''
        for (k, v) in metadata.items():
            headers['x-object-meta-' + k] = v

        # On some clouds this is not necessary. On others it is. I'm confused.
        self.create_container(container)

        if self.is_object_stale(container, name, filename, md5, sha256):

            endpoint = '{container}/{name}'.format(
                container=container, name=name)
            self.log.debug(
                "swift uploading %(filename)s to %(endpoint)s",
                {'filename': filename, 'endpoint': endpoint})

            if file_size <= segment_size:
                self._upload_object(endpoint, filename, headers)
            else:
                self._upload_large_object(
                    endpoint, filename, headers,
                    file_size, segment_size, use_slo)

    def _upload_object(self, endpoint, filename, headers):
        return self._object_store_client.put(
            endpoint, headers=headers, data=open(filename, 'r'))

    def _get_file_segments(self, endpoint, filename, file_size, segment_size):
        # Use an ordered dict here so that testing can replicate things
        segments = collections.OrderedDict()
        for (index, offset) in enumerate(range(0, file_size, segment_size)):
            remaining = file_size - (index * segment_size)
            segment = _utils.FileSegment(
                filename, offset,
                segment_size if segment_size < remaining else remaining)
            name = '{endpoint}/{index:0>6}'.format(
                endpoint=endpoint, index=index)
            segments[name] = segment
        return segments

    def _object_name_from_url(self, url):
        '''Get container_name/object_name from the full URL called.

        Remove the Swift endpoint from the front of the URL, and remove
        the leaving / that will leave behind.'''
        endpoint = self._object_store_client.get_endpoint()
        object_name = url.replace(endpoint, '')
        if object_name.startswith('/'):
            object_name = object_name[1:]
        return object_name

    def _add_etag_to_manifest(self, segment_results, manifest):
        for result in segment_results:
            if 'Etag' not in result.headers:
                continue
            name = self._object_name_from_url(result.url)
            for entry in manifest:
                if entry['path'] == '/{name}'.format(name=name):
                    entry['etag'] = result.headers['Etag']

    def _upload_large_object(
            self, endpoint, filename,
            headers, file_size, segment_size, use_slo):
        # If the object is big, we need to break it up into segments that
        # are no larger than segment_size, upload each of them individually
        # and then upload a manifest object. The segments can be uploaded in
        # parallel, so we'll use the async feature of the TaskManager.

        segment_futures = []
        segment_results = []
        retry_results = []
        retry_futures = []
        manifest = []

        # Get an OrderedDict with keys being the swift location for the
        # segment, the value a FileSegment file-like object that is a
        # slice of the data for the segment.
        segments = self._get_file_segments(
            endpoint, filename, file_size, segment_size)

        # Schedule the segments for upload
        for name, segment in segments.items():
            # Async call to put - schedules execution and returns a future
            segment_future = self._object_store_client.put(
                name, headers=headers, data=segment, run_async=True)
            segment_futures.append(segment_future)
            # TODO(mordred) Collect etags from results to add to this manifest
            # dict. Then sort the list of dicts by path.
            manifest.append(dict(
                path='/{name}'.format(name=name),
                size_bytes=segment.length))

        # Try once and collect failed results to retry
        segment_results, retry_results = task_manager.wait_for_futures(
            segment_futures, raise_on_error=False)

        self._add_etag_to_manifest(segment_results, manifest)

        for result in retry_results:
            # Grab the FileSegment for the failed upload so we can retry
            name = self._object_name_from_url(result.url)
            segment = segments[name]
            segment.seek(0)
            # Async call to put - schedules execution and returns a future
            segment_future = self._object_store_client.put(
                name, headers=headers, data=segment, run_async=True)
            # TODO(mordred) Collect etags from results to add to this manifest
            # dict. Then sort the list of dicts by path.
            retry_futures.append(segment_future)

        # If any segments fail the second time, just throw the error
        segment_results, retry_results = task_manager.wait_for_futures(
            retry_futures, raise_on_error=True)

        self._add_etag_to_manifest(segment_results, manifest)

        if use_slo:
            return self._finish_large_object_slo(endpoint, headers, manifest)
        else:
            return self._finish_large_object_dlo(endpoint, headers)

    def _finish_large_object_slo(self, endpoint, headers, manifest):
        # TODO(mordred) send an etag of the manifest, which is the md5sum
        # of the concatenation of the etags of the results
        headers = headers.copy()
        return self._object_store_client.put(
            endpoint,
            params={'multipart-manifest': 'put'},
            headers=headers, data=json.dumps(manifest))

    def _finish_large_object_dlo(self, endpoint, headers):
        headers = headers.copy()
        headers['X-Object-Manifest'] = endpoint
        return self._object_store_client.put(endpoint, headers=headers)

    def update_object(self, container, name, metadata=None, **headers):
        """Update the metadata of an object

        :param container: The name of the container the object is in
        :param name: Name for the object within the container.
        :param metadata: This dict will get changed into headers that set
            metadata of the object
        :param headers: These will be passed through to the object update
            API as HTTP Headers.

        :raises: ``OpenStackCloudException`` on operation error.
        """
        if not metadata:
            metadata = {}

        metadata_headers = {}

        for (k, v) in metadata.items():
            metadata_headers['x-object-meta-' + k] = v

        headers = dict(headers, **metadata_headers)

        return self._object_store_client.post(
            '{container}/{object}'.format(
                container=container, object=name),
            headers=headers)

    def list_objects(self, container, full_listing=True):
        """List objects.

        :param container: Name of the container to list objects in.
        :param full_listing: Ignored. Present for backwards compat

        :returns: list of Munch of the objects

        :raises: OpenStackCloudException on operation error.
        """
        return self._object_store_client.get(
            container, params=dict(format='json'))

    def delete_object(self, container, name, meta=None):
        """Delete an object from a container.

        :param string container: Name of the container holding the object.
        :param string name: Name of the object to delete.
        :param dict meta: Metadata for the object in question. (optional, will
                          be fetched if not provided)

        :returns: True if delete succeeded, False if the object was not found.

        :raises: OpenStackCloudException on operation error.
        """
        # TODO(mordred) DELETE for swift returns status in text/plain format
        # like so:
        #   Number Deleted: 15
        #   Number Not Found: 0
        #   Response Body:
        #   Response Status: 200 OK
        #   Errors:
        # We should ultimately do something with that
        try:
            if not meta:
                meta = self.get_object_metadata(container, name)
            if not meta:
                return False
            params = {}
            if meta.get('X-Static-Large-Object', None) == 'True':
                params['multipart-manifest'] = 'delete'
            self._object_store_client.delete(
                '{container}/{object}'.format(
                    container=container, object=name),
                params=params)
            return True
        except OpenStackCloudHTTPError:
            return False

    def delete_autocreated_image_objects(
            self, container=OBJECT_AUTOCREATE_CONTAINER):
        """Delete all objects autocreated for image uploads.

        This method should generally not be needed, as shade should clean up
        the objects it uses for object-based image creation. If something
        goes wrong and it is found that there are leaked objects, this method
        can be used to delete any objects that shade has created on the user's
        behalf in service of image uploads.
        """
        # This method only makes sense on clouds that use tasks
        if not self.image_api_use_tasks:
            return False

        deleted = False
        for obj in self.list_objects(container):
            meta = self.get_object_metadata(container, obj['name'])
            if meta.get(OBJECT_AUTOCREATE_KEY) == 'true':
                if self.delete_object(container, obj['name'], meta):
                    deleted = True
        return deleted

    def get_object_metadata(self, container, name):
        try:
            return self._object_store_client.head(
                '{container}/{object}'.format(
                    container=container, object=name)).headers
        except OpenStackCloudException as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_object(self, container, obj, query_string=None,
                   resp_chunk_size=1024, outfile=None):
        """Get the headers and body of an object

        :param string container: name of the container.
        :param string obj: name of the object.
        :param string query_string: query args for uri.
                                    (delimiter, prefix, etc.)
        :param int resp_chunk_size: chunk size of data to read. Only used
                                    if the results are being written to a
                                    file. (optional, defaults to 1k)
        :param outfile: Write the object to a file instead of
                        returning the contents. If this option is
                        given, body in the return tuple will be None. outfile
                        can either be a file path given as a string, or a
                        File like object.

        :returns: Tuple (headers, body) of the object, or None if the object
                  is not found (404)
        :raises: OpenStackCloudException on operation error.
        """
        # TODO(mordred) implement resp_chunk_size
        try:
            endpoint = '{container}/{object}'.format(
                container=container, object=obj)
            if query_string:
                endpoint = '{endpoint}?{query_string}'.format(
                    endpoint=endpoint, query_string=query_string)
            response = self._object_store_client.get(
                endpoint, stream=True)
            response_headers = {
                k.lower(): v for k, v in response.headers.items()}
            if outfile:
                if isinstance(outfile, six.string_types):
                    outfile_handle = open(outfile, 'wb')
                else:
                    outfile_handle = outfile
                for chunk in response.iter_content(
                        resp_chunk_size, decode_unicode=False):
                    outfile_handle.write(chunk)
                if isinstance(outfile, six.string_types):
                    outfile_handle.close()
                else:
                    outfile_handle.flush()
                return (response_headers, None)
            else:
                return (response_headers, response.text)
        except OpenStackCloudHTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def create_subnet(self, network_name_or_id, cidr=None, ip_version=4,
                      enable_dhcp=False, subnet_name=None, tenant_id=None,
                      allocation_pools=None,
                      gateway_ip=None, disable_gateway_ip=False,
                      dns_nameservers=None, host_routes=None,
                      ipv6_ra_mode=None, ipv6_address_mode=None,
                      use_default_subnetpool=False):
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
        :param allocation_pools:
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
        :param bool disable_gateway_ip:
           Set to ``True`` if gateway IP address is disabled and ``False`` if
           enabled. It is not allowed with gateway_ip.
           Default is ``False``.
        :param dns_nameservers:
           A list of DNS name servers for the subnet. For example::

             [ "8.8.8.7", "8.8.8.8" ]

        :param host_routes:
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
        :param bool use_default_subnetpool:
           Use the default subnetpool for ``ip_version`` to obtain a CIDR. It
           is required to pass ``None`` to the ``cidr`` argument when enabling
           this option.

        :returns: The new subnet object.
        :raises: OpenStackCloudException on operation error.
        """

        if tenant_id is not None:
            filters = {'tenant_id': tenant_id}
        else:
            filters = None

        network = self.get_network(network_name_or_id, filters)
        if not network:
            raise OpenStackCloudException(
                "Network %s not found." % network_name_or_id)

        if disable_gateway_ip and gateway_ip:
            raise OpenStackCloudException(
                'arg:disable_gateway_ip is not allowed with arg:gateway_ip')

        if not cidr and not use_default_subnetpool:
            raise OpenStackCloudException(
                'arg:cidr is required when a subnetpool is not used')

        if cidr and use_default_subnetpool:
            raise OpenStackCloudException(
                'arg:cidr must be set to None when use_default_subnetpool == '
                'True')

        # Be friendly on ip_version and allow strings
        if isinstance(ip_version, six.string_types):
            try:
                ip_version = int(ip_version)
            except ValueError:
                raise OpenStackCloudException('ip_version must be an integer')

        # The body of the neutron message for the subnet we wish to create.
        # This includes attributes that are required or have defaults.
        subnet = {
            'network_id': network['id'],
            'ip_version': ip_version,
            'enable_dhcp': enable_dhcp
        }

        # Add optional attributes to the message.
        if cidr:
            subnet['cidr'] = cidr
        if subnet_name:
            subnet['name'] = subnet_name
        if tenant_id:
            subnet['tenant_id'] = tenant_id
        if allocation_pools:
            subnet['allocation_pools'] = allocation_pools
        if gateway_ip:
            subnet['gateway_ip'] = gateway_ip
        if disable_gateway_ip:
            subnet['gateway_ip'] = None
        if dns_nameservers:
            subnet['dns_nameservers'] = dns_nameservers
        if host_routes:
            subnet['host_routes'] = host_routes
        if ipv6_ra_mode:
            subnet['ipv6_ra_mode'] = ipv6_ra_mode
        if ipv6_address_mode:
            subnet['ipv6_address_mode'] = ipv6_address_mode
        if use_default_subnetpool:
            subnet['use_default_subnetpool'] = True

        data = self._network_client.post("/subnets.json",
                                         json={"subnet": subnet})

        return self._get_and_munchify('subnet', data)

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
            self.log.debug("Subnet %s not found for deleting", name_or_id)
            return False

        self._network_client.delete(
            "/subnets/{subnet_id}.json".format(subnet_id=subnet['id']))
        return True

    def update_subnet(self, name_or_id, subnet_name=None, enable_dhcp=None,
                      gateway_ip=None, disable_gateway_ip=None,
                      allocation_pools=None, dns_nameservers=None,
                      host_routes=None):
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
        :param bool disable_gateway_ip:
           Set to ``True`` if gateway IP address is disabled and ``False`` if
           enabled. It is not allowed with gateway_ip.
           Default is ``False``.
        :param allocation_pools:
           A list of dictionaries of the start and end addresses for the
           allocation pools. For example::

             [
               {
                 "start": "192.168.199.2",
                 "end": "192.168.199.254"
               }
             ]

        :param dns_nameservers:
           A list of DNS name servers for the subnet. For example::

             [ "8.8.8.7", "8.8.8.8" ]

        :param host_routes:
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
        if disable_gateway_ip:
            subnet['gateway_ip'] = None
        if allocation_pools:
            subnet['allocation_pools'] = allocation_pools
        if dns_nameservers:
            subnet['dns_nameservers'] = dns_nameservers
        if host_routes:
            subnet['host_routes'] = host_routes

        if not subnet:
            self.log.debug("No subnet data to update")
            return

        if disable_gateway_ip and gateway_ip:
            raise OpenStackCloudException(
                'arg:disable_gateway_ip is not allowed with arg:gateway_ip')

        curr_subnet = self.get_subnet(name_or_id)
        if not curr_subnet:
            raise OpenStackCloudException(
                "Subnet %s not found." % name_or_id)

        data = self._network_client.put(
            "/subnets/{subnet_id}.json".format(subnet_id=curr_subnet['id']),
            json={"subnet": subnet})
        return self._get_and_munchify('subnet', data)

    @_utils.valid_kwargs('name', 'admin_state_up', 'mac_address', 'fixed_ips',
                         'subnet_id', 'ip_address', 'security_groups',
                         'allowed_address_pairs', 'extra_dhcp_opts',
                         'device_owner', 'device_id')
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

        :returns: a ``munch.Munch`` describing the created port.

        :raises: ``OpenStackCloudException`` on operation error.
        """
        kwargs['network_id'] = network_id

        data = self._network_client.post(
            "/ports.json", json={'port': kwargs},
            error_message="Error creating port for network {0}".format(
                network_id))
        return self._get_and_munchify('port', data)

    @_utils.valid_kwargs('name', 'admin_state_up', 'fixed_ips',
                         'security_groups', 'allowed_address_pairs',
                         'extra_dhcp_opts', 'device_owner', 'device_id')
    def update_port(self, name_or_id, **kwargs):
        """Update a port

        Note: to unset an attribute use None value. To leave an attribute
        untouched just omit it.

        :param name_or_id: name or ID of the port to update. (Required)
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
        :param device_id: The ID of the resource this port is attached to.

        :returns: a ``munch.Munch`` describing the updated port.

        :raises: OpenStackCloudException on operation error.
        """
        port = self.get_port(name_or_id=name_or_id)
        if port is None:
            raise OpenStackCloudException(
                "failed to find port '{port}'".format(port=name_or_id))

        data = self._network_client.put(
            "/ports/{port_id}.json".format(port_id=port['id']),
            json={"port": kwargs},
            error_message="Error updating port {0}".format(name_or_id))
        return self._get_and_munchify('port', data)

    def delete_port(self, name_or_id):
        """Delete a port

        :param name_or_id: ID or name of the port to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        port = self.get_port(name_or_id=name_or_id)
        if port is None:
            self.log.debug("Port %s not found for deleting", name_or_id)
            return False

        self._network_client.delete(
            "/ports/{port_id}.json".format(port_id=port['id']),
            error_message="Error deleting port {0}".format(name_or_id))
        return True

    def create_security_group(self, name, description, project_id=None):
        """Create a new security group

        :param string name: A name for the security group.
        :param string description: Describes the security group.
        :param string project_id:
            Specify the project ID this security group will be created
            on (admin-only).

        :returns: A ``munch.Munch`` representing the new security group.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
                 not supported on this cloud.
        """

        # Security groups not supported
        if not self._has_secgroups():
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        data = []
        security_group_json = {
            'security_group': {
                'name': name, 'description': description
            }}
        if project_id is not None:
            security_group_json['security_group']['tenant_id'] = project_id
        if self._use_neutron_secgroups():
            data = self._network_client.post(
                '/security-groups.json',
                json=security_group_json,
                error_message="Error creating security group {0}".format(name))
        else:
            data = _adapter._json_response(self.compute.post(
                '/os-security-groups', json=security_group_json))
        return self._normalize_secgroup(
            self._get_and_munchify('security_group', data))

    def delete_security_group(self, name_or_id):
        """Delete a security group

        :param string name_or_id: The name or unique ID of the security group.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
                 not supported on this cloud.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        # TODO(mordred): Let's come back and stop doing a GET before we do
        #                the delete.
        secgroup = self.get_security_group(name_or_id)
        if secgroup is None:
            self.log.debug('Security group %s not found for deleting',
                           name_or_id)
            return False

        if self._use_neutron_secgroups():
            self._network_client.delete(
                '/security-groups/{sg_id}.json'.format(sg_id=secgroup['id']),
                error_message="Error deleting security group {0}".format(
                    name_or_id)
            )
            return True

        else:
            _adapter._json_response(self.compute.delete(
                '/os-security-groups/{id}'.format(id=secgroup['id'])))
            return True

    @_utils.valid_kwargs('name', 'description')
    def update_security_group(self, name_or_id, **kwargs):
        """Update a security group

        :param string name_or_id: Name or ID of the security group to update.
        :param string name: New name for the security group.
        :param string description: New description for the security group.

        :returns: A ``munch.Munch`` describing the updated security group.

        :raises: OpenStackCloudException on operation error.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        group = self.get_security_group(name_or_id)

        if group is None:
            raise OpenStackCloudException(
                "Security group %s not found." % name_or_id)

        if self._use_neutron_secgroups():
            data = self._network_client.put(
                '/security-groups/{sg_id}.json'.format(sg_id=group['id']),
                json={'security_group': kwargs},
                error_message="Error updating security group {0}".format(
                    name_or_id))
        else:
            for key in ('name', 'description'):
                kwargs.setdefault(key, group[key])
            data = _adapter._json_response(
                self.compute.put(
                    '/os-security-groups/{id}'.format(id=group['id']),
                    json={'security-group': kwargs}))
        return self._normalize_secgroup(
            self._get_and_munchify('security_group', data))

    def create_security_group_rule(self,
                                   secgroup_name_or_id,
                                   port_range_min=None,
                                   port_range_max=None,
                                   protocol=None,
                                   remote_ip_prefix=None,
                                   remote_group_id=None,
                                   direction='ingress',
                                   ethertype='IPv4',
                                   project_id=None):
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
        :param string project_id:
            Specify the project ID this security group will be created
            on (admin-only).

        :returns: A ``munch.Munch`` representing the new security group rule.

        :raises: OpenStackCloudException on operation error.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        secgroup = self.get_security_group(secgroup_name_or_id)
        if not secgroup:
            raise OpenStackCloudException(
                "Security group %s not found." % secgroup_name_or_id)

        if self._use_neutron_secgroups():
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
            if project_id is not None:
                rule_def['tenant_id'] = project_id

            data = self._network_client.post(
                '/security-group-rules.json',
                json={'security_group_rule': rule_def},
                error_message="Error creating security group rule")
        else:
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

            security_group_rule_dict = dict(security_group_rule=dict(
                parent_group_id=secgroup['id'],
                ip_protocol=protocol,
                from_port=port_range_min,
                to_port=port_range_max,
                cidr=remote_ip_prefix,
                group_id=remote_group_id
            ))
            if project_id is not None:
                security_group_rule_dict[
                    'security_group_rule']['tenant_id'] = project_id
            data = _adapter._json_response(
                self.compute.post(
                    '/os-security-group-rules',
                    json=security_group_rule_dict
                ))
        return self._normalize_secgroup_rule(
            self._get_and_munchify('security_group_rule', data))

    def delete_security_group_rule(self, rule_id):
        """Delete a security group rule

        :param string rule_id: The unique ID of the security group rule.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudUnavailableFeature if security groups are
                 not supported on this cloud.
        """
        # Security groups not supported
        if not self._has_secgroups():
            raise OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        if self._use_neutron_secgroups():
            try:
                self._network_client.delete(
                    '/security-group-rules/{sg_id}.json'.format(sg_id=rule_id),
                    error_message="Error deleting security group rule "
                                  "{0}".format(rule_id))
            except OpenStackCloudResourceNotFound:
                return False
            return True

        else:
            _adapter._json_response(self.compute.delete(
                '/os-security-group-rules/{id}'.format(id=rule_id)))
            return True

    def list_zones(self):
        """List all available zones.

        :returns: A list of zones dicts.

        """
        data = self._dns_client.get(
            "/zones",
            error_message="Error fetching zones list")
        return self._get_and_munchify('zones', data)

    def get_zone(self, name_or_id, filters=None):
        """Get a zone by name or ID.

        :param name_or_id: Name or ID of the zone
        :param filters:
            A dictionary of meta data to use for further filtering
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns:  A zone dict or None if no matching zone is found.

        """
        return _utils._get_entity(self, 'zone', name_or_id, filters)

    def search_zones(self, name_or_id=None, filters=None):
        zones = self.list_zones()
        return _utils._filter_list(zones, name_or_id, filters)

    def create_zone(self, name, zone_type=None, email=None, description=None,
                    ttl=None, masters=None):
        """Create a new zone.

        :param name: Name of the zone being created.
        :param zone_type: Type of the zone (primary/secondary)
        :param email: Email of the zone owner (only
                      applies if zone_type is primary)
        :param description: Description of the zone
        :param ttl: TTL (Time to live) value in seconds
        :param masters: Master nameservers (only applies
                        if zone_type is secondary)

        :returns: a dict representing the created zone.

        :raises: OpenStackCloudException on operation error.
        """

        # We capitalize in case the user passes time in lowercase, as
        # designate call expects PRIMARY/SECONDARY
        if zone_type is not None:
            zone_type = zone_type.upper()
            if zone_type not in ('PRIMARY', 'SECONDARY'):
                raise OpenStackCloudException(
                    "Invalid type %s, valid choices are PRIMARY or SECONDARY" %
                    zone_type)

        zone = {
            "name": name,
            "email": email,
            "description": description,
        }
        if ttl is not None:
            zone["ttl"] = ttl

        if zone_type is not None:
            zone["type"] = zone_type

        if masters is not None:
            zone["masters"] = masters

        data = self._dns_client.post(
            "/zones", json=zone,
            error_message="Unable to create zone {name}".format(name=name))
        return self._get_and_munchify(key=None, data=data)

    @_utils.valid_kwargs('email', 'description', 'ttl', 'masters')
    def update_zone(self, name_or_id, **kwargs):
        """Update a zone.

        :param name_or_id: Name or ID of the zone being updated.
        :param email: Email of the zone owner (only
                      applies if zone_type is primary)
        :param description: Description of the zone
        :param ttl: TTL (Time to live) value in seconds
        :param masters: Master nameservers (only applies
                        if zone_type is secondary)

        :returns: a dict representing the updated zone.

        :raises: OpenStackCloudException on operation error.
        """
        zone = self.get_zone(name_or_id)
        if not zone:
            raise OpenStackCloudException(
                "Zone %s not found." % name_or_id)

        data = self._dns_client.patch(
            "/zones/{zone_id}".format(zone_id=zone['id']), json=kwargs,
            error_message="Error updating zone {0}".format(name_or_id))
        return self._get_and_munchify(key=None, data=data)

    def delete_zone(self, name_or_id):
        """Delete a zone.

        :param name_or_id: Name or ID of the zone being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """

        zone = self.get_zone(name_or_id)
        if zone is None:
            self.log.debug("Zone %s not found for deleting", name_or_id)
            return False

        return self._dns_client.delete(
            "/zones/{zone_id}".format(zone_id=zone['id']),
            error_message="Error deleting zone {0}".format(name_or_id))

        return True

    def list_recordsets(self, zone):
        """List all available recordsets.

        :param zone: Name or ID of the zone managing the recordset

        :returns: A list of recordsets.

        """
        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            raise OpenStackCloudException(
                "Zone %s not found." % zone)
        return self._dns_client.get(
            "/zones/{zone_id}/recordsets".format(zone_id=zone_obj['id']),
            error_message="Error fetching recordsets list")

    def get_recordset(self, zone, name_or_id):
        """Get a recordset by name or ID.

        :param zone: Name or ID of the zone managing the recordset
        :param name_or_id: Name or ID of the recordset

        :returns:  A recordset dict or None if no matching recordset is
            found.

        """
        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            raise OpenStackCloudException(
                "Zone %s not found." % zone)
        try:
            return self._dns_client.get(
                "/zones/{zone_id}/recordsets/{recordset_id}".format(
                    zone_id=zone_obj['id'], recordset_id=name_or_id),
                error_message="Error fetching recordset")
        except Exception:
            return None

    def search_recordsets(self, zone, name_or_id=None, filters=None):
        recordsets = self.list_recordsets(zone=zone)
        return _utils._filter_list(recordsets, name_or_id, filters)

    def create_recordset(self, zone, name, recordset_type, records,
                         description=None, ttl=None):
        """Create a recordset.

        :param zone: Name or ID of the zone managing the recordset
        :param name: Name of the recordset
        :param recordset_type: Type of the recordset
        :param records: List of the recordset definitions
        :param description: Description of the recordset
        :param ttl: TTL value of the recordset

        :returns: a dict representing the created recordset.

        :raises: OpenStackCloudException on operation error.

        """
        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            raise OpenStackCloudException(
                "Zone %s not found." % zone)

        # We capitalize the type in case the user sends in lowercase
        recordset_type = recordset_type.upper()

        body = {
            'name': name,
            'type': recordset_type,
            'records': records
        }

        if description:
            body['description'] = description

        if ttl:
            body['ttl'] = ttl

        return self._dns_client.post(
            "/zones/{zone_id}/recordsets".format(zone_id=zone_obj['id']),
            json=body,
            error_message="Error creating recordset {name}".format(name=name))

    @_utils.valid_kwargs('description', 'ttl', 'records')
    def update_recordset(self, zone, name_or_id, **kwargs):
        """Update a recordset.

        :param zone: Name or ID of the zone managing the recordset
        :param name_or_id: Name or ID of the recordset being updated.
        :param records: List of the recordset definitions
        :param description: Description of the recordset
        :param ttl: TTL (Time to live) value in seconds of the recordset

        :returns: a dict representing the updated recordset.

        :raises: OpenStackCloudException on operation error.
        """
        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            raise OpenStackCloudException(
                "Zone %s not found." % zone)

        recordset_obj = self.get_recordset(zone, name_or_id)
        if recordset_obj is None:
            raise OpenStackCloudException(
                "Recordset %s not found." % name_or_id)

        new_recordset = self._dns_client.put(
            "/zones/{zone_id}/recordsets/{recordset_id}".format(
                zone_id=zone_obj['id'], recordset_id=name_or_id), json=kwargs,
            error_message="Error updating recordset {0}".format(name_or_id))

        return new_recordset

    def delete_recordset(self, zone, name_or_id):
        """Delete a recordset.

        :param zone: Name or ID of the zone managing the recordset.
        :param name_or_id: Name or ID of the recordset being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """

        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            self.log.debug("Zone %s not found for deleting", zone)
            return False

        recordset = self.get_recordset(zone_obj['id'], name_or_id)
        if recordset is None:
            self.log.debug("Recordset %s not found for deleting", name_or_id)
            return False

        self._dns_client.delete(
            "/zones/{zone_id}/recordsets/{recordset_id}".format(
                zone_id=zone_obj['id'], recordset_id=name_or_id),
            error_message="Error deleting recordset {0}".format(name_or_id))

        return True

    @_utils.cache_on_arguments()
    def list_cluster_templates(self, detail=False):
        """List cluster templates.

        :param bool detail. Ignored. Included for backwards compat.
            ClusterTemplates are always returned with full details.

        :returns: a list of dicts containing the cluster template details.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        with _utils.shade_exceptions("Error fetching cluster template list"):
            data = self._container_infra_client.get(
                '/baymodels/detail')
        return self._normalize_cluster_templates(
            self._get_and_munchify('baymodels', data))
    list_baymodels = list_cluster_templates

    def search_cluster_templates(
            self, name_or_id=None, filters=None, detail=False):
        """Search cluster templates.

        :param name_or_id: cluster template name or ID.
        :param filters: a dict containing additional filters to use.
        :param detail: a boolean to control if we need summarized or
            detailed output.

        :returns: a list of dict containing the cluster templates

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        cluster_templates = self.list_cluster_templates(detail=detail)
        return _utils._filter_list(
            cluster_templates, name_or_id, filters)
    search_baymodels = search_cluster_templates

    def get_cluster_template(self, name_or_id, filters=None, detail=False):
        """Get a cluster template by name or ID.

        :param name_or_id: Name or ID of the cluster template.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A cluster template dict or None if no matching
            cluster template is found.
        """
        return _utils._get_entity(self, 'cluster_template', name_or_id,
                                  filters=filters, detail=detail)
    get_baymodel = get_cluster_template

    def create_cluster_template(
            self, name, image_id=None, keypair_id=None, coe=None, **kwargs):
        """Create a cluster template.

        :param string name: Name of the cluster template.
        :param string image_id: Name or ID of the image to use.
        :param string keypair_id: Name or ID of the keypair to use.
        :param string coe: Name of the coe for the cluster template.

        Other arguments will be passed in kwargs.

        :returns: a dict containing the cluster template description

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        error_message = ("Error creating cluster template of name"
                         " {cluster_template_name}".format(
                             cluster_template_name=name))
        with _utils.shade_exceptions(error_message):
            body = kwargs.copy()
            body['name'] = name
            body['image_id'] = image_id
            body['keypair_id'] = keypair_id
            body['coe'] = coe

            cluster_template = self._container_infra_client.post(
                '/baymodels', json=body)

        self.list_cluster_templates.invalidate(self)
        return cluster_template
    create_baymodel = create_cluster_template

    def delete_cluster_template(self, name_or_id):
        """Delete a cluster template.

        :param name_or_id: Name or unique ID of the cluster template.
        :returns: True if the delete succeeded, False if the
            cluster template was not found.

        :raises: OpenStackCloudException on operation error.
        """

        cluster_template = self.get_cluster_template(name_or_id)

        if not cluster_template:
            self.log.debug(
                "Cluster template %(name_or_id)s does not exist",
                {'name_or_id': name_or_id},
                exc_info=True)
            return False

        with _utils.shade_exceptions("Error in deleting cluster template"):
            self._container_infra_client.delete(
                '/baymodels/{id}'.format(id=cluster_template['id']))
            self.list_cluster_templates.invalidate(self)

        return True
    delete_baymodel = delete_cluster_template

    @_utils.valid_kwargs('name', 'image_id', 'flavor_id', 'master_flavor_id',
                         'keypair_id', 'external_network_id', 'fixed_network',
                         'dns_nameserver', 'docker_volume_size', 'labels',
                         'coe', 'http_proxy', 'https_proxy', 'no_proxy',
                         'network_driver', 'tls_disabled', 'public',
                         'registry_enabled', 'volume_driver')
    def update_cluster_template(self, name_or_id, operation, **kwargs):
        """Update a cluster template.

        :param name_or_id: Name or ID of the cluster template being updated.
        :param operation: Operation to perform - add, remove, replace.

        Other arguments will be passed with kwargs.

        :returns: a dict representing the updated cluster template.

        :raises: OpenStackCloudException on operation error.
        """
        self.list_cluster_templates.invalidate(self)
        cluster_template = self.get_cluster_template(name_or_id)
        if not cluster_template:
            raise OpenStackCloudException(
                "Cluster template %s not found." % name_or_id)

        if operation not in ['add', 'replace', 'remove']:
            raise TypeError(
                "%s operation not in 'add', 'replace', 'remove'" % operation)

        patches = _utils.generate_patches_from_kwargs(operation, **kwargs)
        # No need to fire an API call if there is an empty patch
        if not patches:
            return cluster_template

        with _utils.shade_exceptions(
                "Error updating cluster template {0}".format(name_or_id)):
            self._container_infra_client.patch(
                '/baymodels/{id}'.format(id=cluster_template['id']),
                json=patches)

        new_cluster_template = self.get_cluster_template(name_or_id)
        return new_cluster_template
    update_baymodel = update_cluster_template

    def list_nics(self):
        msg = "Error fetching machine port list"
        data = self._baremetal_client.get("/ports",
                                          microversion="1.6",
                                          error_message=msg)
        return data['ports']

    def list_nics_for_machine(self, uuid):
        """Returns a list of ports present on the machine node.

        :param uuid: String representing machine UUID value in
                     order to identify the machine.
        :returns: A list of ports.
        """
        msg = "Error fetching port list for node {node_id}".format(
            node_id=uuid)
        url = "/nodes/{node_id}/ports".format(node_id=uuid)
        data = self._baremetal_client.get(url,
                                          microversion="1.6",
                                          error_message=msg)
        return data['ports']

    def get_nic_by_mac(self, mac):
        try:
            url = '/ports/detail?address=%s' % mac
            data = self._baremetal_client.get(url)
            if len(data['ports']) == 1:
                return data['ports'][0]
        except Exception:
            pass
        return None

    def list_machines(self):
        msg = "Error fetching machine node list"
        data = self._baremetal_client.get("/nodes",
                                          microversion="1.6",
                                          error_message=msg)
        return self._get_and_munchify('nodes', data)

    def get_machine(self, name_or_id):
        """Get Machine by name or uuid

        Search the baremetal host out by utilizing the supplied id value
        which can consist of a name or UUID.

        :param name_or_id: A node name or UUID that will be looked up.

        :returns: ``munch.Munch`` representing the node found or None if no
                  nodes are found.
        """
        # NOTE(TheJulia): This is the initial microversion shade support for
        # ironic was created around. Ironic's default behavior for newer
        # versions is to expose the field, but with a value of None for
        # calls by a supported, yet older microversion.
        # Consensus for moving forward with microversion handling in shade
        # seems to be to take the same approach, although ironic's API
        # does it for the user.
        version = "1.6"
        try:
            url = '/nodes/{node_id}'.format(node_id=name_or_id)
            return self._normalize_machine(
                self._baremetal_client.get(url, microversion=version))
        except Exception:
            return None

    def get_machine_by_mac(self, mac):
        """Get machine by port MAC address

        :param mac: Port MAC address to query in order to return a node.

        :returns: ``munch.Munch`` representing the node found or None
                  if the node is not found.
        """
        try:
            port_url = '/ports/detail?address={mac}'.format(mac=mac)
            port = self._baremetal_client.get(port_url, microversion=1.6)
            machine_url = '/nodes/{machine}'.format(
                machine=port['ports'][0]['node_uuid'])
            return self._baremetal_client.get(machine_url, microversion=1.6)
        except Exception:
            return None

    def inspect_machine(self, name_or_id, wait=False, timeout=3600):
        """Inspect a Barmetal machine

        Engages the Ironic node inspection behavior in order to collect
        metadata about the baremetal machine.

        :param name_or_id: String representing machine name or UUID value in
                           order to identify the machine.

        :param wait: Boolean value controlling if the method is to wait for
                     the desired state to be reached or a failure to occur.

        :param timeout: Integer value, defautling to 3600 seconds, for the$
                        wait state to reach completion.

        :returns: ``munch.Munch`` representing the current state of the machine
                  upon exit of the method.
        """

        return_to_available = False

        machine = self.get_machine(name_or_id)
        if not machine:
            raise OpenStackCloudException(
                "Machine inspection failed to find: %s." % name_or_id)

        # NOTE(TheJulia): If in available state, we can do this, however
        # We need to to move the host back to m
        if "available" in machine['provision_state']:
            return_to_available = True
            # NOTE(TheJulia): Changing available machine to managedable state
            # and due to state transitions we need to until that transition has
            # completd.
            self.node_set_provision_state(machine['uuid'], 'manage',
                                          wait=True, timeout=timeout)
        elif ("manage" not in machine['provision_state'] and
                "inspect failed" not in machine['provision_state']):
            raise OpenStackCloudException(
                "Machine must be in 'manage' or 'available' state to "
                "engage inspection: Machine: %s State: %s"
                % (machine['uuid'], machine['provision_state']))
        with _utils.shade_exceptions("Error inspecting machine"):
            machine = self.node_set_provision_state(machine['uuid'], 'inspect')
            if wait:
                for count in utils.iterate_timeout(
                        timeout,
                        "Timeout waiting for node transition to "
                        "target state of 'inspect'"):
                    machine = self.get_machine(name_or_id)

                    if "inspect failed" in machine['provision_state']:
                        raise OpenStackCloudException(
                            "Inspection of node %s failed, last error: %s"
                            % (machine['uuid'], machine['last_error']))

                    if "manageable" in machine['provision_state']:
                        break

            if return_to_available:
                machine = self.node_set_provision_state(
                    machine['uuid'], 'provide', wait=wait, timeout=timeout)

            return(machine)

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

        :param nics:
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

        :returns: Returns a ``munch.Munch`` representing the new
                  baremetal node.
        """

        msg = ("Baremetal machine node failed to be created.")
        port_msg = ("Baremetal machine port failed to be created.")

        url = '/nodes'
        # TODO(TheJulia): At some point we need to figure out how to
        # handle data across when the requestor is defining newer items
        # with the older api.
        machine = self._baremetal_client.post(url,
                                              json=kwargs,
                                              error_message=msg,
                                              microversion="1.6")

        created_nics = []
        try:
            for row in nics:
                payload = {'address': row['mac'],
                           'node_uuid': machine['uuid']}
                nic = self._baremetal_client.post('/ports',
                                                  json=payload,
                                                  error_message=port_msg)
                created_nics.append(nic['uuid'])

        except Exception as e:
            self.log.debug("ironic NIC registration failed", exc_info=True)
            # TODO(mordred) Handle failures here
            try:
                for uuid in created_nics:
                    try:
                        port_url = '/ports/{uuid}'.format(uuid=uuid)
                        # NOTE(TheJulia): Added in hope that it is logged.
                        port_msg = ('Failed to delete port {port} for node'
                                    '{node}').format(port=uuid,
                                                     node=machine['uuid'])
                        self._baremetal_client.delete(port_url,
                                                      error_message=port_msg)
                    except Exception:
                        pass
            finally:
                version = "1.6"
                msg = "Baremetal machine failed to be deleted."
                url = '/nodes/{node_id}'.format(
                    node_id=machine['uuid'])
                self._baremetal_client.delete(url,
                                              error_message=msg,
                                              microversion=version)
            raise OpenStackCloudException(
                "Error registering NICs with the baremetal service: %s"
                % str(e))

        with _utils.shade_exceptions(
                "Error transitioning node to available state"):
            if wait:
                for count in utils.iterate_timeout(
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
                    for count in utils.iterate_timeout(
                            lock_timeout,
                            "Timeout waiting for reservation to clear "
                            "before setting provide state"):
                        machine = self.get_machine(machine['uuid'])
                        if (machine['reservation'] is None and
                           machine['provision_state'] is not 'enroll'):
                            # NOTE(TheJulia): In this case, the node has
                            # has moved on from the previous state and is
                            # likely not being verified, as no lock is
                            # present on the node.
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
        if not isinstance(machine, str):
            return self._normalize_machine(machine)
        else:
            return machine

    def unregister_machine(self, nics, uuid, wait=False, timeout=600):
        """Unregister Baremetal from Ironic

        Removes entries for Network Interfaces and baremetal nodes
        from an Ironic API

        :param nics: An array of strings that consist of MAC addresses
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

        # NOTE(TheJulia) There is a high possibility of a lock being present
        # if the machine was just moved through the state machine. This was
        # previously concealed by exception retry logic that detected the
        # failure, and resubitted the request in python-ironicclient.
        try:
            self.wait_for_baremetal_node_lock(machine, timeout=timeout)
        except OpenStackCloudException as e:
            raise OpenStackCloudException("Error unregistering node '%s': "
                                          "Exception occured while waiting "
                                          "to be able to proceed: %s"
                                          % (machine['uuid'], e))

        for nic in nics:
            port_msg = ("Error removing NIC {nic} from baremetal API for "
                        "node {uuid}").format(nic=nic, uuid=uuid)
            port_url = '/ports/detail?address={mac}'.format(mac=nic['mac'])
            port = self._baremetal_client.get(port_url, microversion=1.6,
                                              error_message=port_msg)
            port_url = '/ports/{uuid}'.format(uuid=port['ports'][0]['uuid'])
            _utils._call_client_and_retry(self._baremetal_client.delete,
                                          port_url, retry_on=[409, 503],
                                          error_message=port_msg)

        with _utils.shade_exceptions(
                "Error unregistering machine {node_id} from the baremetal "
                "API".format(node_id=uuid)):

            # NOTE(TheJulia): While this should not matter microversion wise,
            # ironic assumes all calls without an explicit microversion to be
            # version 1.0. Ironic expects to deprecate support for older
            # microversions in future releases, as such, we explicitly set
            # the version to what we have been using with the client library..
            version = "1.6"
            msg = "Baremetal machine failed to be deleted"
            url = '/nodes/{node_id}'.format(
                node_id=uuid)
            _utils._call_client_and_retry(self._baremetal_client.delete,
                                          url, retry_on=[409, 503],
                                          error_message=msg,
                                          microversion=version)

            if wait:
                for count in utils.iterate_timeout(
                        timeout,
                        "Timeout waiting for machine to be deleted"):
                    if not self.get_machine(uuid):
                        break

    def patch_machine(self, name_or_id, patch):
        """Patch Machine Information

        This method allows for an interface to manipulate node entries
        within Ironic.

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

        :returns: ``munch.Munch`` representing the newly updated node.
        """

        msg = ("Error updating machine via patch operation on node "
               "{node}".format(node=name_or_id))
        url = '/nodes/{node_id}'.format(node_id=name_or_id)
        return self._normalize_machine(
            self._baremetal_client.patch(url,
                                         json=patch,
                                         error_message=msg))

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

        :returns: ``munch.Munch`` containing a machine sub-dictonary consisting
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
                "Unexpected machine response missing key %s [%s]",
                e.args[0], name_or_id)
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

        with _utils.shade_exceptions(
            "Machine update failed - patch operation failed on Machine "
            "{node}".format(node=name_or_id)
        ):
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

    def validate_node(self, uuid):
        # TODO(TheJulia): There are soooooo many other interfaces
        # that we can support validating, while these are essential,
        # we should support more.
        # TODO(TheJulia): Add a doc string :(
        msg = ("Failed to query the API for validation status of "
               "node {node_id}").format(node_id=uuid)
        url = '/nodes/{node_id}/validate'.format(node_id=uuid)
        ifaces = self._baremetal_client.get(url, error_message=msg)

        if not ifaces['deploy'] or not ifaces['power']:
            raise OpenStackCloudException(
                "ironic node %s failed to validate. "
                "(deploy: %s, power: %s)" % (ifaces['deploy'],
                                             ifaces['power']))

    def node_set_provision_state(self,
                                 name_or_id,
                                 state,
                                 configdrive=None,
                                 wait=False,
                                 timeout=3600):
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
        :param boolean wait: A boolean value, defaulted to false, to control
                             if the method will wait for the desire end state
                             to be reached before returning.
        :param integer timeout: Integer value, defaulting to 3600 seconds,
                                representing the amount of time to wait for
                                the desire end state to be reached.

        :raises: OpenStackCloudException on operation error.

        :returns: ``munch.Munch`` representing the current state of the machine
                  upon exit of the method.
        """
        # NOTE(TheJulia): Default microversion for this call is 1.6.
        # Setting locally until we have determined our master plan regarding
        # microversion handling.
        version = "1.6"
        msg = ("Baremetal machine node failed change provision state to "
               "{state}".format(state=state))

        url = '/nodes/{node_id}/states/provision'.format(
            node_id=name_or_id)
        payload = {'target': state}
        if configdrive:
            payload['configdrive'] = configdrive

        machine = _utils._call_client_and_retry(self._baremetal_client.put,
                                                url,
                                                retry_on=[409, 503],
                                                json=payload,
                                                error_message=msg,
                                                microversion=version)
        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for node transition to "
                    "target state of '%s'" % state):
                machine = self.get_machine(name_or_id)
                if 'failed' in machine['provision_state']:
                    raise OpenStackCloudException(
                        "Machine encountered a failure.")
                # NOTE(TheJulia): This performs matching if the requested
                # end state matches the state the node has reached.
                if state in machine['provision_state']:
                    break
                # NOTE(TheJulia): This performs matching for cases where
                # the reqeusted state action ends in available state.
                if ("available" in machine['provision_state'] and
                        state in ["provide", "deleted"]):
                    break
        else:
            machine = self.get_machine(name_or_id)
        return machine

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
        msg = ("Error setting machine maintenance state to {state} on node "
               "{node}").format(state=state, node=name_or_id)
        url = '/nodes/{name_or_id}/maintenance'.format(name_or_id=name_or_id)
        if state:
            payload = {'reason': reason}
            self._baremetal_client.put(url,
                                       json=payload,
                                       error_message=msg)
        else:
            self._baremetal_client.delete(url, error_message=msg)
        return None

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
        msg = ("Error setting machine power state to {state} on node "
               "{node}").format(state=state, node=name_or_id)
        url = '/nodes/{name_or_id}/states/power'.format(name_or_id=name_or_id)
        if 'reboot' in state:
            desired_state = 'rebooting'
        else:
            desired_state = 'power {state}'.format(state=state)
        payload = {'target': desired_state}
        _utils._call_client_and_retry(self._baremetal_client.put,
                                      url,
                                      retry_on=[409, 503],
                                      json=payload,
                                      error_message=msg,
                                      microversion="1.6")
        return None

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

    def activate_node(self, uuid, configdrive=None,
                      wait=False, timeout=1200):
        self.node_set_provision_state(
            uuid, 'active', configdrive, wait=wait, timeout=timeout)

    def deactivate_node(self, uuid, wait=False,
                        timeout=1200):
        self.node_set_provision_state(
            uuid, 'deleted', wait=wait, timeout=timeout)

    def set_node_instance_info(self, uuid, patch):
        msg = ("Error updating machine via patch operation on node "
               "{node}".format(node=uuid))
        url = '/nodes/{node_id}'.format(node_id=uuid)
        return self._baremetal_client.patch(url,
                                            json=patch,
                                            error_message=msg)

    def purge_node_instance_info(self, uuid):
        patch = []
        patch.append({'op': 'remove', 'path': '/instance_info'})
        msg = ("Error updating machine via patch operation on node "
               "{node}".format(node=uuid))
        url = '/nodes/{node_id}'.format(node_id=uuid)
        return self._baremetal_client.patch(url,
                                            json=patch,
                                            error_message=msg)

    def wait_for_baremetal_node_lock(self, node, timeout=30):
        """Wait for a baremetal node to have no lock.

        Baremetal nodes in ironic have a reservation lock that
        is used to represent that a conductor has locked the node
        while performing some sort of action, such as changing
        configuration as a result of a machine state change.

        This lock can occur during power syncronization, and prevents
        updates to objects attached to the node, such as ports.

        In the vast majority of cases, locks should clear in a few
        seconds, and as such this method will only wait for 30 seconds.
        The default wait is two seconds between checking if the lock
        has cleared.

        This method is intended for use by methods that need to
        gracefully block without genreating errors, however this
        method does prevent another client or a timer from
        triggering a lock immediately after we see the lock as
        having cleared.

        :param node: The json representation of the node,
                     specificially looking for the node
                     'uuid' and 'reservation' fields.
        :param timeout: Integer in seconds to wait for the
                        lock to clear. Default: 30

        :raises: OpenStackCloudException upon client failure.
        :returns: None
        """
        # TODO(TheJulia): This _can_ still fail with a race
        # condition in that between us checking the status,
        # a conductor where the conductor could still obtain
        # a lock before we are able to obtain a lock.
        # This means we should handle this with such conections

        if node['reservation'] is None:
            return
        else:
            msg = 'Waiting for lock to be released for node {node}'.format(
                node=node['uuid'])
            for count in utils.iterate_timeout(timeout, msg, 2):
                current_node = self.get_machine(node['uuid'])
                if current_node['reservation'] is None:
                    return

    @_utils.valid_kwargs('type', 'service_type', 'description')
    def create_service(self, name, enabled=True, **kwargs):
        """Create a service.

        :param name: Service name.
        :param type: Service type. (type or service_type required.)
        :param service_type: Service type. (type or service_type required.)
        :param description: Service description (optional).
        :param enabled: Whether the service is enabled (v3 only)

        :returns: a ``munch.Munch`` containing the services description,
            i.e. the following attributes::
            - id: <service id>
            - name: <service name>
            - type: <service type>
            - service_type: <service type>
            - description: <service description>

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.

        """
        type_ = kwargs.pop('type', None)
        service_type = kwargs.pop('service_type', None)

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        if self._is_client_version('identity', 2):
            url, key = '/OS-KSADM/services', 'OS-KSADM:service'
            kwargs['type'] = type_ or service_type
        else:
            url, key = '/services', 'service'
            kwargs['type'] = type_ or service_type
            kwargs['enabled'] = enabled
        kwargs['name'] = name

        msg = 'Failed to create service {name}'.format(name=name)
        data = self._identity_client.post(
            url, json={key: kwargs}, error_message=msg)
        service = self._get_and_munchify(key, data)
        return _utils.normalize_keystone_services([service])[0]

    @_utils.valid_kwargs('name', 'enabled', 'type', 'service_type',
                         'description')
    def update_service(self, name_or_id, **kwargs):
        # NOTE(SamYaple): Service updates are only available on v3 api
        if self._is_client_version('identity', 2):
            raise OpenStackCloudUnavailableFeature(
                'Unavailable Feature: Service update requires Identity v3'
            )

        # NOTE(SamYaple): Keystone v3 only accepts 'type' but shade accepts
        #                 both 'type' and 'service_type' with a preference
        #                 towards 'type'
        type_ = kwargs.pop('type', None)
        service_type = kwargs.pop('service_type', None)
        if type_ or service_type:
            kwargs['type'] = type_ or service_type

        if self._is_client_version('identity', 2):
            url, key = '/OS-KSADM/services', 'OS-KSADM:service'
        else:
            url, key = '/services', 'service'

        service = self.get_service(name_or_id)
        msg = 'Error in updating service {service}'.format(service=name_or_id)
        data = self._identity_client.patch(
            '{url}/{id}'.format(url=url, id=service['id']), json={key: kwargs},
            endpoint_filter={'interface': 'admin'}, error_message=msg)
        service = self._get_and_munchify(key, data)
        return _utils.normalize_keystone_services([service])[0]

    def list_services(self):
        """List all Keystone services.

        :returns: a list of ``munch.Munch`` containing the services description

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.
        """
        if self._is_client_version('identity', 2):
            url, key = '/OS-KSADM/services', 'OS-KSADM:services'
        else:
            url, key = '/services', 'services'
        data = self._identity_client.get(
            url, endpoint_filter={'interface': 'admin'},
            error_message="Failed to list services")
        services = self._get_and_munchify(key, data)
        return _utils.normalize_keystone_services(services)

    def search_services(self, name_or_id=None, filters=None):
        """Search Keystone services.

        :param name_or_id: Name or id of the desired service.
        :param filters: a dict containing additional filters to use. e.g.
                        {'type': 'network'}.

        :returns: a list of ``munch.Munch`` containing the services description

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call.
        """
        services = self.list_services()
        return _utils._filter_list(services, name_or_id, filters)

    def get_service(self, name_or_id, filters=None):
        """Get exactly one Keystone service.

        :param name_or_id: Name or id of the desired service.
        :param filters: a dict containing additional filters to use. e.g.
                {'type': 'network'}

        :returns: a ``munch.Munch`` containing the services description,
            i.e. the following attributes::
            - id: <service id>
            - name: <service name>
            - type: <service type>
            - description: <service description>

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            openstack API call or if multiple matches are found.
        """
        return _utils._get_entity(self, 'service', name_or_id, filters)

    def delete_service(self, name_or_id):
        """Delete a Keystone service.

        :param name_or_id: Service name or id.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call
        """
        service = self.get_service(name_or_id=name_or_id)
        if service is None:
            self.log.debug("Service %s not found for deleting", name_or_id)
            return False

        if self._is_client_version('identity', 2):
            url = '/OS-KSADM/services'
        else:
            url = '/services'

        error_msg = 'Failed to delete service {id}'.format(id=service['id'])
        self._identity_client.delete(
            '{url}/{id}'.format(url=url, id=service['id']),
            endpoint_filter={'interface': 'admin'}, error_message=error_msg)

        return True

    @_utils.valid_kwargs('public_url', 'internal_url', 'admin_url')
    def create_endpoint(self, service_name_or_id, url=None, interface=None,
                        region=None, enabled=True, **kwargs):
        """Create a Keystone endpoint.

        :param service_name_or_id: Service name or id for this endpoint.
        :param url: URL of the endpoint
        :param interface: Interface type of the endpoint
        :param public_url: Endpoint public URL.
        :param internal_url: Endpoint internal URL.
        :param admin_url: Endpoint admin URL.
        :param region: Endpoint region.
        :param enabled: Whether the endpoint is enabled

        NOTE: Both v2 (public_url, internal_url, admin_url) and v3
              (url, interface) calling semantics are supported. But
              you can only use one of them at a time.

        :returns: a list of ``munch.Munch`` containing the endpoint description

        :raises: OpenStackCloudException if the service cannot be found or if
            something goes wrong during the openstack API call.
        """
        public_url = kwargs.pop('public_url', None)
        internal_url = kwargs.pop('internal_url', None)
        admin_url = kwargs.pop('admin_url', None)

        if (url or interface) and (public_url or internal_url or admin_url):
            raise OpenStackCloudException(
                "create_endpoint takes either url and interface OR"
                " public_url, internal_url, admin_url")

        service = self.get_service(name_or_id=service_name_or_id)
        if service is None:
            raise OpenStackCloudException("service {service} not found".format(
                service=service_name_or_id))

        if self._is_client_version('identity', 2):
            if url:
                # v2.0 in use, v3-like arguments, one endpoint created
                if interface != 'public':
                    raise OpenStackCloudException(
                        "Error adding endpoint for service {service}."
                        " On a v2 cloud the url/interface API may only be"
                        " used for public url. Try using the public_url,"
                        " internal_url, admin_url parameters instead of"
                        " url and interface".format(
                            service=service_name_or_id))
                endpoint_args = {'publicurl': url}
            else:
                # v2.0 in use, v2.0-like arguments, one endpoint created
                endpoint_args = {}
                if public_url:
                    endpoint_args.update({'publicurl': public_url})
                if internal_url:
                    endpoint_args.update({'internalurl': internal_url})
                if admin_url:
                    endpoint_args.update({'adminurl': admin_url})

            # keystone v2.0 requires 'region' arg even if it is None
            endpoint_args.update(
                {'service_id': service['id'], 'region': region})

            data = self._identity_client.post(
                '/endpoints', json={'endpoint': endpoint_args},
                endpoint_filter={'interface': 'admin'},
                error_message=("Failed to create endpoint for service"
                               " {service}".format(service=service['name'])))
            return [self._get_and_munchify('endpoint', data)]
        else:
            endpoints_args = []
            if url:
                # v3 in use, v3-like arguments, one endpoint created
                endpoints_args.append(
                    {'url': url, 'interface': interface,
                     'service_id': service['id'], 'enabled': enabled,
                     'region': region})
            else:
                # v3 in use, v2.0-like arguments, one endpoint created for each
                # interface url provided
                endpoint_args = {'region': region, 'enabled': enabled,
                                 'service_id': service['id']}
                if public_url:
                    endpoint_args.update({'url': public_url,
                                          'interface': 'public'})
                    endpoints_args.append(endpoint_args.copy())
                if internal_url:
                    endpoint_args.update({'url': internal_url,
                                          'interface': 'internal'})
                    endpoints_args.append(endpoint_args.copy())
                if admin_url:
                    endpoint_args.update({'url': admin_url,
                                          'interface': 'admin'})
                    endpoints_args.append(endpoint_args.copy())

            endpoints = []
            error_msg = ("Failed to create endpoint for service"
                         " {service}".format(service=service['name']))
            for args in endpoints_args:
                data = self._identity_client.post(
                    '/endpoints', json={'endpoint': args},
                    error_message=error_msg)
                endpoints.append(self._get_and_munchify('endpoint', data))
            return endpoints

    @_utils.valid_kwargs('enabled', 'service_name_or_id', 'url', 'interface',
                         'region')
    def update_endpoint(self, endpoint_id, **kwargs):
        # NOTE(SamYaple): Endpoint updates are only available on v3 api
        if self._is_client_version('identity', 2):
            raise OpenStackCloudUnavailableFeature(
                'Unavailable Feature: Endpoint update'
            )

        service_name_or_id = kwargs.pop('service_name_or_id', None)
        if service_name_or_id is not None:
            kwargs['service_id'] = service_name_or_id

        data = self._identity_client.patch(
            '/endpoints/{}'.format(endpoint_id), json={'endpoint': kwargs},
            error_message="Failed to update endpoint {}".format(endpoint_id))
        return self._get_and_munchify('endpoint', data)

    def list_endpoints(self):
        """List Keystone endpoints.

        :returns: a list of ``munch.Munch`` containing the endpoint description

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        # Force admin interface if v2.0 is in use
        v2 = self._is_client_version('identity', 2)
        kwargs = {'endpoint_filter': {'interface': 'admin'}} if v2 else {}

        data = self._identity_client.get(
            '/endpoints', error_message="Failed to list endpoints", **kwargs)
        endpoints = self._get_and_munchify('endpoints', data)

        return endpoints

    def search_endpoints(self, id=None, filters=None):
        """List Keystone endpoints.

        :param id: endpoint id.
        :param filters: a dict containing additional filters to use. e.g.
                {'region': 'region-a.geo-1'}

        :returns: a list of ``munch.Munch`` containing the endpoint
            description. Each dict contains the following attributes::
            - id: <endpoint id>
            - region: <endpoint region>
            - public_url: <endpoint public url>
            - internal_url: <endpoint internal url> (optional)
            - admin_url: <endpoint admin url> (optional)

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        # NOTE(SamYaple): With keystone v3 we can filter directly via the
        # the keystone api, but since the return of all the endpoints even in
        # large environments is small, we can continue to filter in shade just
        # like the v2 api.
        endpoints = self.list_endpoints()
        return _utils._filter_list(endpoints, id, filters)

    def get_endpoint(self, id, filters=None):
        """Get exactly one Keystone endpoint.

        :param id: endpoint id.
        :param filters: a dict containing additional filters to use. e.g.
                {'region': 'region-a.geo-1'}

        :returns: a ``munch.Munch`` containing the endpoint description.
            i.e. a ``munch.Munch`` containing the following attributes::
            - id: <endpoint id>
            - region: <endpoint region>
            - public_url: <endpoint public url>
            - internal_url: <endpoint internal url> (optional)
            - admin_url: <endpoint admin url> (optional)
        """
        return _utils._get_entity(self, 'endpoint', id, filters)

    def delete_endpoint(self, id):
        """Delete a Keystone endpoint.

        :param id: Id of the endpoint to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call.
        """
        endpoint = self.get_endpoint(id=id)
        if endpoint is None:
            self.log.debug("Endpoint %s not found for deleting", id)
            return False

        # Force admin interface if v2.0 is in use
        v2 = self._is_client_version('identity', 2)
        kwargs = {'endpoint_filter': {'interface': 'admin'}} if v2 else {}

        error_msg = "Failed to delete endpoint {id}".format(id=id)
        self._identity_client.delete('/endpoints/{id}'.format(id=id),
                                     error_message=error_msg, **kwargs)

        return True

    def create_domain(self, name, description=None, enabled=True):
        """Create a domain.

        :param name: The name of the domain.
        :param description: A description of the domain.
        :param enabled: Is the domain enabled or not (default True).

        :returns: a ``munch.Munch`` containing the domain representation.

        :raise OpenStackCloudException: if the domain cannot be created.
        """
        domain_ref = {'name': name, 'enabled': enabled}
        if description is not None:
            domain_ref['description'] = description
        msg = 'Failed to create domain {name}'.format(name=name)
        data = self._identity_client.post(
            '/domains', json={'domain': domain_ref}, error_message=msg)
        domain = self._get_and_munchify('domain', data)
        return _utils.normalize_domains([domain])[0]

    def update_domain(
            self, domain_id=None, name=None, description=None,
            enabled=None, name_or_id=None):
        if domain_id is None:
            if name_or_id is None:
                raise OpenStackCloudException(
                    "You must pass either domain_id or name_or_id value"
                )
            dom = self.get_domain(None, name_or_id)
            if dom is None:
                raise OpenStackCloudException(
                    "Domain {0} not found for updating".format(name_or_id)
                )
            domain_id = dom['id']

        domain_ref = {}
        domain_ref.update({'name': name} if name else {})
        domain_ref.update({'description': description} if description else {})
        domain_ref.update({'enabled': enabled} if enabled is not None else {})

        error_msg = "Error in updating domain {id}".format(id=domain_id)
        data = self._identity_client.patch(
            '/domains/{id}'.format(id=domain_id),
            json={'domain': domain_ref}, error_message=error_msg)
        domain = self._get_and_munchify('domain', data)
        return _utils.normalize_domains([domain])[0]

    def delete_domain(self, domain_id=None, name_or_id=None):
        """Delete a domain.

        :param domain_id: ID of the domain to delete.
        :param name_or_id: Name or ID of the domain to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call.
        """
        if domain_id is None:
            if name_or_id is None:
                raise OpenStackCloudException(
                    "You must pass either domain_id or name_or_id value"
                )
            dom = self.get_domain(name_or_id=name_or_id)
            if dom is None:
                self.log.debug(
                    "Domain %s not found for deleting", name_or_id)
                return False
            domain_id = dom['id']

        # A domain must be disabled before deleting
        self.update_domain(domain_id, enabled=False)
        error_msg = "Failed to delete domain {id}".format(id=domain_id)
        self._identity_client.delete('/domains/{id}'.format(id=domain_id),
                                     error_message=error_msg)

        return True

    def list_domains(self, **filters):
        """List Keystone domains.

        :returns: a list of ``munch.Munch`` containing the domain description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        data = self._identity_client.get(
            '/domains', params=filters, error_message="Failed to list domains")
        domains = self._get_and_munchify('domains', data)
        return _utils.normalize_domains(domains)

    def search_domains(self, filters=None, name_or_id=None):
        """Search Keystone domains.

        :param name_or_id: domain name or id
        :param dict filters: A dict containing additional filters to use.
             Keys to search on are id, name, enabled and description.

        :returns: a list of ``munch.Munch`` containing the domain description.
            Each ``munch.Munch`` contains the following attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        if filters is None:
            filters = {}
        if name_or_id is not None:
            domains = self.list_domains()
            return _utils._filter_list(domains, name_or_id, filters)
        else:
            return self.list_domains(**filters)

    def get_domain(self, domain_id=None, name_or_id=None, filters=None):
        """Get exactly one Keystone domain.

        :param domain_id: domain id.
        :param name_or_id: domain name or id.
        :param dict filters: A dict containing additional filters to use.
             Keys to search on are id, name, enabled and description.

        :returns: a ``munch.Munch`` containing the domain description, or None
            if not found. Each ``munch.Munch`` contains the following
            attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        if domain_id is None:
            # NOTE(SamYaple): search_domains() has filters and name_or_id
            # in the wrong positional order which prevents _get_entity from
            # being able to return quickly if passing a domain object so we
            # duplicate that logic here
            if hasattr(name_or_id, 'id'):
                return name_or_id
            return _utils._get_entity(self, 'domain', filters, name_or_id)
        else:
            error_msg = 'Failed to get domain {id}'.format(id=domain_id)
            data = self._identity_client.get(
                '/domains/{id}'.format(id=domain_id),
                error_message=error_msg)
            domain = self._get_and_munchify('domain', data)
            return _utils.normalize_domains([domain])[0]

    @_utils.valid_kwargs('domain_id')
    @_utils.cache_on_arguments()
    def list_groups(self, **kwargs):
        """List Keystone Groups.

        :param domain_id: domain id.

        :returns: A list of ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        data = self._identity_client.get(
            '/groups', params=kwargs, error_message="Failed to list groups")
        return _utils.normalize_groups(self._get_and_munchify('groups', data))

    @_utils.valid_kwargs('domain_id')
    def search_groups(self, name_or_id=None, filters=None, **kwargs):
        """Search Keystone groups.

        :param name: Group name or id.
        :param filters: A dict containing additional filters to use.
        :param domain_id: domain id.

        :returns: A list of ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        groups = self.list_groups(**kwargs)
        return _utils._filter_list(groups, name_or_id, filters)

    @_utils.valid_kwargs('domain_id')
    def get_group(self, name_or_id, filters=None, **kwargs):
        """Get exactly one Keystone group.

        :param id: Group name or id.
        :param filters: A dict containing additional filters to use.
        :param domain_id: domain id.

        :returns: A ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        return _utils._get_entity(self, 'group', name_or_id, filters, **kwargs)

    def create_group(self, name, description, domain=None):
        """Create a group.

        :param string name: Group name.
        :param string description: Group description.
        :param string domain: Domain name or ID for the group.

        :returns: A ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        group_ref = {'name': name}
        if description:
            group_ref['description'] = description
        if domain:
            dom = self.get_domain(domain)
            if not dom:
                raise OpenStackCloudException(
                    "Creating group {group} failed: Invalid domain "
                    "{domain}".format(group=name, domain=domain)
                )
            group_ref['domain_id'] = dom['id']

        error_msg = "Error creating group {group}".format(group=name)
        data = self._identity_client.post(
            '/groups', json={'group': group_ref}, error_message=error_msg)
        group = self._get_and_munchify('group', data)
        self.list_groups.invalidate(self)
        return _utils.normalize_groups([group])[0]

    @_utils.valid_kwargs('domain_id')
    def update_group(self, name_or_id, name=None, description=None,
                     **kwargs):
        """Update an existing group

        :param string name: New group name.
        :param string description: New group description.
        :param domain_id: domain id.

        :returns: A ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        self.list_groups.invalidate(self)
        group = self.get_group(name_or_id, **kwargs)
        if group is None:
            raise OpenStackCloudException(
                "Group {0} not found for updating".format(name_or_id)
            )

        group_ref = {}
        if name:
            group_ref['name'] = name
        if description:
            group_ref['description'] = description

        error_msg = "Unable to update group {name}".format(name=name_or_id)
        data = self._identity_client.patch(
            '/groups/{id}'.format(id=group['id']),
            json={'group': group_ref}, error_message=error_msg)
        group = self._get_and_munchify('group', data)
        self.list_groups.invalidate(self)
        return _utils.normalize_groups([group])[0]

    @_utils.valid_kwargs('domain_id')
    def delete_group(self, name_or_id, **kwargs):
        """Delete a group

        :param name_or_id: ID or name of the group to delete.
        :param domain_id: domain id.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        group = self.get_group(name_or_id, **kwargs)
        if group is None:
            self.log.debug(
                "Group %s not found for deleting", name_or_id)
            return False

        error_msg = "Unable to delete group {name}".format(name=name_or_id)
        self._identity_client.delete('/groups/{id}'.format(id=group['id']),
                                     error_message=error_msg)

        self.list_groups.invalidate(self)
        return True

    @_utils.valid_kwargs('domain_id')
    def list_roles(self, **kwargs):
        """List Keystone roles.

        :param domain_id: domain id for listing roles (v3)

        :returns: a list of ``munch.Munch`` containing the role description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        v2 = self._is_client_version('identity', 2)
        url = '/OS-KSADM/roles' if v2 else '/roles'
        data = self._identity_client.get(
            url, params=kwargs, error_message="Failed to list roles")
        return self._normalize_roles(self._get_and_munchify('roles', data))

    @_utils.valid_kwargs('domain_id')
    def search_roles(self, name_or_id=None, filters=None, **kwargs):
        """Seach Keystone roles.

        :param string name: role name or id.
        :param dict filters: a dict containing additional filters to use.
        :param domain_id: domain id (v3)

        :returns: a list of ``munch.Munch`` containing the role description.
            Each ``munch.Munch`` contains the following attributes::

                - id: <role id>
                - name: <role name>
                - description: <role description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        roles = self.list_roles(**kwargs)
        return _utils._filter_list(roles, name_or_id, filters)

    @_utils.valid_kwargs('domain_id')
    def get_role(self, name_or_id, filters=None, **kwargs):
        """Get exactly one Keystone role.

        :param id: role name or id.
        :param filters: a dict containing additional filters to use.
        :param domain_id: domain id (v3)

        :returns: a single ``munch.Munch`` containing the role description.
            Each ``munch.Munch`` contains the following attributes::

                - id: <role id>
                - name: <role name>
                - description: <role description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        return _utils._get_entity(self, 'role', name_or_id, filters, **kwargs)

    def _keystone_v2_role_assignments(self, user, project=None,
                                      role=None, **kwargs):
        data = self._identity_client.get(
            "/tenants/{tenant}/users/{user}/roles".format(
                tenant=project, user=user),
            error_message="Failed to list role assignments")

        roles = self._get_and_munchify('roles', data)

        ret = []
        for tmprole in roles:
            if role is not None and role != tmprole.id:
                continue
            ret.append({
                'role': {
                    'id': tmprole.id
                },
                'scope': {
                    'project': {
                        'id': project,
                    }
                },
                'user': {
                    'id': user,
                }
            })
        return ret

    def _keystone_v3_role_assignments(self, **filters):
        # NOTE(samueldmq): different parameters have different representation
        # patterns as query parameters in the call to the list role assignments
        # API. The code below handles each set of patterns separately and
        # renames the parameters names accordingly, ignoring 'effective',
        # 'include_names' and 'include_subtree' whose do not need any renaming.
        for k in ('group', 'role', 'user'):
            if k in filters:
                filters[k + '.id'] = filters[k]
                del filters[k]
        for k in ('project', 'domain'):
            if k in filters:
                filters['scope.' + k + '.id'] = filters[k]
                del filters[k]
        if 'os_inherit_extension_inherited_to' in filters:
            filters['scope.OS-INHERIT:inherited_to'] = (
                filters['os_inherit_extension_inherited_to'])
            del filters['os_inherit_extension_inherited_to']

        data = self._identity_client.get(
            '/role_assignments', params=filters,
            error_message="Failed to list role assignments")
        return self._get_and_munchify('role_assignments', data)

    def list_role_assignments(self, filters=None):
        """List Keystone role assignments

        :param dict filters: Dict of filter conditions. Acceptable keys are:

            * 'user' (string) - User ID to be used as query filter.
            * 'group' (string) - Group ID to be used as query filter.
            * 'project' (string) - Project ID to be used as query filter.
            * 'domain' (string) - Domain ID to be used as query filter.
            * 'role' (string) - Role ID to be used as query filter.
            * 'os_inherit_extension_inherited_to' (string) - Return inherited
              role assignments for either 'projects' or 'domains'
            * 'effective' (boolean) - Return effective role assignments.
            * 'include_subtree' (boolean) - Include subtree

            'user' and 'group' are mutually exclusive, as are 'domain' and
            'project'.

            NOTE: For keystone v2, only user, project, and role are used.
                  Project and user are both required in filters.

        :returns: a list of ``munch.Munch`` containing the role assignment
            description. Contains the following attributes::

                - id: <role id>
                - user|group: <user or group id>
                - project|domain: <project or domain id>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        # NOTE(samueldmq): although 'include_names' is a valid query parameter
        # in the keystone v3 list role assignments API, it would have NO effect
        # on shade due to normalization. It is not documented as an acceptable
        # filter in the docs above per design!

        if not filters:
            filters = {}

        # NOTE(samueldmq): the docs above say filters are *IDs*, though if
        # munch.Munch objects are passed, this still works for backwards
        # compatibility as keystoneclient allows either IDs or objects to be
        # passed in.
        # TODO(samueldmq): fix the docs above to advertise munch.Munch objects
        # can be provided as parameters too
        for k, v in filters.items():
            if isinstance(v, munch.Munch):
                filters[k] = v['id']

        if self._is_client_version('identity', 2):
            if filters.get('project') is None or filters.get('user') is None:
                raise OpenStackCloudException(
                    "Must provide project and user for keystone v2"
                )
            assignments = self._keystone_v2_role_assignments(**filters)
        else:
            assignments = self._keystone_v3_role_assignments(**filters)

        return _utils.normalize_role_assignments(assignments)

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

        :returns: A ``munch.Munch`` describing the new flavor.

        :raises: OpenStackCloudException on operation error.
        """
        with _utils.shade_exceptions("Failed to create flavor {name}".format(
                name=name)):
            payload = {
                'disk': disk,
                'OS-FLV-EXT-DATA:ephemeral': ephemeral,
                'id': flavorid,
                'os-flavor-access:is_public': is_public,
                'name': name,
                'ram': ram,
                'rxtx_factor': rxtx_factor,
                'swap': swap,
                'vcpus': vcpus,
            }
            if flavorid == 'auto':
                payload['id'] = None
            data = _adapter._json_response(self.compute.post(
                '/flavors',
                json=dict(flavor=payload)))

        return self._normalize_flavor(
            self._get_and_munchify('flavor', data))

    def delete_flavor(self, name_or_id):
        """Delete a flavor

        :param name_or_id: ID or name of the flavor to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        flavor = self.get_flavor(name_or_id, get_extra=False)
        if flavor is None:
            self.log.debug(
                "Flavor %s not found for deleting", name_or_id)
            return False

        _adapter._json_response(
            self.compute.delete(
                '/flavors/{id}'.format(id=flavor['id'])),
            error_message="Unable to delete flavor {name}".format(
                name=name_or_id))

        return True

    def set_flavor_specs(self, flavor_id, extra_specs):
        """Add extra specs to a flavor

        :param string flavor_id: ID of the flavor to update.
        :param dict extra_specs: Dictionary of key-value pairs.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        _adapter._json_response(
            self.compute.post(
                "/flavors/{id}/os-extra_specs".format(id=flavor_id),
                json=dict(extra_specs=extra_specs)),
            error_message="Unable to set flavor specs")

    def unset_flavor_specs(self, flavor_id, keys):
        """Delete extra specs from a flavor

        :param string flavor_id: ID of the flavor to update.
        :param keys: List of spec keys to delete.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        for key in keys:
            _adapter._json_response(
                self.compute.delete(
                    "/flavors/{id}/os-extra_specs/{key}".format(
                        id=flavor_id, key=key)),
                error_message="Unable to delete flavor spec {0}".format(key))

    def _mod_flavor_access(self, action, flavor_id, project_id):
        """Common method for adding and removing flavor access
        """
        with _utils.shade_exceptions("Error trying to {action} access from "
                                     "flavor ID {flavor}".format(
                                         action=action, flavor=flavor_id)):
            endpoint = '/flavors/{id}/action'.format(id=flavor_id)
            access = {'tenant': project_id}
            access_key = '{action}TenantAccess'.format(action=action)

            _adapter._json_response(
                self.compute.post(endpoint, json={access_key: access}))

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

    def list_flavor_access(self, flavor_id):
        """List access from a private flavor for a project/tenant.

        :param string flavor_id: ID of the private flavor.

        :returns: a list of ``munch.Munch`` containing the access description

        :raises: OpenStackCloudException on operation error.
        """
        data = _adapter._json_response(
            self.compute.get(
                '/flavors/{id}/os-flavor-access'.format(id=flavor_id)),
            error_message=(
                "Error trying to list access from flavorID {flavor}".format(
                    flavor=flavor_id)))
        return _utils.normalize_flavor_accesses(
            self._get_and_munchify('flavor_access', data))

    @_utils.valid_kwargs('domain_id')
    def create_role(self, name, **kwargs):
        """Create a Keystone role.

        :param string name: The name of the role.
        :param domain_id: domain id (v3)

        :returns: a ``munch.Munch`` containing the role description

        :raise OpenStackCloudException: if the role cannot be created
        """
        v2 = self._is_client_version('identity', 2)
        url = '/OS-KSADM/roles' if v2 else '/roles'
        kwargs['name'] = name
        msg = 'Failed to create role {name}'.format(name=name)
        data = self._identity_client.post(
            url, json={'role': kwargs}, error_message=msg)
        role = self._get_and_munchify('role', data)
        return self._normalize_role(role)

    @_utils.valid_kwargs('domain_id')
    def update_role(self, name_or_id, name, **kwargs):
        """Update a Keystone role.

        :param name_or_id: Name or id of the role to update
        :param string name: The new role name
        :param domain_id: domain id

        :returns: a ``munch.Munch`` containing the role description

        :raise OpenStackCloudException: if the role cannot be created
        """
        if self._is_client_version('identity', 2):
            raise OpenStackCloudUnavailableFeature(
                'Unavailable Feature: Role update requires Identity v3'
            )
        kwargs['name_or_id'] = name_or_id
        role = self.get_role(**kwargs)
        if role is None:
            self.log.debug(
                "Role %s not found for updating", name_or_id)
            return False
        msg = 'Failed to update role {name}'.format(name=name_or_id)
        json_kwargs = {'role_id': role.id, 'role': {'name': name}}
        data = self._identity_client.patch('/roles', error_message=msg,
                                           json=json_kwargs)
        role = self._get_and_munchify('role', data)
        return self._normalize_role(role)

    @_utils.valid_kwargs('domain_id')
    def delete_role(self, name_or_id, **kwargs):
        """Delete a Keystone role.

        :param string id: Name or id of the role to delete.
        :param domain_id: domain id (v3)

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the openstack API call.
        """
        role = self.get_role(name_or_id, **kwargs)
        if role is None:
            self.log.debug(
                "Role %s not found for deleting", name_or_id)
            return False

        v2 = self._is_client_version('identity', 2)
        url = '{preffix}/{id}'.format(
            preffix='/OS-KSADM/roles' if v2 else '/roles', id=role['id'])
        error_msg = "Unable to delete role {name}".format(name=name_or_id)
        self._identity_client.delete(url, error_message=error_msg)

        return True

    def _get_grant_revoke_params(self, role, user=None, group=None,
                                 project=None, domain=None):
        role = self.get_role(role)
        if role is None:
            return {}
        data = {'role': role.id}

        # domain and group not available in keystone v2.0
        is_keystone_v2 = self._is_client_version('identity', 2)

        filters = {}
        if not is_keystone_v2 and domain:
            filters['domain_id'] = data['domain'] = \
                self.get_domain(domain)['id']

        if user:
            data['user'] = self.get_user(user, filters=filters)

        if project:
            # drop domain in favor of project
            data.pop('domain', None)
            data['project'] = self.get_project(project, filters=filters)

        if not is_keystone_v2 and group:
            data['group'] = self.get_group(group, filters=filters)

        return data

    def grant_role(self, name_or_id, user=None, group=None,
                   project=None, domain=None, wait=False, timeout=60):
        """Grant a role to a user.

        :param string name_or_id: The name or id of the role.
        :param string user: The name or id of the user.
        :param string group: The name or id of the group. (v3)
        :param string project: The name or id of the project.
        :param string domain: The id of the domain. (v3)
        :param bool wait: Wait for role to be granted
        :param int timeout: Timeout to wait for role to be granted

        NOTE: domain is a required argument when the grant is on a project,
            user or group specified by name. In that situation, they are all
            considered to be in that domain. If different domains are in use
            in the same role grant, it is required to specify those by ID.

        NOTE: for wait and timeout, sometimes granting roles is not
              instantaneous.

        NOTE: project is required for keystone v2

        :returns: True if the role is assigned, otherwise False

        :raise OpenStackCloudException: if the role cannot be granted
        """
        data = self._get_grant_revoke_params(name_or_id, user, group,
                                             project, domain)
        filters = data.copy()
        if not data:
            raise OpenStackCloudException(
                'Role {0} not found.'.format(name_or_id))

        if data.get('user') is not None and data.get('group') is not None:
            raise OpenStackCloudException(
                'Specify either a group or a user, not both')
        if data.get('user') is None and data.get('group') is None:
            raise OpenStackCloudException(
                'Must specify either a user or a group')
        if self._is_client_version('identity', 2) and \
                data.get('project') is None:
            raise OpenStackCloudException(
                'Must specify project for keystone v2')

        if self.list_role_assignments(filters=filters):
            self.log.debug('Assignment already exists')
            return False

        error_msg = "Error granting access to role: {0}".format(data)
        if self._is_client_version('identity', 2):
            # For v2.0, only tenant/project assignment is supported
            url = "/tenants/{t}/users/{u}/roles/OS-KSADM/{r}".format(
                t=data['project']['id'], u=data['user']['id'], r=data['role'])

            self._identity_client.put(url, error_message=error_msg,
                                      endpoint_filter={'interface': 'admin'})
        else:
            if data.get('project') is None and data.get('domain') is None:
                raise OpenStackCloudException(
                    'Must specify either a domain or project')

            # For v3, figure out the assignment type and build the URL
            if data.get('domain'):
                url = "/domains/{}".format(data['domain'])
            else:
                url = "/projects/{}".format(data['project']['id'])
            if data.get('group'):
                url += "/groups/{}".format(data['group']['id'])
            else:
                url += "/users/{}".format(data['user']['id'])
            url += "/roles/{}".format(data.get('role'))

            self._identity_client.put(url, error_message=error_msg)

        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for role to be granted"):
                if self.list_role_assignments(filters=filters):
                    break
        return True

    def revoke_role(self, name_or_id, user=None, group=None,
                    project=None, domain=None, wait=False, timeout=60):
        """Revoke a role from a user.

        :param string name_or_id: The name or id of the role.
        :param string user: The name or id of the user.
        :param string group: The name or id of the group. (v3)
        :param string project: The name or id of the project.
        :param string domain: The id of the domain. (v3)
        :param bool wait: Wait for role to be revoked
        :param int timeout: Timeout to wait for role to be revoked

        NOTE: for wait and timeout, sometimes revoking roles is not
              instantaneous.

        NOTE: project is required for keystone v2

        :returns: True if the role is revoke, otherwise False

        :raise OpenStackCloudException: if the role cannot be removed
        """
        data = self._get_grant_revoke_params(name_or_id, user, group,
                                             project, domain)
        filters = data.copy()

        if not data:
            raise OpenStackCloudException(
                'Role {0} not found.'.format(name_or_id))

        if data.get('user') is not None and data.get('group') is not None:
            raise OpenStackCloudException(
                'Specify either a group or a user, not both')
        if data.get('user') is None and data.get('group') is None:
            raise OpenStackCloudException(
                'Must specify either a user or a group')
        if self._is_client_version('identity', 2) and \
                data.get('project') is None:
            raise OpenStackCloudException(
                'Must specify project for keystone v2')

        if not self.list_role_assignments(filters=filters):
            self.log.debug('Assignment does not exist')
            return False

        error_msg = "Error revoking access to role: {0}".format(data)
        if self._is_client_version('identity', 2):
            # For v2.0, only tenant/project assignment is supported
            url = "/tenants/{t}/users/{u}/roles/OS-KSADM/{r}".format(
                t=data['project']['id'], u=data['user']['id'], r=data['role'])

            self._identity_client.delete(
                url, error_message=error_msg,
                endpoint_filter={'interface': 'admin'})
        else:
            if data.get('project') is None and data.get('domain') is None:
                raise OpenStackCloudException(
                    'Must specify either a domain or project')

            # For v3, figure out the assignment type and build the URL
            if data.get('domain'):
                url = "/domains/{}".format(data['domain'])
            else:
                url = "/projects/{}".format(data['project']['id'])
            if data.get('group'):
                url += "/groups/{}".format(data['group']['id'])
            else:
                url += "/users/{}".format(data['user']['id'])
            url += "/roles/{}".format(data.get('role'))

            self._identity_client.delete(url, error_message=error_msg)

        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for role to be revoked"):
                if not self.list_role_assignments(filters=filters):
                    break
        return True

    def list_hypervisors(self):
        """List all hypervisors

        :returns: A list of hypervisor ``munch.Munch``.
        """

        data = _adapter._json_response(
            self.compute.get('/os-hypervisors/detail'),
            error_message="Error fetching hypervisor list")
        return self._get_and_munchify('hypervisors', data)

    def search_aggregates(self, name_or_id=None, filters=None):
        """Seach host aggregates.

        :param name: aggregate name or id.
        :param filters: a dict containing additional filters to use.

        :returns: a list of dicts containing the aggregates

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the openstack API call.
        """
        aggregates = self.list_aggregates()
        return _utils._filter_list(aggregates, name_or_id, filters)

    def list_aggregates(self):
        """List all available host aggregates.

        :returns: A list of aggregate dicts.

        """
        data = _adapter._json_response(
            self.compute.get('/os-aggregates'),
            error_message="Error fetching aggregate list")
        return self._get_and_munchify('aggregates', data)

    def get_aggregate(self, name_or_id, filters=None):
        """Get an aggregate by name or ID.

        :param name_or_id: Name or ID of the aggregate.
        :param dict filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'availability_zone': 'nova',
                  'metadata': {
                      'cpu_allocation_ratio': '1.0'
                  }
                }

        :returns: An aggregate dict or None if no matching aggregate is
                  found.

        """
        return _utils._get_entity(self, 'aggregate', name_or_id, filters)

    def create_aggregate(self, name, availability_zone=None):
        """Create a new host aggregate.

        :param name: Name of the host aggregate being created
        :param availability_zone: Availability zone to assign hosts

        :returns: a dict representing the new host aggregate.

        :raises: OpenStackCloudException on operation error.
        """
        data = _adapter._json_response(
            self.compute.post(
                '/os-aggregates',
                json={'aggregate': {
                    'name': name,
                    'availability_zone': availability_zone
                }}),
            error_message="Unable to create host aggregate {name}".format(
                name=name))
        return self._get_and_munchify('aggregate', data)

    @_utils.valid_kwargs('name', 'availability_zone')
    def update_aggregate(self, name_or_id, **kwargs):
        """Update a host aggregate.

        :param name_or_id: Name or ID of the aggregate being updated.
        :param name: New aggregate name
        :param availability_zone: Availability zone to assign to hosts

        :returns: a dict representing the updated host aggregate.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        data = _adapter._json_response(
            self.compute.put(
                '/os-aggregates/{id}'.format(id=aggregate['id']),
                json={'aggregate': kwargs}),
            error_message="Error updating aggregate {name}".format(
                name=name_or_id))
        return self._get_and_munchify('aggregate', data)

    def delete_aggregate(self, name_or_id):
        """Delete a host aggregate.

        :param name_or_id: Name or ID of the host aggregate to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            self.log.debug("Aggregate %s not found for deleting", name_or_id)
            return False

        return _adapter._json_response(
            self.compute.delete(
                '/os-aggregates/{id}'.format(id=aggregate['id'])),
            error_message="Error deleting aggregate {name}".format(
                name=name_or_id))

        return True

    def set_aggregate_metadata(self, name_or_id, metadata):
        """Set aggregate metadata, replacing the existing metadata.

        :param name_or_id: Name of the host aggregate to update
        :param metadata: Dict containing metadata to replace (Use
                {'key': None} to remove a key)

        :returns: a dict representing the new host aggregate.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        err_msg = "Unable to set metadata for host aggregate {name}".format(
            name=name_or_id)

        data = _adapter._json_response(
            self.compute.post(
                '/os-aggregates/{id}/action'.format(id=aggregate['id']),
                json={'set_metadata': {'metadata': metadata}}),
            error_message=err_msg)
        return self._get_and_munchify('aggregate', data)

    def add_host_to_aggregate(self, name_or_id, host_name):
        """Add a host to an aggregate.

        :param name_or_id: Name or ID of the host aggregate.
        :param host_name: Host to add.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        err_msg = "Unable to add host {host} to aggregate {name}".format(
            host=host_name, name=name_or_id)

        return _adapter._json_response(
            self.compute.post(
                '/os-aggregates/{id}/action'.format(id=aggregate['id']),
                json={'add_host': {'host': host_name}}),
            error_message=err_msg)

    def remove_host_from_aggregate(self, name_or_id, host_name):
        """Remove a host from an aggregate.

        :param name_or_id: Name or ID of the host aggregate.
        :param host_name: Host to remove.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        err_msg = "Unable to remove host {host} to aggregate {name}".format(
            host=host_name, name=name_or_id)

        return _adapter._json_response(
            self.compute.post(
                '/os-aggregates/{id}/action'.format(id=aggregate['id']),
                json={'remove_host': {'host': host_name}}),
            error_message=err_msg)

    def get_volume_type_access(self, name_or_id):
        """Return a list of volume_type_access.

        :param name_or_id: Name or ID of the volume type.

        :raises: OpenStackCloudException on operation error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise OpenStackCloudException(
                "VolumeType not found: %s" % name_or_id)

        data = self._volume_client.get(
            '/types/{id}/os-volume-type-access'.format(id=volume_type.id),
            error_message="Unable to get volume type access"
                          " {name}".format(name=name_or_id))
        return self._normalize_volume_type_accesses(
            self._get_and_munchify('volume_type_access', data))

    def add_volume_type_access(self, name_or_id, project_id):
        """Grant access on a volume_type to a project.

        :param name_or_id: ID or name of a volume_type
        :param project_id: A project id

        NOTE: the call works even if the project does not exist.

        :raises: OpenStackCloudException on operation error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise OpenStackCloudException(
                "VolumeType not found: %s" % name_or_id)
        with _utils.shade_exceptions():
            payload = {'project': project_id}
            self._volume_client.post(
                '/types/{id}/action'.format(id=volume_type.id),
                json=dict(addProjectAccess=payload),
                error_message="Unable to authorize {project} "
                              "to use volume type {name}".format(
                              name=name_or_id, project=project_id))

    def remove_volume_type_access(self, name_or_id, project_id):
        """Revoke access on a volume_type to a project.

        :param name_or_id: ID or name of a volume_type
        :param project_id: A project id

        :raises: OpenStackCloudException on operation error.
        """
        volume_type = self.get_volume_type(name_or_id)
        if not volume_type:
            raise OpenStackCloudException(
                "VolumeType not found: %s" % name_or_id)
        with _utils.shade_exceptions():
            payload = {'project': project_id}
            self._volume_client.post(
                '/types/{id}/action'.format(id=volume_type.id),
                json=dict(removeProjectAccess=payload),
                error_message="Unable to revoke {project} "
                              "to use volume type {name}".format(
                              name=name_or_id, project=project_id))

    def set_compute_quotas(self, name_or_id, **kwargs):
        """ Set a quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: OpenStackCloudException if the resource to set the
            quota does not exist.
        """

        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        # compute_quotas = {key: val for key, val in kwargs.items()
        #                  if key in quota.COMPUTE_QUOTAS}
        # TODO(ghe): Manage volume and network quotas
        # network_quotas = {key: val for key, val in kwargs.items()
        #                  if key in quota.NETWORK_QUOTAS}
        # volume_quotas = {key: val for key, val in kwargs.items()
        #                 if key in quota.VOLUME_QUOTAS}

        kwargs['force'] = True
        _adapter._json_response(
            self.compute.put(
                '/os-quota-sets/{project}'.format(project=proj.id),
                json={'quota_set': kwargs}),
            error_message="No valid quota or resource")

    def get_compute_quotas(self, name_or_id):
        """ Get quota for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")
        data = _adapter._json_response(
            self.compute.get(
                '/os-quota-sets/{project}'.format(project=proj.id)))
        return self._get_and_munchify('quota_set', data)

    def delete_compute_quotas(self, name_or_id):
        """ Delete quota for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project or the
                 nova client call failed

        :returns: dict with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")
        return _adapter._json_response(
            self.compute.delete(
                '/os-quota-sets/{project}'.format(project=proj.id)))

    def get_compute_usage(self, name_or_id, start=None, end=None):
        """ Get usage for a specific project

        :param name_or_id: project name or id
        :param start: :class:`datetime.datetime` or string. Start date in UTC
                      Defaults to 2010-07-06T12:00:00Z (the date the OpenStack
                      project was started)
        :param end: :class:`datetime.datetime` or string. End date in UTC.
                    Defaults to now
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the usage
        """
        def parse_date(date):
            try:
                return iso8601.parse_date(date)
            except iso8601.iso8601.ParseError:
                # Yes. This is an exception mask. However,iso8601 is an
                # implementation detail - and the error message is actually
                # less informative.
                raise OpenStackCloudException(
                    "Date given, {date}, is invalid. Please pass in a date"
                    " string in ISO 8601 format -"
                    " YYYY-MM-DDTHH:MM:SS".format(
                        date=date))

        def parse_datetime_for_nova(date):
            # Must strip tzinfo from the date- it breaks Nova. Also,
            # Nova is expecting this in UTC. If someone passes in an
            # ISO8601 date string or a datetime with timzeone data attached,
            # strip the timezone data but apply offset math first so that
            # the user's well formed perfectly valid date will be used
            # correctly.
            offset = date.utcoffset()
            if offset:
                date = date - datetime.timedelta(hours=offset)
            return date.replace(tzinfo=None)

        if not start:
            start = parse_date('2010-07-06')
        elif not isinstance(start, datetime.datetime):
            start = parse_date(start)
        if not end:
            end = datetime.datetime.utcnow()
        elif not isinstance(start, datetime.datetime):
            end = parse_date(end)

        start = parse_datetime_for_nova(start)
        end = parse_datetime_for_nova(end)

        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist: {}".format(
                name=proj.id))

        data = _adapter._json_response(
            self.compute.get(
                '/os-simple-tenant-usage/{project}'.format(project=proj.id),
                params=dict(start=start.isoformat(), end=end.isoformat())),
            error_message="Unable to get usage for project: {name}".format(
                name=proj.id))
        return self._normalize_compute_usage(
            self._get_and_munchify('tenant_usage', data))

    def set_volume_quotas(self, name_or_id, **kwargs):
        """ Set a volume quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: OpenStackCloudException if the resource to set the
            quota does not exist.
        """

        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        kwargs['tenant_id'] = proj.id
        self._volume_client.put(
            '/os-quota-sets/{tenant_id}'.format(tenant_id=proj.id),
            json={'quota_set': kwargs},
            error_message="No valid quota or resource")

    def get_volume_quotas(self, name_or_id):
        """ Get volume quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        data = self._volume_client.get(
            '/os-quota-sets/{tenant_id}'.format(tenant_id=proj.id),
            error_message="cinder client call failed")
        return self._get_and_munchify('quota_set', data)

    def delete_volume_quotas(self, name_or_id):
        """ Delete volume quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project or the
                 cinder client call failed

        :returns: dict with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        return self._volume_client.delete(
            '/os-quota-sets/{tenant_id}'.format(tenant_id=proj.id),
            error_message="cinder client call failed")

    def set_network_quotas(self, name_or_id, **kwargs):
        """ Set a network quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: OpenStackCloudException if the resource to set the
            quota does not exist.
        """

        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")

        self._network_client.put(
            '/quotas/{project_id}.json'.format(project_id=proj.id),
            json={'quota': kwargs},
            error_message=("Error setting Neutron's quota for "
                           "project {0}".format(proj.id)))

    def get_network_quotas(self, name_or_id, details=False):
        """ Get network quotas for a project

        :param name_or_id: project name or id
        :param details: if set to True it will return details about usage
                        of quotas by given project
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")
        url = '/quotas/{project_id}'.format(project_id=proj.id)
        if details:
            url = url + "/details"
        url = url + ".json"
        data = self._network_client.get(
            url,
            error_message=("Error fetching Neutron's quota for "
                           "project {0}".format(proj.id)))
        return self._get_and_munchify('quota', data)

    def get_network_extensions(self):
        """Get Cloud provided network extensions

        :returns: set of Neutron extension aliases
        """
        return self._neutron_extensions()

    def delete_network_quotas(self, name_or_id):
        """ Delete network quotas for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project or the
                 network client call failed

        :returns: dict with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise OpenStackCloudException("project does not exist")
        self._network_client.delete(
            '/quotas/{project_id}.json'.format(project_id=proj.id),
            error_message=("Error deleting Neutron's quota for "
                           "project {0}".format(proj.id)))

    def list_magnum_services(self):
        """List all Magnum services.
        :returns: a list of dicts containing the service details.

        :raises: OpenStackCloudException on operation error.
        """
        with _utils.shade_exceptions("Error fetching Magnum services list"):
            data = self._container_infra_client.get('/mservices')
            return self._normalize_magnum_services(
                self._get_and_munchify('mservices', data))
