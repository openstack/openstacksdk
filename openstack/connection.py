# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
The :class:`~openstack.connection.Connection` class is the primary interface
to the Python SDK. It maintains a context for a connection to a region of
a cloud provider. The :class:`~openstack.connection.Connection` has an
attribute to access each OpenStack service.

At a minimum, the :class:`~openstack.connection.Connection` class needs to be
created with a config or the parameters to build one.

While the overall system is very flexible, there are four main use cases
for different ways to create a :class:`~openstack.connection.Connection`.

* Using config settings and keyword arguments as described in
  :ref:`openstack-config`
* Using only keyword arguments passed to the constructor ignoring config files
  and environment variables.
* Using an existing authenticated `keystoneauth1.session.Session`, such as
  might exist inside of an OpenStack service operational context.
* Using an existing :class:`~openstack.config.cloud_region.CloudRegion`.

Creating the Connection
-----------------------

Using config settings
~~~~~~~~~~~~~~~~~~~~~

For users who want to create a :class:`~openstack.connection.Connection` making
use of named clouds in ``clouds.yaml`` files, ``OS_`` environment variables
and python keyword arguments, the :func:`openstack.connect` factory function
is the recommended way to go:

.. code-block:: python

    import openstack

    conn = openstack.connect(cloud='example', region_name='earth1')

If the application in question is a command line application that should also
accept command line arguments, an `argparse.Namespace` can be passed to
:func:`openstack.connect` that will have relevant arguments added to it and
then subsequently consumed by the constructor:

.. code-block:: python

    import argparse
    import openstack

    options = argparse.ArgumentParser(description='Awesome OpenStack App')
    conn = openstack.connect(options=options)

Using only keyword arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the application wants to avoid loading any settings from ``clouds.yaml`` or
environment variables, use the :class:`~openstack.connection.Connection`
constructor directly. As long as the ``cloud`` argument is omitted or ``None``,
the :class:`~openstack.connection.Connection` constructor will not load
settings from files or the environment.

.. note::

    This is a different default behavior than the :func:`~openstack.connect`
    factory function. In :func:`~openstack.connect` if ``cloud`` is omitted
    or ``None``, a default cloud will be loaded, defaulting to the ``envvars``
    cloud if it exists.

.. code-block:: python

    from openstack import connection

    conn = connection.Connection(
        region_name='example-region',
        auth={
            'auth_url': 'https://auth.example.com',
            'username': 'amazing-user',
            'password': 'super-secret-password',
            'project_id': '33aa1afc-03fe-43b8-8201-4e0d3b4b8ab5',
            'user_domain_id': '054abd68-9ad9-418b-96d3-3437bb376703',
        },
        compute_api_version='2',
        identity_interface='internal',
    )

Per-service settings as needed by `keystoneauth1.adapter.Adapter` such as
``api_version``, ``service_name``, and ``interface`` can be set, as seen
above, by prefixing them with the official ``service-type`` name of the
service. ``region_name`` is a setting for the entire
:class:`~openstack.config.cloud_region.CloudRegion` and cannot be set per
service.

From existing authenticated Session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For applications that already have an authenticated Session, simply passing
it to the :class:`~openstack.connection.Connection` constructor is all that
is needed:

.. code-block:: python

    from openstack import connection

    conn = connection.Connection(
        session=session,
        region_name='example-region',
        compute_api_version='2',
        identity_interface='internal',
    )

From oslo.conf CONF object
~~~~~~~~~~~~~~~~~~~~~~~~~~

For applications that have an oslo.config ``CONF`` object that has been
populated with ``keystoneauth1.loading.register_adapter_conf_options`` in
groups named by the OpenStack service's project name, it is possible to
construct a Connection with the ``CONF`` object and an authenticated Session.

.. note::

    This is primarily intended for use by OpenStack services to talk amongst
    themselves.

.. code-block:: python

    from keystoneauth1 import loading as ks_loading
    from oslo_config import cfg
    from openstack import connection

    CONF = cfg.CONF

    group = cfg.OptGroup('neutron')
    ks_loading.register_session_conf_options(CONF, group)
    ks_loading.register_auth_conf_options(CONF, group)
    ks_loading.register_adapter_conf_options(CONF, group)

    CONF()

    auth = ks_loading.load_auth_from_conf_options(CONF, 'neutron')
    sess = ks_loading.load_session_from_conf_options(CONF, 'neutron', auth=auth)

    conn = connection.Connection(
        session=sess,
        oslo_conf=CONF,
    )

This can then be used with an appropriate configuration file.

