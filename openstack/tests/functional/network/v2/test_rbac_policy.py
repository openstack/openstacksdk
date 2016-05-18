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

from openstack.network.v2 import network
from openstack.network.v2 import rbac_policy
from openstack.tests.functional import base


class TestRBACPolicy(base.BaseFunctionalTest):

    NET_NAME = 'net-' + uuid.uuid4().hex
    UPDATE_NAME = uuid.uuid4().hex
    ACTION = 'access_as_shared'
    OBJ_TYPE = 'network'
    TARGET_TENANT_ID = '*'
    NET_ID = None
    ID = None

    @classmethod
    def setUpClass(cls):
        super(TestRBACPolicy, cls).setUpClass()
        net = cls.conn.network.create_network(name=cls.NET_NAME)
        assert isinstance(net, network.Network)
        cls.NET_ID = net.id

        sot = cls.conn.network.\
            create_rbac_policy(action=cls.ACTION,
                               object_type=cls.OBJ_TYPE,
                               target_tenant=cls.TARGET_TENANT_ID,
                               object_id=cls.NET_ID)
        assert isinstance(sot, rbac_policy.RBACPolicy)
        cls.ID = sot.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_rbac_policy(cls.ID,
                                                  ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_network(cls.NET_ID,
                                              ignore_missing=False)
        cls.assertIs(None, sot)

    def test_find(self):
        sot = self.conn.network.find_rbac_policy(self.ID)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_rbac_policy(self.ID)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        ids = [o.id for o in self.conn.network.rbac_policies()]
        self.assertIn(self.ID, ids)
