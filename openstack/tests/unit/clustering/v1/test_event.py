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

from openstack.clustering.v1 import event


FAKE = {
    'action': 'NODE_CREATE',
    'cluster_id': None,
    'id': 'ffaed25e-46f5-4089-8e20-b3b4722fd597',
    'level': '20',
    'oid': 'efff1c11-2ada-47da-bedd-2c9af4fd099a',
    'oname': 'node_create_b4a49016',
    'otype': 'NODEACTION',
    'project': '42d9e9663331431f97b75e25136307ff',
    'status': 'START',
    'status_reason': 'The action was abandoned.',
    'timestamp': '2016-10-10T12:46:36.000000',
    'user': '5e5bf8027826429c96af157f68dc9072'
}


class TestEvent(base.TestCase):

    def setUp(self):
        super(TestEvent, self).setUp()

    def test_basic(self):
        sot = event.Event()
        self.assertEqual('event', sot.resource_key)
        self.assertEqual('events', sot.resources_key)
        self.assertEqual('/events', sot.base_path)
        self.assertEqual('clustering', sot.service.service_type)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = event.Event(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['action'], sot.action)
        self.assertEqual(FAKE['cluster_id'], sot.cluster_id)
        self.assertEqual(FAKE['level'], sot.level)
        self.assertEqual(FAKE['oid'], sot.obj_id)
        self.assertEqual(FAKE['oname'], sot.obj_name)
        self.assertEqual(FAKE['otype'], sot.obj_type)
        self.assertEqual(FAKE['project'], sot.project_id)
        self.assertEqual(FAKE['status'], sot.status)
        self.assertEqual(FAKE['status_reason'], sot.status_reason)
        self.assertEqual(FAKE['timestamp'], sot.generated_at)
        self.assertEqual(FAKE['user'], sot.user_id)
