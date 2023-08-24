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

from openstack.network.v2 import sfc_port_chain
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "description": "",
    "project_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "tenant_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "port_pair_groups": ["p_group1", "p_group2"],
    "flow_classifiers": ["f_classifier1", "f_classifier_2"],
    "chain_parameters": {"correlation": "mpls", "symmetric": True},
    "id": "6ecd9cf3-ca64-46c7-863f-f2eb1b9e838a",
    "name": "peers",
}


class TestPortChain(base.TestCase):
    def test_basic(self):
        sot = sfc_port_chain.SfcPortChain()
        self.assertEqual('port_chain', sot.resource_key)
        self.assertEqual('port_chains', sot.resources_key)
        self.assertEqual('/sfc/port_chains', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = sfc_port_chain.SfcPortChain(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['port_pair_groups'], sot.port_pair_groups)
        self.assertEqual(EXAMPLE['flow_classifiers'], sot.flow_classifiers)
        self.assertEqual(EXAMPLE['chain_parameters'], sot.chain_parameters)
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
