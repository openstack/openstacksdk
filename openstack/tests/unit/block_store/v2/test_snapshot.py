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

import testtools

from openstack.block_store.v2 import snapshot

FAKE_ID = "ffa9bc5e-1172-4021-acaf-cdcd78a9584d"

SNAPSHOT = {
    "status": "creating",
    "description": "Daily backup",
    "created_at": "2015-03-09T12:14:57.233772",
    "metadata": {},
    "volume_id": "5aa119a8-d25b-45a7-8d1b-88e127885635",
    "size": 1,
    "id": FAKE_ID,
    "name": "snap-001",
    "force": "true",
}

DETAILS = {
    "os-extended-snapshot-attributes:progress": "100%",
    "os-extended-snapshot-attributes:project_id":
        "0c2eba2c5af04d3f9e9d0d410b371fde"
}

DETAILED_SNAPSHOT = SNAPSHOT.copy()
DETAILED_SNAPSHOT.update(**DETAILS)


class TestSnapshot(testtools.TestCase):

    def test_basic(self):
        sot = snapshot.Snapshot(SNAPSHOT)
        self.assertEqual("snapshot", sot.resource_key)
        self.assertEqual("snapshots", sot.resources_key)
        self.assertEqual("/snapshots", sot.base_path)
        self.assertEqual("volume", sot.service.service_type)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({"name": "name",
                              "status": "status",
                              "all_tenants": "all_tenants",
                              "volume_id": "volume_id",
                              "limit": "limit",
                              "marker": "marker"},
                             sot._query_mapping._mapping)

    def test_create_basic(self):
        sot = snapshot.Snapshot(**SNAPSHOT)
        self.assertEqual(SNAPSHOT["id"], sot.id)
        self.assertEqual(SNAPSHOT["status"], sot.status)
        self.assertEqual(SNAPSHOT["created_at"], sot.created_at)
        self.assertEqual(SNAPSHOT["metadata"], sot.metadata)
        self.assertEqual(SNAPSHOT["volume_id"], sot.volume_id)
        self.assertEqual(SNAPSHOT["size"], sot.size)
        self.assertEqual(SNAPSHOT["name"], sot.name)
        self.assertTrue(sot.is_forced)


class TestSnapshotDetail(testtools.TestCase):

    def test_basic(self):
        sot = snapshot.SnapshotDetail(DETAILED_SNAPSHOT)
        self.assertIsInstance(sot, snapshot.Snapshot)
        self.assertEqual("/snapshots/detail", sot.base_path)

    def test_create_detailed(self):
        sot = snapshot.SnapshotDetail(**DETAILED_SNAPSHOT)

        self.assertEqual(
            DETAILED_SNAPSHOT["os-extended-snapshot-attributes:progress"],
            sot.progress)
        self.assertEqual(
            DETAILED_SNAPSHOT["os-extended-snapshot-attributes:project_id"],
            sot.project_id)
