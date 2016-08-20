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

from mock import patch
import os_client_config as occ
from shade import OperatorCloud
from shade.exc import OpenStackCloudException, OpenStackCloudTimeout
from shade.meta import obj_to_dict
from shade.tests import fakes
from shade.tests.unit import base
import testtools


class TestRoleAssignment(base.TestCase):

    def setUp(self):
        super(TestRoleAssignment, self).setUp()
        self.fake_role = obj_to_dict(fakes.FakeRole('12345', 'test'))
        self.fake_user = obj_to_dict(fakes.FakeUser('12345',
                                                    'test@nobody.org',
                                                    'test',
                                                    domain_id='test-domain'))
        self.fake_group = obj_to_dict(fakes.FakeGroup('12345',
                                                      'test',
                                                      'test group',
                                                      domain_id='test-domain'))
        self.fake_project = obj_to_dict(
            fakes.FakeProject('12345', domain_id='test-domain'))
        self.fake_domain = obj_to_dict(fakes.FakeDomain('test-domain',
                                                        'test',
                                                        'test domain',
                                                        enabled=True))
        self.user_project_assignment = obj_to_dict({
            'role': {
                'id': self.fake_role['id']
            },
            'scope': {
                'project': {
                    'id': self.fake_project['id']
                }
            },
            'user': {
                'id': self.fake_user['id']
            }
        })
        self.group_project_assignment = obj_to_dict({
            'role': {
                'id': self.fake_role['id']
            },
            'scope': {
                'project': {
                    'id': self.fake_project['id']
                }
            },
            'group': {
                'id': self.fake_group['id']
            }
        })
        self.user_domain_assignment = obj_to_dict({
            'role': {
                'id': self.fake_role['id']
            },
            'scope': {
                'domain': {
                    'id': self.fake_domain['id']
                }
            },
            'user': {
                'id': self.fake_user['id']
            }
        })
        self.group_domain_assignment = obj_to_dict({
            'role': {
                'id': self.fake_role['id']
            },
            'scope': {
                'domain': {
                    'id': self.fake_domain['id']
                }
            },
            'group': {
                'id': self.fake_group['id']
            }
        })

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_user_v2(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.roles.roles_for_user.return_value = []
        mock_keystone.roles.add_user_role.return_value = self.fake_role
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                project=self.fake_project['id']))
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['id'],
                project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_user_project_v2(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.roles_for_user.return_value = []
        mock_keystone.roles.add_user_role.return_value = self.fake_role
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                project=self.fake_project['id']))
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['id'],
                project=self.fake_project['id']))
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['id'],
                user=self.fake_user['name'],
                project=self.fake_project['id']))
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['id'],
                user=self.fake_user['id'],
                project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_user_project_v2_exists(self,
                                               mock_keystone,
                                               mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.roles_for_user.return_value = [self.fake_role]
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_user_project(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.role_assignments.list.return_value = []
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                project=self.fake_project['id']))
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['id'],
                project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_user_project_exists(self,
                                            mock_keystone,
                                            mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.role_assignments.list.return_value = \
            [self.user_project_assignment]
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            project=self.fake_project['id']))
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['id'],
            user=self.fake_user['id'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_group_project(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.groups.list.return_value = [self.fake_group]
        mock_keystone.role_assignments.list.return_value = []
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            project=self.fake_project['id']))
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_group_project_exists(self,
                                             mock_keystone,
                                             mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.groups.list.return_value = [self.fake_group]
        mock_keystone.role_assignments.list.return_value = \
            [self.group_project_assignment]
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            project=self.fake_project['id']))
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_user_domain(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.domains.get.return_value = self.fake_domain
        mock_keystone.role_assignments.list.return_value = []
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            domain=self.fake_domain['id']))
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            domain=self.fake_domain['id']))
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            domain=self.fake_domain['name']))
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            domain=self.fake_domain['name']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_user_domain_exists(self,
                                           mock_keystone,
                                           mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.domains.get.return_value = self.fake_domain
        mock_keystone.role_assignments.list.return_value = \
            [self.user_domain_assignment]
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            domain=self.fake_domain['name']))
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            domain=self.fake_domain['name']))
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            domain=self.fake_domain['id']))
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            domain=self.fake_domain['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_group_domain(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.groups.list.return_value = [self.fake_group]
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.domains.get.return_value = self.fake_domain
        mock_keystone.role_assignments.list.return_value = []
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            domain=self.fake_domain['name']))
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            domain=self.fake_domain['name']))
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            domain=self.fake_domain['id']))
        self.assertTrue(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            domain=self.fake_domain['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_group_domain_exists(self,
                                            mock_keystone,
                                            mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.groups.list.return_value = [self.fake_group]
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.domains.get.return_value = self.fake_domain
        mock_keystone.role_assignments.list.return_value = \
            [self.group_domain_assignment]
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            domain=self.fake_domain['name']))
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            domain=self.fake_domain['name']))
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            domain=self.fake_domain['id']))
        self.assertFalse(self.op_cloud.grant_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            domain=self.fake_domain['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_user_v2(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.roles.roles_for_user.return_value = [self.fake_role]
        mock_keystone.roles.remove_user_role.return_value = self.fake_role
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            project=self.fake_project['id']))
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_user_project_v2(self,
                                         mock_keystone,
                                         mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.roles_for_user.return_value = []
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            project=self.fake_project['id']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            project=self.fake_project['id']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['id'],
            user=self.fake_user['name'],
            project=self.fake_project['id']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['id'],
            user=self.fake_user['id'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_user_project_v2_exists(self,
                                                mock_keystone,
                                                mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.roles_for_user.return_value = [self.fake_role]
        mock_keystone.roles.remove_user_role.return_value = self.fake_role
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_user_project(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.role_assignments.list.return_value = []
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            project=self.fake_project['id']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_user_project_exists(self,
                                             mock_keystone,
                                             mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.role_assignments.list.return_value = \
            [self.user_project_assignment]
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            project=self.fake_project['id']))
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['id'],
            user=self.fake_user['id'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_group_project(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.groups.list.return_value = [self.fake_group]
        mock_keystone.role_assignments.list.return_value = []
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            project=self.fake_project['id']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_group_project_exists(self,
                                              mock_keystone,
                                              mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.groups.list.return_value = [self.fake_group]
        mock_keystone.role_assignments.list.return_value = \
            [self.group_project_assignment]
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            project=self.fake_project['id']))
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            project=self.fake_project['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_user_domain(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.domains.get.return_value = self.fake_domain
        mock_keystone.role_assignments.list.return_value = []
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            domain=self.fake_domain['id']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            domain=self.fake_domain['id']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            domain=self.fake_domain['name']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            domain=self.fake_domain['name']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_user_domain_exists(self,
                                            mock_keystone,
                                            mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.domains.get.return_value = self.fake_domain
        mock_keystone.role_assignments.list.return_value = \
            [self.user_domain_assignment]
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            domain=self.fake_domain['name']))
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            domain=self.fake_domain['name']))
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            domain=self.fake_domain['id']))
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['id'],
            domain=self.fake_domain['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_group_domain(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.groups.list.return_value = [self.fake_group]
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.domains.get.return_value = self.fake_domain
        mock_keystone.role_assignments.list.return_value = []
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            domain=self.fake_domain['name']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            domain=self.fake_domain['name']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            domain=self.fake_domain['id']))
        self.assertFalse(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            domain=self.fake_domain['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_group_domain_exists(self,
                                             mock_keystone,
                                             mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.groups.list.return_value = [self.fake_group]
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.domains.get.return_value = self.fake_domain
        mock_keystone.role_assignments.list.return_value = \
            [self.group_domain_assignment]
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            domain=self.fake_domain['name']))
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            domain=self.fake_domain['name']))
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['name'],
            domain=self.fake_domain['id']))
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            group=self.fake_group['id'],
            domain=self.fake_domain['id']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_no_role(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = []

        with testtools.ExpectedException(
            OpenStackCloudException,
            'Role {0} not found'.format(self.fake_role['name'])
        ):
            self.op_cloud.grant_role(
                self.fake_role['name'],
                group=self.fake_group['name'],
                domain=self.fake_domain['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_no_role(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = []
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Role {0} not found'.format(self.fake_role['name'])
        ):
            self.op_cloud.revoke_role(
                self.fake_role['name'],
                group=self.fake_group['name'],
                domain=self.fake_domain['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_no_user_or_group_specified(self,
                                              mock_keystone,
                                              mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Must specify either a user or a group'
        ):
            self.op_cloud.grant_role(self.fake_role['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_no_user_or_group_specified(self,
                                               mock_keystone,
                                               mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Must specify either a user or a group'
        ):
            self.op_cloud.revoke_role(self.fake_role['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_no_user_or_group(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = []
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Must specify either a user or a group'
        ):
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_no_user_or_group(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = []
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Must specify either a user or a group'
        ):
            self.op_cloud.revoke_role(
                self.fake_role['name'],
                user=self.fake_user['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_both_user_and_group(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.groups.list.return_value = [self.fake_group]
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Specify either a group or a user, not both'
        ):
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                group=self.fake_group['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_both_user_and_group(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.groups.list.return_value = [self.fake_group]
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Specify either a group or a user, not both'
        ):
            self.op_cloud.revoke_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                group=self.fake_group['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_both_project_and_domain(self,
                                           mock_keystone,
                                           mock_api_version):
        mock_api_version.return_value = '3'
        fake_user2 = fakes.FakeUser('12345',
                                    'test@nobody.org',
                                    'test',
                                    domain_id='default')
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user, fake_user2]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.domains.get.return_value = self.fake_domain
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                project=self.fake_project['id'],
                domain=self.fake_domain['name']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_both_project_and_domain(self,
                                            mock_keystone,
                                            mock_api_version):
        mock_api_version.return_value = '3'
        fake_user2 = fakes.FakeUser('12345',
                                    'test@nobody.org',
                                    'test',
                                    domain_id='default')
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user, fake_user2]
        mock_keystone.projects.list.return_value = [self.fake_project]
        mock_keystone.domains.get.return_value = self.fake_domain
        mock_keystone.role_assignments.list.return_value = \
            [self.user_project_assignment]
        self.assertTrue(self.op_cloud.revoke_role(
            self.fake_role['name'],
            user=self.fake_user['name'],
            project=self.fake_project['id'],
            domain=self.fake_domain['name']))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_no_project_or_domain(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.projects.list.return_value = []
        mock_keystone.domains.get.return_value = None
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Must specify either a domain or project'
        ):
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_no_project_or_domain(self,
                                         mock_keystone,
                                         mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.projects.list.return_value = []
        mock_keystone.domains.get.return_value = None
        mock_keystone.role_assignments.list.return_value = \
            [self.user_project_assignment]
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Must specify either a domain or project'
        ):
            self.op_cloud.revoke_role(
                self.fake_role['name'],
                user=self.fake_user['name'])

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_bad_domain_exception(self,
                                        mock_keystone,
                                        mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.domains.get.side_effect = Exception('test')
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Failed to get domain baddomain \(Inner Exception: test\)'
        ):
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                domain='baddomain')

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_bad_domain_exception(self,
                                         mock_keystone,
                                         mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.domains.get.side_effect = Exception('test')
        with testtools.ExpectedException(
            OpenStackCloudException,
            'Failed to get domain baddomain \(Inner Exception: test\)'
        ):
            self.op_cloud.revoke_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                domain='baddomain')

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_user_project_v2_wait(self,
                                             mock_keystone,
                                             mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.roles_for_user.side_effect = [
            [], [], [self.fake_role]]
        mock_keystone.roles.add_user_role.return_value = self.fake_role
        self.assertTrue(
            self.op_cloud.grant_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                project=self.fake_project['id'],
                wait=True))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_grant_role_user_project_v2_wait_exception(self,
                                                       mock_keystone,
                                                       mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.roles_for_user.return_value = []
        mock_keystone.roles.add_user_role.return_value = self.fake_role

        with testtools.ExpectedException(
            OpenStackCloudTimeout,
            'Timeout waiting for role to be granted'
        ):
            self.assertTrue(self.op_cloud.grant_role(
                self.fake_role['name'], user=self.fake_user['name'],
                project=self.fake_project['id'], wait=True, timeout=0.01))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_user_project_v2_wait(
            self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.roles_for_user.side_effect = [
            [self.fake_role], [self.fake_role],
            []]
        mock_keystone.roles.remove_user_role.return_value = self.fake_role
        self.assertTrue(
            self.op_cloud.revoke_role(
                self.fake_role['name'],
                user=self.fake_user['name'],
                project=self.fake_project['id'],
                wait=True))

    @patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @patch.object(OperatorCloud, 'keystone_client')
    def test_revoke_role_user_project_v2_wait_exception(self,
                                                        mock_keystone,
                                                        mock_api_version):
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.list.return_value = [self.fake_role]
        mock_keystone.tenants.list.return_value = [self.fake_project]
        mock_keystone.users.list.return_value = [self.fake_user]
        mock_keystone.roles.roles_for_user.return_value = [self.fake_role]
        mock_keystone.roles.remove_user_role.return_value = self.fake_role
        with testtools.ExpectedException(
            OpenStackCloudTimeout,
            'Timeout waiting for role to be revoked'
        ):
            self.assertTrue(self.op_cloud.revoke_role(
                self.fake_role['name'], user=self.fake_user['name'],
                project=self.fake_project['id'], wait=True, timeout=0.01))
