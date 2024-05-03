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

from openstack.network.v2 import network_segment_range
from openstack.tests.functional import base


class TestNetworkSegmentRange(base.BaseFunctionalTest):
    NETWORK_SEGMENT_RANGE_ID = None
    NAME = "test_name"
    DEFAULT = False
    SHARED = False
    PROJECT_ID = "2018"
    NETWORK_TYPE = "vlan"
    PHYSICAL_NETWORK = "phys_net"
    MINIMUM = 100
    MAXIMUM = 200

    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud required for this test")

        # NOTE(kailun): The network segment range extension is not yet enabled
        # by default.
        # Skip the tests if not enabled.
        if not self.operator_cloud.network.find_extension(
            "network-segment-range"
        ):
            self.skipTest("Network Segment Range extension disabled")

        test_seg_range = (
            self.operator_cloud.network.create_network_segment_range(
                name=self.NAME,
                default=self.DEFAULT,
                shared=self.SHARED,
                project_id=self.PROJECT_ID,
                network_type=self.NETWORK_TYPE,
                physical_network=self.PHYSICAL_NETWORK,
                minimum=self.MINIMUM,
                maximum=self.MAXIMUM,
            )
        )
        self.assertIsInstance(
            test_seg_range, network_segment_range.NetworkSegmentRange
        )
        self.NETWORK_SEGMENT_RANGE_ID = test_seg_range.id
        self.assertEqual(self.NAME, test_seg_range.name)
        self.assertEqual(self.DEFAULT, test_seg_range.default)
        self.assertEqual(self.SHARED, test_seg_range.shared)
        self.assertEqual(self.PROJECT_ID, test_seg_range.project_id)
        self.assertEqual(self.NETWORK_TYPE, test_seg_range.network_type)
        self.assertEqual(
            self.PHYSICAL_NETWORK, test_seg_range.physical_network
        )
        self.assertEqual(self.MINIMUM, test_seg_range.minimum)
        self.assertEqual(self.MAXIMUM, test_seg_range.maximum)

    def tearDown(self):
        super().tearDown()

    def test_create_delete(self):
        del_test_seg_range = (
            self.operator_cloud.network.delete_network_segment_range(
                self.NETWORK_SEGMENT_RANGE_ID
            )
        )
        self.assertIsNone(del_test_seg_range)

    def test_find(self):
        test_seg_range = (
            self.operator_cloud.network.find_network_segment_range(
                self.NETWORK_SEGMENT_RANGE_ID
            )
        )
        self.assertEqual(self.NETWORK_SEGMENT_RANGE_ID, test_seg_range.id)

    def test_get(self):
        test_seg_range = self.operator_cloud.network.get_network_segment_range(
            self.NETWORK_SEGMENT_RANGE_ID
        )
        self.assertEqual(self.NETWORK_SEGMENT_RANGE_ID, test_seg_range.id)
        self.assertEqual(self.NAME, test_seg_range.name)
        self.assertEqual(self.DEFAULT, test_seg_range.default)
        self.assertEqual(self.SHARED, test_seg_range.shared)
        self.assertEqual(self.PROJECT_ID, test_seg_range.project_id)
        self.assertEqual(self.NETWORK_TYPE, test_seg_range.network_type)
        self.assertEqual(
            self.PHYSICAL_NETWORK, test_seg_range.physical_network
        )
        self.assertEqual(self.MINIMUM, test_seg_range.minimum)
        self.assertEqual(self.MAXIMUM, test_seg_range.maximum)

    def test_list(self):
        ids = [
            o.id
            for o in self.operator_cloud.network.network_segment_ranges(
                name=None
            )
        ]
        self.assertIn(self.NETWORK_SEGMENT_RANGE_ID, ids)

    def test_update(self):
        update_seg_range = self.operator_cloud.network.update_segment(
            self.NETWORK_SEGMENT_RANGE_ID, name="update_test_name"
        )
        self.assertEqual("update_test_name", update_seg_range.name)
