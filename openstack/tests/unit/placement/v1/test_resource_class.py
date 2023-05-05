# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.placement.v1 import resource_class as rc
from openstack.tests.unit import base

FAKE = {
    'name': 'CUSTOM_FPGA',
}


class TestResourceClass(base.TestCase):
    def test_basic(self):
        sot = rc.ResourceClass()
        self.assertEqual(None, sot.resource_key)
        self.assertEqual('resource_classes', sot.resources_key)
        self.assertEqual('/resource_classes', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_patch)

        self.assertDictEqual(
            {'limit': 'limit', 'marker': 'marker'}, sot._query_mapping._mapping
        )

    def test_make_it(self):
        sot = rc.ResourceClass(**FAKE)
        self.assertEqual(FAKE['name'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)
