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

from openstack.instance_ha.v1 import segment
from openstack.tests.unit import base

FAKE_ID = "1c2f1795-ce78-4d4c-afd0-ce141fdb3952"
FAKE_UUID = "11f7597f-87d2-4057-b754-ba611f989807"
SEGMENT = {
    "id": FAKE_ID,
    "uuid": FAKE_UUID,
    "created_at": "2018-03-22T00:00:00.000000",
    "updated_at": "2018-03-23T00:00:00.000000",
    "name": "my_segment",
    "description": "something",
    "recovery_method": "auto",
    "service_type": "COMPUTE_HOST"
}


class TestSegment(base.TestCase):

    def test_basic(self):
        sot = segment.Segment(SEGMENT)
        self.assertEqual("segment", sot.resource_key)
        self.assertEqual("segments", sot.resources_key)
        self.assertEqual("/segments", sot.base_path)
        self.assertEqual("ha", sot.service.service_type)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)

        self.assertDictEqual({"limit": "limit",
                              "marker": "marker",
                              "recovery_method": "recovery_method",
                              "service_type": "service_type",
                              "sort_dir": "sort_dir",
                              "sort_key": "sort_key"},
                             sot._query_mapping._mapping)

    def test_create(self):
        sot = segment.Segment(**SEGMENT)
        self.assertEqual(SEGMENT["id"], sot.id)
        self.assertEqual(SEGMENT["uuid"], sot.uuid)
        self.assertEqual(SEGMENT["created_at"], sot.created_at)
        self.assertEqual(SEGMENT["updated_at"], sot.updated_at)
        self.assertEqual(SEGMENT["name"], sot.name)
        self.assertEqual(SEGMENT["description"], sot.description)
        self.assertEqual(SEGMENT["recovery_method"], sot.recovery_method)
        self.assertEqual(SEGMENT["service_type"], sot.service_type)
