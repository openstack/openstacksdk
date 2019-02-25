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
import warnings

from openstack.cloud import exc
from openstack.image import _base_proxy
from openstack.image.v1 import image as _image


class Proxy(_base_proxy.BaseImageProxy):

    def upload_image(self, **attrs):
        """Upload a new image from attributes

        .. warning:
          This method is deprecated - and also doesn't work very well.
          Please stop using it immediately and switch to
          `create_image`.

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.image.v1.image.Image`,
                           comprised of the properties on the Image class.

        :returns: The results of image creation
        :rtype: :class:`~openstack.image.v1.image.Image`
        """
        warnings.warn("upload_image is deprecated. Use create_image instead.")
        return self._create(_image.Image, **attrs)

    def _upload_image(
            self, name, filename, meta, wait, timeout, **image_kwargs):
        # NOTE(mordred) wait and timeout parameters are unused, but
        # are present for ease at calling site.
        image_data = open(filename, 'rb')
        image_kwargs['properties'].update(meta)
        image_kwargs['name'] = name

        # TODO(mordred) Convert this to use image Resource
        image = self._connection._get_and_munchify(
            'image',
            self.post('/images', json=image_kwargs))
        checksum = image_kwargs['properties'].get(
            self._connection._IMAGE_MD5_KEY, '')

        try:
            # Let us all take a brief moment to be grateful that this
            # is not actually how OpenStack APIs work anymore
            headers = {
                'x-glance-registry-purge-props': 'false',
            }
            if checksum:
                headers['x-image-meta-checksum'] = checksum

            image = self._connection._get_and_munchify(
                'image',
                self.put(
                    '/images/{id}'.format(id=image.id),
                    headers=headers, data=image_data))

        except exc.OpenStackCloudHTTPError:
            self._connection.log.debug(
                "Deleting failed upload of image %s", name)
            try:
                self.delete('/images/{id}'.format(id=image.id))
            except exc.OpenStackCloudHTTPError:
                # We're just trying to clean up - if it doesn't work - shrug
                self._connection.log.warning(
                    "Failed deleting image after we failed uploading it.",
                    exc_info=True)
            raise
        return self._connection._normalize_image(image)

    def _update_image_properties(self, image, meta, properties):
        properties.update(meta)
        img_props = {}
        for k, v in iter(properties.items()):
            if image.properties.get(k, None) != v:
                img_props['x-image-meta-{key}'.format(key=k)] = v
        if not img_props:
            return False
        self.put(
            '/images/{id}'.format(id=image.id), headers=img_props)
        self._connection.list_images.invalidate(self._connection)
        return True

    def _existing_image(self, **kwargs):
        return _image.Image.existing(connection=self._connection, **kwargs)

    def delete_image(self, image, ignore_missing=True):
        """Delete an image

        :param image: The value can be either the ID of an image or a
                      :class:`~openstack.image.v1.image.Image` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the image does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent image.

        :returns: ``None``
        """
        self._delete(_image.Image, image, ignore_missing=ignore_missing)

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
        return self._find(_image.Image, name_or_id,
                          ignore_missing=ignore_missing)

    def get_image(self, image):
        """Get a single image

        :param image: The value can be the ID of an image or a
                      :class:`~openstack.image.v1.image.Image` instance.

        :returns: One :class:`~openstack.image.v1.image.Image`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_image.Image, image)

    def images(self, **query):
        """Return a generator of images

        :param kwargs query: Optional query parameters to be sent to limit
                               the resources being returned.

        :returns: A generator of image objects
        :rtype: :class:`~openstack.image.v1.image.Image`
        """
        return self._list(_image.Image, **query)

    def update_image(self, image, **attrs):
        """Update a image

        :param image: Either the ID of a image or a
                      :class:`~openstack.image.v1.image.Image` instance.
        :attrs kwargs: The attributes to update on the image represented
                       by ``value``.

        :returns: The updated image
        :rtype: :class:`~openstack.image.v1.image.Image`
        """
        return self._update(_image.Image, image, **attrs)
