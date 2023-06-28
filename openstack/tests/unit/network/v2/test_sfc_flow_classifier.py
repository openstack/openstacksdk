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

from openstack.network.v2 import sfc_flow_classifier
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "description": "",
    "project_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "tenant_id": "4ad57e7ce0b24fca8f12b9834d91079d",
    "ethertype": "IPv4",
    "protocol": 6,
    "source_port_range_min": 22,
    "source_port_range_max": 2000,
    "destination_port_range_min": 80,
    "destination_port_range_max": 80,
    "source_ip_prefix": None,
    "destination_ip_prefix": "22.12.34.45",
    "logical_source_port": "uuid1",
    "logical_destination_port": "uuid2",
    "l7_parameters": None,
    "id": "6ecd9cf3-ca64-46c7-863f-f2eb1b9e838a",
    "name": "flow_classifier",
}


class TestFlowClassifier(base.TestCase):
    def test_basic(self):
        sot = sfc_flow_classifier.SfcFlowClassifier()
        self.assertEqual('flow_classifier', sot.resource_key)
        self.assertEqual('flow_classifiers', sot.resources_key)
        self.assertEqual('/sfc/flow_classifiers', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = sfc_flow_classifier.SfcFlowClassifier(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['protocol'], sot.protocol)
        self.assertEqual(EXAMPLE['ethertype'], sot.ethertype)
        self.assertEqual(
            EXAMPLE['source_port_range_min'], sot.source_port_range_min
        )
        self.assertEqual(
            EXAMPLE['source_port_range_max'], sot.source_port_range_max
        )
        self.assertEqual(
            EXAMPLE['destination_port_range_min'],
            sot.destination_port_range_min,
        )
        self.assertEqual(
            EXAMPLE['destination_port_range_max'],
            sot.destination_port_range_max,
        )
        self.assertEqual(EXAMPLE['source_ip_prefix'], sot.source_ip_prefix)
        self.assertEqual(
            EXAMPLE['destination_ip_prefix'], sot.destination_ip_prefix
        )
        self.assertEqual(
            EXAMPLE['logical_source_port'], sot.logical_source_port
        )
        self.assertEqual(
            EXAMPLE['logical_destination_port'], sot.logical_destination_port
        )
        self.assertEqual(EXAMPLE['l7_parameters'], sot.l7_parameters)
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
                'ethertype': 'ethertype',
                'protocol': 'protocol',
                'source_port_range_min': 'source_port_range_min',
                'source_port_range_max': 'source_port_range_max',
                'destination_port_range_min': 'destination_port_range_min',
                'destination_port_range_max': 'destination_port_range_max',
                'logical_source_port': 'logical_source_port',
                'logical_destination_port': 'logical_destination_port',
            },
            sot._query_mapping._mapping,
        )
