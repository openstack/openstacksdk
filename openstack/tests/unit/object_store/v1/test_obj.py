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

from openstack.object_store.v1 import obj
from openstack.tests.unit.cloud import test_object as base_test_object

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


class TestObject(base_test_object.BaseTestObject):

    def setUp(self):
        super(TestObject, self).setUp()
        self.the_data = b'test body'
        self.the_data_length = len(self.the_data)
        # TODO(mordred) Make the_data be from getUniqueString and then
        # have hash and etag be actual md5 sums of that string
        self.body = {
            "hash": "243f87b91224d85722564a80fd3cb1f1",
            "last_modified": "2014-07-13T18:41:03.319240",
            "bytes": self.the_data_length,
            "name": self.object,
            "content_type": "application/octet-stream"
        }
        self.headers = {
            'Content-Length': str(len(self.the_data)),
            'Content-Type': 'application/octet-stream',
            'Accept-Ranges': 'bytes',
            'Last-Modified': 'Thu, 15 Dec 2016 13:34:14 GMT',
            'Etag': '"b5c454b44fbd5344793e3fb7e3850768"',
            'X-Timestamp': '1481808853.65009',
            'X-Trans-Id': 'tx68c2a2278f0c469bb6de1-005857ed80dfw1',
            'Date': 'Mon, 19 Dec 2016 14:24:00 GMT',
            'X-Static-Large-Object': 'True',
            'X-Object-Meta-Mtime': '1481513709.168512',
            'X-Delete-At': '1453416226.16744',
        }

    def test_basic(self):
        sot = obj.Object.new(**self.body)
        self.assert_no_calls()
        self.assertIsNone(sot.resources_key)
        self.assertEqual('name', sot._alternate_id())
        self.assertEqual('/%(container)s', sot.base_path)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_head)

    def test_new(self):
        sot = obj.Object.new(container=self.container, name=self.object)
        self.assert_no_calls()
        self.assertEqual(self.object, sot.name)
        self.assertEqual(self.container, sot.container)

    def test_from_body(self):
        sot = obj.Object.existing(container=self.container, **self.body)
        self.assert_no_calls()

        # Attributes from header
        self.assertEqual(self.container, sot.container)
        self.assertEqual(
            int(self.body['bytes']), sot.content_length)
        self.assertEqual(self.body['last_modified'], sot.last_modified_at)
        self.assertEqual(self.body['hash'], sot.etag)
        self.assertEqual(self.body['content_type'], sot.content_type)

    def test_from_headers(self):
        sot = obj.Object.existing(container=self.container, **self.headers)
        self.assert_no_calls()

        # Attributes from header
        self.assertEqual(self.container, sot.container)
        self.assertEqual(
            int(self.headers['Content-Length']), sot.content_length)
        self.assertEqual(self.headers['Accept-Ranges'], sot.accept_ranges)
        self.assertEqual(self.headers['Last-Modified'], sot.last_modified_at)
        self.assertEqual(self.headers['Etag'], sot.etag)
        self.assertEqual(self.headers['X-Timestamp'], sot.timestamp)
        self.assertEqual(self.headers['Content-Type'], sot.content_type)
        self.assertEqual(self.headers['X-Delete-At'], sot.delete_at)

    def test_download(self):
        headers = {
            'X-Newest': 'True',
            'If-Match': self.headers['Etag'],
            'Accept': 'bytes'
        }
        self.register_uris([
            dict(method='GET', uri=self.object_endpoint,
                 headers=self.headers,
                 content=self.the_data,
                 validate=dict(
                     headers=headers
                 ))
        ])
        sot = obj.Object.new(container=self.container, name=self.object)
        sot.is_newest = True
        # if_match is a list type, but we're passing a string. This tests
        # the up-conversion works properly.
        sot.if_match = self.headers['Etag']

        rv = sot.download(self.conn.object_store)

        self.assertEqual(self.the_data, rv)

        self.assert_calls()

    def _test_create(self, method, data):
        sot = obj.Object.new(container=self.container, name=self.object,
                             data=data)
        sot.is_newest = True
        sent_headers = {"x-newest": 'True', "Accept": ""}
        self.register_uris([
            dict(method=method, uri=self.object_endpoint,
                 headers=self.headers,
                 validate=dict(
                     headers=sent_headers))
        ])

        rv = sot.create(self.conn.object_store)
        self.assertEqual(rv.etag, self.headers['Etag'])

        self.assert_calls()

    def test_create_data(self):
        self._test_create('PUT', self.the_data)

    def test_create_no_data(self):
        self._test_create('PUT', None)
