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

from openstack.compute.v2 import server_action
from openstack.tests.unit import base

EXAMPLE = {
    'action': 'stop',
    'events': [
        {
            'event': 'compute_stop_instance',
            'finish_time': '2018-04-25T01:26:36.790544',
            'host': 'compute',
            'hostId': '2091634baaccdc4c5a1d57069c833e402921df696b7f970791b12ec6',  # noqa: E501
            'result': 'Success',
            'start_time': '2018-04-25T01:26:36.539271',
            'traceback': None,
            'details': None,
        }
    ],
    'instance_uuid': '4bf3473b-d550-4b65-9409-292d44ab14a2',
    'message': None,
    'project_id': '6f70656e737461636b20342065766572',
    'request_id': 'req-0d819d5c-1527-4669-bdf0-ffad31b5105b',
    'start_time': '2018-04-25T01:26:36.341290',
    'updated_at': '2018-04-25T01:26:36.790544',
    'user_id': 'admin',
}


class TestServerAction(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.status_code = 200
        self.sess = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = server_action.ServerAction()
        self.assertEqual('instanceAction', sot.resource_key)
        self.assertEqual('instanceActions', sot.resources_key)
        self.assertEqual(
            '/servers/%(server_id)s/os-instance-actions',
            sot.base_path,
        )
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)

        self.assertDictEqual(
            {
                'changes_before': 'changes-before',
                'changes_since': 'changes-since',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = server_action.ServerAction(**EXAMPLE)
        self.assertEqual(EXAMPLE['action'], sot.action)
        # FIXME: This isn't populated since it conflicts with the server_id URI
        # argument
        # self.assertEqual(EXAMPLE['instance_uuid'], sot.server_id)
        self.assertEqual(EXAMPLE['message'], sot.message)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['request_id'], sot.request_id)
        self.assertEqual(EXAMPLE['start_time'], sot.start_time)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
        self.assertEqual(
            [server_action.ServerActionEvent(**e) for e in EXAMPLE['events']],
            sot.events,
        )
