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

from openstack.compute.v2 import server_meta

FAKE_KEY = 'cervus'
FAKE_SERVER_ID = 'cervidae'
FAKE_VALUE = 'canadensis'
EXAMPLE = {
    'key': FAKE_KEY,
    'server_id': FAKE_SERVER_ID,
    'value': FAKE_VALUE,
}
FAKE_RESPONSE = {"meta": {FAKE_KEY: FAKE_VALUE}}
FAKE_RESPONSES = {"metadata": {FAKE_KEY: FAKE_VALUE}}


class TestServerMeta(testtools.TestCase):

    def test_basic(self):
        sot = server_meta.ServerMeta()
        self.assertEqual('meta', sot.resource_key)
        self.assertEqual(None, sot.resources_key)
        self.assertEqual('/servers/%(server_id)s/metadata', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = server_meta.ServerMeta(EXAMPLE)
        self.assertEqual(EXAMPLE['key'], sot.key)
        self.assertEqual(EXAMPLE['server_id'], sot.server_id)
        self.assertEqual(EXAMPLE['value'], sot.value)

    def test_create(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSE
        sess = mock.Mock()
        sess.put = mock.MagicMock()
        sess.put.return_value = resp
        sot = server_meta.ServerMeta(EXAMPLE)

        sot.create(sess)

        url = 'servers/' + FAKE_SERVER_ID + '/metadata/' + FAKE_KEY
        body = {"meta": {FAKE_KEY: FAKE_VALUE}}
        sess.put.assert_called_with(url, service=sot.service, json=body)
        self.assertEqual(FAKE_VALUE, sot.value)
        self.assertEqual(FAKE_KEY, sot.key)
        self.assertEqual(FAKE_SERVER_ID, sot.server_id)

    def test_get(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSES
        sess = mock.Mock()
        sess.get = mock.MagicMock()
        sess.get.return_value = resp
        sot = server_meta.ServerMeta()
        path_args = {'server_id': FAKE_SERVER_ID}

        resp = sot.list(sess, path_args=path_args)

        url = '/servers/' + FAKE_SERVER_ID + '/metadata'
        sess.get.assert_called_with(url, service=sot.service, params={})
        self.assertEqual(1, len(resp))
        self.assertEqual(FAKE_SERVER_ID, resp[0].server_id)
        self.assertEqual(FAKE_KEY, resp[0].key)
        self.assertEqual(FAKE_VALUE, resp[0].value)

    def test_update(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSE
        sess = mock.Mock()
        sess.put = mock.MagicMock()
        sess.put.return_value = resp
        sot = server_meta.ServerMeta(EXAMPLE)

        sot.update(sess)

        url = 'servers/' + FAKE_SERVER_ID + '/metadata/' + FAKE_KEY
        body = {"meta": {FAKE_KEY: FAKE_VALUE}}
        sess.put.assert_called_with(url, service=sot.service, json=body)
        self.assertEqual(FAKE_VALUE, sot.value)
        self.assertEqual(FAKE_KEY, sot.key)
        self.assertEqual(FAKE_SERVER_ID, sot.server_id)

    def test_delete(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSES
        sess = mock.Mock()
        sess.delete = mock.MagicMock()
        sess.delete.return_value = resp
        sot = server_meta.ServerMeta(EXAMPLE)

        sot.delete(sess)

        url = 'servers/' + FAKE_SERVER_ID + '/metadata/' + FAKE_KEY
        sess.delete.assert_called_with(url, service=sot.service, accept=None)

    def test_list(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSES
        sess = mock.Mock()
        sess.get = mock.MagicMock()
        sess.get.return_value = resp
        sot = server_meta.ServerMeta()
        path_args = {'server_id': FAKE_SERVER_ID}

        resp = sot.list(sess, path_args=path_args)

        url = '/servers/' + FAKE_SERVER_ID + '/metadata'
        sess.get.assert_called_with(url, service=sot.service, params={})
        self.assertEqual(1, len(resp))
        self.assertEqual(FAKE_SERVER_ID, resp[0].server_id)
        self.assertEqual(FAKE_KEY, resp[0].key)
        self.assertEqual(FAKE_VALUE, resp[0].value)
