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

from openstack.network.v2 import bgp_peer as _bgp_peer
from openstack.network.v2 import bgp_speaker as _bgp_speaker
from openstack.tests.functional import base


class TestBGPSpeaker(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.LOCAL_AS = 101
        self.IP_VERSION = 4
        self.REMOTE_AS = 42
        self.PEER_IP = '172.200.12.3'
        self.SPEAKER_NAME = 'my_speaker' + self.getUniqueString()
        self.PEER_NAME = 'my_peer' + self.getUniqueString()

        if not self.user_cloud.network.find_extension("bgp"):
            self.skipTest("Neutron BGP Dynamic Routing Extension disabled")

        bgp_speaker = self.operator_cloud.network.create_bgp_speaker(
            ip_version=self.IP_VERSION,
            local_as=self.LOCAL_AS,
            name=self.SPEAKER_NAME,
        )
        assert isinstance(bgp_speaker, _bgp_speaker.BgpSpeaker)
        self.SPEAKER = bgp_speaker

        bgp_peer = self.operator_cloud.network.create_bgp_peer(
            name=self.PEER_NAME,
            auth_type='none',
            remote_as=self.REMOTE_AS,
            peer_ip=self.PEER_IP,
        )
        assert isinstance(bgp_peer, _bgp_peer.BgpPeer)
        self.PEER = bgp_peer

    def tearDown(self):
        sot = self.operator_cloud.network.delete_bgp_peer(self.PEER.id)
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_bgp_speaker(self.SPEAKER.id)
        self.assertIsNone(sot)
        super().tearDown()

    def test_find_bgp_speaker(self):
        sot = self.operator_cloud.network.find_bgp_speaker(self.SPEAKER.name)
        self.assertEqual(self.IP_VERSION, sot.ip_version)
        self.assertEqual(self.LOCAL_AS, sot.local_as)
        # Check defaults
        self.assertTrue(sot.advertise_floating_ip_host_routes)
        self.assertTrue(sot.advertise_tenant_networks)

    def test_get_bgp_speaker(self):
        sot = self.operator_cloud.network.get_bgp_speaker(self.SPEAKER.id)
        self.assertEqual(self.IP_VERSION, sot.ip_version)
        self.assertEqual(self.LOCAL_AS, sot.local_as)

    def test_list_bgp_speakers(self):
        speaker_ids = [
            sp.id for sp in self.operator_cloud.network.bgp_speakers()
        ]
        self.assertIn(self.SPEAKER.id, speaker_ids)

    def test_update_bgp_speaker(self):
        sot = self.operator_cloud.network.update_bgp_speaker(
            self.SPEAKER.id, advertise_floating_ip_host_routes=False
        )
        self.assertFalse(sot.advertise_floating_ip_host_routes)

    def test_find_bgp_peer(self):
        sot = self.operator_cloud.network.find_bgp_peer(self.PEER.name)
        self.assertEqual(self.PEER_IP, sot.peer_ip)
        self.assertEqual(self.REMOTE_AS, sot.remote_as)

    def test_get_bgp_peer(self):
        sot = self.operator_cloud.network.get_bgp_peer(self.PEER.id)
        self.assertEqual(self.PEER_IP, sot.peer_ip)
        self.assertEqual(self.REMOTE_AS, sot.remote_as)

    def test_list_bgp_peers(self):
        peer_ids = [pe.id for pe in self.operator_cloud.network.bgp_peers()]
        self.assertIn(self.PEER.id, peer_ids)

    def test_update_bgp_peer(self):
        name = 'new_peer_name' + self.getUniqueString()
        sot = self.operator_cloud.network.update_bgp_peer(
            self.PEER.id, name=name
        )
        self.assertEqual(name, sot.name)

    def test_add_remove_peer_to_speaker(self):
        self.operator_cloud.network.add_bgp_peer_to_speaker(
            self.SPEAKER.id, self.PEER.id
        )
        sot = self.operator_cloud.network.get_bgp_speaker(self.SPEAKER.id)
        self.assertEqual([self.PEER.id], sot.peers)

        # Remove the peer
        self.operator_cloud.network.remove_bgp_peer_from_speaker(
            self.SPEAKER.id, self.PEER.id
        )
        sot = self.operator_cloud.network.get_bgp_speaker(self.SPEAKER.id)
        self.assertEqual([], sot.peers)

    def test_add_remove_gw_network_to_speaker(self):
        net_name = 'my_network' + self.getUniqueString()
        net = self.user_cloud.create_network(name=net_name)
        self.operator_cloud.network.add_gateway_network_to_speaker(
            self.SPEAKER.id, net.id
        )
        sot = self.operator_cloud.network.get_bgp_speaker(self.SPEAKER.id)
        self.assertEqual([net.id], sot.networks)

        # Remove the network
        self.operator_cloud.network.remove_gateway_network_from_speaker(
            self.SPEAKER.id, net.id
        )
        sot = self.operator_cloud.network.get_bgp_speaker(self.SPEAKER.id)
        self.assertEqual([], sot.networks)

    def test_get_advertised_routes_of_speaker(self):
        sot = self.operator_cloud.network.get_advertised_routes_of_speaker(
            self.SPEAKER.id
        )
        self.assertEqual({'advertised_routes': []}, sot)
