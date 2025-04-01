# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import typing as ty
import warnings

from openstack.cloud import _utils
from openstack.cloud import openstackcloud
from openstack import exceptions
from openstack import utils
from openstack import warnings as os_warnings

if ty.TYPE_CHECKING:
    import concurrent.futures
    from keystoneauth1 import session as ks_session
    from oslo_config import cfg

    from openstack.config import cloud_region
    from openstack import service_description


class ImageCloudMixin(openstackcloud._OpenStackCloudMixin):
    def __init__(
        self,
        cloud: ty.Optional[str] = None,
        config: ty.Optional['cloud_region.CloudRegion'] = None,
        session: ty.Optional['ks_session.Session'] = None,
        app_name: ty.Optional[str] = None,
        app_version: ty.Optional[str] = None,
        extra_services: ty.Optional[
            list['service_description.ServiceDescription']
        ] = None,
        strict: bool = False,
        use_direct_get: ty.Optional[bool] = None,
        task_manager: ty.Any = None,
        rate_limit: ty.Union[float, dict[str, float], None] = None,
        oslo_conf: ty.Optional['cfg.ConfigOpts'] = None,
        service_types: ty.Optional[list[str]] = None,
        global_request_id: ty.Optional[str] = None,
        strict_proxies: bool = False,
        pool_executor: ty.Optional['concurrent.futures.Executor'] = None,
        **kwargs: ty.Any,
    ):
        super().__init__(
            cloud=cloud,
            config=config,
            session=session,
            app_name=app_name,
            app_version=app_version,
            extra_services=extra_services,
            strict=strict,
            use_direct_get=use_direct_get,
            task_manager=task_manager,
            rate_limit=rate_limit,
            oslo_conf=oslo_conf,
            service_types=service_types,
            global_request_id=global_request_id,
            strict_proxies=strict_proxies,
            pool_executor=pool_executor,
            **kwargs,
        )

        self.image_api_use_tasks = self.config.config['image_api_use_tasks']

    def search_images(self, name_or_id=None, filters=None):
        images = self.list_images()
        return _utils._filter_list(images, name_or_id, filters)

    def list_images(self, filter_deleted=True, show_all=False):
        """Get available images.

        :param filter_deleted: Control whether deleted images are returned.
        :param show_all: Show all images, including images that are shared
            but not accepted. (By default in glance v2 shared image that
            have not been accepted are not shown) show_all will override the
            value of filter_deleted to False.
        :returns: A list of glance images.
        """
        if show_all:
            filter_deleted = False
        # First, try to actually get images from glance, it's more efficient
        images = []
        params = {}
        image_list = []
        if utils.supports_version(self.image, '2'):
            if show_all:
                params['member_status'] = 'all'
        image_list = list(self.image.images(**params))

        for image in image_list:
            # The cloud might return DELETED for invalid images.
            # While that's cute and all, that's an implementation detail.
            if not filter_deleted:
                images.append(image)
            elif image.status.lower() != 'deleted':
                images.append(image)
        return images

    def get_image(self, name_or_id, filters=None):
        """Get an image by name or ID.

        :param name_or_id: Name or ID of the image.
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :returns: An image :class:`openstack.image.v2.image.Image` object.
        """
        if filters is not None:
            warnings.warn(
                "The 'filters' argument is deprecated; use 'search_images' "
                "instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_images(name_or_id, filters)
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

            return entities[0]

        return self.image.find_image(name_or_id)

    def get_image_by_id(self, id):
        """Get a image by ID

        :param id: ID of the image.
        :returns: An image :class:`openstack.image.v2.image.Image` object.
        """
        return self.image.get_image(id)

    def download_image(
        self,
        name_or_id,
        output_path=None,
        output_file=None,
        chunk_size=1024 * 1024,
        stream=False,
    ):
        """Download an image by name or ID

        :param str name_or_id: Name or ID of the image.
        :param output_path: the output path to write the image to. Either this
            or output_file must be specified
        :param output_file: a file object (or file-like object) to write the
            image data to. Only write() will be called on this object. Either
            this or output_path must be specified
        :param int chunk_size: size in bytes to read from the wire and buffer
            at one time. Defaults to 1024 * 1024 = 1 MiB
        :param: bool stream: whether to stream the output in chunk_size.

        :returns: When output_path and output_file are not given - the bytes
            comprising the given Image when stream is False, otherwise a
            :class:`requests.Response` instance. When output_path or
            output_file are given - an image
            :class:`~openstack.image.v2.image.Image` instance.
        :raises: :class:`~openstack.exceptions.SDKException` in the event
            download_image is called without exactly one of either output_path
            or output_file
        :raises: :class:`~openstack.exceptions.BadRequestException` if no
            images are found matching the name or ID provided
        """
        if output_path is None and output_file is None:
            raise exceptions.SDKException(
                'No output specified, an output path or file object '
                'is necessary to write the image data to'
            )
        elif output_path is not None and output_file is not None:
            raise exceptions.SDKException(
                'Both an output path and file object were provided, '
                'however only one can be used at once'
            )

        image = self.image.find_image(name_or_id, ignore_missing=False)

        return self.image.download_image(
            image,
            output=output_file or output_path,
            chunk_size=chunk_size,
            stream=stream,
        )

    def get_image_exclude(self, name_or_id, exclude):
        for image in self.search_images(name_or_id):
            if exclude:
                if exclude not in image.name:
                    return image
            else:
                return image
        return None

    def get_image_name(self, image_id, exclude=None):
        image = self.get_image_exclude(image_id, exclude)
        if image:
            return image.name
        return None

    def get_image_id(self, image_name, exclude=None):
        image = self.get_image_exclude(image_name, exclude)
        if image:
            return image.id
        return None

    def wait_for_image(self, image, timeout=3600):
        image_id = image['id']
        for count in utils.iterate_timeout(
            timeout, "Timeout waiting for image to snapshot"
        ):
            image = self.get_image(image_id)
            if not image:
                continue
            if image['status'] == 'active':
                return image
            elif image['status'] == 'error':
                raise exceptions.SDKException(
                    f'Image {image_id} hit error state'
                )

    def delete_image(
        self,
        name_or_id,
        wait=False,
        timeout=3600,
        delete_objects=True,
    ):
        """Delete an existing image.

        :param name_or_id: Name of the image to be deleted.
        :param wait: If True, waits for image to be deleted.
        :param timeout: Seconds to wait for image deletion. None is forever.
        :param delete_objects: If True, also deletes uploaded swift objects.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` if there are
            problems deleting.
        """
        image = self.get_image(name_or_id)
        if not image:
            return False
        self.image.delete_image(image)

        # Task API means an image was uploaded to swift
        # TODO(gtema) does it make sense to move this into proxy?
        if self.image_api_use_tasks and (
            self.image._IMAGE_OBJECT_KEY in image.properties
            or self.image._SHADE_IMAGE_OBJECT_KEY in image.properties
        ):
            container, objname = image.properties.get(
                self.image._IMAGE_OBJECT_KEY,
                image.properties.get(self.image._SHADE_IMAGE_OBJECT_KEY),
            ).split('/', 1)
            self.object_store.delete_object(
                objname,
                container=container,
            )

        if wait:
            for count in utils.iterate_timeout(
                timeout, "Timeout waiting for the image to be deleted."
            ):
                if self.get_image(image.id) is None:
                    break
        return True

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
        wait=False,
        timeout=3600,
        tags=None,
        allow_duplicates=False,
        meta=None,
        volume=None,
        **kwargs,
    ):
        """Upload an image.

        :param str name: Name of the image to create. If it is a pathname
            of an image, the name will be constructed from the
            extensionless basename of the path.
        :param str filename: The path to the file to upload, if needed.
            (optional, defaults to None)
        :param str container: Name of the container in swift where images
            should be uploaded for import if the cloud requires such a thing.
            (optiona, defaults to 'images')
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
        :param bool wait: If true, waits for image to be created. Defaults to
            true - however, be aware that one of the upload methods is always
            synchronous.
        :param timeout: Seconds to wait for image creation. None is forever.
        :param allow_duplicates: If true, skips checks that enforce unique
            image name. (optional, defaults to False)
        :param meta: A dict of key/value pairs to use for metadata that
            bypasses automatic type conversion.
        :param volume: Name or ID or volume object of a volume to create an
            image from. Mutually exclusive with (optional, defaults to None)

        Additional kwargs will be passed to the image creation as additional
        metadata for the image and will have all values converted to string
        except for min_disk, min_ram, size and virtual_size which will be
        converted to int.

        If you are sure you have all of your data types correct or have an
        advanced need to be explicit, use meta. If you are just a normal
        consumer, using kwargs is likely the right choice.

        If a value is in meta and kwargs, meta wins.

        :returns: An image :class:`openstack.image.v2.image.Image` object.
        :raises: :class:`~openstack.exceptions.SDKException` if there are
            problems uploading
        """
        if volume:
            image = self.block_storage.create_image(
                name=name,
                volume=volume,
                allow_duplicates=allow_duplicates,
                container_format=container_format,
                disk_format=disk_format,
                wait=wait,
                timeout=timeout,
            )
        else:
            image = self.image.create_image(
                name,
                filename=filename,
                container=container,
                md5=md5,
                sha256=sha256,
                disk_format=disk_format,
                container_format=container_format,
                disable_vendor_agent=disable_vendor_agent,
                wait=wait,
                timeout=timeout,
                tags=tags,
                allow_duplicates=allow_duplicates,
                meta=meta,
                **kwargs,
            )

        if not wait:
            return image

        try:
            for count in utils.iterate_timeout(
                timeout, "Timeout waiting for the image to finish."
            ):
                image_obj = self.get_image(image.id)
                if image_obj and image_obj.status not in ('queued', 'saving'):
                    return image_obj
        except exceptions.ResourceTimeout:
            self.log.debug(
                "Timeout waiting for image to become ready. Deleting."
            )
            self.delete_image(image.id, wait=True)
            raise

    def update_image_properties(
        self, image=None, name_or_id=None, meta=None, **properties
    ):
        image = image or name_or_id
        return self.image.update_image_properties(
            image=image, meta=meta, **properties
        )
