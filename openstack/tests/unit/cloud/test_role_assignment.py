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


class TestRoleAssignment(base.TestCase):
    IS_INHERITED = False

    def _build_role_assignment_response(
        self, role_id, scope_type, scope_id, entity_type, entity_id
    ):
        self.assertThat(['group', 'user'], matchers.Contains(entity_type))
        self.assertThat(['project', 'domain'], matchers.Contains(scope_type))
        # NOTE(notmorgan): Links are thrown out by shade, but we construct them
        # for corectness.
        link_str = (
            'https://identity.example.com/identity/v3/{scope_t}s'
            '/{scopeid}/{entity_t}s/{entityid}/roles/{roleid}'
        )
        return [
            {
                'links': {
                    'assignment': link_str.format(
                        scope_t=scope_type,
                        scopeid=scope_id,
                        entity_t=entity_type,
                        entityid=entity_id,
                        roleid=role_id,
                    )
                },
                'role': {'id': role_id},
                'scope': {scope_type: {'id': scope_id}},
                entity_type: {'id': entity_id},
            }
        ]

    def setUp(self, cloud_config_fixture='clouds.yaml'):
        super().setUp(cloud_config_fixture)
        self.role_data = self._get_role_data()
        self.domain_data = self._get_domain_data()
        self.user_data = self._get_user_data(
            domain_id=self.domain_data.domain_id
        )
        self.project_data = self._get_project_data(
            domain_id=self.domain_data.domain_id
        )
        self.project_data_v2 = self._get_project_data(
            project_name=self.project_data.project_name,
            project_id=self.project_data.project_id,
            v3=False,
        )
        self.group_data = self._get_group_data(
            domain_id=self.domain_data.domain_id
        )

        self.user_project_assignment = self._build_role_assignment_response(
            role_id=self.role_data.role_id,
            scope_type='project',
            scope_id=self.project_data.project_id,
            entity_type='user',
            entity_id=self.user_data.user_id,
        )

        self.group_project_assignment = self._build_role_assignment_response(
            role_id=self.role_data.role_id,
            scope_type='project',
            scope_id=self.project_data.project_id,
            entity_type='group',
            entity_id=self.group_data.group_id,
        )

        self.user_domain_assignment = self._build_role_assignment_response(
            role_id=self.role_data.role_id,
            scope_type='domain',
            scope_id=self.domain_data.domain_id,
            entity_type='user',
            entity_id=self.user_data.user_id,
        )

        self.group_domain_assignment = self._build_role_assignment_response(
            role_id=self.role_data.role_id,
            scope_type='domain',
            scope_id=self.domain_data.domain_id,
            entity_type='group',
            entity_id=self.group_data.group_id,
        )

        # Cleanup of instances to ensure garbage collection/no leaking memory
        # in tests.
        self.addCleanup(delattr, self, 'role_data')
        self.addCleanup(delattr, self, 'user_data')
        self.addCleanup(delattr, self, 'domain_data')
        self.addCleanup(delattr, self, 'group_data')
        self.addCleanup(delattr, self, 'project_data')
        self.addCleanup(delattr, self, 'project_data_v2')
        self.addCleanup(delattr, self, 'user_project_assignment')
        self.addCleanup(delattr, self, 'group_project_assignment')
        self.addCleanup(delattr, self, 'user_domain_assignment')
        self.addCleanup(delattr, self, 'group_domain_assignment')

    def get_mock_url(
        self,
        service_type='identity',
        interface='public',
        resource='role_assignments',
        append=None,
        base_url_append='v3',
        qs_elements=None,
        inherited=False,
    ):
        if inherited:
            base_url_append = base_url_append + '/OS-INHERIT'
        if append and inherited:
            append.append('inherited_to_projects')

        return super().get_mock_url(
            service_type,
            interface,
            resource,
            append,
            base_url_append,
            qs_elements,
        )

    def __get(
        self, resource, data, attr, qs_elements, use_name=False, is_found=True
    ):
        if not use_name:
            if is_found:
                return [
                    dict(
                        method='GET',
                        uri=self.get_mock_url(
                            resource=resource + 's',  # do roles from role
                            append=[getattr(data, attr)],
                            qs_elements=qs_elements,
                        ),
                        status_code=200,
                        json=data.json_response,
                    )
                ]
            else:
                return [
                    dict(
                        method='GET',
                        uri=self.get_mock_url(
                            resource=resource + 's',  # do roles from role
                            append=[getattr(data, attr)],
                            qs_elements=qs_elements,
                        ),
                        status_code=404,
                    ),
                    dict(
                        method='GET',
                        uri=self.get_mock_url(
                            resource=resource + 's',  # do roles from role
                            qs_elements=qs_elements,
                        ),
                        status_code=200,
                        json={(resource + 's'): []},
                    ),
                ]
        else:
            return [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource=resource + 's',
                        append=[getattr(data, attr)],
                        qs_elements=qs_elements,
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource=resource + 's',
                        qs_elements=['name=' + getattr(data, attr)]
                        + qs_elements,
                    ),
                    status_code=200,
                    json={(resource + 's'): [data.json_response[resource]]},
                ),
            ]

    def __user_mocks(
        self, user_data, use_name, is_found=True, domain_data=None
    ):
        qs_elements = []
        if domain_data:
            qs_elements = ['domain_id=' + domain_data.domain_id]
        uri_mocks = []
        if not use_name:
            uri_mocks.append(
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='users',
                        append=[user_data.user_id],
                        # TODO(stephenfin): We shouldn't be passing domain ID
                        # here since it's unnecessary, but that requires a much
                        # larger rework of the Resource.find method.
                        qs_elements=qs_elements,
                    ),
                    json=user_data.json_response if is_found else None,
                    status_code=200 if is_found else 404,
                ),
            )
        else:
            uri_mocks += [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='users',
                        append=[user_data.name],
                        qs_elements=qs_elements,
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='users',
                        qs_elements=qs_elements + ['name=' + user_data.name],
                    ),
                    status_code=200,
                    json={
                        'users': (
                            [user_data.json_response['user']]
                            if is_found
                            else []
                        )
                    },
                ),
            ]
        return uri_mocks

    def _get_mock_role_query_urls(
        self,
        role_data,
        domain_data=None,
        project_data=None,
        group_data=None,
        user_data=None,
        use_role_name=False,
        use_domain_name=False,
        use_project_name=False,
        use_group_name=False,
        use_user_name=False,
        use_domain_in_query=True,
    ):
        """Build uri mocks for querying role assignments"""
        uri_mocks = []

        if domain_data:
            uri_mocks.extend(
                self.__get(
                    'domain',
                    domain_data,
                    'domain_id' if not use_domain_name else 'domain_name',
                    [],
                    use_name=use_domain_name,
                )
            )

        qs_elements = []
        if domain_data and use_domain_in_query:
            qs_elements = ['domain_id=' + domain_data.domain_id]

        uri_mocks.extend(
            self.__get(
                'role',
                role_data,
                'role_id' if not use_role_name else 'role_name',
                [],
                use_name=use_role_name,
            )
        )

        if user_data:
            uri_mocks.extend(
                self.__user_mocks(
                    user_data,
                    use_user_name,
                    is_found=True,
                    domain_data=domain_data,
                )
            )

        if group_data:
            uri_mocks.extend(
                self.__get(
                    'group',
                    group_data,
                    'group_id' if not use_group_name else 'group_name',
                    qs_elements,
                    use_name=use_group_name,
                )
            )

        if project_data:
            uri_mocks.extend(
                self.__get(
                    'project',
                    project_data,
                    'project_id' if not use_project_name else 'project_name',
                    qs_elements,
                    use_name=use_project_name,
                )
            )

        return uri_mocks

    def test_grant_role_user_id_project(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
            use_role_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.user_id,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_user_name_project(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
            use_role_name=True,
            use_user_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )

    def test_grant_role_user_id_project_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.grant_role(
                self.role_data.role_id,
                user=self.user_data.user_id,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_user_name_project_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
            use_role_name=True,
            use_user_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_group_id_project(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            group_data=self.group_data,
            use_role_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                group=self.group_data.group_id,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_group_name_project(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            group_data=self.group_data,
            use_role_name=True,
            use_group_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_group_id_project_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            group_data=self.group_data,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.grant_role(
                self.role_data.role_id,
                group=self.group_data.group_id,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_group_name_project_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            group_data=self.group_data,
            use_role_name=True,
            use_group_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.grant_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    # ===== Domain
    def test_grant_role_user_id_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            user_data=self.user_data,
            use_role_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.user_id,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_user_name_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            user_data=self.user_data,
            use_role_name=True,
            use_user_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )

    def test_grant_role_user_id_domain_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            user_data=self.user_data,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.grant_role(
                self.role_data.role_id,
                user=self.user_data.user_id,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_user_name_domain_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            user_data=self.user_data,
            use_role_name=True,
            use_user_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_group_id_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            group_data=self.group_data,
            use_role_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                group=self.group_data.group_id,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_group_name_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            group_data=self.group_data,
            use_role_name=True,
            use_group_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_group_id_domain_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            group_data=self.group_data,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.grant_role(
                self.role_data.role_id,
                group=self.group_data.group_id,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_role_group_name_domain_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            group_data=self.group_data,
            use_role_name=True,
            use_group_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.grant_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    # ==== Revoke
    def test_revoke_role_user_id_project(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
            use_role_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.user_id,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_user_name_project(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
            use_role_name=True,
            use_user_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )

    def test_revoke_role_user_id_project_not_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.revoke_role(
                self.role_data.role_id,
                user=self.user_data.user_id,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_user_name_project_not_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
            use_role_name=True,
            use_user_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_group_id_project(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            group_data=self.group_data,
            use_role_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                group=self.group_data.group_id,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_group_name_project(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            group_data=self.group_data,
            use_role_name=True,
            use_group_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_group_id_project_not_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            group_data=self.group_data,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.revoke_role(
                self.role_data.role_id,
                group=self.group_data.group_id,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_group_name_project_not_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            group_data=self.group_data,
            use_role_name=True,
            use_group_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.revoke_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                project=self.project_data.project_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    # ==== Domain
    def test_revoke_role_user_id_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            user_data=self.user_data,
            use_role_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.user_id,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_user_name_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            user_data=self.user_data,
            use_role_name=True,
            use_user_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )

    def test_revoke_role_user_id_domain_not_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            user_data=self.user_data,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.revoke_role(
                self.role_data.role_id,
                user=self.user_data.user_id,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_user_name_domain_not_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            user_data=self.user_data,
            use_role_name=True,
            use_user_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_group_id_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            group_data=self.group_data,
            use_role_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                group=self.group_data.group_id,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_group_name_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            group_data=self.group_data,
            use_role_name=True,
            use_group_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_group_id_domain_not_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            group_data=self.group_data,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.revoke_role(
                self.role_data.role_id,
                group=self.group_data.group_id,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_revoke_role_group_name_domain_not_exists(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            domain_data=self.domain_data,
            group_data=self.group_data,
            use_role_name=True,
            use_group_name=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='domains',
                        append=[
                            self.domain_data.domain_id,
                            'groups',
                            self.group_data.group_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertFalse(
            self.cloud.revoke_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                domain=self.domain_data.domain_id,
                inherited=self.IS_INHERITED,
            )
        )
        self.assert_calls()

    def test_grant_no_role(self):
        uris = self.__get(
            'domain', self.domain_data, 'domain_name', [], use_name=True
        )
        uris.extend(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='roles',
                        append=[self.role_data.role_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='roles',
                        qs_elements=[
                            'name=' + self.role_data.role_name,
                        ],
                    ),
                    status_code=200,
                    json={'roles': []},
                ),
            ]
        )
        self.register_uris(uris)

        with testtools.ExpectedException(exceptions.NotFoundException):
            self.cloud.grant_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                domain=self.domain_data.domain_name,
                inherited=self.IS_INHERITED,
            )
        self.assert_calls()

    def test_revoke_no_role(self):
        uris = self.__get(
            'domain', self.domain_data, 'domain_name', [], use_name=True
        )
        uris.extend(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='roles',
                        append=[self.role_data.role_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='roles',
                        qs_elements=[
                            'name=' + self.role_data.role_name,
                        ],
                    ),
                    status_code=200,
                    json={'roles': []},
                ),
            ]
        )
        self.register_uris(uris)

        with testtools.ExpectedException(exceptions.NotFoundException):
            self.cloud.revoke_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                domain=self.domain_data.domain_name,
                inherited=self.IS_INHERITED,
            )
        self.assert_calls()

    def test_grant_no_user_or_group_specified(self):
        uris = self.__get(
            'role', self.role_data, 'role_name', [], use_name=True
        )
        self.register_uris(uris)
        with testtools.ExpectedException(
            exceptions.SDKException,
            'Must specify either a user or a group',
        ):
            self.cloud.grant_role(
                self.role_data.role_name,
                inherited=self.IS_INHERITED,
            )
        self.assert_calls()

    def test_revoke_no_user_or_group_specified(self):
        uris = self.__get(
            'role', self.role_data, 'role_name', [], use_name=True
        )
        self.register_uris(uris)
        with testtools.ExpectedException(
            exceptions.SDKException,
            'Must specify either a user or a group',
        ):
            self.cloud.revoke_role(
                self.role_data.role_name,
                inherited=self.IS_INHERITED,
            )
        self.assert_calls()

    def test_grant_both_user_and_group(self):
        uris = self.__get(
            'role', self.role_data, 'role_name', [], use_name=True
        )
        self.register_uris(uris)

        with testtools.ExpectedException(
            exceptions.SDKException,
            'Specify either a group or a user, not both',
        ):
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                group=self.group_data.group_name,
                inherited=self.IS_INHERITED,
            )
        self.assert_calls()

    def test_revoke_both_user_and_group(self):
        uris = self.__get(
            'role', self.role_data, 'role_name', [], use_name=True
        )
        uris.extend(self.__user_mocks(self.user_data, use_name=True))
        uris.extend(
            self.__get(
                'group', self.group_data, 'group_name', [], use_name=True
            )
        )
        self.register_uris(uris)

        with testtools.ExpectedException(
            exceptions.SDKException,
            'Specify either a group or a user, not both',
        ):
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                group=self.group_data.group_name,
                inherited=self.IS_INHERITED,
            )

    def test_grant_both_project_and_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
            domain_data=self.domain_data,
            use_role_name=True,
            use_user_name=True,
            use_project_name=True,
            use_domain_name=True,
            use_domain_in_query=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=404,
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_name,
                domain=self.domain_data.domain_name,
                inherited=self.IS_INHERITED,
            )
        )

    def test_revoke_both_project_and_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            project_data=self.project_data,
            user_data=self.user_data,
            domain_data=self.domain_data,
            use_role_name=True,
            use_user_name=True,
            use_project_name=True,
            use_domain_name=True,
            use_domain_in_query=True,
        )
        uris.extend(
            [
                dict(
                    method='HEAD',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    complete_qs=True,
                    status_code=204,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        resource='projects',
                        append=[
                            self.project_data.project_id,
                            'users',
                            self.user_data.user_id,
                            'roles',
                            self.role_data.role_id,
                        ],
                        inherited=self.IS_INHERITED,
                    ),
                    status_code=200,
                ),
            ]
        )
        self.register_uris(uris)

        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_name,
                domain=self.domain_data.domain_name,
                inherited=self.IS_INHERITED,
            )
        )

    def test_grant_no_project_or_domain(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            use_role_name=True,
        )

        self.register_uris(uris)

        with testtools.ExpectedException(
            exceptions.SDKException,
            'Must specify either a domain, project or system',
        ):
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                inherited=self.IS_INHERITED,
            )
        self.assert_calls()

    def test_revoke_no_project_or_domain_or_system(self):
        uris = self._get_mock_role_query_urls(
            self.role_data,
            use_role_name=True,
        )

        self.register_uris(uris)

        with testtools.ExpectedException(
            exceptions.SDKException,
            'Must specify either a domain, project or system',
        ):
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                inherited=self.IS_INHERITED,
            )
        self.assert_calls()

    def test_grant_bad_domain_exception(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='domains', append=['baddomain']
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='domains', qs_elements=['name=baddomain']
                    ),
                    status_code=404,
                ),
            ]
        )
        with testtools.ExpectedException(exceptions.NotFoundException):
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                domain='baddomain',
                inherited=self.IS_INHERITED,
            )
        self.assert_calls()

    def test_revoke_bad_domain_exception(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='domains', append=['baddomain']
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='domains', qs_elements=['name=baddomain']
                    ),
                    status_code=404,
                ),
            ]
        )
        with testtools.ExpectedException(exceptions.NotFoundException):
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                domain='baddomain',
                inherited=self.IS_INHERITED,
            )
        self.assert_calls()


class TestInheritedRoleAssignment(TestRoleAssignment):
    IS_INHERITED = True
