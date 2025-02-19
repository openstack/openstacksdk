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

import os
import typing as ty
import warnings

from openstack import exceptions as exc
from openstack.image.v1 import image as _image
from openstack import proxy
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings


def _get_name_and_filename(name, image_format):
    # See if name points to an existing file
    if os.path.exists(name):
        # Neat. Easy enough
        return os.path.splitext(os.path.basename(name))[0], name

    # Try appending the disk format
    name_with_ext = '.'.join((name, image_format))
    if os.path.exists(name_with_ext):
        return os.path.basename(name), name_with_ext

    return name, None


class Proxy(proxy.Proxy):
    retriable_status_codes = [503]

    _IMAGE_MD5_KEY = 'owner_specified.openstack.md5'
    _IMAGE_SHA256_KEY = 'owner_specified.openstack.sha256'
    _IMAGE_OBJECT_KEY = 'owner_specified.openstack.object'

    # NOTE(shade) shade keys were owner_specified.shade.md5 - we need to add
    #             those to freshness checks so that a shade->sdk transition
    #             doesn't result in a re-upload
    _SHADE_IMAGE_MD5_KEY = 'owner_specified.shade.md5'
    _SHADE_IMAGE_SHA256_KEY = 'owner_specified.shade.sha256'
    _SHADE_IMAGE_OBJECT_KEY = 'owner_specified.shade.object'

    # ====== IMAGES ======
    def create_image(
        self,
        name,
        filename=None,
        container=None,
        md5=None,
        sha256=None,
        disk_format=None,
        container_format=None,
        disable_vendor_agent=True,
        allow_duplicates=False,
        meta=None,
        data=None,
        validate_checksum=False,
        tags=None,
        **kwargs,
    ):
        """Create an image and optionally upload data.

        Create a new image. If ``filename`` or ``data`` are provided, it will
        also upload data to this image.

        :param str name: Name of the image to create. If it is a path name
            of an image, the name will be constructed from the extensionless
            basename of the path.
        :param str filename: The path to the file to upload, if needed.
            (optional, defaults to None)
        :param data: Image data (string or file-like object). It is mutually
            exclusive with filename
        :param str container: Name of the container in swift where images
            should be uploaded for import if the cloud requires such a thing.
            (optional, defaults to 'images')
        :param str md5: md5 sum of the image file. If not given, an md5 will
            be calculated.
        :param str sha256: sha256 sum of the image file. If not given, an md5
            will be calculated.
        :param str disk_format: The disk format the image is in. (optional,
            defaults to the os-client-config config value for this cloud)
        :param str container_format: The container format the image is in.
            (optional, defaults to the os-client-config config value for this
            cloud)
        :param list tags: List of tags for this image. Each tag is a string
            of at most 255 chars.
        :param bool disable_vendor_agent: Whether or not to append metadata
            flags to the image to inform the cloud in question to not expect a
            vendor agent to be runing. (optional, defaults to True)
        :param allow_duplicates: If true, skips checks that enforce unique
            image name. (optional, defaults to False)
        :param meta: A dict of key/value pairs to use for metadata that
            bypasses automatic type conversion.
        :param bool validate_checksum: If true and cloud returns checksum,
            compares return value with the one calculated or passed into this
            call. If value does not match - raises exception. Default is
            'false'

        Additional kwargs will be passed to the image creation as additional
        metadata for the image and will have all values converted to string
        except for min_disk, min_ram, size and virtual_size which will be
        converted to int.

        If you are sure you have all of your data types correct or have an
        advanced need to be explicit, use meta. If you are just a normal
        consumer, using kwargs is likely the right choice.

        If a value is in meta and kwargs, meta wins.

        :returns: The results of image creation
        :rtype: :class:`~openstack.image.v1.image.Image`
        :raises: SDKException if there are problems uploading
        """
        # these were previously provided for API (method) compatibility; that
        # was a bad idea
        if (
            'use_import' in kwargs
            or 'stores' in kwargs
            or 'all_stores' in kwargs
            or 'all_stores_must_succeed' in kwargs
        ):
            raise exc.InvalidRequest(
                "Glance v1 does not support stores or image import"
            )

        # silently ignore these; they were never supported and were only given
        # for API (method) compatibility
        kwargs.pop('wait')
        kwargs.pop('timeout')

        if container is None:
            container = self._connection._OBJECT_AUTOCREATE_CONTAINER

        if not meta:
            meta = {}

        if not disk_format:
            disk_format = self._connection.config.config['image_format']

        if not container_format:
            # https://docs.openstack.org/image-guide/image-formats.html
            container_format = 'bare'

        if data and filename:
            raise exc.SDKException(
                'Passing filename and data simultaneously is not supported'
            )

        # If there is no filename, see if name is actually the filename
        if not filename and not data:
            name, filename = _get_name_and_filename(
                name,
                self._connection.config.config['image_format'],
            )

        if validate_checksum and data and not isinstance(data, bytes):
            raise exc.SDKException(
                'Validating checksum is not possible when data is not a '
                'direct binary object'
            )

        if not (md5 or sha256) and validate_checksum:
            if filename:
                md5, sha256 = utils._get_file_hashes(filename)
            elif data and isinstance(data, bytes):
                md5, sha256 = utils._calculate_data_hashes(data)

        if allow_duplicates:
            current_image = None
        else:
            current_image = self.find_image(name)
            if current_image:
                # NOTE(pas-ha) 'properties' may be absent or be None
                props = current_image.get('properties') or {}
                md5_key = props.get(
                    self._IMAGE_MD5_KEY,
                    props.get(self._SHADE_IMAGE_MD5_KEY, ''),
                )
                sha256_key = props.get(
                    self._IMAGE_SHA256_KEY,
                    props.get(self._SHADE_IMAGE_SHA256_KEY, ''),
                )
                up_to_date = utils._hashes_up_to_date(
                    md5=md5,
                    sha256=sha256,
                    md5_key=md5_key,
                    sha256_key=sha256_key,
                )
                if up_to_date:
                    self.log.debug(
                        "image %(name)s exists and is up to date",
                        {'name': name},
                    )
                    return current_image
                else:
                    self.log.debug(
                        "image %(name)s exists, but contains different "
                        "checksums. Updating.",
                        {'name': name},
                    )

        if disable_vendor_agent:
            kwargs.update(
                self._connection.config.config['disable_vendor_agent']
            )

        # If a user used the v1 calling format, they will have
        # passed a dict called properties along
        properties = kwargs.pop('properties', {})
        properties[self._IMAGE_MD5_KEY] = md5 or ''
        properties[self._IMAGE_SHA256_KEY] = sha256 or ''
        properties[self._IMAGE_OBJECT_KEY] = '/'.join([container, name])
        kwargs.update(properties)
        image_kwargs = {'properties': kwargs}
        if disk_format:
            image_kwargs['disk_format'] = disk_format
        if container_format:
            image_kwargs['container_format'] = container_format
        if tags:
            image_kwargs['tags'] = tags

        if filename or data:
            image = self._upload_image(
                name,
                filename=filename,
                data=data,
                meta=meta,
                validate_checksum=validate_checksum,
                **image_kwargs,
            )
        else:
            image = self._create(_image.Image, name=name, **kwargs)

        return image

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
        warnings.warn(
            "upload_image is deprecated. Use create_image instead.",
            os_warnings.RemovedInSDK50Warning,
        )
        return self._create(_image.Image, **attrs)

    def _upload_image(
        self,
        name,
        filename,
        data,
        meta,
        **image_kwargs,
    ):
        if filename and not data:
            image_data = open(filename, 'rb')
        else:
            image_data = data
        image_kwargs['properties'].update(meta)
        image_kwargs['name'] = name

        # TODO(mordred) Convert this to use image Resource
        image = self._connection._get_and_munchify(
            'image', self.post('/images', json=image_kwargs)
        )
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
                    f'/images/{image.id}',
                    headers=headers,
                    data=image_data,
                ),
            )
        except exc.HttpException:
            self.log.debug("Deleting failed upload of image %s", name)
            try:
                self.delete(f'/images/{image.id}')
            except exc.HttpException:
                # We're just trying to clean up - if it doesn't work - shrug
                self.log.warning(
                    "Failed deleting image after we failed uploading it.",
                    exc_info=True,
                )
            raise
        return image

    def _existing_image(self, **kwargs):
        return _image.Image.existing(connection=self._connection, **kwargs)

    def delete_image(self, image, ignore_missing=True):
        """Delete an image

        :param image: The value can be either the ID of an image or a
            :class:`~openstack.image.v1.image.Image` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
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
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.image.v1.image.Image` or None
        """
        return self._find(
            _image.Image, name_or_id, ignore_missing=ignore_missing
        )

    def get_image(self, image):
        """Get a single image

        :param image: The value can be the ID of an image or a
            :class:`~openstack.image.v1.image.Image` instance.

        :returns: One :class:`~openstack.image.v1.image.Image`
        :raises: :class:`~openstack.exceptions.NotFoundException`
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
        :param attrs: The attributes to update on the image represented
            by ``image``.

        :returns: The updated image
        :rtype: :class:`~openstack.image.v1.image.Image`
        """
        return self._update(_image.Image, image, **attrs)

    def download_image(
        self,
        image,
        stream=False,
        output=None,
        chunk_size=1024 * 1024,
    ):
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

            When ``False``, return the entire contents of the response.
        :param output: Either a file object or a path to store data into.
        :param int chunk_size: size in bytes to read from the wire and buffer
            at one time. Defaults to 1024 * 1024 = 1 MiB

        :returns: When output is not given - the bytes comprising the given
            Image when stream is False, otherwise a :class:`requests.Response`
            instance. When output is given - a
            :class:`~openstack.image.v2.image.Image` instance.
        """

        image = self._get_resource(_image.Image, image)

        return image.download(
            self,
            stream=stream,
            output=output,
            chunk_size=chunk_size,
        )

    def _update_image_properties(self, image, meta, properties):
        properties.update(meta)
        img_props = {}
        for k, v in iter(properties.items()):
            if image.properties.get(k, None) != v:
                img_props[f'x-image-meta-{k}'] = v
        if not img_props:
            return False
        self.put(f'/images/{image.id}', headers=img_props)
        return True

    def update_image_properties(
        self,
        image=None,
        meta=None,
        **kwargs,
    ):
        """
        Update the properties of an existing image.

        :param image: Name or id of an image or an Image object.
        :param meta: A dict of key/value pairs to use for metadata that
            bypasses automatic type conversion.

        Additional kwargs will be passed to the image creation as additional
        metadata for the image and will have all values converted to string
        except for min_disk, min_ram, size and virtual_size which will be
        converted to int.
        """

        if isinstance(image, str):
            image = self._connection.get_image(image)

        if not meta:
            meta = {}

        img_props = {}
        for k, v in iter(kwargs.items()):
            if v and k in ['ramdisk', 'kernel']:
                v = self._connection.get_image_id(v)
                k = f'{k}_id'
            img_props[k] = v

        return self._update_image_properties(image, meta, img_props)

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: ty.Optional[list[str]] = None,
        interval: ty.Union[int, float, None] = 2,
        wait: ty.Optional[int] = None,
        attribute: str = 'status',
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :return: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int = 2,
        wait: int = 120,
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)
