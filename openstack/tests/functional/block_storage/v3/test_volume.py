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


class TestVolume(base.BaseBlockStorageTest):
    def setUp(self):
        super().setUp()

        if not self.user_cloud.has_service('block-storage'):
            self.skipTest('block-storage service not supported by cloud')

        volume_name = self.getUniqueString()

        self.volume = self.block_storage_client.create_volume(
            name=volume_name,
            size=1,
        )
        self.block_storage_client.wait_for_status(
            self.volume,
            status='available',
            failures=['error'],
            interval=2,
            wait=self._wait_for_timeout,
        )
        self.assertIsInstance(self.volume, _volume.Volume)
        self.assertEqual(volume_name, self.volume.name)

    def tearDown(self):
        self.block_storage_client.delete_volume(self.volume)
        super().tearDown()

    def test_volume(self):
        # get
        volume = self.block_storage_client.get_volume(self.volume.id)
        self.assertEqual(self.volume.name, volume.name)

        # find
        volume = self.block_storage_client.find_volume(self.volume.name)
        self.assertEqual(self.volume.id, volume.id)

        # list
        volumes = self.block_storage_client.volumes()
        # other tests may have created volumes so we don't assert that this is
        # the *only* volume present
        self.assertIn(self.volume.id, {v.id for v in volumes})

        # update
        volume_name = self.getUniqueString()
        volume_description = self.getUniqueString()
        volume = self.block_storage_client.update_volume(
            self.volume,
            name=volume_name,
            description=volume_description,
        )
        self.assertIsInstance(volume, _volume.Volume)
        volume = self.block_storage_client.get_volume(self.volume.id)
        self.assertEqual(volume_name, volume.name)
        self.assertEqual(volume_description, volume.description)
