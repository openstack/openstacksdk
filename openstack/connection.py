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

Using config settings
---------------------

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

Using Only Keyword Arguments
----------------------------

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
        auth=dict(
            auth_url='https://auth.example.com',
            username='amazing-user',
            password='super-secret-password',
            project_id='33aa1afc-03fe-43b8-8201-4e0d3b4b8ab5',
            user_domain_id='054abd68-9ad9-418b-96d3-3437bb376703'),
        compute_api_version='2',
        identity_interface='internal')

Per-service settings as needed by `keystoneauth1.adapter.Adapter` such as
``api_version``, ``service_name``, and ``interface`` can be set, as seen
above, by prefixing them with the official ``service-type`` name of the
service. ``region_name`` is a setting for the entire
:class:`~openstack.config.cloud_region.CloudRegion` and cannot be set per
service.

From existing authenticated Session
-----------------------------------

For applications that already have an authenticated Session, simply passing
it to the :class:`~openstack.connection.Connection` constructor is all that
is needed:

.. code-block:: python

    from openstack import connection

    conn = connection.Connection(
        session=session,
        region_name='example-region',
        compute_api_version='2',
        identity_interface='internal')

From oslo.conf CONF object
--------------------------

For applications that have an oslo.config ``CONF`` object that has been
populated with ``keystoneauth1.loading.register_adapter_conf_options`` in
groups named by the OpenStack service's project name, it is possible to
construct a Connection with the ``CONF`` object and an authenticated Session.

.. note::

    This is primarily intended for use by OpenStack services to talk amongst
    themselves.

.. code-block:: python

    from openstack import connection

    conn = connection.Connection(
        session=session,
        oslo_conf=CONF)

From existing CloudRegion
-------------------------

If you already have an :class:`~openstack.config.cloud_region.CloudRegion`
you can pass it in instead:

.. code-block:: python

    from openstack import connection
    import openstack.config

    config = openstack.config.get_cloud_region(
        cloud='example', region_name='earth')
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
import warnings
import weakref

try:
    # For python 3.8 and later
    import importlib.metadata as importlib_metadata
except ImportError:
    # For everyone else
    import importlib_metadata

import concurrent.futures
import keystoneauth1.exceptions
import requestsexceptions

from openstack import _log
from openstack import _services_mixin
from openstack.cloud import openstackcloud as _cloud
from openstack.cloud import _accelerator
from openstack.cloud import _baremetal
from openstack.cloud import _block_storage
from openstack.cloud import _compute
from openstack.cloud import _clustering
from openstack.cloud import _coe
from openstack.cloud import _dns
from openstack.cloud import _floating_ip
from openstack.cloud import _identity
from openstack.cloud import _image
from openstack.cloud import _network
from openstack.cloud import _network_common
from openstack.cloud import _object_store
from openstack.cloud import _orchestration
from openstack.cloud import _security_group
from openstack import config as _config
from openstack.config import cloud_region
from openstack import exceptions
from openstack import service_description

__all__ = [
    'from_config',
    'Connection',
]

if requestsexceptions.SubjectAltNameWarning:
    warnings.filterwarnings(
        'ignore', category=requestsexceptions.SubjectAltNameWarning)

_logger = _log.setup_logging('openstack')


def from_config(cloud=None, config=None, options=None, **kwargs):
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
            cloud=cloud, argparse=options, **kwargs)

    return Connection(config=config)


