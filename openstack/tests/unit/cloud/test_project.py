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
from testtools import matchers

from openstack import exceptions
from openstack.tests.unit import base


class TestProject(base.TestCase):
    def get_mock_url(
        self,
        service_type='identity',
        interface='public',
        resource=None,
        append=None,
        base_url_append=None,
        v3=True,
        qs_elements=None,
    ):
        if v3 and resource is None:
            resource = 'projects'
        elif not v3 and resource is None:
            resource = 'tenants'
        if base_url_append is None and v3:
            base_url_append = 'v3'
        return super().get_mock_url(
            service_type=service_type,
            interface=interface,
            resource=resource,
            append=append,
            base_url_append=base_url_append,
            qs_elements=qs_elements,
        )

    def test_create_project_v3(
        self,
    ):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc'),
            parent_id=uuid.uuid4().hex,
        )
        reference_req = project_data.json_request.copy()
        reference_req['project']['enabled'] = True
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json=project_data.json_response,
                    validate=dict(json=reference_req),
                )
            ]
        )
        project = self.cloud.create_project(
            name=project_data.project_name,
            description=project_data.description,
            domain_id=project_data.domain_id,
            parent_id=project_data.parent_id,
        )
        self.assertThat(project.id, matchers.Equals(project_data.project_id))
        self.assertThat(
            project.name, matchers.Equals(project_data.project_name)
        )
        self.assertThat(
            project.description, matchers.Equals(project_data.description)
        )
        self.assertThat(
            project.domain_id, matchers.Equals(project_data.domain_id)
        )
        self.assert_calls()

    def test_delete_project_v3(self):
        project_data = self._get_project_data(v3=False)
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[project_data.project_id]),
                    status_code=200,
                    json=project_data.json_response,
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(append=[project_data.project_id]),
                    status_code=204,
                ),
            ]
        )
        self.cloud.delete_project(project_data.project_id)
        self.assert_calls()

    def test_update_project_not_found(self):
        project_data = self._get_project_data()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(append=[project_data.project_id]),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        qs_elements=['name=' + project_data.project_id]
                    ),
                    status_code=200,
                    json={'projects': []},
                ),
            ]
        )
        with testtools.ExpectedException(exceptions.NotFoundException):
            self.cloud.update_project(project_data.project_id)
        self.assert_calls()

    def test_update_project_v3(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc')
        )
        reference_req = project_data.json_request.copy()
        # Remove elements not actually sent in the update
        reference_req['project'].pop('domain_id')
        reference_req['project'].pop('name')
        reference_req['project'].pop('enabled')
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        append=[project_data.project_id],
                        qs_elements=['domain_id=' + project_data.domain_id],
                    ),
                    status_code=200,
                    json={'projects': [project_data.json_response['project']]},
                ),
                dict(
                    method='PATCH',
                    uri=self.get_mock_url(append=[project_data.project_id]),
                    status_code=200,
                    json=project_data.json_response,
                    validate=dict(json=reference_req),
                ),
            ]
        )
        project = self.cloud.update_project(
            project_data.project_id,
            description=project_data.description,
            domain_id=project_data.domain_id,
        )
        self.assertThat(project.id, matchers.Equals(project_data.project_id))
        self.assertThat(
            project.name, matchers.Equals(project_data.project_name)
        )
        self.assertThat(
            project.description, matchers.Equals(project_data.description)
        )
        self.assert_calls()

    def test_list_projects_v3(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc')
        )
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource=(
                            f'projects?domain_id={project_data.domain_id}'
                        )
                    ),
                    status_code=200,
                    json={'projects': [project_data.json_response['project']]},
                )
            ]
        )
        projects = self.cloud.list_projects(project_data.domain_id)
        self.assertThat(len(projects), matchers.Equals(1))
        self.assertThat(
            projects[0].id, matchers.Equals(project_data.project_id)
        )
        self.assert_calls()

    def test_list_projects_v3_kwarg(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc')
        )
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource=(
                            f'projects?domain_id={project_data.domain_id}'
                        )
                    ),
                    status_code=200,
                    json={'projects': [project_data.json_response['project']]},
                )
            ]
        )
        projects = self.cloud.list_projects(domain_id=project_data.domain_id)
        self.assertThat(len(projects), matchers.Equals(1))
        self.assertThat(
            projects[0].id, matchers.Equals(project_data.project_id)
        )
        self.assert_calls()

    def test_list_projects_search_compat(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc')
        )
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json={'projects': [project_data.json_response['project']]},
                )
            ]
        )
        projects = self.cloud.search_projects(project_data.project_id)
        self.assertThat(len(projects), matchers.Equals(1))
        self.assertThat(
            projects[0].id, matchers.Equals(project_data.project_id)
        )
        self.assert_calls()

    def test_list_projects_search_compat_v3(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc')
        )
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource=(
                            f'projects?domain_id={project_data.domain_id}'
                        )
                    ),
                    status_code=200,
                    json={'projects': [project_data.json_response['project']]},
                )
            ]
        )
        projects = self.cloud.search_projects(domain_id=project_data.domain_id)
        self.assertThat(len(projects), matchers.Equals(1))
        self.assertThat(
            projects[0].id, matchers.Equals(project_data.project_id)
        )
        self.assert_calls()
