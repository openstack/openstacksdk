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

from openstack.network.v2 import address_group
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'name': '1',
    'description': '2',
    'project_id': '3',
    'addresses': ['10.0.0.1/32'],
}


class TestAddressGroup(base.TestCase):
    def test_basic(self):
        sot = address_group.AddressGroup()
        self.assertEqual('address_group', sot.resource_key)
        self.assertEqual('address_groups', sot.resources_key)
        self.assertEqual('/address-groups', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                "name": "name",
                "description": "description",
                "project_id": "project_id",
                "sort_key": "sort_key",
                "sort_dir": "sort_dir",
                "limit": "limit",
                "marker": "marker",
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = address_group.AddressGroup(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertCountEqual(EXAMPLE['addresses'], sot.addresses)
