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


@six.add_metaclass(abc.ABCMeta)
class BaseAuthenticator(object):
    """The basic structure of an authenticator."""

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
        :return string: A token to use.
        """

    @abc.abstractmethod
    def get_endpoint(self, transport, service, **kwargs):
        """Return an endpoint for the client.

        There are no required keyword arguments to ``get_endpoint`` as an
        authenticator should use best effort with the information available to
        determine the endpoint.

        :param Transport transport: A transport object so the authenticator
                                    can make HTTP calls
        :param ServiceIdentifier service: The object that identifies the
                                          service for the authenticator.

        :returns string: The base URL that will be used to talk to the
                         required service or None if not available.
        """
