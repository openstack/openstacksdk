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
import uuid

from openstack.tests.functional import base
from openstack.tests.functional.auto_scaling.v1.test_config import \
    auto_create_config
from openstack.tests.functional.auto_scaling.v1.test_group import \
    auto_create_group
from openstack.tests.functional.auto_scaling.v1.test_policy import create_policy


class TestActivity(base.BaseFunctionalTest):
    group = "588b4592-0998-4722-b51d-e6dbc574ec32"

    def test_list_activity(self):
        query = {
            "start_time": "2017-06-22T01:21:02Z",
            "end_time": "2017-06-22T15:00:02Z",
            "limit": 10
        }
        activities = self.conn.auto_scaling.activities(self.group, **query)
        for activity in activities:
            print activity
