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

from openstack.network.v2 import vpn_ipsec_site_connection
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "admin_state_up": True,
    "auth_mode": "1",
    "ikepolicy_id": "2",
    "vpnservice_id": "3",
    "local_ep_group_id": "4",
    "peer_address": "5",
    "route_mode": "6",
    "ipsecpolicy_id": "7",
    "peer_id": "8",
    "psk": "9",
    "description": "10",
    "initiator": "11",
    "peer_cidrs": ['1', '2'],
    "name": "12",
    "tenant_id": "13",
    "interval": 5,
    "mtu": 5,
    "peer_ep_group_id": "14",
    "dpd": {'a': 5},
    "timeout": 16,
    "action": "17",
    "local_id": "18",
}


class TestVpnIPSecSiteConnection(base.TestCase):
    def test_basic(self):
        sot = vpn_ipsec_site_connection.VpnIPSecSiteConnection()
        self.assertEqual('ipsec_site_connection', sot.resource_key)
        self.assertEqual('ipsec_site_connections', sot.resources_key)
        self.assertEqual('/vpn/ipsec-site-connections', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = vpn_ipsec_site_connection.VpnIPSecSiteConnection(**EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['auth_mode'], sot.auth_mode)
        self.assertEqual(EXAMPLE['ikepolicy_id'], sot.ikepolicy_id)
        self.assertEqual(EXAMPLE['vpnservice_id'], sot.vpnservice_id)
        self.assertEqual(EXAMPLE['local_ep_group_id'], sot.local_ep_group_id)
        self.assertEqual(EXAMPLE['peer_address'], sot.peer_address)
        self.assertEqual(EXAMPLE['route_mode'], sot.route_mode)
        self.assertEqual(EXAMPLE['ipsecpolicy_id'], sot.ipsecpolicy_id)
        self.assertEqual(EXAMPLE['peer_id'], sot.peer_id)
        self.assertEqual(EXAMPLE['psk'], sot.psk)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['initiator'], sot.initiator)
        self.assertEqual(EXAMPLE['peer_cidrs'], sot.peer_cidrs)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['interval'], sot.interval)
        self.assertEqual(EXAMPLE['mtu'], sot.mtu)
        self.assertEqual(EXAMPLE['peer_ep_group_id'], sot.peer_ep_group_id)
        self.assertEqual(EXAMPLE['dpd'], sot.dpd)
        self.assertEqual(EXAMPLE['timeout'], sot.timeout)
        self.assertEqual(EXAMPLE['action'], sot.action)
        self.assertEqual(EXAMPLE['local_id'], sot.local_id)
