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

from openstack.compute.v2 import server_metadata

FAKE_SERVER_ID = 'cervidae'
FAKE_KEY = 'cervus'
FAKE_VALUE = 'canadensis'
FAKE_KEY2 = 'odocoileus'
FAKE_VALUE2 = 'hemionus'
EXAMPLE = {
    'server_id': FAKE_SERVER_ID,
    FAKE_KEY: FAKE_VALUE,
}
FAKE_RESPONSE = {"metadata": {FAKE_KEY: FAKE_VALUE, FAKE_KEY2: FAKE_VALUE2}}


class TestServerMetadata(testtools.TestCase):

    def test_basic(self):
        sot = server_metadata.ServerMetadata()
        self.assertEqual('metadata', sot.resource_key)
        self.assertEqual(None, sot.resources_key)
        self.assertEqual('/servers/%(server_id)s/metadata', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = server_metadata.ServerMetadata(EXAMPLE)
        self.assertEqual(EXAMPLE['server_id'], sot.server_id)
        self.assertEqual(FAKE_VALUE, sot[FAKE_KEY])

    def test_create(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSE
        sess = mock.Mock()
        sess.put = mock.MagicMock()
        sess.put.return_value = resp
        sot = server_metadata.ServerMetadata(EXAMPLE.copy())

        sot.create(sess)

        url = '/servers/' + FAKE_SERVER_ID + '/metadata'
        body = {"metadata": {FAKE_KEY: FAKE_VALUE}}
        sess.put.assert_called_with(url, service=sot.service, json=body)
        self.assertEqual(FAKE_SERVER_ID, sot.server_id)
        self.assertEqual(FAKE_VALUE, sot[FAKE_KEY])

    def test_get(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSE
        sess = mock.Mock()
        sess.get = mock.MagicMock()
        sess.get.return_value = resp
        sot = server_metadata.ServerMetadata(EXAMPLE.copy())

        sot.get(sess)

        url = '/servers/' + FAKE_SERVER_ID + '/metadata'
        sess.get.assert_called_with(url, service=sot.service)
        self.assertEqual(FAKE_SERVER_ID, sot.server_id)
        self.assertEqual(FAKE_VALUE, sot[FAKE_KEY])
        self.assertEqual(FAKE_VALUE2, sot[FAKE_KEY2])

    def test_update(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSE
        sess = mock.Mock()
        sess.put = mock.MagicMock()
        sess.put.return_value = resp
        sot = server_metadata.ServerMetadata(EXAMPLE.copy())

        sot.update(sess)

        url = '/servers/' + FAKE_SERVER_ID + '/metadata'
        body = {"metadata": {FAKE_KEY: FAKE_VALUE}}
        sess.put.assert_called_with(url, service=sot.service, json=body)
        self.assertEqual(FAKE_SERVER_ID, sot.server_id)
        self.assertEqual(FAKE_VALUE, sot[FAKE_KEY])
