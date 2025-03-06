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

import re
import urllib.parse

from openstack import exceptions
from openstack import resource
from openstack import utils


class Info(resource.Resource):
    base_path = "/info"

    allow_fetch = True

    _query_mapping = resource.QueryParameters(
        'swiftinfo_sig', 'swiftinfo_expires'
    )

    # Properties
    bulk_delete = resource.Body("bulk_delete", type=dict)
    swift = resource.Body("swift", type=dict)
    slo = resource.Body("slo", type=dict)
    staticweb = resource.Body("staticweb", type=dict)
    tempurl = resource.Body("tempurl", type=dict)

    # The endpoint in the catalog has version and project-id in it
    # To get capabilities, we have to disassemble and reassemble the URL
    # to append 'info'
    # This logic is taken from swiftclient
    def _get_info_url(self, url):
        URI_PATTERN_VERSION = re.compile(r'\/v\d+\.?\d*(\/.*)?')
        scheme, netloc, path, params, query, fragment = urllib.parse.urlparse(
            url
        )
        if URI_PATTERN_VERSION.search(path):
            path = URI_PATTERN_VERSION.sub('/info', path)
        else:
            path = utils.urljoin(path, 'info')

        return urllib.parse.urlunparse(
            (scheme, netloc, path, params, query, fragment)
        )

    def fetch(
        self,
        session,
        requires_id=False,
        base_path=None,
        error_message=None,
        skip_cache=False,
        **kwargs,
    ):
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
        :raises: :exc:`~openstack.exceptions.NotFoundException` if
                 the resource was not found.
        """
        if not self.allow_fetch:
            raise exceptions.MethodNotSupported(self, "fetch")

        session = self._get_session(session)
        info_url = self._get_info_url(session.get_endpoint())

        microversion = self._get_microversion(session)
        response = session.get(info_url, microversion=microversion)

        self.microversion = microversion
        self._translate_response(response, error_message=error_message)
        return self
