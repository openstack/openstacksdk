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


import tempfile
import testtools

import openstack.cloud
from openstack.tests import fakes
from openstack.tests.unit import base

from openstack.orchestration.v1 import stack


class TestStack(base.TestCase):

    def setUp(self):
        super(TestStack, self).setUp()
        self.stack_id = self.getUniqueString('id')
        self.stack_name = self.getUniqueString('name')
        self.stack_tag = self.getUniqueString('tag')
        self.stack = fakes.make_fake_stack(self.stack_id, self.stack_name)

    def test_list_stacks(self):
        fake_stacks = [
            self.stack,
            fakes.make_fake_stack(
                self.getUniqueString('id'),
                self.getUniqueString('name'))
        ]
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT),
                 json={"stacks": fake_stacks}),
        ])
        stacks = self.cloud.list_stacks()
        self.assertEqual(
            [f.toDict() for f in self.cloud._normalize_stacks(
                stack.Stack(**st) for st in fake_stacks)],
            [f.toDict() for f in stacks])

        self.assert_calls()

    def test_list_stacks_filters(self):
        fake_stacks = [
            self.stack,
            fakes.make_fake_stack(
                self.getUniqueString('id'),
                self.getUniqueString('name'))
        ]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'orchestration', 'public',
                     append=['stacks'],
                     qs_elements=['name=a', 'status=b'],
                 ),
                 json={"stacks": fake_stacks}),
        ])
        stacks = self.cloud.list_stacks(name='a', status='b')
        self.assertEqual(
            [f.toDict() for f in self.cloud._normalize_stacks(
                stack.Stack(**st) for st in fake_stacks)],
            [f.toDict() for f in stacks])

        self.assert_calls()

    def test_list_stacks_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT),
                 status_code=404)
        ])
        with testtools.ExpectedException(
                openstack.cloud.OpenStackCloudURINotFound):
            self.cloud.list_stacks()
        self.assert_calls()

    def test_search_stacks(self):
        fake_stacks = [
            self.stack,
            fakes.make_fake_stack(
                self.getUniqueString('id'),
                self.getUniqueString('name'))
        ]
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT),
                 json={"stacks": fake_stacks}),
        ])
        stacks = self.cloud.search_stacks()
        self.assertEqual(
            self.cloud._normalize_stacks(
                stack.Stack(**st) for st in fake_stacks),
            stacks)
        self.assert_calls()

    def test_search_stacks_filters(self):
        fake_stacks = [
            self.stack,
            fakes.make_fake_stack(
                self.getUniqueString('id'),
                self.getUniqueString('name'),
                status='CREATE_FAILED')
        ]
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT),
                 json={"stacks": fake_stacks}),
        ])
        filters = {'status': 'FAILED'}
        stacks = self.cloud.search_stacks(filters=filters)
        self.assertEqual(
            self.cloud._normalize_stacks(
                stack.Stack(**st) for st in fake_stacks[1:]),
            stacks)
        self.assert_calls()

    def test_search_stacks_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT),
                 status_code=404)
        ])
        with testtools.ExpectedException(
                openstack.cloud.OpenStackCloudURINotFound):
            self.cloud.search_stacks()

    def test_delete_stack(self):
        resolve = 'resolve_outputs=False'
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     name=self.stack_name, resolve=resolve),
                 status_code=302,
                 headers=dict(
                     location='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                         endpoint=fakes.ORCHESTRATION_ENDPOINT,
                         id=self.stack_id, name=self.stack_name,
                         resolve=resolve))),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, name=self.stack_name, resolve=resolve),
                 json={"stack": self.stack}),
            dict(method='DELETE',
                 uri='{endpoint}/stacks/{id}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id)),
        ])
        self.assertTrue(self.cloud.delete_stack(self.stack_name))
        self.assert_calls()

    def test_delete_stack_not_found(self):
        resolve = 'resolve_outputs=False'
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks/stack_name?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT, resolve=resolve),
                 status_code=404),
        ])
        self.assertFalse(self.cloud.delete_stack('stack_name'))
        self.assert_calls()

    def test_delete_stack_exception(self):
        resolve = 'resolve_outputs=False'
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, resolve=resolve),
                 status_code=302,
                 headers=dict(
                     location='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                         endpoint=fakes.ORCHESTRATION_ENDPOINT,
                         id=self.stack_id, name=self.stack_name,
                         resolve=resolve))),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, name=self.stack_name, resolve=resolve),
                 json={"stack": self.stack}),
            dict(method='DELETE',
                 uri='{endpoint}/stacks/{id}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id),
                 status_code=400,
                 reason="ouch"),
        ])
        with testtools.ExpectedException(
                openstack.cloud.OpenStackCloudBadRequest):
            self.cloud.delete_stack(self.stack_id)
        self.assert_calls()

    def test_delete_stack_by_name_wait(self):
        marker_event = fakes.make_fake_stack_event(
            self.stack_id, self.stack_name, status='CREATE_COMPLETE',
            resource_name='name')
        marker_qs = 'marker={e_id}&sort_dir=asc'.format(
            e_id=marker_event['id'])
        resolve = 'resolve_outputs=False'
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     name=self.stack_name,
                     resolve=resolve),
                 status_code=302,
                 headers=dict(
                     location='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                         endpoint=fakes.ORCHESTRATION_ENDPOINT,
                         id=self.stack_id, name=self.stack_name,
                         resolve=resolve))),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, name=self.stack_name, resolve=resolve),
                 json={"stack": self.stack}),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/events?{qs}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     name=self.stack_name,
                     qs='limit=1&sort_dir=desc'),
                 complete_qs=True,
                 json={"events": [marker_event]}),
            dict(method='DELETE',
                 uri='{endpoint}/stacks/{id}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id)),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/events?{qs}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     name=self.stack_name,
                     qs=marker_qs),
                 complete_qs=True,
                 json={"events": [
                     fakes.make_fake_stack_event(
                         self.stack_id, self.stack_name,
                         status='DELETE_COMPLETE', resource_name='name'),
                 ]}),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, name=self.stack_name, resolve=resolve),
                 status_code=404),
        ])

        self.assertTrue(self.cloud.delete_stack(self.stack_name, wait=True))
        self.assert_calls()

    def test_delete_stack_by_id_wait(self):
        marker_event = fakes.make_fake_stack_event(
            self.stack_id, self.stack_name, status='CREATE_COMPLETE',
            resource_name='name')
        marker_qs = 'marker={e_id}&sort_dir=asc'.format(
            e_id=marker_event['id'])
        resolve = 'resolve_outputs=False'
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id,
                     resolve=resolve),
                 status_code=302,
                 headers=dict(
                     location='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                         endpoint=fakes.ORCHESTRATION_ENDPOINT,
                         id=self.stack_id, name=self.stack_name,
                         resolve=resolve))),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, name=self.stack_name, resolve=resolve),
                 json={"stack": self.stack}),
            dict(method='GET',
                 uri='{endpoint}/stacks/{id}/events?{qs}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id,
                     qs='limit=1&sort_dir=desc'),
                 complete_qs=True,
                 json={"events": [marker_event]}),
            dict(method='DELETE',
                 uri='{endpoint}/stacks/{id}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id)),
            dict(method='GET',
                 uri='{endpoint}/stacks/{id}/events?{qs}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id,
                     qs=marker_qs),
                 complete_qs=True,
                 json={"events": [
                     fakes.make_fake_stack_event(
                         self.stack_id, self.stack_name,
                         status='DELETE_COMPLETE'),
                 ]}),
            dict(method='GET',
                 uri='{endpoint}/stacks/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, resolve=resolve),
                 status_code=404),
        ])

        self.assertTrue(self.cloud.delete_stack(self.stack_id, wait=True))
        self.assert_calls()

    def test_delete_stack_wait_failed(self):
        failed_stack = self.stack.copy()
        failed_stack['stack_status'] = 'DELETE_FAILED'
        marker_event = fakes.make_fake_stack_event(
            self.stack_id, self.stack_name, status='CREATE_COMPLETE')
        marker_qs = 'marker={e_id}&sort_dir=asc'.format(
            e_id=marker_event['id'])
        resolve = 'resolve_outputs=False'
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, resolve=resolve),
                 status_code=302,
                 headers=dict(
                     location='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                         endpoint=fakes.ORCHESTRATION_ENDPOINT,
                         id=self.stack_id, name=self.stack_name,
                         resolve=resolve))),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, name=self.stack_name, resolve=resolve),
                 json={"stack": self.stack}),
            dict(method='GET',
                 uri='{endpoint}/stacks/{id}/events?{qs}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id,
                     qs='limit=1&sort_dir=desc'),
                 complete_qs=True,
                 json={"events": [marker_event]}),
            dict(method='DELETE',
                 uri='{endpoint}/stacks/{id}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id)),
            dict(method='GET',
                 uri='{endpoint}/stacks/{id}/events?{qs}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id,
                     qs=marker_qs),
                 complete_qs=True,
                 json={"events": [
                     fakes.make_fake_stack_event(
                         self.stack_id, self.stack_name,
                         status='DELETE_COMPLETE'),
                 ]}),
            dict(method='GET',
                 uri='{endpoint}/stacks/{id}?resolve_outputs=False'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id),
                 status_code=302,
                 headers=dict(
                     location='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                         endpoint=fakes.ORCHESTRATION_ENDPOINT,
                         id=self.stack_id, name=self.stack_name,
                         resolve=resolve))),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/{id}?{resolve}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, name=self.stack_name, resolve=resolve),
                 json={"stack": failed_stack}),
        ])

        with testtools.ExpectedException(
                openstack.cloud.OpenStackCloudException):
            self.cloud.delete_stack(self.stack_id, wait=True)

        self.assert_calls()

    def test_create_stack(self):
        test_template = tempfile.NamedTemporaryFile(delete=False)
        test_template.write(fakes.FAKE_TEMPLATE.encode('utf-8'))
        test_template.close()
        self.register_uris([
            dict(
                method='POST', uri='{endpoint}/stacks'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT),
                json={"stack": self.stack},
                validate=dict(
                    json={
                        'disable_rollback': False,
                        'parameters': {},
                        'stack_name': self.stack_name,
                        'tags': self.stack_tag,
                        'template': fakes.FAKE_TEMPLATE_CONTENT,
                        'timeout_mins': 60}
                )),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    name=self.stack_name),
                status_code=302,
                headers=dict(
                    location='{endpoint}/stacks/{name}/{id}'.format(
                        endpoint=fakes.ORCHESTRATION_ENDPOINT,
                        id=self.stack_id, name=self.stack_name))),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}/{id}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    id=self.stack_id, name=self.stack_name),
                json={"stack": self.stack}),
        ])

        self.cloud.create_stack(
            self.stack_name,
            tags=self.stack_tag,
            template_file=test_template.name
        )

        self.assert_calls()

    def test_create_stack_wait(self):

        test_template = tempfile.NamedTemporaryFile(delete=False)
        test_template.write(fakes.FAKE_TEMPLATE.encode('utf-8'))
        test_template.close()

        self.register_uris([
            dict(
                method='POST', uri='{endpoint}/stacks'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT),
                json={"stack": self.stack},
                validate=dict(
                    json={
                        'disable_rollback': False,
                        'parameters': {},
                        'stack_name': self.stack_name,
                        'tags': self.stack_tag,
                        'template': fakes.FAKE_TEMPLATE_CONTENT,
                        'timeout_mins': 60}
                )),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}/events?sort_dir=asc'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    name=self.stack_name),
                json={"events": [
                    fakes.make_fake_stack_event(
                        self.stack_id, self.stack_name,
                        status='CREATE_COMPLETE',
                        resource_name='name'),
                ]}),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    name=self.stack_name),
                status_code=302,
                headers=dict(
                    location='{endpoint}/stacks/{name}/{id}'.format(
                        endpoint=fakes.ORCHESTRATION_ENDPOINT,
                        id=self.stack_id, name=self.stack_name))),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}/{id}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    id=self.stack_id, name=self.stack_name),
                json={"stack": self.stack}),
        ])
        self.cloud.create_stack(
            self.stack_name,
            tags=self.stack_tag,
            template_file=test_template.name,
            wait=True)

        self.assert_calls()

    def test_update_stack(self):
        test_template = tempfile.NamedTemporaryFile(delete=False)
        test_template.write(fakes.FAKE_TEMPLATE.encode('utf-8'))
        test_template.close()

        self.register_uris([
            dict(
                method='PUT',
                uri='{endpoint}/stacks/{name}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    name=self.stack_name),
                validate=dict(
                    json={
                        'disable_rollback': False,
                        'parameters': {},
                        'tags': self.stack_tag,
                        'template': fakes.FAKE_TEMPLATE_CONTENT,
                        'timeout_mins': 60}),
                json={}),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    name=self.stack_name),
                status_code=302,
                headers=dict(
                    location='{endpoint}/stacks/{name}/{id}'.format(
                        endpoint=fakes.ORCHESTRATION_ENDPOINT,
                        id=self.stack_id, name=self.stack_name))),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}/{id}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    id=self.stack_id, name=self.stack_name),
                json={"stack": self.stack}),
        ])
        self.cloud.update_stack(
            self.stack_name,
            tags=self.stack_tag,
            template_file=test_template.name)

        self.assert_calls()

    def test_update_stack_wait(self):
        marker_event = fakes.make_fake_stack_event(
            self.stack_id, self.stack_name, status='CREATE_COMPLETE',
            resource_name='name')
        marker_qs = 'marker={e_id}&sort_dir=asc'.format(
            e_id=marker_event['id'])
        test_template = tempfile.NamedTemporaryFile(delete=False)
        test_template.write(fakes.FAKE_TEMPLATE.encode('utf-8'))
        test_template.close()

        self.register_uris([
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}/events?{qs}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    name=self.stack_name,
                    qs='limit=1&sort_dir=desc'),
                json={"events": [marker_event]}),
            dict(
                method='PUT',
                uri='{endpoint}/stacks/{name}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    name=self.stack_name),
                validate=dict(
                    json={
                        'disable_rollback': False,
                        'parameters': {},
                        'tags': self.stack_tag,
                        'template': fakes.FAKE_TEMPLATE_CONTENT,
                        'timeout_mins': 60}),
                json={}),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}/events?{qs}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    name=self.stack_name,
                    qs=marker_qs),
                json={"events": [
                    fakes.make_fake_stack_event(
                        self.stack_id, self.stack_name,
                        status='UPDATE_COMPLETE',
                        resource_name='name'),
                ]}),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    name=self.stack_name),
                status_code=302,
                headers=dict(
                    location='{endpoint}/stacks/{name}/{id}'.format(
                        endpoint=fakes.ORCHESTRATION_ENDPOINT,
                        id=self.stack_id, name=self.stack_name))),
            dict(
                method='GET',
                uri='{endpoint}/stacks/{name}/{id}'.format(
                    endpoint=fakes.ORCHESTRATION_ENDPOINT,
                    id=self.stack_id, name=self.stack_name),
                json={"stack": self.stack}),
        ])
        self.cloud.update_stack(
            self.stack_name,
            tags=self.stack_tag,
            template_file=test_template.name,
            wait=True)

        self.assert_calls()

    def test_get_stack(self):
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     name=self.stack_name),
                 status_code=302,
                 headers=dict(
                     location='{endpoint}/stacks/{name}/{id}'.format(
                         endpoint=fakes.ORCHESTRATION_ENDPOINT,
                         id=self.stack_id, name=self.stack_name))),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/{id}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, name=self.stack_name),
                 json={"stack": self.stack}),
        ])

        res = self.cloud.get_stack(self.stack_name)
        self.assertIsNotNone(res)
        self.assertEqual(self.stack['stack_name'], res['stack_name'])
        self.assertEqual(self.stack['stack_name'], res['name'])
        self.assertEqual(self.stack['stack_status'], res['stack_status'])
        self.assertEqual('COMPLETE', res['status'])

        self.assert_calls()

    def test_get_stack_in_progress(self):
        in_progress = self.stack.copy()
        in_progress['stack_status'] = 'CREATE_IN_PROGRESS'
        self.register_uris([
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     name=self.stack_name),
                 status_code=302,
                 headers=dict(
                     location='{endpoint}/stacks/{name}/{id}'.format(
                         endpoint=fakes.ORCHESTRATION_ENDPOINT,
                         id=self.stack_id, name=self.stack_name))),
            dict(method='GET',
                 uri='{endpoint}/stacks/{name}/{id}'.format(
                     endpoint=fakes.ORCHESTRATION_ENDPOINT,
                     id=self.stack_id, name=self.stack_name),
                 json={"stack": in_progress}),
        ])

        res = self.cloud.get_stack(self.stack_name)
        self.assertIsNotNone(res)
        self.assertEqual(in_progress['stack_name'], res['stack_name'])
        self.assertEqual(in_progress['stack_name'], res['name'])
        self.assertEqual(in_progress['stack_status'], res['stack_status'])
        self.assertEqual('CREATE', res['action'])
        self.assertEqual('IN_PROGRESS', res['status'])

        self.assert_calls()
