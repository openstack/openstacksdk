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
from openstack.tests import test_proxy_base


class TestOrchestrationProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestOrchestrationProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_stack_find(self):
        self.verify_find('openstack.orchestration.v1.stack.Stack.find',
                         self.proxy.find_stack)

    def test_stack_list(self):
        self.verify_list('openstack.orchestration.v1.stack.Stack.list',
                         self.proxy.list_stacks)

    def test_stack_get(self):
        self.verify_get('openstack.orchestration.v1.stack.Stack.get',
                        self.proxy.get_stack)
