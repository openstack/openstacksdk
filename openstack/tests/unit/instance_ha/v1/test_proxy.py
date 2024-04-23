# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from openstack.instance_ha.v1 import _proxy
from openstack.instance_ha.v1 import host
from openstack.instance_ha.v1 import notification
from openstack.instance_ha.v1 import segment
from openstack.instance_ha.v1 import vmove
from openstack.tests.unit import test_proxy_base

SEGMENT_ID = "c50b96eb-2a66-40f8-bca8-c5fa90d595c0"
HOST_ID = "52d05e43-d08e-42b8-ae33-e47c8ea2ad47"
NOTIFICATION_ID = "a0e70d3a-b3a2-4616-b65d-a7c03a2c85fc"
VMOVE_ID = "16a7c91f-8342-49a7-c731-3a632293f845"


class TestInstanceHaProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestInstanceHaHosts(TestInstanceHaProxy):
    def test_hosts(self):
        self.verify_list(
            self.proxy.hosts,
            host.Host,
            method_args=[SEGMENT_ID],
            expected_args=[],
            expected_kwargs={"segment_id": SEGMENT_ID},
        )

    def test_host_get(self):
        self.verify_get(
            self.proxy.get_host,
            host.Host,
            method_args=[HOST_ID],
            method_kwargs={"segment_id": SEGMENT_ID},
            expected_kwargs={"segment_id": SEGMENT_ID},
        )

    def test_host_create(self):
        self.verify_create(
            self.proxy.create_host,
            host.Host,
            method_args=[SEGMENT_ID],
            method_kwargs={},
            expected_args=[],
            expected_kwargs={"segment_id": SEGMENT_ID},
        )

    def test_host_update(self):
        self.verify_update(
            self.proxy.update_host,
            host.Host,
            method_kwargs={"segment_id": SEGMENT_ID},
        )

    def test_host_delete(self):
        self.verify_delete(
            self.proxy.delete_host,
            host.Host,
            True,
            method_kwargs={"segment_id": SEGMENT_ID},
            expected_kwargs={"segment_id": SEGMENT_ID},
        )


class TestInstanceHaNotifications(TestInstanceHaProxy):
    def test_notifications(self):
        self.verify_list(self.proxy.notifications, notification.Notification)

    def test_notification_get(self):
        self.verify_get(self.proxy.get_notification, notification.Notification)

    def test_notification_create(self):
        self.verify_create(
            self.proxy.create_notification, notification.Notification
        )


class TestInstanceHaSegments(TestInstanceHaProxy):
    def test_segments(self):
        self.verify_list(self.proxy.segments, segment.Segment)

    def test_segment_get(self):
        self.verify_get(self.proxy.get_segment, segment.Segment)

    def test_segment_create(self):
        self.verify_create(self.proxy.create_segment, segment.Segment)

    def test_segment_update(self):
        self.verify_update(self.proxy.update_segment, segment.Segment)

    def test_segment_delete(self):
        self.verify_delete(self.proxy.delete_segment, segment.Segment, True)


class TestInstanceHaVMoves(TestInstanceHaProxy):
    def test_vmoves(self):
        self.verify_list(
            self.proxy.vmoves,
            vmove.VMove,
            method_args=[NOTIFICATION_ID],
            expected_args=[],
            expected_kwargs={"notification_id": NOTIFICATION_ID},
        )

    def test_vmove_get(self):
        self.verify_get(
            self.proxy.get_vmove,
            vmove.VMove,
            method_args=[VMOVE_ID, NOTIFICATION_ID],
            expected_args=[VMOVE_ID],
            expected_kwargs={"notification_id": NOTIFICATION_ID},
        )
