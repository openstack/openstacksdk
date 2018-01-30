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

import mock

from openstack import exceptions
from openstack.image.v2 import _proxy
from openstack.image.v2 import image
from openstack.image.v2 import member
from openstack.tests.unit.image.v2 import test_image as fake_image
from openstack.tests.unit import test_proxy_base

EXAMPLE = fake_image.EXAMPLE


class TestImageProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestImageProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_image_create_no_args(self):
        # container_format and disk_format are required args
        self.assertRaises(exceptions.InvalidRequest, self.proxy.upload_image)

    def test_image_create(self):
        # NOTE: This doesn't use any of the base class verify methods
        # because it ends up making two separate calls to complete the
        # operation.
        created_image = mock.Mock(spec=image.Image(id="id"))

        self.proxy._create = mock.Mock()
        self.proxy._create.return_value = created_image

        rv = self.proxy.upload_image(data="data", container_format="x",
                                     disk_format="y", name="z")

        self.proxy._create.assert_called_with(image.Image,
                                              container_format="x",
                                              disk_format="y",
                                              name="z")
        created_image.upload.assert_called_with(self.proxy)
        self.assertEqual(rv, created_image)

    def test_image_delete(self):
        self.verify_delete(self.proxy.delete_image, image.Image, False)

    def test_image_delete_ignore(self):
        self.verify_delete(self.proxy.delete_image, image.Image, True)

    @mock.patch("openstack.resource.Resource._translate_response")
    @mock.patch("openstack.proxy.Proxy._get")
    @mock.patch("openstack.image.v2.image.Image.update")
    def test_image_update(self, mock_update_image, mock_get_image,
                          mock_transpose):
        original_image = image.Image(**EXAMPLE)
        mock_get_image.return_value = original_image
        EXAMPLE['name'] = 'fake_name'
        updated_image = image.Image(**EXAMPLE)
        mock_update_image.return_value = updated_image.to_dict()
        result = self.proxy.update_image(original_image,
                                         **updated_image.to_dict())
        self.assertEqual('fake_name', result.get('name'))

    def test_image_get(self):
        self.verify_get(self.proxy.get_image, image.Image)

    def test_images(self):
        self.verify_list(self.proxy.images, image.Image, paginated=True)

    def test_add_tag(self):
        self._verify("openstack.image.v2.image.Image.add_tag",
                     self.proxy.add_tag,
                     method_args=["image", "tag"],
                     expected_args=["tag"])

    def test_remove_tag(self):
        self._verify("openstack.image.v2.image.Image.remove_tag",
                     self.proxy.remove_tag,
                     method_args=["image", "tag"],
                     expected_args=["tag"])

    def test_deactivate_image(self):
        self._verify("openstack.image.v2.image.Image.deactivate",
                     self.proxy.deactivate_image,
                     method_args=["image"])

    def test_reactivate_image(self):
        self._verify("openstack.image.v2.image.Image.reactivate",
                     self.proxy.reactivate_image,
                     method_args=["image"])

    def test_member_create(self):
        self.verify_create(self.proxy.add_member, member.Member,
                           method_kwargs={"image": "test_id"},
                           expected_kwargs={"image_id": "test_id"})

    def test_member_delete(self):
        self._verify2("openstack.proxy.Proxy._delete",
                      self.proxy.remove_member,
                      method_args=["member_id"],
                      method_kwargs={"image": "image_id",
                                     "ignore_missing": False},
                      expected_args=[member.Member],
                      expected_kwargs={"member_id": "member_id",
                                       "image_id": "image_id",
                                       "ignore_missing": False})

    def test_member_delete_ignore(self):
        self._verify2("openstack.proxy.Proxy._delete",
                      self.proxy.remove_member,
                      method_args=["member_id"],
                      method_kwargs={"image": "image_id"},
                      expected_args=[member.Member],
                      expected_kwargs={"member_id": "member_id",
                                       "image_id": "image_id",
                                       "ignore_missing": True})

    def test_member_update(self):
        self._verify2("openstack.proxy.Proxy._update",
                      self.proxy.update_member,
                      method_args=['member_id', 'image_id'],
                      expected_args=[member.Member],
                      expected_kwargs={'member_id': 'member_id',
                                       'image_id': 'image_id'})

    def test_member_get(self):
        self._verify2("openstack.proxy.Proxy._get",
                      self.proxy.get_member,
                      method_args=['member_id'],
                      method_kwargs={"image": "image_id"},
                      expected_args=[member.Member],
                      expected_kwargs={'member_id': 'member_id',
                                       'image_id': 'image_id'})

    def test_member_find(self):
        self._verify2("openstack.proxy.Proxy._find",
                      self.proxy.find_member,
                      method_args=['member_id'],
                      method_kwargs={"image": "image_id"},
                      expected_args=[member.Member, "member_id"],
                      expected_kwargs={'ignore_missing': True,
                                       'image_id': 'image_id'})

    def test_members(self):
        self.verify_list(self.proxy.members, member.Member, paginated=False,
                         method_args=('image_1',),
                         expected_kwargs={'image_id': 'image_1'})
