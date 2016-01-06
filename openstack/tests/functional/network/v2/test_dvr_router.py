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

from openstack.network.v2 import router
from openstack.tests.functional import base


class TestDVRRouter(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex
    UPDATE_NAME = uuid.uuid4().hex
    ID = None

    @classmethod
    def setUpClass(cls):
        super(TestDVRRouter, cls).setUpClass()
        sot = cls.conn.network.create_router(name=cls.NAME, distributed=True)
        assert isinstance(sot, router.Router)
        cls.assertIs(cls.NAME, sot.name)
        cls.ID = sot.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_router(cls.ID, ignore_missing=False)
        cls.assertIs(None, sot)

    def test_find(self):
        sot = self.conn.network.find_router(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_router(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)
        self.assertTrue(sot.is_distributed)

    def test_list(self):
        names = [o.name for o in self.conn.network.routers()]
        self.assertIn(self.NAME, names)
        dvr = [o.is_distributed for o in self.conn.network.routers()]
        self.assertTrue(dvr)

    def test_update(self):
        sot = self.conn.network.update_router(self.ID, name=self.UPDATE_NAME)
        self.assertEqual(self.UPDATE_NAME, sot.name)
