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

    def test_image_delete(self):
        self.verify_delete2(image.Image, self.proxy.delete_image, False)

    def test_image_delete_ignore(self):
        self.verify_delete2(image.Image, self.proxy.delete_image, True)

    def test_image_update(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_image,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[image.Image, "resource_or_id"],
                            expected_kwargs=kwargs)

    def test_member_delete(self):
        self.verify_delete2(member.Member, self.proxy.delete_member, False)

    def test_member_delete_ignore(self):
        self.verify_delete2(member.Member, self.proxy.delete_member, True)

    def test_member_update(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_member,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[member.Member, "resource_or_id"],
                            expected_kwargs=kwargs)

    def test_tag_delete(self):
        self.verify_delete2(tag.Tag, self.proxy.delete_tag, False)

    def test_tag_delete_ignore(self):
        self.verify_delete2(tag.Tag, self.proxy.delete_tag, True)
