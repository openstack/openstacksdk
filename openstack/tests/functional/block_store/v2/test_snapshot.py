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

from openstack.block_store.v2 import snapshot as _snapshot
from openstack.block_store.v2 import volume as _volume
from openstack.tests.functional import base


class TestSnapshot(base.BaseFunctionalTest):

    SNAPSHOT_NAME = uuid.uuid4().hex
    SNAPSHOT_ID = None
    VOLUME_NAME = uuid.uuid4().hex
    VOLUME_ID = None

    @classmethod
    def setUpClass(cls):
        super(TestSnapshot, cls).setUpClass()
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
        snapshot = cls.conn.block_store.create_snapshot(
            name=cls.SNAPSHOT_NAME,
            volume_id=cls.VOLUME_ID)
        cls.conn.block_store.wait_for_status(snapshot,
                                             status='available',
                                             failures=['error'],
                                             interval=2,
                                             wait=120)
        assert isinstance(snapshot, _snapshot.Snapshot)
        cls.assertIs(cls.SNAPSHOT_NAME, snapshot.name)
        cls.SNAPSHOT_ID = snapshot.id

    @classmethod
    def tearDownClass(cls):
        snapshot = cls.conn.block_store.get_snapshot(cls.SNAPSHOT_ID)
        sot = cls.conn.block_store.delete_snapshot(snapshot,
                                                   ignore_missing=False)
        cls.conn.block_store.wait_for_delete(snapshot,
                                             interval=2,
                                             wait=120)
        cls.assertIs(None, sot)
        sot = cls.conn.block_store.delete_volume(cls.VOLUME_ID,
                                                 ignore_missing=False)
        cls.assertIs(None, sot)

    def test_get(self):
        sot = self.conn.block_store.get_snapshot(self.SNAPSHOT_ID)
        self.assertEqual(self.SNAPSHOT_NAME, sot.name)
