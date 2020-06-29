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
from openstack import exceptions
from openstack.image import _base_proxy
from openstack.image.v1 import image as _image


class Proxy(_base_proxy.BaseImageProxy):

    def _create_image(self, **kwargs):
        """Create image resource from attributes
        """
        return self._create(_image.Image, **kwargs)

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
        self, name, filename, data, meta, wait, timeout,
        use_import=False,
        stores=None,
        all_stores=None,
        all_stores_must_succeed=None,
        **image_kwargs,
    ):
        if use_import:
            raise exceptions.InvalidRequest(
                "Glance v1 does not support image import")
        if stores or all_stores or all_stores_must_succeed:
            raise exceptions.InvalidRequest(
                "Glance v1 does not support stores")
        # NOTE(mordred) wait and timeout parameters are unused, but
        # are present for ease at calling site.
        if filename and not data:
            image_data = open(filename, 'rb')
        else:
            image_data = data
        image_kwargs['properties'].update(meta)
        image_kwargs['name'] = name

        # TODO(mordred) Convert this to use image Resource
        image = self._connection._get_and_munchify(
            'image',
            self.post('/images', json=image_kwargs))
        checksum = image_kwargs['properties'].get(self._IMAGE_MD5_KEY, '')

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
            self.log.debug(
                "Deleting failed upload of image %s", name)
            try:
                self.delete('/images/{id}'.format(id=image.id))
            except exc.OpenStackCloudHTTPError:
                # We're just trying to clean up - if it doesn't work - shrug
                self.log.warning(
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
        return self._list(_image.Image, base_path='/images/detail', **query)

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

    def download_image(self, image, stream=False, output=None,
                       chunk_size=1024):
        """Download an image

        This will download an image to memory when ``stream=False``, or allow
        streaming downloads using an iterator when ``stream=True``.
        For examples of working with streamed responses, see
        :ref:`download_image-stream-true`.

        :param image: The value can be either the ID of an image or a
                      :class:`~openstack.image.v2.image.Image` instance.

        :param bool stream: When ``True``, return a :class:`requests.Response`
                            instance allowing you to iterate over the
                            response data stream instead of storing its entire
                            contents in memory. See
                            :meth:`requests.Response.iter_content` for more
                            details. *NOTE*: If you do not consume
                            the entirety of the response you must explicitly
                            call :meth:`requests.Response.close` or otherwise
                            risk inefficiencies with the ``requests``
                            library's handling of connections.


                            When ``False``, return the entire
                            contents of the response.
        :param output: Either a file object or a path to store data into.
        :param int chunk_size: size in bytes to read from the wire and buffer
            at one time. Defaults to 1024

        :returns: When output is not given - the bytes comprising the given
            Image when stream is False, otherwise a :class:`requests.Response`
            instance. When output is given - a
            :class:`~openstack.image.v2.image.Image` instance.
        """

        image = self._get_resource(_image.Image, image)

        return image.download(
            self, stream=stream, output=output, chunk_size=chunk_size)
