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


from openstack.block_storage.v2 import volume as _volume
from openstack.tests.functional import base


class TestVolume(base.BaseFunctionalTest):

    def setUp(self):
        super(TestVolume, self).setUp()

        self.VOLUME_NAME = self.getUniqueString()
        self.VOLUME_ID = None

        volume = self.conn.block_storage.create_volume(
            name=self.VOLUME_NAME,
            size=1)
        self.conn.block_storage.wait_for_status(
            volume,
            status='available',
            failures=['error'],
            interval=2,
            wait=120)
        assert isinstance(volume, _volume.Volume)
        self.assertEqual(self.VOLUME_NAME, volume.name)
        self.VOLUME_ID = volume.id

    def tearDown(self):
        sot = self.conn.block_storage.delete_volume(
            self.VOLUME_ID,
            ignore_missing=False)
        self.assertIsNone(sot)
        super(TestVolume, self).tearDown()

    def test_get(self):
        sot = self.conn.block_storage.get_volume(self.VOLUME_ID)
        self.assertEqual(self.VOLUME_NAME, sot.name)
