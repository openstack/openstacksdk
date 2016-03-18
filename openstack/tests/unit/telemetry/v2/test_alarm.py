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

from openstack.telemetry.v2 import alarm

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'alarm_actions': ['1'],
    'alarm_id': IDENTIFIER,
    'combination_rule': {'alarm_ids': ['2', 'b'], 'operator': 'or', },
    'description': '3',
    'enabled': True,
    'insufficient_data_actions': ['4'],
    'name': '5',
    'ok_actions': ['6'],
    'project_id': '7',
    'repeat_actions': False,
    'severity': 'low',
    'state': 'insufficient data',
    'state_timestamp': '2015-03-09T12:15:57.233772',
    'timestamp': '2015-03-09T12:15:57.233772',
    'threshold_rule': {'meter_name': 'a',
                       'evaluation_periods:': '1',
                       'period': '60',
                       'statistic': 'avg',
                       'threshold': '92.6',
                       'comparison_operator': 'gt',
                       'exclude_outliers': True, },
    'time_constraints': [{'name': 'a', 'duration': 'b', 'start': 'c', }],
    'type': '10',
    'user_id': '11',
}


class TestAlarm(testtools.TestCase):

    def setUp(self):
        super(TestAlarm, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = ''
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = alarm.Alarm()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/alarms', sot.base_path)
        self.assertEqual('metering', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = alarm.Alarm(EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['alarm_actions'], sot.alarm_actions)
        self.assertEqual(IDENTIFIER, sot.alarm_id)
        self.assertEqual(EXAMPLE['combination_rule'], sot.combination_rule)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertTrue(sot.is_enabled)
        self.assertEqual(EXAMPLE['insufficient_data_actions'],
                         sot.insufficient_data_actions)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['ok_actions'], sot.ok_actions)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertFalse(sot.is_repeat_actions)
        self.assertEqual(EXAMPLE['severity'], sot.severity)
        self.assertEqual(EXAMPLE['state'], sot.state)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.state_changed_at.replace(tzinfo=None))
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['threshold_rule'], sot.threshold_rule)
        self.assertEqual(EXAMPLE['time_constraints'], sot.time_constraints)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)

    def test_check_status(self):
        sot = alarm.Alarm(EXAMPLE)
        sot.check_state(self.sess)

        url = 'alarms/IDENTIFIER/state'
        self.sess.get.assert_called_with(url, endpoint_filter=sot.service)

    def test_change_status(self):
        sot = alarm.Alarm(EXAMPLE)
        self.assertEqual(self.resp.body, sot.change_state(self.sess, 'alarm'))

        url = 'alarms/IDENTIFIER/state'
        self.sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                         json='alarm')
