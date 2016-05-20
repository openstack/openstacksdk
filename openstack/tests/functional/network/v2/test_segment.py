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

import unittest
import uuid

from openstack.network.v2 import network
from openstack.network.v2 import segment
from openstack.tests.functional import base


# NOTE(rtheis): Routed networks is still a WIP and not enabled by default.
@unittest.skip("bp/routed-networks")
class TestSegment(base.BaseFunctionalTest):

    NETWORK_NAME = uuid.uuid4().hex
    NETWORK_TYPE = None
    PHYSICAL_NETWORK = None
    SEGMENTATION_ID = None
    NETWORK_ID = None
    SEGMENT_ID = None

    @classmethod
    def setUpClass(cls):
        super(TestSegment, cls).setUpClass()

        # Create a network to hold the segment.
        net = cls.conn.network.create_network(name=cls.NETWORK_NAME)
        assert isinstance(net, network.Network)
        cls.assertIs(cls.NETWORK_NAME, net.name)
        cls.NETWORK_ID = net.id

        # Get the segment for the network.
        for seg in cls.conn.network.segments():
            assert isinstance(seg, segment.Segment)
            if cls.NETWORK_ID == seg.network_id:
                cls.NETWORK_TYPE = seg.network_type
                cls.PHYSICAL_NETWORK = seg.physical_network
                cls.SEGMENTATION_ID = seg.segmentation_id
                cls.SEGMENT_ID = seg.id
                break

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_network(cls.NETWORK_ID,
                                              ignore_missing=False)
        cls.assertIs(None, sot)

    def test_find(self):
        sot = self.conn.network.find_segment(self.SEGMENT_ID)
        self.assertEqual(self.SEGMENT_ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_segment(self.SEGMENT_ID)
        self.assertEqual(self.SEGMENT_ID, sot.id)
        self.assertEqual(self.NETWORK_ID, sot.network_id)
        self.assertEqual(self.NETWORK_TYPE, sot.network_type)
        self.assertEqual(self.PHYSICAL_NETWORK, sot.physical_network)
        self.assertEqual(self.SEGMENTATION_ID, sot.segmentation_id)

    def test_list(self):
        ids = [o.id for o in self.conn.network.segments()]
        self.assertIn(self.SEGMENT_ID, ids)
