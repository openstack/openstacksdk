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
import uuid

from openstack.tests.functional import base


@unittest.skip("bug/1524468")
@unittest.skipUnless(base.service_exists(service_type="metering"),
                     "Metering service does not exist")
@unittest.skipUnless(base.service_exists(service_type="alarming"),
                     "Alarming service does not exist")
class TestAlarmChange(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex
    alarm = None

    @classmethod
    def setUpClass(cls):
        super(TestAlarmChange, cls).setUpClass()
        meter = next(cls.conn.telemetry.meters())
        alarm = cls.conn.alarm.create_alarm(
            name=cls.NAME,
            type='threshold',
            threshold_rule={
                'meter_name': meter.name,
                'threshold': 1.1,
            },
        )
        cls.alarm = alarm

    @classmethod
    def tearDownClass(cls):
        cls.conn.alarm.delete_alarm(cls.alarm, ignore_missing=False)

    def test_list(self):
        change = next(self.conn.alarm.alarm_changes(self.alarm))
        self.assertEqual(self.alarm.id, change.alarm_id)
        self.assertEqual('creation', change.type)
