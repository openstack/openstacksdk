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
to the Python SDK it maintains a context for a connection to a cloud provider.
The connection has an attribute to access each supported service.

Examples
--------

At a minimum, the :class:`~openstack.connection.Connection` class needs to be
created with a config or the parameters to build one.

Create a connection
~~~~~~~~~~~~~~~~~~~

The preferred way to create a connection is to manage named configuration
settings in your clouds.yaml file and refer to them by name.::

    from openstack import connection

    conn = connection.Connection(cloud='example', region_name='earth1')

If you already have an :class:`~openstack.config.cloud_region.CloudRegion`
you can pass it in instead.::

    from openstack import connection
    import openstack.config

    config = openstack.config.OpenStackConfig.get_one(
        cloud='example', region_name='earth')
    conn = connection.Connection(config=config)

It's also possible to pass in parameters directly if needed. The following
example constructor uses the default identity password auth
plugin and provides a username and password.::

    from openstack import connection
    auth_args = {
        'auth_url': 'http://172.20.1.108:5000/v3',
        'project_name': 'admin',
        'user_domain_name': 'default',
        'project_domain_name': 'default',
        'username': 'admin',
        'password': 'admin',
    }
    conn = connection.Connection(**auth_args)

List
~~~~

Services are accessed through an attribute named after the service's official
service-type. A list of all the projects is retrieved in this manner::

    projects = conn.identity.list_projects()

Find or create
~~~~~~~~~~~~~~
If you wanted to make sure you had a network named 'zuul', you would first
try to find it and if that fails, you would create it::

    network = conn.network.find_network("zuul")
    if network is None:
        network = conn.network.create_network({"name": "zuul"})

"""
import importlib
import logging
import sys

import keystoneauth1.exceptions
import os_service_types
from six.moves import urllib

import openstack.config
from openstack.config import cloud_region
from openstack import exceptions
from openstack import proxy
from openstack import proxy2
from openstack import task_manager
from openstack import utils

_logger = logging.getLogger(__name__)


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
        despite the naming of the the
        `openstack.config.loader.OpenStackConfig.get_one` argument to which
        it is passed.

    :rtype: :class:`~openstack.connection.Connection`
    """
    # TODO(mordred) Backwards compat while we transition
    cloud = cloud or kwargs.get('cloud_name')
    config = config or kwargs.get('cloud_config')
    if config is None:
        config = openstack.config.OpenStackConfig().get_one(
            cloud=cloud, argparse=options)

    if config.debug:
        utils.enable_logging(True, stream=sys.stdout)

    return Connection(config=config)


