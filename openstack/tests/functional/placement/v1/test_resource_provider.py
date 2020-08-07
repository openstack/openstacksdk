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

from openstack.placement.v1 import resource_provider
from openstack.tests.functional import base


class TestResourceProvider(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()
        self._set_operator_cloud(interface='admin')

        self.NAME = self.getUniqueString()

        sot = self.conn.placement.create_resource_provider(name=self.NAME)
        assert isinstance(sot, resource_provider.ResourceProvider)
        self.assertEqual(self.NAME, sot.name)
        self._resource_provider = sot

    def tearDown(self):
        sot = self.conn.placement.delete_resource_provider(
            self._resource_provider)
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.conn.placement.find_resource_provider(self.NAME)
        self.assertEqual(self.NAME, sot.name)

    def test_get(self):
        sot = self.conn.placement.get_resource_provider(
            self._resource_provider.id)
        self.assertEqual(self.NAME, sot.name)

    def test_list(self):
        names = [o.name for o in self.conn.placement.resource_providers()]
        self.assertIn(self.NAME, names)
