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
The :class:`~openstack.session.Session` is the class that maintains session
layer similar to the OSI model session layer.  The session has a transport
and an authenticator.  The transport is used by the session and authenticator
for HTTP layer transport.  The authenticator is responsible for providing an
authentication token and an endpoint to communicate with.

Examples
--------

The following examples use the example authenticator which takes the token
and endpoint as arguments.

Create a session
~~~~~~~~~~~~~~~~

Constructor::

    from examples import authenticator
    from openstack import session
    from openstack import transport
    xport = transport.Transport()
    token = 'SecretToken'
    endpoint = 'http://cloud.example.com:3333'
    auther = authenticator.TestAuthenticator(token, endpoint)
    sess = session.Session(xport, auther)

HTTP GET
~~~~~~~~

Making a basic HTTP GET call::

    containers = sess.get('/').json()

The containers variable will contain a list of dict describing the containers.

HTTP PUT
~~~~~~~~

Creating a new object::

    objay_data = 'roland garros'
    objay_len = len(objay_data)
    headers = {"Content-Length": objay_len, "Content-Type": "text/plain"}
    resp = sess.put('/pilots/french.txt', headers=headers, data=objay_data)
"""

import logging

from openstack import user_preference
from openstack import utils


_logger = logging.getLogger(__name__)


class Session(object):

    def __init__(self, transport, authenticator, preference=None):
        """Create a new object with a transport and authenticator.

        Session layer which uses the transport for communication.  The
        authenticator also uses the transport to keep authenticated.

        :param transport: A transport that provides an HTTP request method.
            The transport is also to be used by the authenticator, if needed.
        :type transport: :class:`~openstack.transport.Transport`
        :param authenticator: An authenticator that provides get_token and
            get_endpoint methods for the session.
        :type authenticator: :class:`~openstack.auth.base.BaseAuthPlugin`
        :param preference: If the user has any special preferences such as the
            service name, region, version or visibility, they may be provided
            in the preference object.  If no preferences are provided, the
            services that appear first in the service catalog will be used.
        :type preference: :class:`~openstack.user_preference.UserPreference`

        All the other methods of the session accept the following parameters:

        :param str path: Path relative to service base url.
        :param service: a service filter for the authenticator to determine
            the correct endpoint to use.
        :type service: :class:`~openstack.auth.service_filter.ServiceFilter`
        :param bool authenticate: A flag that indicates if a token should be
            attached to the request.  This parameter defaults to true.
        :param kwargs: The remaining arguments are passed to the transport
            request method.
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
        :param service: Object that filters service to the authenticator.
        :type service: :class:`~openstack.auth.service_filter.ServiceFilter`
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
        """Perform an HTTP HEAD request."""
        return self._request(path, 'HEAD', **kwargs)

    def get(self, path, **kwargs):
        """Perform an HTTP GET request."""
        return self._request(path, 'GET', **kwargs)

    def post(self, path, **kwargs):
        """Perform an HTTP POST request."""
        return self._request(path, 'POST', **kwargs)

    def put(self, path, **kwargs):
        """Perform an HTTP PUT request."""
        return self._request(path, 'PUT', **kwargs)

    def delete(self, path, **kwargs):
        """Perform an HTTP DELETE request."""
        return self._request(path, 'DELETE', **kwargs)

    def patch(self, path, **kwargs):
        """Perform an HTTP PATCH request."""
        return self._request(path, 'PATCH', **kwargs)

    def get_services(self):
        """Get list of services from preferences."""
        return self.preference.get_services()
