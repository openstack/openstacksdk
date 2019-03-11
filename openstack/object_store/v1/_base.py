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

from openstack import exceptions
from openstack import resource


class BaseResource(resource.Resource):

    commit_method = 'POST'
    create_method = 'PUT'

    #: Metadata stored for this resource. *Type: dict*
    metadata = dict()

    _custom_metadata_prefix = None
    _system_metadata = dict()

    def _calculate_headers(self, metadata):
        headers = {}
        for key in metadata:
            if key in self._system_metadata.keys():
                header = self._system_metadata[key]
            elif key in self._system_metadata.values():
                header = key
            else:
                if key.startswith(self._custom_metadata_prefix):
                    header = key
                else:
                    header = self._custom_metadata_prefix + key
            headers[header] = metadata[key]
        return headers

    def set_metadata(self, session, metadata, refresh=True):
        request = self._prepare_request()
        response = session.post(
            request.url,
            headers=self._calculate_headers(metadata))
        self._translate_response(response, has_body=False)
        if refresh:
            response = session.head(request.url)
            self._translate_response(response, has_body=False)
        return self

    def delete_metadata(self, session, keys):
        request = self._prepare_request()
        headers = {key: '' for key in keys}
        response = session.post(
            request.url,
            headers=self._calculate_headers(headers))
        exceptions.raise_from_response(
            response, error_message="Error deleting metadata keys")
        return self

    def _set_metadata(self, headers):
        self.metadata = dict()

        for header in headers:
            if header.startswith(self._custom_metadata_prefix):
                key = header[len(self._custom_metadata_prefix):].lower()
                self.metadata[key] = headers[header]

    def _translate_response(self, response, has_body=None, error_message=None):
        super(BaseResource, self)._translate_response(
            response, has_body=has_body, error_message=error_message)
        self._set_metadata(response.headers)
