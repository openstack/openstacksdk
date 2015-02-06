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

from openstack.auth.identity import v2
from openstack.auth import service_filter
from openstack import connection
from openstack import exceptions
from openstack import resource
from openstack.tests import base
from openstack import transport
from openstack import user_preference


class TestConnection(base.TestCase):
    def setUp(self):
        super(TestConnection, self).setUp()
        self.xport = transport.Transport()
        self.auth = v2.Auth(auth_url='http://127.0.0.1/v2', token='b')
        self.pref = user_preference.UserPreference()
        self.conn = connection.Connection(authenticator=mock.MagicMock(),
                                          transport=mock.MagicMock())
        self.conn.session = mock.MagicMock()

    def test_create_transport(self):
        conn = connection.Connection(authenticator='2', verify=True,
                                     user_agent='1')
        self.assertTrue(conn.transport.verify)
        self.assertIn('1', conn.transport._user_agent)

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

    def test_create_authenticator_discoverable(self):
        auth_args = {
            'auth_url': '0',
            'user_name': '1',
            'password': '2',
        }
        conn = connection.Connection(transport='0', auth_plugin='identity',
                                     **auth_args)
        self.assertEqual('0', conn.authenticator.auth_url)
        self.assertEqual(
            '1',
            conn.authenticator.auth_plugin.password_method.user_name)
        self.assertEqual(
            '2',
            conn.authenticator.auth_plugin.password_method.password)

    def test_create_authenticator_no_name(self):
        auth_args = {
            'auth_url': 'http://localhost/v2',
            'user_name': '1',
            'password': '2',
        }
        conn = connection.Connection(transport='0', **auth_args)
        self.assertEqual('openstack.auth.identity.discoverable',
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

    def test_custom_user_agent(self):
        user_agent = "MyProgram/1.0"
        conn = connection.Connection(authenticator=self.auth,
                                     user_agent=user_agent)
        self.assertTrue(conn.transport._user_agent.startswith(user_agent))


class TestService(service_filter.ServiceFilter):
    valid_versions = [service_filter.ValidVersion('v2')]

    def __init__(self):
        super(TestService, self).__init__(service_type='test')


class TestResource(resource.Resource):
    resource_key = "testable"
    resources_key = "testables"
    base_path = "/testables"
    service = TestService()
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True
    name = resource.prop('name')


class TestConnectionObjectMethods(base.TestCase):
    def setUp(self):
        super(TestConnectionObjectMethods, self).setUp()
        self.conn = connection.Connection(authenticator=mock.MagicMock(),
                                          transport=mock.MagicMock())
        self.conn.session = mock.MagicMock()
        self.args = {'name': 'fee', 'id': 'fie'}
        self.body = {'testable': self.args}
        self.response = mock.Mock
        self.response.body = self.body

    def test_obj_create(self):
        test = TestResource.existing(**self.args)
        self.conn.session.put = mock.MagicMock()
        self.conn.session.put.and_return = self.response
        self.assertEqual(test, self.conn.create(test))
        url = 'testables/fie'
        self.conn.session.put.assert_called_with(url, json=self.body,
                                                 service=test.service)

    def test_obj_get(self):
        test = TestResource.existing(**self.args)
        self.conn.session.get = mock.MagicMock()
        self.conn.session.get.and_return = self.response
        self.assertEqual(test, self.conn.get(test))
        url = 'testables/fie'
        self.conn.session.get.assert_called_with(url, service=test.service)

    def test_obj_head(self):
        test = TestResource.existing(**self.args)
        self.conn.session.head = mock.MagicMock()
        self.conn.session.head.and_return = self.response
        self.assertEqual(test, self.conn.head(test))
        url = 'testables/fie'
        self.conn.session.head.assert_called_with(url, service=test.service,
                                                  accept=None)

    def test_obj_update(self):
        test = TestResource.existing(**self.args)
        test['name'] = 'newname'
        self.body = {'testable': {'name': 'newname'}}
        self.conn.session.patch = mock.MagicMock()
        self.conn.session.patch.and_return = self.response
        self.assertEqual(test, self.conn.update(test))
        url = 'testables/fie'
        self.conn.session.patch.assert_called_with(url, json=self.body,
                                                   service=test.service)

    def test_obj_delete(self):
        test = TestResource.existing(**self.args)
        self.conn.session.delete = mock.MagicMock()
        self.conn.session.delete.and_return = self.response
        self.assertEqual(None, self.conn.delete(test))
        url = 'testables/fie'
        self.conn.session.delete.assert_called_with(url, service=test.service,
                                                    accept=None)
