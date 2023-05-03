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

from openstack.network.v2 import network as _network
from openstack.network.v2 import port as _port
from openstack.network.v2 import tap_flow as _tap_flow
from openstack.network.v2 import tap_service as _tap_service
from openstack.tests.functional import base


class TestTapService(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.user_cloud.network.find_extension("taas"):
            self.skipTest("Neutron Tap-as-a-service Extension disabled")

        self.TAP_S_NAME = 'my_service' + self.getUniqueString()
        self.TAP_F_NAME = 'my_flow' + self.getUniqueString()
        net = self.user_cloud.network.create_network()
        assert isinstance(net, _network.Network)
        self.SERVICE_NET_ID = net.id

        net = self.user_cloud.network.create_network()
        assert isinstance(net, _network.Network)
        self.FLOW_NET_ID = net.id

        port = self.user_cloud.network.create_port(
            network_id=self.SERVICE_NET_ID
        )
        assert isinstance(port, _port.Port)
        self.SERVICE_PORT_ID = port.id

        port = self.user_cloud.network.create_port(network_id=self.FLOW_NET_ID)
        assert isinstance(port, _port.Port)
        self.FLOW_PORT_ID = port.id

        tap_service = self.user_cloud.network.create_tap_service(
            name=self.TAP_S_NAME, port_id=self.SERVICE_PORT_ID
        )
        assert isinstance(tap_service, _tap_service.TapService)
        self.TAP_SERVICE = tap_service

        tap_flow = self.user_cloud.network.create_tap_flow(
            name=self.TAP_F_NAME,
            tap_service_id=self.TAP_SERVICE.id,
            source_port=self.FLOW_PORT_ID,
            direction='BOTH',
        )
        assert isinstance(tap_flow, _tap_flow.TapFlow)
        self.TAP_FLOW = tap_flow

    def tearDown(self):
        sot = self.user_cloud.network.delete_tap_flow(
            self.TAP_FLOW.id, ignore_missing=False
        )
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_tap_service(
            self.TAP_SERVICE.id, ignore_missing=False
        )
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_port(self.SERVICE_PORT_ID)
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_port(self.FLOW_PORT_ID)
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_network(self.SERVICE_NET_ID)
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_network(self.FLOW_NET_ID)
        self.assertIsNone(sot)
        super().tearDown()

    def test_find_tap_service(self):
        sot = self.user_cloud.network.find_tap_service(self.TAP_SERVICE.name)
        self.assertEqual(self.SERVICE_PORT_ID, sot.port_id)
        self.assertEqual(self.TAP_S_NAME, sot.name)

    def test_get_tap_service(self):
        sot = self.user_cloud.network.get_tap_service(self.TAP_SERVICE.id)
        self.assertEqual(self.SERVICE_PORT_ID, sot.port_id)
        self.assertEqual(self.TAP_S_NAME, sot.name)

    def test_list_tap_services(self):
        tap_service_ids = [
            ts.id for ts in self.user_cloud.network.tap_services()
        ]
        self.assertIn(self.TAP_SERVICE.id, tap_service_ids)

    def test_update_tap_service(self):
        description = 'My tap service'
        sot = self.user_cloud.network.update_tap_service(
            self.TAP_SERVICE.id, description=description
        )
        self.assertEqual(description, sot.description)

    def test_find_tap_flow(self):
        sot = self.user_cloud.network.find_tap_flow(self.TAP_FLOW.name)
        self.assertEqual(self.FLOW_PORT_ID, sot.source_port)
        self.assertEqual(self.TAP_SERVICE.id, sot.tap_service_id)
        self.assertEqual('BOTH', sot.direction)
        self.assertEqual(self.TAP_F_NAME, sot.name)

    def test_get_tap_flow(self):
        sot = self.user_cloud.network.get_tap_flow(self.TAP_FLOW.id)
        self.assertEqual(self.FLOW_PORT_ID, sot.source_port)
        self.assertEqual(self.TAP_F_NAME, sot.name)
        self.assertEqual(self.TAP_SERVICE.id, sot.tap_service_id)
        self.assertEqual('BOTH', sot.direction)

    def test_list_tap_flows(self):
        tap_flow_ids = [tf.id for tf in self.user_cloud.network.tap_flows()]
        self.assertIn(self.TAP_FLOW.id, tap_flow_ids)

    def test_update_tap_flow(self):
        description = 'My tap flow'
        sot = self.user_cloud.network.update_tap_flow(
            self.TAP_FLOW.id, description=description
        )
        self.assertEqual(description, sot.description)
