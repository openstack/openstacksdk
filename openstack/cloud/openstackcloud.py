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
import copy
import functools
import six
# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import types  # noqa
import warnings

import dogpile.cache
import munch
import requests.models
import requestsexceptions

import keystoneauth1.exceptions
import keystoneauth1.session

from openstack import _log
from openstack.cloud import exc
from openstack.cloud import _floating_ip
from openstack.cloud import _object_store
from openstack.cloud import meta
from openstack.cloud import _utils
import openstack.config
from openstack.config import cloud_region as cloud_region_mod
from openstack import proxy

DEFAULT_SERVER_AGE = 5
DEFAULT_PORT_AGE = 5
DEFAULT_FLOAT_AGE = 5
_CONFIG_DOC_URL = _floating_ip._CONFIG_DOC_URL

DEFAULT_OBJECT_SEGMENT_SIZE = _object_store.DEFAULT_OBJECT_SEGMENT_SIZE
# This halves the current default for Swift
DEFAULT_MAX_FILE_SIZE = _object_store.DEFAULT_MAX_FILE_SIZE
OBJECT_CONTAINER_ACLS = _object_store.OBJECT_CONTAINER_ACLS


class _OpenStackCloudMixin(object):
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
    _OBJECT_MD5_KEY = 'x-object-meta-x-sdk-md5'
    _OBJECT_SHA256_KEY = 'x-object-meta-x-sdk-sha256'
    _OBJECT_AUTOCREATE_KEY = 'x-object-meta-x-sdk-autocreated'
    _OBJECT_AUTOCREATE_CONTAINER = 'images'

    # NOTE(shade) shade keys were x-object-meta-x-shade-md5 - we need to check
    #             those in freshness checks so that a shade->sdk transition
    #             doesn't result in a re-upload
    _SHADE_OBJECT_MD5_KEY = 'x-object-meta-x-shade-md5'
    _SHADE_OBJECT_SHA256_KEY = 'x-object-meta-x-shade-sha256'
    _SHADE_OBJECT_AUTOCREATE_KEY = 'x-object-meta-x-shade-autocreated'

    def __init__(self):

        super(_OpenStackCloudMixin, self).__init__()

        self.log = _log.setup_logging('openstack')

        self.name = self.config.name
        self.auth = self.config.get_auth_args()
        self.default_interface = self.config.get_interface()
        self.force_ipv4 = self.config.force_ipv4

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

        # self.__pool_executor = None

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

        cloud_region = config.get_one(**params)
        # Attach the discovery cache from the old session so we won't
        # double discover.
        cloud_region._discovery_cache = self.session._discovery_cache
        # Override the cloud name so that logging/location work right
        cloud_region._name = self.name
        cloud_region.config['profile'] = self.name
        # Use self.__class__ so that we return whatever this if, like if it's
        # a subclass in the case of shade wrapping sdk.
        return self.__class__(config=cloud_region)

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

    def global_request(self, global_request_id):
        """Make a new Connection object with a global request id set.

        Take the existing settings from the current Connection and construct a
        new Connection object with the global_request_id overridden.

        .. code-block:: python

          from oslo_context import context
          cloud = openstack.connect(cloud='example')
          # Work normally
          servers = cloud.list_servers()
          cloud2 = cloud.global_request(context.generate_request_id())
          # cloud2 sends all requests with global_request_id set
          servers = cloud2.list_servers()

        Additionally, this can be used as a context manager:

        .. code-block:: python

          from oslo_context import context
          c = openstack.connect(cloud='example')
          # Work normally
          servers = c.list_servers()
          with c.global_request(context.generate_request_id()) as c2:
              # c2 sends all requests with global_request_id set
              servers = c2.list_servers()

        :param global_request_id: The `global_request_id` to send.
        """
        params = copy.deepcopy(self.config.config)
        cloud_region = cloud_region_mod.from_session(
            session=self.session,
            app_name=self.config._app_name,
            app_version=self.config._app_version,
            discovery_cache=self.session._discovery_cache,
            **params)

        # Override the cloud name so that logging/location work right
        cloud_region._name = self.name
        cloud_region.config['profile'] = self.name
        # Use self.__class__ so that we return whatever this is, like if it's
        # a subclass in the case of shade wrapping sdk.
        new_conn = self.__class__(config=cloud_region)
        new_conn.set_global_request_id(global_request_id)
        return new_conn

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
                raise exc.OpenStackCloudException(
                    "Version {config_version} requested for {service_type}"
                    " but shade understands a minimum of {min_version}".format(
                        config_version=config_version,
                        service_type=service_type,
                        min_version=min_version))
            elif max_major and config_major > max_major:
                raise exc.OpenStackCloudException(
                    "Version {config_version} requested for {service_type}"
                    " but openstack.cloud understands a maximum of"
                    " {max_version}".format(
                        config_version=config_version,
                        service_type=service_type,
                        max_version=max_version))
            request_min_version = config_version
            request_max_version = '{version}.latest'.format(
                version=config_major)
            adapter = proxy._ShadeAdapter(
                session=self.session,
                service_type=self.config.get_service_type(service_type),
                service_name=self.config.get_service_name(service_type),
                interface=self.config.get_interface(service_type),
                endpoint_override=self.config.get_endpoint(service_type),
                region_name=self.config.get_region_name(service_type),
                statsd_prefix=self.config.get_statsd_prefix(),
                statsd_client=self.config.get_statsd_client(),
                prometheus_counter=self.config.get_prometheus_counter(),
                prometheus_histogram=self.config.get_prometheus_histogram(),
                influxdb_client=self.config.get_influxdb_client(),
                min_version=request_min_version,
                max_version=request_max_version)
            if adapter.get_endpoint():
                return adapter

        adapter = proxy._ShadeAdapter(
            session=self.session,
            service_type=self.config.get_service_type(service_type),
            service_name=self.config.get_service_name(service_type),
            interface=self.config.get_interface(service_type),
            endpoint_override=self.config.get_endpoint(service_type),
            region_name=self.config.get_region_name(service_type),
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
        if api_version and config_version and (api_major != config_major):
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
        return proxy._ShadeAdapter(
            session=self.session,
            service_type=self.config.get_service_type(service_type),
            service_name=self.config.get_service_name(service_type),
            interface=self.config.get_interface(service_type),
            endpoint_override=self.config.get_endpoint(
                service_type) or endpoint_override,
            region_name=self.config.get_region_name(service_type))

    def _is_client_version(self, client, version):
        client_name = '_{client}_client'.format(
            client=client.replace('-', '_'))
        client = getattr(self, client_name)
        return client._version_matches(version)

    @property
    def _application_catalog_client(self):
        if 'application-catalog' not in self._raw_clients:
            self._raw_clients['application-catalog'] = self._get_raw_client(
                'application-catalog')
        return self._raw_clients['application-catalog']

    @property
    def _database_client(self):
        if 'database' not in self._raw_clients:
            self._raw_clients['database'] = self._get_raw_client('database')
        return self._raw_clients['database']

    @property
    def _raw_image_client(self):
        if 'raw-image' not in self._raw_clients:
            image_client = self._get_raw_client('image')
            self._raw_clients['raw-image'] = image_client
        return self._raw_clients['raw-image']

    def pprint(self, resource):
        """Wrapper around pprint that groks munch objects"""
        # import late since this is a utility function
        import pprint
        new_resource = _utils._dictify_resource(resource)
        pprint.pprint(new_resource)

    def pformat(self, resource):
        """Wrapper around pformat that groks munch objects"""
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

    def endpoint_for(self, service_type, interface=None, region_name=None):
        """Return the endpoint for a given service.

        Respects config values for Connection, including
        ``*_endpoint_override``. For direct values from the catalog
        regardless of overrides, see
        :meth:`~openstack.config.cloud_region.CloudRegion.get_endpoint_from_catalog`

        :param service_type: Service Type of the endpoint to search for.
        :param interface:
            Interface of the endpoint to search for. Optional, defaults to
            the configured value for interface for this Connection.
        :param region_name:
            Region Name of the endpoint to search for. Optional, defaults to
            the configured value for region_name for this Connection.

        :returns: The endpoint of the service, or None if not found.
        """

        endpoint_override = self.config.get_endpoint(service_type)
        if endpoint_override:
            return endpoint_override
        return self.config.get_endpoint_from_catalog(
            service_type=service_type,
            interface=interface,
            region_name=region_name)

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
            # TODO(efried): This is wrong, but it only seems to be used in a
            # repr; can we get rid of it?
            region_name=self.config.get_region_name(),
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
                raise exc.OpenStackCloudException(
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
        if isinstance(data, requests.models.Response):
            data = proxy._json_response(data)
        return meta.get_and_munchify(key, data)

    def get_name(self):
        return self.name

    def get_session_endpoint(self, service_key):
        try:
            return self.config.get_session_endpoint(service_key)
        except keystoneauth1.exceptions.catalog.EndpointNotFound as e:
            self.log.debug(
                "Endpoint not found in %s cloud: %s", self.name, str(e))
            endpoint = None
        except exc.OpenStackCloudException:
            raise
        except Exception as e:
            raise exc.OpenStackCloudException(
                "Error getting {service} endpoint on {cloud}:{region}:"
                " {error}".format(
                    service=service_key,
                    cloud=self.name,
                    region=self.config.get_region_name(service_key),
                    error=str(e)))
        return endpoint

    def has_service(self, service_key):
        if not self.config.has_service(service_key):
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
        except exc.OpenStackCloudException:
            return False
        if endpoint:
            return True
        else:
            return False
