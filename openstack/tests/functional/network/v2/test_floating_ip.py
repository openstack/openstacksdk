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
from openstack.network.v2 import router
from openstack.network.v2 import subnet
from openstack.tests.functional import base


class TestFloatingIP(base.BaseFunctionalTest):

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
    DNS_DOMAIN = "example.org."
    DNS_NAME = "fip1"

    def setUp(self):
        super(TestFloatingIP, self).setUp()
        self.TIMEOUT_SCALING_FACTOR = 1.5
        self.ROT_NAME = self.getUniqueString()
        self.EXT_NET_NAME = self.getUniqueString()
        self.EXT_SUB_NAME = self.getUniqueString()
        self.INT_NET_NAME = self.getUniqueString()
        self.INT_SUB_NAME = self.getUniqueString()
        # Create Exeternal Network
        args = {'router:external': True}
        net = self._create_network(self.EXT_NET_NAME, **args)
        self.EXT_NET_ID = net.id
        sub = self._create_subnet(
            self.EXT_SUB_NAME, self.EXT_NET_ID, self.EXT_CIDR)
        self.EXT_SUB_ID = sub.id
        # Create Internal Network
        net = self._create_network(self.INT_NET_NAME)
        self.INT_NET_ID = net.id
        sub = self._create_subnet(
            self.INT_SUB_NAME, self.INT_NET_ID, self.INT_CIDR)
        self.INT_SUB_ID = sub.id
        # Create Router
        args = {'external_gateway_info': {'network_id': self.EXT_NET_ID}}
        sot = self.conn.network.create_router(name=self.ROT_NAME, **args)
        assert isinstance(sot, router.Router)
        self.assertEqual(self.ROT_NAME, sot.name)
        self.ROT_ID = sot.id
        self.ROT = sot
        # Add Router's Interface to Internal Network
        sot = self.ROT.add_interface(
            self.conn.network, subnet_id=self.INT_SUB_ID)
        self.assertEqual(sot['subnet_id'], self.INT_SUB_ID)
        # Create Port in Internal Network
        prt = self.conn.network.create_port(network_id=self.INT_NET_ID)
        assert isinstance(prt, port.Port)
        self.PORT_ID = prt.id
        self.PORT = prt
        # Create Floating IP.
        fip = self.conn.network.create_ip(
            floating_network_id=self.EXT_NET_ID,
            dns_domain=self.DNS_DOMAIN, dns_name=self.DNS_NAME)
        assert isinstance(fip, floating_ip.FloatingIP)
        self.FIP = fip

    def tearDown(self):
        sot = self.conn.network.delete_ip(self.FIP.id, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_port(self.PORT_ID, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.ROT.remove_interface(
            self.conn.network, subnet_id=self.INT_SUB_ID)
        self.assertEqual(sot['subnet_id'], self.INT_SUB_ID)
        sot = self.conn.network.delete_router(
            self.ROT_ID, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_subnet(
            self.EXT_SUB_ID, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_network(
            self.EXT_NET_ID, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_subnet(
            self.INT_SUB_ID, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_network(
            self.INT_NET_ID, ignore_missing=False)
        self.assertIsNone(sot)
        super(TestFloatingIP, self).tearDown()

    def _create_network(self, name, **args):
        self.name = name
        net = self.conn.network.create_network(name=name, **args)
        assert isinstance(net, network.Network)
        self.assertEqual(self.name, net.name)
        return net

    def _create_subnet(self, name, net_id, cidr):
        self.name = name
        self.net_id = net_id
        self.cidr = cidr
        sub = self.conn.network.create_subnet(
            name=self.name,
            ip_version=self.IPV4,
            network_id=self.net_id,
            cidr=self.cidr)
        assert isinstance(sub, subnet.Subnet)
        self.assertEqual(self.name, sub.name)
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
        self.assertIsNone(sot.port_details)

    def test_get(self):
        sot = self.conn.network.get_ip(self.FIP.id)
        self.assertEqual(self.EXT_NET_ID, sot.floating_network_id)
        self.assertEqual(self.FIP.id, sot.id)
        self.assertEqual(self.FIP.floating_ip_address, sot.floating_ip_address)
        self.assertEqual(self.FIP.fixed_ip_address, sot.fixed_ip_address)
        self.assertEqual(self.FIP.port_id, sot.port_id)
        self.assertEqual(self.FIP.port_details, sot.port_details)
        self.assertEqual(self.FIP.router_id, sot.router_id)
        self.assertEqual(self.DNS_DOMAIN, sot.dns_domain)
        self.assertEqual(self.DNS_NAME, sot.dns_name)

    def test_list(self):
        ids = [o.id for o in self.conn.network.ips()]
        self.assertIn(self.FIP.id, ids)

    def test_update(self):
        sot = self.conn.network.update_ip(self.FIP.id, port_id=self.PORT_ID)
        self.assertEqual(self.PORT_ID, sot.port_id)
        self._assert_port_details(self.PORT, sot.port_details)
        self.assertEqual(self.FIP.id, sot.id)

    def test_set_tags(self):
        sot = self.conn.network.get_ip(self.FIP.id)
        self.assertEqual([], sot.tags)

        self.conn.network.set_tags(sot, ['blue'])
        sot = self.conn.network.get_ip(self.FIP.id)
        self.assertEqual(['blue'], sot.tags)

        self.conn.network.set_tags(sot, [])
        sot = self.conn.network.get_ip(self.FIP.id)
        self.assertEqual([], sot.tags)

    def _assert_port_details(self, port, port_details):
        self.assertEqual(port.name, port_details['name'])
        self.assertEqual(port.network_id, port_details['network_id'])
        self.assertEqual(port.mac_address, port_details['mac_address'])
        self.assertEqual(port.is_admin_state_up,
                         port_details['admin_state_up'])
        self.assertEqual(port.status, port_details['status'])
        self.assertEqual(port.device_id, port_details['device_id'])
        self.assertEqual(port.device_owner, port_details['device_owner'])
