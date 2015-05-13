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

from openstack.image.v1 import image
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def create_image(self, **attrs):
        """Create a new image from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.image.v1.image.Image`,
                           comprised of the properties on the Image class.

        :returns: The results of image creation
        :rtype: :class:`~openstack.compute.v2.image.Image`
        """
        return self._create(image.Image, **attrs)

    def delete_image(self, value, ignore_missing=True):
        """Delete an image

        :param value: The value can be either the ID of an image or a
                      :class:`~openstack.image.v1.image.Image` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the image does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent image.

        :returns: ``None``
        """
        self._delete(image.Image, value, ignore_missing)

    def find_image(self, name_or_id):
        return image.Image.find(self.session, name_or_id)

    def get_image(self, value):
        """Get a single image

        :param value: The value can be the ID of an image or a
                      :class:`~openstack.image.v1.image.Image` instance.

        :returns: One :class:`~openstack.image.v1.image.Image`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(image.Image, value)

    def list_images(self, **params):
        return image.Image.list(self.session, **params)

    def update_image(self, value, **attrs):
        """Update a image

        :param value: Either the id of a image or a
                      :class:`~openstack.compute.v2.image.Image` instance.
        :attrs kwargs: The attributes to update on the image represented
                       by ``value``.

        :returns: The updated image
        :rtype: :class:`~openstack.compute.v2.image.Image`
        """
        return self._update(image.Image, value, **attrs)
