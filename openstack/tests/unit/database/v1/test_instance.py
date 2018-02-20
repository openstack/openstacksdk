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
from openstack.tests.unit import base

from openstack.database.v1 import instance

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'flavor': '1',
    'id': IDENTIFIER,
    'links': '3',
    'name': '4',
    'status': '5',
    'volume': '6',
    'datastore': {'7': 'seven'},
    'region': '8',
    'hostname': '9',
    'created': '10',
    'updated': '11',
}


class TestInstance(base.TestCase):

    def test_basic(self):
        sot = instance.Instance()
        self.assertEqual('instance', sot.resource_key)
        self.assertEqual('instances', sot.resources_key)
        self.assertEqual('/instances', sot.base_path)
        self.assertEqual('database', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = instance.Instance(**EXAMPLE)
        self.assertEqual(EXAMPLE['flavor'], sot.flavor)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['volume'], sot.volume)
        self.assertEqual(EXAMPLE['datastore'], sot.datastore)
        self.assertEqual(EXAMPLE['region'], sot.region)
        self.assertEqual(EXAMPLE['hostname'], sot.hostname)
        self.assertEqual(EXAMPLE['created'], sot.created_at)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)

    def test_enable_root_user(self):
        sot = instance.Instance(**EXAMPLE)
        response = mock.Mock()
        response.body = {'user': {'name': 'root', 'password': 'foo'}}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)

        self.assertEqual(response.body['user'], sot.enable_root_user(sess))

        url = ("instances/%s/root" % IDENTIFIER)
        sess.post.assert_called_with(url,)

    def test_is_root_enabled(self):
        sot = instance.Instance(**EXAMPLE)
        response = mock.Mock()
        response.body = {'rootEnabled': True}
        response.json = mock.Mock(return_value=response.body)
        sess = mock.Mock()
        sess.get = mock.Mock(return_value=response)

        self.assertTrue(sot.is_root_enabled(sess))

        url = ("instances/%s/root" % IDENTIFIER)
        sess.get.assert_called_with(url,)

    def test_action_restart(self):
        sot = instance.Instance(**EXAMPLE)
        response = mock.Mock()
        response.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)

        self.assertIsNone(sot.restart(sess))

        url = ("instances/%s/action" % IDENTIFIER)
        body = {'restart': {}}
        sess.post.assert_called_with(url,
                                     json=body)

    def test_action_resize(self):
        sot = instance.Instance(**EXAMPLE)
        response = mock.Mock()
        response.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)
        flavor = 'http://flavor/flav'

        self.assertIsNone(sot.resize(sess, flavor))

        url = ("instances/%s/action" % IDENTIFIER)
        body = {'resize': {'flavorRef': flavor}}
        sess.post.assert_called_with(url,
                                     json=body)

    def test_action_resize_volume(self):
        sot = instance.Instance(**EXAMPLE)
        response = mock.Mock()
        response.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)
        size = 4

        self.assertIsNone(sot.resize_volume(sess, size))

        url = ("instances/%s/action" % IDENTIFIER)
        body = {'resize': {'volume': size}}
        sess.post.assert_called_with(url,
                                     json=body)
