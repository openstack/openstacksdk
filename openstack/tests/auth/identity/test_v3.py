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

from openstack.auth.identity import v3
from openstack import exceptions
from openstack.tests.auth import common

TEST_URL = 'http://127.0.0.1:5000/v3.0'


class TestV3Auth(testtools.TestCase):

    def test_missing_args(self):
        with testtools.ExpectedException(exceptions.AuthorizationFailure):
            v3.Auth(TEST_URL)

    def test_password_user_domain(self):
        kargs = {
            'trust_id': common.TEST_TRUST_ID,
            'project_id': common.TEST_PROJECT_ID,
            'project_name': common.TEST_PROJECT_NAME,
            'user_name': common.TEST_USER,
            'user_id': common.TEST_USER_ID,
            'user_domain_id': common.TEST_DOMAIN_ID,
            'user_domain_name': common.TEST_DOMAIN_NAME,
            'password': common.TEST_PASS,
        }
        sot = v3.Auth(TEST_URL, **kargs)

        self.assertEqual(1, len(sot.auth_methods))
        auther = sot.auth_methods[0]
        self.assertEqual(common.TEST_USER_ID, auther.user_id)
        self.assertEqual(common.TEST_USER, auther.user_name)
        self.assertEqual(common.TEST_DOMAIN_ID, auther.user_domain_id)
        self.assertEqual(common.TEST_DOMAIN_NAME, auther.user_domain_name)
        self.assertEqual(common.TEST_PASS, auther.password)
        expected = ('password', {'user': {'id': common.TEST_USER_ID,
                                          'password': common.TEST_PASS}})
        self.assertEqual(expected, auther.get_auth_data(None, None, {}))
        self.assertEqual(common.TEST_TRUST_ID, sot.trust_id)
        self.assertEqual(None, sot.domain_id)
        self.assertEqual(None, sot.domain_name)
        self.assertEqual(common.TEST_PROJECT_ID, sot.project_id)
        self.assertEqual(common.TEST_PROJECT_NAME, sot.project_name)
        self.assertEqual(None, sot.project_domain_id)
        self.assertEqual(None, sot.project_domain_name)
        self.assertEqual(TEST_URL + '/auth/tokens', sot.token_url)

    def test_password_domain(self):
        kargs = {
            'domain_id': common.TEST_DOMAIN_ID,
            'domain_name': common.TEST_DOMAIN_NAME,
            'trust_id': common.TEST_TRUST_ID,
            'project_id': common.TEST_PROJECT_ID,
            'project_name': common.TEST_PROJECT_NAME,
            'user_name': common.TEST_USER,
            'user_id': common.TEST_USER_ID,
            'password': common.TEST_PASS,
        }
        sot = v3.Auth(TEST_URL, **kargs)

        self.assertEqual(1, len(sot.auth_methods))
        auther = sot.auth_methods[0]
        self.assertEqual(common.TEST_USER_ID, auther.user_id)
        self.assertEqual(common.TEST_USER, auther.user_name)
        self.assertEqual(None, auther.user_domain_id)
        self.assertEqual(None, auther.user_domain_name)
        self.assertEqual(common.TEST_PASS, auther.password)
        expected = ('password', {'user': {'id': common.TEST_USER_ID,
                                          'password': common.TEST_PASS}})
        self.assertEqual(expected, auther.get_auth_data(None, None, {}))
        self.assertEqual(common.TEST_TRUST_ID, sot.trust_id)
        self.assertEqual(common.TEST_DOMAIN_ID, sot.domain_id)
        self.assertEqual(common.TEST_DOMAIN_NAME, sot.domain_name)
        self.assertEqual(common.TEST_PROJECT_ID, sot.project_id)
        self.assertEqual(common.TEST_PROJECT_NAME, sot.project_name)
        self.assertEqual(None, sot.project_domain_id)
        self.assertEqual(None, sot.project_domain_name)
        self.assertEqual(TEST_URL + '/auth/tokens', sot.token_url)

    def test_token_project_domain(self):
        kargs = {
            'project_domain_id': common.TEST_DOMAIN_ID,
            'project_domain_name': common.TEST_DOMAIN_NAME,
            'trust_id': common.TEST_TRUST_ID,
            'project_id': common.TEST_PROJECT_ID,
            'project_name': common.TEST_PROJECT_NAME,
            'token': common.TEST_TOKEN,
        }
        sot = v3.Auth(TEST_URL, **kargs)

        self.assertEqual(1, len(sot.auth_methods))
        auther = sot.auth_methods[0]
        self.assertEqual(common.TEST_TOKEN, auther.token)
        expected = ('token', {'id': common.TEST_TOKEN})
        self.assertEqual(expected, auther.get_auth_data(None, None, {}))
        self.assertEqual(common.TEST_TRUST_ID, sot.trust_id)
        self.assertEqual(None, sot.domain_id)
        self.assertEqual(None, sot.domain_name)
        self.assertEqual(common.TEST_PROJECT_ID, sot.project_id)
        self.assertEqual(common.TEST_PROJECT_NAME, sot.project_name)
        self.assertEqual(common.TEST_DOMAIN_ID, sot.project_domain_id)
        self.assertEqual(common.TEST_DOMAIN_NAME, sot.project_domain_name)
        self.assertEqual(TEST_URL + '/auth/tokens', sot.token_url)

    def create_mock_transport(self, xresp):
        transport = mock.Mock()
        transport.post = mock.Mock()
        response = mock.Mock()
        response.json = mock.Mock()
        response.json.return_value = xresp
        response.headers = {'X-Subject-Token': common.TEST_SUBJECT}
        transport.post.return_value = response
        return transport

    def test_authorize_token(self):
        kargs = {'token': common.TEST_TOKEN}
        sot = v3.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(common.TEST_RESPONSE_DICT_V3)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/auth/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        ejson = {'auth': {'identity': {'token': {'id': common.TEST_TOKEN},
                          'methods': ['token']}}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = common.TEST_RESPONSE_DICT_V3['token'].copy()
        ecatalog['auth_token'] = common.TEST_SUBJECT
        ecatalog['version'] = 'v3'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_token_access_info(self):
        ecatalog = common.TEST_RESPONSE_DICT_V3['token'].copy()
        kargs = {
            'access_info': ecatalog,
            'token': common.TEST_TOKEN,
        }
        sot = v3.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(common.TEST_RESPONSE_DICT_V3)

        resp = sot.authorize(xport)

        ecatalog['auth_token'] = common.TEST_TOKEN
        ecatalog['version'] = 'v3'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_token_domain_id(self):
        kargs = {
            'domain_id': common.TEST_DOMAIN_ID,
            'token': common.TEST_TOKEN,
        }
        sot = v3.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(common.TEST_RESPONSE_DICT_V3)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/auth/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        ejson = {'auth': {'identity': {'token': {'id': common.TEST_TOKEN},
                          'methods': ['token']},
                          'scope': {'domain': {'id': common.TEST_DOMAIN_ID}}}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = common.TEST_RESPONSE_DICT_V3['token'].copy()
        ecatalog['auth_token'] = common.TEST_SUBJECT
        ecatalog['version'] = 'v3'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_token_domain_name(self):
        kargs = {
            'domain_name': common.TEST_DOMAIN_NAME,
            'token': common.TEST_TOKEN,
        }
        sot = v3.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(common.TEST_RESPONSE_DICT_V3)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/auth/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        scope = {'domain': {'name': common.TEST_DOMAIN_NAME}}
        ejson = {'auth': {'identity': {'token': {'id': common.TEST_TOKEN},
                          'methods': ['token']},
                          'scope': scope}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = common.TEST_RESPONSE_DICT_V3['token'].copy()
        ecatalog['auth_token'] = common.TEST_SUBJECT
        ecatalog['version'] = 'v3'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_token_project_id(self):
        kargs = {
            'project_id': common.TEST_PROJECT_ID,
            'token': common.TEST_TOKEN,
        }
        sot = v3.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(common.TEST_RESPONSE_DICT_V3)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/auth/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        scope = {'project': {'id': common.TEST_PROJECT_ID}}
        ejson = {'auth': {'identity': {'token': {'id': common.TEST_TOKEN},
                          'methods': ['token']},
                          'scope': scope}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = common.TEST_RESPONSE_DICT_V3['token'].copy()
        ecatalog['auth_token'] = common.TEST_SUBJECT
        ecatalog['version'] = 'v3'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_token_project_name(self):
        kargs = {
            'project_name': common.TEST_PROJECT_NAME,
            'project_domain_id': common.TEST_DOMAIN_ID,
            'token': common.TEST_TOKEN,
        }
        sot = v3.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(common.TEST_RESPONSE_DICT_V3)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/auth/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        domain = {'domain': {'id': common.TEST_DOMAIN_ID},
                  'name': common.TEST_PROJECT_NAME}
        scope = {'project': domain}
        ejson = {'auth': {'identity': {'methods': ['token'],
                                       'token': {'id': common.TEST_TOKEN}},
                          'scope': scope}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = common.TEST_RESPONSE_DICT_V3['token'].copy()
        ecatalog['auth_token'] = common.TEST_SUBJECT
        ecatalog['version'] = 'v3'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_token_project_name_domain_name(self):
        kargs = {
            'project_name': common.TEST_PROJECT_NAME,
            'project_domain_name': common.TEST_DOMAIN_NAME,
            'token': common.TEST_TOKEN,
        }
        sot = v3.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(common.TEST_RESPONSE_DICT_V3)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/auth/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        domain = {'domain': {'name': common.TEST_DOMAIN_NAME},
                  'name': common.TEST_PROJECT_NAME}
        scope = {'project': domain}
        ejson = {'auth': {'identity': {'methods': ['token'],
                                       'token': {'id': common.TEST_TOKEN}},
                          'scope': scope}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = common.TEST_RESPONSE_DICT_V3['token'].copy()
        ecatalog['auth_token'] = common.TEST_SUBJECT
        ecatalog['version'] = 'v3'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_token_trust_id(self):
        kargs = {
            'token': common.TEST_TOKEN,
            'trust_id': common.TEST_TRUST_ID,
        }
        sot = v3.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport(common.TEST_RESPONSE_DICT_V3)

        resp = sot.authorize(xport)

        eurl = TEST_URL + '/auth/tokens'
        eheaders = {'Accept': 'application/json',
                    'X-Auth-Token': common.TEST_TOKEN}
        scope = {'OS-TRUST:trust': {'id': common.TEST_TRUST_ID}}
        ejson = {'auth': {'identity': {'token': {'id': common.TEST_TOKEN},
                          'methods': ['token']},
                          'scope': scope}}
        xport.post.assert_called_with(eurl, headers=eheaders, json=ejson)
        ecatalog = common.TEST_RESPONSE_DICT_V3['token'].copy()
        ecatalog['auth_token'] = common.TEST_SUBJECT
        ecatalog['version'] = 'v3'
        self.assertEqual(ecatalog, resp._info)

    def test_authorize_mutually_exclusive(self):
        x = self.create_mock_transport(common.TEST_RESPONSE_DICT_V3)
        kargs = {'token': common.TEST_TOKEN}

        sot = v3.Auth(TEST_URL, **kargs)
        sot.domain_id = 'a'
        sot.project_id = 'b'
        self.assertRaises(exceptions.AuthorizationFailure, sot.authorize, x)

        sot = v3.Auth(TEST_URL, **kargs)
        sot.domain_name = 'a'
        sot.project_name = 'b'
        self.assertRaises(exceptions.AuthorizationFailure, sot.authorize, x)

        sot = v3.Auth(TEST_URL, **kargs)
        sot.domain_name = 'a'
        sot.trust_id = 'b'
        self.assertRaises(exceptions.AuthorizationFailure, sot.authorize, x)

        sot = v3.Auth(TEST_URL, **kargs)
        sot.project_id = 'a'
        sot.trust_id = 'b'
        self.assertRaises(exceptions.AuthorizationFailure, sot.authorize, x)

    def test_authorize_bad_response(self):
        kargs = {'token': common.TEST_TOKEN}
        sot = v3.Auth(TEST_URL, **kargs)
        xport = self.create_mock_transport({})

        self.assertRaises(exceptions.InvalidResponse, sot.authorize, xport)

    def test_invalidate(self):
        kargs = {
            'user_name': common.TEST_USER,
            'password': common.TEST_PASS,
            'token': common.TEST_TOKEN,
            'access_info': {},
        }
        sot = v3.Auth(TEST_URL, **kargs)
        self.assertEqual(1, len(sot.auth_methods))
        auther = sot.auth_methods[0]
        self.assertEqual(common.TEST_TOKEN, auther.token)

        self.assertEqual(True, sot.invalidate())

        self.assertEqual(None, sot.access_info)
        self.assertEqual(1, len(sot.auth_methods))
        auther = sot.auth_methods[0]
        self.assertEqual(common.TEST_USER, auther.user_name)
        self.assertEqual(common.TEST_PASS, auther.password)

    def test_valid_options(self):
        expected = [
            'access_info',
            'auth_url',
            'domain_id',
            'domain_name',
            'password',
            'project_domain_id',
            'project_domain_name',
            'project_id',
            'project_name',
            'reauthenticate',
            'token',
            'trust_id',
            'user_domain_id',
            'user_domain_name',
            'user_id',
            'user_name',
        ]
        self.assertEqual(expected, v3.Auth.valid_options)
