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


from openstack.network.v2 import l3_conntrack_helper as _l3_conntrack_helper
from openstack.network.v2 import router
from openstack.tests.functional import base


class TestL3ConntrackHelper(base.BaseFunctionalTest):
    PROTOCOL = "udp"
    HELPER = "tftp"
    PORT = 69

    ROT_ID = None

    def setUp(self):
        super().setUp()

        if not self.user_cloud.network.find_extension("l3-conntrack-helper"):
            self.skipTest("L3 conntrack helper extension disabled")

        self.ROT_NAME = self.getUniqueString()
        # Create Router
        sot = self.user_cloud.network.create_router(name=self.ROT_NAME)
        self.assertIsInstance(sot, router.Router)
        self.assertEqual(self.ROT_NAME, sot.name)
        self.ROT_ID = sot.id
        self.ROT = sot

        # Create conntrack helper
        ct_helper = self.user_cloud.network.create_conntrack_helper(
            router=self.ROT,
            protocol=self.PROTOCOL,
            helper=self.HELPER,
            port=self.PORT,
        )
        self.assertIsInstance(ct_helper, _l3_conntrack_helper.ConntrackHelper)
        self.CT_HELPER = ct_helper

    def tearDown(self):
        sot = self.user_cloud.network.delete_router(
            self.ROT_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_get(self):
        sot = self.user_cloud.network.get_conntrack_helper(
            self.CT_HELPER, self.ROT_ID
        )
        self.assertEqual(self.PROTOCOL, sot.protocol)
        self.assertEqual(self.HELPER, sot.helper)
        self.assertEqual(self.PORT, sot.port)

    def test_list(self):
        helper_ids = [
            o.id
            for o in self.user_cloud.network.conntrack_helpers(self.ROT_ID)
        ]
        self.assertIn(self.CT_HELPER.id, helper_ids)

    def test_update(self):
        NEW_PORT = 90
        sot = self.user_cloud.network.update_conntrack_helper(
            self.CT_HELPER.id, self.ROT_ID, port=NEW_PORT
        )
        self.assertEqual(NEW_PORT, sot.port)
