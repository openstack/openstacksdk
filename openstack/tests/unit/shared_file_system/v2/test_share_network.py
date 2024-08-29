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

from openstack.shared_file_system.v2 import share_network
from openstack.tests.unit import base

IDENTIFIER = '6e1821be-c494-4f62-8301-5dcd19f4d615'
EXAMPLE = {
    "id": IDENTIFIER,
    "project_id": "4b8184eddd6b429a93231c056ae9cd12",
    "name": "my_share_net",
    "description": "My share network",
    "created_at": "2021-06-10T10:11:17.291981",
    "updated_at": None,
    "share_network_subnets": [],
}


class TestShareNetwork(base.TestCase):
    def test_basic(self):
        networks = share_network.ShareNetwork()
        self.assertEqual('share_networks', networks.resources_key)
        self.assertEqual('/share-networks', networks.base_path)
        self.assertTrue(networks.allow_list)
        self.assertTrue(networks.allow_create)
        self.assertTrue(networks.allow_fetch)
        self.assertTrue(networks.allow_commit)
        self.assertTrue(networks.allow_delete)
        self.assertFalse(networks.allow_head)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
                "project_id": "project_id",
                "created_since": "created_since",
                "created_before": "created_before",
                "offset": "offset",
                "security_service_id": "security_service_id",
                "all_projects": "all_tenants",
                "name": "name",
                "description": "description",
            },
            networks._query_mapping._mapping,
        )

    def test_share_network(self):
        networks = share_network.ShareNetwork(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], networks.id)
        self.assertEqual(EXAMPLE['name'], networks.name)
        self.assertEqual(EXAMPLE['project_id'], networks.project_id)
        self.assertEqual(EXAMPLE['description'], networks.description)
        self.assertEqual(EXAMPLE['created_at'], networks.created_at)
        self.assertEqual(EXAMPLE['updated_at'], networks.updated_at)
