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
import time
import typing as ty
import warnings

from openstack import exceptions
from openstack.image.v2 import cache as _cache
from openstack.image.v2 import image as _image
from openstack.image.v2 import member as _member
from openstack.image.v2 import metadef_namespace as _metadef_namespace
from openstack.image.v2 import metadef_object as _metadef_object
from openstack.image.v2 import metadef_property as _metadef_property
from openstack.image.v2 import metadef_resource_type as _metadef_resource_type
from openstack.image.v2 import metadef_schema as _metadef_schema
from openstack.image.v2 import schema as _schema
from openstack.image.v2 import service_info as _si
from openstack.image.v2 import task as _task
from openstack import proxy
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings

# Rackspace returns this for intermittent import errors
_IMAGE_ERROR_396 = "Image cannot be imported. Error code: '396'"
_INT_PROPERTIES = ('min_disk', 'min_ram', 'size', 'virtual_size')
_RAW_PROPERTIES = ('is_protected', 'protected', 'tags')


def _get_name_and_filename(name, image_format):
    # See if name points to an existing file
    if os.path.exists(name) and os.path.isfile(name):
        # Neat. Easy enough
        return os.path.splitext(os.path.basename(name))[0], name

    # Try appending the disk format
    name_with_ext = '.'.join((name, image_format))
    if os.path.exists(name_with_ext) and os.path.isfile(name):
        return os.path.basename(name), name_with_ext

    return name, None


