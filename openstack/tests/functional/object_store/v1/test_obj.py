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

from openstack.tests.functional import base


class TestObject(base.BaseFunctionalTest):

    DATA = b'abc'

    def setUp(self):
        super(TestObject, self).setUp()
        self.require_service('object-store')

        self.FOLDER = self.getUniqueString()
        self.FILE = self.getUniqueString()
        self.conn.object_store.create_container(name=self.FOLDER)
        self.addCleanup(self.conn.object_store.delete_container, self.FOLDER)
        self.sot = self.conn.object_store.upload_object(
            container=self.FOLDER, name=self.FILE, data=self.DATA)
        self.addEmptyCleanup(
            self.conn.object_store.delete_object, self.sot,
            ignore_missing=False)

    def test_list(self):
        names = [o.name for o
                 in self.conn.object_store.objects(container=self.FOLDER)]
        self.assertIn(self.FILE, names)

    def test_download_object(self):
        result = self.conn.object_store.download_object(
            self.FILE, container=self.FOLDER)
        self.assertEqual(self.DATA, result)
        result = self.conn.object_store.download_object(self.sot)
        self.assertEqual(self.DATA, result)

    def test_system_metadata(self):
        # get system metadata
        obj = self.conn.object_store.get_object_metadata(
            self.FILE, container=self.FOLDER)
        # TODO(shade) obj.bytes is coming up None on python3 but not python2
        # self.assertGreaterEqual(0, obj.bytes)
        self.assertIsNotNone(obj.etag)

        # set system metadata
        obj = self.conn.object_store.get_object_metadata(
            self.FILE, container=self.FOLDER)
        self.assertIsNone(obj.content_disposition)
        self.assertIsNone(obj.content_encoding)
        self.conn.object_store.set_object_metadata(
            obj, content_disposition='attachment', content_encoding='gzip')
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertEqual('attachment', obj.content_disposition)
        self.assertEqual('gzip', obj.content_encoding)

        # update system metadata
        self.conn.object_store.set_object_metadata(
            obj, content_encoding='deflate')
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertEqual('attachment', obj.content_disposition)
        self.assertEqual('deflate', obj.content_encoding)

        # set custom metadata
        self.conn.object_store.set_object_metadata(obj, k0='v0')
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertIn('k0', obj.metadata)
        self.assertEqual('v0', obj.metadata['k0'])
        self.assertEqual('attachment', obj.content_disposition)
        self.assertEqual('deflate', obj.content_encoding)

        # unset more system metadata
        self.conn.object_store.delete_object_metadata(
            obj, keys=['content_disposition'])
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertIn('k0', obj.metadata)
        self.assertEqual('v0', obj.metadata['k0'])
        self.assertIsNone(obj.content_disposition)
        self.assertEqual('deflate', obj.content_encoding)
        self.assertIsNone(obj.delete_at)

    def test_custom_metadata(self):
        # get custom metadata
        obj = self.conn.object_store.get_object_metadata(
            self.FILE, container=self.FOLDER)
        self.assertFalse(obj.metadata)

        # set no custom metadata
        self.conn.object_store.set_object_metadata(obj)
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertFalse(obj.metadata)

        # set empty custom metadata
        self.conn.object_store.set_object_metadata(obj, k0='')
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertFalse(obj.metadata)

        # set custom metadata
        self.conn.object_store.set_object_metadata(obj, k1='v1')
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertTrue(obj.metadata)
        self.assertEqual(1, len(obj.metadata))
        self.assertIn('k1', obj.metadata)
        self.assertEqual('v1', obj.metadata['k1'])

        # set more custom metadata by named object and container
        self.conn.object_store.set_object_metadata(self.FILE, self.FOLDER,
                                                   k2='v2')
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertTrue(obj.metadata)
        self.assertEqual(2, len(obj.metadata))
        self.assertIn('k1', obj.metadata)
        self.assertEqual('v1', obj.metadata['k1'])
        self.assertIn('k2', obj.metadata)
        self.assertEqual('v2', obj.metadata['k2'])

        # update custom metadata
        self.conn.object_store.set_object_metadata(obj, k1='v1.1')
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertTrue(obj.metadata)
        self.assertEqual(2, len(obj.metadata))
        self.assertIn('k1', obj.metadata)
        self.assertEqual('v1.1', obj.metadata['k1'])
        self.assertIn('k2', obj.metadata)
        self.assertEqual('v2', obj.metadata['k2'])

        # unset custom metadata
        self.conn.object_store.delete_object_metadata(obj, keys=['k1'])
        obj = self.conn.object_store.get_object_metadata(obj)
        self.assertTrue(obj.metadata)
        self.assertEqual(1, len(obj.metadata))
        self.assertIn('k2', obj.metadata)
        self.assertEqual('v2', obj.metadata['k2'])
