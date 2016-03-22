# -*- coding: utf-8 -*-

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

"""
test_volume
----------------------------------

Functional tests for `shade` block storage methods.
"""

from testtools import content

from shade.tests.functional import base


class TestVolume(base.BaseFunctionalTestCase):

    def setUp(self):
        super(TestVolume, self).setUp()
        if not self.demo_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')

    def test_volumes(self):
        '''Test volume and snapshot functionality'''
        volume_name = self.getUniqueString()
        snapshot_name = self.getUniqueString()
        self.addDetail('volume', content.text_content(volume_name))
        self.addCleanup(self.cleanup, volume_name, snapshot_name)
        volume = self.demo_cloud.create_volume(
            display_name=volume_name, size=1)
        snapshot = self.demo_cloud.create_volume_snapshot(
            volume['id'],
            display_name=snapshot_name
        )

        volume_ids = [v['id'] for v in self.demo_cloud.list_volumes()]
        self.assertIn(volume['id'], volume_ids)

        snapshot_list = self.demo_cloud.list_volume_snapshots()
        snapshot_ids = [s['id'] for s in snapshot_list]
        self.assertIn(snapshot['id'], snapshot_ids)

        ret_snapshot = self.demo_cloud.get_volume_snapshot_by_id(
            snapshot['id'])
        self.assertEqual(snapshot['id'], ret_snapshot['id'])

        self.demo_cloud.delete_volume_snapshot(snapshot_name, wait=True)
        self.demo_cloud.delete_volume(volume_name, wait=True)

    def cleanup(self, volume_name, snapshot_name):
        volume = self.demo_cloud.get_volume(volume_name)
        snapshot = self.demo_cloud.get_volume_snapshot(snapshot_name)
        # Need to delete snapshots before volumes
        if snapshot:
            self.demo_cloud.delete_volume_snapshot(snapshot_name)
        if volume:
            self.demo_cloud.delete_volume(volume_name)
