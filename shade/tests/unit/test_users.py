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

import uuid

import testtools

import shade
from shade.tests.unit import base


class TestUsers(base.RequestsMockTestCase):

    def _get_keystone_mock_url(self, resource, append=None, v3=True):
        base_url_append = None
        if v3:
            base_url_append = 'v3'
        return self.get_mock_url(
            service_type='identity', interface='admin', resource=resource,
            append=append, base_url_append=base_url_append)

    def test_create_user_v2(self):
        self.use_keystone_v2()

        user_data = self._get_user_data()

        self.register_uri('POST',
                          self._get_keystone_mock_url(resource='users',
                                                      v3=False),
                          status_code=204,
                          json=user_data.json_response,
                          validate=dict(json=user_data.json_request))
        self.register_uri('GET',
                          self._get_keystone_mock_url(
                              resource='users',
                              append=[user_data.user_id],
                              v3=False),
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
            self._get_keystone_mock_url(resource='users'),
            status_code=204,
            json=user_data.json_response,
            validate=user_data.json_request)
        self.register_uri(
            'GET',
            self._get_keystone_mock_url(resource='users',
                                        append=[user_data.user_id]),
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
        self.register_uri('GET',
                          self._get_keystone_mock_url(resource='users',
                                                      v3=False),
                          status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri('GET',
                          self._get_keystone_mock_url(
                              resource='users',
                              v3=False,
                              append=[user_data.user_id]),
                          json=user_data.json_response)
        self.register_uri(
            'PUT',
            self._get_keystone_mock_url(
                resource='users', v3=False,
                append=[user_data.user_id, 'OS-KSADM', 'password']),
            status_code=204, json=user_data.json_response,
            validate=dict(json={'user': {'password': user_data.password}}))
        self.register_uri('GET',
                          self._get_keystone_mock_url(
                              resource='users', v3=False,
                              append=[user_data.user_id]),
                          json=user_data.json_response)
        # NOTE(notmorgan): when keystoneclient is dropped, the extra call is
        # not needed as it is a blank put. Keystoneclient has very limited
        # logic and does odd things when updates inclue passwords in v2
        # keystone.
        self.register_uri(
            'PUT',
            self._get_keystone_mock_url(resource='users',
                                        append=[user_data.user_id],
                                        v3=False),
            status_code=204, json=user_data.json_response,
            validate=dict(json={'user': {}}))
        self.register_uri('GET',
                          self._get_keystone_mock_url(
                              resource='users',
                              v3=False,
                              append=[user_data.user_id]),
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
        self.register_uri('GET', self._get_keystone_mock_url(resource='users'),
                          status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri('GET',
                          self._get_keystone_mock_url(
                              resource='users', append=[user_data.user_id]),
                          status_code=200, json=user_data.json_response)
        self.register_uri('DELETE',
                          self._get_keystone_mock_url(
                              resource='users', append=[user_data.user_id]),
                          status_code=204)
        self.op_cloud.delete_user(user_data.name)
        self.assert_calls()

    def test_delete_user_not_found(self):
        self._add_discovery_uri_call()
        self.register_uri('GET',
                          self._get_keystone_mock_url(resource='users'),
                          status_code=200,
                          json={'users': []})
        self.assertFalse(self.op_cloud.delete_user(self.getUniqueString()))

    def test_add_user_to_group(self):
        self._add_discovery_uri_call()
        user_data = self._get_user_data()
        group_data = self._get_group_data()
        self.register_uri('GET',
                          self._get_keystone_mock_url(resource='users'),
                          status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri(
            'GET',
            self._get_keystone_mock_url(resource='groups'),
            status_code=200,
            json={'groups': [group_data.json_response['group']]})
        self.register_uri(
            'PUT',
            self._get_keystone_mock_url(
                resource='groups',
                append=[group_data.group_id, 'users', user_data.user_id]),
            status_code=200)
        self.op_cloud.add_user_to_group(user_data.user_id, group_data.group_id)
        self.assert_calls()

    def test_is_user_in_group(self):
        self._add_discovery_uri_call()
        user_data = self._get_user_data()
        group_data = self._get_group_data()
        self.register_uri('GET',
                          self._get_keystone_mock_url(resource='users'),
                          status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri(
            'GET',
            self._get_keystone_mock_url(resource='groups'),
            status_code=200,
            json={'groups': [group_data.json_response['group']]})
        self.register_uri(
            'HEAD',
            self._get_keystone_mock_url(
                resource='groups',
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
                          self._get_keystone_mock_url(resource='users'),
                          status_code=200,
                          json={'users': [user_data.json_response['user']]})
        self.register_uri(
            'GET',
            self._get_keystone_mock_url(resource='groups'),
            status_code=200,
            json={'groups': [group_data.json_response['group']]})
        self.register_uri(
            'DELETE',
            self._get_keystone_mock_url(
                resource='groups',
                append=[group_data.group_id, 'users', user_data.user_id]),
            status_code=204)
        self.op_cloud.remove_user_from_group(user_data.user_id,
                                             group_data.group_id)
        self.assert_calls()
