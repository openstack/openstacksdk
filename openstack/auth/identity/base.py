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
The base identity plugin.  Identity plugins must define the authorize method.
For examples of this class, see the v2 and v3 authentication plugins.
"""

import abc

import six

from openstack.auth import base


@six.add_metaclass(abc.ABCMeta)
class BaseIdentityPlugin(base.BaseAuthPlugin):

    #: Consider a token valid if it does not expire for this many seconds
    BEST_BEFORE_SECONDS = 1

    def __init__(self, auth_url=None, reauthenticate=True):
        """Create an identity authorization plugin.

        :param string auth_url: Authorization URL
        :param bool reauthenticate: Should the plugin attempt reauthorization.
        """
        super(BaseIdentityPlugin, self).__init__()
        self.auth_url = auth_url
        self.access_info = None
        self.reauthenticate = reauthenticate

    @abc.abstractmethod
    def authorize(self, transport, **kwargs):
        """Obtain access information from an OpenStack Identity Service.

        Thus method will authenticate and fetch a new AccessInfo when
        invoked.

        :param transport: A transport object for the authenticator.
        :type transport: :class:`~openstack.transport.Transport`

        :raises InvalidResponse: The response returned wasn't appropriate.
        :raises HttpError: An error from an invalid HTTP response.

        :returns AccessInfo: Token access information.
        """

    def get_token(self, transport, **kwargs):
        """Return a valid auth token.

        If a valid token is not present then a new one will be fetched.

        :param transport: A transport object for the authenticator.
        :type transport: :class:`~openstack.transport.Transport`

        :raises HttpError: An error from an invalid HTTP response.

        :return string: A valid token.
        """
        return self.get_access(transport).auth_token

    def _needs_reauthenticate(self):
        """Return if the existing token needs to be re-authenticated.

        The token should be refreshed if it is about to expire.

        :returns: True if the plugin should fetch a new token. False otherwise.
        """
        if not self.access_info:
            # authentication was never fetched.
            return True

        if not self.reauthenticate:
            # don't re-authenticate if it has been disallowed.
            return False

        if self.access_info.will_expire_soon(self.BEST_BEFORE_SECONDS):
            # if it's about to expire we should re-authenticate now.
            self.invalidate()
            return True

        # otherwise it's fine and use the existing one.
        return False

    def get_access(self, transport):
        """Fetch or return a current AccessInfo object.

        If a valid AccessInfo is present then it is returned otherwise a new
        one will be fetched.

        :param transport: A transport object for the authenticator.
        :type transport: :class:`~openstack.transport.Transport`

        :raises HttpError: An error from an invalid HTTP response.

        :returns AccessInfo: Valid AccessInfo
        """
        if self._needs_reauthenticate():
            self.access_info = self.authorize(transport)

        return self.access_info

    def invalidate(self):
        """Invalidate the current authentication data.

        This should result in fetching a new token on next call.

        A plugin may be invalidated if an Unauthorized HTTP response is
        returned to indicate that the token may have been revoked or is
        otherwise now invalid.

        :returns bool: True if there was something that the plugin did to
                       invalidate. This means that it makes sense to try again.
                       If nothing happens returns False to indicate give up.
        """
        self.access_info = None
        return True

    def get_endpoint(self, transport, service, **kwargs):
        """Return a valid endpoint for a service.

        If a valid token is not present then a new one will be fetched using
        the transport.

        :param transport: A transport object for the authenticator.
        :type transport: :class:`~openstack.transport.Transport`
        :param service: The filter to identify the desired service.
        :type service: :class:`~openstack.auth.service_filter.ServiceFilter`

        :raises HttpError: An error from an invalid HTTP response.

        :return string or None: A valid endpoint URL or None if not available.
        """
        service_catalog = self.get_access(transport).service_catalog
        return service_catalog.get_url(service)

    def get_versions(self, transport, service, **kwargs):
        """Return the valid versions for the given service.

        :param Transport transport: Authenticator may need to make HTTP calls.
        :type transport: :class:`~openstack.transport.Transport`
        :param ServiceFilter service: Filter to identify the desired service.
        :type service: :class:`~openstack.auth.service_filter.ServiceFilter`

        :returns list: Returns list of versions that match the filter.
        """
        service_catalog = self.get_access(transport).service_catalog
        return service_catalog.get_versions(service)
