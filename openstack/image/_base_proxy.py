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

import six

from openstack import proxy


class BaseImageProxy(six.with_metaclass(abc.ABCMeta, proxy.Proxy)):

    retriable_status_codes = [503]

    def create_image(
            self, name, filename=None,
            container=None,
            md5=None, sha256=None,
            disk_format=None, container_format=None,
            disable_vendor_agent=True,
            allow_duplicates=False, meta=None,
            wait=False, timeout=3600,
            **kwargs):
        """Upload an image.

        :param str name: Name of the image to create. If it is a pathname
                         of an image, the name will be constructed from the
                         extensionless basename of the path.
        :param str filename: The path to the file to upload, if needed.
                             (optional, defaults to None)
        :param str container: Name of the container in swift where images
                              should be uploaded for import if the cloud
                              requires such a thing. (optiona, defaults to
                              'images')
        :param str md5: md5 sum of the image file. If not given, an md5 will
                        be calculated.
        :param str sha256: sha256 sum of the image file. If not given, an md5
                           will be calculated.
        :param str disk_format: The disk format the image is in. (optional,
                                defaults to the os-client-config config value
                                for this cloud)
        :param str container_format: The container format the image is in.
                                     (optional, defaults to the
                                     os-client-config config value for this
                                     cloud)
        :param bool disable_vendor_agent: Whether or not to append metadata
                                          flags to the image to inform the
                                          cloud in question to not expect a
                                          vendor agent to be runing.
                                          (optional, defaults to True)
        :param allow_duplicates: If true, skips checks that enforce unique
                                 image name. (optional, defaults to False)
        :param meta: A dict of key/value pairs to use for metadata that
                     bypasses automatic type conversion.
        :param bool wait: If true, waits for image to be created. Defaults to
                          true - however, be aware that one of the upload
                          methods is always synchronous.
        :param timeout: Seconds to wait for image creation. None is forever.

        Additional kwargs will be passed to the image creation as additional
        metadata for the image and will have all values converted to string
        except for min_disk, min_ram, size and virtual_size which will be
        converted to int.

        If you are sure you have all of your data types correct or have an
        advanced need to be explicit, use meta. If you are just a normal
        consumer, using kwargs is likely the right choice.

        If a value is in meta and kwargs, meta wins.

        :returns: A ``munch.Munch`` of the Image object

        :raises: OpenStackCloudException if there are problems uploading
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

        # If there is no filename, see if name is actually the filename
        if not filename:
            name, filename = self._connection._get_name_and_filename(name)
        if not (md5 or sha256):
            (md5, sha256) = self._connection._get_file_hashes(filename)
        if allow_duplicates:
            current_image = None
        else:
            current_image = self._connection.get_image(name)
            if current_image:
                md5_key = current_image.get(
                    self._connection._IMAGE_MD5_KEY,
                    current_image.get(
                        self._connection._SHADE_IMAGE_MD5_KEY, ''))
                sha256_key = current_image.get(
                    self._connection._IMAGE_SHA256_KEY,
                    current_image.get(
                        self._connection._SHADE_IMAGE_SHA256_KEY, ''))
                up_to_date = self._connection._hashes_up_to_date(
                    md5=md5, sha256=sha256,
                    md5_key=md5_key, sha256_key=sha256_key)
                if up_to_date:
                    self._connection.log.debug(
                        "image %(name)s exists and is up to date",
                        {'name': name})
                    return current_image
        kwargs[self._connection._IMAGE_MD5_KEY] = md5 or ''
        kwargs[self._connection._IMAGE_SHA256_KEY] = sha256 or ''
        kwargs[self._connection._IMAGE_OBJECT_KEY] = '/'.join(
            [container, name])

        if disable_vendor_agent:
            kwargs.update(
                self._connection.config.config['disable_vendor_agent'])

        # If a user used the v1 calling format, they will have
        # passed a dict called properties along
        properties = kwargs.pop('properties', {})
        kwargs.update(properties)
        image_kwargs = dict(properties=kwargs)
        if disk_format:
            image_kwargs['disk_format'] = disk_format
        if container_format:
            image_kwargs['container_format'] = container_format

        image = self._upload_image(
            name, filename,
            wait=wait, timeout=timeout,
            meta=meta, **image_kwargs)
        self._connection._get_cache(None).invalidate()
        return image

    @abc.abstractmethod
    def _upload_image(self, name, filename, meta, **image_kwargs):
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
