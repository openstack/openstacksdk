# Copyright(c) 2022 Inspur
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

from openstack.instance_ha.v1 import vmove
from openstack.tests.unit import base

FAKE_ID = "1"
FAKE_UUID = "16a7c91f-8342-49a7-c731-3a632293f845"
FAKE_NOTIFICATION_ID = "a0e70d3a-b3a2-4616-b65d-a7c03a2c85fc"
FAKE_SERVER_ID = "1c2f1795-ce78-4d4c-afd0-ce141fdb3952"

VMOVE = {
    'id': FAKE_ID,
    'uuid': FAKE_UUID,
    'notification_id': FAKE_NOTIFICATION_ID,
    'created_at': "2023-01-28T14:55:26.000000",
    'updated_at': "2023-01-28T14:55:31.000000",
    'server_id': FAKE_SERVER_ID,
    'server_name': 'vm1',
    'source_host': 'host1',
    'dest_host': 'host2',
    'start_time': "2023-01-28T14:55:27.000000",
    'end_time': "2023-01-28T14:55:31.000000",
    'status': 'succeeded',
    'type': 'evacuation',
    'message': None,
}


class TestVMove(base.TestCase):
    def test_basic(self):
        sot = vmove.VMove(VMOVE)
        self.assertEqual("vmove", sot.resource_key)
        self.assertEqual("vmoves", sot.resources_key)
        self.assertEqual(
            "/notifications/%(notification_id)s/vmoves", sot.base_path
        )
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_fetch)

        self.assertDictEqual(
            {
                "status": "status",
                "type": "type",
                "limit": "limit",
                "marker": "marker",
                "sort_dir": "sort_dir",
                "sort_key": "sort_key",
            },
            sot._query_mapping._mapping,
        )

    def test_create(self):
        sot = vmove.VMove(**VMOVE)
        self.assertEqual(VMOVE["id"], sot.id)
        self.assertEqual(VMOVE["uuid"], sot.uuid)
        self.assertEqual(VMOVE["notification_id"], sot.notification_id)
        self.assertEqual(VMOVE["created_at"], sot.created_at)
        self.assertEqual(VMOVE["updated_at"], sot.updated_at)
        self.assertEqual(VMOVE["server_id"], sot.server_id)
        self.assertEqual(VMOVE["server_name"], sot.server_name)
        self.assertEqual(VMOVE["source_host"], sot.source_host)
        self.assertEqual(VMOVE["dest_host"], sot.dest_host)
        self.assertEqual(VMOVE["start_time"], sot.start_time)
        self.assertEqual(VMOVE["end_time"], sot.end_time)
        self.assertEqual(VMOVE["status"], sot.status)
        self.assertEqual(VMOVE["type"], sot.type)
        self.assertEqual(VMOVE["message"], sot.message)
