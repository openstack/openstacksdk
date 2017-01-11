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
test_create_volume_snapshot
----------------------------------

Tests for the `create_volume_snapshot` command.
"""

from mock import patch
from shade import meta
from shade import OpenStackCloud
from shade.tests import fakes
from shade.tests.unit import base
from shade.exc import (OpenStackCloudException, OpenStackCloudTimeout)


class TestCreateVolumeSnapshot(base.TestCase):

    @patch.object(OpenStackCloud, 'cinder_client')
    def test_create_volume_snapshot_wait(self, mock_cinder):
        """
        Test that create_volume_snapshot with a wait returns the volume
        snapshot when its status changes to "available".
        """
        build_snapshot = fakes.FakeVolumeSnapshot('1234', 'creating',
                                                  'foo', 'derpysnapshot')
        fake_snapshot = fakes.FakeVolumeSnapshot('1234', 'available',
                                                 'foo', 'derpysnapshot')

        mock_cinder.volume_snapshots.create.return_value = build_snapshot
        mock_cinder.volume_snapshots.get.return_value = fake_snapshot
        mock_cinder.volume_snapshots.list.return_value = [
            build_snapshot, fake_snapshot]

        self.assertEqual(
            self.cloud._normalize_volume(
                meta.obj_to_dict(fake_snapshot)),
            self.cloud.create_volume_snapshot(volume_id='1234', wait=True)
        )

        mock_cinder.volume_snapshots.create.assert_called_with(
            force=False, volume_id='1234'
        )
        mock_cinder.volume_snapshots.get.assert_called_with(
            snapshot_id=meta.obj_to_dict(build_snapshot)['id']
        )

    @patch.object(OpenStackCloud, 'cinder_client')
    def test_create_volume_snapshot_with_timeout(self, mock_cinder):
        """
        Test that a timeout while waiting for the volume snapshot to create
        raises an exception in create_volume_snapshot.
        """
        build_snapshot = fakes.FakeVolumeSnapshot('1234', 'creating',
                                                  'foo', 'derpysnapshot')

        mock_cinder.volume_snapshots.create.return_value = build_snapshot
        mock_cinder.volume_snapshots.get.return_value = build_snapshot
        mock_cinder.volume_snapshots.list.return_value = [build_snapshot]

        self.assertRaises(
            OpenStackCloudTimeout,
            self.cloud.create_volume_snapshot, volume_id='1234',
            wait=True, timeout=0.01)

        mock_cinder.volume_snapshots.create.assert_called_with(
            force=False, volume_id='1234'
        )
        mock_cinder.volume_snapshots.get.assert_called_with(
            snapshot_id=meta.obj_to_dict(build_snapshot)['id']
        )

    @patch.object(OpenStackCloud, 'cinder_client')
    def test_create_volume_snapshot_with_error(self, mock_cinder):
        """
        Test that a error status while waiting for the volume snapshot to
        create raises an exception in create_volume_snapshot.
        """
        build_snapshot = fakes.FakeVolumeSnapshot('1234', 'creating',
                                                  'bar', 'derpysnapshot')
        error_snapshot = fakes.FakeVolumeSnapshot('1234', 'error',
                                                  'blah', 'derpysnapshot')

        mock_cinder.volume_snapshots.create.return_value = build_snapshot
        mock_cinder.volume_snapshots.get.return_value = error_snapshot
        mock_cinder.volume_snapshots.list.return_value = [error_snapshot]

        self.assertRaises(
            OpenStackCloudException,
            self.cloud.create_volume_snapshot, volume_id='1234',
            wait=True, timeout=5)

        mock_cinder.volume_snapshots.create.assert_called_with(
            force=False, volume_id='1234'
        )
        mock_cinder.volume_snapshots.get.assert_called_with(
            snapshot_id=meta.obj_to_dict(build_snapshot)['id']
        )
