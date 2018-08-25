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

from openstack.instance_ha.v1 import host
from openstack.tests.unit import base

FAKE_ID = "1c2f1795-ce78-4d4c-afd0-ce141fdb3952"
FAKE_UUID = "11f7597f-87d2-4057-b754-ba611f989807"
FAKE_HOST_ID = "c27dec16-ed4d-4ebe-8e77-f1e28ec32417"
FAKE_CONTROL_ATTRIBUTES = {
    "mcastaddr": "239.255.1.1",
    "mcastport": "5405"
}
HOST = {
    "id": FAKE_ID,
    "uuid": FAKE_UUID,
    "segment_id": FAKE_HOST_ID,
    "created_at": "2018-03-22T00:00:00.000000",
    "updated_at": "2018-03-23T00:00:00.000000",
    "name": "my_host",
    "type": "pacemaker",
    "control_attributes": FAKE_CONTROL_ATTRIBUTES,
    "on_maintenance": False,
    "reserved": False,
    "failover_segment_id": FAKE_HOST_ID
}


class TestHost(base.TestCase):

    def test_basic(self):
        sot = host.Host(HOST)
        self.assertEqual("host", sot.resource_key)
        self.assertEqual("hosts", sot.resources_key)
        self.assertEqual("/segments/%(segment_id)s/hosts", sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)

        self.assertDictEqual({"failover_segment_id": "failover_segment_id",
                              "limit": "limit",
                              "marker": "marker",
                              "on_maintenance": "on_maintenance",
                              "reserved": "reserved",
                              "sort_dir": "sort_dir",
                              "sort_key": "sort_key",
                              "type": "type"},
                             sot._query_mapping._mapping)

    def test_create(self):
        sot = host.Host(**HOST)
        self.assertEqual(HOST["id"], sot.id)
        self.assertEqual(HOST["uuid"], sot.uuid)
        self.assertEqual(HOST["segment_id"], sot.segment_id)
        self.assertEqual(HOST["created_at"], sot.created_at)
        self.assertEqual(HOST["updated_at"], sot.updated_at)
        self.assertEqual(HOST["name"], sot.name)
        self.assertEqual(HOST["type"], sot.type)
        self.assertEqual(HOST["control_attributes"], sot.control_attributes)
        self.assertEqual(HOST["on_maintenance"], sot.on_maintenance)
        self.assertEqual(HOST["reserved"], sot.reserved)
        self.assertEqual(HOST["failover_segment_id"], sot.failover_segment_id)
