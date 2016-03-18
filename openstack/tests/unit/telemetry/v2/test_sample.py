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

import datetime

import mock
import testtools

from openstack.telemetry.v2 import sample

SAMPLE = {
    'sample_id': '0',
    'metadata': {'1': 'one'},
    'counter_name': '2',
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

OLD_SAMPLE = {
    'counter_name': '1',
    'counter_type': '2',
    'counter_unit': '3',
    'counter_volume': '4',
    'message_id': '0',
    'project_id': '5',
    'recorded_at': '2015-03-09T12:15:57.233772',
    'resource_id': '7',
    'resource_metadata': '8',
    'source': '9',
    'timestamp': '2015-03-09T12:15:57.233772',
    'user_id': '11',
}


class TestSample(testtools.TestCase):

    def test_basic(self):
        sot = sample.Sample(SAMPLE)
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/meters/%(counter_name)s', sot.base_path)
        self.assertEqual('metering', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_new(self):
        sot = sample.Sample(SAMPLE)
        self.assertEqual(SAMPLE['sample_id'], sot.id)
        self.assertEqual(SAMPLE['metadata'], sot.metadata)
        self.assertEqual(SAMPLE['counter_name'], sot.counter_name)
        self.assertEqual(SAMPLE['project_id'], sot.project_id)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.recorded_at.replace(tzinfo=None))
        self.assertEqual(SAMPLE['resource_id'], sot.resource_id)
        self.assertEqual(SAMPLE['source'], sot.source)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.generated_at.replace(tzinfo=None))
        self.assertEqual(SAMPLE['type'], sot.type)
        self.assertEqual(SAMPLE['unit'], sot.unit)
        self.assertEqual(SAMPLE['user_id'], sot.user_id)
        self.assertEqual(SAMPLE['volume'], sot.volume)

    def test_make_old(self):
        sot = sample.Sample(OLD_SAMPLE)
        self.assertIsNone(sot.id)
        self.assertEqual(OLD_SAMPLE['counter_name'], sot.counter_name)
        self.assertEqual(OLD_SAMPLE['counter_type'], sot.type)
        self.assertEqual(OLD_SAMPLE['counter_unit'], sot.unit)
        self.assertEqual(OLD_SAMPLE['counter_volume'], sot.volume)
        self.assertEqual(OLD_SAMPLE['project_id'], sot.project_id)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.recorded_at.replace(tzinfo=None))
        self.assertEqual(OLD_SAMPLE['resource_id'], sot.resource_id)
        self.assertEqual(OLD_SAMPLE['resource_metadata'], sot.metadata)
        self.assertEqual(OLD_SAMPLE['source'], sot.source)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.generated_at.replace(tzinfo=None))
        self.assertEqual(OLD_SAMPLE['user_id'], sot.user_id)

    def test_list(self):
        sess = mock.Mock()
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=[SAMPLE, OLD_SAMPLE])
        sess.get = mock.Mock(return_value=resp)
        path_args = {'counter_name': 'name_of_meter'}

        found = sample.Sample.list(sess, path_args=path_args)
        first = next(found)
        self.assertEqual(SAMPLE['sample_id'], first.id)
        self.assertEqual(SAMPLE['metadata'], first.metadata)
        self.assertEqual(SAMPLE['counter_name'], first.counter_name)
        self.assertEqual(SAMPLE['project_id'], first.project_id)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, first.recorded_at.replace(tzinfo=None))
        self.assertEqual(SAMPLE['resource_id'], first.resource_id)
        self.assertEqual(SAMPLE['source'], first.source)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, first.generated_at.replace(tzinfo=None))
        self.assertEqual(SAMPLE['type'], first.type)
        self.assertEqual(SAMPLE['unit'], first.unit)
        self.assertEqual(SAMPLE['user_id'], first.user_id)
        self.assertEqual(SAMPLE['volume'], first.volume)
        second = next(found)
        self.assertEqual(OLD_SAMPLE['counter_name'], second.counter_name)

    def test_create(self):
        sess = mock.Mock()
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=[SAMPLE])
        sess.post = mock.Mock(return_value=resp)

        data = {'sample_id': None,
                'counter_name': 'temperature',
                'project_id': 'project',
                'resource_id': 'resource',
                'type': 'gauge',
                'unit': 'instance',
                'volume': '98.6'}
        new_sample = sample.Sample.new(**data)

        new_sample.create(sess)
        url = '/meters/temperature'
        sess.post.assert_called_with(url, endpoint_filter=new_sample.service,
                                     json=[data])
        self.assertIsNone(new_sample.id)
