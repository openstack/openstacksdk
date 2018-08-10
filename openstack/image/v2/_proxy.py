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

from openstack import exceptions
from openstack.image.v2 import image as _image
from openstack.image.v2 import member as _member
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):

    def upload_image(self, container_format=None, disk_format=None,
                     data=None, **attrs):
        """Upload a new image from attributes

        :param container_format: Format of the container.
                                 A valid value is ami, ari, aki, bare,
                                 ovf, ova, or docker.
        :param disk_format: The format of the disk. A valid value is ami,
                            ari, aki, vhd, vmdk, raw, qcow2, vdi, or iso.
        :param data: The data to be uploaded as an image.
        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.image.v2.image.Image`,
                           comprised of the properties on the Image class.

        :returns: The results of image creation
        :rtype: :class:`~openstack.image.v2.image.Image`
        """
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

    def download_image(self, image, stream=False):
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

        :returns: The bytes comprising the given Image when stream is
                  False, otherwise a :class:`requests.Response`
                  instance.
        """

        image = self._get_resource(_image.Image, image)
        return image.download(self, stream=stream)

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

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of image objects
        :rtype: :class:`~openstack.image.v2.image.Image`
        """
        return self._list(_image.Image, paginated=True, **query)

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
        return self._list(_member.Member, paginated=False,
                          image_id=image_id)

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
