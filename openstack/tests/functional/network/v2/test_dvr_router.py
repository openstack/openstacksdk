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


class TestDVRRouter(base.BaseFunctionalTest):
    ID = None

    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            # Current policies forbid regular user use it
            self.skipTest("Operator cloud is required for this test")

        if not self.operator_cloud._has_neutron_extension("dvr"):
            self.skipTest("dvr service not supported by cloud")

        self.NAME = self.getUniqueString()
        self.UPDATE_NAME = self.getUniqueString()
        sot = self.operator_cloud.network.create_router(
            name=self.NAME, distributed=True
        )
        assert isinstance(sot, router.Router)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id

    def tearDown(self):
        sot = self.operator_cloud.network.delete_router(
            self.ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.operator_cloud.network.find_router(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.operator_cloud.network.get_router(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)
        self.assertTrue(sot.is_distributed)

    def test_list(self):
        names = [o.name for o in self.operator_cloud.network.routers()]
        self.assertIn(self.NAME, names)
        dvr = [o.is_distributed for o in self.operator_cloud.network.routers()]
        self.assertTrue(dvr)

    def test_update(self):
        sot = self.operator_cloud.network.update_router(
            self.ID, name=self.UPDATE_NAME
        )
        self.assertEqual(self.UPDATE_NAME, sot.name)
