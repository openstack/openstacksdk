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

import mock
import testtools

from openstack.database.v1 import user

INSTANCE_ID = 'INSTANCE_ID'

CREATING = {
    'databases': '1',
    'name': '2',
    'password': '3',
}
EXISTING = {
    'databases': '1',
    'name': '2',
}


class TestUser(testtools.TestCase):

    def test_basic(self):
        sot = user.User()
        self.assertEqual('user', sot.resource_key)
        self.assertEqual('users', sot.resources_key)
        self.assertEqual('/instances/%(instance_id)s/users', sot.base_path)
        self.assertEqual('database', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make(self):
        sot = user.User(CREATING)
        self.assertEqual(CREATING['name'], sot.id)
        self.assertEqual(CREATING['databases'], sot.databases)
        self.assertEqual(CREATING['name'], sot.name)
        self.assertEqual(CREATING['password'], sot.password)

    def test_existing(self):
        sot = user.User(EXISTING)
        self.assertEqual(EXISTING['name'], sot.id)
        self.assertEqual(EXISTING['databases'], sot.databases)
        self.assertEqual(EXISTING['name'], sot.name)
        self.assertIsNone(sot.password)

    def test_create(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        path_args = {'instance_id': INSTANCE_ID}
        url = '/instances/%(instance_id)s/users' % path_args
        payload = {'users': [CREATING]}

        user.User.create_by_id(sess, CREATING, path_args=path_args)
        sess.post.assert_called_with(url, endpoint_filter=user.User.service,
                                     json=payload)
