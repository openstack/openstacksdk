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

from openstack.shared_file_system.v2 import share
from openstack.tests.unit import base

IDENTIFIER = '08a87d37-5ca2-4308-86c5-cba06d8d796c'
EXAMPLE = {
    "id": IDENTIFIER,
    "size": 1,
    "availability_zone": "manila-zone-1",
    "created_at": "2021-02-11T17:38:00.000000",
    "status": "available",
    "name": None,
    "description": None,
    "project_id": "d19444eb73af4b37bc0794532ef6fc50",
    "snapshot_id": None,
    "share_network_id": None,
    "share_protocol": "NFS",
    "metadata": {},
    "share_type": "cbb18bb7-cc97-477a-b64b-ed7c7f2a1c67",
    "volume_type": "default",
    "is_public": False,
    "is_snapshot_supported": True,
    "task_state": None,
    "share_type_name": "default",
    "access_rules_status": "active",
    "replication_type": None,
    "is_replicated": False,
    "user_id": "6c262cab98de42c2afc4cfccbefc50c7",
    "is_creating_new_share_from_snapshot_supported": True,
    "is_reverting_to_snapshot_supported": True,
    "share_group_id": None,
    "source_share_group_snapshot_member_id": None,
    "is_mounting_snapshot_supported": True,
    "progress": "100%",
    "share_server_id": None,
    "host": "new@denver#lvm-single-pool"
}


class TestShares(base.TestCase):

    def test_basic(self):
        shares_resource = share.Share()
        self.assertEqual('shares', shares_resource.resources_key)
        self.assertEqual('/shares', shares_resource.base_path)
        self.assertTrue(shares_resource.allow_list)
        self.assertTrue(shares_resource.allow_create)
        self.assertTrue(shares_resource.allow_fetch)
        self.assertTrue(shares_resource.allow_commit)
        self.assertTrue(shares_resource.allow_delete)

    def test_make_shares(self):
        shares_resource = share.Share(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], shares_resource.id)
        self.assertEqual(EXAMPLE['size'], shares_resource.size)
        self.assertEqual(EXAMPLE['availability_zone'],
                         shares_resource.availability_zone)
        self.assertEqual(EXAMPLE['created_at'], shares_resource.created_at)
        self.assertEqual(EXAMPLE['status'], shares_resource.status)
        self.assertEqual(EXAMPLE['name'], shares_resource.name)
        self.assertEqual(EXAMPLE['description'],
                         shares_resource.description)
        self.assertEqual(EXAMPLE['project_id'], shares_resource.project_id)
        self.assertEqual(EXAMPLE['snapshot_id'], shares_resource.snapshot_id)
        self.assertEqual(EXAMPLE['share_network_id'],
                         shares_resource.share_network_id)
        self.assertEqual(EXAMPLE['share_protocol'],
                         shares_resource.share_protocol)
        self.assertEqual(EXAMPLE['metadata'], shares_resource.metadata)
        self.assertEqual(EXAMPLE['share_type'], shares_resource.share_type)
        self.assertEqual(EXAMPLE['is_public'], shares_resource.is_public)
        self.assertEqual(EXAMPLE['is_snapshot_supported'],
                         shares_resource.is_snapshot_supported)
        self.assertEqual(EXAMPLE['task_state'], shares_resource.task_state)
        self.assertEqual(EXAMPLE['share_type_name'],
                         shares_resource.share_type_name)
        self.assertEqual(EXAMPLE['access_rules_status'],
                         shares_resource.access_rules_status)
        self.assertEqual(EXAMPLE['replication_type'],
                         shares_resource.replication_type)
        self.assertEqual(EXAMPLE['is_replicated'],
                         shares_resource.is_replicated)
        self.assertEqual(EXAMPLE['user_id'], shares_resource.user_id)
        self.assertEqual(EXAMPLE[
            'is_creating_new_share_from_snapshot_supported'],
            (shares_resource.is_creating_new_share_from_snapshot_supported))
        self.assertEqual(EXAMPLE['is_reverting_to_snapshot_supported'],
                         shares_resource.is_reverting_to_snapshot_supported)
        self.assertEqual(EXAMPLE['share_group_id'],
                         shares_resource.share_group_id)
        self.assertEqual(EXAMPLE[
            'source_share_group_snapshot_member_id'],
            shares_resource.source_share_group_snapshot_member_id)
        self.assertEqual(EXAMPLE['is_mounting_snapshot_supported'],
                         shares_resource.is_mounting_snapshot_supported)
        self.assertEqual(EXAMPLE['progress'],
                         shares_resource.progress)
        self.assertEqual(EXAMPLE['share_server_id'],
                         shares_resource.share_server_id)
        self.assertEqual(EXAMPLE['host'], shares_resource.host)
