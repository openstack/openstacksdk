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

    projects = [project for project in conn.identity.projects()]

Find or create
~~~~~~~~~~~~~~
If you wanted to make sure you had a network named 'zuul', you would first
try to find it and if that fails, you would create it::

    network = conn.network.find_network("zuul")
    if network is None:
        network = conn.network.create_network({"name": "zuul"})

"""
__all__ = [
    'from_config',
    'Connection',
]

import warnings

import keystoneauth1.exceptions
import os_service_types
import requestsexceptions
import six

from openstack import _log
from openstack import config as _config
from openstack import exceptions
from openstack import service_description
from openstack import task_manager

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
        despite the naming of the the
        `openstack.config.loader.OpenStackConfig.get_one` argument to which
        it is passed.

    :rtype: :class:`~openstack.connection.Connection`
    """
    # TODO(mordred) Backwards compat while we transition
    cloud = cloud or kwargs.get('cloud_name')
    config = config or kwargs.get('cloud_config')
    if config is None:
        config = _config.OpenStackConfig().get_one(
            cloud=cloud, argparse=options)

    return Connection(config=config)


class Connection(object):

    def __init__(self, cloud=None, config=None, session=None,
                 app_name=None, app_version=None,
                 # TODO(shade) Remove these once we've shifted
                 # python-openstackclient to not use the profile interface.
                 authenticator=None, profile=None,
                 extra_services=None,
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
                              transition. See `Transition from Profile`_ for
                              details.
        :param profile: DEPRECATED. Only exists for short-term backwards
                        compatibility for python-openstackclient while we
                        transition. See `Transition from Profile`_ for details.
        :param extra_services: List of
            :class:`~openstack.service_description.ServiceDescription`
            objects describing services that openstacksdk otherwise does not
            know about.
        :param kwargs: If a config is not provided, the rest of the parameters
            provided are assumed to be arguments to be passed to the
            CloudRegion contructor.
        """
        self.config = config
        self._extra_services = {}
        if extra_services:
            for service in extra_services:
                self._extra_services[service.service_type] = service

        if not self.config:
            if profile:
                import openstack.profile
                # TODO(shade) Remove this once we've shifted
                # python-openstackclient to not use the profile interface.
                self.config = openstack.profile._get_config_from_profile(
                    profile, authenticator, **kwargs)
            else:
                openstack_config = _config.OpenStackConfig(
                    app_name=app_name, app_version=app_version,
                    load_yaml_config=profile is None)
                self.config = openstack_config.get_one(
                    cloud=cloud, validate=session is None, **kwargs)

        if self.config.name:
            tm_name = ':'.join([
                self.config.name,
                self.config.region_name or 'unknown'])
        else:
            tm_name = self.config.region_name or 'unknown'

        self.task_manager = task_manager.TaskManager(name=tm_name)

        if session:
            # TODO(mordred) Expose constructor option for this in OCC
            self.config._keystone_session = session

        self.session = self.config.get_session()
        # Hide a reference to the connection on the session to help with
        # backwards compatibility for folks trying to just pass conn.session
        # to a Resource method's session argument.
        self.session._sdk_connection = self

        service_type_manager = os_service_types.ServiceTypes()
        for service in service_type_manager.services:
            self.add_service(
                service_description.OpenStackServiceDescription(
                    service, self.config))

    def add_service(self, service):
        """Add a service to the Connection.

        Attaches an instance of the :class:`~openstack.proxy.BaseProxy`
        class contained in
        :class:`~openstack.service_description.ServiceDescription`.
        The :class:`~openstack.proxy.BaseProxy` will be attached to the
        `Connection` by its ``service_type`` and by any ``aliases`` that
        may be specified.

        :param openstack.service_description.ServiceDescription service:
            Object describing the service to be attached. As a convenience,
            if ``service`` is a string it will be treated as a ``service_type``
            and a basic
            :class:`~openstack.service_description.ServiceDescription`
            will be created.
        """
        # If we don't have a proxy, just instantiate BaseProxy so that
        # we get an adapter.
        if isinstance(service, six.string_types):
            service_type = service
            service = service_description.ServiceDescription(service_type)
        else:
            service_type = service.service_type
        proxy_object = service.proxy_class(
            session=self.config.get_session(),
            task_manager=self.task_manager,
            allow_version_hack=True,
            service_type=self.config.get_service_type(service_type),
            service_name=self.config.get_service_name(service_type),
            interface=self.config.get_interface(service_type),
            region_name=self.config.region_name,
            version=self.config.get_api_version(service_type),
        )

        # Register the proxy class with every known alias
        for attr_name in service.all_types:
            setattr(self, attr_name.replace('-', '_'), proxy_object)

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
