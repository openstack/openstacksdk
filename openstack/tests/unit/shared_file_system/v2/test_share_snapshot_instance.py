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

from openstack.shared_file_system.v2 import share_snapshot_instance
from openstack.tests.unit import base

EXAMPLE = {
    "status": "available",
    "share_id": "618599ab-09a1-432d-973a-c102564c7fec",
    "share_instance_id": "8edff0cb-e5ce-4bab-aa99-afe02ed6a76a",
    "snapshot_id": "d447de19-a6d3-40b3-ae9f-895c86798924",
    "progress": "100%",
    "created_at": "2021-06-04T00:44:52.000000",
    "id": "275516e8-c998-4e78-a41e-7dd3a03e71cd",
    "provider_location": "/path/to/fake...",
    "updated_at": "2017-06-04T00:44:54.000000",
}


class TestShareSnapshotInstances(base.TestCase):
    def test_basic(self):
        instances = share_snapshot_instance.ShareSnapshotInstance()
        self.assertEqual('snapshot_instance', instances.resource_key)
        self.assertEqual('snapshot_instances', instances.resources_key)
        self.assertEqual('/snapshot-instances', instances.base_path)
        self.assertTrue(instances.allow_list)

    def test_make_share_snapshot_instance(self):
        instance = share_snapshot_instance.ShareSnapshotInstance(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], instance.id)
        self.assertEqual(EXAMPLE['share_id'], instance.share_id)
        self.assertEqual(
            EXAMPLE['share_instance_id'], instance.share_instance_id
        )
        self.assertEqual(EXAMPLE['snapshot_id'], instance.snapshot_id)
        self.assertEqual(EXAMPLE['status'], instance.status)
        self.assertEqual(EXAMPLE['progress'], instance.progress)
        self.assertEqual(EXAMPLE['created_at'], instance.created_at)
        self.assertEqual(EXAMPLE['updated_at'], instance.updated_at)
        self.assertEqual(
            EXAMPLE['provider_location'], instance.provider_location
        )
