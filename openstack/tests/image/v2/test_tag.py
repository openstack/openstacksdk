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

from openstack.image.v2 import tag

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'image_id': 'IMAGE_ID',
    'tag': IDENTIFIER,
}


class TestTag(testtools.TestCase):
    def test_basic(self):
        sot = tag.Tag()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('tags', sot.resources_key)
        self.assertEqual('/images/%(image_id)s/tags', sot.base_path)
        self.assertEqual('image', sot.service.service_type)
        self.assertEqual('tag', sot.id_attribute)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = tag.Tag(EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['image_id'], sot.image_id)

    def test_create(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.put = mock.Mock(return_value=resp)
        url = 'images/{image_id}/tags/{tag}'.format(**EXAMPLE)
        tag.Tag(EXAMPLE).create(sess)
        sess.put.assert_called_with(url, service=tag.Tag.service, json=None)
