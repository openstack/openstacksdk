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

from openstack.block_storage.v3 import volume as _volume
from openstack.compute.v2 import server as _server
from openstack.compute.v2 import volume_attachment as _volume_attachment
from openstack.tests.functional.compute import base


class TestServerVolumeAttachment(base.BaseComputeTest):
    def setUp(self):
        super().setUp()

        if not self.user_cloud.has_service('block-storage'):
            self.skipTest('block-storage service not supported by cloud')

        self.server_name = self.getUniqueString()
        self.volume_name = self.getUniqueString()

        # create the server and volume

        server = self.user_cloud.compute.create_server(
            name=self.server_name,
            flavor_id=self.flavor.id,
            image_id=self.image.id,
            networks='none',
        )
        self.user_cloud.compute.wait_for_server(
            server, wait=self._wait_for_timeout
        )
        self.addCleanup(self._delete_server, server)
        self.assertIsInstance(server, _server.Server)
        self.assertEqual(self.server_name, server.name)

        volume = self.user_cloud.block_storage.create_volume(
            name=self.volume_name, size=1
        )
        self.user_cloud.block_storage.wait_for_status(
            volume, status='available', wait=self._wait_for_timeout
        )
        self.addCleanup(self._delete_volume, volume)
        self.assertIsInstance(volume, _volume.Volume)
        self.assertEqual(self.volume_name, volume.name)

        self.server = server
        self.volume = volume

    def _delete_server(self, server):
        self.user_cloud.compute.delete_server(server.id)
        self.user_cloud.compute.wait_for_delete(
            server, wait=self._wait_for_timeout
        )

    def _delete_volume(self, volume):
        self.user_cloud.block_storage.delete_volume(volume.id)
        self.user_cloud.block_storage.wait_for_delete(
            volume, wait=self._wait_for_timeout
        )

    def test_volume_attachment(self):
        # create the volume attachment

        volume_attachment = self.user_cloud.compute.create_volume_attachment(
            self.server, self.volume
        )
        self.assertIsInstance(
            volume_attachment, _volume_attachment.VolumeAttachment
        )
        self.user_cloud.block_storage.wait_for_status(
            self.volume, status='in-use', wait=self._wait_for_timeout
        )

        # list all attached volume attachments (there should only be one)

        volume_attachments = list(
            self.user_cloud.compute.volume_attachments(self.server)
        )
        self.assertEqual(1, len(volume_attachments))
        self.assertIsInstance(
            volume_attachments[0], _volume_attachment.VolumeAttachment
        )

        # update the volume attachment

        volume_attachment = self.user_cloud.compute.update_volume_attachment(
            self.server, self.volume, delete_on_termination=True
        )
        self.assertIsInstance(
            volume_attachment, _volume_attachment.VolumeAttachment
        )

        # retrieve details of the (updated) volume attachment

        volume_attachment = self.user_cloud.compute.get_volume_attachment(
            self.server, self.volume
        )
        self.assertIsInstance(
            volume_attachment, _volume_attachment.VolumeAttachment
        )
        self.assertTrue(volume_attachment.delete_on_termination)

        # delete the volume attachment

        result = self.user_cloud.compute.delete_volume_attachment(
            self.server, self.volume, ignore_missing=False
        )
        self.assertIsNone(result)

        self.user_cloud.block_storage.wait_for_status(
            self.volume, status='available', wait=self._wait_for_timeout
        )

        # Wait for the attachment to be deleted.
        # This is done to prevent a race between the BDM
        # record being deleted and we trying to delete the server.
        self.user_cloud.compute.wait_for_delete(
            volume_attachment, wait=self._wait_for_timeout
        )

        # Verify the server doesn't have any volume attachment
        volume_attachments = list(
            self.user_cloud.compute.volume_attachments(self.server)
        )
        self.assertEqual(0, len(volume_attachments))
