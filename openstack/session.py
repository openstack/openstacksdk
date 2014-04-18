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


_logger = logging.getLogger(__name__)


class Session(object):

    def __init__(self, transport, authenticator):
        """Maintains client communication session.

        Session layer which uses the transport for communication.  The
        authenticator also uses the transport to keep authenticated.

        :param transport: A transport layer for the session.
        :param authenticator: An authenticator to authenticate the session.
        """
        self.transport = transport
        self.authenticator = authenticator

    def _request(self, service, path, method, authenticate=True, **kwargs):
        """Send an HTTP request with the specified characteristics.

        Handle a session level request.

        :param ServiceIdentifier service: Object that identifies service to
                                          the authenticator.
        :type service: :class:`openstack.auth.service.ServiceIdentifier`
        :param string path: Path relative to authentictor base url.
        :param string method: The http method to use. (eg. 'GET', 'POST').
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

        url = self.authenticator.get_endpoint(self.transport, service) + path
        return self.transport.request(method, url, **kwargs)

    def head(self, service, path, **kwargs):
        return self._request(service, path, 'HEAD', **kwargs)

    def get(self, service, path, **kwargs):
        return self._request(service, path, 'GET', **kwargs)

    def post(self, service, path, **kwargs):
        return self._request(service, path, 'POST', **kwargs)

    def put(self, service, path, **kwargs):
        return self._request(service, path, 'PUT', **kwargs)

    def delete(self, service, path, **kwargs):
        return self._request(service, path, 'DELETE', **kwargs)

    def patch(self, service, path, **kwargs):
        return self._request(service, path, 'PATCH', **kwargs)