.. code-block:: ini

    [neutron]
    region_name = RegionOne
    auth_strategy = keystone
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    password = password
    username = neutron
    auth_url = http://10.0.110.85/identity
    auth_type = password
    service_metadata_proxy = True
    default_floating_pool = public

You may also wish to configure a service user. As discussed in the `Keystone
documentation`__, service users are users with specific roles that identify the
user as a service. The use of service users can avoid issues caused by the
expiration of the original user's token during long running operations, as a
fresh token issued for the service user will always accompany the user's token,
which may have expired.

.. code-block:: python

    from keystoneauth1 import loading as ks_loading
    from keystoneauth1 import service_token
    from oslo_config import cfg
    import openstack
    from openstack import connection

    CONF = cfg.CONF

    neutron_group = cfg.OptGroup('neutron')
    ks_loading.register_session_conf_options(CONF, neutron_group)
    ks_loading.register_auth_conf_options(CONF, neutron_group)
    ks_loading.register_adapter_conf_options(CONF, neutron_group)

    service_group = cfg.OptGroup('service_user')
    ks_loading.register_session_conf_options(CONF, service_group)
    ks_loading.register_auth_conf_options(CONF, service_group)

    CONF()
    user_auth = ks_loading.load_auth_from_conf_options(CONF, 'neutron')
    service_auth = ks_loading.load_auth_from_conf_options(CONF, 'service_user')
    auth = service_token.ServiceTokenAuthWrapper(user_auth, service_auth)

    sess = ks_loading.load_session_from_conf_options(CONF, 'neutron', auth=auth)

    conn = connection.Connection(
        session=sess,
        oslo_conf=CONF,
    )

This will necessitate an additional section in the configuration file used.

.. code-block:: ini

    [service_user]
    auth_strategy = keystone
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    password = password
    username = nova
    auth_url = http://10.0.110.85/identity
    auth_type = password

.. __: https://docs.openstack.org/keystone/latest/admin/manage-services.html

From existing CloudRegion
~~~~~~~~~~~~~~~~~~~~~~~~~

If you already have an :class:`~openstack.config.cloud_region.CloudRegion`
you can pass it in instead:

.. code-block:: python

    from openstack import connection
    import openstack.config

    config = openstack.config.get_cloud_region(
        cloud='example',
        region_name='earth',
    )
    conn = connection.Connection(config=config)

Using the Connection
--------------------

Services are accessed through an attribute named after the service's official
service-type.

List
~~~~

An iterator containing a list of all the projects is retrieved in this manner:

.. code-block:: python

    projects = conn.identity.projects()

Find or create
~~~~~~~~~~~~~~

If you wanted to make sure you had a network named 'zuul', you would first
try to find it and if that fails, you would create it::

    network = conn.network.find_network("zuul")
    if network is None:
        network = conn.network.create_network(name="zuul")

