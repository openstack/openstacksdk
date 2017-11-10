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

import unittest

from openstack.tests.functional import base


@unittest.skip("bug/1524468")
class TestAlarmChange(base.BaseFunctionalTest):

    alarm = None

    def setUp(self):
        super(TestAlarmChange, self).setUp()
        self.require_service('alarming')
        self.require_service('metering')

        self.NAME = self.getUniqueString()
        meter = next(self.conn.telemetry.meters())
        self.alarm = self.conn.alarm.create_alarm(
            name=self.NAME,
            type='threshold',
            threshold_rule={
                'meter_name': meter.name,
                'threshold': 1.1,
            },
        )
        self.addCleanup(
            self.conn.alarm.delete_alarm, self.alarm, ignore_missing=False)

    def test_list(self):
        change = next(self.conn.alarm.alarm_changes(self.alarm))
        self.assertEqual(self.alarm.id, change.alarm_id)
        self.assertEqual('creation', change.type)
