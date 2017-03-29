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

from openstack.network.v2 import floating_ip
from openstack.network.v2 import network
from openstack.network.v2 import port
from openstack.network.v2 import router
from openstack.network.v2 import subnet
from openstack.tests.functional import base


class TestFloatingIP(base.BaseFunctionalTest):

    ROT_NAME = uuid.uuid4().hex
    EXT_NET_NAME = uuid.uuid4().hex
    EXT_SUB_NAME = uuid.uuid4().hex
    INT_NET_NAME = uuid.uuid4().hex
    INT_SUB_NAME = uuid.uuid4().hex
    IPV4 = 4
    EXT_CIDR = "10.100.0.0/24"
    INT_CIDR = "10.101.0.0/24"
    EXT_NET_ID = None
    INT_NET_ID = None
    EXT_SUB_ID = None
    INT_SUB_ID = None
    ROT_ID = None
    PORT_ID = None
    FIP = None

    @classmethod
    def setUpClass(cls):
        super(TestFloatingIP, cls).setUpClass()
        # Create Exeternal Network
        args = {'router:external': True}
        net = cls._create_network(cls.EXT_NET_NAME, **args)
        cls.EXT_NET_ID = net.id
        sub = cls._create_subnet(cls.EXT_SUB_NAME, cls.EXT_NET_ID,
                                 cls.EXT_CIDR)
        cls.EXT_SUB_ID = sub.id
        # Create Internal Network
        net = cls._create_network(cls.INT_NET_NAME)
        cls.INT_NET_ID = net.id
        sub = cls._create_subnet(cls.INT_SUB_NAME, cls.INT_NET_ID,
                                 cls.INT_CIDR)
        cls.INT_SUB_ID = sub.id
        # Create Router
        args = {'external_gateway_info': {'network_id': cls.EXT_NET_ID}}
        sot = cls.conn.network.create_router(name=cls.ROT_NAME, **args)
        assert isinstance(sot, router.Router)
        cls.assertIs(cls.ROT_NAME, sot.name)
        cls.ROT_ID = sot.id
        cls.ROT = sot
        # Add Router's Interface to Internal Network
        sot = cls.ROT.add_interface(cls.conn.session, subnet_id=cls.INT_SUB_ID)
        cls.assertIs(sot['subnet_id'], cls.INT_SUB_ID)
        # Create Port in Internal Network
        prt = cls.conn.network.create_port(network_id=cls.INT_NET_ID)
        assert isinstance(prt, port.Port)
        cls.PORT_ID = prt.id
        # Create Floating IP.
        fip = cls.conn.network.create_ip(floating_network_id=cls.EXT_NET_ID)
        assert isinstance(fip, floating_ip.FloatingIP)
        cls.FIP = fip

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_ip(cls.FIP.id, ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_port(cls.PORT_ID, ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.ROT.remove_interface(cls.conn.session,
                                       subnet_id=cls.INT_SUB_ID)
        cls.assertIs(sot['subnet_id'], cls.INT_SUB_ID)
        sot = cls.conn.network.delete_router(cls.ROT_ID, ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_subnet(cls.EXT_SUB_ID,
                                             ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_network(cls.EXT_NET_ID,
                                              ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_subnet(cls.INT_SUB_ID,
                                             ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_network(cls.INT_NET_ID,
                                              ignore_missing=False)
        cls.assertIs(None, sot)

    @classmethod
    def _create_network(cls, name, **args):
        cls.name = name
        net = cls.conn.network.create_network(name=name, **args)
        assert isinstance(net, network.Network)
        cls.assertIs(cls.name, net.name)
        return net

    @classmethod
    def _create_subnet(cls, name, net_id, cidr):
        cls.name = name
        cls.net_id = net_id
        cls.cidr = cidr
        sub = cls.conn.network.create_subnet(name=cls.name,
                                             ip_version=cls.IPV4,
                                             network_id=cls.net_id,
                                             cidr=cls.cidr)
        assert isinstance(sub, subnet.Subnet)
        cls.assertIs(cls.name, sub.name)
        return sub

    def test_find_by_id(self):
        sot = self.conn.network.find_ip(self.FIP.id)
        self.assertEqual(self.FIP.id, sot.id)

    def test_find_by_ip_address(self):
        sot = self.conn.network.find_ip(self.FIP.floating_ip_address)
        self.assertEqual(self.FIP.floating_ip_address, sot.floating_ip_address)
        self.assertEqual(self.FIP.floating_ip_address, sot.name)

    def test_find_available_ip(self):
        sot = self.conn.network.find_available_ip()
        self.assertIsNotNone(sot.id)
        self.assertIsNone(sot.port_id)

    def test_get(self):
        sot = self.conn.network.get_ip(self.FIP.id)
        self.assertEqual(self.EXT_NET_ID, sot.floating_network_id)
        self.assertEqual(self.FIP.id, sot.id)
        self.assertEqual(self.FIP.floating_ip_address, sot.floating_ip_address)
        self.assertEqual(self.FIP.fixed_ip_address, sot.fixed_ip_address)
        self.assertEqual(self.FIP.port_id, sot.port_id)
        self.assertEqual(self.FIP.router_id, sot.router_id)

    def test_list(self):
        ids = [o.id for o in self.conn.network.ips()]
        self.assertIn(self.FIP.id, ids)

    def test_update(self):
        sot = self.conn.network.update_ip(self.FIP.id, port_id=self.PORT_ID)
        self.assertEqual(self.PORT_ID, sot.port_id)
        self.assertEqual(self.FIP.id, sot.id)
