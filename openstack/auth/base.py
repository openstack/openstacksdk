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
The base class for an authenticator.  A plugin must define the get_token,
get_endpoint, and get_versions methods.  The simpliest example would be
something that is just given such as::

    class SimpleAuthenticator(base.BaseAuthPlugin):
        def __init__(self, token, endpoint, versions):
            super(SimpleAuthenticator, self).__init__()
            self.token = token
            self.endpoint = endpoint
            self.versions = versions

        def get_token(self, transport, **kwargs):
            return self.token

        def get_endpoint(self, transport, service, **kwargs):
            return self.endpoint

        def get_versions(self, transport, service, **kwargs):
            return self.versions
"""

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BaseAuthPlugin(object):

    @abc.abstractmethod
    def get_token(self, transport, **kwargs):
        """Obtain a token.

        How the token is obtained is up to the authenticator. If it is still
        valid it may be re-used, retrieved from cache or invoke an
        authentication request against a server.

        There are no required kwargs. They are implementation specific to
        an authenticator.

        An authenticator may raise an exception if it fails to retrieve a
        token.

        :param transport: A transport object so the authenticator can make
                          HTTP calls.
        :type transport: :class:`~openstack.transport.Transport`
        :return string: A token to use.
        """

    @abc.abstractmethod
    def get_endpoint(self, transport, service, **kwargs):
        """Return an endpoint for the client.

        There are no required keyword arguments to ``get_endpoint`` as an
        authenticator should use best effort with the information available to
        determine the endpoint.

        :param transport: Authenticator may need to make HTTP calls.
        :type transport: :class:`~openstack.transport.Transport`
        :param service: Filter to identify the desired service.
        :type service: :class:`~openstack.auth.service_filter.ServiceFilter`

        :returns string: The base URL that will be used to talk to the
                         required service or None if not available.
        """

    @abc.abstractmethod
    def get_versions(self, transport, service, **kwargs):
        """Return the valid versions for the given service.

        :param transport: Authenticator may need to make HTTP calls.
        :type transport: :class:`~openstack.transport.Transport`
        :param service: Filter to identify the desired service.
        :type service: :class:`~openstack.auth.service_filter.ServiceFilter`

        :returns list: Returns list of versions that match the filter.
        """

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
        return False
