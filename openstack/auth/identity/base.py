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

import abc

import six

from openstack.auth import base


@six.add_metaclass(abc.ABCMeta)
class BaseIdentityPlugin(base.BaseAuthPlugin):

    # Consider a token valid if it does not expire for this many seconds
    BEST_BEFORE_SECONDS = 1

    def __init__(self, auth_url=None, reauthenticate=True):
        super(BaseIdentityPlugin, self).__init__()
        self.auth_url = auth_url
        self.access_info = None
        self.reauthenticate = reauthenticate

    @abc.abstractmethod
    def authorize(self, transport, **kwargs):
        """Obtain access information from an OpenStack Identity Service.

        Thus method will authenticate and fetch a new AccessInfo when
        invoked.

        :raises InvalidResponse: The response returned wasn't appropriate.
        :raises HttpError: An error from an invalid HTTP response.

        :returns AccessInfo: Token access information.
        """

    def get_token(self, transport, **kwargs):
        """Return a valid auth token.

        If a valid token is not present then a new one will be fetched.

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

        :param Transport transport: A transport object so the authenticator
                                    can authenticate.
        :param ServiceFilter service: The filter to identify the desired
                                      service.

        :raises HttpError: An error from an invalid HTTP response.

        :return string or None: A valid endpoint URL or None if not available.
        """
        service_catalog = self.get_access(transport).service_catalog
        return service_catalog.get_url(service)
