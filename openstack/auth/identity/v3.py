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
Identity v3 authorization plugins.  The plugin must be constructed with an
auhorization URL and a user id, user name or token.  A user id or user name
would also require a password. For example::

    from openstack.auth.identity import v3
    from openstack import transport

    args = {
        'password': 'openSesame',
        'auth_url': 'https://10.1.1.1:5000/v3/',
        'user_name': 'alibaba',
    }
    auth = v3.Auth(**args)
    xport = transport.Transport()
    accessInfo = auth.authorize(xport)
"""

import abc
import logging

import six

from openstack.auth import access
from openstack.auth.identity import base
from openstack import exceptions

_logger = logging.getLogger(__name__)


class Auth(base.BaseIdentityPlugin):

    #: Valid options for this plugin
    valid_options = [
        'access_info',
        'auth_url',
        'domain_id',
        'domain_name',
        'password',
        'project_domain_id',
        'project_domain_name',
        'project_id',
        'project_name',
        'reauthenticate',
        'token',
        'trust_id',
        'user_domain_id',
        'user_domain_name',
        'user_id',
        'user_name',
    ]

    def __init__(self, auth_url,
                 access_info=None,
                 domain_id=None,
                 domain_name=None,
                 password='',
                 project_domain_id=None,
                 project_domain_name=None,
                 project_id=None,
                 project_name=None,
                 reauthenticate=True,
                 token=None,
                 trust_id=None,
                 user_domain_id=None,
                 user_domain_name=None,
                 user_id=None,
                 user_name=None):
        """Construct an Identity V3 Authentication Plugin.

        This authorization plugin should be constructed with a password
        and user_id or user_name.  It may also be constructed with a token.
        More detailed information on some of the methods can be found in the
        base class :class:`~openstack.auth.identity.base.BaseIdentityPlugin`.

        :param string auth_url: Identity service endpoint for authentication.
        :param string access_info: Access info including service catalog.
        :param string domain_id: Domain ID for domain scoping.
        :param string domain_name: Domain name for domain scoping.
        :param string password: User password for authentication.
        :param string project_domain_id: Project's domain ID for project.
        :param string project_domain_name: Project's domain name for project.
        :param string project_id: Project ID for project scoping.
        :param string project_name: Project name for project scoping.
        :param bool reauthenticate: Get new token if token expires.
        :param string token: Token to use for authentication.
        :param string trust_id: Trust ID for trust scoping.
        :param string user_domain_id: User's domain ID for authentication.
        :param string user_domain_name: User's domain name for authentication.
        :param string user_name: User name for authentication.
        :param string user_id: User ID for authentication.

        :raises :class:`~openstack.exceptions.AuthorizationFailure`: if a
        user_id, user_name or token is not provided.
        """

        super(Auth, self).__init__(auth_url=auth_url,
                                   reauthenticate=reauthenticate)

        if not (user_id or user_name or token):
            msg = 'You need to specify either a user_name, user_id or token'
            raise exceptions.AuthorizationFailure(msg)

        self.access_info = access_info
        self.domain_id = domain_id
        self.domain_name = domain_name
        self.project_domain_id = project_domain_id
        self.project_domain_name = project_domain_name
        self.project_id = project_id
        self.project_name = project_name
        self.reauthenticate = reauthenticate
        self.trust_id = trust_id
        self.password_method = PasswordMethod(
            password=password,
            user_domain_id=user_domain_id,
            user_domain_name=user_domain_name,
            user_name=user_name,
            user_id=user_id,
        )
        if token:
            self.token_method = TokenMethod(token=token)
            self.auth_methods = [self.token_method]
        else:
            self.token_method = None
            self.auth_methods = [self.password_method]

    @property
    def token_url(self):
        """The full URL where we will send authentication data."""
        return '%s/auth/tokens' % self.auth_url.rstrip('/')

    def authorize(self, transport, **kwargs):
        """Obtain access information from an OpenStack Identity Service."""
        headers = {'Accept': 'application/json'}
        body = {'auth': {'identity': {}}}
        ident = body['auth']['identity']

        if self.token_method and self.access_info:
            return access.AccessInfoV3(self.token_method.token,
                                       **self.access_info)

        for method in self.auth_methods:
            name, auth_data = method.get_auth_data(transport, self, headers)
            ident.setdefault('methods', []).append(name)
            ident[name] = auth_data

        if not ident:
            raise exceptions.AuthorizationFailure('Authentication method '
                                                  'required (e.g. password)')

        mutual_exclusion = [bool(self.domain_id or self.domain_name),
                            bool(self.project_id or self.project_name),
                            bool(self.trust_id)]

        if sum(mutual_exclusion) > 1:
            raise exceptions.AuthorizationFailure('Authentication cannot be '
                                                  'scoped to multiple '
                                                  'targets. Pick one of: '
                                                  'project, domain or trust')

        if self.domain_id:
            body['auth']['scope'] = {'domain': {'id': self.domain_id}}
        elif self.domain_name:
            body['auth']['scope'] = {'domain': {'name': self.domain_name}}
        elif self.project_id:
            body['auth']['scope'] = {'project': {'id': self.project_id}}
        elif self.project_name:
            scope = body['auth']['scope'] = {'project': {}}
            scope['project']['name'] = self.project_name

            if self.project_domain_id:
                scope['project']['domain'] = {'id': self.project_domain_id}
            elif self.project_domain_name:
                scope['project']['domain'] = {'name': self.project_domain_name}
        elif self.trust_id:
            body['auth']['scope'] = {'OS-TRUST:trust': {'id': self.trust_id}}

        _logger.debug('Making authentication request to %s', self.token_url)
        resp = transport.post(self.token_url, json=body, headers=headers)

        try:
            resp_data = resp.json()['token']
        except (KeyError, ValueError):
            raise exceptions.InvalidResponse(response=resp)

        return access.AccessInfoV3(resp.headers['X-Subject-Token'],
                                   **resp_data)

    def invalidate(self):
        """Invalidate the current authentication data."""
        if super(Auth, self).invalidate():
            self.auth_methods = [self.password_method]
            self.access_info = None
            return True
        return False


@six.add_metaclass(abc.ABCMeta)
class AuthMethod(object):
    """One part of a V3 Authentication strategy.

    V3 Tokens allow multiple methods to be presented when authentication
    against the server. Each one of these methods is implemented by an
    AuthMethod.
    """
    def __init__(self, **kwargs):
        for param in kwargs:
            setattr(self, param, kwargs.get(param, None))

    @abc.abstractmethod
    def get_auth_data(self, transport, auth, headers, **kwargs):
        """Return the authentication section of an auth plugin.

        :param Transport transport: The communication transport.
        :param Auth auth: The auth plugin calling the method.
        :param dict headers: The headers that will be sent with the auth
                             request if a plugin needs to add to them.
        :return tuple(string, dict): The identifier of this plugin and a dict
                                     of authentication data for the auth type.
        """


class PasswordMethod(AuthMethod):
    """Identity v3 password authentication method.

    The identity v3 authorization password method derived from
    :class:`~openstack.auth.identity.v3.AuthMethod`.
    """

    def get_auth_data(self, transport, auth, headers, **kwargs):
        """Identity v3 password authentication data."""
        user = {'password': self.password}

        if self.user_id:
            user['id'] = self.user_id
        elif self.user_name:
            user['name'] = self.user_name

            if self.user_domain_id:
                user['domain'] = {'id': self.user_domain_id}
            elif self.user_domain_name:
                user['domain'] = {'name': self.user_domain_name}

        return 'password', {'user': user}


class TokenMethod(AuthMethod):
    """Identity v3 token authentication method.

    The identity v3 authorization token method derived from
    :class:`~openstack.auth.identity.v3.AuthMethod`.
    """

    def get_auth_data(self, transport, auth, headers, **kwargs):
        """Identity v3 token authentication data."""
        headers['X-Auth-Token'] = self.token
        return 'token', {'id': self.token}
