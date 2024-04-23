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

from openstack.network.v2 import vpn_ike_policy
from openstack.tests.functional import base


class TestVpnIkePolicy(base.BaseFunctionalTest):
    ID = None

    def setUp(self):
        super().setUp()
        if not self.user_cloud._has_neutron_extension("vpnaas"):
            self.skipTest("vpnaas service not supported by cloud")
        self.IKEPOLICY_NAME = self.getUniqueString("ikepolicy")
        self.UPDATE_NAME = self.getUniqueString("ikepolicy-updated")
        policy = self.user_cloud.network.create_vpn_ike_policy(
            name=self.IKEPOLICY_NAME
        )
        assert isinstance(policy, vpn_ike_policy.VpnIkePolicy)
        self.assertEqual(self.IKEPOLICY_NAME, policy.name)
        self.ID = policy.id

    def tearDown(self):
        ikepolicy = self.user_cloud.network.delete_vpn_ike_policy(
            self.ID, ignore_missing=True
        )
        self.assertIsNone(ikepolicy)
        super().tearDown()

    def test_list(self):
        policies = [f.name for f in self.user_cloud.network.vpn_ike_policies()]
        self.assertIn(self.IKEPOLICY_NAME, policies)

    def test_find(self):
        policy = self.user_cloud.network.find_vpn_ike_policy(
            self.IKEPOLICY_NAME
        )
        self.assertEqual(self.ID, policy.id)

    def test_get(self):
        policy = self.user_cloud.network.get_vpn_ike_policy(self.ID)
        self.assertEqual(self.IKEPOLICY_NAME, policy.name)
        self.assertEqual(self.ID, policy.id)

    def test_update(self):
        policy = self.user_cloud.network.update_vpn_ike_policy(
            self.ID, name=self.UPDATE_NAME
        )
        self.assertEqual(self.UPDATE_NAME, policy.name)
