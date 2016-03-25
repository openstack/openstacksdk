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

import testtools

from openstack.cluster.v1 import policy


FAKE_ID = 'ac5415bd-f522-4160-8be0-f8853e4bc332'
FAKE_NAME = 'test_policy'

FAKE = {
    'name': FAKE_NAME,
    'spec': {
        'type': 'senlin.policy.deletion',
        'version': '1.0',
        'properties': {
            'criteria': 'OLDEST_FIRST',
            'grace_period': 60,
            'reduce_desired_capacity': False,
            'destroy_after_deletion': True,
        }
    },
    'type': 'senlin.policy.deletion-1.0',
    'created_at': '2015-10-10T12:46:36.000000',
    'updated_at': '2016-10-10T12:46:36.000000',
    'data': {},
}


class TestPolicy(testtools.TestCase):

    def setUp(self):
        super(TestPolicy, self).setUp()

    def test_basic(self):
        sot = policy.Policy()
        self.assertEqual('policy', sot.resource_key)
        self.assertEqual('policies', sot.resources_key)
        self.assertEqual('/policies', sot.base_path)
        self.assertEqual('clustering', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = policy.Policy(FAKE)
        self.assertIsNone(sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['spec'], sot.spec)
        self.assertEqual(FAKE['data'], sot.data)
        dt = datetime.datetime(2015, 10, 10, 12, 46, 36, 000000).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
        dt = datetime.datetime(2016, 10, 10, 12, 46, 36, 000000).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))
