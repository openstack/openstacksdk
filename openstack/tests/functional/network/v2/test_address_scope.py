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


from openstack.network.v2 import address_scope as _address_scope
from openstack.tests.functional import base


class TestAddressScope(base.BaseFunctionalTest):
    ADDRESS_SCOPE_ID = None
    IS_SHARED = False
    IP_VERSION = 4

    def setUp(self):
        super().setUp()
        self.ADDRESS_SCOPE_NAME = self.getUniqueString()
        self.ADDRESS_SCOPE_NAME_UPDATED = self.getUniqueString()
        address_scope = self.user_cloud.network.create_address_scope(
            ip_version=self.IP_VERSION,
            name=self.ADDRESS_SCOPE_NAME,
            shared=self.IS_SHARED,
        )
        assert isinstance(address_scope, _address_scope.AddressScope)
        self.assertEqual(self.ADDRESS_SCOPE_NAME, address_scope.name)
        self.ADDRESS_SCOPE_ID = address_scope.id

    def tearDown(self):
        sot = self.user_cloud.network.delete_address_scope(
            self.ADDRESS_SCOPE_ID
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_address_scope(
            self.ADDRESS_SCOPE_NAME
        )
        self.assertEqual(self.ADDRESS_SCOPE_ID, sot.id)

    def test_get(self):
        sot = self.user_cloud.network.get_address_scope(self.ADDRESS_SCOPE_ID)
        self.assertEqual(self.ADDRESS_SCOPE_NAME, sot.name)
        self.assertEqual(self.IS_SHARED, sot.is_shared)
        self.assertEqual(self.IP_VERSION, sot.ip_version)

    def test_list(self):
        names = [o.name for o in self.user_cloud.network.address_scopes()]
        self.assertIn(self.ADDRESS_SCOPE_NAME, names)

    def test_update(self):
        sot = self.user_cloud.network.update_address_scope(
            self.ADDRESS_SCOPE_ID, name=self.ADDRESS_SCOPE_NAME_UPDATED
        )
        self.assertEqual(self.ADDRESS_SCOPE_NAME_UPDATED, sot.name)
