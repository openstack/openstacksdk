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

import testtools

from openstack.cluster.v1 import receiver


FAKE_ID = 'ae63a10b-4a90-452c-aef1-113a0b255ee3'
FAKE_NAME = 'test_receiver'

FAKE = {
    'id': FAKE_ID,
    'name': FAKE_NAME,
    'type': 'webhook',
    'cluster_id': 'FAKE_CLUSTER',
    'action': 'CLUSTER_RESIZE',
    'created_at': '2015-10-10T12:46:36.000000',
    'updated_at': '2016-10-10T12:46:36.000000',
    'actor': {},
    'params': {
        'adjustment_type': 'CHANGE_IN_CAPACITY',
        'adjustment': 2
    },
    'channel': {
        'alarm_url': 'http://host:port/webhooks/AN_ID/trigger?V=1',
    },
    'user': 'FAKE_USER',
    'project': 'FAKE_PROJECT',
    'domain': '',
}


class TestReceiver(testtools.TestCase):

    def setUp(self):
        super(TestReceiver, self).setUp()

    def test_basic(self):
        sot = receiver.Receiver()
        self.assertEqual('receiver', sot.resource_key)
        self.assertEqual('receivers', sot.resources_key)
        self.assertEqual('/receivers', sot.base_path)
        self.assertEqual('clustering', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = receiver.Receiver(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['type'], sot.type)
        self.assertEqual(FAKE['cluster_id'], sot.cluster_id)
        self.assertEqual(FAKE['action'], sot.action)
        self.assertEqual(FAKE['params'], sot.params)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
        self.assertEqual(FAKE['user'], sot.user_id)
        self.assertEqual(FAKE['project'], sot.project_id)
        self.assertEqual(FAKE['domain'], sot.domain_id)
        self.assertEqual(FAKE['channel'], sot.channel)
