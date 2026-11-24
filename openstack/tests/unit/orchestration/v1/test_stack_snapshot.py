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

from typing import Any

from openstack import exceptions
from openstack.orchestration.v1 import _proxy
from openstack.orchestration.v1 import stack
from openstack.orchestration.v1 import stack_snapshot
from openstack.tests.unit import base


FAKE: dict[str, Any] = {
    'id': 'snapshot-id',
    'name': 'snapshot-name',
    'status': 'COMPLETE',
    'status_reason': 'Stack SNAPSHOT completed successfully',
    'creation_time': '2015-03-09T12:15:57.233772',
    'data': {'resources': {}},
}
ENDPOINT = 'https://heat.example/v1/project'
COLLECTION = ENDPOINT + '/stacks/stack-name/stack-id/snapshots'
DETAIL = COLLECTION + '/snapshot-id'


class TestStackSnapshot(base.TestCase):
    def setUp(self):
        super().setUp()
        self.session = _proxy.Proxy(
            session=self.cloud.session,
            endpoint_override=ENDPOINT,
            service_type='orchestration',
        )
        self.stack = stack.Stack(id='stack-id', name='stack-name')
        self.sot = stack_snapshot.StackSnapshot(
            stack_name='stack-name', stack_id='stack-id', **FAKE
        )

    def test_basic(self):
        self.assertEqual('snapshot', self.sot.resource_key)
        self.assertEqual('snapshots', self.sot.resources_key)
        self.assertTrue(self.sot.allow_create)
        self.assertTrue(self.sot.allow_fetch)
        self.assertTrue(self.sot.allow_list)
        self.assertTrue(self.sot.allow_delete)
        self.assertFalse(self.sot.allow_commit)

    def test_make_it(self):
        self.assertEqual(FAKE['id'], self.sot.id)
        self.assertEqual(FAKE['name'], self.sot.name)
        self.assertEqual(FAKE['status'], self.sot.status)
        self.assertEqual(FAKE['status_reason'], self.sot.status_reason)
        self.assertEqual(FAKE['creation_time'], self.sot.created_at)
        self.assertEqual(FAKE['data'], self.sot.data)
        self.assertEqual('stack-id', self.sot.stack_id)
        self.assertEqual('stack-name', self.sot.stack_name)

    def test_create(self):
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=COLLECTION,
                    json=FAKE,
                    validate=dict(json={'name': 'snapshot-name'}),
                ),
            ]
        )
        sot = stack_snapshot.StackSnapshot(
            stack_name='stack-name', stack_id='stack-id', name='snapshot-name'
        )
        result = self.session.create_stack_snapshot(self.stack, name=sot.name)
        self.assertIsInstance(result, stack_snapshot.StackSnapshot)
        self.assertEqual(FAKE['id'], result.id)
        self.assertEqual(FAKE['status'], result.status)
        self.assert_calls()

    def test_fetch(self):
        self.register_uris(
            [
                dict(method='GET', uri=DETAIL, json={'snapshot': FAKE}),
            ]
        )
        sot = stack_snapshot.StackSnapshot(
            id=FAKE['id'], stack_name='stack-name', stack_id='stack-id'
        )
        self.assertIs(sot, sot.fetch(self.session))
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['creation_time'], sot.created_at)
        self.assert_calls()

    def test_list(self):
        self.register_uris(
            [
                dict(method='GET', uri=COLLECTION, json={'snapshots': [FAKE]}),
            ]
        )
        result = list(
            stack_snapshot.StackSnapshot.list(
                self.session, stack_name='stack-name', stack_id='stack-id'
            )
        )
        self.assertEqual(1, len(result))
        self.assertEqual(FAKE['id'], result[0].id)
        self.assertEqual('stack-id', result[0].stack_id)
        self.assertEqual('stack-name', result[0].stack_name)
        self.assert_calls()

    def test_delete(self):
        self.register_uris(
            [
                dict(method='DELETE', uri=DETAIL, status_code=204),
            ]
        )
        self.sot.delete(self.session)
        self.assert_calls()

    def test_delete_missing_snapshot(self):
        self.register_uris(
            [
                dict(method='DELETE', uri=DETAIL, status_code=404),
            ]
        )
        self.assertIsNone(
            self.session.delete_stack_snapshot(self.stack, self.sot)
        )
        self.assert_calls()

    def test_delete_missing_snapshot_not_ignored(self):
        self.register_uris(
            [
                dict(method='DELETE', uri=DETAIL, status_code=404),
            ]
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.session.delete_stack_snapshot,
            self.stack,
            self.sot.id,
            ignore_missing=False,
        )
        self.assert_calls()

    def test_fetch_missing_snapshot(self):
        self.register_uris(
            [
                dict(method='GET', uri=DETAIL, status_code=404),
            ]
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.session.get_stack_snapshot,
            self.stack,
            self.sot.id,
        )
        self.assert_calls()

    def test_restore(self):
        self.register_uris(
            [
                dict(method='POST', uri=DETAIL + '/restore', status_code=202),
            ]
        )
        self.assertIsNone(self.sot.restore(self.session))
        self.assert_calls()

    def test_restore_not_found(self):
        self.register_uris(
            [
                dict(method='POST', uri=DETAIL + '/restore', status_code=404),
            ]
        )
        self.assertRaises(
            exceptions.NotFoundException, self.sot.restore, self.session
        )
        self.assert_calls()

    def test_restore_encoded_path(self):
        self.sot.stack_name = 'stack name'
        self.sot.id = 'snapshot/id'
        self.register_uris(
            [
                dict(
                    method='POST',
                    status_code=202,
                    uri=ENDPOINT + '/stacks/stack%20name/stack-id/snapshots/'
                    'snapshot%2Fid/restore',
                ),
            ]
        )
        self.sot.restore(self.session)
        self.assert_calls()
