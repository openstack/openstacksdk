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
attributes are created dynamically based on user preferences and the service
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
        'user_name': 'admin',
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

    try:
        network = conn.network.find_network("jenkins")
    except exceptions.ResourceNotFound:
        network = conn.network.create_network({"name": "jenkins"})

"""
import logging
import sys

from stevedore import driver

from openstack import exceptions
from openstack import session
from openstack import transport as xport


USER_AGENT = 'OSPythonSDK'
"""Default value for the HTTP User-Agent header"""
_logger = logging.getLogger(__name__)


class Connection(object):

    AUTH_PLUGIN_NAMESPACE = "openstack.auth.plugin"
    """Namespace for the authorization plugin entry point"""

    def __init__(self, transport=None, authenticator=None, preference=None,
                 verify=True, user_agent=USER_AGENT,
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
        :param preference: If the user has any special preferences such as the
            service name, region, version or visibility, they may be provided
            in the preference object.  If no preferences are provided, the
            services that appear first in the service catalog will be used.
        :type preference: :class:`~openstack.user_preference.UserPreference`
        :param bool verify: If a transport is not provided to the connection,
            this parameter will be used to create a transport.  If ``verify``
            is set to true, which is the default, the SSL cert will be
            verified.  It can also be set to a CA_BUNDLE path.
        :param str user_agent: If a transport is not provided to the
            connection, this parameter will be used to create a transport.
            The value of this parameter is used for the ``User-Agent`` HTTP
            header. The default value is the module level attribute
            ``USER_AGENT`` which is set to ``"OSPythonSDK"``.
        :param str auth_plugin: The name of authentication plugin to use.  If
            the authentication plugin name is not provided, the connection will
            try to guess what plugin to use based on the *auth_url* in the
            *auth_args*.  Two common values for the plugin would be
            ``identityv2`` and ``identityv3``.
        :param auth_args: The rest of the parameters provided are assumed to be
            authentication arguments that are used by the authentication
            plugin.
        """
        self.transport = self._create_transport(transport, verify, user_agent)
        self.authenticator = self._create_authenticator(authenticator,
                                                        auth_plugin,
                                                        **auth_args)
        self.session = session.Session(self.transport, self.authenticator,
                                       preference)
        self._open()

    def _create_transport(self, transport, verify, user_agent):
        if transport:
            return transport
        return xport.Transport(verify=verify, user_agent=user_agent)

    def _create_authenticator(self, authenticator, auth_plugin, **auth_args):
        if authenticator:
            return authenticator
        if auth_plugin is None:
            if 'auth_url' not in auth_args:
                msg = ("auth_url was not provided.")
                raise exceptions.AuthorizationFailure(msg)
            auth_url = auth_args['auth_url']
            endpoint_version = auth_url.split('v')[-1][0]
            if endpoint_version == '2':
                auth_plugin = 'identity_v2'
            else:
                auth_plugin = 'identity_v3'

        mgr = driver.DriverManager(
            namespace=self.AUTH_PLUGIN_NAMESPACE,
            name=auth_plugin,
            invoke_on_load=False,
        )
        plugin = mgr.driver
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
            proxy = getattr(sys.modules[module], "Proxy")
            setattr(self, attr_name, proxy(self.session))
        except Exception as e:
            _logger.warn("Unable to load %s: %s" % (module, e))
