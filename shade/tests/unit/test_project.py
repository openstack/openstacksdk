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

import testtools
from testtools import matchers

import shade
import shade._utils
from shade.tests.unit import base


class TestProject(base.RequestsMockTestCase):

    def get_mock_url(self, service_type='identity', interface='admin',
                     resource=None, append=None, base_url_append=None,
                     v3=True):
        if v3 and resource is None:
            resource = 'projects'
        elif not v3 and resource is None:
            resource = 'tenants'
        if base_url_append is None and v3:
            base_url_append = 'v3'
        return super(TestProject, self).get_mock_url(
            service_type=service_type, interface=interface, resource=resource,
            append=append, base_url_append=base_url_append)

    def test_create_project_v2(self):
        self.use_keystone_v2()
        project_data = self._get_project_data(v3=False)
        self.register_uris([
            dict(method='POST', uri=self.get_mock_url(v3=False),
                 status_code=200, json=project_data.json_response,
                 validate=dict(json=project_data.json_request))
        ])
        project = self.op_cloud.create_project(
            name=project_data.project_name,
            description=project_data.description)
        self.assertThat(project.id, matchers.Equals(project_data.project_id))
        self.assertThat(
            project.name, matchers.Equals(project_data.project_name))
        self.assert_calls()

    def test_create_project_v3(self,):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc'))
        reference_req = project_data.json_request.copy()
        reference_req['project']['enabled'] = True
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(),
                 status_code=200,
                 json=project_data.json_response,
                 validate=dict(json=reference_req))
        ])
        project = self.op_cloud.create_project(
            name=project_data.project_name,
            description=project_data.description,
            domain_id=project_data.domain_id)
        self.assertThat(project.id, matchers.Equals(project_data.project_id))
        self.assertThat(
            project.name, matchers.Equals(project_data.project_name))
        self.assertThat(
            project.description, matchers.Equals(project_data.description))
        self.assertThat(
            project.domain_id, matchers.Equals(project_data.domain_id))
        self.assert_calls()

    def test_create_project_v3_no_domain(self):
        with testtools.ExpectedException(
                shade.OpenStackCloudException,
                "User or project creation requires an explicit"
                " domain_id argument."
        ):
            self.op_cloud.create_project(name='foo', description='bar')

    def test_delete_project_v2(self):
        self.use_keystone_v2()
        project_data = self._get_project_data(v3=False)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(v3=False),
                 status_code=200,
                 json={'tenants': [project_data.json_response['tenant']]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     v3=False, append=[project_data.project_id]),
                 status_code=204)
        ])
        self.op_cloud.delete_project(project_data.project_id)
        self.assert_calls()

    def test_delete_project_v3(self):
        project_data = self._get_project_data(v3=False)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(),
                 status_code=200,
                 json={'projects': [project_data.json_response['tenant']]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(append=[project_data.project_id]),
                 status_code=204)
        ])
        self.op_cloud.delete_project(project_data.project_id)
        self.assert_calls()

    def test_update_project_not_found(self):
        project_data = self._get_project_data()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(),
                 status_code=200,
                 json={'projects': []})
        ])
        # NOTE(notmorgan): This test (and shade) does not represent a case
        # where the project is in the project list but a 404 is raised when
        # the PATCH is issued. This is a bug in shade and should be fixed,
        # shade will raise an attribute error instead of the proper
        # project not found exception.
        with testtools.ExpectedException(
                shade.OpenStackCloudException,
                "Project %s not found." % project_data.project_id
        ):
            self.op_cloud.update_project(project_data.project_id)
        self.assert_calls()

    def test_update_project_v2(self):
        self.use_keystone_v2()
        project_data = self._get_project_data(
            v3=False,
            description=self.getUniqueString('projectDesc'))
        # remove elements that are not updated in this test.
        project_data.json_request['tenant'].pop('name')
        project_data.json_request['tenant'].pop('enabled')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(v3=False),
                 status_code=200,
                 json={'tenants': [project_data.json_response['tenant']]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     v3=False, append=[project_data.project_id]),
                 status_code=200,
                 json=project_data.json_response,
                 validate=dict(json=project_data.json_request))
        ])
        project = self.op_cloud.update_project(
            project_data.project_id,
            description=project_data.description)
        self.assertThat(project.id, matchers.Equals(project_data.project_id))
        self.assertThat(
            project.name, matchers.Equals(project_data.project_name))
        self.assertThat(
            project.description, matchers.Equals(project_data.description))
        self.assert_calls()

    def test_update_project_v3(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc'))
        reference_req = project_data.json_request.copy()
        # Remove elements not actually sent in the update
        reference_req['project'].pop('domain_id')
        reference_req['project'].pop('name')
        reference_req['project'].pop('enabled')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource=('projects?domain_id=%s' %
                               project_data.domain_id)),
                 status_code=200,
                 json={'projects': [project_data.json_response['project']]}),
            dict(method='PATCH',
                 uri=self.get_mock_url(append=[project_data.project_id]),
                 status_code=200, json=project_data.json_response,
                 validate=dict(json=reference_req))
        ])
        project = self.op_cloud.update_project(
            project_data.project_id,
            description=project_data.description,
            domain_id=project_data.domain_id)
        self.assertThat(project.id, matchers.Equals(project_data.project_id))
        self.assertThat(
            project.name, matchers.Equals(project_data.project_name))
        self.assertThat(
            project.description, matchers.Equals(project_data.description))
        self.assert_calls()

    def test_list_projects_v3(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc'))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource=('projects?domain_id=%s' %
                               project_data.domain_id)),
                 status_code=200,
                 json={'projects': [project_data.json_response['project']]})
        ])
        projects = self.op_cloud.list_projects(project_data.domain_id)
        self.assertThat(len(projects), matchers.Equals(1))
        self.assertThat(
            projects[0].id, matchers.Equals(project_data.project_id))
        self.assert_calls()

    def test_list_projects_v3_kwarg(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc'))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource=('projects?domain_id=%s' %
                               project_data.domain_id)),
                 status_code=200,
                 json={'projects': [project_data.json_response['project']]})
        ])
        projects = self.op_cloud.list_projects(
            domain_id=project_data.domain_id)
        self.assertThat(len(projects), matchers.Equals(1))
        self.assertThat(
            projects[0].id, matchers.Equals(project_data.project_id))
        self.assert_calls()

    def test_list_projects_search_compat(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc'))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(),
                 status_code=200,
                 json={'projects': [project_data.json_response['project']]})
        ])
        projects = self.op_cloud.search_projects(project_data.project_id)
        self.assertThat(len(projects), matchers.Equals(1))
        self.assertThat(
            projects[0].id, matchers.Equals(project_data.project_id))
        self.assert_calls()

    def test_list_projects_search_compat_v3(self):
        project_data = self._get_project_data(
            description=self.getUniqueString('projectDesc'))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource=('projects?domain_id=%s' %
                               project_data.domain_id)),
                 status_code=200,
                 json={'projects': [project_data.json_response['project']]})
        ])
        projects = self.op_cloud.search_projects(
            domain_id=project_data.domain_id)
        self.assertThat(len(projects), matchers.Equals(1))
        self.assertThat(
            projects[0].id, matchers.Equals(project_data.project_id))
        self.assert_calls()
