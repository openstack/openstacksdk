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

from openstack.network.v2 import ndp_proxy as _ndp_proxy
from openstack.network.v2 import network
from openstack.network.v2 import port
from openstack.network.v2 import router
from openstack.network.v2 import subnet
from openstack.tests.functional import base


class TestNDPProxy(base.BaseFunctionalTest):
    IPV6 = 6
    EXT_CIDR = "2002::1:0/112"
    INT_CIDR = "2002::2:0/112"
    EXT_NET_ID = None
    INT_NET_ID = None
    EXT_SUB_ID = None
    INT_SUB_ID = None
    ROT_ID = None
    INTERNAL_PORT_ID = None

    def setUp(self):
        super().setUp()

        if not self.user_cloud.network.find_extension("l3-ndp-proxy"):
            self.skipTest("L3 ndp proxy extension disabled")

        self.ROT_NAME = self.getUniqueString()
        self.EXT_NET_NAME = self.getUniqueString()
        self.EXT_SUB_NAME = self.getUniqueString()
        self.INT_NET_NAME = self.getUniqueString()
        self.INT_SUB_NAME = self.getUniqueString()

        # Find External Network
        for net in self.user_cloud.network.networks(is_router_external=True):
            self.EXT_NET_ID = net.id
        # Find subnet of the chosen external net
        for sub in self.user_cloud.network.subnets(network_id=self.EXT_NET_ID):
            self.EXT_SUB_ID = sub.id
        if not self.EXT_NET_ID and self.operator_cloud:
            # There is no existing external net, but operator
            # credentials available
            # WARNING: this external net is not dropped
            # Create External Network
            net = self._create_network(
                self.EXT_NET_NAME, **{"router:external": True}
            )
            self.EXT_NET_ID = net.id
            sub = self._create_subnet(
                self.EXT_SUB_NAME, self.EXT_NET_ID, self.EXT_CIDR
            )
            self.EXT_SUB_ID = sub.id

        # Create Router
        sot = self.user_cloud.network.create_router(
            name=self.ROT_NAME,
            **{
                "external_gateway_info": {"network_id": self.EXT_NET_ID},
                "enable_ndp_proxy": True,
            },
        )
        assert isinstance(sot, router.Router)
        self.assertEqual(self.ROT_NAME, sot.name)
        self.ROT_ID = sot.id
        self.ROT = sot
        # Add Router's Interface to Internal Network
        sot = self.ROT.add_interface(
            self.user_cloud.network, subnet_id=self.INT_SUB_ID
        )
        self.assertEqual(sot["subnet_id"], self.INT_SUB_ID)
        # Create Port in Internal Network
        prt = self.user_cloud.network.create_port(network_id=self.INT_NET_ID)
        assert isinstance(prt, port.Port)
        self.INTERNAL_PORT_ID = prt.id
        self.INTERNAL_IP_ADDRESS = prt.fixed_ips[0]["ip_address"]
        # Create ndp proxy
        np = self.user_cloud.network.create_ndp_proxy(
            router_id=self.ROT_ID, port_id=self.INTERNAL_PORT_ID
        )
        assert isinstance(np, _ndp_proxy.NDPProxy)
        self.NP = np

    def tearDown(self):
        sot = self.user_cloud.network.delete_ndp_proxy(
            self.NP.id, ignore_missing=False
        )
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_port(
            self.INTERNAL_PORT_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        sot = self.ROT.remove_interface(
            self.user_cloud.network, subnet_id=self.INT_SUB_ID
        )
        self.assertEqual(sot["subnet_id"], self.INT_SUB_ID)
        sot = self.user_cloud.network.delete_router(
            self.ROT_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_subnet(
            self.INT_SUB_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_network(
            self.INT_NET_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def _create_network(self, name, **args):
        self.name = name
        net = self.user_cloud.network.create_network(name=name, **args)
        assert isinstance(net, network.Network)
        self.assertEqual(self.name, net.name)
        return net

    def _create_subnet(self, name, net_id, cidr):
        self.name = name
        self.net_id = net_id
        self.cidr = cidr
        sub = self.user_cloud.network.create_subnet(
            name=self.name,
            ip_version=self.IPV6,
            network_id=self.net_id,
            cidr=self.cidr,
        )
        assert isinstance(sub, subnet.Subnet)
        self.assertEqual(self.name, sub.name)
        return sub

    def test_find(self):
        sot = self.user_cloud.network.find_ndp_proxy(self.NP.id)
        self.assertEqual(self.ROT_ID, sot.router_id)
        self.assertEqual(self.INTERNAL_PORT_ID, sot.port_id)
        self.assertEqual(self.INTERNAL_IP_ADDRESS, sot.ip_address)

    def test_get(self):
        sot = self.user_cloud.network.get_ndp_proxy(self.NP.id)
        self.assertEqual(self.ROT_ID, sot.router_id)
        self.assertEqual(self.INTERNAL_PORT_ID, sot.port_id)
        self.assertEqual(self.INTERNAL_IP_ADDRESS, sot.ip_address)

    def test_list(self):
        np_ids = [o.id for o in self.user_cloud.network.ndp_proxies()]
        self.assertIn(self.NP.id, np_ids)

    def test_update(self):
        description = "balabalbala"
        sot = self.user_cloud.network.update_ndp_proxy(
            self.NP.id, description=description
        )
        self.assertEqual(description, sot.description)
