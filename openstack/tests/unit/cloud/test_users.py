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

import openstack.cloud
from openstack.tests.unit import base


class TestUsers(base.TestCase):

    def _get_keystone_mock_url(self, resource, append=None, v3=True):
        base_url_append = None
        if v3:
            base_url_append = 'v3'
        return self.get_mock_url(
            service_type='identity', interface='admin', resource=resource,
            append=append, base_url_append=base_url_append)

    def _get_user_list(self, user_data):
        uri = self._get_keystone_mock_url(resource='users')
        return {
            'users': [
                user_data.json_response['user'],
            ],
            'links': {
                'self': uri,
                'previous': None,
                'next': None,
            }
        }

    def test_create_user_v2(self):
        self.use_keystone_v2()

        user_data = self._get_user_data()

        self.register_uris([
            dict(method='POST',
                 uri=self._get_keystone_mock_url(resource='users', v3=False),
                 status_code=200,
                 json=user_data.json_response,
                 validate=dict(json=user_data.json_request)),
        ])

        user = self.cloud.create_user(
            name=user_data.name, email=user_data.email,
            password=user_data.password)

        self.assertEqual(user_data.name, user.name)
        self.assertEqual(user_data.email, user.email)
        self.assertEqual(user_data.user_id, user.id)
        self.assert_calls()

    def test_create_user_v3(self):
        user_data = self._get_user_data(
            domain_id=uuid.uuid4().hex,
            description=self.getUniqueString('description'))

        self.register_uris([
            dict(method='POST',
                 uri=self._get_keystone_mock_url(resource='users'),
                 status_code=200, json=user_data.json_response,
                 validate=dict(json=user_data.json_request)),
        ])

        user = self.cloud.create_user(
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
        mock_user_resource_uri = self._get_keystone_mock_url(
            resource='users', append=[user_data.user_id], v3=False)
        mock_users_uri = self._get_keystone_mock_url(
            resource='users', v3=False)

        self.register_uris([
            # GET list to find user id
            # PUT user with password update
            # PUT empty update (password change is different than update)
            #     but is always chained together [keystoneclient oddity]
            dict(method='GET', uri=mock_users_uri, status_code=200,
                 json=self._get_user_list(user_data)),
            dict(method='PUT',
                 uri=self._get_keystone_mock_url(
                     resource='users', v3=False,
                     append=[user_data.user_id, 'OS-KSADM', 'password']),
                 status_code=200, json=user_data.json_response,
                 validate=dict(
                     json={'user': {'password': user_data.password}})),
            dict(method='PUT', uri=mock_user_resource_uri, status_code=200,
                 json=user_data.json_response,
                 validate=dict(json={'user': {}}))])

        user = self.cloud.update_user(
            user_data.user_id, password=user_data.password)
        self.assertEqual(user_data.name, user.name)
        self.assertEqual(user_data.email, user.email)
        self.assert_calls()

    def test_create_user_v3_no_domain(self):
        user_data = self._get_user_data(domain_id=uuid.uuid4().hex,
                                        email='test@example.com')
        with testtools.ExpectedException(
                openstack.cloud.OpenStackCloudException,
                "User or project creation requires an explicit"
                " domain_id argument."
        ):
            self.cloud.create_user(
                name=user_data.name, email=user_data.email,
                password=user_data.password)

    def test_delete_user(self):
        user_data = self._get_user_data(domain_id=uuid.uuid4().hex)
        user_resource_uri = self._get_keystone_mock_url(
            resource='users', append=[user_data.user_id])

        self.register_uris([
            dict(method='GET',
                 uri=self._get_keystone_mock_url(resource='users'),
                 status_code=200,
                 json=self._get_user_list(user_data)),
            dict(method='GET', uri=user_resource_uri, status_code=200,
                 json=user_data.json_response),
            dict(method='DELETE', uri=user_resource_uri, status_code=204)])

        self.cloud.delete_user(user_data.name)
        self.assert_calls()

    def test_delete_user_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self._get_keystone_mock_url(resource='users'),
                 status_code=200, json={'users': []})])
        self.assertFalse(self.cloud.delete_user(self.getUniqueString()))

    def test_add_user_to_group(self):
        user_data = self._get_user_data()
        group_data = self._get_group_data()

        self.register_uris([
            dict(method='GET',
                 uri=self._get_keystone_mock_url(resource='users'),
                 status_code=200,
                 json=self._get_user_list(user_data)),
            dict(method='GET',
                 uri=self._get_keystone_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [group_data.json_response['group']]}),
            dict(method='PUT',
                 uri=self._get_keystone_mock_url(
                     resource='groups',
                     append=[group_data.group_id, 'users', user_data.user_id]),
                 status_code=200)])
        self.cloud.add_user_to_group(user_data.user_id, group_data.group_id)
        self.assert_calls()

    def test_is_user_in_group(self):
        user_data = self._get_user_data()
        group_data = self._get_group_data()

        self.register_uris([
            dict(method='GET',
                 uri=self._get_keystone_mock_url(resource='users'),
                 status_code=200,
                 json=self._get_user_list(user_data)),
            dict(method='GET',
                 uri=self._get_keystone_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [group_data.json_response['group']]}),
            dict(method='HEAD',
                 uri=self._get_keystone_mock_url(
                     resource='groups',
                     append=[group_data.group_id, 'users', user_data.user_id]),
                 status_code=204)])

        self.assertTrue(self.cloud.is_user_in_group(
            user_data.user_id, group_data.group_id))
        self.assert_calls()

    def test_remove_user_from_group(self):
        user_data = self._get_user_data()
        group_data = self._get_group_data()

        self.register_uris([
            dict(method='GET',
                 uri=self._get_keystone_mock_url(resource='users'),
                 json=self._get_user_list(user_data)),
            dict(method='GET',
                 uri=self._get_keystone_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [group_data.json_response['group']]}),
            dict(method='DELETE',
                 uri=self._get_keystone_mock_url(
                     resource='groups',
                     append=[group_data.group_id, 'users', user_data.user_id]),
                 status_code=204)])

        self.cloud.remove_user_from_group(
            user_data.user_id, group_data.group_id)
        self.assert_calls()
