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

from openstack.image.v2 import image as _image
from openstack.image.v2 import member as _member
from openstack.image.v2 import tag as _tag
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def upload_image(self, **attrs):
        """Upload a new image from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.image.v2.image.Image`,
                           comprised of the properties on the Image class.

        :returns: The results of image creation
        :rtype: :class:`~openstack.image.v2.image.Image`
        """

        data = attrs.pop('data')
        img = self._create(_image.Image, **attrs)

        img.data = data
        img.upload_image(self.session)

        return img

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

        :param image: Either the id of a image or a
                      :class:`~openstack.image.v2.image.Image` instance.
        :attrs kwargs: The attributes to update on the image represented
                       by ``value``.

        :returns: The updated image
        :rtype: :class:`~openstack.image.v2.image.Image`
        """
        return self._update(_image.Image, image, **attrs)

    def create_member(self, **attrs):
        """Create a new member from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.image.v2.member.Member`,
                           comprised of the properties on the Member class.

        :returns: The results of member creation
        :rtype: :class:`~openstack.image.v2.member.Member`
        """
        return self._create(_member.Member, **attrs)

    def delete_member(self, member, ignore_missing=True):
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
        self._delete(_member.Member, member, ignore_missing=ignore_missing)

    def find_member(self, name_or_id, ignore_missing=True):
        """Find a single member

        :param name_or_id: The name or ID of a member.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.image.v2.member.Member` or None
        """
        return self._find(_member.Member, name_or_id,
                          ignore_missing=ignore_missing)

    def get_member(self, member):
        """Get a single member

        :param member: The value can be the ID of a member or a
                       :class:`~openstack.image.v2.member.Member` instance.

        :returns: One :class:`~openstack.image.v2.member.Member`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_member.Member, member)

    def members(self, **query):
        """Return a generator of members

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of member objects
        :rtype: :class:`~openstack.image.v2.member.Member`
        """
        return self._list(_member.Member, paginated=False, **query)

    def update_member(self, member, **attrs):
        """Update a member

        :param member: Either the id of a member or a
                       :class:`~openstack.image.v2.member.Member` instance.
        :attrs kwargs: The attributes to update on the member represented
                       by ``value``.

        :returns: The updated member
        :rtype: :class:`~openstack.image.v2.member.Member`
        """
        return self._update(_member.Member, member, **attrs)

    def create_tag(self, **attrs):
        """Create a new tag from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.image.v2.tag.Tag`,
                           comprised of the properties on the Tag class.

        :returns: The results of tag creation
        :rtype: :class:`~openstack.image.v2.tag.Tag`
        """
        return self._create(_tag.Tag, **attrs)

    def delete_tag(self, tag, ignore_missing=True):
        """Delete a tag

        :param tag: The value can be either the ID of a tag or a
                    :class:`~openstack.image.v2.tag.Tag` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the tag does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent tag.

        :returns: ``None``
        """
        self._delete(_tag.Tag, tag, ignore_missing=ignore_missing)
