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

from openstack.image.v1 import _proxy
from openstack.image.v1 import image
from openstack.tests.unit import test_proxy_base2 as test_proxy_base


class TestImageProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestImageProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_image_upload_attrs(self):
        self.verify_create(self.proxy.upload_image, image.Image)

    def test_image_delete(self):
        self.verify_delete(self.proxy.delete_image, image.Image, False)

    def test_image_delete_ignore(self):
        self.verify_delete(self.proxy.delete_image, image.Image, True)

    def test_image_find(self):
        self.verify_find(self.proxy.find_image, image.Image)

    def test_image_get(self):
        self.verify_get(self.proxy.get_image, image.Image)

    def test_images(self):
        self.verify_list(self.proxy.images, image.Image, paginated=True)

    def test_image_update(self):
        self.verify_update(self.proxy.update_image, image.Image)
