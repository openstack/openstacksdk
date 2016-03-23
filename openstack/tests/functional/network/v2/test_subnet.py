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
from openstack.network.v2 import subnet
from openstack.tests.functional import base


class TestSubnet(base.BaseFunctionalTest):

    NET_NAME = uuid.uuid4().hex
    SUB_NAME = uuid.uuid4().hex
    UPDATE_NAME = uuid.uuid4().hex
    IPV4 = 4
    CIDR = "10.100.0.0/24"
    DNS_SERVERS = ["8.8.4.4", "8.8.8.8"]
    POOL = [{"start": "10.100.0.2", "end": "10.100.0.253"}]
    ROUTES = [{"destination": "10.101.0.0/24", "nexthop": "10.100.0.254"}]
    NET_ID = None
    SUB_ID = None

    @classmethod
    def setUpClass(cls):
        super(TestSubnet, cls).setUpClass()
        net = cls.conn.network.create_network(name=cls.NET_NAME)
        assert isinstance(net, network.Network)
        cls.assertIs(cls.NET_NAME, net.name)
        cls.NET_ID = net.id
        sub = cls.conn.network.create_subnet(name=cls.SUB_NAME,
                                             ip_version=cls.IPV4,
                                             network_id=cls.NET_ID,
                                             cidr=cls.CIDR,
                                             dns_nameservers=cls.DNS_SERVERS,
                                             allocation_pools=cls.POOL,
                                             host_routes=cls.ROUTES)
        assert isinstance(sub, subnet.Subnet)
        cls.assertIs(cls.SUB_NAME, sub.name)
        cls.SUB_ID = sub.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_subnet(cls.SUB_ID)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_network(cls.NET_ID, ignore_missing=False)
        cls.assertIs(None, sot)

    def test_find(self):
        sot = self.conn.network.find_subnet(self.SUB_NAME)
        self.assertEqual(self.SUB_ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_subnet(self.SUB_ID)
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
        names = [o.name for o in self.conn.network.subnets()]
        self.assertIn(self.SUB_NAME, names)

    def test_update(self):
        sot = self.conn.network.update_subnet(self.SUB_ID,
                                              name=self.UPDATE_NAME)
        self.assertEqual(self.UPDATE_NAME, sot.name)