class Proxy(proxy.Proxy):
    _resource_registry = {
        "cache": _cache.Cache,
        "image": _image.Image,
        "image_member": _member.Member,
        "metadef_namespace": _metadef_namespace.MetadefNamespace,
        "metadef_resource_type": _metadef_resource_type.MetadefResourceType,
        "metadef_resource_type_association": _metadef_resource_type.MetadefResourceTypeAssociation,  # noqa
        "schema": _schema.Schema,
        "info_import": _si.Import,
        "info_store": _si.Store,
        "task": _task.Task,
    }

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

    # ====== CACHE MANAGEMENT======
    def get_image_cache(self):
        return self._get(_cache.Cache, requires_id=False)

    def cache_delete_image(self, image, ignore_missing=True):
        """Delete an image from cache.

        :param image: The value can be either the name of an image or a
            :class:`~openstack.image.v2.image.Image`
            instance.
        :param bool ignore_missing: When set to ``False``,
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the metadef namespace does not exist.
        :returns: ``None``
        """
        return self._delete(_cache.Cache, image, ignore_missing=ignore_missing)

    def queue_image(self, image_id):
        """Queue image(s) for caching."""
        cache = self._get_resource(_cache.Cache, None)
        return cache.queue(self, image_id)

    def clear_cache(self, target='both'):
        """Clear all images from cache, queue or both

        :param target: Specify which target you want to clear
            One of: ``both``(default), ``cache``, ``queue``.
        """
        cache = self._get_resource(_cache.Cache, None)
        return cache.clear(self, target)

    # ====== IMAGES ======

    def create_image(
        self,
        name,
        *,
        filename=None,
        data=None,
        container=None,
        md5=None,
        sha256=None,
        disk_format=None,
        container_format=None,
        tags=None,
        disable_vendor_agent=True,
        allow_duplicates=False,
        meta=None,
        wait=False,
        timeout=3600,
        validate_checksum=False,
        use_import=False,
        stores=None,
        all_stores=None,
        all_stores_must_succeed=None,
        **kwargs,
    ):
        """Create an image and optionally upload data

        Create a new image. If ``filename`` or ``data`` are provided, it will
        also upload data to this image.

        Note that uploading image data is actually quite a complicated
        procedure. There are three ways to upload an image:

        * Image upload
        * Image import
        * Image tasks

        If the image tasks API is enabled, this must be used. However, this API
        is deprecated since the Image service's Mitaka (12.0.0) release and is
        now admin-only. Assuming this API is not enabled, you may choose
        between image upload or image import. Image import is more powerful and
        allows you to upload data from multiple sources including other glance
        instances. It should be preferred on all services that support it.

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
        :param list tags: List of tags for this image. Each tag is a string
            of at most 255 chars.
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
        :param bool use_import: Use the 'glance-direct' method of the
            interoperable image import mechanism to import the image. This
            defaults to false because it is harder on the target cloud so
            should only be used when needed, such as when the user needs the
            cloud to transform image format. If the cloud has disabled direct
            uploads, this will default to true. If you wish to use other import
            methods, use the ``import_image`` method instead.
        :param stores: List of stores to be used when enabled_backends is
            activated in glance. List values can be the id of a store or a
            :class:`~openstack.image.v2.service_info.Store` instance.
            Implies ``use_import`` equals ``True``.
        :param all_stores: Upload to all available stores. Mutually exclusive
            with ``store`` and ``stores``.
            Implies ``use_import`` equals ``True``.
        :param all_stores_must_succeed: When set to True, if an error occurs
            during the upload in at least one store, the worfklow fails, the
            data is deleted from stores where copying is done (not staging),
            and the state of the image is unchanged. When set to False, the
            workflow will fail (data deleted from stores, …) only if the import
            fails on all stores specified by the user. In case of a partial
            success, the locations added to the image will be the stores where
            the data has been correctly uploaded.
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

        :returns: The results of image creation
        :rtype: :class:`~openstack.image.v2.image.Image`
        :raises: SDKException if there are problems uploading
        """
        if filename and data:
            raise exceptions.SDKException(
                'filename and data are mutually exclusive'
            )

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
        if not filename and not data:
            name, filename = _get_name_and_filename(
                name,
                self._connection.config.config['image_format'],
            )

        if validate_checksum and data and not isinstance(data, bytes):
            raise exceptions.SDKException(
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
                wait=wait,
                timeout=timeout,
                validate_checksum=validate_checksum,
                use_import=use_import,
                stores=stores,
                all_stores=all_stores,
                all_stores_must_succeed=all_stores_must_succeed,
                **image_kwargs,
            )
        else:
            properties = image_kwargs.pop('properties', {})
            image_kwargs.update(self._make_v2_image_params(meta, properties))
            image_kwargs['name'] = name
            image = self._create(_image.Image, **image_kwargs)  # type: ignore[arg-type]

        return image

    def import_image(
        self,
        image,
        method='glance-direct',
        *,
        uri=None,
        remote_region=None,
        remote_image_id=None,
        remote_service_interface=None,
        store=None,
        stores=None,
        all_stores=None,
        all_stores_must_succeed=None,
    ):
        """Import data to an existing image

        Interoperable image import process are introduced in the Image API
        v2.6. It mainly allow image importing from an external url and let
        Image Service download it by itself without sending binary data at
        image creation.

        :param image: The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param method: Method to use for importing the image. Not all
            deployments support all methods. One of: ``glance-direct``
            (default), ``web-download``, ``glance-download``, or
            ``copy-image``. Use of ``glance-direct`` requires the image be
            first staged.
        :param uri: Required only if using the ``web-download`` import method.
            This url is where the data is made available to the Image
            service.
        :param remote_region: The remote glance region to download the image
            from when using glance-download.
        :param remote_image_id: The ID of the image to import from the
            remote glance when using glance-download.
        :param remote_service_interface: The remote glance service interface to
            use when using glance-download.
        :param store: Used when enabled_backends is activated in glance. The
            value can be the id of a store or a.
            :class:`~openstack.image.v2.service_info.Store` instance.
        :param stores: List of stores to be used when enabled_backends is
            activated in glance. List values can be the id of a store or a
            :class:`~openstack.image.v2.service_info.Store` instance.
        :param all_stores: Upload to all available stores. Mutually exclusive
            with ``store`` and ``stores``.
        :param all_stores_must_succeed: When set to True, if an error occurs
            during the upload in at least one store, the worfklow fails, the
            data is deleted from stores where copying is done (not staging),
            and the state of the image is unchanged. When set to False, the
            workflow will fail (data deleted from stores, …) only if the
            import fails on all stores specified by the user. In case of
            a partial success, the locations added to the image will be
            the stores where the data has been correctly uploaded.
            Default is True.

        :returns: The raw response from the request.
        """
        image = self._get_resource(_image.Image, image)

        if all_stores and (store or stores):
            raise exceptions.InvalidRequest(
                "all_stores is mutually exclusive with store and stores"
            )

        if store is not None:
            if stores:
                raise exceptions.InvalidRequest(
                    "store and stores are mutually exclusive"
                )
            store = self._get_resource(_si.Store, store)

        stores = stores or []
        new_stores = []
        for s in stores:
            new_stores.append(self._get_resource(_si.Store, s))
        stores = new_stores

        # as for the standard image upload function, container_format and
        # disk_format are required for using image import process
        if not all([image.container_format, image.disk_format]):
            raise exceptions.InvalidRequest(
                "Both container_format and disk_format are required for "
                "importing an image"
            )

        return image.import_image(
            self,
            method=method,
            uri=uri,
            remote_region=remote_region,
            remote_image_id=remote_image_id,
            remote_service_interface=remote_service_interface,
            store=store,
            stores=stores,
            all_stores=all_stores,
            all_stores_must_succeed=all_stores_must_succeed,
        )

    def stage_image(self, image, *, filename=None, data=None):
        """Stage binary image data

        :param image: The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param filename: Optional name of the file to read data from.
        :param data: Optional data to be uploaded as an image.

        :returns: The results of image creation
        :rtype: :class:`~openstack.image.v2.image.Image`
        """
        if filename and data:
            raise exceptions.SDKException(
                'filename and data are mutually exclusive'
            )

        image = self._get_resource(_image.Image, image)

        if 'queued' != image.status:
            raise exceptions.SDKException(
                'Image stage is only possible for images in the queued state. '
                f'Current state is {image.status}'
            )

        if filename:
            image.data = open(filename, 'rb')
        elif data:
            image.data = data
        image.stage(self)

        # Stage does not return content, but updates the object
        image.fetch(self)

        return image

    def upload_image(
        self,
        container_format=None,
        disk_format=None,
        data=None,
        **attrs,
    ):
        """Create and upload a new image from attributes

        .. warning:

           This method is deprecated - and also doesn't work very well.
           Please stop using it immediately and switch to `create_image`.

        :param container_format: Format of the container.
            A valid value is ami, ari, aki, bare, ovf, ova, or docker.
        :param disk_format: The format of the disk. A valid value is ami,
            ari, aki, vhd, vmdk, raw, qcow2, vdi, or iso.
        :param data: The data to be uploaded as an image.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.image.v2.image.Image`, comprised of the
            properties on the Image class.

        :returns: The results of image creation
        :rtype: :class:`~openstack.image.v2.image.Image`
        """
        warnings.warn(
            "upload_image is deprecated. Use create_image instead.",
            os_warnings.RemovedInSDK50Warning,
        )
        # container_format and disk_format are required to be set
        # on the image by the time upload_image is called, but they're not
        # required by the _create call. Enforce them here so that we don't
        # need to handle a failure in _create, as upload_image will
        # return a 400 with a message about disk_format and container_format
        # not being set.
        if not all([container_format, disk_format]):
            raise exceptions.InvalidRequest(
                "Both container_format and disk_format are required"
            )

        img = self._create(
            _image.Image,
            disk_format=disk_format,
            container_format=container_format,
            **attrs,
        )

        # TODO(briancurtin): Perhaps we should run img.upload_image
        # in a background thread and just return what is called by
        # self._create, especially because the upload_image call doesn't
        # return anything anyway. Otherwise this blocks while uploading
        # significant amounts of image data.
        img.data = data
        img.upload(self)

        return img

    def _upload_image(
        self,
        name,
        *,
        filename=None,
        data=None,
        meta=None,
        wait=False,
        timeout=None,
        validate_checksum=True,
        use_import=False,
        stores=None,
        all_stores=None,
        all_stores_must_succeed=None,
        **kwargs,
    ):
        # We can never have nice things. Glance v1 took "is_public" as a
        # boolean. Glance v2 takes "visibility". If the user gives us
        # is_public, we know what they mean. If they give us visibility, they
        # know that they mean.
        if 'is_public' in kwargs['properties']:
            is_public = kwargs['properties'].pop('is_public')
            if is_public:
                kwargs['visibility'] = 'public'
            else:
                kwargs['visibility'] = 'private'

        try:
            # This makes me want to die inside
            if self._connection.image_api_use_tasks:
                if use_import:
                    raise exceptions.SDKException(
                        "The Glance Task API and Import API are mutually "
                        "exclusive. Either disable image_api_use_tasks in "
                        "config, or do not request using import"
                    )
                return self._upload_image_task(
                    name,
                    filename,
                    data=data,
                    meta=meta,
                    wait=wait,
                    timeout=timeout,
                    **kwargs,
                )
            else:
                return self._upload_image_put(
                    name,
                    filename,
                    data=data,
                    meta=meta,
                    validate_checksum=validate_checksum,
                    use_import=use_import,
                    stores=stores,
                    all_stores=all_stores,
                    all_stores_must_succeed=all_stores_must_succeed,
                    **kwargs,
                )
        except exceptions.SDKException:
            self.log.debug("Image creation failed", exc_info=True)
            raise
        except Exception as e:
            raise exceptions.SDKException(f"Image creation failed: {str(e)}")

    def _make_v2_image_params(self, meta, properties):
        ret: dict = {}
        for k, v in iter(properties.items()):
            if k in _INT_PROPERTIES:
                ret[k] = int(v)
            elif k in _RAW_PROPERTIES:
                ret[k] = v
            else:
                if v is None:
                    ret[k] = None
                else:
                    ret[k] = str(v)
        ret.update(meta)
        return ret

    def _upload_image_put(
        self,
        name,
        filename,
        data,
        meta,
        validate_checksum,
        use_import=False,
        stores=None,
        all_stores=None,
        all_stores_must_succeed=None,
        **image_kwargs,
    ):
        # use of any of these imply use_import=True
        if stores or all_stores or all_stores_must_succeed:
            use_import = True

        if filename and not data:
            image_data = open(filename, 'rb')
        else:
            image_data = data

        properties = image_kwargs.pop('properties', {})

        image_kwargs.update(self._make_v2_image_params(meta, properties))
        image_kwargs['name'] = name

        image = self._create(_image.Image, **image_kwargs)
        image.data = image_data

        supports_import = (
            image.image_import_methods
            and 'glance-direct' in image.image_import_methods
        )
        if use_import and not supports_import:
            raise exceptions.SDKException(
                "Importing image was requested but the cloud does not "
                "support the image import method."
            )

        try:
            if not use_import:
                response = image.upload(self)
                exceptions.raise_from_response(response)
            if use_import:
                image.stage(self)
                image.import_image(self)

            # image_kwargs are flat here
            md5 = image_kwargs.get(self._IMAGE_MD5_KEY)
            sha256 = image_kwargs.get(self._IMAGE_SHA256_KEY)
            if validate_checksum and (md5 or sha256):
                # Verify that the hash computed remotely matches the local
                # value
                data = image.fetch(self)
                checksum = data.get('checksum')
                if checksum:
                    valid = checksum == md5 or checksum == sha256
                    if not valid:
                        raise Exception('Image checksum verification failed')
        except Exception:
            self.log.debug("Deleting failed upload of image %s", name)
            self.delete_image(image.id)
            raise

        return image

    def _upload_image_task(
        self,
        name,
        filename,
        data,
        wait,
        timeout,
        meta,
        **image_kwargs,
    ):
        if not self._connection.has_service('object-store'):
            raise exceptions.SDKException(
                f"The cloud {self._connection.config.name} is configured to use tasks for image "
                "upload, but no object-store service is available. "
                "Aborting."
            )

        properties = image_kwargs.get('properties', {})
        md5 = properties[self._IMAGE_MD5_KEY]
        sha256 = properties[self._IMAGE_SHA256_KEY]
        container = properties[self._IMAGE_OBJECT_KEY].split('/', 1)[0]
        image_kwargs.pop('disk_format', None)
        image_kwargs.pop('container_format', None)

        self._connection.create_container(container)
        self._connection.create_object(
            container,
            name,
            filename,
            md5=md5,
            sha256=sha256,
            data=data,
            metadata={self._connection._OBJECT_AUTOCREATE_KEY: 'true'},
            **{
                'content-type': 'application/octet-stream',
                'x-delete-after': str(24 * 60 * 60),
            },
        )
        # TODO(mordred): Can we do something similar to what nodepool does
        # using glance properties to not delete then upload but instead make a
        # new "good" image and then mark the old one as "bad"
        task_args = {
            'type': 'import',
            'input': {
                'import_from': f'{container}/{name}',
                'image_properties': {'name': name},
            },
        }

        glance_task = self.create_task(**task_args)
        if wait:
            start = time.time()

            try:
                glance_task = self.wait_for_task(
                    task=glance_task, status='success', wait=timeout
                )

                image_id = glance_task.result['image_id']
                image = self.get_image(image_id)
                # NOTE(gtema): Since we might move unknown attributes of
                # the image under properties - merge current with update
                # properties not to end up removing "existing" properties
                props = image.properties.copy()
                props.update(image_kwargs.pop('properties', {}))
                image_kwargs['properties'] = props

                image = self.update_image(image, **image_kwargs)
                self.log.debug(
                    "Image Task %s imported %s in %s",
                    glance_task.id,
                    image_id,
                    (time.time() - start),
                )
            except exceptions.ResourceFailure as e:
                glance_task = self.get_task(glance_task)
                raise exceptions.SDKException(
                    f"Image creation failed: {e.message}",
                    extra_data=glance_task,
                )
            finally:
                # Clean up after ourselves. The object we created is not
                # needed after the import is done.
                self._connection.delete_object(container, name)
            return image
        else:
            return glance_task

    def _existing_image(self, **kwargs):
        return _image.Image.existing(connection=self._connection, **kwargs)

    def download_image(
        self,
        image,
        *,
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
            instance allowing you to iterate over the response data stream
            instead of storing its entire contents in memory. See
            :meth:`requests.Response.iter_content` for more details.

            *NOTE*: If you do not consume the entirety of the response you must
            explicitly call :meth:`requests.Response.close` or otherwise risk
            inefficiencies with the ``requests`` library's handling of
            connections.

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

    def delete_image(self, image, *, store=None, ignore_missing=True):
        """Delete an image

        :param image: The value can be either the ID of an image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param store: The value can be either the ID of a store or a
            :class:`~openstack.image.v2.service_info.Store` instance that the
            image is associated with. If specified, the image will only be
            deleted from the specified store.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the image does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent image.

        :returns: ``None``
        """
        if store:
            store = self._get_resource(_si.Store, store)
            store.delete_image(self, image, ignore_missing=ignore_missing)
        else:
            self._delete(_image.Image, image, ignore_missing=ignore_missing)

    def find_image(self, name_or_id, ignore_missing=True):
        """Find a single image

        :param name_or_id: The name or ID of a image.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.image.v2.image.Image` or None
        """
        return self._find(
            _image.Image,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def get_image(self, image):
        """Get a single image

        :param image: The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.

        :returns: One :class:`~openstack.image.v2.image.Image`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_image.Image, image)

    def images(self, **query):
        """Return a generator of images

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of image objects
        :rtype: :class:`~openstack.image.v2.image.Image`
        """
        return self._list(_image.Image, **query)

    def update_image(self, image, **attrs):
        """Update a image

        :param image: Either the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param attrs: The attributes to update on the image represented
            by ``image``.

        :returns: The updated image
        :rtype: :class:`~openstack.image.v2.image.Image`
        """
        return self._update(_image.Image, image, **attrs)

    def deactivate_image(self, image):
        """Deactivate an image

        :param image: Either the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.

        :returns: None
        """
        image = self._get_resource(_image.Image, image)
        image.deactivate(self)

    def reactivate_image(self, image):
        """Reactivate an image

        :param image: Either the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.

        :returns: None
        """
        image = self._get_resource(_image.Image, image)
        image.reactivate(self)

    def update_image_properties(
        self,
        image=None,
        meta=None,
        **kwargs,
    ):
        """Update the properties of an existing image

        :param image: The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param meta: A dict of key/value pairs to use for metadata that
            bypasses automatic type conversion.

        Additional kwargs will be passed to the image creation as additional
        metadata for the image and will have all values converted to string
        except for min_disk, min_ram, size and virtual_size which will be
        converted to int.
        """
        image = self._get_resource(_image.Image, image)

        if not meta:
            meta = {}

        properties = {}
        for k, v in iter(kwargs.items()):
            if v and k in ['ramdisk', 'kernel']:
                v = self._connection.get_image_id(v)
                k = f'{k}_id'
            properties[k] = v

        img_props = image.properties.copy()

        for k, v in iter(self._make_v2_image_params(meta, properties).items()):
            if image.get(k, None) != v:
                img_props[k] = v
        if not img_props:
            return False

        self.update_image(image, **img_props)

        return True

    def add_tag(self, image, tag):
        """Add a tag to an image

        :param image: The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance
            that the member will be created for.
        :param str tag: The tag to be added

        :returns: None
        """
        image = self._get_resource(_image.Image, image)
        image.add_tag(self, tag)

    def remove_tag(self, image, tag):
        """Remove a tag to an image

        :param image: The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance
            that the member will be created for.
        :param str tag: The tag to be removed

        :returns: None
        """
        image = self._get_resource(_image.Image, image)
        image.remove_tag(self, tag)

    # ====== IMAGE MEMBERS ======
    def add_member(self, image, **attrs):
        """Create a new member from attributes

        :param image: The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance
            that the member will be created for.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.image.v2.member.Member`,
            comprised of the properties on the Member class.

        See `Image Sharing Reference
        <https://docs.openstack.org/api-ref/image/v2/index.html?expanded=create-image-member-detail#create-image-member>`__
        for details.

        :returns: The results of member creation
        :rtype: :class:`~openstack.image.v2.member.Member`
        """
        image_id = resource.Resource._get_id(image)
        return self._create(_member.Member, image_id=image_id, **attrs)

    def remove_member(self, member, image=None, ignore_missing=True):
        """Delete a member

        :param member: The value can be either the ID of a member or a
            :class:`~openstack.image.v2.member.Member` instance.
        :param image: The value can be either the ID of an image or a
            :class:`~openstack.image.v2.image.Image` instance that the member
            is part of. This is required if ``member`` is an ID.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the member does not exist. When set to ``True``, no exception will
            be set when attempting to delete a nonexistent member.

        :returns: ``None``
        """
        image_id = resource.Resource._get_id(image)
        member_id = resource.Resource._get_id(member)
        self._delete(
            _member.Member,
            None,
            member_id=member_id,
            image_id=image_id,
            ignore_missing=ignore_missing,
        )

    def find_member(self, name_or_id, image, ignore_missing=True):
        """Find a single member

        :param name_or_id: The name or ID of a member.
        :param image: This is the image that the member belongs to,
            the value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.image.v2.member.Member` or None
        """
        image_id = resource.Resource._get_id(image)
        return self._find(
            _member.Member,
            name_or_id,
            image_id=image_id,
            ignore_missing=ignore_missing,
        )

    def get_member(self, member, image):
        """Get a single member on an image

        :param member: The value can be the ID of a member or a
            :class:`~openstack.image.v2.member.Member` instance.
        :param image: This is the image that the member belongs to.
            The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :returns: One :class:`~openstack.image.v2.member.Member`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        member_id = resource.Resource._get_id(member)
        image_id = resource.Resource._get_id(image)
        return self._get(
            _member.Member, member_id=member_id, image_id=image_id
        )

    def members(self, image, **query):
        """Return a generator of members

        :param image: This is the image that the member belongs to,
            the value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of member objects
        :rtype: :class:`~openstack.image.v2.member.Member`
        """
        image_id = resource.Resource._get_id(image)
        return self._list(_member.Member, image_id=image_id)

    def update_member(self, member, image, **attrs):
        """Update the member of an image

        :param member: Either the ID of a member or a
            :class:`~openstack.image.v2.member.Member` instance.
        :param image: This is the image that the member belongs to.
            The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param attrs: The attributes to update on the member represented
            by ``member``.

        See `Image Sharing Reference
        <https://docs.openstack.org/api-ref/image/v2/index.html?expanded=update-image-member-detail#update-image-member>`__
        for details.

        :returns: The updated member
        :rtype: :class:`~openstack.image.v2.member.Member`
        """
        member_id = resource.Resource._get_id(member)
        image_id = resource.Resource._get_id(image)
        return self._update(
            _member.Member,
            None,
            member_id=member_id,
            image_id=image_id,
            **attrs,
        )

    # ====== METADEF NAMESPACES ======
    def create_metadef_namespace(self, **attrs):
        """Create a new metadef namespace from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            comprised of the properties on the MetadefNamespace class.

        :returns: The results of metadef namespace creation
        :rtype: :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
        """
        return self._create(_metadef_namespace.MetadefNamespace, **attrs)

    def delete_metadef_namespace(self, metadef_namespace, ignore_missing=True):
        """Delete a metadef namespace

        :param metadef_namespace: The value can be either the name of a metadef
            namespace or a
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.
        :param bool ignore_missing: When set to ``False``,
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the metadef namespace does not exist.
        :returns: ``None``
        """
        self._delete(
            _metadef_namespace.MetadefNamespace,
            metadef_namespace,
            ignore_missing=ignore_missing,
        )

    # NOTE(stephenfin): There is no 'find_metadef_namespace' since namespaces
    # are identified by the namespace name, not an arbitrary UUID, meaning
    # 'find_metadef_namespace' would be identical to 'get_metadef_namespace'

    def get_metadef_namespace(self, metadef_namespace):
        """Get a single metadef namespace

        :param metadef_namespace: Either the name of a metadef namespace or an
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.

        :returns: One
            :class:`~~openstack.image.v2.metadef_namespace.MetadefNamespace`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(
            _metadef_namespace.MetadefNamespace,
            metadef_namespace,
        )

    def metadef_namespaces(self, **query):
        """Return a generator of metadef namespaces

        :returns: A generator object of metadef namespaces
        :rtype: :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._list(_metadef_namespace.MetadefNamespace, **query)

    def update_metadef_namespace(self, metadef_namespace, **attrs):
        """Update a server

        :param metadef_namespace: Either the name of a metadef namespace or an
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.
        :param attrs: The attributes to update on the metadef namespace
            represented by ``metadef_namespace``.

        :returns: The updated metadef namespace
        :rtype: :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
        """
        # rather annoyingly, Glance insists on us providing the 'namespace'
        # argument, even if we're not changing it...
        if 'namespace' not in attrs:
            attrs['namespace'] = resource.Resource._get_id(metadef_namespace)

        return self._update(
            _metadef_namespace.MetadefNamespace,
            metadef_namespace,
            **attrs,
        )

    # ====== METADEF OBJECT ======
    def create_metadef_object(self, namespace, **attrs):
        """Create a new object from namespace

        :param namespace: The value can be either the name of a metadef
            namespace or a
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.image.v2.metadef_object.MetadefObject`,
            comprised of the properties on the Metadef object class.

        :returns: A metadef namespace
        :rtype: :class:`~openstack.image.v2.metadef_object.MetadefObject`
        """
        namespace_name = resource.Resource._get_id(namespace)
        return self._create(
            _metadef_object.MetadefObject,
            namespace_name=namespace_name,
            **attrs,
        )

    def get_metadef_object(self, metadef_object, namespace):
        """Get a single metadef object

        :param metadef_object: The value can be the ID of a metadef_object
            or a
            :class:`~openstack.image.v2.metadef_object.MetadefObject`
            instance.
        :param namespace: The value can be either the name of a metadef
            namespace or a
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.
        :returns: One :class:`~openstack.image.v2.metadef_object.MetadefObject`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        object_name = resource.Resource._get_id(metadef_object)
        namespace_name = resource.Resource._get_id(namespace)
        return self._get(
            _metadef_object.MetadefObject,
            namespace_name=namespace_name,
            name=object_name,
        )

    def metadef_objects(self, namespace):
        """Get metadef object list of the namespace

        :param namespace: The value can be either the name of a metadef
            namespace or a
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.

        :returns: One :class:`~openstack.image.v2.metadef_object.MetadefObject`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        namespace_name = resource.Resource._get_id(namespace)
        return self._list(
            _metadef_object.MetadefObject,
            namespace_name=namespace_name,
        )

    def update_metadef_object(self, metadef_object, namespace, **attrs):
        """Update a single metadef object

        :param metadef_object: The value can be the ID of a metadef_object or a
            :class:`~openstack.image.v2.metadef_object.MetadefObject` instance.
        :param namespace: The value can be either the name of a metadef
            namespace or a
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.
        :param dict attrs: Keyword arguments which will be used to update
            a :class:`~openstack.image.v2.metadef_object.MetadefObject`

        :returns: One :class:`~openstack.image.v2.metadef_object.MetadefObject`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        namespace_name = resource.Resource._get_id(namespace)
        metadef_object = resource.Resource._get_id(metadef_object)
        return self._update(
            _metadef_object.MetadefObject,
            metadef_object,
            namespace_name=namespace_name,
            **attrs,
        )

    def delete_metadef_object(self, metadef_object, namespace, **attrs):
        """Removes a single metadef object

        :param metadef_object: The value can be the ID of a metadef_object or a
            :class:`~openstack.image.v2.metadef_object.MetadefObject` instance.
        :param namespace: The value can be either the name of a metadef
            namespace or a
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.
        :param dict attrs: Keyword arguments which will be used to update
            a :class:`~openstack.image.v2.metadef_object.MetadefObject`

        :returns: ``None``
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        namespace_name = resource.Resource._get_id(namespace)
        return self._delete(
            _metadef_object.MetadefObject,
            metadef_object,
            namespace_name=namespace_name,
            **attrs,
        )

    def delete_all_metadef_objects(self, namespace):
        """Delete all objects

        :param namespace: The value can be either the name of a metadef
            namespace or a
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.
        :returns: ``None``
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        namespace = self._get_resource(
            _metadef_namespace.MetadefNamespace, namespace
        )
        return namespace.delete_all_objects(self)

    # ====== METADEF RESOURCE TYPES ======
    def metadef_resource_types(self, **query):
        """Return a generator of metadef resource types

        :return: A generator object of metadef resource types
        :rtype:
            :class:`~openstack.image.v2.metadef_resource_type.MetadefResourceType`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._list(_metadef_resource_type.MetadefResourceType, **query)

    # ====== METADEF RESOURCE TYPES ASSOCIATION======
    def create_metadef_resource_type_association(
        self,
        metadef_namespace,
        **attrs,
    ):
        """Creates a resource type association between a namespace
            and the resource type specified in the body of the request.

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.image.v2.metadef_resource_type.MetadefResourceTypeAssociation`
            comprised of the properties on the
            MetadefResourceTypeAssociation class.

        :returns: The results of metadef resource type association creation
        :rtype:
            :class:`~openstack.image.v2.metadef_resource_type.MetadefResourceTypeAssociation`
        """
        namespace_name = resource.Resource._get_id(metadef_namespace)
        return self._create(
            _metadef_resource_type.MetadefResourceTypeAssociation,
            namespace_name=namespace_name,
            **attrs,
        )

    def delete_metadef_resource_type_association(
        self,
        metadef_resource_type,
        metadef_namespace,
        ignore_missing=True,
    ):
        """Removes a resource type association in a namespace.

        :param metadef_resource_type: The value can be either the name of
            a metadef resource type association or an
            :class:`~openstack.image.v2.metadef_resource_type.MetadefResourceTypeAssociation`
            instance.
        :param metadef_namespace: The value can be either the name of metadef
            namespace or an
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance
        :param bool ignore_missing: When set to ``False``,
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the metadef resource type association does not exist.
        :returns: ``None``
        """
        namespace_name = resource.Resource._get_id(metadef_namespace)
        self._delete(
            _metadef_resource_type.MetadefResourceTypeAssociation,
            metadef_resource_type,
            namespace_name=namespace_name,
            ignore_missing=ignore_missing,
        )

    def metadef_resource_type_associations(self, metadef_namespace, **query):
        """Return a generator of metadef resource type associations

        :param metadef_namespace: The value can be either the name of metadef
            namespace or an
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance
        :return: A generator object of metadef resource type associations
        :rtype:
            :class:`~openstack.image.v2.metadef_resource_type.MetadefResourceTypeAssociation`
        :raises: :class:`~openstack.exceptions.NotFoundException`
                when no resource can be found.
        """
        namespace_name = resource.Resource._get_id(metadef_namespace)
        return self._list(
            _metadef_resource_type.MetadefResourceTypeAssociation,
            namespace_name=namespace_name,
            **query,
        )

    # ====== METADEF PROPERTY ======
    def create_metadef_property(self, metadef_namespace, **attrs):
        """Create a metadef property

        :param metadef_namespace: The value can be either the name of metadef
            namespace or an
            :class:`~openstack.image.v2.metadef_property.MetadefNamespace`
            instance
        :param attrs: The attributes to create on the metadef property
            represented by ``metadef_property``.

        :returns: The created metadef property
        :rtype: :class:`~openstack.image.v2.metadef_property.MetadefProperty`
        """
        namespace_name = resource.Resource._get_id(metadef_namespace)
        return self._create(
            _metadef_property.MetadefProperty,
            namespace_name=namespace_name,
            **attrs,
        )

    def update_metadef_property(
        self, metadef_property, metadef_namespace, **attrs
    ):
        """Update a metadef property

        :param metadef_property: The value can be either the name of metadef
            property or an
            :class:`~openstack.image.v2.metadef_property.MetadefProperty`
            instance.
        :param metadef_namespace: The value can be either the name of metadef
            namespace or an
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance
        :param attrs: The attributes to update on the metadef property
            represented by ``metadef_property``.

        :returns: The updated metadef property
        :rtype: :class:`~openstack.image.v2.metadef_property.MetadefProperty`
        """
        namespace_name = resource.Resource._get_id(metadef_namespace)
        metadef_property = resource.Resource._get_id(metadef_property)
        return self._update(
            _metadef_property.MetadefProperty,
            metadef_property,
            namespace_name=namespace_name,
            **attrs,
        )

    def delete_metadef_property(
        self, metadef_property, metadef_namespace, ignore_missing=True
    ):
        """Delete a metadef property

        :param metadef_property: The value can be either the name of metadef
            property or an
            :class:`~openstack.image.v2.metadef_property.MetadefProperty`
            instance
        :param metadef_namespace: The value can be either the name of metadef
            namespace or an
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance
        :param bool ignore_missing: When set to
            ``False`` :class:`~openstack.exceptions.NotFoundException` will be
            raised when the instance does not exist. When set to ``True``,
            no exception will be set when attempting to delete a nonexistent
            instance.

        :returns: ``None``
        """
        namespace_name = resource.Resource._get_id(metadef_namespace)
        metadef_property = resource.Resource._get_id(metadef_property)
        return self._delete(
            _metadef_property.MetadefProperty,
            metadef_property,
            namespace_name=namespace_name,
            ignore_missing=ignore_missing,
        )

    def metadef_properties(self, metadef_namespace, **query):
        """Return a generator of metadef properties

        :param metadef_namespace: The value can be either the name of metadef
            namespace or an
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of property objects
        """
        namespace_name = resource.Resource._get_id(metadef_namespace)
        return self._list(
            _metadef_property.MetadefProperty,
            requires_id=False,
            namespace_name=namespace_name,
            **query,
        )

    def get_metadef_property(
        self, metadef_property, metadef_namespace, **query
    ):
        """Get a single metadef property

        :param metadef_property: The value can be either the name of metadef
            property or an
            :class:`~openstack.image.v2.metadef_property.MetadefProperty`
            instance.
        :param metadef_namespace: The value can be either the name of metadef
            namespace or an
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance

        :returns: One
            :class:`~~openstack.image.v2.metadef_property.MetadefProperty`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        namespace_name = resource.Resource._get_id(metadef_namespace)
        return self._get(
            _metadef_property.MetadefProperty,
            metadef_property,
            namespace_name=namespace_name,
            **query,
        )

    def delete_all_metadef_properties(self, metadef_namespace):
        """Delete all metadata definitions property inside a specific namespace.

        :param metadef_namespace: The value can be either the name of a metadef
            namespace or a
            :class:`~openstack.image.v2.metadef_namespace.MetadefNamespace`
            instance.

        :returns: ``None``
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        namespace = self._get_resource(
            _metadef_namespace.MetadefNamespace, metadef_namespace
        )
        return namespace.delete_all_properties(self)

    # ====== SCHEMAS ======
    def get_images_schema(self):
        """Get images schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _schema.Schema,
            requires_id=False,
            base_path='/schemas/images',
        )

    def get_image_schema(self):
        """Get single image schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _schema.Schema,
            requires_id=False,
            base_path='/schemas/image',
        )

    def get_members_schema(self):
        """Get image members schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _schema.Schema,
            requires_id=False,
            base_path='/schemas/members',
        )

    def get_member_schema(self):
        """Get image member schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _schema.Schema,
            requires_id=False,
            base_path='/schemas/member',
        )

    def get_tasks_schema(self):
        """Get image tasks schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _schema.Schema,
            requires_id=False,
            base_path='/schemas/tasks',
        )

    def get_task_schema(self):
        """Get image task schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _schema.Schema,
            requires_id=False,
            base_path='/schemas/task',
        )

    def get_metadef_namespace_schema(self):
        """Get metadata definition namespace schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/namespace',
        )

    def get_metadef_namespaces_schema(self):
        """Get metadata definition namespaces schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/namespaces',
        )

    def get_metadef_resource_type_schema(self):
        """Get metadata definition resource type association schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/resource_type',
        )

    def get_metadef_resource_types_schema(self):
        """Get metadata definition resource type associations schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/resource_types',
        )

    def get_metadef_object_schema(self):
        """Get metadata definition object schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/object',
        )

    def get_metadef_objects_schema(self):
        """Get metadata definition objects schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/objects',
        )

    def get_metadef_property_schema(self):
        """Get metadata definition property schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/property',
        )

    def get_metadef_properties_schema(self):
        """Get metadata definition properties schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/properties',
        )

    def get_metadef_tag_schema(self):
        """Get metadata definition tag schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/tag',
        )

    def get_metadef_tags_schema(self):
        """Get metadata definition tags schema

        :returns: One :class:`~openstack.image.v2.metadef_schema.MetadefSchema`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _metadef_schema.MetadefSchema,
            requires_id=False,
            base_path='/schemas/metadefs/tags',
        )

    # ====== TASKS ======
    def tasks(self, **query):
        """Return a generator of tasks

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of task objects
        :rtype: :class:`~openstack.image.v2.task.Task`
        """
        return self._list(_task.Task, **query)

    def get_task(self, task):
        """Get task details

        :param task: The value can be the ID of a task or a
            :class:`~openstack.image.v2.task.Task` instance.

        :returns: One :class:`~openstack.image.v2.task.Task`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_task.Task, task)

    def create_task(self, **attrs):
        """Create a new task from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.image.v2.task.Task`,
            comprised of the properties on the Task class.

        :returns: The results of task creation
        :rtype: :class:`~openstack.image.v2.task.Task`
        """
        return self._create(_task.Task, **attrs)

    def wait_for_task(
        self,
        task,
        status='success',
        failures=None,
        interval=2,
        wait=120,
    ):
        """Wait for a task to be in a particular status.

        :param task: The resource to wait on to reach the specified status.
            The resource must have a ``status`` attribute.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
            checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
            Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute.
        """
        if failures is None:
            failures = ['failure']
        else:
            failures = [f.lower() for f in failures]

        if task.status.lower() == status.lower():
            return task

        name = f"{task.__class__.__name__}:{task.id}"
        msg = f"Timeout waiting for {name} to transition to {status}"

        for count in utils.iterate_timeout(
            timeout=wait, message=msg, wait=interval
        ):
            task = task.fetch(self)

            if not task:
                raise exceptions.ResourceFailure(
                    f"{name} went away while waiting for {status}"
                )

            new_status = task.status
            normalized_status = new_status.lower()
            if normalized_status == status.lower():
                return task
            elif normalized_status in failures:
                if task.message == _IMAGE_ERROR_396:
                    task_args = {'input': task.input, 'type': task.type}
                    task = self.create_task(**task_args)
                    self.log.debug(f'Got error 396. Recreating task {task}')
                else:
                    raise exceptions.ResourceFailure(
                        f"{name} transitioned to failure state {new_status}"
                    )

            self.log.debug(
                'Still waiting for resource %s to reach state %s, '
                'current state is %s',
                name,
                status,
                new_status,
            )

    # ====== STORES ======
    def stores(self, details=False, **query):
        """Return a generator of supported image stores

        :returns: A generator of store objects
        :rtype: :class:`~openstack.image.v2.service_info.Store`
        """
        if details:
            query['base_path'] = utils.urljoin(_si.Store.base_path, 'detail')
        return self._list(_si.Store, **query)

    # ====== IMPORTS ======
    def get_import_info(self):
        """Get a info about image constraints

        :returns: One :class:`~openstack.image.v2.service_info.Import`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_si.Import, requires_id=False)

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

    def _get_cleanup_dependencies(self):
        return {'image': {'before': ['identity']}}

    def _service_cleanup(
        self,
        dry_run=True,
        client_status_queue=None,
        identified_resources=None,
        filters=None,
        resource_evaluation_fn=None,
        skip_resources=None,
    ):
        if self.should_skip_resource_cleanup("image", skip_resources):
            return

        project_id = self.get_project_id()

        # Note that images cannot be deleted when they are still being used
        for obj in self.images(owner=project_id):
            self._service_cleanup_del_res(
                self.delete_image,
                obj,
                dry_run=dry_run,
                client_status_queue=client_status_queue,
                identified_resources=identified_resources,
                filters=filters,
                resource_evaluation_fn=resource_evaluation_fn,
            )
