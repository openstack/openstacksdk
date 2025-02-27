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


from openstack.compute.v2 import keypair as _keypair
from openstack.tests.functional import base


class TestKeypair(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        # Keypairs can't have .'s in the name. Because why?
        self.keypair_name = self.getUniqueString().split('.')[-1]

    def _delete_keypair(self, keypair):
        ret = self.user_cloud.compute.delete_keypair(keypair)
        self.assertIsNone(ret)

    def test_keypair(self):
        # create the keypair

        keypair = self.user_cloud.compute.create_keypair(
            name=self.keypair_name, type='ssh'
        )
        self.assertIsInstance(keypair, _keypair.Keypair)
        self.assertEqual(self.keypair_name, keypair.name)
        self.addCleanup(self._delete_keypair, keypair)

        # retrieve details of the keypair by ID

        keypair = self.user_cloud.compute.get_keypair(self.keypair_name)
        self.assertIsInstance(keypair, _keypair.Keypair)
        self.assertEqual(self.keypair_name, keypair.name)
        self.assertEqual(self.keypair_name, keypair.id)
        self.assertEqual('ssh', keypair.type)

        # retrieve details of the keypair by name

        keypair = self.user_cloud.compute.find_keypair(self.keypair_name)
        self.assertIsInstance(keypair, _keypair.Keypair)
        self.assertEqual(self.keypair_name, keypair.name)
        self.assertEqual(self.keypair_name, keypair.id)

        # list all keypairs

        keypairs = list(self.user_cloud.compute.keypairs())
        self.assertIsInstance(keypair, _keypair.Keypair)
        self.assertIn(self.keypair_name, {x.name for x in keypairs})


class TestKeypairAdmin(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.keypair_name = self.getUniqueString().split('.')[-1]
        self.user = self.operator_cloud.list_users()[0]

    def _delete_keypair(self, keypair):
        ret = self.user_cloud.compute.delete_keypair(keypair)
        self.assertIsNone(ret)

    def test_keypair(self):
        # create the keypair (for another user)
        keypair = self.operator_cloud.compute.create_keypair(
            name=self.keypair_name, user_id=self.user.id
        )
        self.assertIsInstance(keypair, _keypair.Keypair)
        self.assertEqual(self.keypair_name, keypair.name)
        self.addCleanup(self._delete_keypair, keypair)

        # retrieve details of the keypair by ID (for another user)

        keypair = self.operator_cloud.compute.get_keypair(
            self.keypair_name, user_id=self.user.id
        )
        self.assertEqual(self.keypair_name, keypair.name)
        self.assertEqual(self.keypair_name, keypair.id)
        self.assertEqual(self.user.id, keypair.user_id)
