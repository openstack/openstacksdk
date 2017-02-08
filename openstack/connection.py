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
The connection has an attribute to access each supported service.  The service
attributes are created dynamically based on user profiles and the service
catalog.

Examples
--------

At a minimum, the :class:`~openstack.connection.Connection` class needs to be
created with an authenticator or the parameters to build one.

Create a connection
~~~~~~~~~~~~~~~~~~~

The following example constructor uses the identity authenticator using
username and password.  The default settings for the transport are used
by this connection.::

    from openstack import connection
    auth_args = {
        'auth_url': 'http://172.20.1.108:5000/v3',
        'project_name': 'admin',
        'username': 'admin',
        'password': 'admin',
    }
    conn = connection.Connection(**auth_args)

List
~~~~

Services are accessed through an attribute named after the service.  A list
of all the projects is retrieved in this manner::

    projects = conn.identity.list_projects()

Find or create
~~~~~~~~~~~~~~
If you wanted to make sure you had a network named 'jenkins', you would first
try to find it and if that fails, you would create it::

    network = conn.network.find_network("jenkins")
    if network is None:
        network = conn.network.create_network({"name": "jenkins"})

"""
import logging
import sys

from keystoneauth1.loading import base as ksa_loader
import os_client_config

from openstack import exceptions
from openstack import profile as _profile
from openstack import proxy
from openstack import proxy2
from openstack import session as _session
from openstack import utils

_logger = logging.getLogger(__name__)


def from_config(cloud_name=None, cloud_config=None, options=None):
    """Create a Connection using os-client-config

    :param str cloud_name: Use the `cloud_name` configuration details when
                           creating the Connection instance.
    :param cloud_config: An instance of
                         `os_client_config.config.OpenStackConfig`
                         as returned from the os-client-config library.
                         If no `config` is provided,
                         `os_client_config.OpenStackConfig` will be called,
                         and the provided `cloud_name` will be used in
                         determining which cloud's configuration details
                         will be used in creation of the
                         `Connection` instance.
    :param options: A namespace object; allows direct passing in of options to
                    be added to the cloud config. This does not have to be an
                    instance of argparse.Namespace, despite the naming of the
                    the `os_client_config.config.OpenStackConfig.get_one_cloud`
                    argument to which it is passed.

    :rtype: :class:`~openstack.connection.Connection`
    """
    # TODO(thowe): I proposed that service name defaults to None in OCC
    defaults = {}
    prof = _profile.Profile()
    services = [service.service_type for service in prof.get_services()]
    for service in services:
        defaults[service + '_service_name'] = None
    # TODO(thowe): default is 2 which turns into v2 which doesn't work
    # this stuff needs to be fixed where we keep version and path separated.
    defaults['network_api_version'] = 'v2.0'
    if cloud_config is None:
        occ = os_client_config.OpenStackConfig(override_defaults=defaults)
        cloud_config = occ.get_one_cloud(cloud=cloud_name, argparse=options)

    if cloud_config.debug:
        utils.enable_logging(True, stream=sys.stdout)

    # TODO(mordred) we need to add service_type setting to openstacksdk.
    # Some clouds have type overridden as well as name.
    services = [service.service_type for service in prof.get_services()]
    for service in cloud_config.get_services():
        if service in services:
            version = cloud_config.get_api_version(service)
            if version:
                version = str(version)
                if not version.startswith("v"):
                    version = "v" + version
                prof.set_version(service, version)
            name = cloud_config.get_service_name(service)
            if name:
                prof.set_name(service, name)
            interface = cloud_config.get_interface(service)
            if interface:
                prof.set_interface(service, interface)

    region = cloud_config.get_region_name(service)
    if region:
        for service in services:
            prof.set_region(service, region)

    # Auth
    auth = cloud_config.config['auth']
    # TODO(thowe) We should be using auth_type
    auth['auth_plugin'] = cloud_config.config['auth_type']
    if 'cacert' in auth:
        auth['verify'] = auth.pop('cacert')
    if 'cacert' in cloud_config.config:
        auth['verify'] = cloud_config.config['cacert']
    insecure = cloud_config.config.get('insecure', False)
    if insecure:
        auth['verify'] = False

    cert = cloud_config.config.get('cert')
    if cert:
        key = cloud_config.config.get('key')
        auth['cert'] = (cert, key) if key else cert

    return Connection(profile=prof, **auth)


class Connection(object):

    def __init__(self, session=None, authenticator=None, profile=None,
                 verify=True, cert=None, user_agent=None,
                 auth_plugin="password",
                 **auth_args):
        """Create a context for a connection to a cloud provider.

        A connection needs a transport and an authenticator.  The user may pass
        in a transport and authenticator they want to use or they may pass in
        the parameters to create a transport and authenticator.  The connection
        creates a
        :class:`~openstack.session.Session` which uses the profile
        and authenticator to perform HTTP requests.

        :param session: A session object compatible with
            :class:`~openstack.session.Session`.
        :type session: :class:`~openstack.session.Session`
        :param authenticator: An authenticator derived from the base
            authenticator plugin that was previously created.  Two common
            authentication identity plugins are
            :class:`identity_v2 <openstack.auth.identity.v2.Auth>` and
            :class:`identity_v3 <openstack.auth.identity.v3.Auth>`.
            If this parameter is not passed in, the connection will create an
            authenticator.
        :type authenticator: :class:`~openstack.auth.base.BaseAuthPlugin`
        :param profile: If the user has any special profiles such as the
            service name, region, version or interface, they may be provided
            in the profile object.  If no profiles are provided, the
            services that appear first in the service catalog will be used.
        :type profile: :class:`~openstack.profile.Profile`
        :param bool verify: If a transport is not provided to the connection,
            this parameter will be used to create a transport.  If ``verify``
            is set to true, which is the default, the SSL cert will be
            verified.  It can also be set to a CA_BUNDLE path.
        :param cert: If a transport is not provided to the connection then this
            parameter will be used to create a transport. `cert` allows to
            provide a client certificate file path or a tuple with client
            certificate and key paths.
        :type cert: str or tuple
        :param str user_agent: If a transport is not provided to the
            connection, this parameter will be used when creating a transport.
            The value given here will be prepended to the default, which is
            specified in :attr:`~openstack.transport.USER_AGENT`.
            The resulting ``user_agent`` value is used for the ``User-Agent``
            HTTP header.
        :param str auth_plugin: The name of authentication plugin to use.
            The default value is ``password``.
        :param auth_args: The rest of the parameters provided are assumed to be
            authentication arguments that are used by the authentication
            plugin.
        """
        self.profile = profile if profile else _profile.Profile()
        if session:
            # Make sure it is the right kind of session. A keystoneauth1
            # session would work in some ways but show strange errors in
            # others. E.g. a Resource.find would work with an id but fail when
            # given a name because it attempts to catch
            # openstack.exceptions.NotFoundException to signal that a search by
            # ID failed before trying a search by name, but with a
            # keystoneauth1 session the lookup by ID raises
            # keystoneauth1.exceptions.NotFound instead. We need to ensure our
            # Session class gets used so that our implementation of various
            # methods always works as we expect.
            if not isinstance(session, _session.Session):
                raise exceptions.SDKException(
                    'Session instance is from %s but must be from %s' %
                    (session.__module__, _session.__name__))
            self.session = session
        else:
            self.authenticator = self._create_authenticator(authenticator,
                                                            auth_plugin,
                                                            **auth_args)
            self.session = _session.Session(
                self.profile, auth=self.authenticator, verify=verify,
                cert=cert, user_agent=user_agent)

        self._open()

    def _create_authenticator(self, authenticator, auth_plugin, **args):
        if authenticator:
            return authenticator
        # TODO(thowe): Jamie was suggesting we should support other
        #              ways of loading the plugin
        loader = ksa_loader.get_plugin_loader(auth_plugin)
        load_args = {}
        for opt in loader.get_options():
            if args.get(opt.dest):
                load_args[opt.dest] = args[opt.dest]
        return loader.load_from_options(**load_args)

    def _open(self):
        """Open the connection.

        NOTE(thowe): Have this set up some lazy loader instead.
        """
        for service in self.profile.get_services():
            self._load(service)

    def _load(self, service):
        attr_name = service.get_service_module()
        module = service.get_module() + "._proxy"
        try:
            __import__(module)
            proxy_class = getattr(sys.modules[module], "Proxy")
            if not (issubclass(proxy_class, proxy.BaseProxy) or
                    issubclass(proxy_class, proxy2.BaseProxy)):
                raise TypeError("%s.Proxy must inherit from BaseProxy" %
                                proxy_class.__module__)
            setattr(self, attr_name, proxy_class(self.session))
        except Exception as e:
            _logger.warn("Unable to load %s: %s" % (module, e))

    def authorize(self):
        """Authorize this Connection

        **NOTE**: This method is optional. When an application makes a call
                  to any OpenStack service, this method allows you to request
                  a token manually before attempting to do anything else.

        :returns: A string token.

        :raises: :class:`~openstack.exceptions.HttpException` if the
                 authorization fails due to reasons like the credentials
                 provided are unable to be authorized or the `auth_plugin`
                 argument is missing, etc.
        """
        headers = self.session.get_auth_headers()

        return headers.get('X-Auth-Token') if headers else None
