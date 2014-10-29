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

from openstack.auth.identity import v2
from openstack import connection
from openstack import exceptions
from openstack.tests import base
from openstack import transport
from openstack import user_preference


class TestConnection(base.TestCase):
    def setUp(self):
        super(TestConnection, self).setUp()
        self.xport = transport.Transport()
        self.auth = v2.Auth(auth_url='http://127.0.0.1/v2', token='b')
        self.pref = user_preference.UserPreference()

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
        args = {
            'transport': self.xport,
            'authenticator': self.auth,
            'preference': self.pref,
        }
        conn = connection.Connection(**args)
        self.assertEqual(self.xport, conn.session.transport)
        self.assertEqual(self.auth, conn.session.authenticator)
        self.assertEqual(self.pref, conn.session.preference)
        self.assertEqual('openstack.compute.v2._proxy',
                         conn.compute.__class__.__module__)
        self.assertEqual('openstack.database.v1._proxy',
                         conn.database.__class__.__module__)
        self.assertEqual('openstack.identity.v3._proxy',
                         conn.identity.__class__.__module__)
        self.assertEqual('openstack.image.v1._proxy',
                         conn.image.__class__.__module__)
        self.assertEqual('openstack.network.v2._proxy',
                         conn.network.__class__.__module__)
        self.assertEqual('openstack.object_store.v1._proxy',
                         conn.object_store.__class__.__module__)
        self.assertEqual('openstack.orchestration.v1._proxy',
                         conn.orchestration.__class__.__module__)
        self.assertEqual('openstack.telemetry.v2._proxy',
                         conn.telemetry.__class__.__module__)
