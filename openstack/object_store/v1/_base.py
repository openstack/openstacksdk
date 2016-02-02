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

from openstack.object_store import object_store_service
from openstack import resource


class BaseResource(resource.Resource):
    service = object_store_service.ObjectStoreService()

    #: Metadata stored for this resource. *Type: dict*
    metadata = dict()

    _custom_metadata_prefix = None
    _system_metadata = dict()

    def _calculate_headers(self, metadata):
        headers = dict()
        for key in metadata:
            if key in self._system_metadata:
                header = self._system_metadata[key]
            else:
                header = self._custom_metadata_prefix + key
            headers[header] = metadata[key]
        return headers

    def set_metadata(self, session, metadata):
        url = self._get_url(self, self.id)
        session.post(url, endpoint_filter=self.service,
                     headers=self._calculate_headers(metadata))

    def delete_metadata(self, session, keys):
        url = self._get_url(self, self.id)
        headers = {key: '' for key in keys}
        session.post(url, endpoint_filter=self.service,
                     headers=self._calculate_headers(headers))

    def _set_metadata(self):
        self.metadata = dict()
        headers = self.get_headers()

        for header in headers:
            if header.startswith(self._custom_metadata_prefix):
                key = header[len(self._custom_metadata_prefix):].lower()
                self.metadata[key] = headers[header]

    def get(self, session, include_headers=False, args=None):
        super(BaseResource, self).get(session, include_headers, args)
        self._set_metadata()
        return self

    def head(self, session):
        super(BaseResource, self).head(session)
        self._set_metadata()
        return self

    @classmethod
    def update_by_id(cls, session, resource_id, attrs, path_args=None):
        """Update a Resource with the given attributes.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.
        :param dict attrs: The attributes to be sent in the body
                           of the request.
        :param dict path_args: This parameter is sent by the base
                               class but is ignored for this method.

        :return: A ``dict`` representing the response headers.
        """
        url = cls._get_url(None, resource_id)
        headers = attrs.get(resource.HEADERS, dict())
        headers['Accept'] = ''
        return session.post(url, endpoint_filter=cls.service,
                            headers=headers).headers
