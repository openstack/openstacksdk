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

    ACTION = 'access_as_shared'
    OBJ_TYPE = 'network'
    TARGET_TENANT_ID = '*'
    NET_ID = None
    ID = None

    def setUp(self):
        super(TestRBACPolicy, self).setUp()
        self.NET_NAME = self.getUniqueString('net')
        self.UPDATE_NAME = self.getUniqueString()
        net = self.conn.network.create_network(name=self.NET_NAME)
        assert isinstance(net, network.Network)
        self.NET_ID = net.id

        sot = self.conn.network.create_rbac_policy(
            action=self.ACTION,
            object_type=self.OBJ_TYPE,
            target_tenant=self.TARGET_TENANT_ID,
            object_id=self.NET_ID)
        assert isinstance(sot, rbac_policy.RBACPolicy)
        self.ID = sot.id

    def tearDown(self):
        sot = self.conn.network.delete_rbac_policy(
            self.ID,
            ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_network(
            self.NET_ID,
            ignore_missing=False)
        self.assertIsNone(sot)
        super(TestRBACPolicy, self).tearDown()

    def test_find(self):
        sot = self.conn.network.find_rbac_policy(self.ID)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_rbac_policy(self.ID)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        ids = [o.id for o in self.conn.network.rbac_policies()]
        self.assertIn(self.ID, ids)
