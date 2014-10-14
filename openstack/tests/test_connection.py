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

from openstack import connection
from openstack import exceptions
from openstack.tests import base


class TestConnection(base.TestCase):
    def test_create_transport(self):
        conn = connection.Connection(authenticator='2', verify=True,
                                     user_agent='1')
        self.assertTrue(conn.transport.verify)
        self.assertEqual('1', conn.transport._user_agent)

    def test_create_authenticator_v2(self):
        auth_args = {
            'auth_url': '0',
            'user_name': '1',
            'password': '2',
        }
        conn = connection.Connection(transport='0', auth_plugin='identity_v2',
                                     **auth_args)
        self.assertEqual('0', conn.authenticator.auth_url)
        self.assertEqual('1', conn.authenticator.user_name)
        self.assertEqual('2', conn.authenticator.password)

    def test_create_authenticator_v3(self):
        auth_args = {
            'auth_url': '0',
            'user_name': '1',
            'password': '2',
        }
        conn = connection.Connection(transport='0', auth_plugin='identity_v3',
                                     **auth_args)
        self.assertEqual('0', conn.authenticator.auth_url)
        self.assertEqual('1', conn.authenticator.password_method.user_name)
        self.assertEqual('2', conn.authenticator.password_method.password)

    def test_create_authenticator_no_name_2(self):
        auth_args = {
            'auth_url': 'http://localhost/v2',
            'user_name': '1',
            'password': '2',
        }
        conn = connection.Connection(transport='0', **auth_args)
        self.assertEqual('openstack.auth.identity.v2',
                         conn.authenticator.__class__.__module__)

    def test_create_authenticator_no_name_3(self):
        auth_args = {
            'auth_url': 'http://localhost/v3',
            'user_name': '1',
            'password': '2',
        }
        conn = connection.Connection(transport='0', **auth_args)
        self.assertEqual('openstack.auth.identity.v3',
                         conn.authenticator.__class__.__module__)

    def test_create_authenticator_no_nothing(self):
        self.assertRaises(
            exceptions.AuthorizationFailure,
            connection.Connection,
        )

    def test_create_session(self):
        args = {'transport': '0', 'authenticator': '1', 'preference': '2'}
        conn = connection.Connection(**args)
        self.assertEqual('0', conn.session.transport)
        self.assertEqual('1', conn.session.authenticator)
        self.assertEqual('2', conn.session.preference)
