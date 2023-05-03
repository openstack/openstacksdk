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

from openstack.network.v2 import address_scope
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'ip_version': 4,
    'name': '1',
    'shared': True,
    'project_id': '2',
}


class TestAddressScope(base.TestCase):
    def test_basic(self):
        sot = address_scope.AddressScope()
        self.assertEqual('address_scope', sot.resource_key)
        self.assertEqual('address_scopes', sot.resources_key)
        self.assertEqual('/address-scopes', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = address_scope.AddressScope(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['ip_version'], sot.ip_version)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertTrue(sot.is_shared)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
