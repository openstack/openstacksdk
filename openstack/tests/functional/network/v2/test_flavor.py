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

from openstack.network.v2 import flavor
from openstack.tests.functional import base


class TestFlavor(base.BaseFunctionalTest):

    FLAVOR_NAME = uuid.uuid4().hex
    UPDATE_NAME = "UPDATED-NAME"
    SERVICE_TYPE = "FLAVORS"
    ID = None

    @classmethod
    def setUpClass(cls):
        super(TestFlavor, cls).setUpClass()
        flavors = cls.conn.network.create_flavor(name=cls.FLAVOR_NAME,
                                                 service_type=cls.SERVICE_TYPE)
        assert isinstance(flavors, flavor.Flavor)
        cls.assertIs(cls.FLAVOR_NAME, flavors.name)
        cls.assertIs(cls.SERVICE_TYPE, flavors.service_type)

        cls.ID = flavors.id

    @classmethod
    def tearDownClass(cls):
        flavors = cls.conn.network.delete_flavor(cls.ID, ignore_missing=True)
        cls.assertIs(None, flavors)

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
