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
from openstack.network.v2 import router
from openstack.network.v2 import subnet
from openstack.tests.functional import base


class TestRouterInterface(base.BaseFunctionalTest):

    CIDR = "10.100.0.0/16"
    IPV4 = 4
    ROUTER_ID = None
    NET_ID = None
    SUB_ID = None
    ROT = None

    def setUp(self):
        super(TestRouterInterface, self).setUp()
        self.ROUTER_NAME = self.getUniqueString()
        self.NET_NAME = self.getUniqueString()
        self.SUB_NAME = self.getUniqueString()
        sot = self.conn.network.create_router(name=self.ROUTER_NAME)
        assert isinstance(sot, router.Router)
        self.assertEqual(self.ROUTER_NAME, sot.name)
        net = self.conn.network.create_network(name=self.NET_NAME)
        assert isinstance(net, network.Network)
        self.assertEqual(self.NET_NAME, net.name)
        sub = self.conn.network.create_subnet(
            name=self.SUB_NAME,
            ip_version=self.IPV4,
            network_id=net.id,
            cidr=self.CIDR)
        assert isinstance(sub, subnet.Subnet)
        self.assertEqual(self.SUB_NAME, sub.name)
        self.ROUTER_ID = sot.id
        self.ROT = sot
        self.NET_ID = net.id
        self.SUB_ID = sub.id

    def tearDown(self):
        sot = self.conn.network.delete_router(
            self.ROUTER_ID, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_subnet(
            self.SUB_ID, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_network(
            self.NET_ID, ignore_missing=False)
        self.assertIsNone(sot)
        super(TestRouterInterface, self).tearDown()

    def test_router_add_remove_interface(self):
        iface = self.ROT.add_interface(self.conn.network,
                                       subnet_id=self.SUB_ID)
        self._verification(iface)
        iface = self.ROT.remove_interface(self.conn.network,
                                          subnet_id=self.SUB_ID)
        self._verification(iface)

    def _verification(self, interface):
        self.assertEqual(interface['subnet_id'], self.SUB_ID)
        self.assertIn('port_id', interface)
