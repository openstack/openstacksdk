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

from openstack import exceptions
from openstack.orchestration.v1 import stack
from openstack import resource
from openstack.tests.unit import base
from openstack.tests.unit import test_resource

FAKE_ID = 'ce8ae86c-9810-4cb1-8888-7fb53bc523bf'
FAKE_NAME = 'test_stack'
FAKE = {
    'capabilities': '1',
    'creation_time': '2015-03-09T12:15:57.233772',
    'deletion_time': '2015-03-09T12:15:57.233772',
    'description': '3',
    'disable_rollback': True,
    'environment': {'var1': 'val1'},
    'environment_files': [],
    'files': {'file1': 'content'},
    'files_container': 'dummy_container',
    'id': FAKE_ID,
    'links': [{'href': f'stacks/{FAKE_NAME}/{FAKE_ID}', 'rel': 'self'}],
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
        'links': [{'href': f'stacks/{FAKE_NAME}/{FAKE_ID}', 'rel': 'self'}],
    }
}
FAKE_UPDATE_PREVIEW_RESPONSE = {
    'unchanged': [
        {
            'updated_time': 'datetime',
            'resource_name': '',
            'physical_resource_id': '{resource id or }',
            'resource_action': 'CREATE',
            'resource_status': 'COMPLETE',
            'resource_status_reason': '',
            'resource_type': 'restype',
            'stack_identity': '{stack_id}',
            'stack_name': '{stack_name}',
        }
    ],
    'updated': [
        {
            'updated_time': 'datetime',
            'resource_name': '',
            'physical_resource_id': '{resource id or }',
            'resource_action': 'CREATE',
            'resource_status': 'COMPLETE',
            'resource_status_reason': '',
            'resource_type': 'restype',
            'stack_identity': '{stack_id}',
            'stack_name': '{stack_name}',
        }
    ],
    'replaced': [
        {
            'updated_time': 'datetime',
            'resource_name': '',
            'physical_resource_id': '{resource id or }',
            'resource_action': 'CREATE',
            'resource_status': 'COMPLETE',
            'resource_status_reason': '',
            'resource_type': 'restype',
            'stack_identity': '{stack_id}',
            'stack_name': '{stack_name}',
        }
    ],
    'added': [
        {
            'updated_time': 'datetime',
            'resource_name': '',
            'physical_resource_id': '{resource id or }',
            'resource_action': 'CREATE',
            'resource_status': 'COMPLETE',
            'resource_status_reason': '',
            'resource_type': 'restype',
            'stack_identity': '{stack_id}',
            'stack_name': '{stack_name}',
        }
    ],
    'deleted': [
        {
            'updated_time': 'datetime',
            'resource_name': '',
            'physical_resource_id': '{resource id or }',
            'resource_action': 'CREATE',
            'resource_status': 'COMPLETE',
            'resource_status_reason': '',
            'resource_type': 'restype',
            'stack_identity': '{stack_id}',
            'stack_name': '{stack_name}',
        }
    ],
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

        self.assertDictEqual(
            {
                'action': 'action',
                'any_tags': 'tags-any',
                'limit': 'limit',
                'marker': 'marker',
                'name': 'name',
                'not_any_tags': 'not-tags-any',
                'not_tags': 'not-tags',
                'owner_id': 'owner_id',
                'project_id': 'tenant_id',
                'status': 'status',
                'tags': 'tags',
                'username': 'username',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = stack.Stack(**FAKE)
        self.assertEqual(FAKE['capabilities'], sot.capabilities)
        self.assertEqual(FAKE['creation_time'], sot.created_at)
        self.assertEqual(FAKE['deletion_time'], sot.deleted_at)
        self.assertEqual(FAKE['description'], sot.description)
        self.assertEqual(FAKE['environment'], sot.environment)
        self.assertEqual(FAKE['environment_files'], sot.environment_files)
        self.assertEqual(FAKE['files'], sot.files)
        self.assertEqual(FAKE['files_container'], sot.files_container)
        self.assertTrue(sot.is_rollback_disabled)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['notification_topics'], sot.notification_topics)
        self.assertEqual(FAKE['outputs'], sot.outputs)
        self.assertEqual(FAKE['parameters'], sot.parameters)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['status'], sot.status)
        self.assertEqual(FAKE['status_reason'], sot.status_reason)
        self.assertEqual(FAKE['tags'], sot.tags)
        self.assertEqual(
            FAKE['template_description'], sot.template_description
        )
        self.assertEqual(FAKE['template_url'], sot.template_url)
        self.assertEqual(FAKE['timeout_mins'], sot.timeout_mins)
        self.assertEqual(FAKE['updated_time'], sot.updated_at)

    @mock.patch.object(resource.Resource, 'create')
    def test_create(self, mock_create):
        sess = mock.Mock()
        sot = stack.Stack()

        res = sot.create(sess)

        mock_create.assert_called_once_with(sess, False)
        self.assertEqual(mock_create.return_value, res)

    def test_check(self):
        sess = mock.Mock()
        sot = stack.Stack(**FAKE)
        sot._action = mock.Mock()
        sot._action.side_effect = [
            test_resource.FakeResponse(None, 200, None),
            exceptions.BadRequestException(message='oops'),
            exceptions.NotFoundException(message='oops'),
        ]
        body = {'check': ''}

        sot.check(sess)
        sot._action.assert_called_with(sess, body)

        self.assertRaises(exceptions.BadRequestException, sot.check, sess)
        self.assertRaises(exceptions.NotFoundException, sot.check, sess)

    def test_fetch(self):
        sess = mock.Mock()
        sess.default_microversion = None
        sot = stack.Stack(**FAKE)

        sess.get = mock.Mock()
        sess.get.side_effect = [
            test_resource.FakeResponse(
                {'stack': {'stack_status': 'CREATE_COMPLETE'}}, 200
            ),
            test_resource.FakeResponse(
                {'stack': {'stack_status': 'CREATE_COMPLETE'}}, 200
            ),
            exceptions.NotFoundException(message='oops'),
            test_resource.FakeResponse(
                {'stack': {'stack_status': 'DELETE_COMPLETE'}}, 200
            ),
        ]

        self.assertEqual(sot, sot.fetch(sess))
        sess.get.assert_called_with(
            f'stacks/{sot.id}',
            microversion=None,
            skip_cache=False,
        )
        sot.fetch(sess, resolve_outputs=False)
        sess.get.assert_called_with(
            f'stacks/{sot.id}?resolve_outputs=False',
            microversion=None,
            skip_cache=False,
        )
        ex = self.assertRaises(exceptions.NotFoundException, sot.fetch, sess)
        self.assertEqual('oops', str(ex))
        ex = self.assertRaises(exceptions.NotFoundException, sot.fetch, sess)
        self.assertEqual(f'No stack found for {FAKE_ID}', str(ex))

    def test_abandon(self):
        sess = mock.Mock()
        sess.default_microversion = None

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {}
        sess.delete = mock.Mock(return_value=mock_response)
        sot = stack.Stack(**FAKE)

        sot.abandon(sess)

        sess.delete.assert_called_with(
            f'stacks/{FAKE_NAME}/{FAKE_ID}/abandon',
        )

    def test_export(self):
        sess = mock.Mock()
        sess.default_microversion = None

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {}
        sess.get = mock.Mock(return_value=mock_response)
        sot = stack.Stack(**FAKE)

        sot.export(sess)

        sess.get.assert_called_with(
            f'stacks/{FAKE_NAME}/{FAKE_ID}/export',
        )

    def test_commit(self):
        sess = mock.Mock()
        sess.default_microversion = None

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {}
        sess.put = mock.Mock(return_value=mock_response)
        sot = stack.Stack(**FAKE)
        body = sot._body.dirty.copy()

        sot.commit(sess)

        sess.put.assert_called_with(
            f'/stacks/{FAKE_NAME}/{FAKE_ID}',
            headers={},
            microversion=None,
            json=body,
        )

    def test_commit_preview(self):
        sess = mock.Mock()
        sess.default_microversion = None

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = FAKE_UPDATE_PREVIEW_RESPONSE.copy()
        sess.put = mock.Mock(return_value=mock_response)
        sot = stack.Stack(**FAKE)
        body = sot._body.dirty.copy()

        ret = sot.commit(sess, preview=True)

        sess.put.assert_called_with(
            f'stacks/{FAKE_NAME}/{FAKE_ID}/preview',
            headers={},
            microversion=None,
            json=body,
        )

        self.assertEqual(FAKE_UPDATE_PREVIEW_RESPONSE['added'], ret.added)
        self.assertEqual(FAKE_UPDATE_PREVIEW_RESPONSE['deleted'], ret.deleted)
        self.assertEqual(
            FAKE_UPDATE_PREVIEW_RESPONSE['replaced'], ret.replaced
        )
        self.assertEqual(
            FAKE_UPDATE_PREVIEW_RESPONSE['unchanged'], ret.unchanged
        )
        self.assertEqual(FAKE_UPDATE_PREVIEW_RESPONSE['updated'], ret.updated)

    def test_suspend(self):
        sess = mock.Mock()

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {}
        sess.post = mock.Mock(return_value=mock_response)
        url = f"stacks/{FAKE_ID}/actions"
        body = {"suspend": None}
        sot = stack.Stack(**FAKE)

        res = sot.suspend(sess)

        self.assertIsNone(res)
        sess.post.assert_called_with(url, json=body, microversion=None)

    def test_resume(self):
        sess = mock.Mock()

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {}
        sess.post = mock.Mock(return_value=mock_response)
        url = f"stacks/{FAKE_ID}/actions"

        body = {"resume": None}

        sot = stack.Stack(**FAKE)

        res = sot.resume(sess)

        self.assertIsNone(res)
        sess.post.assert_called_with(url, json=body, microversion=None)
