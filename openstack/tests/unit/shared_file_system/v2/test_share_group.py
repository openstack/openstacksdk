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

from openstack.shared_file_system.v2 import share_group
from openstack.tests.unit import base


EXAMPLE = {
    "status": "creating",
    "description": None,
    "links": "[]",
    "availability_zone": None,
    "source_share_group_snapshot_id": None,
    "share_network_id": None,
    "share_server_id": None,
    "host": None,
    "share_group_type_id": "89861c2a-10bf-4013-bdd4-3d020466aee4",
    "consistent_snapshot_support": None,
    "id": "f9c1f80c-2392-4e34-bd90-fc89cdc5bf93",
    "name": None,
    "created_at": "2021-06-03T19:20:33.974421",
    "project_id": "e23850eeb91d4fa3866af634223e454c",
    "share_types": ["ecd11f4c-d811-4471-b656-c755c77e02ba"],
}


class TestShareGroups(base.TestCase):
    def test_basic(self):
        share_groups = share_group.ShareGroup()
        self.assertEqual('share_groups', share_groups.resources_key)
        self.assertEqual('/share-groups', share_groups.base_path)
        self.assertTrue(share_groups.allow_list)
        self.assertTrue(share_groups.allow_fetch)
        self.assertTrue(share_groups.allow_create)
        self.assertTrue(share_groups.allow_commit)
        self.assertTrue(share_groups.allow_delete)
        self.assertFalse(share_groups.allow_head)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
                "share_group_id": "share_group_id",
            },
            share_groups._query_mapping._mapping,
        )

    def test_make_share_groups(self):
        share_group_res = share_group.ShareGroup(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], share_group_res.id)
        self.assertEqual(EXAMPLE['status'], share_group_res.status)
        self.assertEqual(
            EXAMPLE['availability_zone'], share_group_res.availability_zone
        )
        self.assertEqual(EXAMPLE['description'], share_group_res.description)
        self.assertEqual(
            EXAMPLE['source_share_group_snapshot_id'],
            share_group_res.share_group_snapshot_id,
        )
        self.assertEqual(
            EXAMPLE['share_network_id'], share_group_res.share_network_id
        )
        self.assertEqual(
            EXAMPLE['share_group_type_id'], share_group_res.share_group_type_id
        )
        self.assertEqual(
            EXAMPLE['consistent_snapshot_support'],
            share_group_res.consistent_snapshot_support,
        )
        self.assertEqual(EXAMPLE['created_at'], share_group_res.created_at)
        self.assertEqual(EXAMPLE['project_id'], share_group_res.project_id)
        self.assertEqual(EXAMPLE['share_types'], share_group_res.share_types)
