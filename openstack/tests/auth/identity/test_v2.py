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

from openstack.auth.identity import v2
from openstack import exceptions
from openstack.tests.auth import common

TEST_URL = 'http://127.0.0.1:5000/v2.0'

TEST_SERVICE_CATALOG = common.TEST_SERVICE_CATALOG_V2
TEST_RESPONSE_DICT = common.TEST_RESPONSE_DICT_V2


class TestV2Auth(testtools.TestCase):

    def test_missing_args(self):
        with testtools.ExpectedException(exceptions.AuthorizationFailure):
            v2.Auth(TEST_URL)

    def test_password(self):
        kargs = {
            'password': common.TEST_PASS,
            'project_id': common.TEST_TENANT_ID,
            'project_name': common.TEST_TENANT_NAME,
            'trust_id': common.TEST_TRUST_ID,
            'user_name': common.TEST_USER,
        }

        sot = v2.Auth(TEST_URL, **kargs)

        self.assertEqual(common.TEST_USER, sot.user_name)
        self.assertEqual(common.TEST_PASS, sot.password)
        self.assertEqual(common.TEST_TRUST_ID, sot.trust_id)
        self.assertEqual(common.TEST_TENANT_ID, sot.tenant_id)
        self.assertEqual(common.TEST_TENANT_NAME, sot.tenant_name)
        expected = {'passwordCredentials': {'password': common.TEST_PASS,
                                            'username': common.TEST_USER}}
        headers = {}
        self.assertEqual(expected, sot.get_auth_data(headers))
        self.assertEqual({}, headers)

    def test_empty_token(self):
        kargs = {
            'password': common.TEST_PASS,
            'token': '',
            'user_name': common.TEST_USER,
        }

        sot = v2.Auth(TEST_URL, **kargs)

        self.assertEqual(common.TEST_USER, sot.user_name)
        self.assertEqual(common.TEST_PASS, sot.password)
        self.assertEqual(None, sot.token)

    def test_token(self):
        kargs = {
            'project_id': common.TEST_TENANT_ID,
            'project_name': common.TEST_TENANT_NAME,
            'token': common.TEST_TOKEN,
            'trust_id': common.TEST_TRUST_ID,
        }

        sot = v2.Auth(TEST_URL, **kargs)

        self.assertEqual(common.TEST_TOKEN, sot.token)
        self.assertEqual(common.TEST_TRUST_ID, sot.trust_id)
        self.assertEqual(common.TEST_TENANT_ID, sot.tenant_id)
        self.assertEqual(common.TEST_TENANT_NAME, sot.tenant_name)
        expected = {'token': {'id': common.TEST_TOKEN}}
        headers = {}
        self.assertEqual(expected, sot.get_auth_data(headers))
        self.assertEqual({'X-Auth-Token': common.TEST_TOKEN}, headers)

    def test_user_id(self):
        kargs = {
            'password': common.TEST_PASS,
            'project_id': common.TEST_TENANT_ID,
            'project_name': common.TEST_TENANT_NAME,
            'trust_id': common.TEST_TRUST_ID,
            'user_name': common.TEST_USER,
            'user_id': common.TEST_USER_ID,
        }

        sot = v2.Auth(TEST_URL, **kargs)

        self.assertEqual(common.TEST_USER, sot.user_name)
        self.assertEqual(common.TEST_USER_ID, sot.user_id)
        self.assertEqual(common.TEST_PASS, sot.password)
        self.assertEqual(common.TEST_TRUST_ID, sot.trust_id)
        self.assertEqual(common.TEST_TENANT_ID, sot.tenant_id)
        self.assertEqual(common.TEST_TENANT_NAME, sot.tenant_name)
        expected = {'passwordCredentials': {'password': common.TEST_PASS,
                                            'userId': common.TEST_USER_ID}}
        headers = {}
        self.assertEqual(expected, sot.get_auth_data(headers))
        self.assertEqual({}, headers)

    def create_mock_transport(self, xresp):
        transport = mock.Mock()
        transport.post = mock.Mock()
        response = mock.Mock()
        response.json = mock.Mock()
        response.json.return_value = xresp
        transport.post.return_value = response
        return transport

    def test_authorize_tenant_id(self):
        kargs = {
            'project_id': common.TEST_TENANT_ID,
            'project_name': common.TEST_TENANT_NAME,
            'token': common.TEST_TOKEN,
            'trust_id': common.TEST_TRUST_ID,
        }
        sot = v2.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(TEST_RESPONSE_DICT)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        ejson = {'auth': {'token': {'id': common.TEST_TOKEN},
                          'trust_id': common.TEST_TRUST_ID,
                          'tenantId': common.TEST_TENANT_ID}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = TEST_RESPONSE_DICT['access'].copy()
        ecatalog['version'] = 'v2.0'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_tenant_name(self):
        kargs = {
            'project_name': common.TEST_TENANT_NAME,
            'token': common.TEST_TOKEN,
        }
        sot = v2.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(TEST_RESPONSE_DICT)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        ejson = {'auth': {'token': {'id': common.TEST_TOKEN},
                          'tenantName': common.TEST_TENANT_NAME}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = TEST_RESPONSE_DICT['access'].copy()
        ecatalog['version'] = 'v2.0'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_token_only(self):
        kargs = {'token': common.TEST_TOKEN}
        sot = v2.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(TEST_RESPONSE_DICT)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        ejson = {'auth': {'token': {'id': common.TEST_TOKEN}}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = TEST_RESPONSE_DICT['access'].copy()
        ecatalog['version'] = 'v2.0'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_token_access_info(self):
        ecatalog = TEST_RESPONSE_DICT['access'].copy()
        ecatalog['version'] = 'v2.0'
        kargs = {
            'access_info': ecatalog,
            'token': common.TEST_TOKEN,
        }
        sot = v2.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(TEST_RESPONSE_DICT)

        resp = sot.authorize(xport)

        self.assertEqual(ecatalog, resp._info)

    def test_authorize_bad_response(self):
        kargs = {'token': common.TEST_TOKEN}
        sot = v2.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport({})

        self.assertRaises(exceptions.InvalidResponse, sot.authorize, xport)

    def test_invalidate(self):
        kargs = {
            'access_info': {'a': 'b'},
            'password': common.TEST_PASS,
            'token': common.TEST_TOKEN,
            'user_name': common.TEST_USER,
        }
        sot = v2.Auth(TEST_URL, **kargs)
        expected = {'token': {'id': common.TEST_TOKEN}}
        headers = {}
        self.assertEqual(expected, sot.get_auth_data(headers))
        self.assertEqual({'X-Auth-Token': common.TEST_TOKEN}, headers)

        self.assertEqual(True, sot.invalidate())

        expected = {'passwordCredentials': {'password': common.TEST_PASS,
                                            'username': common.TEST_USER}}
        headers = {}
        self.assertEqual(None, sot.token)
        self.assertEqual(None, sot.access_info)
        self.assertEqual(expected, sot.get_auth_data(headers))
        self.assertEqual({}, headers)

    def test_valid_options(self):
        expected = [
            'access_info',
            'auth_url',
            'user_name',
            'user_id',
            'password',
            'project_id',
            'project_name',
            'reauthenticate',
            'token',
            'trust_id',
        ]
        self.assertEqual(expected, v2.Auth.valid_options)
