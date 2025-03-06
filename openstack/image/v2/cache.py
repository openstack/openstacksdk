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


class CachedImage(resource.Resource):
    image_id = resource.Body('image_id')
    hits = resource.Body('hits')
    last_accessed = resource.Body('last_accessed')
    last_modified = resource.Body('last_modified')
    size = resource.Body('size')


class Cache(resource.Resource):
    base_path = '/cache'

    allow_fetch = True
    allow_delete = True
    allow_create = True

    _max_microversion = '2.14'

    cached_images = resource.Body(
        'cached_images',
        type=list,
        list_type=CachedImage,
    )
    queued_images = resource.Body('queued_images', type=list)

    def queue(self, session, image, *, microversion=None):
        """Queue an image into cache.
        :param session: The session to use for making this request
        :param image: The image to be queued into cache.
        :returns: The server response
        """
        if microversion is None:
            microversion = self._get_microversion(session)
        image_id = resource.Resource._get_id(image)
        url = utils.urljoin(self.base_path, image_id)

        response = session.put(url, microversion=microversion)
        exceptions.raise_from_response(response)
        return response

    # FIXME(stephenfin): This needs to be renamed as it conflicts with
    # dict.clear
    def clear(self, session, target='both'):  # type: ignore[override]
        """Clears the cache.
        :param session: The session to use for making this request
        :param target: Specify which target you want to clear
            One of: ``both``(default), ``cache``, ``queue``.
        :returns: The server response
        """
        headers = {}
        if target in ('cache', 'queue'):
            headers = {'x-image-cache-clear-target': target}
        elif target != "both":
            raise exceptions.InvalidRequest(
                'Target must be "cache", "queue" or "both".'
            )
        response = session.delete(self.base_path, headers=headers)
        exceptions.raise_from_response(response)
        return response
