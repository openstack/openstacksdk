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

from openstack.message.v2 import _proxy
from openstack.message.v2 import message
from openstack.message.v2 import queue
from openstack import proxy2 as proxy_base
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

    @mock.patch.object(proxy_base.BaseProxy, '_get_resource')
    def test_message_post(self, mock_get_resource):
        message_obj = message.Message(queue_name="test_queue")
        mock_get_resource.return_value = message_obj
        self._verify("openstack.message.v2.message.Message.post",
                     self.proxy.post_message,
                     method_args=["test_queue", ["msg1", "msg2"]],
                     expected_args=[["msg1", "msg2"]])
        mock_get_resource.assert_called_once_with(message.Message, None,
                                                  queue_name="test_queue")

    @mock.patch.object(proxy_base.BaseProxy, '_get_resource')
    def test_message_get(self, mock_get_resource):
        mock_get_resource.return_value = "resource_or_id"
        self._verify2("openstack.proxy2.BaseProxy._get",
                      self.proxy.get_message,
                      method_args=["test_queue", "resource_or_id"],
                      expected_args=[message.Message, "resource_or_id"])
        mock_get_resource.assert_called_once_with(message.Message,
                                                  "resource_or_id",
                                                  queue_name="test_queue")

    def test_messages(self):
        self.verify_list(self.proxy.messages, message.Message,
                         paginated=True, method_args=["test_queue"],
                         expected_kwargs={"queue_name": "test_queue"})

    @mock.patch.object(proxy_base.BaseProxy, '_get_resource')
    def test_message_delete(self, mock_get_resource):
        mock_get_resource.return_value = "resource_or_id"
        self.verify_delete(self.proxy.delete_message,
                           message.Message, False,
                           ["test_queue", "resource_or_id"])
        mock_get_resource.assert_called_once_with(message.Message,
                                                  "resource_or_id",
                                                  queue_name="test_queue")

    @mock.patch.object(proxy_base.BaseProxy, '_get_resource')
    def test_message_delete_ignore(self, mock_get_resource):
        mock_get_resource.return_value = "resource_or_id"
        self.verify_delete(self.proxy.delete_message,
                           message.Message, True,
                           ["test_queue", "resource_or_id"])
        mock_get_resource.assert_called_once_with(message.Message,
                                                  "resource_or_id",
                                                  queue_name="test_queue")
