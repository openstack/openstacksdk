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

from openstack.image.v1 import image
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def create_image(self, **data):
        return image.Image(data).create(self.session)

    def delete_image(self, value, ignore_missing=True):
        """Delete an image

        :param value: The value can be either the ID of an image or a
                      :class:`~openstack.image.v1.image.Image` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the image does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(image.Image, value, ignore_missing)

    def find_image(self, name_or_id):
        return image.Image.find(self.session, name_or_id)

    def get_image(self, **data):
        return image.Image(data).get(self.session)

    def list_images(self, **params):
        return image.Image.list(self.session, **params)

    def update_image(self, **data):
        return image.Image(data).update(self.session)
