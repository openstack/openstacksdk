# -*- coding: utf-8 -*-

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

import shade
from shade.tests.unit import base


class TestUsers(base.TestCase):

    def setUp(self):
        super(TestUsers, self).setUp()
        self.cloud = shade.operator_cloud(validate=False)

    @mock.patch.object(shade.OpenStackCloud, 'get_user')
    @mock.patch.object(shade.OperatorCloud, 'get_group')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_add_user_to_group(self, mock_keystone, mock_group, mock_user):
        mock_user.return_value = munch.Munch(dict(id=1))
        mock_group.return_value = munch.Munch(dict(id=2))
        self.cloud.add_user_to_group("user", "group")
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
        self.assertTrue(self.cloud.is_user_in_group("user", "group"))
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
        self.cloud.remove_user_from_group("user", "group")
        mock_keystone.users.remove_from_group.assert_called_once_with(
            user=1, group=2
        )
