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
Identity discoverable authorization plugin must be constructed with an
auhorization URL and a user id, user name or token.  A user id or user name
would also require a password. The arguments that apply to the selected v2
or v3 plugin will be used.  The rest of the arguments will be ignored.  For
example::

    from openstack.auth.identity import discoverable
    from openstack import transport

    args = {
        'password': 'openSesame',
        'auth_url': 'https://10.1.1.1:5000/v3/',
        'user_name': 'alibaba',
    }
    auth = discoverable.Auth(**args)
    xport = transport.Transport()
    accessInfo = auth.authorize(xport)
"""

from openstack.auth.identity import base
from openstack.auth.identity import v2
from openstack.auth.identity import v3
from openstack import exceptions


class Auth(base.BaseIdentityPlugin):

    #: Valid options for this plugin
    valid_options = list(set(v2.Auth.valid_options + v3.Auth.valid_options))

    def __init__(self, auth_url=None, **auth_args):
        """Construct an Identity Authentication Plugin.

        This authorization plugin should be constructed with an auth_url
        and everything needed by either a v2 or v3 identity plugin.

        :param string auth_url: Identity service endpoint for authentication.

        :raises TypeError: if a user_id, user_name or token is not provided.
        """

        super(Auth, self).__init__(auth_url=auth_url)

        if not auth_url:
            msg = ("The authorization URL auth_url was not provided.")
            raise exceptions.AuthorizationFailure(msg)
        endpoint_version = auth_url.split('v')[-1][0]
        if endpoint_version == '2':
            plugin = v2.Auth
        else:
            plugin = v3.Auth
        valid_list = plugin.valid_options
        args = dict((n, auth_args[n]) for n in valid_list if n in auth_args)
        self.auth_plugin = plugin(auth_url, **args)

    @property
    def token_url(self):
        """The full URL where we will send authentication data."""
        return self.auth_plugin.token_url

    def authorize(self, transport, **kwargs):
        return self.auth_plugin.authorize(transport, **kwargs)

    def invalidate(self):
        return self.auth_plugin.invalidate()
