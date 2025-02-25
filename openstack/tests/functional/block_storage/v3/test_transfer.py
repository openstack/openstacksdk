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

from openstack.tests.functional.block_storage.v3 import base
from openstack import utils


class TestTransfer(base.BaseBlockStorageTest):
    def setUp(self):
        super().setUp()

        self.VOLUME_NAME = self.getUniqueString()

        self.volume = self.user_cloud.block_storage.create_volume(
            name=self.VOLUME_NAME,
            size=1,
        )
        self.user_cloud.block_storage.wait_for_status(
            self.volume,
            status='available',
            failures=['error'],
            interval=2,
            wait=self._wait_for_timeout,
        )
        self.VOLUME_ID = self.volume.id

    def tearDown(self):
        sot = self.user_cloud.block_storage.delete_volume(
            self.VOLUME_ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_transfer(self):
        if not utils.supports_microversion(
            self.operator_cloud.block_storage, "3.55"
        ):
            self.skipTest("Cannot test new transfer API if MV < 3.55")
        sot = self.operator_cloud.block_storage.create_transfer(
            volume_id=self.VOLUME_ID,
            name=self.VOLUME_NAME,
        )
        self.assertIn('auth_key', sot)
        self.assertIn('created_at', sot)
        self.assertIn('id', sot)
        self.assertIn('name', sot)
        self.assertIn('volume_id', sot)

        sot = self.user_cloud.block_storage.delete_transfer(
            sot.id, ignore_missing=False
        )
