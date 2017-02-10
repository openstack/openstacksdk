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

import collections
import uuid

import testtools

import shade
from shade.tests.unit import base


_UserData = collections.namedtuple(
    'UserData',
    'user_id, password, name, email, description, domain_id, enabled, '
    'json_response, json_request')


_GroupData = collections.namedtuple(
    'GroupData',
    'group_id, group_name, domain_id, description, json_response')


class TestUsers(base.RequestsMockTestCase):

    def _get_mock_url(self, v3=False, append=None, resource='users',
                      interface='admin'):
        service_catalog = self.cloud.keystone_session.auth.get_access(
            self.cloud.keystone_session).service_catalog
        endpoint_url = service_catalog.url_for(
            service_type='identity',
            interface=interface)
        to_join = [endpoint_url, resource]
        if v3:
            to_join.insert(1, 'v3')
        to_join.extend(append or [])
        return '/'.join(to_join)

    def _get_group_data(self, name=None, domain_id=None, description=None):
        group_id = uuid.uuid4().hex
        name or self.getUniqueString('groupname')
        domain_id = uuid.UUID(domain_id or uuid.uuid4().hex).hex
        response = {'id': group_id, 'name': name, 'domain_id': domain_id}
        if description is not None:
            response['description'] = description

        return _GroupData(group_id, name, domain_id, description,
                          {'group': response})

    def _get_user_data(self, name=None, password=None, **kwargs):

        name = name or self.getUniqueString('username')
        password = password or self.getUniqueString('user_password')
        user_id = uuid.uuid4().hex

        response = {'name': name, 'id': user_id}
        request = {'name': name, 'password': password, 'tenantId': None}

        if kwargs.get('domain_id'):
            kwargs['domain_id'] = uuid.UUID(kwargs['domain_id']).hex
            response['domain_id'] = kwargs.pop('domain_id')

        response['email'] = kwargs.pop('email', None)
        request['email'] = response['email']

        response['enabled'] = kwargs.pop('enabled', True)
        request['enabled'] = response['enabled']

        response['description'] = kwargs.pop('description', None)
        if response['description']:
            request['description'] = response['description']

        self.assertIs(0, len(kwargs), message='extra key-word args received '
                                              'on _get_user_data')

        return _UserData(user_id, password, name, response['email'],
                         response['description'], response.get('domain_id'),
                         response.get('enabled'), {'user': response},
                         {'user': request})

    def test_create_user_v2(self):
        self.use_keystone_v2()

        user_data = self._get_user_data()

        self.register_uri('POST', self._get_mock_url(), status_code=204,
                          json=user_data.json_response,
                          validate=dict(json=user_data.json_request))
        self.register_uri('GET',
                          self._get_mock_url(append=[user_data.user_id]),
                          status_code=200, json=user_data.json_response)
        user = self.op_cloud.create_user(
            name=user_data.name, email=user_data.email,
            password=user_data.password)

        self.assertEqual(user_data.name, user.name)
        self.assertEqual(user_data.email, user.email)
        self.assertEqual(user_data.user_id, user.id)
        self.assert_calls()

    def test_create_user_v3(self):
        self._add_discovery_uri_call()
        user_data = self._get_user_data(
            domain_id=uuid.uuid4().hex,
            description=self.getUniqueString('description'))
        self.register_uri(
            'POST',
            self._get_mock_url(v3=True), status_code=204,
            json=user_data.json_response,
            validate=user_data.json_request)
        self.register_uri(
            'GET',
            self._get_mock_url(v3=True, append=[user_data.user_id]),
            status_code=200, json=user_data.json_response)
        user = self.op_cloud.create_user(
            name=user_data.name, email=user_data.email,
            password=user_data.password,
            description=user_data.description,
            domain_id=user_data.domain_id)

        self.assertEqual(user_data.name, user.name)
        self.assertEqual(user_data.email, user.email)
        self.assertEqual(user_data.description, user.description)
        self.assertEqual(user_data.user_id, user.id)
        self.assert_calls()

    def test_update_user_password_v2(self):
        self.use_keystone_v2()
        user_data = self._get_user_data(email='test@example.com')
        self.register_uri('GET', self._get_mock_url(), status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri('GET',
                          self._get_mock_url(append=[user_data.user_id]),
                          json=user_data.json_response)
        self.register_uri(
            'PUT',
            self._get_mock_url(
                append=[user_data.user_id, 'OS-KSADM', 'password']),
            status_code=204, json=user_data.json_response,
            validate=dict(json={'user': {'password': user_data.password}}))
        self.register_uri('GET',
                          self._get_mock_url(append=[user_data.user_id]),
                          json=user_data.json_response)
        # NOTE(notmorgan): when keystoneclient is dropped, the extra call is
        # not needed as it is a blank put. Keystoneclient has very limited
        # logic and does odd things when updates inclue passwords in v2
        # keystone.
        self.register_uri(
            'PUT',
            self._get_mock_url(append=[user_data.user_id]),
            status_code=204, json=user_data.json_response,
            validate=dict(json={'user': {}}))
        self.register_uri('GET',
                          self._get_mock_url(append=[user_data.user_id]),
                          json=user_data.json_response)
        user = self.op_cloud.update_user(
            user_data.user_id, password=user_data.password)
        self.assertEqual(user_data.name, user.name)
        self.assertEqual(user_data.email, user.email)
        self.assert_calls()

    def test_create_user_v3_no_domain(self):
        user_data = self._get_user_data(domain_id=uuid.uuid4().hex,
                                        email='test@example.com')
        with testtools.ExpectedException(
                shade.OpenStackCloudException,
                "User or project creation requires an explicit"
                " domain_id argument."
        ):
            self.op_cloud.create_user(
                name=user_data.name, email=user_data.email,
                password=user_data.password)

    def test_delete_user(self):
        self._add_discovery_uri_call()
        user_data = self._get_user_data(domain_id=uuid.uuid4().hex)
        self.register_uri('GET', self._get_mock_url(v3=True), status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri('GET',
                          self._get_mock_url(v3=True,
                                             append=[user_data.user_id]),
                          status_code=200, json=user_data.json_response)
        self.register_uri('DELETE',
                          self._get_mock_url(v3=True,
                                             append=[user_data.user_id]),
                          status_code=204)
        self.op_cloud.delete_user(user_data.name)
        self.assert_calls()

    def test_delete_user_not_found(self):
        self._add_discovery_uri_call()
        self.register_uri('GET',
                          self._get_mock_url(v3=True),
                          status_code=200,
                          json={'users': []})
        self.assertFalse(self.op_cloud.delete_user(self.getUniqueString()))

    def test_add_user_to_group(self):
        self._add_discovery_uri_call()
        user_data = self._get_user_data()
        group_data = self._get_group_data()
        self.register_uri('GET',
                          self._get_mock_url(v3=True),
                          status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri(
            'GET',
            self._get_mock_url(v3=True, resource='groups'),
            status_code=200,
            json={'groups': [group_data.json_response['group']]})
        self.register_uri(
            'PUT',
            self._get_mock_url(
                v3=True, resource='groups',
                append=[group_data.group_id, 'users', user_data.user_id]),
            status_code=200)
        self.op_cloud.add_user_to_group(user_data.user_id, group_data.group_id)
        self.assert_calls()

    def test_is_user_in_group(self):
        self._add_discovery_uri_call()
        user_data = self._get_user_data()
        group_data = self._get_group_data()
        self.register_uri('GET',
                          self._get_mock_url(v3=True),
                          status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri(
            'GET',
            self._get_mock_url(v3=True, resource='groups'),
            status_code=200,
            json={'groups': [group_data.json_response['group']]})
        self.register_uri(
            'HEAD',
            self._get_mock_url(
                v3=True, resource='groups',
                append=[group_data.group_id, 'users', user_data.user_id]),
            status_code=204)
        self.assertTrue(self.op_cloud.is_user_in_group(
            user_data.user_id, group_data.group_id))
        self.assert_calls()

    def test_remove_user_from_group(self):
        self._add_discovery_uri_call()
        user_data = self._get_user_data()
        group_data = self._get_group_data()
        self.register_uri('GET',
                          self._get_mock_url(v3=True),
                          status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri(
            'GET',
            self._get_mock_url(v3=True, resource='groups'),
            status_code=200,
            json={'groups': [group_data.json_response['group']]})
        self.register_uri(
            'DELETE',
            self._get_mock_url(
                v3=True, resource='groups',
                append=[group_data.group_id, 'users', user_data.user_id]),
            status_code=204)
        self.op_cloud.remove_user_from_group(user_data.user_id,
                                             group_data.group_id)
        self.assert_calls()
