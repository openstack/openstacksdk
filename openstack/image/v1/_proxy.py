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

    def upload_image(self, **attrs):
        """Upload a new image from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.image.v1.image.Image`,
                           comprised of the properties on the Image class.

        :returns: The results of image creation
        :rtype: :class:`~openstack.image.v1.image.Image`
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
        self._delete(image.Image, value, ignore_missing=ignore_missing)

    def find_image(self, name_or_id, ignore_missing=True):
        """Find a single image

        :param name_or_id: The name or ID of a image.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.image.v1.image.Image` or None
        """
        return self._find(image.Image, name_or_id,
                          ignore_missing=ignore_missing)

    def get_image(self, value):
        """Get a single image

        :param value: The value can be the ID of an image or a
                      :class:`~openstack.image.v1.image.Image` instance.

        :returns: One :class:`~openstack.image.v1.image.Image`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(image.Image, value)

    def images(self, **query):
        """Return a generator of images

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of image objects
        :rtype: :class:`~openstack.image.v1.image.Image`
        """
        return self._list(image.Image, paginated=True, **query)

    def update_image(self, value, **attrs):
        """Update a image

        :param value: Either the id of a image or a
                      :class:`~openstack.image.v1.image.Image` instance.
        :attrs kwargs: The attributes to update on the image represented
                       by ``value``.

        :returns: The updated image
        :rtype: :class:`~openstack.image.v1.image.Image`
        """
        return self._update(image.Image, value, **attrs)
