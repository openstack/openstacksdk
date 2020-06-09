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

from unittest import mock
import uuid

from openstack.message.v2 import queue
from openstack.tests.unit import base

FAKE1 = {
    'name': 'test_queue',
    'description': 'Queue used for test.',
    '_default_message_ttl': 3600,
    '_max_messages_post_size': 262144
}


FAKE2 = {
    'name': 'test_queue',
    'description': 'Queue used for test.',
    '_default_message_ttl': 3600,
    '_max_messages_post_size': 262144,
    'client_id': 'OLD_CLIENT_ID',
    'project_id': 'OLD_PROJECT_ID'
}


class TestQueue(base.TestCase):
    def test_basic(self):
        sot = queue.Queue()
        self.assertEqual('queues', sot.resources_key)
        self.assertEqual('/queues', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = queue.Queue.new(**FAKE2)
        self.assertEqual(FAKE1['description'], sot.description)
        self.assertEqual(FAKE1['name'], sot.name)
        self.assertEqual(FAKE1['name'], sot.id)
        self.assertEqual(FAKE1['_default_message_ttl'],
                         sot.default_message_ttl)
        self.assertEqual(FAKE1['_max_messages_post_size'],
                         sot.max_messages_post_size)
        self.assertEqual(FAKE2['client_id'], sot.client_id)
        self.assertEqual(FAKE2['project_id'], sot.project_id)

    @mock.patch.object(uuid, 'uuid4')
    def test_create(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.put.return_value = resp
        sess.get_project_id.return_value = 'NEW_PROJECT_ID'
        mock_uuid.return_value = 'NEW_CLIENT_ID'

        sot = queue.Queue(**FAKE1)
        sot._translate_response = mock.Mock()
        res = sot.create(sess)

        url = 'queues/%s' % FAKE1['name']
        headers = {'Client-ID': 'NEW_CLIENT_ID',
                   'X-PROJECT-ID': 'NEW_PROJECT_ID'}
        sess.put.assert_called_with(url,
                                    headers=headers, json=FAKE1)
        sess.get_project_id.assert_called_once_with()
        sot._translate_response.assert_called_once_with(resp, has_body=False)
        self.assertEqual(sot, res)

    def test_create_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.put.return_value = resp

        sot = queue.Queue(**FAKE2)
        sot._translate_response = mock.Mock()
        res = sot.create(sess)

        url = 'queues/%s' % FAKE2['name']
        headers = {'Client-ID': 'OLD_CLIENT_ID',
                   'X-PROJECT-ID': 'OLD_PROJECT_ID'}
        sess.put.assert_called_with(url,
                                    headers=headers, json=FAKE1)
        sot._translate_response.assert_called_once_with(resp, has_body=False)
        self.assertEqual(sot, res)

    @mock.patch.object(uuid, 'uuid4')
    def test_get(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.get.return_value = resp
        sess.get_project_id.return_value = 'NEW_PROJECT_ID'
        mock_uuid.return_value = 'NEW_CLIENT_ID'

        sot = queue.Queue(**FAKE1)
        sot._translate_response = mock.Mock()
        res = sot.fetch(sess)

        url = 'queues/%s' % FAKE1['name']
        headers = {'Client-ID': 'NEW_CLIENT_ID',
                   'X-PROJECT-ID': 'NEW_PROJECT_ID'}
        sess.get.assert_called_with(url,
                                    headers=headers)
        sess.get_project_id.assert_called_once_with()
        sot._translate_response.assert_called_once_with(resp)
        self.assertEqual(sot, res)

    def test_get_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.get.return_value = resp

        sot = queue.Queue(**FAKE2)
        sot._translate_response = mock.Mock()
        res = sot.fetch(sess)

        url = 'queues/%s' % FAKE2['name']
        headers = {'Client-ID': 'OLD_CLIENT_ID',
                   'X-PROJECT-ID': 'OLD_PROJECT_ID'}
        sess.get.assert_called_with(url,
                                    headers=headers)
        sot._translate_response.assert_called_once_with(resp)
        self.assertEqual(sot, res)

    @mock.patch.object(uuid, 'uuid4')
    def test_delete(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.delete.return_value = resp
        sess.get_project_id.return_value = 'NEW_PROJECT_ID'
        mock_uuid.return_value = 'NEW_CLIENT_ID'

        sot = queue.Queue(**FAKE1)
        sot._translate_response = mock.Mock()
        sot.delete(sess)

        url = 'queues/%s' % FAKE1['name']
        headers = {'Client-ID': 'NEW_CLIENT_ID',
                   'X-PROJECT-ID': 'NEW_PROJECT_ID'}
        sess.delete.assert_called_with(url,
                                       headers=headers)
        sess.get_project_id.assert_called_once_with()
        sot._translate_response.assert_called_once_with(resp, has_body=False)

    def test_delete_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.delete.return_value = resp

        sot = queue.Queue(**FAKE2)
        sot._translate_response = mock.Mock()
        sot.delete(sess)

        url = 'queues/%s' % FAKE2['name']
        headers = {'Client-ID': 'OLD_CLIENT_ID',
                   'X-PROJECT-ID': 'OLD_PROJECT_ID'}
        sess.delete.assert_called_with(url,
                                       headers=headers)
        sot._translate_response.assert_called_once_with(resp, has_body=False)
