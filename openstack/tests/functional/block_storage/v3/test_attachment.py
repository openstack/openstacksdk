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
from openstack.tests.functional.block_storage.v3 import base


class TestAttachment(base.BaseBlockStorageTest):
    """Test class for volume attachment operations.

    We have implemented a test that performs attachment create
    and attachment delete operations. Attachment create requires
    the instance ID and the volume ID for which we have created a
    volume resource and an instance resource.
    We haven't implemented attachment update test since it requires
    the host connector information which is not readily available to
    us and hard to retrieve. Without passing this information, the
    attachment update operation will fail.
    Similarly, we haven't implement attachment complete test since it
    depends on attachment update and can only be performed when the volume
    status is 'attaching' which is done by attachment update operation.
    """

    def setUp(self):
        super().setUp()

        # Create Volume
        self.volume_name = self.getUniqueString()

        volume = self.user_cloud.block_storage.create_volume(
            name=self.volume_name, size=1
        )
        self.user_cloud.block_storage.wait_for_status(
            volume,
            status='available',
            failures=['error'],
            interval=2,
            wait=self._wait_for_timeout,
        )
        self.assertIsInstance(volume, _volume.Volume)
        self.VOLUME_ID = volume.id

        # Create Server
        self.server_name = self.getUniqueString()
        self.server = self.operator_cloud.compute.create_server(
            name=self.server_name,
            flavor_id=self.flavor.id,
            image_id=self.image.id,
            networks='none',
        )
        self.operator_cloud.compute.wait_for_server(
            self.server, wait=self._wait_for_timeout
        )

    def tearDown(self):
        # Since delete_on_termination flag is set to True, we
        # don't need to cleanup the volume manually
        result = self.operator_cloud.compute.delete_server(self.server.id)
        self.operator_cloud.compute.wait_for_delete(
            self.server, wait=self._wait_for_timeout
        )
        self.assertIsNone(result)
        super().tearDown()

    def test_attachment(self):
        attachment = self.operator_cloud.block_storage.create_attachment(
            self.VOLUME_ID,
            connector={},
            instance_id=self.server.id,
        )
        self.assertIn('id', attachment)
        self.assertIn('status', attachment)
        self.assertIn('instance', attachment)
        self.assertIn('volume_id', attachment)
        self.assertIn('attached_at', attachment)
        self.assertIn('detached_at', attachment)
        self.assertIn('attach_mode', attachment)
        self.assertIn('connection_info', attachment)
        attachment = self.user_cloud.block_storage.delete_attachment(
            attachment.id, ignore_missing=False
        )
