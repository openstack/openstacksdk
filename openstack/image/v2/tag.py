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

from openstack.image import image_service
from openstack.image.v2 import image
from openstack import resource


class Tag(resource.Resource):
    id_attribute = "image"
    base_path = "/images/%(image)s/tags"
    service = image_service.ImageService()

    # capabilities
    allow_create = True
    allow_delete = True

    #: The image to manipulate
    image = resource.prop("image", type=image.Image)

    def create(self, session, tag):
        """Set a tag on the image

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param string tag: A tag to set on the image

        :return: ``None``
        """
        url = self._get_url({"image": self.image.id}, tag)
        headers = {'Accept': ''}
        session.put(url, endpoint_filter=self.service, headers=headers)

    def delete(self, session, tag):
        """Delete a tag on the image

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param string tag: The tag to delete on the image

        :return: ``None``
        """
        url = self._get_url({"image": self.image.id}, tag)
        headers = {'Accept': ''}
        session.delete(url, endpoint_filter=self.service, headers=headers)
