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

from openstack.network.v2 import sfc_service_graph
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "description": "",
    "project_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "tenant_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "port_chains": {
        "0e6b9678-19aa-11ee-97ae-a3cec2c2ac72": [
            "1e19c266-19aa-11ee-8e02-6fa0c9a9832d"
        ],
        "2a394dc8-19aa-11ee-b87e-7f24d71926f1": [
            "3299fcf6-19aa-11ee-9398-3f8c68c11209"
        ],
    },
    "id": "6ecd9cf3-ca64-46c7-863f-f2eb1b9e838a",
    "name": "service_graph",
}


class TestSfcServiceGraph(base.TestCase):
    def test_basic(self):
        sot = sfc_service_graph.SfcServiceGraph()
        self.assertEqual('service_graph', sot.resource_key)
        self.assertEqual('service_graphs', sot.resources_key)
        self.assertEqual('/sfc/service_graphs', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = sfc_service_graph.SfcServiceGraph(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['port_chains'], sot.port_chains)
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
            },
            sot._query_mapping._mapping,
        )
