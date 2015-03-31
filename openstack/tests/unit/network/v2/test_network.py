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

from openstack.network.v2 import network

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'admin_state_up': True,
    'id': IDENTIFIER,
    'name': '3',
    'tenant_id': '4',
    'provider:network_type': '5',
    'provider:physical_network': '6',
    'provider:segmentation_id': '7',
    'router:external': '8',
    'segments': '9',
    'shared': True,
    'status': '11',
    'subnets': '12',
}


class TestNetwork(testtools.TestCase):

    def test_basic(self):
        sot = network.Network()
        self.assertEqual('network', sot.resource_key)
        self.assertEqual('networks', sot.resources_key)
        self.assertEqual('/networks', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = network.Network(EXAMPLE)
        self.assertEqual(EXAMPLE['admin_state_up'], sot.admin_state_up)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['provider:network_type'],
                         sot.provider_network_type)
        self.assertEqual(EXAMPLE['provider:physical_network'],
                         sot.provider_physical_network)
        self.assertEqual(EXAMPLE['provider:segmentation_id'],
                         sot.provider_segmentation_id)
        self.assertEqual(EXAMPLE['router:external'], sot.router_external)
        self.assertEqual(EXAMPLE['segments'], sot.segments)
        self.assertEqual(EXAMPLE['shared'], sot.shared)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['subnets'], sot.subnets)
