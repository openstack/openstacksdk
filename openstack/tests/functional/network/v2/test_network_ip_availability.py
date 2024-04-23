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
from openstack.network.v2 import port
from openstack.network.v2 import subnet
from openstack.tests.functional import base


class TestNetworkIPAvailability(base.BaseFunctionalTest):
    IPV4 = 4
    CIDR = "10.100.0.0/24"
    NET_ID = None
    SUB_ID = None
    PORT_ID = None

    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud required for this test")
        if not self.operator_cloud._has_neutron_extension(
            "network-ip-availability"
        ):
            self.skipTest(
                "Neutron network-ip-availability extension is required "
                "for this test"
            )

        self.NET_NAME = self.getUniqueString()
        self.SUB_NAME = self.getUniqueString()
        self.PORT_NAME = self.getUniqueString()
        self.UPDATE_NAME = self.getUniqueString()
        net = self.operator_cloud.network.create_network(name=self.NET_NAME)
        assert isinstance(net, network.Network)
        self.assertEqual(self.NET_NAME, net.name)
        self.NET_ID = net.id
        sub = self.operator_cloud.network.create_subnet(
            name=self.SUB_NAME,
            ip_version=self.IPV4,
            network_id=self.NET_ID,
            cidr=self.CIDR,
        )
        assert isinstance(sub, subnet.Subnet)
        self.assertEqual(self.SUB_NAME, sub.name)
        self.SUB_ID = sub.id
        prt = self.operator_cloud.network.create_port(
            name=self.PORT_NAME, network_id=self.NET_ID
        )
        assert isinstance(prt, port.Port)
        self.assertEqual(self.PORT_NAME, prt.name)
        self.PORT_ID = prt.id

    def tearDown(self):
        sot = self.operator_cloud.network.delete_port(self.PORT_ID)
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_subnet(self.SUB_ID)
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_network(self.NET_ID)
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.operator_cloud.network.find_network_ip_availability(
            self.NET_ID
        )
        self.assertEqual(self.NET_ID, sot.network_id)

    def test_get(self):
        sot = self.operator_cloud.network.get_network_ip_availability(
            self.NET_ID
        )
        self.assertEqual(self.NET_ID, sot.network_id)
        self.assertEqual(self.NET_NAME, sot.network_name)

    def test_list(self):
        ids = [
            o.network_id
            for o in self.operator_cloud.network.network_ip_availabilities()
        ]
        self.assertIn(self.NET_ID, ids)
