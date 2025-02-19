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

import typing as ty

from openstack import exceptions
from openstack import resource


class BaseResource(resource.Resource):
    commit_method = 'POST'
    create_method = 'PUT'

    #: Metadata stored for this resource. *Type: dict*
    metadata: dict[str, ty.Any] = {}

    _custom_metadata_prefix: str
    _system_metadata: dict[str, ty.Any] = {}
    _last_headers: dict[str, ty.Any] = {}

    def __init__(self, metadata=None, **attrs):
        """Process and save metadata known at creation stage"""
        super().__init__(**attrs)
        if metadata is not None:
            for k, v in metadata.items():
                if not k.lower().startswith(
                    self._custom_metadata_prefix.lower()
                ):
                    self.metadata[self._custom_metadata_prefix + k] = v
                else:
                    self.metadata[k] = v

    def _prepare_request(self, *args, **kwargs):
        request = super()._prepare_request(*args, **kwargs)
        request.headers.update(self._calculate_headers(self.metadata))
        return request

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
            headers[header] = str(metadata[key])
        return headers

    def set_metadata(self, session, metadata, refresh=True):
        request = self._prepare_request()
        response = session.post(
            request.url, headers=self._calculate_headers(metadata)
        )
        self._translate_response(response, has_body=False)
        if refresh:
            response = session.head(request.url)
            self._translate_response(response, has_body=False)
        return self

    def delete_metadata(self, session, keys):
        request = self._prepare_request()
        headers = {key: '' for key in keys}
        response = session.post(
            request.url, headers=self._calculate_headers(headers)
        )
        exceptions.raise_from_response(
            response, error_message="Error deleting metadata keys"
        )
        return self

    def _set_metadata(self, headers):
        self.metadata = dict()

        for header in headers:
            # RADOS and other stuff in front may actually lowcase headers
            if header.lower().startswith(self._custom_metadata_prefix.lower()):
                key = header[len(self._custom_metadata_prefix) :].lower()
                self.metadata[key] = headers[header]

    def _translate_response(
        self,
        response,
        has_body=None,
        error_message=None,
        *,
        resource_response_key=None,
    ):
        # Save headers of the last operation for potential use (get_object of
        # cloud layer).
        # This must happen before invoking parent _translate_response, cause it
        # pops known headers.
        self._last_headers = response.headers.copy()
        super()._translate_response(
            response, has_body=has_body, error_message=error_message
        )
        self._set_metadata(response.headers)
