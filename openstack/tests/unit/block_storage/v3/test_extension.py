# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
# # Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.block_storage.v3 import extension
from openstack.tests.unit import base

EXTENSION = {
    "alias": "os-hosts",
    "description": "Admin-only host administration.",
    "links": [],
    "name": "Hosts",
    "updated": "2011-06-29T00:00:00+00:00",
}


class TestExtension(base.TestCase):
    def test_basic(self):
        extension_resource = extension.Extension()
        self.assertEqual('extensions', extension_resource.resources_key)
        self.assertEqual('/extensions', extension_resource.base_path)
        self.assertFalse(extension_resource.allow_create)
        self.assertFalse(extension_resource.allow_fetch)
        self.assertFalse(extension_resource.allow_commit)
        self.assertFalse(extension_resource.allow_delete)
        self.assertTrue(extension_resource.allow_list)

    def test_make_extension(self):
        extension_resource = extension.Extension(**EXTENSION)
        self.assertEqual(EXTENSION['alias'], extension_resource.alias)
        self.assertEqual(
            EXTENSION['description'], extension_resource.description
        )
        self.assertEqual(EXTENSION['links'], extension_resource.links)
        self.assertEqual(EXTENSION['name'], extension_resource.name)
        self.assertEqual(EXTENSION['updated'], extension_resource.updated_at)
