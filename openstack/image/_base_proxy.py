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
import abc
import os


from openstack import exceptions
from openstack import proxy


class BaseImageProxy(proxy.Proxy, metaclass=abc.ABCMeta):

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

    def create_image(
        self, name, filename=None,
        container=None,
        md5=None, sha256=None,
        disk_format=None, container_format=None,
        disable_vendor_agent=True,
        allow_duplicates=False, meta=None,
        wait=False, timeout=3600,
        data=None, validate_checksum=False,
        use_import=False,
        stores=None,
        all_stores=None,
        all_stores_must_succeed=None,
        **kwargs,
    ):
        """Upload an image.

        :param str name: Name of the image to create. If it is a pathname
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
        :param bool disable_vendor_agent: Whether or not to append metadata
            flags to the image to inform the cloud in question to not expect a
            vendor agent to be runing. (optional, defaults to True)
        :param allow_duplicates: If true, skips checks that enforce unique
            image name. (optional, defaults to False)
        :param meta: A dict of key/value pairs to use for metadata that
            bypasses automatic type conversion.
        :param bool wait: If true, waits for image to be created. Defaults to
            true - however, be aware that one of the upload methods is always
            synchronous.
        :param timeout: Seconds to wait for image creation. None is forever.
        :param bool validate_checksum: If true and cloud returns checksum,
            compares return value with the one calculated or passed into this
            call. If value does not match - raises exception. Default is
            'false'
        :param bool use_import: Use the interoperable image import mechanism
            to import the image. This defaults to false because it is harder on
            the target cloud so should only be used when needed, such as when
            the user needs the cloud to transform image format. If the cloud
            has disabled direct uploads, this will default to true.
        :param stores:
            List of stores to be used when enabled_backends is activated
            in glance. List values can be the id of a store or a
            :class:`~openstack.image.v2.service_info.Store` instance.
            Implies ``use_import`` equals ``True``.
        :param all_stores:
            Upload to all available stores. Mutually exclusive with
            ``store`` and ``stores``.
            Implies ``use_import`` equals ``True``.
        :param all_stores_must_succeed:
            When set to True, if an error occurs during the upload in at
            least one store, the worfklow fails, the data is deleted
            from stores where copying is done (not staging), and the
            state of the image is unchanged. When set to False, the
            workflow will fail (data deleted from stores, …) only if the
            import fails on all stores specified by the user. In case of
            a partial success, the locations added to the image will be
            the stores where the data has been correctly uploaded.
            Default is True.
            Implies ``use_import`` equals ``True``.

        Additional kwargs will be passed to the image creation as additional
        metadata for the image and will have all values converted to string
        except for min_disk, min_ram, size and virtual_size which will be
        converted to int.

        If you are sure you have all of your data types correct or have an
        advanced need to be explicit, use meta. If you are just a normal
        consumer, using kwargs is likely the right choice.

        If a value is in meta and kwargs, meta wins.

        :returns: A ``munch.Munch`` of the Image object

        :raises: SDKException if there are problems uploading
        """
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
            raise exceptions.SDKException(
                'Passing filename and data simultaneously is not supported')
        # If there is no filename, see if name is actually the filename
        if not filename and not data:
            name, filename = self._get_name_and_filename(
                name, self._connection.config.config['image_format'])
        if validate_checksum and data and not isinstance(data, bytes):
            raise exceptions.SDKException(
                'Validating checksum is not possible when data is not a '
                'direct binary object')
        if not (md5 or sha256) and validate_checksum:
            if filename:
                (md5, sha256) = self._connection._get_file_hashes(filename)
            elif data and isinstance(data, bytes):
                (md5, sha256) = self._connection._calculate_data_hashes(data)
        if allow_duplicates:
            current_image = None
        else:
            current_image = self.find_image(name)
            if current_image:
                # NOTE(pas-ha) 'properties' may be absent or be None
                props = current_image.get('properties') or {}
                md5_key = props.get(
                    self._IMAGE_MD5_KEY,
                    props.get(self._SHADE_IMAGE_MD5_KEY, ''))
                sha256_key = props.get(
                    self._IMAGE_SHA256_KEY,
                    props.get(self._SHADE_IMAGE_SHA256_KEY, ''))
                up_to_date = self._connection._hashes_up_to_date(
                    md5=md5, sha256=sha256,
                    md5_key=md5_key, sha256_key=sha256_key)
                if up_to_date:
                    self.log.debug(
                        "image %(name)s exists and is up to date",
                        {'name': name})
                    return current_image
                else:
                    self.log.debug(
                        "image %(name)s exists, but contains different "
                        "checksums. Updating.",
                        {'name': name})

        if disable_vendor_agent:
            kwargs.update(
                self._connection.config.config['disable_vendor_agent'])

        # If a user used the v1 calling format, they will have
        # passed a dict called properties along
        properties = kwargs.pop('properties', {})
        properties[self._IMAGE_MD5_KEY] = md5 or ''
        properties[self._IMAGE_SHA256_KEY] = sha256 or ''
        properties[self._IMAGE_OBJECT_KEY] = '/'.join(
            [container, name])
        kwargs.update(properties)
        image_kwargs = dict(properties=kwargs)
        if disk_format:
            image_kwargs['disk_format'] = disk_format
        if container_format:
            image_kwargs['container_format'] = container_format

        if filename or data:
            image = self._upload_image(
                name, filename=filename, data=data, meta=meta,
                wait=wait, timeout=timeout,
                validate_checksum=validate_checksum,
                use_import=use_import,
                stores=stores,
                all_stores=stores,
                all_stores_must_succeed=stores,
                **image_kwargs)
        else:
            image_kwargs['name'] = name
            image = self._create_image(**image_kwargs)
        self._connection._get_cache(None).invalidate()
        return image

    @abc.abstractmethod
    def _create_image(self, name, **image_kwargs):
        pass

    @abc.abstractmethod
    def _upload_image(
        self, name, filename, data, meta, wait, timeout,
        validate_checksum=True, use_import=False,
        stores=None,
        all_stores=None,
        all_stores_must_succeed=None,
        **image_kwargs
    ):
        pass

    @abc.abstractmethod
    def _update_image_properties(self, image, meta, properties):
        pass

    def update_image_properties(
            self, image=None, meta=None, **kwargs):
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

        if image is None:
            image = self._connection.get_image(image)

        if not meta:
            meta = {}

        img_props = {}
        for k, v in iter(kwargs.items()):
            if v and k in ['ramdisk', 'kernel']:
                v = self._connection.get_image_id(v)
                k = '{0}_id'.format(k)
            img_props[k] = v

        return self._update_image_properties(image, meta, img_props)

    def _get_name_and_filename(self, name, image_format):
        # See if name points to an existing file
        if os.path.exists(name):
            # Neat. Easy enough
            return (os.path.splitext(os.path.basename(name))[0], name)

        # Try appending the disk format
        name_with_ext = '.'.join((name, image_format))
        if os.path.exists(name_with_ext):
            return (os.path.basename(name), name_with_ext)

        return (name, None)
