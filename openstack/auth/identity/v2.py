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
Identity v2 authorization plugins.  The plugin must be constructed with an
auhorization URL and a user id, user name or token.  A user id or user name
would also require a password. For example::

    from openstack.auth.identity import v2
    from openstack import transport

    args = {
        'password': 'openSesame',
        'auth_url': 'https://10.1.1.1:5000/v2.0/',
        'user_name': 'alibaba',
    }
    auth = v2.Auth(**args)
    xport = transport.Transport()
    accessInfo = auth.authorize(xport)
"""

import logging

from openstack.auth import access
from openstack.auth.identity import base
from openstack import exceptions

_logger = logging.getLogger(__name__)


class Auth(base.BaseIdentityPlugin):

    #: Valid options for this plugin
    valid_options = [
        'access_info',
        'auth_url',
        'user_name',
        'user_id',
        'password',
        'project_id',
        'project_name',
        'reauthenticate',
        'token',
        'trust_id',
    ]

    def __init__(self, auth_url,
                 access_info=None,
                 user_name=None,
                 user_id=None,
                 password='',
                 token=None,
                 project_id=None,
                 project_name=None,
                 reauthenticate=True,
                 trust_id=None):
        """Construct an Identity V2 Authentication Plugin.

        A user_name, user_id or token must be provided.  More detailed
        information on some of the methods can be found in the base class
        :class:`~openstack.auth.identity.base.BaseIdentityPlugin`.

        :param string auth_url: Identity service endpoint for authorization.
        :param string access_info: Access info from previous authentication.
        :param string user_name: Username for authentication.
        :param string user_id: User ID for authentication.
        :param string password: Password for authentication.
        :param string project_id: Tenant ID for project scoping.
        :param string project_name: Tenant name for project scoping.
        :param bool reauthenticate: Get new token if token expires.
        :param string token: Existing token for authentication.
        :param string trust_id: Trust ID for trust scoping.

        :raises :class:`~openstack.exceptions.AuthorizationFailure`: if a
        user_id, user_name or token is not provided.
        """
        super(Auth, self).__init__(auth_url=auth_url,
                                   reauthenticate=reauthenticate)

        if not (user_id or user_name or token):
            msg = 'You need to specify either a user_name, user_id or token'
            raise exceptions.AuthorizationFailure(msg)

        self.access_info = access_info or None
        self.user_id = user_id
        self.user_name = user_name
        self.password = password
        self.token = token or None
        self.trust_id = trust_id
        self.tenant_id = project_id
        self.tenant_name = project_name

    def authorize(self, transport, **kwargs):
        """Obtain access information from an OpenStack Identity Service."""
        if self.token and self.access_info:
            return access.AccessInfoV2(**self.access_info)

        headers = {'Accept': 'application/json'}
        url = self.auth_url.rstrip('/') + '/tokens'
        params = {'auth': self.get_auth_data(headers)}

        if self.tenant_id:
            params['auth']['tenantId'] = self.tenant_id
        elif self.tenant_name:
            params['auth']['tenantName'] = self.tenant_name
        if self.trust_id:
            params['auth']['trust_id'] = self.trust_id

        _logger.debug('Making authentication request to %s', url)
        resp = transport.post(url, json=params, headers=headers)

        try:
            resp_data = resp.json()['access']
        except (KeyError, ValueError):
            raise exceptions.InvalidResponse(response=resp)

        return access.AccessInfoV2(**resp_data)

    def get_auth_data(self, headers):
        """Identity v2 token authentication data."""
        if self.token is None:
            auth = {'password': self.password}
            if self.user_id:
                auth['userId'] = self.user_id
            elif self.user_name:
                auth['username'] = self.user_name
            return {'passwordCredentials': auth}
        headers['X-Auth-Token'] = self.token
        return {'token': {'id': self.token}}

    def invalidate(self):
        """Invalidate the current authentication data."""
        if super(Auth, self).invalidate():
            self.access_info = None
            self.token = None
            return True
        return False
