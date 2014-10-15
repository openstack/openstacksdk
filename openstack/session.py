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

import logging

from openstack import user_preference
from openstack import utils


_logger = logging.getLogger(__name__)


class Session(object):

    def __init__(self, transport, authenticator, preference=None):
        """Maintains client communication session.

        Session layer which uses the transport for communication.  The
        authenticator also uses the transport to keep authenticated.

        :param transport: A transport layer for the session.
        :param authenticator: An authenticator to authenticate the session.
        :param UserPreference preference: User service preferences.
        :type preference: :class:`openstack.user_preference.UserPreference`
        """
        self.transport = transport
        self.authenticator = authenticator
        self.preference = preference or user_preference.UserPreference()

    def _request(self, path, method, service=None, authenticate=True,
                 **kwargs):
        """Send an HTTP request with the specified characteristics.

        Handle a session level request.

        :param string path: Path relative to authentictor base url.
        :param string method: The http method to use. (eg. 'GET', 'POST').
        :param ServiceFilter service: Object that filters service to
                                      the authenticator.
        :type service: :class:`openstack.auth.service_filter.ServiceFilter`
        :param bool authenticate: True if a token should be attached
        :param kwargs: any other parameter that can be passed to transport
                       and authenticator.

        :returns: The response to the request.
        """

        headers = kwargs.setdefault('headers', dict())
        if authenticate:
            token = self.authenticator.get_token(self.transport)
            if token:
                headers['X-Auth-Token'] = token
        if service:
            preference = self.preference.get_preference(service.service_type)
            if preference:
                service = preference.join(service)

        endpoint = self.authenticator.get_endpoint(self.transport, service)
        url = utils.urljoin(endpoint, path)

        return self.transport.request(method, url, **kwargs)

    def head(self, path, **kwargs):
        return self._request(path, 'HEAD', **kwargs)

    def get(self, path, **kwargs):
        return self._request(path, 'GET', **kwargs)

    def post(self, path, **kwargs):
        return self._request(path, 'POST', **kwargs)

    def put(self, path, **kwargs):
        return self._request(path, 'PUT', **kwargs)

    def delete(self, path, **kwargs):
        return self._request(path, 'DELETE', **kwargs)

    def patch(self, path, **kwargs):
        return self._request(path, 'PATCH', **kwargs)

    def get_services(self):
        return self.preference.get_services()
