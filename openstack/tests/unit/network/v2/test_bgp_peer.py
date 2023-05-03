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

from openstack.network.v2 import bgp_peer
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'auth_type': 'none',
    'remote_as': '1001',
    'name': 'bgp-peer',
    'peer_ip': '10.0.0.3',
    'id': IDENTIFIER,
    'project_id': '42',
}


class TestBgpPeer(base.TestCase):
    def test_basic(self):
        sot = bgp_peer.BgpPeer()
        self.assertEqual('bgp_peer', sot.resource_key)
        self.assertEqual('bgp_peers', sot.resources_key)
        self.assertEqual('/bgp-peers', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = bgp_peer.BgpPeer(**EXAMPLE)
        self.assertEqual(EXAMPLE['auth_type'], sot.auth_type)
        self.assertEqual(EXAMPLE['remote_as'], sot.remote_as)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['peer_ip'], sot.peer_ip)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )
