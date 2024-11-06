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
# mypy: disable-error-code="method-assign"

from openstack.network.v2 import network
from openstack.network.v2 import subnet
from openstack.tests.functional.network.v2 import common


class TestSubnet(common.TestTagNeutron):
    IPV4 = 4
    CIDR = "10.100.0.0/24"
    DNS_SERVERS = ["8.8.4.4", "8.8.8.8"]
    POOL = [{"start": "10.100.0.2", "end": "10.100.0.253"}]
    ROUTES = [{"destination": "10.101.0.0/24", "nexthop": "10.100.0.254"}]
    NET_ID = None
    SUB_ID = None

    def setUp(self):
        super().setUp()
        self.NET_NAME = self.getUniqueString()
        self.SUB_NAME = self.getUniqueString()
        self.UPDATE_NAME = self.getUniqueString()
        net = self.user_cloud.network.create_network(name=self.NET_NAME)
        assert isinstance(net, network.Network)
        self.assertEqual(self.NET_NAME, net.name)
        self.NET_ID = net.id
        sub = self.user_cloud.network.create_subnet(
            name=self.SUB_NAME,
            ip_version=self.IPV4,
            network_id=self.NET_ID,
            cidr=self.CIDR,
            dns_nameservers=self.DNS_SERVERS,
            allocation_pools=self.POOL,
            host_routes=self.ROUTES,
        )
        assert isinstance(sub, subnet.Subnet)
        self.assertEqual(self.SUB_NAME, sub.name)
        self.SUB_ID = self.ID = sub.id
        self.get_command = self.user_cloud.network.get_subnet

    def tearDown(self):
        sot = self.user_cloud.network.delete_subnet(self.SUB_ID)
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_network(
            self.NET_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_subnet(self.SUB_NAME)
        self.assertEqual(self.SUB_ID, sot.id)

    def test_get(self):
        sot = self.user_cloud.network.get_subnet(self.SUB_ID)
        self.assertEqual(self.SUB_NAME, sot.name)
        self.assertEqual(self.SUB_ID, sot.id)
        self.assertEqual(self.DNS_SERVERS, sot.dns_nameservers)
        self.assertEqual(self.CIDR, sot.cidr)
        self.assertEqual(self.POOL, sot.allocation_pools)
        self.assertEqual(self.IPV4, sot.ip_version)
        self.assertEqual(self.ROUTES, sot.host_routes)
        self.assertEqual("10.100.0.1", sot.gateway_ip)
        self.assertTrue(sot.is_dhcp_enabled)

    def test_list(self):
        names = [o.name for o in self.user_cloud.network.subnets()]
        self.assertIn(self.SUB_NAME, names)

    def test_update(self):
        sot = self.user_cloud.network.update_subnet(
            self.SUB_ID, name=self.UPDATE_NAME
        )
        self.assertEqual(self.UPDATE_NAME, sot.name)
