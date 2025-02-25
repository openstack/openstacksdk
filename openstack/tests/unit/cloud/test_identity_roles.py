# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import testtools
from testtools import matchers

from openstack import exceptions
from openstack.tests.unit import base


RAW_ROLE_ASSIGNMENTS = [
    {
        "links": {"assignment": "http://example"},
        "role": {"id": "123456"},
        "scope": {"domain": {"id": "161718"}},
        "user": {"id": "313233"},
    },
    {
        "links": {"assignment": "http://example"},
        "group": {"id": "101112"},
        "role": {"id": "123456"},
        "scope": {"project": {"id": "456789"}},
    },
]


class TestIdentityRoles(base.TestCase):
    def get_mock_url(
        self,
        service_type='identity',
        interface='public',
        resource='roles',
        append=None,
        base_url_append='v3',
        qs_elements=None,
    ):
        return super().get_mock_url(
            service_type,
            interface,
            resource,
            append,
            base_url_append,
            qs_elements,
        )

    def test_list_roles(self):
        role_data = self._get_role_data()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={'roles': [role_data.json_response['role']]},
                )
            ]
        )
        self.cloud.list_roles()
        self.assert_calls()

    def test_list_role_by_name(self):
        role_data = self._get_role_data()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        qs_elements=[f'name={role_data.role_name}']
                    ),
                    status_code=200,
                    json={'roles': [role_data.json_response['role']]},
                )
            ]
        )
        role = self.cloud.list_roles(name=role_data.role_name)[0]

        self.assertIsNotNone(role)
        self.assertThat(role.id, matchers.Equals(role_data.role_id))
        self.assertThat(role.name, matchers.Equals(role_data.role_name))
        self.assert_calls()

    def test_get_role_by_name(self):
        role_data = self._get_role_data()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[role_data.role_name]),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        qs_elements=[f'name={role_data.role_name}']
                    ),
                    status_code=200,
                    json={'roles': [role_data.json_response['role']]},
                ),
            ]
        )
        role = self.cloud.get_role(role_data.role_name)

        self.assertIsNotNone(role)
        self.assertThat(role.id, matchers.Equals(role_data.role_id))
        self.assertThat(role.name, matchers.Equals(role_data.role_name))
        self.assert_calls()

    def test_get_role_by_id(self):
        role_data = self._get_role_data()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[role_data.role_id]),
                    status_code=200,
                    json=role_data.json_response,
                )
            ]
        )
        role = self.cloud.get_role(role_data.role_id)

        self.assertIsNotNone(role)
        self.assertThat(role.id, matchers.Equals(role_data.role_id))
        self.assertThat(role.name, matchers.Equals(role_data.role_name))
        self.assert_calls()

    def test_create_role(self):
        role_data = self._get_role_data()
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json=role_data.json_response,
                    validate=dict(json=role_data.json_request),
                )
            ]
        )

        role = self.cloud.create_role(role_data.role_name)

        self.assertIsNotNone(role)
        self.assertThat(role.name, matchers.Equals(role_data.role_name))
        self.assertThat(role.id, matchers.Equals(role_data.role_id))
        self.assert_calls()

    def test_update_role(self):
        role_data = self._get_role_data()
        req = {'role': {'name': 'new_name'}}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[role_data.role_id]),
                    status_code=200,
                    json=role_data.json_response,
                ),
                dict(
                    method='PATCH',
                    uri=self.get_mock_url(append=[role_data.role_id]),
                    status_code=200,
                    json=role_data.json_response,
                    validate=dict(json=req),
                ),
            ]
        )

        role = self.cloud.update_role(role_data.role_id, 'new_name')

        self.assertIsNotNone(role)
        self.assertThat(role.name, matchers.Equals(role_data.role_name))
        self.assertThat(role.id, matchers.Equals(role_data.role_id))
        self.assert_calls()

    def test_delete_role_by_id(self):
        role_data = self._get_role_data()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[role_data.role_id]),
                    status_code=200,
                    json=role_data.json_response,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(append=[role_data.role_id]),
                    status_code=204,
                ),
            ]
        )
        role = self.cloud.delete_role(role_data.role_id)
        self.assertThat(role, matchers.Equals(True))
        self.assert_calls()

    def test_delete_role_by_name(self):
        role_data = self._get_role_data()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[role_data.role_name]),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        qs_elements=[f'name={role_data.role_name}']
                    ),
                    status_code=200,
                    json={'roles': [role_data.json_response['role']]},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(append=[role_data.role_id]),
                    status_code=204,
                ),
            ]
        )
        role = self.cloud.delete_role(role_data.role_name)
        self.assertThat(role, matchers.Equals(True))
        self.assert_calls()

    def test_list_role_assignments(self):
        domain_data = self._get_domain_data()
        user_data = self._get_user_data(domain_id=domain_data.domain_id)
        group_data = self._get_group_data(domain_id=domain_data.domain_id)
        project_data = self._get_project_data(domain_id=domain_data.domain_id)
        role_data = self._get_role_data()
        response = [
            {
                'links': 'https://example.com',
                'role': {'id': role_data.role_id},
                'scope': {'domain': {'id': domain_data.domain_id}},
                'user': {'id': user_data.user_id},
            },
            {
                'links': 'https://example.com',
                'role': {'id': role_data.role_id},
                'scope': {'project': {'id': project_data.project_id}},
                'group': {'id': group_data.group_id},
            },
        ]
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='role_assignments'),
                    status_code=200,
                    json={'role_assignments': response},
                    complete_qs=True,
                )
            ]
        )
        ret = self.cloud.list_role_assignments()
        self.assertThat(len(ret), matchers.Equals(2))
        self.assertThat(ret[0].user['id'], matchers.Equals(user_data.user_id))
        self.assertThat(ret[0].role['id'], matchers.Equals(role_data.role_id))
        self.assertThat(
            ret[0].scope['domain']['id'],
            matchers.Equals(domain_data.domain_id),
        )
        self.assertThat(
            ret[1].group['id'], matchers.Equals(group_data.group_id)
        )
        self.assertThat(ret[1].role['id'], matchers.Equals(role_data.role_id))
        self.assertThat(
            ret[1].scope['project']['id'],
            matchers.Equals(project_data.project_id),
        )

    def test_list_role_assignments_filters(self):
        domain_data = self._get_domain_data()
        user_data = self._get_user_data(domain_id=domain_data.domain_id)
        role_data = self._get_role_data()
        response = [
            {
                'links': 'https://example.com',
                'role': {'id': role_data.role_id},
                'scope': {'domain': {'id': domain_data.domain_id}},
                'user': {'id': user_data.user_id},
            }
        ]

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='role_assignments',
                        qs_elements=[
                            f'scope.domain.id={domain_data.domain_id}',
                            f'user.id={user_data.user_id}',
                            'effective=True',
                        ],
                    ),
                    status_code=200,
                    json={'role_assignments': response},
                    complete_qs=True,
                )
            ]
        )
        params = dict(
            user=user_data.user_id,
            domain=domain_data.domain_id,
            effective=True,
        )
        ret = self.cloud.list_role_assignments(filters=params)
        self.assertThat(len(ret), matchers.Equals(1))
        self.assertThat(ret[0].user['id'], matchers.Equals(user_data.user_id))
        self.assertThat(ret[0].role['id'], matchers.Equals(role_data.role_id))
        self.assertThat(
            ret[0].scope['domain']['id'],
            matchers.Equals(domain_data.domain_id),
        )

    def test_list_role_assignments_exception(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(resource='role_assignments'),
                    status_code=403,
                )
            ]
        )
        with testtools.ExpectedException(exceptions.ForbiddenException):
            self.cloud.list_role_assignments()
        self.assert_calls()
