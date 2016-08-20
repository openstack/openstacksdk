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

import mock
import testtools

import os_client_config as occ
import shade
from shade import meta
from shade import _utils
from shade.tests.unit import base
from shade.tests import fakes


RAW_ROLE_ASSIGNMENTS = [
    {
        "links": {"assignment": "http://example"},
        "role": {"id": "123456"},
        "scope": {"domain": {"id": "161718"}},
        "user": {"id": "313233"}
    },
    {
        "links": {"assignment": "http://example"},
        "group": {"id": "101112"},
        "role": {"id": "123456"},
        "scope": {"project": {"id": "456789"}}
    }
]


class TestIdentityRoles(base.TestCase):

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_roles(self, mock_keystone):
        self.op_cloud.list_roles()
        self.assertTrue(mock_keystone.roles.list.called)

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_get_role(self, mock_keystone):
        role_obj = fakes.FakeRole(id='1234', name='fake_role')
        mock_keystone.roles.list.return_value = [role_obj]

        role = self.op_cloud.get_role('fake_role')

        self.assertTrue(mock_keystone.roles.list.called)
        self.assertIsNotNone(role)
        self.assertEqual('1234', role['id'])
        self.assertEqual('fake_role', role['name'])

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_role(self, mock_keystone):
        role_name = 'tootsie_roll'
        role_obj = fakes.FakeRole(id='1234', name=role_name)
        mock_keystone.roles.create.return_value = role_obj

        role = self.op_cloud.create_role(role_name)

        mock_keystone.roles.create.assert_called_once_with(
            name=role_name
        )
        self.assertIsNotNone(role)
        self.assertEqual(role_name, role['name'])

    @mock.patch.object(shade.OperatorCloud, 'get_role')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_role(self, mock_keystone, mock_get):
        role_obj = fakes.FakeRole(id='1234', name='aaa')
        mock_get.return_value = meta.obj_to_dict(role_obj)
        self.assertTrue(self.op_cloud.delete_role('1234'))
        self.assertTrue(mock_keystone.roles.delete.called)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.role_assignments.list.return_value = RAW_ROLE_ASSIGNMENTS
        ret = self.op_cloud.list_role_assignments()
        mock_keystone.role_assignments.list.assert_called_once_with()
        normalized_assignments = _utils.normalize_role_assignments(
            RAW_ROLE_ASSIGNMENTS
        )
        self.assertEqual(normalized_assignments, ret)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments_filters(self, mock_keystone,
                                           mock_api_version):
        mock_api_version.return_value = '3'
        params = dict(user='123', domain='456', effective=True)
        self.op_cloud.list_role_assignments(filters=params)
        mock_keystone.role_assignments.list.assert_called_once_with(**params)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments_exception(self, mock_keystone,
                                             mock_api_version):
        mock_api_version.return_value = '3'
        mock_keystone.role_assignments.list.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Failed to list role assignments"
        ):
            self.op_cloud.list_role_assignments()

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments_keystone_v2(self, mock_keystone,
                                               mock_api_version):
        fake_role = fakes.FakeRole(id='1234', name='fake_role')
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.roles_for_user.return_value = [fake_role]
        ret = self.op_cloud.list_role_assignments(
            filters={
                'user': '2222',
                'project': '3333'})
        self.assertEqual(
            ret, [{
                'id': fake_role.id,
                'project': '3333',
                'user': '2222'}])

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments_keystone_v2_with_role(self, mock_keystone,
                                                         mock_api_version):
        fake_role1 = fakes.FakeRole(id='1234', name='fake_role')
        fake_role2 = fakes.FakeRole(id='4321', name='fake_role')
        mock_api_version.return_value = '2.0'
        mock_keystone.roles.roles_for_user.return_value = [fake_role1,
                                                           fake_role2]
        ret = self.op_cloud.list_role_assignments(
            filters={
                'role': fake_role1.id,
                'user': '2222',
                'project': '3333'})
        self.assertEqual(
            ret, [{
                'id': fake_role1.id,
                'project': '3333',
                'user': '2222'}])

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments_exception_v2(self, mock_keystone,
                                                mock_api_version):
        mock_api_version.return_value = '2.0'
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Must provide project and user for keystone v2"
        ):
            self.op_cloud.list_role_assignments()

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments_exception_v2_no_project(self, mock_keystone,
                                                           mock_api_version):
        mock_api_version.return_value = '2.0'
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Must provide project and user for keystone v2"
        ):
            self.op_cloud.list_role_assignments(filters={'user': '12345'})
