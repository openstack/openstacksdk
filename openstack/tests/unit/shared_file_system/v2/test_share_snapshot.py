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

from openstack.shared_file_system.v2 import share_snapshot
from openstack.tests.unit import base


EXAMPLE = {
    "status": "creating",
    "share_id": "406ea93b-32e9-4907-a117-148b3945749f",
    "user_id": "5c7bdb6eb0504d54a619acf8375c08ce",
    "name": "snapshot_share1",
    "created_at": "2021-06-07T11:50:39.756808",
    "description": "Here is a snapshot of share Share1",
    "share_proto": "NFS",
    "share_size": 1,
    "id": "6d221c1d-0200-461e-8d20-24b4776b9ddb",
    "project_id": "cadd7139bc3148b8973df097c0911016",
    "size": 1,
}


class TestShareSnapshot(base.TestCase):
    def test_basic(self):
        snapshot_resource = share_snapshot.ShareSnapshot()
        self.assertEqual('snapshots', snapshot_resource.resources_key)
        self.assertEqual('/snapshots', snapshot_resource.base_path)
        self.assertTrue(snapshot_resource.allow_list)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
                "snapshot_id": "snapshot_id",
            },
            snapshot_resource._query_mapping._mapping,
        )

    def test_make_share_snapshot(self):
        snapshot_resource = share_snapshot.ShareSnapshot(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], snapshot_resource.id)
        self.assertEqual(EXAMPLE['share_id'], snapshot_resource.share_id)
        self.assertEqual(EXAMPLE['user_id'], snapshot_resource.user_id)
        self.assertEqual(EXAMPLE['created_at'], snapshot_resource.created_at)
        self.assertEqual(EXAMPLE['status'], snapshot_resource.status)
        self.assertEqual(EXAMPLE['name'], snapshot_resource.name)
        self.assertEqual(EXAMPLE['description'], snapshot_resource.description)
        self.assertEqual(EXAMPLE['share_proto'], snapshot_resource.share_proto)
        self.assertEqual(EXAMPLE['share_size'], snapshot_resource.share_size)
        self.assertEqual(EXAMPLE['project_id'], snapshot_resource.project_id)
        self.assertEqual(EXAMPLE['size'], snapshot_resource.size)
