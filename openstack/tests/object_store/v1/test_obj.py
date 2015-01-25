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
from openstack.object_store.v1 import obj


CONTAINER_NAME = "mycontainer"
OBJECT_NAME = "myobject"

# Object can receive both last-modified in headers and last_modified in
# the body. However, originally, only last-modified was handled as an
# expected prop but it was named last_modified. Under Python 3, creating
# an Object with the body value last_modified causes the _attrs dictionary
# size to change while iterating over its values as we have an attribute
# called `last_modified` and we attempt to grow an additional attribute
# called `last-modified`, which is the "name" of `last_modified`.
# The same is true of content_type and content-type, or any prop
# attribute which would follow the same pattern.
# This example should represent the body values returned by a GET, so the keys
# must be underscores.
OBJ_EXAMPLE = {
    "hash": "243f87b91224d85722564a80fd3cb1f1",
    "last_modified": "2014-07-13T18:41:03.319240",
    "bytes": 252466,
    "name": OBJECT_NAME,
    "content_type": "application/octet-stream"
}

HEAD_EXAMPLE = {
    'content-length': '252466',
    'container': CONTAINER_NAME,
    'name': OBJECT_NAME,
    'accept-ranges': 'bytes',
    'last-modified': 'Sun, 13 Jul 2014 18:41:04 GMT',
    'etag': '243f87b91224d85722564a80fd3cb1f1',
    'x-timestamp': '1405276863.31924',
    'date': 'Thu, 28 Aug 2014 14:41:59 GMT',
    'content-type': 'application/octet-stream',
    'id': 'tx5fb5ad4f4d0846c6b2bc7-0053ff3fb7'
}


class TestObject(testtools.TestCase):

    def setUp(self):
        super(TestObject, self).setUp()
        self.resp = mock.Mock()
        self.resp.content = "lol here's some content"
        self.resp.headers = {"X-Trans-Id": "abcdef"}
        self.sess = mock.Mock()
        self.sess.get = mock.MagicMock()
        self.sess.get.return_value = self.resp

    def test_basic(self):
        sot = obj.Object.new(**OBJ_EXAMPLE)
        self.assertIsNone(sot.resources_key)
        self.assertEqual("name", sot.id_attribute)
        self.assertEqual('/%(container)s', sot.base_path)
        self.assertEqual('object-store', sot.service.service_type)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_head)

    def test_new(self):
        sot = obj.Object.new(container=CONTAINER_NAME, name=OBJECT_NAME)
        self.assertEqual(OBJECT_NAME, sot.name)
        self.assertEqual(CONTAINER_NAME, sot.container)

    def test_head(self):
        sot = obj.Object.existing(**HEAD_EXAMPLE)

        # Attributes from header
        self.assertEqual(HEAD_EXAMPLE['container'], sot.container)
        self.assertEqual(HEAD_EXAMPLE['content-length'], sot.content_length)
        self.assertEqual(HEAD_EXAMPLE['accept-ranges'], sot.accept_ranges)
        self.assertEqual(HEAD_EXAMPLE['last-modified'], sot.last_modified)
        self.assertEqual(HEAD_EXAMPLE['etag'], sot.etag)
        self.assertEqual(HEAD_EXAMPLE['x-timestamp'], sot.timestamp)
        self.assertEqual(HEAD_EXAMPLE['date'], sot.date)
        self.assertEqual(HEAD_EXAMPLE['content-type'], sot.content_type)

    def test_get(self):
        sot = obj.Object.new(container=CONTAINER_NAME, name=OBJECT_NAME)
        sot.newest = True
        sot.if_match = {"who": "what"}
        headers = {
            "x-newest": True,
            "if-match": {"who": "what"}
        }

        rv = sot.get(self.sess)

        url = "/%s/%s" % (CONTAINER_NAME, OBJECT_NAME)
        self.sess.get.assert_called_with(url, service=sot.service,
                                         accept="bytes", headers=headers)
        self.assertEqual(rv, self.resp.content)

    def test_cant_get(self):
        sot = obj.Object.new(container=CONTAINER_NAME, name=OBJECT_NAME)
        sot.allow_retrieve = False
        self.assertRaises(exceptions.MethodNotSupported, sot.get, self.sess)
