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

from openstack.orchestration.v1 import stack


FAKE_ID = 'ce8ae86c-9810-4cb1-8888-7fb53bc523bf'
FAKE_NAME = 'test_stack'
FAKE = {
    'capabilities': '1',
    'creation_time': '2',
    'description': '3',
    'disable_rollback': True,
    'id': FAKE_ID,
    'links': '6',
    'notification_topics': '7',
    'outputs': '8',
    'parameters': {'OS::stack_id': '9'},
    'name': FAKE_NAME,
    'status': '11',
    'status_reason': '12',
    'template_description': '13',
    'template_url': 'http://www.example.com/wordpress.yaml',
    'timeout_mins': '14',
    'updated_time': '15',
}
FAKE_CREATE_RESPONSE = {
    'stack': {
        'id': FAKE_ID,
        'links': [{
            'href': 'stacks/%s/%s' % (FAKE_NAME, FAKE_ID),
            'rel': 'self'}]}
}


class TestStack(testtools.TestCase):

    def test_basic(self):
        sot = stack.Stack()
        self.assertEqual('stack', sot.resource_key)
        self.assertEqual('stacks', sot.resources_key)
        self.assertEqual('/stacks', sot.base_path)
        self.assertEqual('orchestration', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = stack.Stack(FAKE)
        self.assertEqual(FAKE['capabilities'], sot.capabilities)
        self.assertEqual(FAKE['creation_time'], sot.created_at)
        self.assertEqual(FAKE['description'], sot.description)
        self.assertEqual(FAKE['disable_rollback'], sot.disable_rollback)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['notification_topics'],
                         sot.notification_topics)
        self.assertEqual(FAKE['outputs'], sot.outputs)
        self.assertEqual(FAKE['parameters'], sot.parameters)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['status'], sot.status)
        self.assertEqual(FAKE['status_reason'],
                         sot.status_reason)
        self.assertEqual(FAKE['template_description'],
                         sot.template_description)
        self.assertEqual(FAKE['template_url'],
                         sot.template_url)
        self.assertEqual(FAKE['timeout_mins'], sot.timeout_mins)
        self.assertEqual(FAKE['updated_time'], sot.updated_at)

    def test_create(self):
        resp = mock.MagicMock()
        resp.body = FAKE_CREATE_RESPONSE
        sess = mock.Mock()
        sess.post = mock.MagicMock()
        sess.post.return_value = resp
        sot = stack.Stack(FAKE)

        sot.create(sess)

        url = '/stacks'
        body = FAKE.copy()
        body.pop('id')
        body.pop('name')
        sess.post.assert_called_with(url, service=sot.service, json=body)
        self.assertEqual(FAKE_ID, sot.id)
        self.assertEqual(FAKE_NAME, sot.name)

    def test_check(self):
        session_mock = mock.MagicMock()
        sot = stack.Stack(FAKE)
        sot._action = mock.MagicMock()
        body = {'check': ''}
        sot.check(session_mock)
        sot._action.assert_called_with(session_mock, body)
