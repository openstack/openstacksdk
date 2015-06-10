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
from openstack.network.v2 import subnet
from openstack.tests.functional import base


class TestFloatingIP(base.BaseFunctionalTest):

    NET_NAME = uuid.uuid4().hex
    SUB_NAME = uuid.uuid4().hex
    IPV4 = 4
    CIDR = "10.100.0.0/24"
    NET_ID = None
    SUB_ID = None
    FIP_ID = None

    @classmethod
    def setUpClass(cls):
        super(TestFloatingIP, cls).setUpClass()
        args = {'router:external': True}
        net = cls.conn.network.create_network(name=cls.NET_NAME, **args)
        assert isinstance(net, network.Network)
        cls.assertIs(cls.NET_NAME, net.name)
        cls.NET_ID = net.id
        sub = cls.conn.network.create_subnet(name=cls.SUB_NAME,
                                             ip_version=cls.IPV4,
                                             network_id=cls.NET_ID,
                                             cidr=cls.CIDR)
        assert isinstance(sub, subnet.Subnet)
        cls.assertIs(cls.SUB_NAME, sub.name)
        cls.SUB_ID = sub.id
        fip = cls.conn.network.create_ip(floating_network_id=cls.NET_ID)
        assert isinstance(fip, floating_ip.FloatingIP)
        cls.FIP_ID = fip.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_ip(cls.FIP_ID, ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_subnet(cls.SUB_ID, ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_network(cls.NET_ID, ignore_missing=False)
        cls.assertIs(None, sot)

    def test_find(self):
        sot = self.conn.network.find_ip(self.FIP_ID)
        self.assertEqual(self.FIP_ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_ip(self.FIP_ID)
        self.assertEqual(self.NET_ID, sot.floating_network_id)
        self.assertEqual('10.100.0.2', sot.floating_ip_address)
        self.assertIn('floating_ip_address', sot)
        self.assertIn('fixed_ip_address', sot)
        self.assertIn('port_id', sot)
        self.assertIn('router_id', sot)

    def test_list(self):
        ids = [o.id for o in self.conn.network.ips()]
        self.assertIn(self.FIP_ID, ids)
