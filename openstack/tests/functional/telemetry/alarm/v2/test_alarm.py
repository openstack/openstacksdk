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

from openstack.telemetry.alarm.v2 import alarm
from openstack.tests.functional import base


@unittest.skip("bug/1524468")
@unittest.skipUnless(base.service_exists(service_type="alarming"),
                     "Alarming service does not exist")
@unittest.skipUnless(base.service_exists(service_type="metering"),
                     "Metering service does not exist")
class TestAlarm(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex
    ID = None

    @classmethod
    def setUpClass(cls):
        super(TestAlarm, cls).setUpClass()
        meter = next(cls.conn.telemetry.meters())
        sot = cls.conn.alarm.create_alarm(
            name=cls.NAME,
            type='threshold',
            threshold_rule={
                'meter_name': meter.name,
                'threshold': 1.1,
            },
        )
        assert isinstance(sot, alarm.Alarm)
        cls.assertIs(cls.NAME, sot.name)
        cls.ID = sot.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.alarm.delete_alarm(cls.ID, ignore_missing=False)
        cls.assertIs(None, sot)

    def test_get(self):
        sot = self.conn.alarm.get_alarm(self.ID)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.ID, sot.id)

    def test_list(self):
        names = [o.name for o in self.conn.alarm.alarms()]
        self.assertIn(self.NAME, names)
