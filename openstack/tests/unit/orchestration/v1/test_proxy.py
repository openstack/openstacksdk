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
import six

from openstack import exceptions
from openstack.orchestration.v1 import _proxy
from openstack.orchestration.v1 import resource
from openstack.orchestration.v1 import stack
from openstack.tests.unit import test_proxy_base


class TestOrchestrationProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestOrchestrationProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_stack_create_attrs(self):
        self.verify_create(self.proxy.create_stack, stack.Stack)

    def test_stack_preview_attrs(self):
        method_kwargs = {"preview": True, "x": 1, "y": 2, "z": 3}
        self.verify_create(self.proxy.create_stack, stack.StackPreview,
                           method_kwargs=method_kwargs)

    def test_stack_find(self):
        self.verify_find(self.proxy.find_stack, stack.Stack)

    def test_stacks(self):
        self.verify_list(self.proxy.stacks, stack.Stack, paginated=False)

    def test_stack_get(self):
        self.verify_get(self.proxy.get_stack, stack.Stack)

    def test_stack_update(self):
        self.verify_update(self.proxy.update_stack, stack.Stack)

    def test_stack_delete(self):
        self.verify_delete(self.proxy.delete_stack, stack.Stack, False)

    def test_stack_delete_ignore(self):
        self.verify_delete(self.proxy.delete_stack, stack.Stack, True)

    @mock.patch.object(stack.Stack, 'from_id')
    @mock.patch.object(stack.Stack, 'find')
    def test_resources_with_stack_object(self, mock_find, mock_from):
        stack_id = '1234'
        stack_name = 'test_stack'
        stack_identity = {'id': stack_id, 'name': stack_name}
        stk = stack.Stack(attrs=stack_identity)
        mock_from.return_value = stk

        path_args = {'stack_id': stk.id, 'stack_name': stk.name}
        self.verify_list(self.proxy.resources, resource.Resource,
                         paginated=False,
                         method_args=[stk],
                         expected_kwargs={'path_args': path_args})

        self.assertEqual(0, mock_find.call_count)

    def test_resources_with_stack_name(self):
        self.verify_find(self.proxy.find_stack, stack.Stack)

    @mock.patch.object(stack.Stack, 'find')
    @mock.patch.object(resource.Resource, 'list')
    def test_resources_stack_not_found(self, mock_list, mock_find):
        stack_name = 'test_stack'
        mock_find.side_effect = exceptions.ResourceNotFound(
            'No stack found for test_stack')

        ex = self.assertRaises(exceptions.ResourceNotFound,
                               self.proxy.resources, stack_name)
        self.assertEqual('ResourceNotFound: No stack found for test_stack',
                         six.text_type(ex))
