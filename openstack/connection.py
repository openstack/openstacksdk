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

from stevedore import driver

from openstack import exceptions
from openstack import session
from openstack import transport as xport

USER_AGENT = 'OSPythonSDK'


class Connection(object):
    AUTH_PLUGIN_NAMESPACE = "openstack.auth.plugin"

    def __init__(self, transport=None, authenticator=None, preference=None,
                 verify=True, user_agent=USER_AGENT,
                 auth_plugin=None, **auth_args):
        """Connection to a cloud provider.

        Context for a connection to a cloud provider.  The context generally
        contains a transport, authenticator, and sesssion.  You may pass in
        a previously created transport and authenticator or you may pass in
        the parameters to create a transport and authenticator.

        :param transport: A transport to make HTTP requests.
        :param authenticator: Authenticator to authenticate session.
        :param preference: User service preferences.
        :param boolean/string verify: ``True`` to verify SSL or CA_BUNDLE path.
        :param string user_agent: Value for ``User-Agent`` header.
        :param string auth_plugin: Name of the authorization plugin.
        :param auth_args: Arguments to create authenticator.
        """
        self.transport = self._create_transport(transport, verify, user_agent)
        self.authenticator = self._create_authenticator(authenticator,
                                                        auth_plugin,
                                                        **auth_args)
        self.session = session.Session(self.transport, self.authenticator,
                                       preference)

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
