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

from openstack.network.v2 import vpn_service
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "admin_state_up": True,
    "description": "1",
    "external_v4_ip": "2",
    "external_v6_ip": "3",
    "id": IDENTIFIER,
    "name": "4",
    "router_id": "5",
    "status": "6",
    "subnet_id": "7",
    "project_id": "8",
}


class TestVpnService(base.TestCase):
    def test_basic(self):
        sot = vpn_service.VpnService()
        self.assertEqual('vpnservice', sot.resource_key)
        self.assertEqual('vpnservices', sot.resources_key)
        self.assertEqual('/vpn/vpnservices', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = vpn_service.VpnService(**EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['external_v4_ip'], sot.external_v4_ip)
        self.assertEqual(EXAMPLE['external_v6_ip'], sot.external_v6_ip)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['router_id'], sot.router_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['subnet_id'], sot.subnet_id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
                'description': 'description',
                'external_v4_ip': 'external_v4_ip',
                'external_v6_ip': 'external_v6_ip',
                'name': 'name',
                'router_id': 'router_id',
                'project_id': 'project_id',
                'tenant_id': 'tenant_id',
                'subnet_id': 'subnet_id',
                'is_admin_state_up': 'admin_state_up',
            },
            sot._query_mapping._mapping,
        )
