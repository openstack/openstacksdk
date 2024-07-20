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
from openstack import utils


class MetadataMixin:
    id: str
    base_path: str
    _body: resource._ComponentManager

    #: *Type: list of tag strings*
    metadata = resource.Body('metadata', type=dict)

    def fetch_metadata(self, session):
        """Lists metadata set on the entity.

        :param session: The session to use for making this request.
        :return: The dictionary with metadata attached to the entity
        """
        url = utils.urljoin(self.base_path, self.id, 'metadata')
        response = session.get(url)
        exceptions.raise_from_response(response)
        json = response.json()

        if 'metadata' in json:
            self._body.attributes.update({'metadata': json['metadata']})
        return self

    def set_metadata(self, session, metadata=None, replace=False):
        """Sets/Replaces metadata key value pairs on the resource.

        :param session: The session to use for making this request.
        :param dict metadata: Dictionary with key-value pairs
        :param bool replace: Replace all resource metadata with the new object
            or merge new and existing.
        """
        url = utils.urljoin(self.base_path, self.id, 'metadata')
        if not metadata:
            metadata = {}
        if not replace:
            response = session.post(url, json={'metadata': metadata})
        else:
            response = session.put(url, json={'metadata': metadata})
        exceptions.raise_from_response(response)
        self._body.attributes.update({'metadata': metadata})
        return self

    def replace_metadata(self, session, metadata=None):
        """Replaces all metadata key value pairs on the resource.

        :param session: The session to use for making this request.
        :param dict metadata: Dictionary with key-value pairs
        :param bool replace: Replace all resource metadata with the new object
            or merge new and existing.
        """
        return self.set_metadata(session, metadata, replace=True)

    def delete_metadata(self, session):
        """Removes all metadata on the entity.

        :param session: The session to use for making this request.
        """
        self.set_metadata(session, None, replace=True)
        return self

    def get_metadata_item(self, session, key):
        """Get the single metadata item on the entity.

        If the metadata key does not exist a 404 will be returned

        :param session: The session to use for making this request.
        :param str key: The key of a metadata item.
        """
        url = utils.urljoin(self.base_path, self.id, 'metadata', key)
        response = session.get(url)
        exceptions.raise_from_response(
            response, error_message='Metadata item does not exist'
        )
        meta = response.json().get('meta', {})
        # Here we need to potentially init metadata
        metadata = self.metadata or {}
        metadata[key] = meta.get(key)
        self._body.attributes.update({'metadata': metadata})

        return self

    def set_metadata_item(self, session, key, value):
        """Create or replace single metadata item to the resource.

        :param session: The session to use for making this request.
        :param str key: The key for the metadata item.
        :param str value: The value.
        """
        url = utils.urljoin(self.base_path, self.id, 'metadata', key)
        response = session.put(url, json={'meta': {key: value}})
        exceptions.raise_from_response(response)
        # we do not want to update tags directly
        metadata = self.metadata
        metadata[key] = value
        self._body.attributes.update({'metadata': metadata})
        return self

    def delete_metadata_item(self, session, key):
        """Removes a single metadata item from the specified resource.

        :param session: The session to use for making this request.
        :param str key: The key as a string.
        """
        url = utils.urljoin(self.base_path, self.id, 'metadata', key)
        response = session.delete(url)
        exceptions.raise_from_response(response)
        # we do not want to update tags directly
        metadata = self.metadata
        try:
            if metadata:
                metadata.pop(key)
            else:
                metadata = {}
        except ValueError:
            pass  # do nothing!
        self._body.attributes.update({'metadata': metadata})
        return self
