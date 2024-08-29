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


from openstack.network.v2 import floating_ip
from openstack.network.v2 import network
from openstack.network.v2 import port
from openstack.network.v2 import port_forwarding as _port_forwarding
from openstack.network.v2 import router
from openstack.network.v2 import subnet
from openstack.tests.functional import base


class TestPortForwarding(base.BaseFunctionalTest):
    IPV4 = 4
    FIP_ID = None
    EXT_CIDR = "10.100.0.0/24"
    INT_CIDR = "10.101.0.0/24"
    EXT_NET_ID = None
    INT_NET_ID = None
    EXT_SUB_ID = None
    INT_SUB_ID = None
    ROT_ID = None

    INTERNAL_PORT_ID = None
    INTERNAL_IP_ADDRESS = None
    INTERNAL_PORT = 8080
    EXTERNAL_PORT = 80
    PROTOCOL = "tcp"
    DESCRIPTION = "description"

    def setUp(self):
        super().setUp()

        if not self.user_cloud._has_neutron_extension("external-net"):
            self.skipTest(
                "Neutron external-net extension is required for this test"
            )
        if not self.user_cloud.network.find_extension(
            "floating-ip-port-forwarding"
        ):
            self.skipTest("Floating IP Port Forwarding extension disabled")

        self.ROT_NAME = self.getUniqueString()
        self.INT_NET_NAME = self.getUniqueString()
        self.INT_SUB_NAME = self.getUniqueString()
        self.EXT_NET_ID = None
        self.EXT_SUB_ID = None

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

        # Create Internal Network
        net = self._create_network(self.INT_NET_NAME)
        self.INT_NET_ID = net.id
        sub = self._create_subnet(
            self.INT_SUB_NAME, self.INT_NET_ID, self.INT_CIDR
        )
        self.INT_SUB_ID = sub.id
        # Create Router
        sot = self.user_cloud.network.create_router(
            name=self.ROT_NAME,
            **{"external_gateway_info": {"network_id": self.EXT_NET_ID}},
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
        # Create Floating IP.
        fip = self.user_cloud.network.create_ip(
            floating_network_id=self.EXT_NET_ID
        )
        assert isinstance(fip, floating_ip.FloatingIP)
        self.FIP_ID = fip.id
        # Create Port Forwarding
        pf = self.user_cloud.network.create_port_forwarding(
            floatingip_id=self.FIP_ID,
            internal_port_id=self.INTERNAL_PORT_ID,
            internal_ip_address=self.INTERNAL_IP_ADDRESS,
            internal_port=self.INTERNAL_PORT,
            external_port=self.EXTERNAL_PORT,
            protocol=self.PROTOCOL,
            description=self.DESCRIPTION,
        )
        assert isinstance(pf, _port_forwarding.PortForwarding)
        self.PF = pf

    def tearDown(self):
        sot = self.user_cloud.network.delete_port_forwarding(
            self.PF, self.FIP_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_ip(
            self.FIP_ID, ignore_missing=False
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
            ip_version=self.IPV4,
            network_id=self.net_id,
            cidr=self.cidr,
        )
        assert isinstance(sub, subnet.Subnet)
        self.assertEqual(self.name, sub.name)
        return sub

    def test_find(self):
        sot = self.user_cloud.network.find_port_forwarding(
            self.PF.id, self.FIP_ID
        )
        self.assertEqual(self.INTERNAL_PORT_ID, sot.internal_port_id)
        self.assertEqual(self.INTERNAL_IP_ADDRESS, sot.internal_ip_address)
        self.assertEqual(self.INTERNAL_PORT, sot.internal_port)
        self.assertEqual(self.EXTERNAL_PORT, sot.external_port)
        self.assertEqual(self.PROTOCOL, sot.protocol)
        self.assertEqual(self.DESCRIPTION, sot.description)

    def test_get(self):
        sot = self.user_cloud.network.get_port_forwarding(self.PF, self.FIP_ID)
        self.assertEqual(self.INTERNAL_PORT_ID, sot.internal_port_id)
        self.assertEqual(self.INTERNAL_IP_ADDRESS, sot.internal_ip_address)
        self.assertEqual(self.INTERNAL_PORT, sot.internal_port)
        self.assertEqual(self.EXTERNAL_PORT, sot.external_port)
        self.assertEqual(self.PROTOCOL, sot.protocol)
        self.assertEqual(self.DESCRIPTION, sot.description)

    def test_list(self):
        pf_ids = [
            o.id for o in self.user_cloud.network.port_forwardings(self.FIP_ID)
        ]
        self.assertIn(self.PF.id, pf_ids)

    def test_update(self):
        NEW_EXTERNAL_PORT = 90
        sot = self.user_cloud.network.update_port_forwarding(
            self.PF.id, self.FIP_ID, external_port=NEW_EXTERNAL_PORT
        )
        self.assertEqual(NEW_EXTERNAL_PORT, sot.external_port)
