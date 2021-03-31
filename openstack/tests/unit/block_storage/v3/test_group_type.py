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

from openstack.block_storage.v3 import group_type
from openstack.tests.unit import base

GROUP_TYPE = {
    "id": "6685584b-1eac-4da6-b5c3-555430cf68ff",
    "name": "grp-type-001",
    "description": "group type 001",
    "is_public": True,
    "group_specs": {
        "consistent_group_snapshot_enabled": "<is> False"
    }
}


class TestGroupType(base.TestCase):

    def test_basic(self):
        resource = group_type.GroupType()
        self.assertEqual("group_type", resource.resource_key)
        self.assertEqual("group_types", resource.resources_key)
        self.assertEqual("/group_types", resource.base_path)
        self.assertTrue(resource.allow_create)
        self.assertTrue(resource.allow_fetch)
        self.assertTrue(resource.allow_delete)
        self.assertTrue(resource.allow_commit)
        self.assertTrue(resource.allow_list)

    def test_make_resource(self):
        resource = group_type.GroupType(**GROUP_TYPE)
        self.assertEqual(GROUP_TYPE["id"], resource.id)
        self.assertEqual(GROUP_TYPE["name"], resource.name)
        self.assertEqual(GROUP_TYPE["description"], resource.description)
        self.assertEqual(GROUP_TYPE["is_public"], resource.is_public)
        self.assertEqual(GROUP_TYPE["group_specs"], resource.group_specs)
