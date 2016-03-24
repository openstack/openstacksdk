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

from openstack.compute.v2 import keypair
from openstack.tests.functional import base


class TestKeypair(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex
    ID = None

    @classmethod
    def setUpClass(cls):
        super(TestKeypair, cls).setUpClass()
        sot = cls.conn.compute.create_keypair(name=cls.NAME)
        assert isinstance(sot, keypair.Keypair)
        cls.assertIs(cls.NAME, sot.name)
        cls._keypair = sot
        cls.ID = sot.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.compute.delete_keypair(cls._keypair)
        cls.assertIs(None, sot)

    def test_find(self):
        sot = self.conn.compute.find_keypair(self.NAME)
        self.assertEqual(self.ID, sot.id)

    def test_get(self):
        sot = self.conn.compute.get_keypair(self.NAME)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        names = [o.name for o in self.conn.compute.keypairs()]
        self.assertIn(self.NAME, names)
