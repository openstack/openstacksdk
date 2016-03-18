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

import mock
import testtools

from openstack.telemetry.v2 import alarm_change

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'alarm_id': 0,
    'detail': '1',
    'event_id': IDENTIFIER,
    'on_behalf_of': '3',
    'project_id': '4',
    'timestamp': '2015-03-09T12:15:57.233772',
    'type': '6',
    'user_id': '7',
}


class TestAlarmChange(testtools.TestCase):

    def test_basic(self):
        sot = alarm_change.AlarmChange()
        self.assertEqual('alarm_change', sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/alarms/%(alarm_id)s/history', sot.base_path)
        self.assertEqual('metering', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = alarm_change.AlarmChange(EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['alarm_id'], sot.alarm_id)
        self.assertEqual(EXAMPLE['detail'], sot.detail)
        self.assertEqual(IDENTIFIER, sot.event_id)
        self.assertEqual(EXAMPLE['on_behalf_of'], sot.on_behalf_of_id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.triggered_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)

    def test_list(self):
        sess = mock.Mock()
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=[EXAMPLE, EXAMPLE])
        sess.get = mock.Mock(return_value=resp)
        path_args = {'alarm_id': IDENTIFIER}

        found = alarm_change.AlarmChange.list(sess, path_args=path_args)
        first = next(found)
        self.assertEqual(IDENTIFIER, first.id)
        self.assertEqual(EXAMPLE['alarm_id'], first.alarm_id)
        self.assertEqual(EXAMPLE['detail'], first.detail)
        self.assertEqual(IDENTIFIER, first.event_id)
        self.assertEqual(EXAMPLE['on_behalf_of'], first.on_behalf_of_id)
        self.assertEqual(EXAMPLE['project_id'], first.project_id)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, first.triggered_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['type'], first.type)
        self.assertEqual(EXAMPLE['user_id'], first.user_id)
