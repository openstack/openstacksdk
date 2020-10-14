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


from openstack.network.v2 import address_group as _address_group
from openstack.tests.functional import base


class TestAddressGroup(base.BaseFunctionalTest):

    ADDRESS_GROUP_ID = None
    ADDRESSES = ['10.0.0.1/32', '2001:db8::/32']

    def setUp(self):
        super(TestAddressGroup, self).setUp()

        # Skip the tests if address group extension is not enabled.
        if not self.conn.network.find_extension('address-group'):
            self.skipTest('Network Address Group extension disabled')

        self.ADDRESS_GROUP_NAME = self.getUniqueString()
        self.ADDRESS_GROUP_DESCRIPTION = self.getUniqueString()
        self.ADDRESS_GROUP_NAME_UPDATED = self.getUniqueString()
        self.ADDRESS_GROUP_DESCRIPTION_UPDATED = self.getUniqueString()
        address_group = self.conn.network.create_address_group(
            name=self.ADDRESS_GROUP_NAME,
            description=self.ADDRESS_GROUP_DESCRIPTION,
            addresses=self.ADDRESSES
        )
        assert isinstance(address_group, _address_group.AddressGroup)
        self.assertEqual(self.ADDRESS_GROUP_NAME, address_group.name)
        self.assertEqual(self.ADDRESS_GROUP_DESCRIPTION,
                         address_group.description)
        self.assertCountEqual(self.ADDRESSES, address_group.addresses)
        self.ADDRESS_GROUP_ID = address_group.id

    def tearDown(self):
        sot = self.conn.network.delete_address_group(self.ADDRESS_GROUP_ID)
        self.assertIsNone(sot)
        super(TestAddressGroup, self).tearDown()

    def test_find(self):
        sot = self.conn.network.find_address_group(self.ADDRESS_GROUP_NAME)
        self.assertEqual(self.ADDRESS_GROUP_ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_address_group(self.ADDRESS_GROUP_ID)
        self.assertEqual(self.ADDRESS_GROUP_NAME, sot.name)

    def test_list(self):
        names = [ag.name for ag in self.conn.network.address_groups()]
        self.assertIn(self.ADDRESS_GROUP_NAME, names)

    def test_update(self):
        sot = self.conn.network.update_address_group(
            self.ADDRESS_GROUP_ID,
            name=self.ADDRESS_GROUP_NAME_UPDATED,
            description=self.ADDRESS_GROUP_DESCRIPTION_UPDATED)
        self.assertEqual(self.ADDRESS_GROUP_NAME_UPDATED, sot.name)
        self.assertEqual(self.ADDRESS_GROUP_DESCRIPTION_UPDATED,
                         sot.description)

    def test_add_remove_addresses(self):
        addrs = ['127.0.0.1/32', 'fe80::/10']
        sot = self.conn.network.add_addresses_to_address_group(
            self.ADDRESS_GROUP_ID, addrs)
        updated_addrs = self.ADDRESSES.copy()
        updated_addrs.extend(addrs)
        self.assertCountEqual(updated_addrs, sot.addresses)
        sot = self.conn.network.remove_addresses_from_address_group(
            self.ADDRESS_GROUP_ID, addrs)
        self.assertCountEqual(self.ADDRESSES, sot.addresses)
