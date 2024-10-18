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
# mypy: disable-error-code="method-assign"

from openstack.network.v2 import router
from openstack.tests.functional.network.v2 import common


class TestRouter(common.TestTagNeutron):
    ID = None

    def setUp(self):
        super().setUp()
        self.NAME = self.getUniqueString()
        self.UPDATE_NAME = self.getUniqueString()
        sot = self.user_cloud.network.create_router(name=self.NAME)
        assert isinstance(sot, router.Router)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id
        self.get_command = self.user_cloud.network.get_router

    def tearDown(self):
        sot = self.user_cloud.network.delete_router(
            self.ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_router(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.user_cloud.network.get_router(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)
        if not self.user_cloud._has_neutron_extension("l3-ha"):
            self.assertFalse(sot.is_ha)

    def test_list(self):
        names = [o.name for o in self.user_cloud.network.routers()]
        self.assertIn(self.NAME, names)
        if not self.user_cloud._has_neutron_extension("l3-ha"):
            ha = [o.is_ha for o in self.user_cloud.network.routers()]
            self.assertIn(False, ha)

    def test_update(self):
        sot = self.user_cloud.network.update_router(
            self.ID, name=self.UPDATE_NAME
        )
        self.assertEqual(self.UPDATE_NAME, sot.name)
