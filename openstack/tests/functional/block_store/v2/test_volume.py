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

import uuid

from openstack.block_store.v2 import volume as _volume
from openstack.tests.functional import base


class TestVolume(base.BaseFunctionalTest):

    VOLUME_NAME = uuid.uuid4().hex
    VOLUME_ID = None

    @classmethod
    def setUpClass(cls):
        super(TestVolume, cls).setUpClass()
        volume = cls.conn.block_store.create_volume(
            name=cls.VOLUME_NAME,
            size=1)
        cls.conn.block_store.wait_for_status(volume,
                                             status='available',
                                             failures=['error'],
                                             interval=2,
                                             wait=120)
        assert isinstance(volume, _volume.Volume)
        cls.assertIs(cls.VOLUME_NAME, volume.name)
        cls.VOLUME_ID = volume.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.block_store.delete_volume(cls.VOLUME_ID,
                                                 ignore_missing=False)
        cls.assertIs(None, sot)

    def test_get(self):
        sot = self.conn.block_store.get_volume(self.VOLUME_ID)
        self.assertEqual(self.VOLUME_NAME, sot.name)
