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
from openstack.network.v2 import tap_mirror as _tap_mirror
from openstack.tests.functional import base


class TestTapMirror(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.user_cloud.network.find_extension("tap-mirror"):
            self.skipTest("Neutron Tap Mirror Extension disabled")

        self.TAP_M_NAME = 'my_tap_mirror' + self.getUniqueString()
        net = self.user_cloud.network.create_network()
        assert isinstance(net, _network.Network)
        self.MIRROR_NET_ID = net.id

        port = self.user_cloud.network.create_port(
            network_id=self.MIRROR_NET_ID
        )
        assert isinstance(port, _port.Port)
        self.MIRROR_PORT_ID = port.id

        self.REMOTE_IP = '193.10.10.2'
        self.MIRROR_TYPE = 'erspanv1'

        tap_mirror = self.user_cloud.network.create_tap_mirror(
            name=self.TAP_M_NAME,
            port_id=self.MIRROR_PORT_ID,
            remote_ip=self.REMOTE_IP,
            mirror_type=self.MIRROR_TYPE,
            directions={'IN': 99},
        )
        assert isinstance(tap_mirror, _tap_mirror.TapMirror)
        self.TAP_MIRROR = tap_mirror

    def tearDown(self):
        sot = self.user_cloud.network.delete_tap_mirror(
            self.TAP_MIRROR.id, ignore_missing=False
        )
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_port(self.MIRROR_PORT_ID)
        self.assertIsNone(sot)
        sot = self.user_cloud.network.delete_network(self.MIRROR_NET_ID)
        self.assertIsNone(sot)

        super().tearDown()

    def test_find_tap_mirror(self):
        sot = self.user_cloud.network.find_tap_mirror(self.TAP_MIRROR.name)
        self.assertEqual(self.MIRROR_PORT_ID, sot.port_id)
        self.assertEqual(self.TAP_M_NAME, sot.name)

    def test_get_tap_mirror(self):
        sot = self.user_cloud.network.get_tap_mirror(self.TAP_MIRROR.id)
        self.assertEqual(self.MIRROR_PORT_ID, sot.port_id)
        self.assertEqual(self.TAP_M_NAME, sot.name)

    def test_list_tap_mirrors(self):
        tap_mirror_ids = [
            tm.id for tm in self.user_cloud.network.tap_mirrors()
        ]
        self.assertIn(self.TAP_MIRROR.id, tap_mirror_ids)

    def test_update_tap_mirror(self):
        description = 'My Tap Mirror'
        sot = self.user_cloud.network.update_tap_mirror(
            self.TAP_MIRROR.id, description=description
        )
        self.assertEqual(description, sot.description)
