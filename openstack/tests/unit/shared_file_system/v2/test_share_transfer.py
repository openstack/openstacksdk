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

from openstack.shared_file_system.v2 import share_transfer
from openstack.tests.unit import base

EXAMPLE = [
    {
        "id": "02a948b4-671b-4c62-b13a-18d613cb4576",
        "resource_type": "share",
        "resource_id": "0fe7cf64-b879-4902-9d86-f80aeff12b06",
        "name": "transfer2",
        "links": [
            {
                "rel": "self",
                "href": "http://127.0.0.1/share/v2/share-transfer"
                "/02a948b4-671b-4c62-b13a-18d613cb4576",
            },
            {
                "rel": "bookmark",
                "href": "http://127.0.0.1/share/share-transfer/02a948b4"
                "-671b-4c62-b13a-18d613cb4576",
            },
        ],
    },
    {
        "id": "a10209ff-b55d-4fed-9f63-abea53b6f107",
        "resource_type": "share",
        "resource_id": "29476819-28a9-4b1a-a21d-3b2d203025a0",
        "name": "transfer1",
        "links": [
            {
                "rel": "self",
                "href": "http://127.0.0.1/share/v2/share-transfer"
                "/a10209ff-b55d-4fed-9f63-abea53b6f107",
            },
            {
                "rel": "bookmark",
                "href": "http://127.0.0.1/share/share-transfer/a10209ff"
                "-b55d-4fed-9f63-abea53b6f107",
            },
        ],
    },
]


class TestShareTransfer(base.TestCase):
    def test_basic(self):
        transfers = share_transfer.ShareTransfer()
        self.assertTrue(transfers.allow_list)
        self.assertTrue(transfers.allow_fetch)
        self.assertTrue(transfers.allow_create)
        self.assertFalse(transfers.allow_commit)
        self.assertTrue(transfers.allow_delete)

    def test_get_share_transfer_details(self):
        transfer = share_transfer.ShareTransfer.existing(**EXAMPLE[0])
        self.assertEqual(EXAMPLE[0]['id'], transfer.id)
        self.assertEqual(EXAMPLE[0]['resource_type'], transfer.resource_type)
        self.assertEqual(EXAMPLE[0]['resource_id'], transfer.resource_id)
        self.assertEqual(EXAMPLE[0]['name'], transfer.name)
        self.assertEqual(EXAMPLE[0]['links'], transfer.links)
