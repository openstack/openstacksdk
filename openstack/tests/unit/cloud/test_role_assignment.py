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

from openstack.cloud import exc
from openstack.tests.unit import base
import testtools
from testtools import matchers


class TestRoleAssignment(base.TestCase):

    def _build_role_assignment_response(self, role_id, scope_type, scope_id,
                                        entity_type, entity_id):
        self.assertThat(['group', 'user'], matchers.Contains(entity_type))
        self.assertThat(['project', 'domain'], matchers.Contains(scope_type))
        # NOTE(notmorgan): Links are thrown out by shade, but we construct them
        # for corectness.
        link_str = ('https://identity.example.com/identity/v3/{scope_t}s'
                    '/{scopeid}/{entity_t}s/{entityid}/roles/{roleid}')
        return [{
            'links': {'assignment': link_str.format(
                scope_t=scope_type, scopeid=scope_id, entity_t=entity_type,
                entityid=entity_id, roleid=role_id)},
            'role': {'id': role_id},
            'scope': {scope_type: {'id': scope_id}},
            entity_type: {'id': entity_id}
        }]

    def setUp(self, cloud_config_fixture='clouds.yaml'):
        super(TestRoleAssignment, self).setUp(cloud_config_fixture)
        self.role_data = self._get_role_data()
        self.domain_data = self._get_domain_data()
        self.user_data = self._get_user_data(
            domain_id=self.domain_data.domain_id)
        self.project_data = self._get_project_data(
            domain_id=self.domain_data.domain_id)
        self.project_data_v2 = self._get_project_data(
            project_name=self.project_data.project_name,
            project_id=self.project_data.project_id,
            v3=False)
        self.group_data = self._get_group_data(
            domain_id=self.domain_data.domain_id)

        self.user_project_assignment = self._build_role_assignment_response(
            role_id=self.role_data.role_id, scope_type='project',
            scope_id=self.project_data.project_id, entity_type='user',
            entity_id=self.user_data.user_id)

        self.group_project_assignment = self._build_role_assignment_response(
            role_id=self.role_data.role_id, scope_type='project',
            scope_id=self.project_data.project_id, entity_type='group',
            entity_id=self.group_data.group_id)

        self.user_domain_assignment = self._build_role_assignment_response(
            role_id=self.role_data.role_id, scope_type='domain',
            scope_id=self.domain_data.domain_id, entity_type='user',
            entity_id=self.user_data.user_id)

        self.group_domain_assignment = self._build_role_assignment_response(
            role_id=self.role_data.role_id, scope_type='domain',
            scope_id=self.domain_data.domain_id, entity_type='group',
            entity_id=self.group_data.group_id)

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

    def get_mock_url(self, service_type='identity', interface='admin',
                     resource='role_assignments', append=None,
                     base_url_append='v3', qs_elements=None):
        return super(TestRoleAssignment, self).get_mock_url(
            service_type, interface, resource, append, base_url_append,
            qs_elements)

    def test_grant_role_user_v2(self):
        self.use_keystone_v2()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={'tenants': [
                     self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='PUT',
                 status_code=201,
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants',
                     append=[self.project_data_v2.project_id,
                             'users', self.user_data.user_id, 'roles',
                             'OS-KSADM', self.role_data.role_id])),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={'tenants': [
                     self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants',
                     append=[self.project_data_v2.project_id,
                             'users', self.user_data.user_id, 'roles',
                             'OS-KSADM', self.role_data.role_id]),
                 status_code=201)
        ])
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_id))
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.user_id,
                project=self.project_data.project_id))
        self.assert_calls()

    def test_grant_role_user_project_v2(self):
        self.use_keystone_v2()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={'tenants': [
                     self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants',
                     append=[self.project_data_v2.project_id,
                             'users', self.user_data.user_id, 'roles',
                             'OS-KSADM', self.role_data.role_id]),
                 status_code=201),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={'tenants': [
                     self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants',
                     append=[self.project_data_v2.project_id,
                             'users', self.user_data.user_id, 'roles',
                             'OS-KSADM', self.role_data.role_id]),
                 status_code=201),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={'tenants': [
                     self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants',
                     append=[self.project_data_v2.project_id,
                             'users', self.user_data.user_id, 'roles',
                             'OS-KSADM', self.role_data.role_id]),
                 status_code=201,
                 ),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={'tenants': [
                     self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants',
                     append=[self.project_data_v2.project_id,
                             'users', self.user_data.user_id, 'roles',
                             'OS-KSADM', self.role_data.role_id]),
                 status_code=201)
        ])
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data_v2.project_id))
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.user_id,
                project=self.project_data_v2.project_id))
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_id,
                user=self.user_data.name,
                project=self.project_data_v2.project_id))
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_id,
                user=self.user_data.user_id,
                project=self.project_data_v2.project_id))
        self.assert_calls()

    def test_grant_role_user_project_v2_exists(self):
        self.use_keystone_v2()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={'tenants': [
                     self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
        ])
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.name,
            project=self.project_data_v2.project_id))
        self.assert_calls()

    def test_grant_role_user_project(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     resource='projects',
                     append=[self.project_data.project_id, 'users',
                             self.user_data.user_id, 'roles',
                             self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     resource='projects',
                     append=[self.project_data.project_id, 'users',
                             self.user_data.user_id, 'roles',
                             self.role_data.role_id]),
                 status_code=204),
        ])
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_id))
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.user_id,
                project=self.project_data.project_id))
        self.assert_calls()

    def test_grant_role_user_project_exists(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='project',
                         scope_id=self.project_data.project_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='project',
                         scope_id=self.project_data.project_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)}),
        ])
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.name,
            project=self.project_data.project_id))
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_id,
            user=self.user_data.user_id,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_grant_role_group_project(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     resource='projects',
                     append=[self.project_data.project_id, 'groups',
                             self.group_data.group_id, 'roles',
                             self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     resource='projects',
                     append=[self.project_data.project_id, 'groups',
                             self.group_data.group_id, 'roles',
                             self.role_data.role_id]),
                 status_code=204),
        ])
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            project=self.project_data.project_id))
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_grant_role_group_project_exists(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='project',
                         scope_id=self.project_data.project_id,
                         entity_type='group',
                         entity_id=self.group_data.group_id)}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='project',
                         scope_id=self.project_data.project_id,
                         entity_type='group',
                         entity_id=self.group_data.group_id)}),
        ])
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            project=self.project_data.project_id))
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_grant_role_user_domain(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'user.id=%s' % self.user_data.user_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'user.id=%s' % self.user_data.user_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'user.id=%s' % self.user_data.user_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'user.id=%s' % self.user_data.user_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204),
        ])
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.name,
            domain=self.domain_data.domain_id))
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            domain=self.domain_data.domain_id))
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.name,
            domain=self.domain_data.domain_name))
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            domain=self.domain_data.domain_name))
        self.assert_calls()

    def test_grant_role_user_domain_exists(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'user.id=%s' % self.user_data.user_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'user.id=%s' % self.user_data.user_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'user.id=%s' % self.user_data.user_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'user.id=%s' % self.user_data.user_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)}),
        ])
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.name,
            domain=self.domain_data.domain_id))
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            domain=self.domain_data.domain_id))
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.name,
            domain=self.domain_data.domain_name))
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            domain=self.domain_data.domain_name))
        self.assert_calls()

    def test_grant_role_group_domain(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'group.id=%s' % self.group_data.group_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'group.id=%s' % self.group_data.group_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'group.id=%s' % self.group_data.group_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'group.id=%s' % self.group_data.group_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204),
        ])
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            domain=self.domain_data.domain_id))
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            domain=self.domain_data.domain_id))
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            domain=self.domain_data.domain_name))
        self.assertTrue(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            domain=self.domain_data.domain_name))
        self.assert_calls()

    def test_grant_role_group_domain_exists(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'group.id=%s' % self.group_data.group_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='group',
                         entity_id=self.group_data.group_id)}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'group.id=%s' % self.group_data.group_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='group',
                         entity_id=self.group_data.group_id)}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'group.id=%s' % self.group_data.group_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='group',
                         entity_id=self.group_data.group_id)}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'role.id=%s' % self.role_data.role_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'group.id=%s' % self.group_data.group_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='group',
                         entity_id=self.group_data.group_id)}),
        ])
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            domain=self.domain_data.domain_id))
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            domain=self.domain_data.domain_id))
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            domain=self.domain_data.domain_name))
        self.assertFalse(self.cloud.grant_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            domain=self.domain_data.domain_name))
        self.assert_calls()

    def test_revoke_role_user_v2(self):
        self.use_keystone_v2()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     base_url_append='OS-KSADM',
                     resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants'),
                 status_code=200,
                 json={
                     'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants',
                     append=[self.project_data_v2.project_id, 'users',
                             self.user_data.user_id, 'roles']),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles', 'OS-KSADM',
                                               self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(
                     base_url_append='OS-KSADM',
                     resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants'),
                 status_code=200,
                 json={
                     'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants',
                     append=[self.project_data_v2.project_id, 'users',
                             self.user_data.user_id, 'roles']),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles', 'OS-KSADM',
                                               self.role_data.role_id]),
                 status_code=204),
        ])
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            project=self.project_data.project_id))
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_revoke_role_user_project_v2(self):
        self.use_keystone_v2()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={
                     'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={
                     'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={
                     'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={
                     'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []})
        ])
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            project=self.project_data.project_id))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            project=self.project_data.project_id))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_id,
            user=self.user_data.name,
            project=self.project_data.project_id))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_id,
            user=self.user_data.user_id,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_revoke_role_user_project_v2_exists(self):
        self.use_keystone_v2()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={
                     'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles', 'OS-KSADM',
                                               self.role_data.role_id]),
                 status_code=204),
        ])
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_revoke_role_user_project(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
        ])
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            project=self.project_data.project_id))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_revoke_role_user_project_exists(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments':
                       self._build_role_assignment_response(
                           role_id=self.role_data.role_id,
                           scope_type='project',
                           scope_id=self.project_data.project_id,
                           entity_type='user',
                           entity_id=self.user_data.user_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='projects',
                                       append=[self.project_data.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id])),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments':
                       self._build_role_assignment_response(
                           role_id=self.role_data.role_id,
                           scope_type='project',
                           scope_id=self.project_data.project_id,
                           entity_type='user',
                           entity_id=self.user_data.user_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='projects',
                                       append=[self.project_data.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id])),
        ])
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            project=self.project_data.project_id))
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_id,
            user=self.user_data.user_id,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_revoke_role_group_project(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
        ])
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            project=self.project_data.project_id))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_revoke_role_group_project_exists(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments':
                       self._build_role_assignment_response(
                           role_id=self.role_data.role_id,
                           scope_type='project',
                           scope_id=self.project_data.project_id,
                           entity_type='group',
                           entity_id=self.group_data.group_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='projects',
                                       append=[self.project_data.project_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id])),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='projects'),
                 status_code=200,
                 json={'projects': [
                     self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments':
                       self._build_role_assignment_response(
                           role_id=self.role_data.role_id,
                           scope_type='project',
                           scope_id=self.project_data.project_id,
                           entity_type='group',
                           entity_id=self.group_data.group_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='projects',
                                       append=[self.project_data.project_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id])),
        ])
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            project=self.project_data.project_id))
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            project=self.project_data.project_id))
        self.assert_calls()

    def test_revoke_role_user_domain(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
        ])
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            domain=self.domain_data.domain_id))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            domain=self.domain_data.domain_id))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            domain=self.domain_data.domain_name))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            domain=self.domain_data.domain_name))
        self.assert_calls()

    def test_revoke_role_user_domain_exists(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments':
                       self._build_role_assignment_response(
                           role_id=self.role_data.role_id,
                           scope_type='domain',
                           scope_id=self.domain_data.domain_id,
                           entity_type='user',
                           entity_id=self.user_data.user_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id])),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id])),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments':
                       self._build_role_assignment_response(
                           role_id=self.role_data.role_id,
                           scope_type='domain',
                           scope_id=self.domain_data.domain_id,
                           entity_type='user',
                           entity_id=self.user_data.user_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id])),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id])),
        ])
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            domain=self.domain_data.domain_name))
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            domain=self.domain_data.domain_name))
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            domain=self.domain_data.domain_id))
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.user_id,
            domain=self.domain_data.domain_id))
        self.assert_calls()

    def test_revoke_role_group_domain(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments': []}),
        ])
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            domain=self.domain_data.domain_name))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            domain=self.domain_data.domain_name))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            domain=self.domain_data.domain_id))
        self.assertFalse(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            domain=self.domain_data.domain_id))
        self.assert_calls()

    def test_revoke_role_group_domain_exists(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments':
                       self._build_role_assignment_response(
                           role_id=self.role_data.role_id,
                           scope_type='domain',
                           scope_id=self.domain_data.domain_id,
                           entity_type='group',
                           entity_id=self.group_data.group_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id])),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='group',
                         entity_id=self.group_data.group_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id])),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={'role_assignments':
                       self._build_role_assignment_response(
                           role_id=self.role_data.role_id,
                           scope_type='domain',
                           scope_id=self.domain_data.domain_id,
                           entity_type='group',
                           entity_id=self.group_data.group_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id])),
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'group.id=%s' % self.group_data.group_id,
                         'scope.domain.id=%s' % self.domain_data.domain_id,
                         'role.id=%s' % self.role_data.role_id]),
                 status_code=200,
                 complete_qs=True,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='domain',
                         scope_id=self.domain_data.domain_id,
                         entity_type='group',
                         entity_id=self.group_data.group_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_id,
                                               'groups',
                                               self.group_data.group_id,
                                               'roles',
                                               self.role_data.role_id])),
        ])
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            domain=self.domain_data.domain_name))
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            domain=self.domain_data.domain_name))
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_name,
            domain=self.domain_data.domain_id))
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            group=self.group_data.group_id,
            domain=self.domain_data.domain_id))
        self.assert_calls()

    def test_grant_no_role(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': []})
        ])

        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Role {0} not found'.format(self.role_data.role_name)
        ):
            self.cloud.grant_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                domain=self.domain_data.domain_name)
        self.assert_calls()

    def test_revoke_no_role(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': []})
        ])

        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Role {0} not found'.format(self.role_data.role_name)
        ):
            self.cloud.revoke_role(
                self.role_data.role_name,
                group=self.group_data.group_name,
                domain=self.domain_data.domain_name)
        self.assert_calls()

    def test_grant_no_user_or_group_specified(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]})
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Must specify either a user or a group'
        ):
            self.cloud.grant_role(self.role_data.role_name)
        self.assert_calls()

    def test_revoke_no_user_or_group_specified(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]})
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Must specify either a user or a group'
        ):
            self.cloud.revoke_role(self.role_data.role_name)
        self.assert_calls()

    def test_grant_no_user_or_group(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': []})
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Must specify either a user or a group'
        ):
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name)
        self.assert_calls()

    def test_revoke_no_user_or_group(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': []})
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Must specify either a user or a group'
        ):
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name)
        self.assert_calls()

    def test_grant_both_user_and_group(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Specify either a group or a user, not both'
        ):
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                group=self.group_data.group_name)
        self.assert_calls()

    def test_revoke_both_user_and_group(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='groups'),
                 status_code=200,
                 json={'groups': [self.group_data.json_response['group']]}),
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Specify either a group or a user, not both'
        ):
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                group=self.group_data.group_name)
        self.assert_calls()

    def test_grant_both_project_and_domain(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource=('projects?domain_id=%s' %
                               self.domain_data.domain_id)),
                 status_code=200,
                 json={'projects':
                       [self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(resource='projects',
                                       append=[self.project_data.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204)
        ])
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_id,
                domain=self.domain_data.domain_name))
        self.assert_calls()

    def test_revoke_both_project_and_domain(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=[self.domain_data.domain_name]),
                 status_code=200,
                 json=self.domain_data.json_response),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource=('projects?domain_id=%s' %
                               self.domain_data.domain_id)),
                 status_code=200,
                 json={'projects':
                       [self.project_data.json_response['project']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=[
                         'user.id=%s' % self.user_data.user_id,
                         'scope.project.id=%s' % self.project_data.project_id,
                         'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='project',
                         scope_id=self.project_data.project_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)}),
            dict(method='DELETE',
                 uri=self.get_mock_url(resource='projects',
                                       append=[self.project_data.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles',
                                               self.role_data.role_id]),
                 status_code=204)
        ])
        self.assertTrue(self.cloud.revoke_role(
            self.role_data.role_name,
            user=self.user_data.name,
            project=self.project_data.project_id,
            domain=self.domain_data.domain_name))
        self.assert_calls()

    def test_grant_no_project_or_domain(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=['user.id=%s' % self.user_data.user_id,
                                  'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={'role_assignments': []})
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Must specify either a domain or project'
        ):
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name)
        self.assert_calls()

    def test_revoke_no_project_or_domain(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='role_assignments',
                     qs_elements=['user.id=%s' % self.user_data.user_id,
                                  'role.id=%s' % self.role_data.role_id]),
                 complete_qs=True,
                 status_code=200,
                 json={
                     'role_assignments': self._build_role_assignment_response(
                         role_id=self.role_data.role_id,
                         scope_type='project',
                         scope_id=self.project_data.project_id,
                         entity_type='user',
                         entity_id=self.user_data.user_id)})
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudException,
            'Must specify either a domain or project'
        ):
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name)
        self.assert_calls()

    def test_grant_bad_domain_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=['baddomain']),
                 status_code=404,
                 headers={'Content-Type': 'text/plain'},
                 text='Could not find domain: baddomain')
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudURINotFound,
            'Failed to get domain baddomain'
        ):
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                domain='baddomain')
        self.assert_calls()

    def test_revoke_bad_domain_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(resource='domains',
                                       append=['baddomain']),
                 status_code=404,
                 headers={'Content-Type': 'text/plain'},
                 text='Could not find domain: baddomain')
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudURINotFound,
            'Failed to get domain baddomain'
        ):
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                domain='baddomain')
        self.assert_calls()

    def test_grant_role_user_project_v2_wait(self):
        self.use_keystone_v2()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={'tenants': [
                     self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     base_url_append=None,
                     resource='tenants',
                     append=[self.project_data_v2.project_id,
                             'users', self.user_data.user_id, 'roles',
                             'OS-KSADM', self.role_data.role_id]),
                 status_code=201),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
        ])
        self.assertTrue(
            self.cloud.grant_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_id,
                wait=True))
        self.assert_calls()

    def test_grant_role_user_project_v2_wait_exception(self):
        self.use_keystone_v2()

        with testtools.ExpectedException(
            exc.OpenStackCloudTimeout,
            'Timeout waiting for role to be granted'
        ):
            self.register_uris([
                dict(method='GET',
                     uri=self.get_mock_url(base_url_append='OS-KSADM',
                                           resource='roles'),
                     status_code=200,
                     json={'roles': [self.role_data.json_response['role']]}),
                dict(method='GET',
                     uri=self.get_mock_url(base_url_append=None,
                                           resource='users'),
                     status_code=200,
                     json={'users': [self.user_data.json_response['user']]}),
                dict(method='GET',
                     uri=self.get_mock_url(base_url_append=None,
                                           resource='tenants'),
                     status_code=200,
                     json={'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
                dict(method='GET',
                     uri=self.get_mock_url(base_url_append=None,
                                           resource='tenants',
                                           append=[
                                               self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                     status_code=200,
                     json={'roles': []}),
                dict(method='PUT',
                     uri=self.get_mock_url(
                         base_url_append=None,
                         resource='tenants',
                         append=[self.project_data_v2.project_id,
                                 'users', self.user_data.user_id, 'roles',
                                 'OS-KSADM', self.role_data.role_id]),
                     status_code=201),
                dict(method='GET',
                     uri=self.get_mock_url(base_url_append=None,
                                           resource='tenants',
                                           append=[
                                               self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                     status_code=200,
                     json={'roles': []}),
            ])
            self.assertTrue(
                self.cloud.grant_role(
                    self.role_data.role_name,
                    user=self.user_data.name,
                    project=self.project_data.project_id,
                    wait=True, timeout=0.01))
        self.assert_calls(do_count=False)

    def test_revoke_role_user_project_v2_wait(self):
        self.use_keystone_v2()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={
                     'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles', 'OS-KSADM',
                                               self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': []}),
        ])
        self.assertTrue(
            self.cloud.revoke_role(
                self.role_data.role_name,
                user=self.user_data.name,
                project=self.project_data.project_id,
                wait=True))
        self.assert_calls(do_count=False)

    def test_revoke_role_user_project_v2_wait_exception(self):
        self.use_keystone_v2()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append='OS-KSADM',
                                       resource='roles'),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None, resource='users'),
                 status_code=200,
                 json={'users': [self.user_data.json_response['user']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants'),
                 status_code=200,
                 json={
                     'tenants': [
                         self.project_data_v2.json_response['tenant']]}),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles', 'OS-KSADM',
                                               self.role_data.role_id]),
                 status_code=204),
            dict(method='GET',
                 uri=self.get_mock_url(base_url_append=None,
                                       resource='tenants',
                                       append=[self.project_data_v2.project_id,
                                               'users',
                                               self.user_data.user_id,
                                               'roles']),
                 status_code=200,
                 json={'roles': [self.role_data.json_response['role']]}),
        ])
        with testtools.ExpectedException(
            exc.OpenStackCloudTimeout,
            'Timeout waiting for role to be revoked'
        ):
            self.assertTrue(self.cloud.revoke_role(
                self.role_data.role_name, user=self.user_data.name,
                project=self.project_data.project_id, wait=True, timeout=0.01))
        self.assert_calls(do_count=False)
