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

from openstack.tests.unit import base

from openstack.clustering.v1 import action


FAKE_ID = '633bd3c6-520b-420f-8e6a-dc2a47022b53'
FAKE_NAME = 'node_create_c3783474'

FAKE = {
    'id': FAKE_ID,
    'name': FAKE_NAME,
    'target': 'c378e474-d091-43a3-b083-e19719291358',
    'action': 'NODE_CREATE',
    'cause': 'RPC Request',
    'owner': None,
    'user': '3747afc360b64702a53bdd64dc1b8976',
    'project': '42d9e9663331431f97b75e25136307ff',
    'domain': '204ccccd267b40aea871750116b5b184',
    'interval': -1,
    'start_time': 1453414055.48672,
    'end_time': 1453414055.48672,
    'timeout': 3600,
    'status': 'SUCCEEDED',
    'status_reason': 'Action completed successfully.',
    'inputs': {},
    'outputs': {},
    'depends_on': [],
    'depended_by': [],
    'created_at': '2015-10-10T12:46:36.000000',
    'updated_at': '2016-10-10T12:46:36.000000',
}


class TestAction(base.TestCase):

    def setUp(self):
        super(TestAction, self).setUp()

    def test_basic(self):
        sot = action.Action()
        self.assertEqual('action', sot.resource_key)
        self.assertEqual('actions', sot.resources_key)
        self.assertEqual('/actions', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = action.Action(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['target'], sot.target_id)
        self.assertEqual(FAKE['action'], sot.action)
        self.assertEqual(FAKE['cause'], sot.cause)
        self.assertEqual(FAKE['owner'], sot.owner_id)
        self.assertEqual(FAKE['user'], sot.user_id)
        self.assertEqual(FAKE['project'], sot.project_id)
        self.assertEqual(FAKE['domain'], sot.domain_id)
        self.assertEqual(FAKE['interval'], sot.interval)
        self.assertEqual(FAKE['start_time'], sot.start_at)
        self.assertEqual(FAKE['end_time'], sot.end_at)
        self.assertEqual(FAKE['timeout'], sot.timeout)
        self.assertEqual(FAKE['status'], sot.status)
        self.assertEqual(FAKE['status_reason'], sot.status_reason)
        self.assertEqual(FAKE['inputs'], sot.inputs)
        self.assertEqual(FAKE['outputs'], sot.outputs)
        self.assertEqual(FAKE['depends_on'], sot.depends_on)
        self.assertEqual(FAKE['depended_by'], sot.depended_by)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
