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

from openstack.cloud import exc
from openstack.cloud import meta
from openstack.tests import fakes
from openstack.tests.unit import base


class TestCreateVolumeSnapshot(base.TestCase):

    def setUp(self):
        super(TestCreateVolumeSnapshot, self).setUp()
        self.use_cinder()

    def test_create_volume_snapshot_wait(self):
        """
        Test that create_volume_snapshot with a wait returns the volume
        snapshot when its status changes to "available".
        """
        snapshot_id = '5678'
        volume_id = '1234'
        build_snapshot = fakes.FakeVolumeSnapshot(snapshot_id, 'creating',
                                                  'foo', 'derpysnapshot')
        build_snapshot_dict = meta.obj_to_munch(build_snapshot)
        fake_snapshot = fakes.FakeVolumeSnapshot(snapshot_id, 'available',
                                                 'foo', 'derpysnapshot')
        fake_snapshot_dict = meta.obj_to_munch(fake_snapshot)

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['snapshots']),
                 json={'snapshot': build_snapshot_dict},
                 validate=dict(json={
                     'snapshot': {'force': False, 'volume_id': '1234'}})),
            dict(method='GET',
                 uri=self.get_mock_url('volumev2', 'public',
                                       append=['snapshots', snapshot_id]),
                 json={'snapshot': build_snapshot_dict}),
            dict(method='GET',
                 uri=self.get_mock_url('volumev2', 'public',
                                       append=['snapshots', snapshot_id]),
                 json={'snapshot': fake_snapshot_dict})])

        self.assertEqual(
            self.cloud._normalize_volume(fake_snapshot_dict),
            self.cloud.create_volume_snapshot(volume_id=volume_id, wait=True)
        )
        self.assert_calls()

    def test_create_volume_snapshot_with_timeout(self):
        """
        Test that a timeout while waiting for the volume snapshot to create
        raises an exception in create_volume_snapshot.
        """
        snapshot_id = '5678'
        volume_id = '1234'
        build_snapshot = fakes.FakeVolumeSnapshot(snapshot_id, 'creating',
                                                  'foo', 'derpysnapshot')
        build_snapshot_dict = meta.obj_to_munch(build_snapshot)

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['snapshots']),
                 json={'snapshot': build_snapshot_dict},
                 validate=dict(json={
                     'snapshot': {'force': False, 'volume_id': '1234'}})),
            dict(method='GET',
                 uri=self.get_mock_url('volumev2', 'public',
                                       append=['snapshots', snapshot_id]),
                 json={'snapshot': build_snapshot_dict})])

        self.assertRaises(
            exc.OpenStackCloudTimeout,
            self.cloud.create_volume_snapshot, volume_id=volume_id,
            wait=True, timeout=0.01)
        self.assert_calls(do_count=False)

    def test_create_volume_snapshot_with_error(self):
        """
        Test that a error status while waiting for the volume snapshot to
        create raises an exception in create_volume_snapshot.
        """
        snapshot_id = '5678'
        volume_id = '1234'
        build_snapshot = fakes.FakeVolumeSnapshot(snapshot_id, 'creating',
                                                  'bar', 'derpysnapshot')
        build_snapshot_dict = meta.obj_to_munch(build_snapshot)
        error_snapshot = fakes.FakeVolumeSnapshot(snapshot_id, 'error',
                                                  'blah', 'derpysnapshot')
        error_snapshot_dict = meta.obj_to_munch(error_snapshot)

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['snapshots']),
                 json={'snapshot': build_snapshot_dict},
                 validate=dict(json={
                     'snapshot': {'force': False, 'volume_id': '1234'}})),
            dict(method='GET',
                 uri=self.get_mock_url('volumev2', 'public',
                                       append=['snapshots', snapshot_id]),
                 json={'snapshot': build_snapshot_dict}),
            dict(method='GET',
                 uri=self.get_mock_url('volumev2', 'public',
                                       append=['snapshots', snapshot_id]),
                 json={'snapshot': error_snapshot_dict})])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_volume_snapshot, volume_id=volume_id,
            wait=True, timeout=5)
        self.assert_calls()
