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


from openstack.compute.v2 import keypair
from openstack.tests.functional import base


class TestKeypair(base.BaseFunctionalTest):

    def setUp(self):
        super(TestKeypair, self).setUp()

        # Keypairs can't have .'s in the name. Because why?
        self.NAME = self.getUniqueString().split('.')[-1]

        sot = self.conn.compute.create_keypair(name=self.NAME)
        assert isinstance(sot, keypair.Keypair)
        self.assertEqual(self.NAME, sot.name)
        self._keypair = sot

    def tearDown(self):
        sot = self.conn.compute.delete_keypair(self._keypair)
        self.assertIsNone(sot)
        super(TestKeypair, self).tearDown()

    def test_find(self):
        sot = self.conn.compute.find_keypair(self.NAME)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.NAME, sot.id)

    def test_get(self):
        sot = self.conn.compute.get_keypair(self.NAME)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.NAME, sot.id)

    def test_list(self):
        names = [o.name for o in self.conn.compute.keypairs()]
        self.assertIn(self.NAME, names)
