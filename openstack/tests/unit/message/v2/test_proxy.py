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

from openstack.message.v2 import _proxy
from openstack.message.v2 import queue
from openstack.tests.unit import test_proxy_base2

QUEUE_NAME = 'test_queue'


class TestMessageProxy(test_proxy_base2.TestProxyBase):
    def setUp(self):
        super(TestMessageProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_queue_create(self):
        self.verify_create(self.proxy.create_queue, queue.Queue)

    def test_queue_get(self):
        self.verify_get(self.proxy.get_queue, queue.Queue)

    def test_queues(self):
        self.verify_list(self.proxy.queues, queue.Queue, paginated=True)

    def test_queue_delete(self):
        self.verify_delete(self.proxy.delete_queue, queue.Queue, False)

    def test_queue_delete_ignore(self):
        self.verify_delete(self.proxy.delete_queue, queue.Queue, True)
