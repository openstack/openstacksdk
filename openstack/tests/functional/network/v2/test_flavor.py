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

from openstack.network.v2 import flavor
from openstack.tests.functional import base


class TestFlavor(base.BaseFunctionalTest):

    UPDATE_NAME = "UPDATED-NAME"
    SERVICE_TYPE = "FLAVORS"
    ID = None

    SERVICE_PROFILE_DESCRIPTION = "DESCRIPTION"
    METAINFO = "FlAVOR_PROFILE_METAINFO"

    def setUp(self):
        super(TestFlavor, self).setUp()
        self.FLAVOR_NAME = self.getUniqueString('flavor')
        flavors = self.conn.network.create_flavor(
            name=self.FLAVOR_NAME,
            service_type=self.SERVICE_TYPE)
        assert isinstance(flavors, flavor.Flavor)
        self.assertEqual(self.FLAVOR_NAME, flavors.name)
        self.assertEqual(self.SERVICE_TYPE, flavors.service_type)

        self.ID = flavors.id

        self.service_profiles = self.conn.network.create_service_profile(
            description=self.SERVICE_PROFILE_DESCRIPTION,
            metainfo=self.METAINFO,)

    def tearDown(self):
        flavors = self.conn.network.delete_flavor(self.ID, ignore_missing=True)
        self.assertIsNone(flavors)

        service_profiles = self.conn.network.delete_service_profile(
            self.ID, ignore_missing=True)
        self.assertIsNone(service_profiles)
        super(TestFlavor, self).tearDown()

    def test_find(self):
        flavors = self.conn.network.find_flavor(self.FLAVOR_NAME)
        self.assertEqual(self.ID, flavors.id)

    def test_get(self):
        flavors = self.conn.network.get_flavor(self.ID)
        self.assertEqual(self.FLAVOR_NAME, flavors.name)
        self.assertEqual(self.ID, flavors.id)

    def test_list(self):
        names = [f.name for f in self.conn.network.flavors()]
        self.assertIn(self.FLAVOR_NAME, names)

    def test_update(self):
        flavor = self.conn.network.update_flavor(self.ID,
                                                 name=self.UPDATE_NAME)
        self.assertEqual(self.UPDATE_NAME, flavor.name)

    def test_associate_disassociate_flavor_with_service_profile(self):
        response = \
            self.conn.network.associate_flavor_with_service_profile(
                self.ID, self.service_profiles.id)
        self.assertIsNotNone(response)

        response = \
            self.conn.network.disassociate_flavor_from_service_profile(
                self.ID, self.service_profiles.id)
        self.assertIsNone(response)
