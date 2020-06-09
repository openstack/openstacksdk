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

from keystoneauth1 import adapter

from openstack.baremetal.v1 import allocation
from openstack import exceptions
from openstack.tests.unit import base

FAKE = {
    "candidate_nodes": [],
    "created_at": "2016-08-18T22:28:48.165105+00:00",
    "extra": {},
    "last_error": None,
    "links": [
        {
            "href": "http://127.0.0.1:6385/v1/allocations/<PG_ID>",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/allocations/<PG_ID>",
            "rel": "bookmark"
        }
    ],
    "name": "test_allocation",
    "node_uuid": "6d85703a-565d-469a-96ce-30b6de53079d",
    "resource_class": "baremetal",
    "state": "active",
    "traits": [],
    "updated_at": None,
    "uuid": "e43c722c-248e-4c6e-8ce8-0d8ff129387a",
}


class TestAllocation(base.TestCase):

    def test_basic(self):
        sot = allocation.Allocation()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('allocations', sot.resources_key)
        self.assertEqual('/allocations', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = allocation.Allocation(**FAKE)
        self.assertEqual(FAKE['candidate_nodes'], sot.candidate_nodes)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['last_error'], sot.last_error)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['node_uuid'], sot.node_id)
        self.assertEqual(FAKE['resource_class'], sot.resource_class)
        self.assertEqual(FAKE['state'], sot.state)
        self.assertEqual(FAKE['traits'], sot.traits)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
        self.assertEqual(FAKE['uuid'], sot.id)


@mock.patch('time.sleep', lambda _t: None)
@mock.patch.object(allocation.Allocation, 'fetch', autospec=True)
class TestWaitForAllocation(base.TestCase):

    def setUp(self):
        super(TestWaitForAllocation, self).setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.default_microversion = '1.52'
        self.session.log = mock.Mock()
        self.fake = dict(FAKE, state='allocating', node_uuid=None)
        self.allocation = allocation.Allocation(**self.fake)

    def test_already_active(self, mock_fetch):
        self.allocation.state = 'active'
        allocation = self.allocation.wait(None)
        self.assertIs(allocation, self.allocation)
        self.assertFalse(mock_fetch.called)

    def test_wait(self, mock_fetch):
        marker = [False]  # mutable object to modify in the closure

        def _side_effect(allocation, session):
            if marker[0]:
                self.allocation.state = 'active'
                self.allocation.node_id = FAKE['node_uuid']
            else:
                marker[0] = True

        mock_fetch.side_effect = _side_effect
        allocation = self.allocation.wait(self.session)
        self.assertIs(allocation, self.allocation)
        self.assertEqual(2, mock_fetch.call_count)

    def test_failure(self, mock_fetch):
        marker = [False]  # mutable object to modify in the closure

        def _side_effect(allocation, session):
            if marker[0]:
                self.allocation.state = 'error'
                self.allocation.last_error = 'boom!'
            else:
                marker[0] = True

        mock_fetch.side_effect = _side_effect
        self.assertRaises(exceptions.ResourceFailure,
                          self.allocation.wait, self.session)
        self.assertEqual(2, mock_fetch.call_count)

    def test_failure_ignored(self, mock_fetch):
        marker = [False]  # mutable object to modify in the closure

        def _side_effect(allocation, session):
            if marker[0]:
                self.allocation.state = 'error'
                self.allocation.last_error = 'boom!'
            else:
                marker[0] = True

        mock_fetch.side_effect = _side_effect
        allocation = self.allocation.wait(self.session, ignore_error=True)
        self.assertIs(allocation, self.allocation)
        self.assertEqual(2, mock_fetch.call_count)

    def test_timeout(self, mock_fetch):
        self.assertRaises(exceptions.ResourceTimeout,
                          self.allocation.wait, self.session, timeout=0.001)
        mock_fetch.assert_called_with(self.allocation, self.session)