class Connection(object):

    def __init__(self, cloud=None, config=None, session=None,
                 app_name=None, app_version=None,
                 # TODO(shade) Remove these once we've shifted
                 # python-openstackclient to not use the profile interface.
                 authenticator=None, profile=None,
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
        :param authenticator: DEPRECATED. Only exists for short-term backwards
                              compatibility for python-openstackclient while we
                              transition.
        :param profile: DEPRECATED. Only exists for short-term backwards
                        compatibility for python-openstackclient while we
                        transition.
        :param kwargs: If a config is not provided, the rest of the parameters
            provided are assumed to be arguments to be passed to the
            CloudRegion contructor.
        """
        self.config = config
        self.service_type_manager = os_service_types.ServiceTypes()

        if not self.config:
            if profile:
                # TODO(shade) Remove this once we've shifted
                # python-openstackclient to not use the profile interface.
                self.config = self._get_config_from_profile(
                    profile, authenticator, **kwargs)
            else:
                openstack_config = openstack.config.OpenStackConfig(
                    app_name=app_name, app_version=app_version,
                    load_yaml_config=profile is None)
                self.config = openstack_config.get_one(
                    cloud=cloud, validate=session is None, **kwargs)

        self.task_manager = task_manager.TaskManager(
            name=':'.join([self.config.name, self.config.region]))

        if session:
            # TODO(mordred) Expose constructor option for this in OCC
            self.config._keystone_session = session

        self.session = self.config.get_session()

        self._open()

    def _get_config_from_profile(self, profile, authenticator, **kwargs):
        """Get openstack.config objects from legacy profile."""
        # TODO(shade) Remove this once we've shifted python-openstackclient
        # to not use the profile interface.

        # We don't have a cloud name. Make one up from the auth_url hostname
        # so that log messages work.
        name = urllib.parse.urlparse(authenticator.auth_url).hostname
        region_name = None
        for service in profile.get_services():
            if service.region:
                region_name = service.region
            service_type = service.service_type
            if service.interface:
                key = cloud_region._make_key('interface', service_type)
                kwargs[key] = service.interface
            if service.version:
                version = service.version
                if version.startswith('v'):
                    version = version[1:]
                key = cloud_region._make_key('api_version', service_type)
                kwargs[key] = service.version

        config = cloud_region.CloudRegion(
            name=name, region=region_name, config=kwargs)
        config._auth = authenticator

    def _open(self):
        """Open the connection. """
        for service in self.service_type_manager.services:
            self._load(service['service_type'])
        # TODO(mordred) openstacksdk has support for the metric service
        # which is not in service-types-authority. What do we do about that?
        self._load('metric')

    def _load(self, service_type):
        service = self._get_service(service_type)

        if service:
            module_name = service.get_module() + "._proxy"
            module = importlib.import_module(module_name)
            proxy_class = getattr(module, "Proxy")
            if not (issubclass(proxy_class, proxy.BaseProxy) or
                    issubclass(proxy_class, proxy2.BaseProxy)):
                raise TypeError("%s.Proxy must inherit from BaseProxy" %
                                proxy_class.__module__)
        else:
            # If we don't have a proxy, just instantiate BaseProxy so that
            # we get an adapter.
            proxy_class = proxy2.BaseProxy

        proxy_object = proxy_class(
            session=self.config.get_session(),
            task_manager=self.task_manager,
            allow_version_hack=True,
            service_type=self.config.get_service_type(service_type),
            service_name=self.config.get_service_name(service_type),
            interface=self.config.get_interface(service_type),
            region_name=self.config.region,
            version=self.config.get_api_version(service_type)
        )
        all_types = self.service_type_manager.get_all_types(service_type)
        # Register the proxy class with every known alias
        for attr_name in [name.replace('-', '_') for name in all_types]:
            setattr(self, attr_name, proxy_object)

    def _get_all_types(self, service_type):
        # We make connection attributes for all official real type names
        # and aliases. Three services have names they were called by in
        # openstacksdk that are not covered by Service Types Authority aliases.
        # Include them here - but take heed, no additional values should ever
        # be added to this list.
        # that were only used in openstacksdk resource naming.
        LOCAL_ALIASES = {
            'baremetal': 'bare_metal',
            'block_storage': 'block_store',
            'clustering': 'cluster',
        }
        all_types = self.service_type_manager.get_all_types(service_type)
        if service_type in LOCAL_ALIASES:
            all_types.append(LOCAL_ALIASES[service_type])
        return all_types

    def _get_service(self, official_service_type):
        service_class = None
        for service_type in self._get_all_types(official_service_type):
            service_class = self._find_service_class(service_type)
            if service_class:
                break
        if not service_class:
            return None
        # TODO(mordred) Replace this with proper discovery
        version_string = self.config.get_api_version(official_service_type)
        version = None
        if version_string:
            version = 'v{version}'.format(version=version_string[0])
        return service_class(version=version)

    def _find_service_class(self, service_type):
        package_name = 'openstack.{service_type}'.format(
            service_type=service_type).replace('-', '_')
        module_name = service_type.replace('-', '_') + '_service'
        class_name = ''.join(
            [part.capitalize() for part in module_name.split('_')])
        try:
            import_name = '.'.join([package_name, module_name])
            service_module = importlib.import_module(import_name)
        except ImportError:
            return None
        service_class = getattr(service_module, class_name, None)
        if not service_class:
            _logger.warn(
                'Unable to find class {class_name} in module for service'
                ' for service {service_type}'.format(
                    class_name=class_name,
                    service_type=service_type))
            return None
        return service_class

    def authorize(self):
        """Authorize this Connection

        **NOTE**: This method is optional. When an application makes a call
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
            raise exceptions.raise_from_response(e.response)
