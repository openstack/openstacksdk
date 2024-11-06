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
# mypy: disable-error-code="method-assign"

from openstack.network.v2 import security_group
from openstack.tests.functional.network.v2 import common


class TestSecurityGroup(common.TestTagNeutron):
    ID = None

    def setUp(self):
        super().setUp()
        self.NAME = self.getUniqueString()
        sot = self.user_cloud.network.create_security_group(name=self.NAME)
        assert isinstance(sot, security_group.SecurityGroup)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id
        self.get_command = self.user_cloud.network.get_security_group

    def tearDown(self):
        sot = self.user_cloud.network.delete_security_group(
            self.ID, ignore_missing=False
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_security_group(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.user_cloud.network.get_security_group(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        names = [o.name for o in self.user_cloud.network.security_groups()]
        self.assertIn(self.NAME, names)

    def test_list_query_list_of_ids(self):
        ids = [
            o.id for o in self.user_cloud.network.security_groups(id=[self.ID])
        ]
        self.assertIn(self.ID, ids)