class Connection(
    _services_mixin.ServicesMixin,
    _cloud._OpenStackCloudMixin,
    _accelerator.AcceleratorCloudMixin,
    _baremetal.BaremetalCloudMixin,
    _block_storage.BlockStorageCloudMixin,
    _compute.ComputeCloudMixin,
    _clustering.ClusteringCloudMixin,
    _coe.CoeCloudMixin,
    _dns.DnsCloudMixin,
    _floating_ip.FloatingIPCloudMixin,
    _identity.IdentityCloudMixin,
    _image.ImageCloudMixin,
    _network.NetworkCloudMixin,
    _network_common.NetworkCommonCloudMixin,
    _object_store.ObjectStoreCloudMixin,
    _orchestration.OrchestrationCloudMixin,
    _security_group.SecurityGroupCloudMixin
):

    def __init__(self, cloud=None, config=None, session=None,
                 app_name=None, app_version=None,
                 extra_services=None,
                 strict=False,
                 use_direct_get=False,
                 task_manager=None,
                 rate_limit=None,
                 oslo_conf=None,
                 service_types=None,
                 global_request_id=None,
                 strict_proxies=False,
                 pool_executor=None,
                 **kwargs):
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
        self.config = config
        self._extra_services = {}
        self._strict_proxies = strict_proxies
        if extra_services:
            for service in extra_services:
                self._extra_services[service.service_type] = service

        if not self.config:
            if oslo_conf:
                self.config = cloud_region.from_conf(
                    oslo_conf, session=session, app_name=app_name,
                    app_version=app_version, service_types=service_types)
            elif session:
                self.config = cloud_region.from_session(
                    session=session,
                    app_name=app_name, app_version=app_version,
                    load_yaml_config=False,
                    load_envvars=False,
                    rate_limit=rate_limit,
                    **kwargs)
            else:
                self.config = _config.get_cloud_region(
                    cloud=cloud,
                    app_name=app_name, app_version=app_version,
                    load_yaml_config=cloud is not None,
                    load_envvars=cloud is not None,
                    rate_limit=rate_limit,
                    **kwargs)

        self._session = None
        self._proxies = {}
        self.__pool_executor = pool_executor
        self._global_request_id = global_request_id
        self.use_direct_get = use_direct_get
        self.strict_mode = strict
        # Call the _*CloudMixin constructors while we work on
        # integrating things better.
        _cloud._OpenStackCloudMixin.__init__(self)
        _accelerator.AcceleratorCloudMixin.__init__(self)
        _baremetal.BaremetalCloudMixin.__init__(self)
        _block_storage.BlockStorageCloudMixin.__init__(self)
        _clustering.ClusteringCloudMixin.__init__(self)
        _coe.CoeCloudMixin.__init__(self)
        _compute.ComputeCloudMixin.__init__(self)
        _dns.DnsCloudMixin.__init__(self)
        _floating_ip.FloatingIPCloudMixin.__init__(self)
        _identity.IdentityCloudMixin.__init__(self)
        _image.ImageCloudMixin.__init__(self)
        _network_common.NetworkCommonCloudMixin.__init__(self)
        _network.NetworkCloudMixin.__init__(self)
        _object_store.ObjectStoreCloudMixin.__init__(self)
        _orchestration.OrchestrationCloudMixin.__init__(self)
        _security_group.SecurityGroupCloudMixin.__init__(self)

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
                    (package_name, function) = vendor_hook.rsplit(':')

                    if package_name and function:
                        ep = importlib_metadata.EntryPoint(
                            name='vendor_hook',
                            value=vendor_hook,
                            group='vendor_hook',
                        )
                        hook = ep.load()
                        hook(self)
                except ValueError:
                    self.log.warning('Hook should be in the entrypoint '
                                     'module:attribute format')
            except (ImportError, TypeError, AttributeError) as e:
                self.log.warning('Configured hook %s cannot be executed: %s',
                                 vendor_hook, e)

        # Add additional metrics into the configuration according to the
        # selected connection. We don't want to deal with overall config in the
        # proxy, just pass required part.
        if (self.config._influxdb_config
                and 'additional_metric_tags' in self.config.config):
            self.config._influxdb_config['additional_metric_tags'] = \
                self.config.config['additional_metric_tags']

    @property
    def session(self):
        if not self._session:
            self._session = self.config.get_session()
            # Hide a reference to the connection on the session to help with
            # backwards compatibility for folks trying to just pass
            # conn.session to a Resource method's session argument.
            self.session._sdk_connection = weakref.proxy(self)
        return self._session

    def add_service(self, service):
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
        def getter(self):
            return service.__get__(self, service)

        # Register the ServiceDescription class (as property)
        # with every known alias for a "runtime descriptor"
        for attr_name in service.all_types:
            setattr(
                self.__class__,
                attr_name.replace('-', '_'),
                property(fget=getter)
            )
        self.config.enable_service(service.service_type)

    def authorize(self):
        """Authorize this Connection

        .. note:: This method is optional. When an application makes a call
                  to any OpenStack service, this method allows you to request
                  a token manually before attempting to do anything else.

        :returns: A string token.

        :raises: :class:`~openstack.exceptions.HttpException` if the
                 authorization fails due to reasons like the credentials
                 provided are unable to be authorized or the `auth_type`
                 argument is missing, etc.
        """
        try:
            return self.session.get_token()
        except keystoneauth1.exceptions.ClientException as e:
            raise exceptions.SDKException(e)

    @property
    def _pool_executor(self):
        if not self.__pool_executor:
            self.__pool_executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=5)
        return self.__pool_executor

    def close(self):
        """Release any resources held open."""
        if self.__pool_executor:
            self.__pool_executor.shutdown()

    def set_global_request_id(self, global_request_id):
        self._global_request_id = global_request_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
