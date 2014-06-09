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
class BaseIdentityPlugin(base.BaseAuthenticator):

    # Consider a token valid if it does not expire for this many seconds
    BEST_BEFORE_SECONDS = 1

    def __init__(self, auth_url=None):
        super(BaseIdentityPlugin, self).__init__()
        self.auth_url = auth_url
        self.access_info = None

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

    def get_access(self, transport):
        """Fetch or return a current AccessInfo object.

        If a valid AccessInfo is present then it is returned otherwise a new
        one will be fetched.

        :raises HttpError: An error from an invalid HTTP response.

        :returns AccessInfo: Valid AccessInfo
        """
        if (not self.access_info or
                self.access_info.will_expire_soon(self.BEST_BEFORE_SECONDS)):
            self.access_info = self.authorize(transport)

        return self.access_info

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
