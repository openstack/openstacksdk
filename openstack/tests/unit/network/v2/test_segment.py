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

from openstack.network.v2 import segment

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'network_id': '1',
    'network_type': 'vxlan',
    'physical_network': None,
    'segmentation_id': 2,
}


class TestSegment(testtools.TestCase):

    def test_basic(self):
        sot = segment.Segment()
        self.assertEqual('segment', sot.resource_key)
        self.assertEqual('segments', sot.resources_key)
        self.assertEqual('/segments', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = segment.Segment(EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['network_id'], sot.network_id)
        self.assertEqual(EXAMPLE['network_type'], sot.network_type)
        self.assertEqual(EXAMPLE['physical_network'], sot.physical_network)
        self.assertEqual(EXAMPLE['segmentation_id'], sot.segmentation_id)
