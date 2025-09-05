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

from openstack import exceptions
from openstack.identity.v3 import token
from openstack.tests.unit import base

IDENTIFIER = 'IDENTIFIER'
TOKEN_DATA = {
    'audit_ids': ['VcxU2JEMTjufVx7sVk7bPw'],
    'catalog': [
        {
            'endpoints': [
                {
                    'id': '068d1b359ee84b438266cb736d81de97',
                    'interface': 'public',
                    'region': 'RegionOne',
                    'region_id': 'RegionOne',
                    'url': 'http://example.com/v2.1',
                }
            ],
            'id': '050726f278654128aba89757ae25950c',
            'name': 'nova',
            'type': 'compute',
        }
    ],
    'domain': {'id': 'default', 'name': 'Default'},
    'expires_at': '2013-02-27T18:30:59.999999Z',
    'issued_at': '2013-02-27T16:30:59.999999Z',
    'methods': ['password'],
    'project': {
        'domain': {'id': 'default', 'name': 'Default'},
        'id': '8538a3f13f9541b28c2620eb19065e45',
        'name': 'admin',
    },
    'roles': [{'id': 'c703057be878458588961ce9a0ce686b', 'name': 'admin'}],
    'system': {'all': True},
    'user': {
        'domain': {'id': 'default', 'name': 'Default'},
        'id': '10a2e6e717a245d9acad3e5f97aeca3d',
        'name': 'admin',
        'password_expires_at': None,
    },
    'is_domain': False,
}

EXAMPLE = {'token': TOKEN_DATA}


class TestToken(base.TestCase):
    def setUp(self):
        super().setUp()
        self.session = mock.Mock(spec=adapter.Adapter)

    def test_basic(self):
        sot = token.Token()
        self.assertEqual('token', sot.resource_key)
        self.assertEqual('/auth/tokens', sot.base_path)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.allow_head)

    def test_make_it(self):
        sot = token.Token(**TOKEN_DATA)
        self.assertEqual(TOKEN_DATA['audit_ids'], sot.audit_ids)
        self.assertEqual(TOKEN_DATA['catalog'], sot.catalog)
        self.assertEqual(TOKEN_DATA['expires_at'], sot.expires_at)
        self.assertEqual(TOKEN_DATA['issued_at'], sot.issued_at)
        self.assertEqual(TOKEN_DATA['methods'], sot.methods)
        self.assertEqual(TOKEN_DATA['user'], sot.user)
        self.assertEqual(TOKEN_DATA['project'], sot.project)
        self.assertEqual(TOKEN_DATA['domain'], sot.domain)
        self.assertEqual(TOKEN_DATA['is_domain'], sot.is_domain)
        self.assertEqual(TOKEN_DATA['system'], sot.system)
        self.assertEqual(TOKEN_DATA['roles'], sot.roles)

    def test_validate(self):
        response = mock.Mock()
        response.status_code = 200
        response.json.return_value = EXAMPLE
        response.headers = {'content-type': 'application/json'}
        self.session.get.return_value = response

        result = token.Token.validate(self.session, 'token')

        self.session.get.assert_called_once_with(
            '/auth/tokens', headers={'x-subject-token': 'token'}, params={}
        )
        self.assertIsInstance(result, token.Token)

    def test_validate_with_params(self):
        response = mock.Mock()
        response.status_code = 200
        response.json.return_value = EXAMPLE
        response.headers = {'content-type': 'application/json'}
        self.session.get.return_value = response

        result = token.Token.validate(
            self.session, 'token', nocatalog=True, allow_expired=True
        )

        self.session.get.assert_called_once_with(
            '/auth/tokens',
            headers={'x-subject-token': 'token'},
            params={'nocatalog': True, 'allow_expired': True},
        )
        self.assertIsInstance(result, token.Token)

    def test_validate_error(self):
        response = mock.Mock()
        response.status_code = 404
        response.json.return_value = {}
        response.headers = {'content-type': 'application/json'}
        self.session.get.return_value = response

        self.assertRaises(
            exceptions.NotFoundException,
            token.Token.validate,
            self.session,
            'token',
        )

    def test_check(self):
        response = mock.Mock()
        response.status_code = 200
        self.session.head.return_value = response

        result = token.Token.check(self.session, 'token')

        self.session.head.assert_called_once_with(
            '/auth/tokens', headers={'x-subject-token': 'token'}, params={}
        )
        self.assertTrue(result)

    def test_check_with_param(self):
        response = mock.Mock()
        response.status_code = 200
        self.session.head.return_value = response

        result = token.Token.check(self.session, 'token', allow_expired=True)

        self.session.head.assert_called_once_with(
            '/auth/tokens',
            headers={'x-subject-token': 'token'},
            params={'allow_expired': True},
        )
        self.assertTrue(result)

    def test_check_invalid_token(self):
        response = mock.Mock()
        response.status_code = 404
        self.session.head.return_value = response

        result = token.Token.check(self.session, 'token')

        self.session.head.assert_called_once_with(
            '/auth/tokens', headers={'x-subject-token': 'token'}, params={}
        )
        self.assertFalse(result)

    def test_revoke(self):
        response = mock.Mock()
        response.status_code = 204
        self.session.delete.return_value = response

        token.Token.revoke(self.session, 'token')

        self.session.delete.assert_called_once_with(
            '/auth/tokens', headers={'x-subject-token': 'token'}
        )

    def test_revoke_error(self):
        response = mock.Mock()
        response.status_code = 404
        response.json.return_value = {}
        response.headers = {'content-type': 'application/json'}
        self.session.delete.return_value = response

        self.assertRaises(
            exceptions.NotFoundException,
            token.Token.revoke,
            self.session,
            'token',
        )
