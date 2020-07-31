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

import time
import warnings

from openstack import exceptions
from openstack.image import _base_proxy
from openstack.image.v2 import image as _image
from openstack.image.v2 import member as _member
from openstack.image.v2 import schema as _schema
from openstack.image.v2 import task as _task
from openstack.image.v2 import service_info as _si
from openstack import resource
from openstack import utils

# Rackspace returns this for intermittent import errors
_IMAGE_ERROR_396 = "Image cannot be imported. Error code: '396'"
_INT_PROPERTIES = ('min_disk', 'min_ram', 'size', 'virtual_size')
_RAW_PROPERTIES = ('protected', 'tags')


class Proxy(_base_proxy.BaseImageProxy):

    def _create_image(self, **kwargs):
        """Create image resource from attributes
        """
        return self._create(_image.Image, **kwargs)

    def import_image(
        self, image, method='glance-direct', uri=None,
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

        :param image:
            The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param method:
            Method to use for importing the image.
            A valid value is glance-direct or web-download.
        :param uri:
            Required only if using the web-download import method.
            This url is where the data is made available to the Image
            service.
        :param store:
            Used when enabled_backends is activated in glance. The value
            can be the id of a store or a
            :class:`~openstack.image.v2.service_info.Store` instance.
        :param stores:
            List of stores to be used when enabled_backends is activated
            in glance. List values can be the id of a store or a
            :class:`~openstack.image.v2.service_info.Store` instance.
        :param all_stores:
            Upload to all available stores. Mutually exclusive with
            ``store`` and ``stores``.
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

        :returns: None
        """
        image = self._get_resource(_image.Image, image)
        if all_stores and (store or stores):
            raise exceptions.InvalidRequest(
                "all_stores is mutually exclusive with"
                " store and stores")
        if store is not None:
            if stores:
                raise exceptions.InvalidRequest(
                    "store and stores are mutually exclusive")
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
                "Both container_format and disk_format are required for"
                " importing an image")

        image.import_image(
            self, method=method, uri=uri,
            store=store,
            stores=stores,
            all_stores=all_stores,
            all_stores_must_succeed=all_stores_must_succeed,
        )

    def stage_image(self, image, filename=None, data=None):
        """Stage binary image data

        :param image: The value can be the ID of a image or a
            :class:`~openstack.image.v2.image.Image` instance.
        :param filename: Optional name of the file to read data from.
        :param data: Optional data to be uploaded as an image.

        :returns: The results of image creation
        :rtype: :class:`~openstack.image.v2.image.Image`
        """
        image = self._get_resource(_image.Image, image)

        if 'queued' != image.status:
            raise exceptions.SDKException('Image stage is only possible for '
                                          'images in the queued state.'
                                          ' Current state is {status}'
                                          .format(status=image.status))

        if filename:
            image.data = open(filename, 'rb')
        elif data:
            image.data = data
        image.stage(self)

        # Stage does not return content, but updates the object
        image.fetch(self)

        return image

    def upload_image(self, container_format=None, disk_format=None,
                     data=None, **attrs):
        """Create and upload a new image from attributes

        .. warning:
          This method is deprecated - and also doesn't work very well.
          Please stop using it immediately and switch to
          `create_image`.

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
        warnings.warn("upload_image is deprecated. Use create_image instead.")
        # container_format and disk_format are required to be set
        # on the image by the time upload_image is called, but they're not
        # required by the _create call. Enforce them here so that we don't
        # need to handle a failure in _create, as upload_image will
        # return a 400 with a message about disk_format and container_format
        # not being set.
        if not all([container_format, disk_format]):
            raise exceptions.InvalidRequest(
                "Both container_format and disk_format are required")

        img = self._create(_image.Image, disk_format=disk_format,
                           container_format=container_format,
                           **attrs)

        # TODO(briancurtin): Perhaps we should run img.upload_image
        # in a background thread and just return what is called by
        # self._create, especially because the upload_image call doesn't
        # return anything anyway. Otherwise this blocks while uploading
        # significant amounts of image data.
        img.data = data
        img.upload(self)

        return img

    def _upload_image(
        self, name, filename=None, data=None, meta=None,
        wait=False, timeout=None, validate_checksum=True,
        use_import=False,
        stores=None,
        all_stores=None,
        all_stores_must_succeed=None,
        **kwargs
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
                        "The Glance Task API and Import API are"
                        " mutually exclusive. Either disable"
                        " image_api_use_tasks in config, or"
                        " do not request using import")
                return self._upload_image_task(
                    name, filename, data=data, meta=meta,
                    wait=wait, timeout=timeout, **kwargs)
            else:
                return self._upload_image_put(
                    name, filename, data=data, meta=meta,
                    validate_checksum=validate_checksum,
                    use_import=use_import,
                    stores=stores,
                    all_stores=all_stores,
                    all_stores_must_succeed=all_stores_must_succeed,
                    **kwargs)
        except exceptions.SDKException:
            self.log.debug("Image creation failed", exc_info=True)
            raise
        except Exception as e:
            raise exceptions.SDKException(
                "Image creation failed: {message}".format(message=str(e)))

    def _make_v2_image_params(self, meta, properties):
        ret = {}
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
        self, name, filename, data, meta,
        validate_checksum, use_import=False,
        stores=None,
        all_stores=None,
        all_stores_must_succeed=None,
        **image_kwargs,
    ):
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
        if stores or all_stores or all_stores_must_succeed:
            use_import = True
        if use_import and not supports_import:
            raise exceptions.SDKException(
                "Importing image was requested but the cloud does not"
                " support the image import method.")

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
                    valid = (checksum == md5 or checksum == sha256)
                    if not valid:
                        raise Exception('Image checksum verification failed')
        except Exception:
            self.log.debug(
                "Deleting failed upload of image %s", name)
            self.delete_image(image.id)
            raise

        return image

    def _upload_image_task(
            self, name, filename, data,
            wait, timeout, meta, **image_kwargs):

        if not self._connection.has_service('object-store'):
            raise exceptions.SDKException(
                "The cloud {cloud} is configured to use tasks for image"
                " upload, but no object-store service is available."
                " Aborting.".format(cloud=self._connection.config.name))
        properties = image_kwargs.get('properties', {})
        md5 = properties[self._IMAGE_MD5_KEY]
        sha256 = properties[self._IMAGE_SHA256_KEY]
        container = properties[self._IMAGE_OBJECT_KEY].split('/', 1)[0]
        image_kwargs.pop('disk_format', None)
        image_kwargs.pop('container_format', None)

        self._connection.create_container(container)
        self._connection.create_object(
            container, name, filename,
            md5=md5, sha256=sha256,
            data=data,
            metadata={self._connection._OBJECT_AUTOCREATE_KEY: 'true'},
            **{'content-type': 'application/octet-stream',
               'x-delete-after': str(24 * 60 * 60)})
        # TODO(mordred): Can we do something similar to what nodepool does
        # using glance properties to not delete then upload but instead make a
        # new "good" image and then mark the old one as "bad"
        task_args = dict(
            type='import', input=dict(
                import_from='{container}/{name}'.format(
                    container=container, name=name),
                image_properties=dict(name=name)))

        glance_task = self.create_task(**task_args)
        self._connection.list_images.invalidate(self)
        if wait:
            start = time.time()

            try:
                glance_task = self.wait_for_task(
                    task=glance_task,
                    status='success',
                    wait=timeout)

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
                    glance_task.id, image_id, (time.time() - start))
            except exceptions.ResourceFailure as e:
                glance_task = self.get_task(glance_task)
                raise exceptions.SDKException(
                    "Image creation failed: {message}".format(
                        message=e.message),
                    extra_data=glance_task)
            finally:
                # Clean up after ourselves. The object we created is not
                # needed after the import is done.
                self._connection.delete_object(container, name)
                self._connection.list_images.invalidate(self)
            return image
        else:
            return glance_task

    def _update_image_properties(self, image, meta, properties):
        if not isinstance(image, _image.Image):
            # If we come here with a dict (cloud) - convert dict to real object
            # to properly consume all properties (to calculate the diff).
            # This currently happens from unittests.
            image = _image.Image.existing(**image)
        img_props = image.properties.copy()

        for k, v in iter(self._make_v2_image_params(meta, properties).items()):
            if image.get(k, None) != v:
                img_props[k] = v
        if not img_props:
            return False

        self.update_image(image, **img_props)

        self._connection.list_images.invalidate(self._connection)
        return True

    def _existing_image(self, **kwargs):
        return _image.Image.existing(connection=self._connection, **kwargs)

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

    def delete_image(self, image, ignore_missing=True):
        """Delete an image

        :param image: The value can be either the ID of an image or a
                      :class:`~openstack.image.v2.image.Image` instance.
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
        :returns: One :class:`~openstack.image.v2.image.Image` or None
        """
        return self._find(_image.Image, name_or_id,
                          ignore_missing=ignore_missing)

    def get_image(self, image):
        """Get a single image

        :param image: The value can be the ID of a image or a
                      :class:`~openstack.image.v2.image.Image` instance.

        :returns: One :class:`~openstack.image.v2.image.Image`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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
        :attrs kwargs: The attributes to update on the image represented
                       by ``value``.

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
        """Deactivate an image

        :param image: Either the ID of a image or a
                      :class:`~openstack.image.v2.image.Image` instance.

        :returns: None
        """
        image = self._get_resource(_image.Image, image)
        image.reactivate(self)

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

    def add_member(self, image, **attrs):
        """Create a new member from attributes

        :param image: The value can be the ID of a image or a
                      :class:`~openstack.image.v2.image.Image` instance
                      that the member will be created for.
        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.image.v2.member.Member`,
                           comprised of the properties on the Member class.

        :returns: The results of member creation
        :rtype: :class:`~openstack.image.v2.member.Member`
        """
        image_id = resource.Resource._get_id(image)
        return self._create(_member.Member, image_id=image_id, **attrs)

    def remove_member(self, member, image, ignore_missing=True):
        """Delete a member

        :param member: The value can be either the ID of a member or a
                       :class:`~openstack.image.v2.member.Member` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the member does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent member.

        :returns: ``None``
        """
        image_id = resource.Resource._get_id(image)
        member_id = resource.Resource._get_id(member)
        self._delete(_member.Member, member_id=member_id, image_id=image_id,
                     ignore_missing=ignore_missing)

    def find_member(self, name_or_id, image, ignore_missing=True):
        """Find a single member

        :param name_or_id: The name or ID of a member.
        :param image: This is the image that the member belongs to,
                      the value can be the ID of a image or a
                      :class:`~openstack.image.v2.image.Image` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.image.v2.member.Member` or None
        """
        image_id = resource.Resource._get_id(image)
        return self._find(_member.Member, name_or_id, image_id=image_id,
                          ignore_missing=ignore_missing)

    def get_member(self, member, image):
        """Get a single member on an image

        :param member: The value can be the ID of a member or a
                       :class:`~openstack.image.v2.member.Member` instance.
        :param image: This is the image that the member belongs to.
                      The value can be the ID of a image or a
                      :class:`~openstack.image.v2.image.Image` instance.
        :returns: One :class:`~openstack.image.v2.member.Member`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        member_id = resource.Resource._get_id(member)
        image_id = resource.Resource._get_id(image)
        return self._get(_member.Member, member_id=member_id,
                         image_id=image_id)

    def members(self, image):
        """Return a generator of members

        :param image: This is the image that the member belongs to,
                      the value can be the ID of a image or a
                      :class:`~openstack.image.v2.image.Image` instance.

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
        :attrs kwargs: The attributes to update on the member represented
                       by ``value``.

        :returns: The updated member
        :rtype: :class:`~openstack.image.v2.member.Member`
        """
        member_id = resource.Resource._get_id(member)
        image_id = resource.Resource._get_id(image)
        return self._update(_member.Member, member_id=member_id,
                            image_id=image_id, **attrs)

    def get_images_schema(self):
        """Get images schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_schema.Schema, requires_id=False,
                         base_path='/schemas/images')

    def get_image_schema(self):
        """Get single image schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_schema.Schema, requires_id=False,
                         base_path='/schemas/image')

    def get_members_schema(self):
        """Get image members schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_schema.Schema, requires_id=False,
                         base_path='/schemas/members')

    def get_member_schema(self):
        """Get image member schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_schema.Schema, requires_id=False,
                         base_path='/schemas/member')

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
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
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

    def wait_for_task(self, task, status='success', failures=None,
                      interval=2, wait=120):
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

        name = "{res}:{id}".format(res=task.__class__.__name__, id=task.id)
        msg = "Timeout waiting for {name} to transition to {status}".format(
            name=name, status=status)

        for count in utils.iterate_timeout(
                timeout=wait,
                message=msg,
                wait=interval):
            task = task.fetch(self)

            if not task:
                raise exceptions.ResourceFailure(
                    "{name} went away while waiting for {status}".format(
                        name=name, status=status))

            new_status = task.status
            normalized_status = new_status.lower()
            if normalized_status == status.lower():
                return task
            elif normalized_status in failures:
                if task.message == _IMAGE_ERROR_396:
                    task_args = dict(input=task.input, type=task.type)
                    task = self.create_task(**task_args)
                    self.log.debug('Got error 396. Recreating task %s' % task)
                else:
                    raise exceptions.ResourceFailure(
                        "{name} transitioned to failure state {status}".format(
                            name=name, status=new_status))

            self.log.debug('Still waiting for resource %s to reach state %s, '
                           'current state is %s', name, status, new_status)

    def get_tasks_schema(self):
        """Get image tasks schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_schema.Schema, requires_id=False,
                         base_path='/schemas/tasks')

    def get_task_schema(self):
        """Get image task schema

        :returns: One :class:`~openstack.image.v2.schema.Schema`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_schema.Schema, requires_id=False,
                         base_path='/schemas/task')

    def stores(self, **query):
        """Return a generator of supported image stores

        :returns: A generator of store objects
        :rtype: :class:`~openstack.image.v2.service_info.Store`
        """
        return self._list(_si.Store, **query)

    def get_import_info(self):
        """Get a info about image constraints

        :returns: One :class:`~openstack.image.v2.service_info.Import`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_si.Import, require_id=False)
