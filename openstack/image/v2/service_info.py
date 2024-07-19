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


class Import(resource.Resource):
    base_path = '/info/import'

    # capabilities
    allow_fetch = True

    #: import methods
    import_methods = resource.Body('import-methods', type=dict)


class Store(resource.Resource):
    resources_key = 'stores'
    base_path = '/info/stores'

    # capabilities
    allow_list = True

    #: Description of the store
    description = resource.Body('description')
    #: default
    is_default = resource.Body('default', type=bool)
    #: properties
    properties = resource.Body('properties', type=dict)

    def delete_image(self, session, image, *, ignore_missing=False):
        """Delete image from store

        :param session: The session to use for making this request.
        :param image: The value can be either the ID of an image or a
            :class:`~openstack.image.v2.image.Image` instance.

        :returns: The result of the ``delete`` if resource found, else None.
        :raises: :class:`~openstack.exceptions.NotFoundException` when
            ignore_missing if ``False`` and a nonexistent resource
            is attempted to be deleted.
        """
        image_id = resource.Resource._get_id(image)
        url = utils.urljoin('/stores', self.id, image_id)

        try:
            response = session.delete(url)
            exceptions.raise_from_response(response)
        except exceptions.NotFoundException:
            if ignore_missing:
                return None
            raise

        return response
