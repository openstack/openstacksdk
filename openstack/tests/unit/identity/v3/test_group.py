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

from unittest import mock

from keystoneauth1 import adapter

from openstack.identity.v3 import group
from openstack.identity.v3 import user
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'description': '1',
    'domain_id': '2',
    'id': IDENTIFIER,
    'name': '4',
}


class TestGroup(base.TestCase):
    def setUp(self):
        super().setUp()
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = 1
        self.sess._get_connection = mock.Mock(return_value=self.cloud)
        self.good_resp = mock.Mock()
        self.good_resp.body = None
        self.good_resp.json = mock.Mock(return_value=self.good_resp.body)
        self.good_resp.status_code = 204

    def test_basic(self):
        sot = group.Group()
        self.assertEqual('group', sot.resource_key)
        self.assertEqual('groups', sot.resources_key)
        self.assertEqual('/groups', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

        self.assertDictEqual(
            {
                'domain_id': 'domain_id',
                'name': 'name',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = group.Group(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['domain_id'], sot.domain_id)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)

    def test_add_user(self):
        sot = group.Group(**EXAMPLE)
        resp = self.good_resp
        self.sess.put = mock.Mock(return_value=resp)

        sot.add_user(self.sess, user.User(id='1'))

        self.sess.put.assert_called_with('groups/IDENTIFIER/users/1')

    def test_remove_user(self):
        sot = group.Group(**EXAMPLE)
        resp = self.good_resp
        self.sess.delete = mock.Mock(return_value=resp)

        sot.remove_user(self.sess, user.User(id='1'))

        self.sess.delete.assert_called_with('groups/IDENTIFIER/users/1')

    def test_check_user(self):
        sot = group.Group(**EXAMPLE)
        resp = self.good_resp
        self.sess.head = mock.Mock(return_value=resp)

        self.assertTrue(sot.check_user(self.sess, user.User(id='1')))

        self.sess.head.assert_called_with('groups/IDENTIFIER/users/1')
