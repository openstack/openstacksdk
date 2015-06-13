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

from openstack.object_store.v1 import container
from openstack.tests.functional import base


class TestContainer(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super(TestContainer, cls).setUpClass()
        tainer = cls.conn.object_store.create_container(name=cls.NAME)
        assert isinstance(tainer, container.Container)
        cls.assertIs(cls.NAME, tainer.name)

    @classmethod
    def tearDownClass(cls):
        result = cls.conn.object_store.delete_container(cls.NAME,
                                                        ignore_missing=False)
        cls.assertIs(None, result)

    def test_list(self):
        names = [o.name for o in self.conn.object_store.containers()]
        self.assertIn(self.NAME, names)

    def test_get_metadata(self):
        tainer = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertEqual(0, tainer.object_count)
        self.assertEqual(0, tainer.bytes_used)
        self.assertEqual(self.NAME, tainer.name)
