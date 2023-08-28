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

from openstack.compute.v2 import extension
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'alias': '1',
    'description': '2',
    'links': [],
    'name': '4',
    'namespace': '5',
    'updated': '2015-03-09T12:14:57.233772',
}


class TestExtension(base.TestCase):
    def test_basic(self):
        sot = extension.Extension()
        self.assertEqual('extension', sot.resource_key)
        self.assertEqual('extensions', sot.resources_key)
        self.assertEqual('/extensions', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = extension.Extension(**EXAMPLE)
        self.assertEqual(EXAMPLE['alias'], sot.alias)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['namespace'], sot.namespace)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
