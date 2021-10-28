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

from openstack.shared_file_system.v2 import share_replica
from openstack.tests.unit import base

EXAMPLE = {
    "share_id": "9faf6f83-24c2-4551-9945-ca35f30a6ff7",
    "status": "available",
    "cast_rules_to_readonly": False,
    "updated_at": "2021-10-27T23:34:31.066083",
    "share_network_id": None,
    "share_server_id": None,
    "host": "some_random_host",
    "id": "6f406701-eb8c-400d-9ef0-1cda205a917d",
    "replica_state": "active",
    "created_at": "2021-10-27T23:34:26.350382",
}


class TestShareReplica(base.TestCase):
    def setUp(self):
        return super().setUp()

    def test_basic(self):
        sr = share_replica.ShareReplica()
        self.assertEqual('share_replica', sr.resource_key)
        self.assertEqual('share_replicas', sr.resources_key)
        self.assertEqual('share-replicas', sr.base_path)
        self.assertTrue(sr.allow_create)
        self.assertTrue(sr.allow_fetch)
        self.assertFalse(sr.allow_commit)
        self.assertTrue(sr.allow_delete)
        self.assertTrue(sr.allow_list)
        self.assertFalse(sr.allow_head)

    def test_share_replica(self):
        sr = share_replica.ShareReplica(**EXAMPLE)
        self.assertEqual(EXAMPLE['share_id'], sr.share_id)
        self.assertEqual(EXAMPLE['status'], sr.status)
        self.assertEqual(
            EXAMPLE['cast_rules_to_readonly'], sr.cast_rules_to_readonly
        )
        self.assertEqual(EXAMPLE['updated_at'], sr.updated_at)
        self.assertEqual(EXAMPLE['share_network_id'], sr.share_network_id)
        self.assertEqual(EXAMPLE['share_server_id'], sr.share_server_id)
        self.assertEqual(EXAMPLE['host'], sr.host)
        self.assertEqual(EXAMPLE['id'], sr.id)
        self.assertEqual(EXAMPLE['replica_state'], sr.replica_state)
        self.assertEqual(EXAMPLE['created_at'], sr.created_at)
