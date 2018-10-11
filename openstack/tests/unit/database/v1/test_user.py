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

from openstack.tests.unit import base

from openstack.database.v1 import user

INSTANCE_ID = 'INSTANCE_ID'

CREATING = {
    'databases': '1',
    'name': '2',
    'password': '3',
}


class TestUser(base.TestCase):

    def test_basic(self):
        sot = user.User()
        self.assertEqual('user', sot.resource_key)
        self.assertEqual('users', sot.resources_key)
        self.assertEqual('/instances/%(instance_id)s/users', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make(self):
        sot = user.User(**CREATING)
        self.assertEqual(CREATING['name'], sot.id)
        self.assertEqual(CREATING['databases'], sot.databases)
        self.assertEqual(CREATING['name'], sot.name)
        self.assertEqual(CREATING['name'], sot.id)
        self.assertEqual(CREATING['password'], sot.password)

    def test_create(self):
        sot = user.User(instance_id=INSTANCE_ID, **CREATING)
        result = sot._prepare_request()
        self.assertEqual(result.body, {sot.resources_key: CREATING})
