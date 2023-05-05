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

from openstack.baremetal.v1 import volume_target
from openstack.tests.unit import base


FAKE = {
    "boot_index": 0,
    "created_at": "2016-08-18T22:28:48.643434+11:11",
    "extra": {},
    "links": [
        {
            "href": "http://127.0.0.1:6385/v1/volume/targets/<ID>",
            "rel": "self",
        },
        {
            "href": "http://127.0.0.1:6385/volume/targets/<ID>",
            "rel": "bookmark",
        },
    ],
    "node_uuid": "6d85703a-565d-469a-96ce-30b6de53079d",
    "properties": {},
    "updated_at": None,
    "uuid": "bd4d008c-7d31-463d-abf9-6c23d9d55f7f",
    "volume_id": "04452bed-5367-4202-8bf5-de4335ac56d2",
    "volume_type": "iscsi",
}


class TestVolumeTarget(base.TestCase):
    def test_basic(self):
        sot = volume_target.VolumeTarget()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('targets', sot.resources_key)
        self.assertEqual('/volume/targets', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

    def test_instantiate(self):
        sot = volume_target.VolumeTarget(**FAKE)
        self.assertEqual(FAKE['boot_index'], sot.boot_index)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['node_uuid'], sot.node_id)
        self.assertEqual(FAKE['properties'], sot.properties)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['volume_id'], sot.volume_id)
        self.assertEqual(FAKE['volume_type'], sot.volume_type)
