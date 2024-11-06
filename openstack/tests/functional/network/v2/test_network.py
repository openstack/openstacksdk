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
from openstack.tests.functional.network.v2 import common


def create_network(conn, name, cidr):
    try:
        network = conn.network.create_network(name=name)
        subnet = conn.network.create_subnet(
            name=name, ip_version=4, network_id=network.id, cidr=cidr
        )
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


class TestNetwork(common.TestTagNeutron):
    ID = None

    def setUp(self):
        super().setUp()
        self.NAME = self.getUniqueString()
        sot = self.user_cloud.network.create_network(name=self.NAME)
        assert isinstance(sot, network.Network)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id
        self.get_command = self.user_cloud.network.get_network

    def tearDown(self):
        sot = self.user_cloud.network.delete_network(
            self.ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_network(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_find_with_filter(self):
        if not self.operator_cloud:
            self.skipTest("Operator cloud required for this test")
        project_id_1 = "1"
        project_id_2 = "2"
        sot1 = self.operator_cloud.network.create_network(
            name=self.NAME, project_id=project_id_1
        )
        sot2 = self.operator_cloud.network.create_network(
            name=self.NAME, project_id=project_id_2
        )
        sot = self.operator_cloud.network.find_network(
            self.NAME, project_id=project_id_1
        )
        self.assertEqual(project_id_1, sot.project_id)
        self.operator_cloud.network.delete_network(sot1.id)
        self.operator_cloud.network.delete_network(sot2.id)

    def test_get(self):
        sot = self.user_cloud.network.get_network(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        names = [o.name for o in self.user_cloud.network.networks()]
        self.assertIn(self.NAME, names)