Additional information about the services can be found in the
:ref:`service-proxies` documentation.
"""

import argparse
import concurrent.futures
import copy
import importlib.metadata as importlib_metadata
import typing as ty
import warnings

import keystoneauth1.exceptions
from keystoneauth1 import session as ks_session
import requestsexceptions
import typing_extensions as ty_ext

from openstack import _log
from openstack.cloud import _accelerator
from openstack.cloud import _baremetal
from openstack.cloud import _block_storage
from openstack.cloud import _coe
from openstack.cloud import _compute
from openstack.cloud import _dns
from openstack.cloud import _identity
from openstack.cloud import _image
from openstack.cloud import _network
from openstack.cloud import _object_store
from openstack.cloud import _orchestration
from openstack.cloud import _shared_file_system
from openstack import config as _config
import openstack.config.cloud_region
from openstack import exceptions
from openstack import service_description

if ty.TYPE_CHECKING:
    from oslo_config import cfg

    from openstack.config import cloud_region
    from openstack import proxy

__all__ = [
    'from_config',
    'Connection',
]

if requestsexceptions.SubjectAltNameWarning:
    warnings.filterwarnings(
        'ignore', category=requestsexceptions.SubjectAltNameWarning
    )

_logger = _log.setup_logging('openstack')


def from_config(
    cloud: ty.Optional[str] = None,
    config: ty.Optional['cloud_region.CloudRegion'] = None,
    options: ty.Optional[argparse.Namespace] = None,
    **kwargs: ty.Any,
) -> 'Connection':
    """Create a Connection using openstack.config

    :param str cloud:
        Use the `cloud` configuration details when creating the Connection.
    :param openstack.config.cloud_region.CloudRegion config:
        An existing CloudRegion configuration. If no `config` is provided,
        `openstack.config.OpenStackConfig` will be called, and the provided
        `name` will be used in determining which cloud's configuration
        details will be used in creation of the `Connection` instance.
    :param argparse.Namespace options:
        Allows direct passing in of options to be added to the cloud config.
        This does not have to be an actual instance of argparse.Namespace,
        despite the naming of the
        `openstack.config.loader.OpenStackConfig.get_one` argument to which
        it is passed.

    :rtype: :class:`~openstack.connection.Connection`
    """
    # TODO(mordred) Backwards compat while we transition
    cloud = kwargs.pop('cloud_name', cloud)
    config = kwargs.pop('cloud_config', config)
    if config is None:
        config = _config.OpenStackConfig().get_one(
            cloud=cloud, argparse=options, **kwargs
        )

    return Connection(config=config)


class Connection(
    _accelerator.AcceleratorCloudMixin,
    _baremetal.BaremetalCloudMixin,
    _block_storage.BlockStorageCloudMixin,
    _compute.ComputeCloudMixin,
    _coe.CoeCloudMixin,
    _dns.DnsCloudMixin,
    _identity.IdentityCloudMixin,
    _image.ImageCloudMixin,
    _network.NetworkCloudMixin,
    _object_store.ObjectStoreCloudMixin,
    _orchestration.OrchestrationCloudMixin,
    _shared_file_system.SharedFileSystemCloudMixin,
):
    def __init__(
        self,
        cloud: ty.Optional[str] = None,
        config: ty.Optional['cloud_region.CloudRegion'] = None,
        session: ty.Optional[ks_session.Session] = None,
        app_name: ty.Optional[str] = None,
        app_version: ty.Optional[str] = None,
        extra_services: ty.Optional[
            list[service_description.ServiceDescription]
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
        :param oslo_conf: An oslo.config ``CONF`` object that has been
            populated with
            ``keystoneauth1.loading.register_adapter_conf_options`` in
            groups named by the OpenStack service's project name.
        :type oslo_conf: :class:`~oslo_config.cfg.ConfigOpts`
        :param service_types:
            A list/set of service types this Connection should support. All
            other service types will be disabled (will error if used).
            **Currently only supported in conjunction with the ``oslo_conf``
            kwarg.**
        :param strict_proxies:
            Throw an ``openstack.exceptions.ServiceDiscoveryException`` if the
            endpoint for a given service doesn't work. This is useful for
            OpenStack services using sdk to talk to other OpenStack services
            where it can be expected that the deployer config is correct and
            errors should be reported immediately.
            Default false.
        :type strict_proxies: bool
        :param global_request_id: A Request-id to send with all interactions.
        :type global_request_id: str
        :param pool_executor:
            A futurist ``Executor`` object to be used for concurrent background
            activities. Defaults to None in which case a ThreadPoolExecutor
            will be created if needed.
        :type pool_executor: :class:`~futurist.Executor`
        :param kwargs: If a config is not provided, the rest of the parameters
            provided are assumed to be arguments to be passed to the
            CloudRegion constructor.
        """
        super().__init__(
            cloud=cloud,
            config=config,
            session=session,
            app_name=app_name,
            app_version=app_version,
            extra_services=extra_services,
            strict=strict,
            use_direct_get=use_direct_get,
            task_manager=task_manager,
            rate_limit=rate_limit,
            oslo_conf=oslo_conf,
            service_types=service_types,
            global_request_id=global_request_id,
            strict_proxies=strict_proxies,
            pool_executor=pool_executor,
            **kwargs,
        )

        # Allow vendors to provide hooks. They will normally only receive a
        # connection object and a responsible to register additional services
        vendor_hook = kwargs.get('vendor_hook')
        if not vendor_hook and 'vendor_hook' in self.config.config:
            # Get the one from profile
            vendor_hook = self.config.config.get('vendor_hook')
        if vendor_hook:
            try:
                # NOTE(gtema): no class name in the hook, plain module:function
                # Split string hook into module and function
                try:
                    package_name, function = vendor_hook.rsplit(':')

                    if package_name and function:
                        ep = importlib_metadata.EntryPoint(
                            name='vendor_hook',
                            value=vendor_hook,
                            group='vendor_hook',
                        )
                        hook = ep.load()
                        hook(self)
                except ValueError:
                    self.log.warning(
                        'Hook should be in the entrypoint '
                        'module:attribute format'
                    )
            except (ImportError, TypeError, AttributeError) as e:
                self.log.warning(
                    'Configured hook %s cannot be executed: %s', vendor_hook, e
                )

        # Add additional metrics into the configuration according to the
        # selected connection. We don't want to deal with overall config in the
        # proxy, just pass required part.
        if (
            self.config._influxdb_config
            and 'additional_metric_tags' in self.config.config
        ):
            self.config._influxdb_config['additional_metric_tags'] = (
                self.config.config['additional_metric_tags']
            )

    def add_service(
        self, service: service_description.ServiceDescription
    ) -> None:
        """Add a service to the Connection.

        Attaches an instance of the :class:`~openstack.proxy.Proxy`
        class contained in
        :class:`~openstack.service_description.ServiceDescription`.
        The :class:`~openstack.proxy.Proxy` will be attached to the
        `Connection` by its ``service_type`` and by any ``aliases`` that
        may be specified.

        :param openstack.service_description.ServiceDescription service:
            Object describing the service to be attached. As a convenience,
            if ``service`` is a string it will be treated as a ``service_type``
            and a basic
            :class:`~openstack.service_description.ServiceDescription`
            will be created.
        """
        # If we don't have a proxy, just instantiate Proxy so that
        # we get an adapter.
        if isinstance(service, str):
            service = service_description.ServiceDescription(service)

        # Directly invoke descriptor of the ServiceDescription
        def getter(self: 'Connection') -> 'proxy.Proxy':
            # TODO(stephenfin): Remove ignore once we have typed
            # ServiceDescription
            return service.__get__(self, service)  # type: ignore

        # Register the ServiceDescription class (as property)
        # with every known alias for a "runtime descriptor"
        for attr_name in service.all_types:
            setattr(
                self.__class__,
                attr_name.replace('-', '_'),
                property(fget=getter),
            )
        self.config.enable_service(service.service_type)

    def authorize(self) -> str:
        """Authorize this Connection

        .. note::

            This method is optional. When an application makes a call to any
            OpenStack service, this method allows you to request a token
            manually before attempting to do anything else.

        :returns: A string token.
        :raises: :class:`~openstack.exceptions.HttpException` if the
            authorization fails due to reasons like the credentials provided
            are unable to be authorized or the `auth_type` argument is missing,
            etc.
        """
        try:
            return ty.cast(str, self.session.get_token())
        except keystoneauth1.exceptions.ClientException as e:
            raise exceptions.SDKException(str(e))

    def connect_as(self, **kwargs: ty.Any) -> ty_ext.Self:
        """Make a new Connection object with new auth context.

        Take the existing settings from the current cloud and construct a new
        Connection object with some of the auth settings overridden. This
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
            normally go in an auth dict. They will override the same settings
            from the parent cloud as appropriate. Entries that do not want to
            be overridden can be ommitted.
        """

        if self.config._openstack_config:
            config = self.config._openstack_config
        else:
            # TODO(mordred) Replace this with from_session
            config = openstack.config.OpenStackConfig(
                app_name=self.config._app_name,
                app_version=self.config._app_version,
                load_yaml_config=False,
            )
        params = copy.deepcopy(self.config.config)
        # Remove profile from current cloud so that overridding works
        params.pop('profile', None)

        # Utility function to help with the stripping below.
        def pop_keys(
            params: dict[str, dict[str, ty.Optional[str]]],
            auth: dict[str, ty.Optional[str]],
            name_key: str,
            id_key: str,
        ) -> None:
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
            id_key = f'{prefix}_id'
            pop_keys(params, kwargs, name_key, id_key)
            id_key = f'{prefix}_domain_id'
            name_key = f'{prefix}_domain_name'
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

    def connect_as_project(self, project: str) -> ty_ext.Self:
        """Make a new Connection object with a new project.

        Take the existing settings from the current cloud and construct a new
        Connection object with the project settings overridden. This
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
            ``list_projects``.
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

    def endpoint_for(
        self,
        service_type: str,
        interface: ty.Optional[str] = None,
        region_name: ty.Optional[str] = None,
    ) -> ty.Optional[str]:
        """Return the endpoint for a given service.

        Respects config values for Connection, including
        ``*_endpoint_override``. For direct values from the catalog regardless
        of overrides, see
        :meth:`~openstack.config.cloud_region.CloudRegion.get_endpoint_from_catalog`

        :param service_type: Service Type of the endpoint to search for.
        :param interface: Interface of the endpoint to search for. Optional,
            defaults to the configured value for interface for this Connection.
        :param region_name: Region Name of the endpoint to search for.
            Optional, defaults to the configured value for region_name for this
            Connection.

        :returns: The endpoint of the service, or None if not found.
        """

        # FIXME(stephenfin): Why is self.config showing as Any?

        endpoint_override = self.config.get_endpoint(service_type)
        if endpoint_override:
            return endpoint_override  # type: ignore
        return self.config.get_endpoint_from_catalog(  # type: ignore
            service_type=service_type,
            interface=interface,
            region_name=region_name,
        )
