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
import testtools

import shade
from shade import meta
from shade.tests import fakes
from shade.tests.unit import base


class TestStack(base.TestCase):

    def setUp(self):
        super(TestStack, self).setUp()
        self.cloud = shade.openstack_cloud(validate=False)

    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_list_stacks(self, mock_heat):
        fake_stacks = [
            fakes.FakeStack('001', 'stack1'),
            fakes.FakeStack('002', 'stack2'),
        ]
        mock_heat.stacks.list.return_value = fake_stacks
        stacks = self.cloud.list_stacks()
        mock_heat.stacks.list.assert_called_once_with()
        self.assertEqual(meta.obj_list_to_dict(fake_stacks), stacks)

    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_list_stacks_exception(self, mock_heat):
        mock_heat.stacks.list.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error fetching stack list"
        ):
            self.cloud.list_stacks()

    @mock.patch.object(shade.OpenStackCloud, 'get_stack')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_delete_stack(self, mock_heat, mock_get):
        stack = {'id': 'stack_id', 'name': 'stack_name'}
        mock_get.return_value = stack
        self.assertTrue(self.cloud.delete_stack('stack_name'))
        mock_get.assert_called_once_with('stack_name')
        mock_heat.stacks.delete.assert_called_once_with(id=stack['id'])

    @mock.patch.object(shade.OpenStackCloud, 'get_stack')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_delete_stack_not_found(self, mock_heat, mock_get):
        mock_get.return_value = None
        self.assertFalse(self.cloud.delete_stack('stack_name'))
        mock_get.assert_called_once_with('stack_name')
        self.assertFalse(mock_heat.stacks.delete.called)

    @mock.patch.object(shade.OpenStackCloud, 'get_stack')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_delete_stack_exception(self, mock_heat, mock_get):
        stack = {'id': 'stack_id', 'name': 'stack_name'}
        mock_get.return_value = stack
        mock_heat.stacks.delete.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Failed to delete stack %s" % stack['id']
        ):
            self.cloud.delete_stack('stack_name')
