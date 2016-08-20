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

import shade
from shade.tests.unit import base
from shade.tests import fakes


class TestGroups(base.TestCase):

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_groups(self, mock_keystone):
        self.op_cloud.list_groups()
        mock_keystone.groups.list.assert_called_once_with()

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_get_group(self, mock_keystone):
        self.op_cloud.get_group('1234')
        mock_keystone.groups.list.assert_called_once_with()

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_group(self, mock_keystone):
        mock_keystone.groups.list.return_value = [
            fakes.FakeGroup('1234', 'name', 'desc')
        ]
        self.assertTrue(self.op_cloud.delete_group('1234'))
        mock_keystone.groups.list.assert_called_once_with()
        mock_keystone.groups.delete.assert_called_once_with(
            group='1234'
        )

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_group(self, mock_keystone):
        self.op_cloud.create_group('test-group', 'test desc')
        mock_keystone.groups.create.assert_called_once_with(
            name='test-group', description='test desc', domain=None
        )

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_update_group(self, mock_keystone):
        mock_keystone.groups.list.return_value = [
            fakes.FakeGroup('1234', 'name', 'desc')
        ]
        self.op_cloud.update_group('1234', 'test-group', 'test desc')
        mock_keystone.groups.list.assert_called_once_with()
        mock_keystone.groups.update.assert_called_once_with(
            group='1234', name='test-group', description='test desc'
        )
