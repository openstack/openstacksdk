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

from openstack.block_storage.v2 import consistency_group
from openstack.tests.unit import base

CONSISTENCY_GROUP = {
    "id": "6f2aa28a-a3e7-4eb3-acdc-38b9b9f08be5",
    "name": "my-cg",
    "description": "My consistency group",
    "status": "available",
    "availability_zone": "nova",
    "created_at": "2016-02-11T10:16:03.000000",
    "volume_types": ["2bb57de0-27e8-4af8-9804-94c4e55d4d9a"],
}


class TestConsistencyGroup(base.TestCase):
    def test_basic(self):
        sot = consistency_group.ConsistencyGroup(**CONSISTENCY_GROUP)
        self.assertEqual("consistencygroup", sot.resource_key)
        self.assertEqual("consistencygroups", sot.resources_key)
        self.assertEqual("/consistencygroups", sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
                "offset": "offset",
                "sort_dir": "sort_dir",
                "sort_key": "sort_key",
                "sort": "sort",
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = consistency_group.ConsistencyGroup(**CONSISTENCY_GROUP)
        self.assertEqual(CONSISTENCY_GROUP["id"], sot.id)
        self.assertEqual(CONSISTENCY_GROUP["name"], sot.name)
        self.assertEqual(CONSISTENCY_GROUP["description"], sot.description)
        self.assertEqual(CONSISTENCY_GROUP["status"], sot.status)
        self.assertEqual(
            CONSISTENCY_GROUP["availability_zone"], sot.availability_zone
        )
        self.assertEqual(CONSISTENCY_GROUP["created_at"], sot.created_at)
        self.assertEqual(CONSISTENCY_GROUP["volume_types"], sot.volume_types)
