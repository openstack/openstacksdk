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

import datetime

import mock
import six
import testtools

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


class TestStack(testtools.TestCase):

    def test_basic(self):
        sot = stack.Stack()
        self.assertEqual('stack', sot.resource_key)
        self.assertEqual('stacks', sot.resources_key)
        self.assertEqual('/stacks', sot.base_path)
        self.assertEqual('orchestration', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = stack.Stack(FAKE)
        self.assertEqual(FAKE['capabilities'], sot.capabilities)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
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
        self.assertEqual(FAKE['status_reason'],
                         sot.status_reason)
        self.assertEqual(FAKE['template_description'],
                         sot.template_description)
        self.assertEqual(FAKE['template_url'],
                         sot.template_url)
        self.assertEqual(FAKE['timeout_mins'], sot.timeout_mins)
        dt = datetime.datetime(2015, 3, 9, 12, 30, 00, 000000).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))

    def test_create(self):
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=FAKE_CREATE_RESPONSE)
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        sot = stack.Stack(FAKE)

        sot.create(sess)

        url = '/stacks'
        body = sot._attrs.copy()
        body.pop('id', None)
        body.pop('name', None)
        sess.post.assert_called_with(url, endpoint_filter=sot.service,
                                     json=body)
        self.assertEqual(FAKE_ID, sot.id)
        self.assertEqual(FAKE_NAME, sot.name)

    def test_preview(self):
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=FAKE_CREATE_RESPONSE)
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        attrs = FAKE.copy()
        sot = stack.StackPreview(attrs)

        sot.create(sess)

        url = '/stacks/preview'
        body = sot._attrs.copy()
        body.pop('id', None)
        body.pop('name', None)
        sess.post.assert_called_with(url, endpoint_filter=sot.service,
                                     json=body)
        self.assertEqual(FAKE_ID, sot.id)
        self.assertEqual(FAKE_NAME, sot.name)

    def test_update(self):
        # heat responds to update request with an 202 status code
        resp_update = mock.Mock()
        resp_update.status_code = 202
        sess = mock.Mock()
        sess.patch = mock.Mock(return_value=resp_update)

        resp_get = mock.Mock()
        resp_get.body = {'stack': FAKE_CREATE_RESPONSE}
        resp_get.json = mock.Mock(return_value=resp_get.body)
        sess.get = mock.Mock(return_value=resp_get)

        # create a stack for update
        sot = stack.Stack(FAKE)
        new_body = sot._attrs.copy()
        del new_body['id']
        del new_body['name']

        sot.timeout_mins = 119
        resp = sot.update(sess)

        url = 'stacks/%s' % sot.id
        new_body['timeout_mins'] = 119
        sess.put.assert_called_once_with(url, endpoint_filter=sot.service,
                                         json=new_body)
        sess.get.assert_called_once_with(url, endpoint_filter=sot.service)
        self.assertEqual(sot, resp)

    def test_check(self):
        session_mock = mock.Mock()
        sot = stack.Stack(FAKE)
        sot._action = mock.Mock()
        body = {'check': ''}
        sot.check(session_mock)
        sot._action.assert_called_with(session_mock, body)

    @mock.patch.object(resource.Resource, 'find')
    def test_find(self, mock_find):
        sess = mock.Mock()
        sot = stack.Stack(FAKE)
        deleted_stack = mock.Mock(status='DELETE_COMPLETE')
        normal_stack = mock.Mock(status='CREATE_COMPLETE')
        mock_find.side_effect = [
            None,
            normal_stack,
            deleted_stack,
            deleted_stack,
        ]

        self.assertIsNone(sot.find(sess, 'fake_name'))
        self.assertEqual(normal_stack, sot.find(sess, 'fake_name'))
        self.assertIsNone(sot.find(sess, 'fake_name', ignore_missing=True))
        ex = self.assertRaises(exceptions.ResourceNotFound, sot.find,
                               sess, 'fake_name', ignore_missing=False)
        self.assertEqual('ResourceNotFound: No stack found for fake_name',
                         six.text_type(ex))

    @mock.patch.object(resource.Resource, 'get')
    def test_get(self, mock_get):
        sess = mock.Mock()
        sot = stack.Stack(FAKE)
        deleted_stack = mock.Mock(id=FAKE_ID, status='DELETE_COMPLETE')
        normal_stack = mock.Mock(status='CREATE_COMPLETE')
        mock_get.side_effect = [
            normal_stack,
            exceptions.NotFoundException(message='oops'),
            deleted_stack,
        ]

        self.assertEqual(normal_stack, sot.get(sess))
        ex = self.assertRaises(exceptions.NotFoundException, sot.get, sess)
        self.assertEqual('NotFoundException: oops', six.text_type(ex))
        ex = self.assertRaises(exceptions.NotFoundException, sot.get, sess)
        self.assertEqual('NotFoundException: No stack found for %s' % FAKE_ID,
                         six.text_type(ex))
