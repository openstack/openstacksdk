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

from openstack.network.v2 import bgpvpn
from openstack.network.v2 import bgpvpn_network_association
from openstack.network.v2 import bgpvpn_port_association
from openstack.network.v2 import bgpvpn_router_association
from openstack.network.v2 import network
from openstack.network.v2 import port
from openstack.network.v2 import router
from openstack.tests.unit import base

IDENTIFIER = 'IDENTIFIER'
NET_ID = 'NET_ID'
PORT_ID = 'PORT_ID'
ROUTER_ID = 'ROUTER_ID'
EXAMPLE = {
    'id': IDENTIFIER,
    'name': 'bgpvpn',
    'project_id': '42',
    'route_distinguishers': ['64512:1777', '64512:1888', '64512:1999'],
    'route_targets': '64512:1444',
    'import_targets': '64512:1555',
    'export_targets': '64512:1666',
}


class TestBgpVpn(base.TestCase):
    def test_basic(self):
        sot = bgpvpn.BgpVpn()
        self.assertEqual('bgpvpn', sot.resource_key)
        self.assertEqual('bgpvpns', sot.resources_key)
        self.assertEqual('/bgpvpn/bgpvpns', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = bgpvpn.BgpVpn(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(
            EXAMPLE['route_distinguishers'], sot.route_distinguishers
        )
        self.assertEqual(EXAMPLE['route_targets'], sot.route_targets)
        self.assertEqual(EXAMPLE['import_targets'], sot.import_targets)
        self.assertEqual(EXAMPLE['export_targets'], sot.export_targets)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'local_pref': 'local_pref',
                'name': 'name',
                'networks': 'networks',
                'routers': 'routers',
                'ports': 'ports',
                'project_id': 'project_id',
                'type': 'type',
                'vni': 'vni',
            },
            sot._query_mapping._mapping,
        )

    def test_create_bgpvpn_network_association(self):
        test_bpgvpn = bgpvpn.BgpVpn(**EXAMPLE)
        test_net = network.Network(**{'name': 'foo_net', 'id': NET_ID})
        sot = bgpvpn_network_association.BgpVpnNetworkAssociation(
            bgpvn_id=test_bpgvpn.id, network_id=test_net.id
        )
        self.assertEqual(test_net.id, sot.network_id)
        self.assertEqual(test_bpgvpn.id, sot.bgpvn_id)

    def test_create_bgpvpn_port_association(self):
        test_bpgvpn = bgpvpn.BgpVpn(**EXAMPLE)
        test_port = port.Port(
            **{'name': 'foo_port', 'id': PORT_ID, 'network_id': NET_ID}
        )
        sot = bgpvpn_port_association.BgpVpnPortAssociation(
            bgpvn_id=test_bpgvpn.id, port_id=test_port.id
        )
        self.assertEqual(test_port.id, sot.port_id)
        self.assertEqual(test_bpgvpn.id, sot.bgpvn_id)

    def test_create_bgpvpn_router_association(self):
        test_bpgvpn = bgpvpn.BgpVpn(**EXAMPLE)
        test_router = router.Router(**{'name': 'foo_port'})
        sot = bgpvpn_router_association.BgpVpnRouterAssociation(
            bgpvn_id=test_bpgvpn.id, router_id=test_router.id
        )
        self.assertEqual(test_router.id, sot.router_id)
        self.assertEqual(test_bpgvpn.id, sot.bgpvn_id)
