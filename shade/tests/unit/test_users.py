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
from shade.tests import fakes
from shade.tests.unit import base


class TestUsers(base.TestCase):

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_user_v2(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '2'
        name = 'Mickey Mouse'
        email = 'mickey@disney.com'
        password = 'mice-rule'
        fake_user = fakes.FakeUser('1', email, name)
        mock_keystone.users.create.return_value = fake_user
        user = self.op_cloud.create_user(
            name=name, email=email, password=password,
        )
        mock_keystone.users.create.assert_called_once_with(
            name=name, password=password, email=email,
            enabled=True,
        )
        self.assertEqual(name, user.name)
        self.assertEqual(email, user.email)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_user_v3(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        name = 'Mickey Mouse'
        email = 'mickey@disney.com'
        password = 'mice-rule'
        domain_id = '456'
        description = 'fake-description'
        fake_user = fakes.FakeUser('1', email, name, description=description)
        mock_keystone.users.create.return_value = fake_user
        user = self.op_cloud.create_user(
            name=name, email=email,
            password=password,
            description=description,
            domain_id=domain_id)
        mock_keystone.users.create.assert_called_once_with(
            name=name, password=password, email=email,
            description=description, enabled=True,
            domain=domain_id
        )
        self.assertEqual(name, user.name)
        self.assertEqual(email, user.email)
        self.assertEqual(description, user.description)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_update_user_password_v2(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '2'
        name = 'Mickey Mouse'
        email = 'mickey@disney.com'
        password = 'mice-rule'
        domain_id = '1'
        user = {'id': '1', 'name': name, 'email': email, 'description': None}
        fake_user = fakes.FakeUser(**user)
        munch_fake_user = munch.Munch(user)
        mock_keystone.users.list.return_value = [fake_user]
        mock_keystone.users.get.return_value = fake_user
        mock_keystone.users.update.return_value = fake_user
        mock_keystone.users.update_password.return_value = fake_user
        user = self.op_cloud.update_user(
            name, name=name, email=email,
            password=password,
            domain_id=domain_id)
        mock_keystone.users.update.assert_called_once_with(
            user=munch_fake_user, name=name, email=email)
        mock_keystone.users.update_password.assert_called_once_with(
            user=munch_fake_user, password=password)
        self.assertEqual(name, user.name)
        self.assertEqual(email, user.email)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_user_v3_no_domain(self, mock_keystone, mock_api_version):
        mock_api_version.return_value = '3'
        name = 'Mickey Mouse'
        email = 'mickey@disney.com'
        password = 'mice-rule'
        with testtools.ExpectedException(
                shade.OpenStackCloudException,
                "User or project creation requires an explicit"
                " domain_id argument."
        ):
            self.op_cloud.create_user(
                name=name, email=email, password=password)

    @mock.patch.object(shade.OpenStackCloud, 'get_user_by_id')
    @mock.patch.object(shade.OpenStackCloud, 'get_user')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_user(self, mock_keystone, mock_get_user, mock_get_by_id):
        mock_get_user.return_value = dict(id='123')
        fake_user = fakes.FakeUser('123', 'email', 'name')
        mock_get_by_id.return_value = fake_user
        self.assertTrue(self.op_cloud.delete_user('name'))
        mock_get_by_id.assert_called_once_with('123', normalize=False)
        mock_keystone.users.delete.assert_called_once_with(user=fake_user)

    @mock.patch.object(shade.OpenStackCloud, 'get_user')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_user_not_found(self, mock_keystone, mock_get_user):
        mock_get_user.return_value = None
        self.assertFalse(self.op_cloud.delete_user('name'))
        self.assertFalse(mock_keystone.users.delete.called)

    @mock.patch.object(shade.OpenStackCloud, 'get_user')
    @mock.patch.object(shade.OperatorCloud, 'get_group')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_add_user_to_group(self, mock_keystone, mock_group, mock_user):
        mock_user.return_value = munch.Munch(dict(id=1))
        mock_group.return_value = munch.Munch(dict(id=2))
        self.op_cloud.add_user_to_group("user", "group")
        mock_keystone.users.add_to_group.assert_called_once_with(
            user=1, group=2
        )

    @mock.patch.object(shade.OpenStackCloud, 'get_user')
    @mock.patch.object(shade.OperatorCloud, 'get_group')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_is_user_in_group(self, mock_keystone, mock_group, mock_user):
        mock_user.return_value = munch.Munch(dict(id=1))
        mock_group.return_value = munch.Munch(dict(id=2))
        mock_keystone.users.check_in_group.return_value = True
        self.assertTrue(self.op_cloud.is_user_in_group("user", "group"))
        mock_keystone.users.check_in_group.assert_called_once_with(
            user=1, group=2
        )

    @mock.patch.object(shade.OpenStackCloud, 'get_user')
    @mock.patch.object(shade.OperatorCloud, 'get_group')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_remove_user_from_group(self, mock_keystone, mock_group,
                                    mock_user):
        mock_user.return_value = munch.Munch(dict(id=1))
        mock_group.return_value = munch.Munch(dict(id=2))
        self.op_cloud.remove_user_from_group("user", "group")
        mock_keystone.users.remove_from_group.assert_called_once_with(
            user=1, group=2
        )
