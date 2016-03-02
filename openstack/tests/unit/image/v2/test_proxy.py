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
        self.verify_create(self.proxy.create_member, member.Member,
                           method_kwargs={'image': 'image_1'},
                           expected_kwargs={'path_args': {
                               'image_id': 'image_1'}})

    def test_member_create_attrs_with_image_instance(self):
        image_1 = image.Image.from_id('image_1')
        self.verify_create(self.proxy.create_member, member.Member,
                           method_kwargs={'image': image_1},
                           expected_kwargs={'path_args': {
                               'image_id': 'image_1'}})

    def test_member_delete(self):
        self.verify_delete(self.proxy.delete_member, member.Member, False,
                           input_path_args=['resource_or_id', 'image_1'],
                           expected_path_args={'image_id': 'image_1'})

    def test_member_delete_ignore(self):
        self.verify_delete(self.proxy.delete_member, member.Member, True,
                           input_path_args=['resource_or_id', 'image_1'],
                           expected_path_args={'image_id': 'image_1'})

    def test_member_delete_with_image_instance(self):
        image_1 = image.Image.from_id('image_1')
        self.verify_delete(self.proxy.delete_member, member.Member, True,
                           input_path_args=['resource_or_id', image_1],
                           expected_path_args={'image_id': 'image_1'})

    def test_member_delete_with_member_instance(self):
        member_1 = member.Member.from_id('member_1')
        member_1.image_id = 'image_1'
        self._verify2('openstack.proxy.BaseProxy._delete',
                      self.proxy.delete_member,
                      method_args=[member_1],
                      expected_args=[member.Member, member_1],
                      expected_kwargs={'path_args': {
                          'image_id': 'image_1'},
                          'ignore_missing': True})

    def test_member_update(self):
        self.verify_update(self.proxy.update_member, member.Member,
                           ['resource_or_id', 'image_1'],
                           path_args={'image_id': 'image_1'})

    def test_member_update_with_image_instance(self):
        image_1 = image.Image.from_id('image_1')
        self.verify_update(self.proxy.update_member, member.Member,
                           ['resource_or_id', image_1],
                           path_args={'image_id': 'image_1'})

    def test_member_update_with_member_instance(self):
        member_1 = member.Member.from_id('member_1')
        member_1.image_id = 'image_1'
        self.verify_update(self.proxy.update_member, member.Member,
                           [member_1], path_args={'image_id': 'image_1'},
                           expected_args=[member_1])

    def test_member_get(self):
        self.verify_get(self.proxy.get_member, member.Member,
                        ['member_1', 'image_1'],
                        expected_args=[member.Member, 'member_1'],
                        expected_kwargs={'path_args': {'image_id': 'image_1'}})

    def test_member_get_with_image_instance(self):
        image_1 = image.Image.from_id('image_1')
        self.verify_get(self.proxy.get_member, member.Member,
                        ['member_1', image_1],
                        expected_args=[member.Member, 'member_1'],
                        expected_kwargs={'path_args': {'image_id': 'image_1'}})

    def test_member_get_with_member_instance(self):
        member_1 = member.Member.from_id('member_1')
        member_1.image_id = 'image_1'
        self.verify_get(self.proxy.get_member, member.Member,
                        [member_1], expected_args=[member.Member, member_1],
                        expected_kwargs={'path_args': {'image_id': 'image_1'}})

    def test_member_find(self):
        self.verify_find(self.proxy.find_member, member.Member,
                         ['name_or_id', 'image_1'],
                         path_args={'image_id': 'image_1'})

    def test_member_find_with_image_instance(self):
        image_1 = image.Image.from_id('image_1')
        self.verify_find(self.proxy.find_member, member.Member,
                         ['name_or_id', image_1],
                         path_args={'image_id': 'image_1'})

    def test_members(self):
        self.verify_list(self.proxy.members, member.Member, paginated=False,
                         method_args=('image_1',),
                         expected_kwargs={
                             'path_args': {'image_id': 'image_1'}})

    def test_members_with_image_instance(self):
        image_1 = image.Image.from_id('image_1')
        self.verify_list(self.proxy.members, member.Member, paginated=False,
                         method_args=(image_1,),
                         expected_kwargs={
                             'path_args': {'image_id': 'image_1'}})

    def test_tag_create_attrs(self):
        self.verify_create(self.proxy.create_tag, tag.Tag)

    def test_tag_delete(self):
        self.verify_delete(self.proxy.delete_tag, tag.Tag, False)

    def test_tag_delete_ignore(self):
        self.verify_delete(self.proxy.delete_tag, tag.Tag, True)
