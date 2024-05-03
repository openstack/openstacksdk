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

from openstack.message.v2 import message
from openstack.tests.unit import base

FAKE1 = {
    'age': 456,
    'body': {
        'current_bytes': '0',
        'event': 'BackupProgress',
        'total_bytes': '99614720',
    },
    'id': '578ee000508f153f256f717d',
    'href': '/v2/queues/queue1/messages/578ee000508f153f256f717d',
    'ttl': 3600,
    'queue_name': 'queue1',
}


FAKE2 = {
    'age': 456,
    'body': {
        'current_bytes': '0',
        'event': 'BackupProgress',
        'total_bytes': '99614720',
    },
    'id': '578ee000508f153f256f717d',
    'href': '/v2/queues/queue1/messages/578ee000508f153f256f717d',
    'ttl': 3600,
    'queue_name': 'queue1',
    'client_id': 'OLD_CLIENT_ID',
    'project_id': 'OLD_PROJECT_ID',
}


class TestMessage(base.TestCase):
    def test_basic(self):
        sot = message.Message()
        self.assertEqual('messages', sot.resources_key)
        self.assertEqual('/queues/%(queue_name)s/messages', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = message.Message.new(**FAKE2)
        self.assertEqual(FAKE2['age'], sot.age)
        self.assertEqual(FAKE2['body'], sot.body)
        self.assertEqual(FAKE2['id'], sot.id)
        self.assertEqual(FAKE2['href'], sot.href)
        self.assertEqual(FAKE2['ttl'], sot.ttl)
        self.assertEqual(FAKE2['queue_name'], sot.queue_name)
        self.assertEqual(FAKE2['client_id'], sot.client_id)
        self.assertEqual(FAKE2['project_id'], sot.project_id)

    @mock.patch.object(uuid, 'uuid4')
    def test_post(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.post.return_value = resp
        resources = [
            '/v2/queues/queue1/messages/578ee000508f153f256f717d'
            '/v2/queues/queue1/messages/579edd6c368cb61de9a7e233'
        ]
        resp.json.return_value = {'resources': resources}
        sess.get_project_id.return_value = 'NEW_PROJECT_ID'
        mock_uuid.return_value = 'NEW_CLIENT_ID'
        messages = [
            {'body': {'key': 'value1'}, 'ttl': 3600},
            {'body': {'key': 'value2'}, 'ttl': 1800},
        ]

        sot = message.Message(**FAKE1)
        res = sot.post(sess, messages)

        url = '/queues/{queue}/messages'.format(queue=FAKE1['queue_name'])
        headers = {
            'Client-ID': 'NEW_CLIENT_ID',
            'X-PROJECT-ID': 'NEW_PROJECT_ID',
        }
        sess.post.assert_called_once_with(
            url, headers=headers, json={'messages': messages}
        )
        sess.get_project_id.assert_called_once_with()
        resp.json.assert_called_once_with()
        self.assertEqual(resources, res)

    def test_post_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.post.return_value = resp
        resources = [
            '/v2/queues/queue1/messages/578ee000508f153f256f717d'
            '/v2/queues/queue1/messages/579edd6c368cb61de9a7e233'
        ]
        resp.json.return_value = {'resources': resources}
        messages = [
            {'body': {'key': 'value1'}, 'ttl': 3600},
            {'body': {'key': 'value2'}, 'ttl': 1800},
        ]

        sot = message.Message(**FAKE2)
        res = sot.post(sess, messages)

        url = '/queues/{queue}/messages'.format(queue=FAKE2['queue_name'])
        headers = {
            'Client-ID': 'OLD_CLIENT_ID',
            'X-PROJECT-ID': 'OLD_PROJECT_ID',
        }
        sess.post.assert_called_once_with(
            url, headers=headers, json={'messages': messages}
        )
        resp.json.assert_called_once_with()
        self.assertEqual(resources, res)

    @mock.patch.object(uuid, 'uuid4')
    def test_get(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.get.return_value = resp
        sess.get_project_id.return_value = 'NEW_PROJECT_ID'
        mock_uuid.return_value = 'NEW_CLIENT_ID'

        sot = message.Message(**FAKE1)
        sot._translate_response = mock.Mock()
        res = sot.fetch(sess)

        url = 'queues/{queue}/messages/{message}'.format(
            queue=FAKE1['queue_name'],
            message=FAKE1['id'],
        )
        headers = {
            'Client-ID': 'NEW_CLIENT_ID',
            'X-PROJECT-ID': 'NEW_PROJECT_ID',
        }
        sess.get.assert_called_with(url, headers=headers, skip_cache=False)
        sess.get_project_id.assert_called_once_with()
        sot._translate_response.assert_called_once_with(resp)
        self.assertEqual(sot, res)

    def test_get_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.get.return_value = resp

        sot = message.Message(**FAKE1)
        sot._translate_response = mock.Mock()
        res = sot.fetch(sess)

        url = 'queues/{queue}/messages/{message}'.format(
            queue=FAKE2['queue_name'],
            message=FAKE2['id'],
        )
        sot = message.Message(**FAKE2)
        sot._translate_response = mock.Mock()
        res = sot.fetch(sess)
        headers = {
            'Client-ID': 'OLD_CLIENT_ID',
            'X-PROJECT-ID': 'OLD_PROJECT_ID',
        }
        sess.get.assert_called_with(url, headers=headers, skip_cache=False)
        sot._translate_response.assert_called_once_with(resp)
        self.assertEqual(sot, res)

    @mock.patch.object(uuid, 'uuid4')
    def test_delete_unclaimed(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.delete.return_value = resp
        sess.get_project_id.return_value = 'NEW_PROJECT_ID'
        mock_uuid.return_value = 'NEW_CLIENT_ID'

        sot = message.Message(**FAKE1)
        sot.claim_id = None
        sot._translate_response = mock.Mock()
        sot.delete(sess)

        url = 'queues/{queue}/messages/{message}'.format(
            queue=FAKE1['queue_name'],
            message=FAKE1['id'],
        )
        headers = {
            'Client-ID': 'NEW_CLIENT_ID',
            'X-PROJECT-ID': 'NEW_PROJECT_ID',
        }
        sess.delete.assert_called_with(url, headers=headers)
        sess.get_project_id.assert_called_once_with()
        sot._translate_response.assert_called_once_with(resp, has_body=False)

    @mock.patch.object(uuid, 'uuid4')
    def test_delete_claimed(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.delete.return_value = resp
        sess.get_project_id.return_value = 'NEW_PROJECT_ID'
        mock_uuid.return_value = 'NEW_CLIENT_ID'

        sot = message.Message(**FAKE1)
        sot.claim_id = 'CLAIM_ID'
        sot._translate_response = mock.Mock()
        sot.delete(sess)

        url = 'queues/{queue}/messages/{message}?claim_id={cid}'.format(
            queue=FAKE1['queue_name'],
            message=FAKE1['id'],
            cid='CLAIM_ID',
        )
        headers = {
            'Client-ID': 'NEW_CLIENT_ID',
            'X-PROJECT-ID': 'NEW_PROJECT_ID',
        }
        sess.delete.assert_called_with(url, headers=headers)
        sess.get_project_id.assert_called_once_with()
        sot._translate_response.assert_called_once_with(resp, has_body=False)

    def test_delete_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.delete.return_value = resp

        sot = message.Message(**FAKE2)
        sot.claim_id = None
        sot._translate_response = mock.Mock()
        sot.delete(sess)

        url = 'queues/{queue}/messages/{message}'.format(
            queue=FAKE2['queue_name'],
            message=FAKE2['id'],
        )
        headers = {
            'Client-ID': 'OLD_CLIENT_ID',
            'X-PROJECT-ID': 'OLD_PROJECT_ID',
        }
        sess.delete.assert_called_with(url, headers=headers)
        sot._translate_response.assert_called_once_with(resp, has_body=False)
