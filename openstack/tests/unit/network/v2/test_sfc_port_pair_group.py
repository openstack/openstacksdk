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

from openstack.network.v2 import sfc_port_pair_group
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "description": "",
    "project_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "tenant_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "port_pairs": ["8d57819a-174d-11ee-97b0-2f370d29c014"],
    "port_pair_group_parameters": {},
    "id": "6ecd9cf3-ca64-46c7-863f-f2eb1b9e838a",
    "name": "port_pair_gr",
}


class TestSfcPortPairGroup(base.TestCase):
    def test_basic(self):
        sot = sfc_port_pair_group.SfcPortPairGroup()
        self.assertEqual('port_pair_group', sot.resource_key)
        self.assertEqual('port_pair_groups', sot.resources_key)
        self.assertEqual('/sfc/port_pair_groups', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = sfc_port_pair_group.SfcPortPairGroup(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['port_pairs'], sot.port_pairs)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(
            EXAMPLE['port_pair_group_parameters'],
            sot.port_pair_group_parameters,
        )
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
            },
            sot._query_mapping._mapping,
        )
