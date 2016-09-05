# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
import testtools

from openstack.telemetry.v2 import sample

SAMPLE = {
    'sample_id': '0',
    'metadata': {'1': 'one'},
    'counter_name': '2',
    'message_id': '4',
    'project_id': '3',
    'recorded_at': '2015-03-09T12:15:57.233772',
    'resource_id': '5',
    'source': '6',
    'timestamp': '2015-03-09T12:15:57.233772',
    'type': '8',
    'unit': '9',
    'user_id': '10',
    'volume': '11.1',
}


class TestSample(testtools.TestCase):

    def test_basic(self):
        sot = sample.Sample()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/meters/%(counter_name)s', sot.base_path)
        self.assertEqual('metering', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_new(self):
        sot = sample.Sample(**SAMPLE)
        self.assertEqual(SAMPLE['message_id'], sot.id)
        self.assertEqual(SAMPLE['metadata'], sot.metadata)
        self.assertEqual(SAMPLE['counter_name'], sot.counter_name)
        self.assertEqual(SAMPLE['project_id'], sot.project_id)
        self.assertEqual(SAMPLE['recorded_at'], sot.recorded_at)
        self.assertEqual(SAMPLE['resource_id'], sot.resource_id)
        self.assertEqual(SAMPLE['source'], sot.source)
        self.assertEqual(SAMPLE['timestamp'], sot.generated_at)
        self.assertEqual(SAMPLE['type'], sot.type)
        self.assertEqual(SAMPLE['unit'], sot.unit)
        self.assertEqual(SAMPLE['user_id'], sot.user_id)
        self.assertEqual(SAMPLE['volume'], sot.volume)

    def test_list(self):
        sess = mock.Mock()
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=[SAMPLE])
        sess.get = mock.Mock(return_value=resp)

        found = sample.Sample.list(sess, counter_name='name_of_meter')
        first = next(found)
        self.assertEqual(SAMPLE['message_id'], first.id)
        self.assertEqual(SAMPLE['metadata'], first.metadata)
        self.assertEqual(SAMPLE['counter_name'], first.counter_name)
        self.assertEqual(SAMPLE['project_id'], first.project_id)
        self.assertEqual(SAMPLE['recorded_at'], first.recorded_at)
        self.assertEqual(SAMPLE['resource_id'], first.resource_id)
        self.assertEqual(SAMPLE['source'], first.source)
        self.assertEqual(SAMPLE['timestamp'], first.generated_at)
        self.assertEqual(SAMPLE['type'], first.type)
        self.assertEqual(SAMPLE['unit'], first.unit)
        self.assertEqual(SAMPLE['user_id'], first.user_id)
        self.assertEqual(SAMPLE['volume'], first.volume)
