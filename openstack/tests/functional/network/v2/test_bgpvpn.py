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

from openstack.network.v2 import bgpvpn as _bgpvpn
from openstack.network.v2 import (
    bgpvpn_network_association as _bgpvpn_net_assoc,
)
from openstack.network.v2 import bgpvpn_port_association as _bgpvpn_port_assoc
from openstack.network.v2 import (
    bgpvpn_router_association as _bgpvpn_router_assoc,
)
from openstack.network.v2 import network as _network
from openstack.network.v2 import port as _port
from openstack.network.v2 import router as _router
from openstack.network.v2 import subnet as _subnet
from openstack.tests.functional import base


class TestBGPVPN(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.BGPVPN_NAME = 'my_bgpvpn' + self.getUniqueString()
        self.NET_NAME = 'my_net' + self.getUniqueString()
        self.SUBNET_NAME = 'my_subnet' + self.getUniqueString()
        self.PORT_NAME = 'my_port' + self.getUniqueString()
        self.ROUTER_NAME = 'my_router' + self.getUniqueString()
        self.CIDR = "10.101.0.0/24"
        self.ROUTE_DISTINGUISHERS = ['64512:1777', '64512:1888', '64512:1999']
        self.VNI = 1000
        self.ROUTE_TARGETS = ('64512:1444',)
        self.IMPORT_TARGETS = ('64512:1555',)
        self.EXPORT_TARGETS = '64512:1666'
        self.TYPE = 'l3'

        if not self.user_cloud.network.find_extension("bgpvpn"):
            self.skipTest("Neutron BGPVPN Extension disabled")
        bgpvpn = self.operator_cloud.network.create_bgpvpn(
            name=self.BGPVPN_NAME,
            route_distinguishers=self.ROUTE_DISTINGUISHERS,
            route_targets=self.ROUTE_TARGETS,
            import_targets=self.IMPORT_TARGETS,
            export_targets=self.EXPORT_TARGETS,
        )
        assert isinstance(bgpvpn, _bgpvpn.BgpVpn)
        self.BGPVPN = bgpvpn

        net = self.operator_cloud.network.create_network(name=self.NET_NAME)
        assert isinstance(net, _network.Network)
        self.NETWORK = net
        subnet = self.operator_cloud.network.create_subnet(
            name=self.SUBNET_NAME,
            ip_version=4,
            network_id=self.NETWORK.id,
            cidr=self.CIDR,
        )
        assert isinstance(subnet, _subnet.Subnet)
        self.SUBNET = subnet

        port = self.operator_cloud.network.create_port(
            name=self.PORT_NAME, network_id=self.NETWORK.id
        )
        assert isinstance(port, _port.Port)
        self.PORT = port

        router = self.operator_cloud.network.create_router(
            name=self.ROUTER_NAME
        )
        assert isinstance(router, _router.Router)
        self.ROUTER = router

        net_assoc = (
            self.operator_cloud.network.create_bgpvpn_network_association(
                self.BGPVPN, network_id=self.NETWORK.id
            )
        )
        assert isinstance(
            net_assoc, _bgpvpn_net_assoc.BgpVpnNetworkAssociation
        )
        self.NET_ASSOC = net_assoc

        port_assoc = (
            self.operator_cloud.network.create_bgpvpn_port_association(
                self.BGPVPN, port_id=self.PORT.id
            )
        )
        assert isinstance(port_assoc, _bgpvpn_port_assoc.BgpVpnPortAssociation)
        self.PORT_ASSOC = port_assoc

        router_assoc = (
            self.operator_cloud.network.create_bgpvpn_router_association(
                self.BGPVPN, router_id=self.ROUTER.id
            )
        )
        assert isinstance(
            router_assoc, _bgpvpn_router_assoc.BgpVpnRouterAssociation
        )
        self.ROUTER_ASSOC = router_assoc

    def tearDown(self):
        sot = self.operator_cloud.network.delete_bgpvpn(self.BGPVPN.id)
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_bgpvpn_network_association(
            self.BGPVPN.id, self.NET_ASSOC.id
        )
        self.assertIsNone(sot)

        sot = self.operator_cloud.network.delete_bgpvpn_port_association(
            self.BGPVPN.id, self.PORT_ASSOC.id
        )
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_bgpvpn_router_association(
            self.BGPVPN.id, self.ROUTER_ASSOC.id
        )
        self.assertIsNone(sot)

        sot = self.operator_cloud.network.delete_router(self.ROUTER)
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_port(self.PORT)
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_subnet(self.SUBNET)
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_network(self.NETWORK)
        self.assertIsNone(sot)

        super().tearDown()

    def test_find_bgpvpn(self):
        sot = self.operator_cloud.network.find_bgpvpn(self.BGPVPN.name)
        self.assertEqual(list(self.ROUTE_TARGETS), sot.route_targets)
        self.assertEqual(list(self.IMPORT_TARGETS), sot.import_targets)
        # Check defaults
        self.assertEqual(self.TYPE, sot.type)

    def test_get_bgpvpn(self):
        sot = self.operator_cloud.network.get_bgpvpn(self.BGPVPN.id)
        self.assertEqual(list(self.ROUTE_TARGETS), sot.route_targets)
        self.assertEqual([self.EXPORT_TARGETS], sot.export_targets)
        self.assertEqual(list(self.IMPORT_TARGETS), sot.import_targets)

    def test_list_bgpvpns(self):
        bgpvpn_ids = [
            bgpvpn.id for bgpvpn in self.operator_cloud.network.bgpvpns()
        ]
        self.assertIn(self.BGPVPN.id, bgpvpn_ids)

    def test_update_bgpvpn(self):
        sot = self.operator_cloud.network.update_bgpvpn(
            self.BGPVPN.id, import_targets='64512:1333'
        )
        self.assertEqual(['64512:1333'], sot.import_targets)

    def test_get_bgpvpnnetwork_association(self):
        sot = self.operator_cloud.network.get_bgpvpn_network_association(
            self.BGPVPN.id, self.NET_ASSOC.id
        )
        self.assertEqual(self.NETWORK.id, sot.network_id)

    def test_list_bgpvpn_network_associations(self):
        net_assoc_ids = [
            net_assoc.id
            for net_assoc in (
                self.operator_cloud.network.bgpvpn_network_associations(
                    self.BGPVPN.id
                )
            )
        ]
        self.assertIn(self.NET_ASSOC.id, net_assoc_ids)

    def test_get_bgpvpn_port_association(self):
        sot = self.operator_cloud.network.get_bgpvpn_port_association(
            self.BGPVPN.id, self.PORT_ASSOC.id
        )
        self.assertEqual(self.PORT.id, sot.port_id)

    def test_list_bgpvpn_port_associations(self):
        port_assoc_ids = [
            port_assoc.id
            for port_assoc in (
                self.operator_cloud.network.bgpvpn_port_associations(
                    self.BGPVPN.id
                )
            )
        ]
        self.assertIn(self.PORT_ASSOC.id, port_assoc_ids)

    def test_get_bgpvpn_router_association(self):
        sot = self.operator_cloud.network.get_bgpvpn_router_association(
            self.BGPVPN.id, self.ROUTER_ASSOC.id
        )
        self.assertEqual(self.ROUTER.id, sot.router_id)

    def test_list_bgpvpn_router_associations(self):
        router_assoc_ids = [
            router_assoc.id
            for router_assoc in (
                self.operator_cloud.network.bgpvpn_router_associations(
                    self.BGPVPN.id
                )
            )
        ]
        self.assertIn(self.ROUTER_ASSOC.id, router_assoc_ids)
