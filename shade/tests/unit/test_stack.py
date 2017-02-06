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
from shade._heat import event_utils
from shade._heat import template_utils
from shade import meta
from shade.tests import fakes
from shade.tests.unit import base


class TestStack(base.TestCase):

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

    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_search_stacks(self, mock_heat):
        fake_stacks = [
            fakes.FakeStack('001', 'stack1'),
            fakes.FakeStack('002', 'stack2'),
        ]
        mock_heat.stacks.list.return_value = fake_stacks
        stacks = self.cloud.search_stacks()
        mock_heat.stacks.list.assert_called_once_with()
        self.assertEqual(meta.obj_list_to_dict(fake_stacks), stacks)

    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_search_stacks_filters(self, mock_heat):
        fake_stacks = [
            fakes.FakeStack('001', 'stack1', status='GOOD'),
            fakes.FakeStack('002', 'stack2', status='BAD'),
        ]
        mock_heat.stacks.list.return_value = fake_stacks
        filters = {'stack_status': 'GOOD'}
        stacks = self.cloud.search_stacks(filters=filters)
        mock_heat.stacks.list.assert_called_once_with()
        self.assertEqual(meta.obj_list_to_dict(fake_stacks[:1]), stacks)

    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_search_stacks_exception(self, mock_heat):
        mock_heat.stacks.list.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error fetching stack list"
        ):
            self.cloud.search_stacks()

    @mock.patch.object(shade.OpenStackCloud, 'get_stack')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_delete_stack(self, mock_heat, mock_get):
        stack = {'id': 'stack_id', 'name': 'stack_name'}
        mock_get.return_value = stack
        self.assertTrue(self.cloud.delete_stack('stack_name'))
        mock_get.assert_called_once_with('stack_name')
        mock_heat.stacks.delete.assert_called_once_with(stack['id'])

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
        mock_heat.stacks.delete.side_effect = Exception('ouch')
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Failed to delete stack stack_name: ouch"
        ):
            self.cloud.delete_stack('stack_name')

    @mock.patch.object(event_utils, 'poll_for_events')
    @mock.patch.object(shade.OpenStackCloud, 'get_stack')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_delete_stack_wait(self, mock_heat, mock_get, mock_poll):
        stack = {'id': 'stack_id', 'name': 'stack_name'}
        mock_get.side_effect = (stack, None)
        self.assertTrue(self.cloud.delete_stack('stack_name', wait=True))
        mock_heat.stacks.delete.assert_called_once_with(stack['id'])
        self.assertEqual(2, mock_get.call_count)
        self.assertEqual(1, mock_poll.call_count)

    @mock.patch.object(event_utils, 'poll_for_events')
    @mock.patch.object(shade.OpenStackCloud, 'get_stack')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_delete_stack_wait_failed(self, mock_heat, mock_get, mock_poll):
        stack = {'id': 'stack_id', 'name': 'stack_name'}
        stack_failed = {'id': 'stack_id', 'name': 'stack_name',
                        'stack_status': 'DELETE_FAILED',
                        'stack_status_reason': 'ouch'}
        mock_get.side_effect = (stack, stack_failed)
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Failed to delete stack stack_name: ouch"
        ):
            self.cloud.delete_stack('stack_name', wait=True)
        mock_heat.stacks.delete.assert_called_once_with(stack['id'])
        self.assertEqual(2, mock_get.call_count)
        self.assertEqual(1, mock_poll.call_count)

    @mock.patch.object(template_utils, 'get_template_contents')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_create_stack(self, mock_heat, mock_template):
        mock_template.return_value = ({}, {})
        self.cloud.create_stack('stack_name')
        self.assertTrue(mock_template.called)
        mock_heat.stacks.create.assert_called_once_with(
            stack_name='stack_name',
            disable_rollback=False,
            environment={},
            parameters={},
            template={},
            files={},
            timeout_mins=60,
        )

    @mock.patch.object(event_utils, 'poll_for_events')
    @mock.patch.object(template_utils, 'get_template_contents')
    @mock.patch.object(shade.OpenStackCloud, 'get_stack')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_create_stack_wait(self, mock_heat, mock_get, mock_template,
                               mock_poll):
        stack = {'id': 'stack_id', 'name': 'stack_name'}
        mock_template.return_value = ({}, {})
        mock_get.return_value = stack
        ret = self.cloud.create_stack('stack_name', wait=True)
        self.assertTrue(mock_template.called)
        mock_heat.stacks.create.assert_called_once_with(
            stack_name='stack_name',
            disable_rollback=False,
            environment={},
            parameters={},
            template={},
            files={},
            timeout_mins=60,
        )
        self.assertEqual(1, mock_get.call_count)
        self.assertEqual(1, mock_poll.call_count)
        self.assertEqual(stack, ret)

    @mock.patch.object(template_utils, 'get_template_contents')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_update_stack(self, mock_heat, mock_template):
        mock_template.return_value = ({}, {})
        self.cloud.update_stack('stack_name')
        self.assertTrue(mock_template.called)
        mock_heat.stacks.update.assert_called_once_with(
            stack_id='stack_name',
            disable_rollback=False,
            environment={},
            parameters={},
            template={},
            files={},
            timeout_mins=60,
        )

    @mock.patch.object(event_utils, 'poll_for_events')
    @mock.patch.object(template_utils, 'get_template_contents')
    @mock.patch.object(shade.OpenStackCloud, 'get_stack')
    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_update_stack_wait(self, mock_heat, mock_get, mock_template,
                               mock_poll):
        stack = {'id': 'stack_id', 'name': 'stack_name'}
        mock_template.return_value = ({}, {})
        mock_get.return_value = stack
        ret = self.cloud.update_stack('stack_name', wait=True)
        self.assertTrue(mock_template.called)
        mock_heat.stacks.update.assert_called_once_with(
            stack_id='stack_name',
            disable_rollback=False,
            environment={},
            parameters={},
            template={},
            files={},
            timeout_mins=60,
        )
        self.assertEqual(1, mock_get.call_count)
        self.assertEqual(1, mock_poll.call_count)
        self.assertEqual(stack, ret)

    @mock.patch.object(shade.OpenStackCloud, 'heat_client')
    def test_get_stack(self, mock_heat):
        stack = fakes.FakeStack('azerty', 'stack',)
        mock_heat.stacks.get.return_value = stack
        res = self.cloud.get_stack('stack')
        self.assertIsNotNone(res)
        self.assertEqual(stack.stack_name, res['stack_name'])
        self.assertEqual(stack.stack_name, res['name'])
        self.assertEqual(stack.stack_status, res['stack_status'])
