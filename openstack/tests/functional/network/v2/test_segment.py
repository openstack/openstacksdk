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

import uuid

from openstack.network.v2 import network
from openstack.network.v2 import segment
from openstack.tests.functional import base


class TestSegment(base.BaseFunctionalTest):

    NETWORK_NAME = uuid.uuid4().hex
    NETWORK_TYPE = None
    PHYSICAL_NETWORK = None
    SEGMENTATION_ID = None
    NETWORK_ID = None
    SEGMENT_ID = None
    SEGMENT_EXTENSION = None

    @classmethod
    def setUpClass(cls):
        super(TestSegment, cls).setUpClass()

        # NOTE(rtheis): The segment extension is not yet enabled by default.
        # Skip the tests if not enabled.
        cls.SEGMENT_EXTENSION = cls.conn.network.find_extension('segment')

        # Create a network to hold the segment.
        net = cls.conn.network.create_network(name=cls.NETWORK_NAME)
        assert isinstance(net, network.Network)
        cls.assertIs(cls.NETWORK_NAME, net.name)
        cls.NETWORK_ID = net.id

        if cls.SEGMENT_EXTENSION:
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

    def test_create_delete(self):
        if self.SEGMENT_EXTENSION:
            sot = self.conn.network.create_segment(
                description='test description',
                name='test name',
                network_id=self.NETWORK_ID,
                network_type='geneve',
                segmentation_id=2055,
            )
            self.assertIsInstance(sot, segment.Segment)
            del_sot = self.conn.network.delete_segment(sot.id)
            self.assertEqual('test description', sot.description)
            self.assertEqual('test name', sot.name)
            self.assertEqual(self.NETWORK_ID, sot.network_id)
            self.assertEqual('geneve', sot.network_type)
            self.assertIsNone(sot.physical_network)
            self.assertEqual(2055, sot.segmentation_id)
            self.assertIsNone(del_sot)
        else:
            self.skipTest('Segment extension disabled')

    def test_find(self):
        if self.SEGMENT_EXTENSION:
            sot = self.conn.network.find_segment(self.SEGMENT_ID)
            self.assertEqual(self.SEGMENT_ID, sot.id)
        else:
            self.skipTest('Segment extension disabled')

    def test_get(self):
        if self.SEGMENT_EXTENSION:
            sot = self.conn.network.get_segment(self.SEGMENT_ID)
            self.assertEqual(self.SEGMENT_ID, sot.id)
            self.assertIsNone(sot.name)
            self.assertEqual(self.NETWORK_ID, sot.network_id)
            self.assertEqual(self.NETWORK_TYPE, sot.network_type)
            self.assertEqual(self.PHYSICAL_NETWORK, sot.physical_network)
            self.assertEqual(self.SEGMENTATION_ID, sot.segmentation_id)
        else:
            self.skipTest('Segment extension disabled')

    def test_list(self):
        if self.SEGMENT_EXTENSION:
            ids = [o.id for o in self.conn.network.segments(name=None)]
            self.assertIn(self.SEGMENT_ID, ids)
        else:
            self.skipTest('Segment extension disabled')

    def test_update(self):
        if self.SEGMENT_EXTENSION:
            sot = self.conn.network.update_segment(self.SEGMENT_ID,
                                                   description='update')
            self.assertEqual('update', sot.description)
        else:
            self.skipTest('Segment extension disabled')
