# Copyright 2017 HuaWei Tld
# Copyright 2017 OpenStack.org
#
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

import logging


def list_alarms(connection):
    query = {
        "limit": 1,
        # "marker": "last-alarm-id",
        "order": "desc"
    }
    for alarm in connection.cloud_eye.alarms(**query):
        logging.info(alarm)


def get_alarm(connection):
    alarm_id = "al1483387711418ZNpR8DX3g"
    alarm = connection.cloud_eye.get_alarm(alarm_id)
    logging.info(alarm)


def delete_alarm(connection):
    alarm_id = "al1483387711418ZNpR8DX3g"
    connection.cloud_eye.delete_alarm(alarm_id)


def enable_alarm(connection):
    alarm_id = "al1483387711418ZNpR8DX3g"
    connection.cloud_eye.enable_alarm(alarm_id)


def disable_alarm(connection):
    alarm_id = "al1483387711418ZNpR8DX3g"
    connection.cloud_eye.disable_alarm(alarm_id)
