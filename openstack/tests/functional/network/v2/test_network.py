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
from openstack.tests.functional import base


def create_network(conn, name, cidr):
    try:
        network = conn.network.create_network(name=name)
        subnet = conn.network.create_subnet(
            name=name,
            ip_version=4,
            network_id=network.id,
            cidr=cidr)
        return (network, subnet)
    except Exception as e:
        print(str(e))
        pass
    return (None, None)


def delete_network(conn, network, subnet):
    if subnet:
        conn.network.delete_subnet(subnet)
    if network:
        conn.network.delete_network(network)


class TestNetwork(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex
    ID = None

    @classmethod
    def setUpClass(cls):
        super(TestNetwork, cls).setUpClass()
        sot = cls.conn.network.create_network(name=cls.NAME)
        assert isinstance(sot, network.Network)
        cls.assertIs(cls.NAME, sot.name)
        cls.ID = sot.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_network(cls.ID, ignore_missing=False)
        cls.assertIs(None, sot)

    def test_find(self):
        sot = self.conn.network.find_network(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_network(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        names = [o.name for o in self.conn.network.networks()]
        self.assertIn(self.NAME, names)
