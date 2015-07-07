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

from openstack.image.v2 import _proxy
from openstack.image.v2 import image
from openstack.image.v2 import member
from openstack.image.v2 import tag
from openstack.tests.unit import test_proxy_base


class TestImageProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestImageProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_image_create_attrs(self):
        self.verify_create(self.proxy.upload_image, image.Image,
                           method_kwargs={'data': 'Image'},
                           expected_kwargs={},
                           expected_result=image.Image())

    def test_image_delete(self):
        self.verify_delete(self.proxy.delete_image, image.Image, False)

    def test_image_delete_ignore(self):
        self.verify_delete(self.proxy.delete_image, image.Image, True)

    def test_image_update(self):
        self.verify_update(self.proxy.update_image, image.Image)

    def test_image_get(self):
        self.verify_get(self.proxy.get_image, image.Image)

    def test_images(self):
        self.verify_list(self.proxy.images, image.Image, paginated=True)

    def test_member_create_attrs(self):
        self.verify_create(self.proxy.create_member, member.Member)

    def test_member_delete(self):
        self.verify_delete(self.proxy.delete_member, member.Member, False)

    def test_member_delete_ignore(self):
        self.verify_delete(self.proxy.delete_member, member.Member, True)

    def test_member_update(self):
        self.verify_update(self.proxy.update_member, member.Member)

    def test_member_get(self):
        self.verify_get(self.proxy.get_member, member.Member)

    def test_members(self):
        self.verify_list(self.proxy.members, member.Member, paginated=False)

    def test_tag_create_attrs(self):
        self.verify_create(self.proxy.create_tag, tag.Tag)

    def test_tag_delete(self):
        self.verify_delete(self.proxy.delete_tag, tag.Tag, False)

    def test_tag_delete_ignore(self):
        self.verify_delete(self.proxy.delete_tag, tag.Tag, True)
