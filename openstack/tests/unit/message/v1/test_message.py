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

import json

import mock
import testtools

from openstack.message.v1 import message

CLIENT = '3381af92-2b9e-11e3-b191-71861300734c'
QUEUE = 'test_queue'
FAKE = {
    'ttl': 300,
    'body': {'key': 'value'}
}
FAKE_HREF = {
    'href': '/v1/queues/test_queue/messages/1234',
    'ttl': 300,
    'body': {'key': 'value'}
}


class TestMessage(testtools.TestCase):

    def test_basic(self):
        sot = message.Message()
        self.assertEqual('messages', sot.resources_key)
        self.assertEqual('/queues/%(queue_name)s/messages', sot.base_path)
        self.assertEqual('messaging', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = message.Message(FAKE)
        self.assertEqual(FAKE['ttl'], sot.ttl)
        self.assertEqual(FAKE['body'], sot.body)

    def test_create(self):
        sess = mock.Mock()
        obj = mock.Mock()
        obj.json = mock.Mock(return_value={'resources': {'k': 'v'}})
        sess.post = mock.Mock(return_value=obj)
        sot = message.Message()

        msg = message.Message.new(client_id=CLIENT, queue_name=QUEUE, **FAKE)
        sot.create_messages(sess, [msg])

        url = '/queues/%s/messages' % QUEUE
        sess.post.assert_called_with(
            url, endpoint_filter=sot.service,
            headers={'Client-ID': CLIENT},
            data=mock.ANY)

        args, kwargs = sess.post.call_args
        self.assertIn("data", kwargs)
        self.assertDictEqual(json.loads(kwargs["data"])[0], FAKE)

    def test_delete(self):
        sess = mock.Mock()
        sess.delete = mock.Mock()
        sess.delete.return_value = mock.Mock()
        sot = message.Message()

        sot.delete_by_id(
            sess, message.Message.new(client_id=CLIENT,
                                      queue_name=QUEUE,
                                      **FAKE_HREF))

        url = '/queues/%s/messages/1234' % QUEUE
        sess.delete.assert_called_with(
            url, endpoint_filter=sot.service,
            headers={'Client-ID': CLIENT, 'Accept': ''})
