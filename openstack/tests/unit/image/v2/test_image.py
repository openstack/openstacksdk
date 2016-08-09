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

from openstack import exceptions
from openstack.image.v2 import image

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'checksum': '1',
    'container_format': '2',
    'created_at': '2015-03-09T12:14:57.233772',
    'data': 'This is not an image',
    'disk_format': '4',
    'min_disk': 5,
    'name': '6',
    'owner': '7',
    'properties': {'a': 'z', 'b': 'y', },
    'protected': False,
    'status': '8',
    'tags': ['g', 'h', 'i'],
    'updated_at': '2015-03-09T12:15:57.233772',
    'virtual_size': '10',
    'visibility': '11',
    'location': '12',
    'size': 13,
    'store': '14',
    'file': '15',
    'locations': ['15', '16'],
    'direct_url': '17',
    'path': '18',
    'value': '19',
    'url': '20',
    'metadata': {'21': '22'}
}


class TestImage(testtools.TestCase):

    def setUp(self):
        super(TestImage, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = image.Image()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('images', sot.resources_key)
        self.assertEqual('/images', sot.base_path)
        self.assertEqual('image', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = image.Image(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['checksum'], sot.checksum)
        self.assertEqual(EXAMPLE['container_format'], sot.container_format)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['disk_format'], sot.disk_format)
        self.assertEqual(EXAMPLE['min_disk'], sot.min_disk)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['owner'], sot.owner_id)
        self.assertEqual(EXAMPLE['properties'], sot.properties)
        self.assertFalse(sot.is_protected)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['tags'], sot.tags)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['virtual_size'], sot.virtual_size)
        self.assertEqual(EXAMPLE['visibility'], sot.visibility)
        self.assertEqual(EXAMPLE['size'], sot.size)
        self.assertEqual(EXAMPLE['store'], sot.store)
        self.assertEqual(EXAMPLE['file'], sot.file)
        self.assertEqual(EXAMPLE['locations'], sot.locations)
        self.assertEqual(EXAMPLE['direct_url'], sot.direct_url)
        self.assertEqual(EXAMPLE['path'], sot.path)
        self.assertEqual(EXAMPLE['value'], sot.value)
        self.assertEqual(EXAMPLE['url'], sot.url)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)

    def test_deactivate(self):
        sot = image.Image(**EXAMPLE)
        self.assertIsNone(sot.deactivate(self.sess))
        self.sess.post.assert_called_with(
            'images/IDENTIFIER/actions/deactivate',
            endpoint_filter=sot.service)

    def test_reactivate(self):
        sot = image.Image(**EXAMPLE)
        self.assertIsNone(sot.reactivate(self.sess))
        self.sess.post.assert_called_with(
            'images/IDENTIFIER/actions/reactivate',
            endpoint_filter=sot.service)

    def test_add_tag(self):
        sot = image.Image(**EXAMPLE)
        tag = "lol"

        self.assertIsNone(sot.add_tag(self.sess, tag))
        self.sess.put.assert_called_with(
            'images/IDENTIFIER/tags/%s' % tag,
            endpoint_filter=sot.service)

    def test_remove_tag(self):
        sot = image.Image(**EXAMPLE)
        tag = "lol"

        self.assertIsNone(sot.remove_tag(self.sess, tag))
        self.sess.delete.assert_called_with(
            'images/IDENTIFIER/tags/%s' % tag,
            endpoint_filter=sot.service)

    def test_upload(self):
        sot = image.Image(**EXAMPLE)

        self.assertIsNone(sot.upload(self.sess))
        self.sess.put.assert_called_with('images/IDENTIFIER/file',
                                         endpoint_filter=sot.service,
                                         data=sot.data,
                                         headers={"Content-Type":
                                                  "application/octet-stream",
                                                  "Accept": ""})

    def test_upload_checksum_match(self):
        sot = image.Image(**EXAMPLE)

        resp = mock.Mock()
        resp.content = b"abc"
        resp.headers = {"Content-MD5": "900150983cd24fb0d6963f7d28e17f72"}
        self.sess.get.return_value = resp

        rv = sot.download(self.sess)
        self.sess.get.assert_called_with('images/IDENTIFIER/file',
                                         endpoint_filter=sot.service)

        self.assertEqual(rv, resp.content)

    def test_upload_checksum_mismatch(self):
        sot = image.Image(**EXAMPLE)

        resp = mock.Mock()
        resp.content = b"abc"
        resp.headers = {"Content-MD5": "the wrong checksum"}
        self.sess.get.return_value = resp

        self.assertRaises(exceptions.InvalidResponse, sot.download, self.sess)
