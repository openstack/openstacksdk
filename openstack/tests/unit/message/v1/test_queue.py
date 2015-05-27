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

from openstack.message.v1 import queue


FAKE_NAME = 'test_queue'
FAKE = {
    'name': FAKE_NAME,
}


class TestQueue(testtools.TestCase):

    def test_basic(self):
        sot = queue.Queue()
        self.assertEqual('queues', sot.resources_key)
        self.assertEqual('/queues', sot.base_path)
        self.assertEqual('messaging', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = queue.Queue(FAKE)
        self.assertEqual(FAKE['name'], sot.name)

    def test_create(self):
        sess = mock.Mock()
        sess.put = mock.Mock()
        sess.put.return_value = mock.Mock()
        sot = queue.Queue(FAKE)

        sot.create(sess)

        url = 'queues/%s' % FAKE_NAME
        headers = {'Accept': ''}
        sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                    headers=headers)
        self.assertEqual(FAKE_NAME, sot.id)
        self.assertEqual(FAKE_NAME, sot.name)
