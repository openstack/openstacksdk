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

    ID = None

    def setUp(self):
        super(TestNetwork, self).setUp()
        self.NAME = self.getUniqueString()
        sot = self.conn.network.create_network(name=self.NAME)
        assert isinstance(sot, network.Network)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id

    def tearDown(self):
        sot = self.conn.network.delete_network(self.ID, ignore_missing=False)
        self.assertIsNone(sot)
        super(TestNetwork, self).tearDown()

    def test_find(self):
        sot = self.conn.network.find_network(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_find_with_filter(self):
        project_id_1 = "1"
        project_id_2 = "2"
        sot1 = self.conn.network.create_network(name=self.NAME,
                                                project_id=project_id_1)
        sot2 = self.conn.network.create_network(name=self.NAME,
                                                project_id=project_id_2)
        sot = self.conn.network.find_network(self.NAME,
                                             project_id=project_id_1)
        self.assertEqual(project_id_1, sot.project_id)
        self.conn.network.delete_network(sot1.id)
        self.conn.network.delete_network(sot2.id)

    def test_get(self):
        sot = self.conn.network.get_network(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        names = [o.name for o in self.conn.network.networks()]
        self.assertIn(self.NAME, names)

    def test_set_tags(self):
        sot = self.conn.network.get_network(self.ID)
        self.assertEqual([], sot.tags)

        self.conn.network.set_tags(sot, ['blue'])
        sot = self.conn.network.get_network(self.ID)
        self.assertEqual(['blue'], sot.tags)

        self.conn.network.set_tags(sot, [])
        sot = self.conn.network.get_network(self.ID)
        self.assertEqual([], sot.tags)
