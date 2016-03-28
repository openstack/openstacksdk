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

from datetime import datetime
import iso8601

import mock
import testtools

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

DICT_EXAMPLE = {
    'container': CONTAINER_NAME,
    'name': OBJECT_NAME,
    'content_type': 'application/octet-stream',
    'headers': {
        'content-length': '252466',
        'accept-ranges': 'bytes',
        'last-modified': 'Sun, 13 Jul 2014 18:41:04 GMT',
        'etag': '243f87b91224d85722564a80fd3cb1f1',
        'x-timestamp': '1453414256.28112',
        'date': 'Thu, 28 Aug 2014 14:41:59 GMT',
        'id': 'tx5fb5ad4f4d0846c6b2bc7-0053ff3fb7',
        'x-delete-at': '1453416226.16744'
    }
}


class TestObject(testtools.TestCase):

    def setUp(self):
        super(TestObject, self).setUp()
        self.resp = mock.Mock()
        self.resp.content = "lol here's some content"
        self.resp.headers = {"X-Trans-Id": "abcdef"}
        self.sess = mock.Mock()
        self.sess.get = mock.Mock(return_value=self.resp)
        self.sess.put = mock.Mock(return_value=self.resp)
        self.sess.post = mock.Mock(return_value=self.resp)

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
        sot = obj.Object.existing(**DICT_EXAMPLE)

        # Attributes from header
        self.assertEqual(DICT_EXAMPLE['container'], sot.container)
        headers = DICT_EXAMPLE['headers']
        self.assertEqual(headers['content-length'], sot.content_length)
        self.assertEqual(headers['accept-ranges'], sot.accept_ranges)
        self.assertEqual(headers['last-modified'], sot.last_modified_at)
        self.assertEqual(headers['etag'], sot.etag)
        self.assertEqual(datetime(2016, 1, 21, 22, 10, 56, 281120,
                                  tzinfo=iso8601.UTC),
                         sot.timestamp)
        self.assertEqual(headers['content-type'], sot.content_type)
        self.assertEqual(datetime(2016, 1, 21, 22, 43, 46, 167440,
                                  tzinfo=iso8601.UTC),
                         sot.delete_at)

    def test_get(self):
        sot = obj.Object.new(container=CONTAINER_NAME, name=OBJECT_NAME)
        sot.is_newest = True
        sot.if_match = {"who": "what"}

        rv = sot.get(self.sess)

        url = "%s/%s" % (CONTAINER_NAME, OBJECT_NAME)
        # TODO(thowe): Should allow filtering bug #1488269
        # headers = {
        #     "x-newest": True,
        #     "if-match": {"who": "what"}
        # }
        headers = {'Accept': 'bytes'}
        self.sess.get.assert_called_with(url, endpoint_filter=sot.service,
                                         headers=headers)
        self.assertEqual(self.resp.content, rv)

    def _test_create(self, method, data, accept):
        sot = obj.Object.new(container=CONTAINER_NAME, name=OBJECT_NAME,
                             data=data)
        sot.is_newest = True
        headers = {"x-newest": True, "Accept": ""}

        rv = sot.create(self.sess)

        url = "%s/%s" % (CONTAINER_NAME, OBJECT_NAME)
        method.assert_called_with(url, endpoint_filter=sot.service, data=data,
                                  headers=headers)
        self.assertEqual(self.resp.headers, rv.get_headers())

    def test_create_data(self):
        self._test_create(self.sess.put, "data", "bytes")

    def test_create_no_data(self):
        self._test_create(self.sess.post, None, None)
