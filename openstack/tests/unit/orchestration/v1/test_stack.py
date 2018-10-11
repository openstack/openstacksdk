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
from openstack.tests.unit import base

from openstack import exceptions
from openstack.orchestration.v1 import stack
from openstack import resource


FAKE_ID = 'ce8ae86c-9810-4cb1-8888-7fb53bc523bf'
FAKE_NAME = 'test_stack'
FAKE = {
    'capabilities': '1',
    'creation_time': '2015-03-09T12:15:57.233772',
    'description': '3',
    'disable_rollback': True,
    'id': FAKE_ID,
    'links': [{
        'href': 'stacks/%s/%s' % (FAKE_NAME, FAKE_ID),
        'rel': 'self'}],
    'notification_topics': '7',
    'outputs': '8',
    'parameters': {'OS::stack_id': '9'},
    'name': FAKE_NAME,
    'status': '11',
    'status_reason': '12',
    'tags': ['FOO', 'bar:1'],
    'template_description': '13',
    'template_url': 'http://www.example.com/wordpress.yaml',
    'timeout_mins': '14',
    'updated_time': '2015-03-09T12:30:00.000000',
}
FAKE_CREATE_RESPONSE = {
    'stack': {
        'id': FAKE_ID,
        'links': [{
            'href': 'stacks/%s/%s' % (FAKE_NAME, FAKE_ID),
            'rel': 'self'}]}
}


class TestStack(base.TestCase):

    def test_basic(self):
        sot = stack.Stack()
        self.assertEqual('stack', sot.resource_key)
        self.assertEqual('stacks', sot.resources_key)
        self.assertEqual('/stacks', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = stack.Stack(**FAKE)
        self.assertEqual(FAKE['capabilities'], sot.capabilities)
        self.assertEqual(FAKE['creation_time'], sot.created_at)
        self.assertEqual(FAKE['description'], sot.description)
        self.assertTrue(sot.is_rollback_disabled)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['notification_topics'],
                         sot.notification_topics)
        self.assertEqual(FAKE['outputs'], sot.outputs)
        self.assertEqual(FAKE['parameters'], sot.parameters)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['status'], sot.status)
        self.assertEqual(FAKE['status_reason'], sot.status_reason)
        self.assertEqual(FAKE['tags'], sot.tags)
        self.assertEqual(FAKE['template_description'],
                         sot.template_description)
        self.assertEqual(FAKE['template_url'], sot.template_url)
        self.assertEqual(FAKE['timeout_mins'], sot.timeout_mins)
        self.assertEqual(FAKE['updated_time'], sot.updated_at)

    @mock.patch.object(resource.Resource, 'create')
    def test_create(self, mock_create):
        sess = mock.Mock()
        sot = stack.Stack(FAKE)

        res = sot.create(sess)

        mock_create.assert_called_once_with(sess, prepend_key=False)
        self.assertEqual(mock_create.return_value, res)

    @mock.patch.object(resource.Resource, 'commit')
    def test_commit(self, mock_commit):
        sess = mock.Mock()
        sot = stack.Stack(FAKE)

        res = sot.commit(sess)

        mock_commit.assert_called_once_with(sess, prepend_key=False,
                                            has_body=False)
        self.assertEqual(mock_commit.return_value, res)

    def test_check(self):
        sess = mock.Mock()
        sot = stack.Stack(**FAKE)
        sot._action = mock.Mock()
        body = {'check': ''}

        sot.check(sess)

        sot._action.assert_called_with(sess, body)

    @mock.patch.object(resource.Resource, 'fetch')
    def test_fetch(self, mock_fetch):
        sess = mock.Mock()
        sot = stack.Stack(**FAKE)
        deleted_stack = mock.Mock(id=FAKE_ID, status='DELETE_COMPLETE')
        normal_stack = mock.Mock(status='CREATE_COMPLETE')
        mock_fetch.side_effect = [
            normal_stack,
            exceptions.ResourceNotFound(message='oops'),
            deleted_stack,
        ]

        self.assertEqual(normal_stack, sot.fetch(sess))
        ex = self.assertRaises(exceptions.ResourceNotFound, sot.fetch, sess)
        self.assertEqual('oops', six.text_type(ex))
        ex = self.assertRaises(exceptions.ResourceNotFound, sot.fetch, sess)
        self.assertEqual('No stack found for %s' % FAKE_ID,
                         six.text_type(ex))


class TestStackPreview(base.TestCase):

    def test_basic(self):
        sot = stack.StackPreview()

        self.assertEqual('/stacks/preview', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
