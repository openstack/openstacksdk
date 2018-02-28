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


from openstack.network.v2 import router
from openstack.tests.functional import base


class TestRouter(base.BaseFunctionalTest):

    ID = None

    def setUp(self):
        super(TestRouter, self).setUp()
        self.NAME = self.getUniqueString()
        self.UPDATE_NAME = self.getUniqueString()
        sot = self.conn.network.create_router(name=self.NAME)
        assert isinstance(sot, router.Router)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id

    def tearDown(self):
        sot = self.conn.network.delete_router(self.ID, ignore_missing=False)
        self.assertIsNone(sot)
        super(TestRouter, self).tearDown()

    def test_find(self):
        sot = self.conn.network.find_router(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_router(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)
        self.assertFalse(sot.is_ha)

    def test_list(self):
        names = [o.name for o in self.conn.network.routers()]
        self.assertIn(self.NAME, names)
        ha = [o.is_ha for o in self.conn.network.routers()]
        self.assertIn(False, ha)

    def test_update(self):
        sot = self.conn.network.update_router(self.ID, name=self.UPDATE_NAME)
        self.assertEqual(self.UPDATE_NAME, sot.name)

    def test_set_tags(self):
        sot = self.conn.network.get_router(self.ID)
        self.assertEqual([], sot.tags)

        self.conn.network.set_tags(sot, ['blue'])
        sot = self.conn.network.get_router(self.ID)
        self.assertEqual(['blue'], sot.tags)

        self.conn.network.set_tags(sot, [])
        sot = self.conn.network.get_router(self.ID)
        self.assertEqual([], sot.tags)
