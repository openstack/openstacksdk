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
from openstack.network.v2 import router
from openstack.network.v2 import subnet
from openstack.tests.functional import base


class TestRouterInterface(base.BaseFunctionalTest):

    ROUTER_NAME = uuid.uuid4().hex
    NET_NAME = uuid.uuid4().hex
    SUB_NAME = uuid.uuid4().hex
    CIDR = "10.100.0.0/16"
    IPV4 = 4
    ROUTER_ID = None
    NET_ID = None
    SUB_ID = None
    ROT = None

    @classmethod
    def setUpClass(cls):
        super(TestRouterInterface, cls).setUpClass()
        sot = cls.conn.network.create_router(name=cls.ROUTER_NAME)
        assert isinstance(sot, router.Router)
        cls.assertIs(cls.ROUTER_NAME, sot.name)
        net = cls.conn.network.create_network(name=cls.NET_NAME)
        assert isinstance(net, network.Network)
        cls.assertIs(cls.NET_NAME, net.name)
        sub = cls.conn.network.create_subnet(name=cls.SUB_NAME,
                                             ip_version=cls.IPV4,
                                             network_id=net.id,
                                             cidr=cls.CIDR)
        assert isinstance(sub, subnet.Subnet)
        cls.assertIs(cls.SUB_NAME, sub.name)
        cls.ROUTER_ID = sot.id
        cls.ROT = sot
        cls.NET_ID = net.id
        cls.SUB_ID = sub.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_router(cls.ROUTER_ID,
                                             ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_subnet(cls.SUB_ID, ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_network(cls.NET_ID, ignore_missing=False)
        cls.assertIs(None, sot)

    def test_router_add_interface(self):
        iface = self.ROT.add_interface(self.conn.session,
                                       subnet_id=self.SUB_ID)
        self._verification(iface)

    def test_router_remove_interface(self):
        iface = self.ROT.remove_interface(self.conn.session,
                                          subnet_id=self.SUB_ID)
        self._verification(iface)

    def _verification(self, interface):
        self.assertEqual(interface['subnet_id'], self.SUB_ID)
        self.assertIn('port_id', interface)
