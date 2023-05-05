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

from openstack.shared_file_system.v2 import share_access_rule
from openstack.tests.unit import base

EXAMPLE = {
    "access_level": "rw",
    "state": "error",
    "id": "507bf114-36f2-4f56-8cf4-857985ca87c1",
    "share_id": "fb213952-2352-41b4-ad7b-2c4c69d13eef",
    "access_type": "cert",
    "access_to": "example.com",
    "access_key": None,
    "created_at": "2021-09-12T02:01:04.000000",
    "updated_at": "2021-09-12T02:01:04.000000",
    "metadata": {"key1": "value1", "key2": "value2"},
}


class TestShareAccessRule(base.TestCase):
    def test_basic(self):
        rules_resource = share_access_rule.ShareAccessRule()
        self.assertEqual('access_list', rules_resource.resources_key)
        self.assertEqual('/share-access-rules', rules_resource.base_path)
        self.assertTrue(rules_resource.allow_list)

        self.assertDictEqual(
            {"limit": "limit", "marker": "marker", "share_id": "share_id"},
            rules_resource._query_mapping._mapping,
        )

    def test_make_share_access_rules(self):
        rules_resource = share_access_rule.ShareAccessRule(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], rules_resource.id)
        self.assertEqual(EXAMPLE['access_level'], rules_resource.access_level)
        self.assertEqual(EXAMPLE['state'], rules_resource.state)
        self.assertEqual(EXAMPLE['id'], rules_resource.id)
        self.assertEqual(EXAMPLE['access_type'], rules_resource.access_type)
        self.assertEqual(EXAMPLE['access_to'], rules_resource.access_to)
        self.assertEqual(EXAMPLE['access_key'], rules_resource.access_key)
        self.assertEqual(EXAMPLE['created_at'], rules_resource.created_at)
        self.assertEqual(EXAMPLE['updated_at'], rules_resource.updated_at)
        self.assertEqual(EXAMPLE['metadata'], rules_resource.metadata)
