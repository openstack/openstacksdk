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

from openstack.network.v2 import vpn_endpoint_group
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "description": "",
    "project_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "tenant_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "endpoints": ["10.2.0.0/24", "10.3.0.0/24"],
    "type": "cidr",
    "id": "6ecd9cf3-ca64-46c7-863f-f2eb1b9e838a",
    "name": "peers",
}


class TestVpnEndpointGroup(base.TestCase):
    def test_basic(self):
        sot = vpn_endpoint_group.VpnEndpointGroup()
        self.assertEqual('endpoint_group', sot.resource_key)
        self.assertEqual('endpoint_groups', sot.resources_key)
        self.assertEqual('/vpn/endpoint-groups', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = vpn_endpoint_group.VpnEndpointGroup(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['endpoints'], sot.endpoints)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
                'description': 'description',
                'name': 'name',
                'project_id': 'project_id',
                'tenant_id': 'tenant_id',
                'type': 'endpoint_type',
            },
            sot._query_mapping._mapping,
        )
