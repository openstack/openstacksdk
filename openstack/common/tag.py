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

import typing_extensions as ty_ext

from openstack import exceptions
from openstack import resource
from openstack import utils


# https://github.com/python/mypy/issues/11583
class _TagQueryParameters(ty.TypedDict):
    tags: str
    any_tags: str
    not_tags: str
    not_any_tags: str


class TagMixin(resource.ResourceMixinProtocol):
    _tag_query_parameters: _TagQueryParameters = {
        'tags': 'tags',
        'any_tags': 'tags-any',
        'not_tags': 'not-tags',
        'not_any_tags': 'not-tags-any',
    }

    #: A list of associated tags
    #: *Type: list of tag strings*
    tags = resource.Body('tags', type=list, default=[])

    def fetch_tags(self, session: resource.AdapterT) -> ty_ext.Self:
        """Lists tags set on the entity.

        :param session: The session to use for making this request.
        :return: The list with tags attached to the entity
        """
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session = self._get_session(session)
        response = session.get(url)
        exceptions.raise_from_response(response)
        # NOTE(gtema): since this is a common method
        # we can't rely on the resource_key, because tags are returned
        # without resource_key. Do parse response here
        json = response.json()
        if 'tags' in json:
            self._body.attributes.update({'tags': json['tags']})
        return self

    def set_tags(
        self, session: resource.AdapterT, tags: list[str]
    ) -> ty_ext.Self:
        """Sets/Replaces all tags on the resource.

        :param session: The session to use for making this request.
        :param list tags: List with tags to be set on the resource
        """
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session = self._get_session(session)
        response = session.put(url, json={'tags': tags})
        exceptions.raise_from_response(response)
        self._body.attributes.update({'tags': tags})
        return self

    def remove_all_tags(self, session: resource.AdapterT) -> ty_ext.Self:
        """Removes all tags on the entity.

        :param session: The session to use for making this request.
        """
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session = self._get_session(session)
        response = session.delete(url)
        exceptions.raise_from_response(response)
        self._body.attributes.update({'tags': []})
        return self

    def check_tag(self, session: resource.AdapterT, tag: str) -> ty_ext.Self:
        """Checks if tag exists on the entity.

        If the tag does not exist a 404 will be returned

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        url = utils.urljoin(self.base_path, self.id, 'tags', tag)
        session = self._get_session(session)
        response = session.get(url)
        exceptions.raise_from_response(
            response, error_message='Tag does not exist'
        )
        return self

    def add_tag(self, session: resource.AdapterT, tag: str) -> ty_ext.Self:
        """Adds a single tag to the resource.

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        url = utils.urljoin(self.base_path, self.id, 'tags', tag)
        session = self._get_session(session)
        response = session.put(url)
        exceptions.raise_from_response(response)
        # we do not want to update tags directly
        tags = self.tags
        tags.append(tag)
        self._body.attributes.update({'tags': tags})
        return self

    def remove_tag(self, session: resource.AdapterT, tag: str) -> ty_ext.Self:
        """Removes a single tag from the specified resource.

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        url = utils.urljoin(self.base_path, self.id, 'tags', tag)
        session = self._get_session(session)
        response = session.delete(url)
        exceptions.raise_from_response(response)
        # we do not want to update tags directly
        tags = self.tags
        try:
            # NOTE(gtema): if tags were not fetched, but request suceeded
            # it is ok. Just ensure tag does not exist locally
            tags.remove(tag)
        except ValueError:
            pass  # do nothing!
        self._body.attributes.update({'tags': tags})
        return self
