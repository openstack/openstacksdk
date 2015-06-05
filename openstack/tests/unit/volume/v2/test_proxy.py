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

from openstack.tests.unit import test_proxy_base
from openstack.volume.v2 import _proxy
from openstack.volume.v2 import snapshot
from openstack.volume.v2 import type
from openstack.volume.v2 import volume


class TestVolumeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestVolumeProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_snapshot_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_snapshot,
                         method_args=["resource_or_id"],
                         expected_args=[snapshot.Snapshot, "resource_or_id"])

    def test_snapshot_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_snapshot,
                            method_kwargs=kwargs,
                            expected_args=[snapshot.Snapshot],
                            expected_kwargs=kwargs)

    def test_snapshot_delete(self):
        self.verify_delete(self.proxy.delete_snapshot,
                           snapshot.Snapshot, False)

    def test_snapshot_delete_ignore(self):
        self.verify_delete(self.proxy.delete_snapshot,
                           snapshot.Snapshot, True)

    def test_type_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_type,
                         method_args=["resource_or_id"],
                         expected_args=[type.Type, "resource_or_id"])

    def test_type_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_type,
                            method_kwargs=kwargs,
                            expected_args=[type.Type],
                            expected_kwargs=kwargs)

    def test_type_delete(self):
        self.verify_delete(self.proxy.delete_type, type.Type, False)

    def test_type_delete_ignore(self):
        self.verify_delete(self.proxy.delete_type, type.Type, True)

    def test_volume_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_volume,
                         method_args=["resource_or_id"],
                         expected_args=[volume.Volume, "resource_or_id"])

    def test_volume_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_volume,
                            method_kwargs=kwargs,
                            expected_args=[volume.Volume],
                            expected_kwargs=kwargs)

    def test_volume_delete(self):
        self.verify_delete(self.proxy.delete_volume, volume.Volume, False)

    def test_volume_delete_ignore(self):
        self.verify_delete(self.proxy.delete_volume, volume.Volume, True)
