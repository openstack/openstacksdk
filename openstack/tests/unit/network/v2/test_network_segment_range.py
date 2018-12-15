# Copyright (c) 2018, Intel Corporation.
# All Rights Reserved.
#
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

from openstack.tests.unit import base

from openstack.network.v2 import network_segment_range

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'name': '1',
    'default': False,
    'shared': False,
    'project_id': '2',
    'network_type': '3',
    'physical_network': '4',
    'minimum': 5,
    'maximum': 6,
    'used': {},
    'available': [],
}


class TestNetworkSegmentRange(base.TestCase):

    def test_basic(self):
        test_seg_range = network_segment_range.NetworkSegmentRange()
        self.assertEqual('network_segment_range', test_seg_range.resource_key)
        self.assertEqual('network_segment_ranges',
                         test_seg_range.resources_key)
        self.assertEqual('/network_segment_ranges', test_seg_range.base_path)

        self.assertTrue(test_seg_range.allow_create)
        self.assertTrue(test_seg_range.allow_fetch)
        self.assertTrue(test_seg_range.allow_commit)
        self.assertTrue(test_seg_range.allow_delete)
        self.assertTrue(test_seg_range.allow_list)

    def test_make_it(self):
        test_seg_range = network_segment_range.NetworkSegmentRange(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], test_seg_range.id)
        self.assertEqual(EXAMPLE['name'], test_seg_range.name)
        self.assertEqual(EXAMPLE['default'], test_seg_range.default)
        self.assertEqual(EXAMPLE['shared'], test_seg_range.shared)
        self.assertEqual(EXAMPLE['project_id'], test_seg_range.project_id)
        self.assertEqual(EXAMPLE['network_type'], test_seg_range.network_type)
        self.assertEqual(EXAMPLE['physical_network'],
                         test_seg_range.physical_network)
        self.assertEqual(EXAMPLE['minimum'], test_seg_range.minimum)
        self.assertEqual(EXAMPLE['maximum'], test_seg_range.maximum)
        self.assertEqual(EXAMPLE['used'], test_seg_range.used)
        self.assertEqual(EXAMPLE['available'], test_seg_range.available)
