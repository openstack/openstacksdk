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

from openstack.instance_ha.v1 import notification
from openstack.tests.unit import base

FAKE_ID = "569429e9-7f14-41be-a38e-920277e637db"
FAKE_UUID = "a0e70d3a-b3a2-4616-b65d-a7c03a2c85fc"
FAKE_HOST_UUID = "cad9ff01-c354-4414-ba3c-31b925be67f1"
PAYLOAD = {
    "instance_uuid": "4032bc1d-d723-47f6-b5ac-b9b3e6dbb795",
    "vir_domain_event": "STOPPED_FAILED",
    "event": "LIFECYCLE"
}
NOTIFICATION = {
    "id": FAKE_ID,
    "notification_uuid": FAKE_UUID,
    "created_at": "2018-03-22T00:00:00.000000",
    "updated_at": "2018-03-23T00:00:00.000000",
    "type": "pacemaker",
    "hostname": "fake_host",
    "status": "new",
    "generated_time": "2018-03-21T00:00:00.000000",
    "payload": PAYLOAD,
    "source_host_uuid": FAKE_HOST_UUID
}


class TestNotification(base.TestCase):

    def test_basic(self):
        sot = notification.Notification(NOTIFICATION)
        self.assertEqual("notification", sot.resource_key)
        self.assertEqual("notifications", sot.resources_key)
        self.assertEqual("/notifications", sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)

        self.assertDictEqual({"generated_since": "generated-since",
                              "limit": "limit",
                              "marker": "marker",
                              "sort_dir": "sort_dir",
                              "sort_key": "sort_key",
                              "source_host_uuid": "source_host_uuid",
                              "status": "status",
                              "type": "type"},
                             sot._query_mapping._mapping)

    def test_create(self):
        sot = notification.Notification(**NOTIFICATION)
        self.assertEqual(NOTIFICATION["id"], sot.id)
        self.assertEqual(
            NOTIFICATION["notification_uuid"], sot.notification_uuid)
        self.assertEqual(NOTIFICATION["created_at"], sot.created_at)
        self.assertEqual(NOTIFICATION["updated_at"], sot.updated_at)
        self.assertEqual(NOTIFICATION["type"], sot.type)
        self.assertEqual(NOTIFICATION["hostname"], sot.hostname)
        self.assertEqual(NOTIFICATION["status"], sot.status)
        self.assertEqual(NOTIFICATION["generated_time"], sot.generated_time)
        self.assertEqual(NOTIFICATION["payload"], sot.payload)
        self.assertEqual(
            NOTIFICATION["source_host_uuid"], sot.source_host_uuid)
