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
from openstack.network.v2 import subnet
from openstack.network.v2 import subnet_pool
from openstack.tests.functional import base


class TestSubnetFromSubnetPool(base.BaseFunctionalTest):

    IPV4 = 4
    CIDR = "10.100.0.0/28"
    MINIMUM_PREFIX_LENGTH = 8
    DEFAULT_PREFIX_LENGTH = 24
    MAXIMUM_PREFIX_LENGTH = 32
    SUBNET_PREFIX_LENGTH = 28
    IP_VERSION = 4
    PREFIXES = ['10.100.0.0/24']
    NET_ID = None
    SUB_ID = None
    SUB_POOL_ID = None

    def setUp(self):
        super(TestSubnetFromSubnetPool, self).setUp()
        self.NET_NAME = self.getUniqueString()
        self.SUB_NAME = self.getUniqueString()
        self.SUB_POOL_NAME = self.getUniqueString()

        sub_pool = self.conn.network.create_subnet_pool(
            name=self.SUB_POOL_NAME,
            min_prefixlen=self.MINIMUM_PREFIX_LENGTH,
            default_prefixlen=self.DEFAULT_PREFIX_LENGTH,
            max_prefixlen=self.MAXIMUM_PREFIX_LENGTH,
            prefixes=self.PREFIXES)
        self.assertIsInstance(sub_pool, subnet_pool.SubnetPool)
        self.assertEqual(self.SUB_POOL_NAME, sub_pool.name)
        self.SUB_POOL_ID = sub_pool.id
        net = self.conn.network.create_network(name=self.NET_NAME)
        self.assertIsInstance(net, network.Network)
        self.assertEqual(self.NET_NAME, net.name)
        self.NET_ID = net.id
        sub = self.conn.network.create_subnet(
            name=self.SUB_NAME,
            ip_version=self.IPV4,
            network_id=self.NET_ID,
            prefixlen=self.SUBNET_PREFIX_LENGTH,
            subnetpool_id=self.SUB_POOL_ID)
        self.assertIsInstance(sub, subnet.Subnet)
        self.assertEqual(self.SUB_NAME, sub.name)
        self.SUB_ID = sub.id

    def tearDown(self):
        sot = self.conn.network.delete_subnet(self.SUB_ID)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_network(
            self.NET_ID, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_subnet_pool(self.SUB_POOL_ID)
        self.assertIsNone(sot)
        super(TestSubnetFromSubnetPool, self).tearDown()

    def test_get(self):
        sot = self.conn.network.get_subnet(self.SUB_ID)
        self.assertEqual(self.SUB_NAME, sot.name)
        self.assertEqual(self.SUB_ID, sot.id)
        self.assertEqual(self.CIDR, sot.cidr)
        self.assertEqual(self.IPV4, sot.ip_version)
        self.assertEqual("10.100.0.1", sot.gateway_ip)
        self.assertTrue(sot.is_dhcp_enabled)
