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

import mock
import testtools

from openstack.telemetry.v2 import statistics

EXAMPLE = {
    'aggregate': '1',
    'avg': '2',
    'count': '3',
    'duration': '4',
    'duration_end': '5',
    'duration_start': '6',
    'groupby': '7',
    'max': '8',
    'min': '9',
    'period': '10',
    'period_end': '11',
    'period_start': '12',
    'sum': '13',
    'unit': '14',
}


class TestStatistics(testtools.TestCase):

    def test_basic(self):
        sot = statistics.Statistics()
        self.assertEqual('statistics', sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/meters/%(meter_name)s/statistics', sot.base_path)
        self.assertEqual('metering', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = statistics.Statistics(EXAMPLE)
        self.assertIsNone(sot.id)
        self.assertEqual(EXAMPLE['aggregate'], sot.aggregate)
        self.assertEqual(EXAMPLE['avg'], sot.avg)
        self.assertEqual(EXAMPLE['count'], sot.count)
        self.assertEqual(EXAMPLE['duration'], sot.duration)
        self.assertEqual(EXAMPLE['duration_end'], sot.duration_end)
        self.assertEqual(EXAMPLE['duration_start'], sot.duration_start)
        self.assertEqual(EXAMPLE['groupby'], sot.group_by)
        self.assertEqual(EXAMPLE['max'], sot.max)
        self.assertEqual(EXAMPLE['min'], sot.min)
        self.assertEqual(EXAMPLE['period'], sot.period)
        self.assertEqual(EXAMPLE['period_end'], sot.period_end)
        self.assertEqual(EXAMPLE['period_start'], sot.period_start)
        self.assertEqual(EXAMPLE['sum'], sot.sum)
        self.assertEqual(EXAMPLE['unit'], sot.unit)

    def test_list(self):
        sess = mock.Mock()
        resp = mock.Mock()
        resp.body = [EXAMPLE]
        sess.get = mock.Mock(return_value=resp)

        args = {'meter_name': 'example'}
        reply = statistics.Statistics.list(sess, path_args=args)

        url = '/meters/example/statistics'
        self.assertEqual(1, len(reply))
        sess.get.assert_called_with(url, service=reply[0].service, params={})
        self.assertEqual(EXAMPLE['aggregate'], reply[0].aggregate)
        self.assertEqual(EXAMPLE['avg'], reply[0].avg)
        self.assertEqual(EXAMPLE['count'], reply[0].count)
        self.assertEqual(EXAMPLE['duration'], reply[0].duration)
        self.assertEqual(EXAMPLE['duration_end'], reply[0].duration_end)
        self.assertEqual(EXAMPLE['duration_start'], reply[0].duration_start)
        self.assertEqual(EXAMPLE['groupby'], reply[0].group_by)
        self.assertEqual(EXAMPLE['max'], reply[0].max)
        self.assertEqual(EXAMPLE['min'], reply[0].min)
        self.assertEqual(EXAMPLE['period'], reply[0].period)
        self.assertEqual(EXAMPLE['period_end'], reply[0].period_end)
        self.assertEqual(EXAMPLE['period_start'], reply[0].period_start)
        self.assertEqual(EXAMPLE['sum'], reply[0].sum)
        self.assertEqual(EXAMPLE['unit'], reply[0].unit)
