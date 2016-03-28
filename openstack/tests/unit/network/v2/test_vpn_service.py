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

import testtools

from openstack.network.v2 import vpn_service

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "router_id": "1",
    "status": "PENDING_CREATE",
    "name": "2",
    "admin_state_up": True,
    "subnet_id": "3",
    "tenant_id": "4",
    "id": IDENTIFIER,
    "description": "5"
}


class TestVPNService(testtools.TestCase):

    def test_basic(self):
        sot = vpn_service.VPNService()
        self.assertEqual('vpnservice', sot.resource_key)
        self.assertEqual('vpnservices', sot.resources_key)
        self.assertEqual('/vpn/vpnservices', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = vpn_service.VPNService(EXAMPLE)
        self.assertTrue(sot.is_admin_state_up)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['router_id'], sot.router_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['subnet_id'], sot.subnet_id)
