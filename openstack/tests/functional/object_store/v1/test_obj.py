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

import uuid

from openstack.tests.functional import base


class TestObject(base.BaseFunctionalTest):

    FOLDER = uuid.uuid4().hex
    FILE = uuid.uuid4().hex
    DATA = 'abc'

    @classmethod
    def setUpClass(cls):
        super(TestObject, cls).setUpClass()
        cls.conn.object_store.create_container(name=cls.FOLDER)
        cls.sot = cls.conn.object_store.upload_object(
            container=cls.FOLDER, name=cls.FILE, data=cls.DATA)

    @classmethod
    def tearDownClass(cls):
        super(TestObject, cls).tearDownClass()
        cls.conn.object_store.delete_object(cls.sot, ignore_missing=False)
        cls.conn.object_store.delete_container(cls.FOLDER)

    def test_list(self):
        names = [o.name for o
                 in self.conn.object_store.objects(container=self.FOLDER)]
        self.assertIn(self.FILE, names)

    def test_get_object(self):
        result = self.conn.object_store.get_object(
            self.FILE, container=self.FOLDER)
        self.assertEqual(self.DATA, result)
        result = self.conn.object_store.get_object(self.sot)
        self.assertEqual(self.DATA, result)

    def test_get_metadata(self):
        self.sot.data = None
        self.sot.set_headers({'x-object-meta-test': 'orly'})
        result = self.conn.object_store.set_object_metadata(self.sot)
        result = self.conn.object_store.get_object_metadata(self.sot)
        self.assertEqual(self.FILE, result.name)
        headers = result.get_headers()
        self.assertEqual(str(len(self.DATA)), headers['content-length'])
        self.assertEqual('orly', headers['x-object-meta-test'])
