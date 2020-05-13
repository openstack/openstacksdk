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

import urllib

from openstack import exceptions
from openstack import resource


class Info(resource.Resource):

    base_path = "/info"

    allow_fetch = True

    _query_mapping = resource.QueryParameters(
        'swiftinfo_sig', 'swiftinfo_expires'
    )

    # Properties
    swift = resource.Body("swift", type=dict)
    slo = resource.Body("slo", type=dict)
    staticweb = resource.Body("staticweb", type=dict)
    tempurl = resource.Body("tempurl", type=dict)

    def fetch(self, session, requires_id=False,
              base_path=None, error_message=None):
        """Get a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param boolean requires_id: A boolean indicating whether resource ID
                                    should be part of the requested URI.
        :param str base_path: Base part of the URI for fetching resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param str error_message: An Error message to be returned if
                                  requested object does not exist.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_fetch` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.ResourceNotFound` if
                 the resource was not found.
        """
        if not self.allow_fetch:
            raise exceptions.MethodNotSupported(self, "fetch")

        # The endpoint in the catalog has version and project-id in it
        # To get capabilities, we have to disassemble and reassemble the URL
        # This logic is taken from swiftclient

        session = self._get_session(session)
        endpoint = urllib.parse.urlparse(session.get_endpoint())
        url = "{scheme}://{netloc}/info".format(
            scheme=endpoint.scheme, netloc=endpoint.netloc)

        microversion = self._get_microversion_for(session, 'fetch')
        response = session.get(url, microversion=microversion)
        kwargs = {}
        if error_message:
            kwargs['error_message'] = error_message

        self.microversion = microversion
        self._translate_response(response, **kwargs)
        return self
