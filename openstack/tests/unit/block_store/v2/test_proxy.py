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

import mock

from openstack.block_store.v2 import _proxy
from openstack.block_store.v2 import snapshot
from openstack.block_store.v2 import type
from openstack.block_store.v2 import volume
from openstack.tests.unit import test_proxy_base


class TestVolumeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestVolumeProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_snapshot_get(self):
        self.verify_get(self.proxy.get_snapshot, snapshot.Snapshot)

    def test_snapshot_create_attrs(self):
        self.verify_create(self.proxy.create_snapshot, snapshot.Snapshot)

    def test_snapshot_create_volume_prop(self):
        self.proxy._create = mock.Mock()

        id = "12345"
        vol = volume.Volume({"id": id})
        self.proxy.create_snapshot(volume=vol)

        kwargs = self.proxy._create.call_args[1]
        self.assertEqual({"volume": id}, kwargs)

    def test_snapshot_delete(self):
        self.verify_delete(self.proxy.delete_snapshot,
                           snapshot.Snapshot, False)

    def test_snapshot_delete_ignore(self):
        self.verify_delete(self.proxy.delete_snapshot,
                           snapshot.Snapshot, True)

    def test_type_get(self):
        self.verify_get(self.proxy.get_type, type.Type)

    def test_type_create_attrs(self):
        self.verify_create(self.proxy.create_type, type.Type)

    def test_type_delete(self):
        self.verify_delete(self.proxy.delete_type, type.Type, False)

    def test_type_delete_ignore(self):
        self.verify_delete(self.proxy.delete_type, type.Type, True)

    def test_volume_get(self):
        self.verify_get(self.proxy.get_volume, volume.Volume)

    def test_volume_create_attrs(self):
        self.verify_create(self.proxy.create_volume, volume.Volume)

    def test_volume_create_snapshot_prop(self):
        self.proxy._create = mock.Mock()

        id1 = "12345"
        id2 = "67890"
        snap = snapshot.Snapshot({"id": id1})
        source = volume.Volume({"id": id2})
        self.proxy.create_volume(snapshot=snap, source_volume=source)

        kwargs = self.proxy._create.call_args[1]
        self.assertEqual({"snapshot": id1, "source_volume": id2}, kwargs)

    def test_volume_delete(self):
        self.verify_delete(self.proxy.delete_volume, volume.Volume, False)

    def test_volume_delete_ignore(self):
        self.verify_delete(self.proxy.delete_volume, volume.Volume, True)
