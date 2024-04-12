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

from openstack.block_storage.v3 import consistency_group_snapshot
from openstack.tests.unit import base

CONSISTENCY_GROUP_SNAPSHOT = {
    "id": "6f2aa28a-a3e7-4eb3-acdc-38b9b9f08be5",
    "name": "my-cg-snap",
    "description": "My consistency group snapshot",
    "consistencygroup_id": "b5b2e3e9-66a8-4f3d-b3eb-9f14a7f0c1d5",
    "status": "available",
    "created_at": "2016-02-11T10:16:03.000000",
}


class TestConsistencyGroupSnapshot(base.TestCase):
    def test_basic(self):
        sot = consistency_group_snapshot.ConsistencyGroupSnapshot(
            **CONSISTENCY_GROUP_SNAPSHOT
        )
        self.assertEqual("cgsnapshot", sot.resource_key)
        self.assertEqual("cgsnapshots", sot.resources_key)
        self.assertEqual("/cgsnapshots", sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_commit)

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
        sot = consistency_group_snapshot.ConsistencyGroupSnapshot(
            **CONSISTENCY_GROUP_SNAPSHOT
        )
        self.assertEqual(CONSISTENCY_GROUP_SNAPSHOT["id"], sot.id)
        self.assertEqual(CONSISTENCY_GROUP_SNAPSHOT["name"], sot.name)
        self.assertEqual(
            CONSISTENCY_GROUP_SNAPSHOT["description"], sot.description
        )
        self.assertEqual(
            CONSISTENCY_GROUP_SNAPSHOT["consistencygroup_id"],
            sot.consistencygroup_id,
        )
        self.assertEqual(CONSISTENCY_GROUP_SNAPSHOT["status"], sot.status)
        self.assertEqual(
            CONSISTENCY_GROUP_SNAPSHOT["created_at"], sot.created_at
        )
