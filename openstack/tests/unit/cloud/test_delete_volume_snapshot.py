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

from openstack.cloud import exc
from openstack.cloud import meta
from openstack.tests import fakes
from openstack.tests.unit import base


class TestDeleteVolumeSnapshot(base.TestCase):

    def test_delete_volume_snapshot(self):
        """
        Test that delete_volume_snapshot without a wait returns True instance
        when the volume snapshot deletes.
        """
        fake_snapshot = fakes.FakeVolumeSnapshot('1234', 'available',
                                                 'foo', 'derpysnapshot')
        fake_snapshot_dict = meta.obj_to_munch(fake_snapshot)

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['snapshots', 'detail']),
                 json={'snapshots': [fake_snapshot_dict]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['snapshots', fake_snapshot_dict['id']]))])

        self.assertTrue(
            self.cloud.delete_volume_snapshot(name_or_id='1234', wait=False))
        self.assert_calls()

    def test_delete_volume_snapshot_with_error(self):
        """
        Test that a exception while deleting a volume snapshot will cause an
        OpenStackCloudException.
        """
        fake_snapshot = fakes.FakeVolumeSnapshot('1234', 'available',
                                                 'foo', 'derpysnapshot')
        fake_snapshot_dict = meta.obj_to_munch(fake_snapshot)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['snapshots', 'detail']),
                 json={'snapshots': [fake_snapshot_dict]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['snapshots', fake_snapshot_dict['id']]),
                 status_code=404)])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.delete_volume_snapshot, name_or_id='1234')
        self.assert_calls()

    def test_delete_volume_snapshot_with_timeout(self):
        """
        Test that a timeout while waiting for the volume snapshot to delete
        raises an exception in delete_volume_snapshot.
        """
        fake_snapshot = fakes.FakeVolumeSnapshot('1234', 'available',
                                                 'foo', 'derpysnapshot')
        fake_snapshot_dict = meta.obj_to_munch(fake_snapshot)

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['snapshots', 'detail']),
                 json={'snapshots': [fake_snapshot_dict]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['snapshots', fake_snapshot_dict['id']]))])

        self.assertRaises(
            exc.OpenStackCloudTimeout,
            self.cloud.delete_volume_snapshot, name_or_id='1234',
            wait=True, timeout=0.01)
        self.assert_calls(do_count=False)
