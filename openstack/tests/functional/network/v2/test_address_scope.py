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

import uuid

from openstack.network.v2 import address_scope as _address_scope
from openstack.tests.functional import base


class TestAddressScope(base.BaseFunctionalTest):

    ADDRESS_SCOPE_ID = None
    ADDRESS_SCOPE_NAME = uuid.uuid4().hex
    ADDRESS_SCOPE_NAME_UPDATED = uuid.uuid4().hex
    IS_SHARED = False
    IP_VERSION = 4

    @classmethod
    def setUpClass(cls):
        super(TestAddressScope, cls).setUpClass()
        address_scope = cls.conn.network.create_address_scope(
            ip_version=cls.IP_VERSION,
            name=cls.ADDRESS_SCOPE_NAME,
            shared=cls.IS_SHARED,
        )
        assert isinstance(address_scope, _address_scope.AddressScope)
        cls.assertIs(cls.ADDRESS_SCOPE_NAME, address_scope.name)
        cls.ADDRESS_SCOPE_ID = address_scope.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_address_scope(cls.ADDRESS_SCOPE_ID)
        cls.assertIs(None, sot)

    def test_find(self):
        sot = self.conn.network.find_address_scope(self.ADDRESS_SCOPE_NAME)
        self.assertEqual(self.ADDRESS_SCOPE_ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_address_scope(self.ADDRESS_SCOPE_ID)
        self.assertEqual(self.ADDRESS_SCOPE_NAME, sot.name)
        self.assertEqual(self.IS_SHARED, sot.is_shared)
        self.assertEqual(self.IP_VERSION, sot.ip_version)

    def test_list(self):
        names = [o.name for o in self.conn.network.address_scopes()]
        self.assertIn(self.ADDRESS_SCOPE_NAME, names)

    def test_update(self):
        sot = self.conn.network.update_address_scope(
            self.ADDRESS_SCOPE_ID,
            name=self.ADDRESS_SCOPE_NAME_UPDATED)
        self.assertEqual(self.ADDRESS_SCOPE_NAME_UPDATED, sot.name)
