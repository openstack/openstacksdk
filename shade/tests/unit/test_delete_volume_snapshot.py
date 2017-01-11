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
test_delete_volume_snapshot
----------------------------------

Tests for the `delete_volume_snapshot` command.
"""

from mock import patch
from shade import OpenStackCloud
from shade.tests import fakes
from shade.tests.unit import base
from shade.exc import (OpenStackCloudException, OpenStackCloudTimeout)


class TestDeleteVolumeSnapshot(base.TestCase):

    @patch.object(OpenStackCloud, 'cinder_client')
    def test_delete_volume_snapshot(self, mock_cinder):
        """
        Test that delete_volume_snapshot without a wait returns True instance
        when the volume snapshot deletes.
        """
        fake_snapshot = fakes.FakeVolumeSnapshot('1234', 'available',
                                                 'foo', 'derpysnapshot')

        mock_cinder.volume_snapshots.list.return_value = [fake_snapshot]

        self.assertEqual(
            True,
            self.cloud.delete_volume_snapshot(name_or_id='1234', wait=False)
        )

        mock_cinder.volume_snapshots.list.assert_called_with(detailed=True,
                                                             search_opts=None)

    @patch.object(OpenStackCloud, 'cinder_client')
    def test_delete_volume_snapshot_with_error(self, mock_cinder):
        """
        Test that a exception while deleting a volume snapshot will cause an
        OpenStackCloudException.
        """
        fake_snapshot = fakes.FakeVolumeSnapshot('1234', 'available',
                                                 'foo', 'derpysnapshot')

        mock_cinder.volume_snapshots.delete.side_effect = Exception(
            "exception")
        mock_cinder.volume_snapshots.list.return_value = [fake_snapshot]

        self.assertRaises(
            OpenStackCloudException,
            self.cloud.delete_volume_snapshot, name_or_id='1234')

        mock_cinder.volume_snapshots.delete.assert_called_with(
            snapshot='1234')

    @patch.object(OpenStackCloud, 'cinder_client')
    def test_delete_volume_snapshot_with_timeout(self, mock_cinder):
        """
        Test that a timeout while waiting for the volume snapshot to delete
        raises an exception in delete_volume_snapshot.
        """
        fake_snapshot = fakes.FakeVolumeSnapshot('1234', 'available',
                                                 'foo', 'derpysnapshot')

        mock_cinder.volume_snapshots.list.return_value = [fake_snapshot]

        self.assertRaises(
            OpenStackCloudTimeout,
            self.cloud.delete_volume_snapshot, name_or_id='1234',
            wait=True, timeout=0.01)

        mock_cinder.volume_snapshots.list.assert_called_with(detailed=True,
                                                             search_opts=None)
