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

import atexit
import concurrent.futures
import copy
import functools
import queue
import types
import typing as ty
import warnings
import weakref

import dogpile.cache
import keystoneauth1.exceptions
import requests.models
import requestsexceptions
import typing_extensions as ty_ext

from openstack import _log
from openstack import _services_mixin
from openstack.cloud import _utils
from openstack.cloud import meta
from openstack import config as cloud_config
from openstack.config import cloud_region
from openstack import exceptions
from openstack import proxy
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings

if ty.TYPE_CHECKING:
    from keystoneauth1 import session as ks_session
    from oslo_config import cfg

    from openstack import service_description


class _OpenStackCloudMixin(_services_mixin.ServicesMixin):
    """Represent a connection to an OpenStack Cloud.

    OpenStackCloud is the entry point for all cloud operations, regardless
    of which OpenStack service those operations may ultimately come from.
    The operations on an OpenStackCloud are resource oriented rather than
    REST API operation oriented. For instance, one will request a Floating IP
    and that Floating IP will be actualized either via neutron or via nova
    depending on how this particular cloud has decided to arrange itself.
    """

    _OBJECT_MD5_KEY = 'x-sdk-md5'
    _OBJECT_SHA256_KEY = 'x-sdk-sha256'
    _OBJECT_AUTOCREATE_KEY = 'x-sdk-autocreated'
    _OBJECT_AUTOCREATE_CONTAINER = 'images'

    # NOTE(shade) shade keys were x-object-meta-x-shade-md5 - we need to check
    #             those in freshness checks so that a shade->sdk transition
    #             doesn't result in a re-upload
    _SHADE_OBJECT_MD5_KEY = 'x-object-meta-x-shade-md5'
    _SHADE_OBJECT_SHA256_KEY = 'x-object-meta-x-shade-sha256'
    _SHADE_OBJECT_AUTOCREATE_KEY = 'x-object-meta-x-shade-autocreated'

    config: cloud_region.CloudRegion

    def __init__(
        self,
        cloud: ty.Optional[str] = None,
        config: ty.Optional[cloud_region.CloudRegion] = None,
        session: ty.Optional['ks_session.Session'] = None,
        app_name: ty.Optional[str] = None,
        app_version: ty.Optional[str] = None,
        extra_services: ty.Optional[
            list['service_description.ServiceDescription']
        ] = None,
        strict: bool = False,
        use_direct_get: ty.Optional[bool] = None,
        task_manager: ty.Any = None,
        rate_limit: ty.Union[float, dict[str, float], None] = None,
        oslo_conf: ty.Optional['cfg.ConfigOpts'] = None,
        service_types: ty.Optional[list[str]] = None,
        global_request_id: ty.Optional[str] = None,
        strict_proxies: bool = False,
        pool_executor: ty.Optional[concurrent.futures.Executor] = None,
        **kwargs: ty.Any,
    ):
        """Create a connection to a cloud.

        A connection needs information about how to connect, how to
        authenticate and how to select the appropriate services to use.

        The recommended way to provide this information is by referencing
        a named cloud config from an existing `clouds.yaml` file. The cloud
        name ``envvars`` may be used to consume a cloud configured via ``OS_``
        environment variables.

        A pre-existing :class:`~openstack.config.cloud_region.CloudRegion`
        object can be passed in lieu of a cloud name, for cases where the user
        already has a fully formed CloudRegion and just wants to use it.

        Similarly, if for some reason the user already has a
        :class:`~keystoneauth1.session.Session` and wants to use it, it may be
        passed in.

        :param str cloud: Name of the cloud from config to use.
        :param config: CloudRegion object representing the config for the
            region of the cloud in question.
        :type config: :class:`~openstack.config.cloud_region.CloudRegion`
        :param session: A session object compatible with
            :class:`~keystoneauth1.session.Session`.
        :type session: :class:`~keystoneauth1.session.Session`
        :param str app_name: Name of the application to be added to User Agent.
        :param str app_version: Version of the application to be added to
            User Agent.
        :param extra_services: List of
            :class:`~openstack.service_description.ServiceDescription`
            objects describing services that openstacksdk otherwise does not
            know about.
        :param bool use_direct_get:
            For get methods, make specific REST calls for server-side
            filtering instead of making list calls and filtering client-side.
            Default false.
        :param task_manager:
            Ignored. Exists for backwards compat during transition. Rate limit
            parameters should be passed directly to the `rate_limit` parameter.
        :param rate_limit:
            Client-side rate limit, expressed in calls per second. The
            parameter can either be a single float, or it can be a dict with
            keys as service-type and values as floats expressing the calls
            per second for that service. Defaults to None, which means no
            rate-limiting is performed.
        :param oslo_conf: An oslo.config CONF object.
        :type oslo_conf: :class:`~oslo_config.cfg.ConfigOpts`
            An oslo.config ``CONF`` object that has been populated with
            ``keystoneauth1.loading.register_adapter_conf_options`` in
            groups named by the OpenStack service's project name.
        :param service_types:
            A list/set of service types this Connection should support. All
            other service types will be disabled (will error if used).
            **Currently only supported in conjunction with the ``oslo_conf``
            kwarg.**
        :param global_request_id: A Request-id to send with all interactions.
        :param strict_proxies:
            If True, check proxies on creation and raise
            ServiceDiscoveryException if the service is unavailable.
        :type strict_proxies: bool
            Throw an ``openstack.exceptions.ServiceDiscoveryException`` if the
            endpoint for a given service doesn't work. This is useful for
            OpenStack services using sdk to talk to other OpenStack services
            where it can be expected that the deployer config is correct and
            errors should be reported immediately.
            Default false.
        :param pool_executor:
        :type pool_executor: :class:`~futurist.Executor`
            A futurist ``Executor`` object to be used for concurrent background
            activities. Defaults to None in which case a ThreadPoolExecutor
            will be created if needed.
        :param kwargs: If a config is not provided, the rest of the parameters
            provided are assumed to be arguments to be passed to the
            CloudRegion constructor.
        """
        super().__init__()

        if use_direct_get is not None:
            warnings.warn(
                "The 'use_direct_get' argument is deprecated for removal",
                os_warnings.RemovedInSDK50Warning,
            )

        self._extra_services = {}
        self._strict_proxies = strict_proxies
        if extra_services:
            for service in extra_services:
                self._extra_services[service.service_type] = service

        if config:
            self.config = config
        else:
            if oslo_conf:
                self.config = cloud_region.from_conf(
                    oslo_conf,
                    session=session,
                    app_name=app_name,
                    app_version=app_version,
                    service_types=service_types,
                )
            elif session:
                self.config = cloud_region.from_session(
                    session=session,
                    app_name=app_name,
                    app_version=app_version,
                    load_yaml_config=False,
                    load_envvars=False,
                    rate_limit=rate_limit,
                    **kwargs,
                )
            else:
                self.config = cloud_config.get_cloud_region(
                    cloud=cloud,
                    app_name=app_name,
                    app_version=app_version,
                    load_yaml_config=cloud is not None,
                    load_envvars=cloud is not None,
                    rate_limit=rate_limit,
                    **kwargs,
                )

        self._session = None
        self._proxies: dict[str, proxy.Proxy] = {}
        self.__pool_executor = pool_executor
        self._global_request_id = global_request_id
        self.use_direct_get = use_direct_get or False
        self.strict_mode = strict

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
                "Turning off Insecure SSL warnings since verify=False"
            )
            category = requestsexceptions.InsecureRequestWarning
            if category:
                # InsecureRequestWarning references a Warning class or is None
                warnings.filterwarnings('ignore', category=category)

        self._disable_warnings: dict[str, bool] = {}

        cache_expiration_time = int(self.config.get_cache_expiration_time())
        cache_class = self.config.get_cache_class()
        cache_arguments = self.config.get_cache_arguments()

        self._cache_expirations = dict()

        if cache_class != 'dogpile.cache.null':
            self.cache_enabled = True
        else:
            self.cache_enabled = False

        # Uncoditionally create cache even with a "null" backend
        self._cache = self._make_cache(
            cache_class, cache_expiration_time, cache_arguments
        )
        expirations = self.config.get_cache_expirations()
        for expire_key in expirations.keys():
            self._cache_expirations[expire_key] = expirations[expire_key]

        self._api_cache_keys: set[str] = set()

        self._local_ipv6 = (
            _utils.localhost_supports_ipv6() if not self.force_ipv4 else False
        )

        # Register cleanup steps
        atexit.register(self.close)

    @property
    def session(self):
        if not self._session:
            self._session = self.config.get_session()
            # Hide a reference to the connection on the session to help with
            # backwards compatibility for folks trying to just pass
            # conn.session to a Resource method's session argument.
            self.session._sdk_connection = weakref.proxy(self)
        return self._session

    @property
    def _pool_executor(self) -> concurrent.futures.Executor:
        if not self.__pool_executor:
            self.__pool_executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=5
            )
        return self.__pool_executor

    def close(self) -> None:
        """Release any resources held open."""
        self.config.set_auth_cache()
        if self.__pool_executor:
            self.__pool_executor.shutdown()
        atexit.unregister(self.close)

    def __enter__(self) -> ty_ext.Self:
        return self

    def __exit__(
        self,
        exc_type: ty.Optional[type[BaseException]],
        exc_value: ty.Optional[BaseException],
        traceback: ty.Optional[types.TracebackType],
    ) -> None:
        self.close()

    def set_global_request_id(self, global_request_id: str) -> None:
        self._global_request_id = global_request_id

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
        config = cloud_region.from_session(
            session=self.session,
            app_name=self.config._app_name,
            app_version=self.config._app_version,
            discovery_cache=self.session._discovery_cache,
            **params,
        )

        # Override the cloud name so that logging/location work right
        config._name = self.name
        config.config['profile'] = self.name
        # Use self.__class__ so that we return whatever this is, like if it's
        # a subclass in the case of shade wrapping sdk.
        new_conn = self.__class__(config=config)
        new_conn.set_global_request_id(global_request_id)
        return new_conn

    def _make_cache(self, cache_class, expiration_time, arguments):
        return dogpile.cache.make_region(
            function_key_generator=self._make_cache_key
        ).configure(
            cache_class, expiration_time=expiration_time, arguments=arguments
        )

    def _make_cache_key(self, namespace, fn):
        fname = fn.__name__
        if namespace is None:
            name_key = self.name
        else:
            name_key = f'{self.name}:{namespace}'

        def generate_key(*args, **kwargs):
            # TODO(frickler): make handling arg keys actually work
            arg_key = ''
            kw_keys = sorted(kwargs.keys())
            kwargs_key = ','.join(
                [f'{k}:{kwargs[k]}' for k in kw_keys if k != 'cache']
            )
            ans = "_".join([str(name_key), fname, arg_key, kwargs_key])
            return ans

        return generate_key

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
        """Return a ``utils.Munch`` describing the current project"""
        return self._get_project_info()

    def _get_project_info(self, project_id=None):
        project_info = utils.Munch(
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
        """Return a ``utils.Munch`` explaining the current cloud location."""
        return self._get_current_location()

    def _get_current_location(self, project_id=None, zone=None):
        return utils.Munch(
            cloud=self.name,
            # TODO(efried): This is wrong, but it only seems to be used in a
            # repr; can we get rid of it?
            region_name=self.config.get_region_name(),
            zone=zone,
            project=self._get_project_info(project_id),
        )

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
        :raises: :class:`~openstack.exceptions.SDKException` on invalid range
            expressions.
        """
        filtered: list[object] = []

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

    def get_session_endpoint(self, service_key, **kwargs):
        if not kwargs:
            kwargs = {}
        try:
            return self.config.get_session_endpoint(service_key, **kwargs)
        except keystoneauth1.exceptions.catalog.EndpointNotFound as e:
            self.log.debug(
                "Endpoint not found in %s cloud: %s", self.name, str(e)
            )
            endpoint = None
        except exceptions.SDKException:
            raise
        except Exception as e:
            raise exceptions.SDKException(
                f"Error getting {service_key} endpoint on {self.name}:{self.config.get_region_name(service_key)}: "
                f"{str(e)}"
            )
        return endpoint

    def has_service(self, service_key, version=None):
        if not self.config.has_service(service_key):
            # TODO(mordred) add a stamp here so that we only report this once
            if not (
                service_key in self._disable_warnings
                and self._disable_warnings[service_key]
            ):
                self.log.debug(
                    "Disabling %(service_key)s entry in catalog per config",
                    {'service_key': service_key},
                )
                self._disable_warnings[service_key] = True
            return False
        try:
            kwargs = dict()
            # If a specific version was requested - try it
            if version is not None:
                kwargs['min_version'] = version
                kwargs['max_version'] = version
            endpoint = self.get_session_endpoint(service_key, **kwargs)
        except exceptions.SDKException:
            return False
        if endpoint:
            return True
        else:
            return False

    def search_resources(
        self,
        resource_type,
        name_or_id,
        get_args=None,
        get_kwargs=None,
        list_args=None,
        list_kwargs=None,
        **filters,
    ):
        """Search resources

        Search resources matching certain conditions

        :param str resource_type: String representation of the expected
            resource as `service.resource` (i.e. "network.security_group").
        :param str name_or_id: Name or ID of the resource
        :param list get_args: Optional args to be passed to the _get call.
        :param dict get_kwargs: Optional kwargs to be passed to the _get call.
        :param list list_args: Optional args to be passed to the _list call.
        :param dict list_kwargs: Optional kwargs to be passed to the _list call
        :param dict filters: Additional filters to be used for querying
            resources.
        """
        get_args = get_args or ()
        get_kwargs = get_kwargs or {}
        list_args = list_args or ()
        list_kwargs = list_kwargs or {}

        # User used string notation. Try to find proper
        # resource
        (service_name, resource_name) = resource_type.split('.')
        if not hasattr(self, service_name):
            raise exceptions.SDKException(
                f"service {service_name} is not existing/enabled"
            )
        service_proxy = getattr(self, service_name)
        try:
            resource_type = service_proxy._resource_registry[resource_name]
        except KeyError:
            raise exceptions.SDKException(
                f"Resource {resource_name} is not known in service {service_name}"
            )

        if name_or_id:
            # name_or_id is definitely not None
            try:
                resource_by_id = service_proxy._get(
                    resource_type, name_or_id, *get_args, **get_kwargs
                )
                return [resource_by_id]
            except exceptions.NotFoundException:
                pass

        if not filters:
            filters = {}

        if name_or_id:
            filters["name"] = name_or_id
        list_kwargs.update(filters)

        return list(
            service_proxy._list(resource_type, *list_args, **list_kwargs)
        )

    def project_cleanup(
        self,
        dry_run=True,
        wait_timeout=120,
        status_queue=None,
        filters=None,
        resource_evaluation_fn=None,
        skip_resources=None,
    ):
        """Cleanup the project resources.

        Cleanup all resources in all services, which provide cleanup methods.

        :param bool dry_run: Cleanup or only list identified resources.
        :param int wait_timeout: Maximum amount of time given to each service
            to comlete the cleanup.
        :param queue status_queue: a threading queue object used to get current
            process status. The queue contain processed resources.
        :param dict filters: Additional filters for the cleanup (only resources
            matching all filters will be deleted, if there are no other
            dependencies).
        :param resource_evaluation_fn: A callback function, which will be
            invoked for each resurce and must return True/False depending on
            whether resource need to be deleted or not.
        :param skip_resources: List of specific resources whose cleanup should
            be skipped.
        """
        dependencies = {}
        get_dep_fn_name = '_get_cleanup_dependencies'
        cleanup_fn_name = '_service_cleanup'
        if not status_queue:
            status_queue = queue.Queue()
        for service in self.config.get_enabled_services():
            try:
                if hasattr(self, service):
                    proxy = getattr(self, service)
                    if (
                        proxy
                        and hasattr(proxy, get_dep_fn_name)
                        and hasattr(proxy, cleanup_fn_name)
                    ):
                        deps = getattr(proxy, get_dep_fn_name)()
                        if deps:
                            dependencies.update(deps)
            except (
                exceptions.NotSupported,
                exceptions.ServiceDisabledException,
            ):
                # Cloud may include endpoint in catalog but not
                # implement the service or disable it
                pass
        dep_graph = utils.TinyDAG()
        for k, v in dependencies.items():
            dep_graph.add_node(k)
            for dep in v['before']:
                dep_graph.add_node(dep)
                dep_graph.add_edge(k, dep)
            for dep in v.get('after', []):
                dep_graph.add_edge(dep, k)

        cleanup_resources: dict[str, resource.Resource] = {}

        for service in dep_graph.walk(timeout=wait_timeout):
            fn = None
            try:
                if hasattr(self, service):
                    proxy = getattr(self, service)
                    cleanup_fn = getattr(proxy, cleanup_fn_name, None)
                    if cleanup_fn:
                        fn = functools.partial(
                            cleanup_fn,
                            dry_run=dry_run,
                            client_status_queue=status_queue,
                            identified_resources=cleanup_resources,
                            filters=filters,
                            resource_evaluation_fn=resource_evaluation_fn,
                            skip_resources=skip_resources,
                        )
            except exceptions.ServiceDisabledException:
                # same reason as above
                pass
            if fn:
                self._pool_executor.submit(
                    cleanup_task, dep_graph, service, fn
                )
            else:
                dep_graph.node_done(service)

        for count in utils.iterate_timeout(
            timeout=wait_timeout,
            message="Timeout waiting for cleanup to finish",
            wait=1,
        ):
            if dep_graph.is_complete():
                return


def cleanup_task(graph, service, fn):
    try:
        fn()
    except Exception:
        log = _log.setup_logging('openstack.project_cleanup')
        log.exception(f'Error in the {service} cleanup function')
    finally:
        graph.node_done(service)
