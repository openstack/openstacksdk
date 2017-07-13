#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from openstack.tests.functional import base


class TestAlarm(base.BaseFunctionalTest):
    alarm = None

    @classmethod
    def setUpClass(cls):
        super(TestAlarm, cls).setUpClass()
        alarms = list(cls.conn.cloud_eye.alarms(limit=20, order="desc"))
        if len(alarms) > 0:
            cls.alarm = alarms[0]
        else:
            raise Exception("No exists alarm for unittest")

    def test_list_alarm(self):
        pass

    def test_get_alarm(self):
        alarm = self.conn.cloud_eye.get_alarm(self.alarm.id)
        self.assertEqual(self.alarm, alarm)

    def test_alarm_actions(self):
        if self.alarm.alarm_enabled:
            self.conn.cloud_eye.disable_alarm(self.alarm)
            self.alarm = self.conn.cloud_eye.get_alarm(self.alarm)
            self.assertFalse(self.alarm.alarm_enabled)

        self.conn.cloud_eye.enable_alarm(self.alarm)
        self.alarm = self.conn.cloud_eye.get_alarm(self.alarm)
        self.assertTrue(self.alarm.alarm_enabled)
