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

from openstack.orchestration.v1 import _proxy
from openstack.orchestration.v1 import stack
from openstack.tests.unit import test_proxy_base


class TestOrchestrationProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestOrchestrationProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_stack_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_stack,
                            method_kwargs=kwargs,
                            expected_args=[stack.Stack],
                            expected_kwargs=kwargs)

    def test_stack_find(self):
        self.verify_find('openstack.orchestration.v1.stack.Stack.find',
                         self.proxy.find_stack)

    def test_stack_list(self):
        self.verify_list('openstack.orchestration.v1.stack.Stack.list',
                         self.proxy.list_stacks)

    def test_stack_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_stack,
                         method_args=["resource_or_id"],
                         expected_args=[stack.Stack, "resource_or_id"])

    def test_stack_delete(self):
        self.verify_delete2(stack.Stack, self.proxy.delete_stack, False)

    def test_stack_delete_ignore(self):
        self.verify_delete2(stack.Stack, self.proxy.delete_stack, True)

    def test_stack_wait_for(self):
        value = stack.Stack(attrs={'id': '1234'})
        self.verify_wait_for_status(
            'openstack.resource.wait_for_status',
            self.proxy.wait_for_stack,
            method_args=[value],
            expected_args=[value, 'CREATE_COMPLETE', ['CREATE_FAILED'],
                           2, 120])
