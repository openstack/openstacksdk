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


from openstack.network.v2 import network
from openstack.network.v2 import rbac_policy
from openstack.tests.functional import base


class TestRBACPolicy(base.BaseFunctionalTest):
    ACTION = "access_as_shared"
    OBJ_TYPE = "network"
    TARGET_TENANT_ID = "*"
    NET_ID = None
    ID = None

    def setUp(self):
        super().setUp()
        if not self.user_cloud._has_neutron_extension("rbac-policies"):
            self.skipTest(
                "Neutron rbac-policies extension is required for this test"
            )

        self.NET_NAME = self.getUniqueString("net")
        self.UPDATE_NAME = self.getUniqueString()
        net = self.user_cloud.network.create_network(name=self.NET_NAME)
        assert isinstance(net, network.Network)
        self.NET_ID = net.id
        if self.operator_cloud:
            sot = self.operator_cloud.network.create_rbac_policy(
                action=self.ACTION,
                object_type=self.OBJ_TYPE,
                target_tenant=self.TARGET_TENANT_ID,
                object_id=self.NET_ID,
            )
            assert isinstance(sot, rbac_policy.RBACPolicy)
            self.ID = sot.id
        else:
            sot = self.user_cloud.network.create_rbac_policy(
                action=self.ACTION,
                object_type=self.OBJ_TYPE,
                target_tenant=self.user_cloud.current_project_id,
                object_id=self.NET_ID,
            )
            assert isinstance(sot, rbac_policy.RBACPolicy)
            self.ID = sot.id

    def tearDown(self):
        if self.operator_cloud:
            sot = self.operator_cloud.network.delete_rbac_policy(
                self.ID, ignore_missing=False
            )
        else:
            sot = self.user_cloud.network.delete_rbac_policy(
                self.ID, ignore_missing=False
            )
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_network(
            self.NET_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        if self.operator_cloud:
            sot = self.operator_cloud.network.find_rbac_policy(self.ID)
        else:
            sot = self.user_cloud.network.find_rbac_policy(self.ID)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        if self.operator_cloud:
            sot = self.operator_cloud.network.get_rbac_policy(self.ID)
        else:
            sot = self.user_cloud.network.get_rbac_policy(self.ID)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        if self.operator_cloud:
            ids = [o.id for o in self.operator_cloud.network.rbac_policies()]
        else:
            ids = [o.id for o in self.user_cloud.network.rbac_policies()]
        if self.ID:
            self.assertIn(self.ID, ids)
