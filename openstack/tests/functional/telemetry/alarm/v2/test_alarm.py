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

from openstack.telemetry.alarm.v2 import alarm
from openstack.tests.functional import base


@unittest.skip("bug/1524468")
class TestAlarm(base.BaseFunctionalTest):

    ID = None

    def setUp(self):
        super(TestAlarm, self).setUp()
        self.require_service('alarming')
        self.require_service('metering')

        self.NAME = self.getUniqueString()
        meter = next(self.conn.telemetry.meters())
        sot = self.conn.alarm.create_alarm(
            name=self.NAME,
            type='threshold',
            threshold_rule={
                'meter_name': meter.name,
                'threshold': 1.1,
            },
        )
        assert isinstance(sot, alarm.Alarm)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id

    def tearDown(self):
        sot = self.conn.alarm.delete_alarm(self.ID, ignore_missing=False)
        self.assertIsNone(sot)
        super(TestAlarm, self).tearDown()

    def test_get(self):
        sot = self.conn.alarm.get_alarm(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        names = [o.name for o in self.conn.alarm.alarms()]
        self.assertIn(self.NAME, names)
