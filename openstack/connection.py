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

import os_client_config

from openstack import module_loader
from openstack import profile
from openstack import proxy
from openstack import session
from openstack import transport as xport
from openstack import utils

_logger = logging.getLogger(__name__)


def from_config(opts):
    """Create a connection from a configuration.

    Create a :class:`~openstack.connection.Connection` from a configuration
    similar to a os-client-config CloudConfig.

    :param opts: Options class like the argparse Namespace object.
    """

    # TODO(thowe): I proposed that service name defaults to None in OCC
    defaults = {}
    prof = profile.Profile()
    services = [service.service_type for service in prof.get_services()]
    for service in services:
        defaults[service + '_service_name'] = None
    # TODO(thowe): default is 2 which turns into v2 which doesn't work
    # this stuff needs to be fixed where we keep version and path separated.
    defaults['network_api_version'] = 'v2.0'

    # Get the cloud_config
    occ = os_client_config.OpenStackConfig(override_defaults=defaults)
    cloud_config = occ.get_one_cloud(opts.cloud, opts)

    if cloud_config.debug:
        utils.enable_logging(True, stream=sys.stdout)

    # TODO(mordred) we need to add service_type setting to openstacksdk.
    # Some clouds have type overridden as well as name.
    prof = profile.Profile()
    services = [service.service_type for service in prof.get_services()]
    for service in cloud_config.get_services():
        if service in services:
            version = cloud_config.get_api_version(service)
            if version:
                version = str(version)
                if not version.startswith("v"):
                    version = "v" + version
            prof.set_version(service, version)
            prof.set_name(service, cloud_config.get_service_name(service))
            prof.set_visibility(
                service, cloud_config.get_endpoint_type(service))
            prof.set_region(service, cloud_config.get_region_name(service))

    # Auth
    auth = cloud_config.config['auth']
    # TODO(thowe) We should be using auth_type
    auth['auth_plugin'] = cloud_config.config['auth_type']
    if 'cacert' in cloud_config.config:
        auth['verify'] = cloud_config.config['cacert']
    if 'insecure' in cloud_config.config:
        auth['verify'] = not bool(cloud_config.config['insecure'])

    return Connection(profile=prof, **auth)


class Connection(object):

    def __init__(self, transport=None, authenticator=None, profile=None,
                 verify=True, user_agent=None,
                 auth_plugin=None, **auth_args):
        """Create a context for a connection to a cloud provider.

        A connection needs a transport and an authenticator.  The user may pass
        in a transport and authenticator they want to use or they may pass in
        the parameters to create a transport and authenticator.  The connection
        creates a
        :class:`~openstack.session.Session` which uses the transport
        and authenticator to perform HTTP requests.

        :param transport: A transport object such as that was previously
            created.  If this parameter is not passed in, the connection will
            create a transport.
        :type transport: :class:`~openstack.transport.Transport`
        :param authenticator: An authenticator derived from the base
            authenticator plugin that was previously created.  Two common
            authentication identity plugins are
            :class:`identity_v2 <openstack.auth.identity.v2.Auth>` and
            :class:`identity_v3 <openstack.auth.identity.v3.Auth>`.
            If this parameter is not passed in, the connection will create an
            authenticator.
        :type authenticator: :class:`~openstack.auth.base.BaseAuthPlugin`
        :param profile: If the user has any special profiles such as the
            service name, region, version or visibility, they may be provided
            in the profile object.  If no profiles are provided, the
            services that appear first in the service catalog will be used.
        :type profile: :class:`~openstack.profile.Profile`
        :param bool verify: If a transport is not provided to the connection,
            this parameter will be used to create a transport.  If ``verify``
            is set to true, which is the default, the SSL cert will be
            verified.  It can also be set to a CA_BUNDLE path.
        :param str user_agent: If a transport is not provided to the
            connection, this parameter will be used when creating a transport.
            The value given here will be prepended to the default, which is
            specified in :attr:`~openstack.transport.USER_AGENT`.
            The resulting ``user_agent`` value is used for the ``User-Agent``
            HTTP header.
        :param str auth_plugin: The name of authentication plugin to use.  If
            the authentication plugin name is not provided, the connection will
            try to guess what plugin to use based on the *auth_url* in the
            *auth_args*.  Two common values for the plugin would be
            ``v3password`` and ``v3token``.
        :param auth_args: The rest of the parameters provided are assumed to be
            authentication arguments that are used by the authentication
            plugin.
        """
        self.transport = self._create_transport(transport, verify, user_agent)
        self.authenticator = self._create_authenticator(authenticator,
                                                        auth_plugin,
                                                        **auth_args)
        self.session = session.Session(self.transport, self.authenticator,
                                       profile)
        self._open()

    def _create_transport(self, transport, verify, user_agent):
        if transport:
            return transport
        return xport.Transport(verify=verify, user_agent=user_agent)

    def _create_authenticator(self, authenticator, auth_plugin, **auth_args):
        if authenticator:
            return authenticator
        plugin = module_loader.ModuleLoader().get_auth_plugin(auth_plugin)
        valid_list = plugin.valid_options
        args = dict((n, auth_args[n]) for n in valid_list if n in auth_args)
        return plugin(**args)

    def _open(self):
        """Open the connection.

        NOTE(thowe): Have this set up some lazy loader instead.
        """
        for service in self.session.get_services():
            self._load(service)

    def _load(self, service):
        attr_name = service.get_service_module()
        module = service.get_module() + "._proxy"
        try:
            __import__(module)
            proxy_class = getattr(sys.modules[module], "Proxy")
            if not issubclass(proxy_class, proxy.BaseProxy):
                raise TypeError("%s.Proxy must inherit from BaseProxy" %
                                proxy_class.__module__)
            setattr(self, attr_name, proxy_class(self.session))
        except Exception as e:
            _logger.warn("Unable to load %s: %s" % (module, e))

    def create(self, obj):
        """Create an object.

        :param obj: A resource object.
        :type resource: :class:`~openstack.resource.Resource`
        """
        obj.create(self.session)
        return obj

    def get(self, obj, include_headers=False):
        """Get an object.

        :param obj: A resource object.
        :type resource: :class:`~openstack.resource.Resource`
        :param bool include_headers: Read object headers.
        """
        obj.get(self.session, include_headers)
        return obj

    def head(self, obj):
        """Get an object.

        :param obj: A resource object.
        :type resource: :class:`~openstack.resource.Resource`
        """
        obj.head(self.session)
        return obj

    def update(self, obj):
        """Update an object.

        :param obj: A resource object.
        :type resource: :class:`~openstack.resource.Resource`
        """
        obj.update(self.session)
        return obj

    def delete(self, obj):
        """Delete an object.

        :param obj: A resource object.
        :type resource: :class:`~openstack.resource.Resource`
        """
        obj.delete(self.session)
