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
import testtools

from openstack.image.v2 import image
from openstack.image.v2 import tag


class TestTag(testtools.TestCase):

    def setUp(self):
        super(TestTag, self).setUp()

        self.session = mock.Mock()
        self.session.put = mock.Mock()
        self.session.delete = mock.Mock()

        self.img = image.Image({"id": "123"})

    def test_basic(self):
        sot = tag.Tag()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('/images/%(image)s/tags', sot.base_path)
        self.assertEqual('image', sot.service.service_type)
        self.assertEqual('image', sot.id_attribute)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = tag.Tag({"image": self.img})
        self.assertEqual(self.img, sot.image)

    def _test_action(self, sot_method, session_method):
        test_tag = "testing"

        sot = tag.Tag({"image": self.img})
        rv = getattr(sot, sot_method)(self.session, test_tag)

        url = 'images/%(image)s/tags/%(tag)s' % {
            "image": self.img.get_id(self.img), "tag": test_tag}
        self.assertIsNone(rv)
        headers = {'Accept': ''}
        session_method.assert_called_with(url, endpoint_filter=sot.service,
                                          headers=headers)

    def test_create(self):
        self._test_action("create", self.session.put)

    def test_delete(self):
        self._test_action("delete", self.session.delete)
