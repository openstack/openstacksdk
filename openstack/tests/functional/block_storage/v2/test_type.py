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


from openstack.block_storage.v2 import type as _type
from openstack.tests.functional import base


class TestType(base.BaseFunctionalTest):

    def setUp(self):
        super(TestType, self).setUp()

        self.TYPE_NAME = self.getUniqueString()
        self.TYPE_ID = None

        sot = self.conn.block_storage.create_type(name=self.TYPE_NAME)
        assert isinstance(sot, _type.Type)
        self.assertEqual(self.TYPE_NAME, sot.name)
        self.TYPE_ID = sot.id

    def tearDown(self):
        sot = self.conn.block_storage.delete_type(
            self.TYPE_ID, ignore_missing=False)
        self.assertIsNone(sot)
        super(TestType, self).tearDown()

    def test_get(self):
        sot = self.conn.block_storage.get_type(self.TYPE_ID)
        self.assertEqual(self.TYPE_NAME, sot.name)
