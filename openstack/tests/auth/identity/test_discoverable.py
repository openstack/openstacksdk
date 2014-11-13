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

from openstack.auth.identity import discoverable
from openstack import exceptions
from openstack.tests.auth import common


class TestDiscoverableAuth(testtools.TestCase):
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
        self.assertEqual(expected, sorted(discoverable.Auth.valid_options))

    def test_create2(self):
        auth_args = {
            'auth_url': 'http://localhost/v2',
            'user_name': '1',
            'password': '2',
        }
        auth = discoverable.Auth(**auth_args)
        self.assertEqual('openstack.auth.identity.v2',
                         auth.auth_plugin.__class__.__module__)

    def test_create3(self):
        auth_args = {
            'auth_url': 'http://localhost/v3',
            'user_name': '1',
            'password': '2',
        }
        auth = discoverable.Auth(**auth_args)
        self.assertEqual('openstack.auth.identity.v3',
                         auth.auth_plugin.__class__.__module__)

    def test_create_who_knows(self):
        auth_args = {
            'auth_url': 'http://localhost:5000/',
            'user_name': '1',
            'password': '2',
        }
        auth = discoverable.Auth(**auth_args)
        self.assertEqual('openstack.auth.identity.v3',
                         auth.auth_plugin.__class__.__module__)

    def test_create_authenticator_no_nothing(self):
        self.assertRaises(
            exceptions.AuthorizationFailure,
            discoverable.Auth,
        )

    def test_methods(self):
        auth_args = {
            'auth_url': 'http://localhost:5000/',
            'user_name': '1',
            'password': '2',
        }
        auth = discoverable.Auth(**auth_args)
        self.assertEqual('http://localhost:5000/auth/tokens', auth.token_url)
        xport = mock.MagicMock()
        xport.post = mock.Mock()
        response = mock.Mock()
        response.json = mock.Mock()
        response.json.return_value = common.TEST_RESPONSE_DICT_V3
        response.headers = {'X-Subject-Token': common.TEST_SUBJECT}
        xport.post.return_value = response

        result = auth.authorize(xport)
        self.assertEqual(common.TEST_SUBJECT, result.auth_token)
        self.assertEqual(True, auth.invalidate())
