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


from openstack.network.v2 import network
from openstack.network.v2 import segment
from openstack.tests.functional import base


class TestSegment(base.BaseFunctionalTest):

    NETWORK_TYPE = None
    PHYSICAL_NETWORK = None
    SEGMENTATION_ID = None
    NETWORK_ID = None
    SEGMENT_ID = None
    SEGMENT_EXTENSION = None

    def setUp(self):
        super(TestSegment, self).setUp()
        self.NETWORK_NAME = self.getUniqueString()

        # NOTE(rtheis): The segment extension is not yet enabled by default.
        # Skip the tests if not enabled.
        if not self.conn.network.find_extension('segment'):
            self.skipTest('Segment extension disabled')

        # Create a network to hold the segment.
        net = self.conn.network.create_network(name=self.NETWORK_NAME)
        assert isinstance(net, network.Network)
        self.assertEqual(self.NETWORK_NAME, net.name)
        self.NETWORK_ID = net.id

        if self.SEGMENT_EXTENSION:
            # Get the segment for the network.
            for seg in self.conn.network.segments():
                assert isinstance(seg, segment.Segment)
                if self.NETWORK_ID == seg.network_id:
                    self.NETWORK_TYPE = seg.network_type
                    self.PHYSICAL_NETWORK = seg.physical_network
                    self.SEGMENTATION_ID = seg.segmentation_id
                    self.SEGMENT_ID = seg.id
                    break

    def tearDown(self):
        sot = self.conn.network.delete_network(
            self.NETWORK_ID,
            ignore_missing=False)
        self.assertIsNone(sot)
        super(TestSegment, self).tearDown()

    def test_create_delete(self):
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

    def test_find(self):
        sot = self.conn.network.find_segment(self.SEGMENT_ID)
        self.assertEqual(self.SEGMENT_ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_segment(self.SEGMENT_ID)
        self.assertEqual(self.SEGMENT_ID, sot.id)
        self.assertIsNone(sot.name)
        self.assertEqual(self.NETWORK_ID, sot.network_id)
        self.assertEqual(self.NETWORK_TYPE, sot.network_type)
        self.assertEqual(self.PHYSICAL_NETWORK, sot.physical_network)
        self.assertEqual(self.SEGMENTATION_ID, sot.segmentation_id)

    def test_list(self):
        ids = [o.id for o in self.conn.network.segments(name=None)]
        self.assertIn(self.SEGMENT_ID, ids)

    def test_update(self):
        sot = self.conn.network.update_segment(self.SEGMENT_ID,
                                               description='update')
        self.assertEqual('update', sot.description)
