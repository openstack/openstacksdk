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

import munch
import os_client_config as occ
import testtools

import shade
import shade._utils
from shade.tests.unit import base


class TestProject(base.TestCase):

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_project_v2(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '2'
        name = 'project_name'
        description = 'Project description'
        self.op_cloud.create_project(name=name, description=description)
        mock_keystone.tenants.create.assert_called_once_with(
            project_name=name, description=description, enabled=True,
            tenant_name=name
        )

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_project_v3(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        name = 'project_name'
        description = 'Project description'
        domain_id = '123'
        self.op_cloud.create_project(
            name=name, description=description, domain_id=domain_id)
        mock_keystone.projects.create.assert_called_once_with(
            project_name=name, description=description, enabled=True,
            name=name, domain=domain_id
        )

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_project_v3_no_domain(self, mock_keystone,
                                         mock_api_version):
        mock_api_version.return_value = '3'
        with testtools.ExpectedException(
                shade.OpenStackCloudException,
                "User or project creation requires an explicit"
                " domain_id argument."
        ):
            self.op_cloud.create_project(name='foo', description='bar')

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'get_project')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_project_v2(self, mock_keystone, mock_get,
                               mock_api_version):
        mock_api_version.return_value = '2'
        mock_get.return_value = dict(id='123')
        self.assertTrue(self.op_cloud.delete_project('123'))
        mock_get.assert_called_once_with('123', domain_id=None)
        mock_keystone.tenants.delete.assert_called_once_with(tenant='123')

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'get_project')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_project_v3(self, mock_keystone, mock_get,
                               mock_api_version):
        mock_api_version.return_value = '3'
        mock_get.return_value = dict(id='123')
        self.assertTrue(self.op_cloud.delete_project('123'))
        mock_get.assert_called_once_with('123', domain_id=None)
        mock_keystone.projects.delete.assert_called_once_with(project='123')

    @mock.patch.object(shade.OpenStackCloud, 'get_project')
    def test_update_project_not_found(self, mock_get_project):
        mock_get_project.return_value = None
        with testtools.ExpectedException(
                shade.OpenStackCloudException,
                "Project ABC not found."
        ):
            self.op_cloud.update_project('ABC')

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'get_project')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_update_project_v2(self, mock_keystone, mock_get_project,
                               mock_api_version):
        mock_api_version.return_value = '2'
        mock_get_project.return_value = munch.Munch(dict(id='123'))
        self.op_cloud.update_project('123', description='new', enabled=False)
        mock_keystone.tenants.update.assert_called_once_with(
            description='new', enabled=False, tenant_id='123')

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'get_project')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_update_project_v3(self, mock_keystone, mock_get_project,
                               mock_api_version):
        mock_api_version.return_value = '3'
        mock_get_project.return_value = munch.Munch(dict(id='123'))
        self.op_cloud.update_project('123', description='new', enabled=False)
        mock_keystone.projects.update.assert_called_once_with(
            description='new', enabled=False, project='123')

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_projects_v3(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        self.op_cloud.list_projects('123')
        mock_keystone.projects.list.assert_called_once_with(
            domain='123')

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_projects_v3_kwarg(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        self.op_cloud.list_projects(domain_id='123')
        mock_keystone.projects.list.assert_called_once_with(
            domain='123')

    @mock.patch.object(shade._utils, '_filter_list')
    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_projects_search_compat(
            self, mock_keystone, mock_api_version, mock_filter_list):
        mock_api_version.return_value = '3'
        self.op_cloud.search_projects('123')
        mock_keystone.projects.list.assert_called_once_with()
        mock_filter_list.assert_called_once_with(mock.ANY, '123', mock.ANY)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_projects_search_compat_v3(
            self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        self.op_cloud.search_projects(domain_id='123')
        mock_keystone.projects.list.assert_called_once_with(domain='123')
