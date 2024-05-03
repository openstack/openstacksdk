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
from openstack.network.v2 import trunk as _trunk
from openstack.tests.functional import base


class TestTrunk(base.BaseFunctionalTest):
    TIMEOUT_SCALING_FACTOR = 2.0

    def setUp(self):
        super().setUp()

        # Skip the tests if trunk extension is not enabled.
        if not self.user_cloud.network.find_extension("trunk"):
            self.skipTest("Network trunk extension disabled")

        self.TRUNK_NAME = self.getUniqueString()
        self.TRUNK_NAME_UPDATED = self.getUniqueString()
        net = self.user_cloud.network.create_network()
        assert isinstance(net, network.Network)
        self.NET_ID = net.id
        prt = self.user_cloud.network.create_port(network_id=self.NET_ID)
        assert isinstance(prt, port.Port)
        self.PORT_ID = prt.id
        self.ports_to_clean = [self.PORT_ID]
        trunk = self.user_cloud.network.create_trunk(
            name=self.TRUNK_NAME, port_id=self.PORT_ID
        )
        assert isinstance(trunk, _trunk.Trunk)
        self.TRUNK_ID = trunk.id

    def tearDown(self):
        self.user_cloud.network.delete_trunk(
            self.TRUNK_ID, ignore_missing=False
        )
        for port_id in self.ports_to_clean:
            self.user_cloud.network.delete_port(port_id, ignore_missing=False)
        self.user_cloud.network.delete_network(
            self.NET_ID, ignore_missing=False
        )
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_trunk(self.TRUNK_NAME)
        self.assertEqual(self.TRUNK_ID, sot.id)

    def test_get(self):
        sot = self.user_cloud.network.get_trunk(self.TRUNK_ID)
        self.assertEqual(self.TRUNK_ID, sot.id)
        self.assertEqual(self.TRUNK_NAME, sot.name)

    def test_list(self):
        ids = [o.id for o in self.user_cloud.network.trunks()]
        self.assertIn(self.TRUNK_ID, ids)

    def test_update(self):
        sot = self.user_cloud.network.update_trunk(
            self.TRUNK_ID, name=self.TRUNK_NAME_UPDATED
        )
        self.assertEqual(self.TRUNK_NAME_UPDATED, sot.name)

    def test_subports(self):
        port_for_subport = self.user_cloud.network.create_port(
            network_id=self.NET_ID
        )
        self.ports_to_clean.append(port_for_subport.id)
        subports = [
            {
                "port_id": port_for_subport.id,
                "segmentation_type": "vlan",
                "segmentation_id": 111,
            }
        ]

        sot = self.user_cloud.network.get_trunk_subports(self.TRUNK_ID)
        self.assertEqual({"sub_ports": []}, sot)

        self.user_cloud.network.add_trunk_subports(self.TRUNK_ID, subports)
        sot = self.user_cloud.network.get_trunk_subports(self.TRUNK_ID)
        self.assertEqual({"sub_ports": subports}, sot)

        self.user_cloud.network.delete_trunk_subports(
            self.TRUNK_ID, [{"port_id": port_for_subport.id}]
        )
        sot = self.user_cloud.network.get_trunk_subports(self.TRUNK_ID)
        self.assertEqual({"sub_ports": []}, sot)
