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

import datetime
import uuid

from openstack.tests.functional import base
from openstack import utils


class TestMetricData(base.BaseFunctionalTest):
    NAME = "SDK_" + uuid.uuid4().hex
    now = datetime.datetime.now()
    dimensions = [{
        "name": "instance_id",
        "value": "33328f02-3814-422e-b688-bfdba93d4050"
    }]

    @classmethod
    def setUpClass(cls):
        super(TestMetricData, cls).setUpClass()

    def test_1_add_metric_data(self):
        data = [
            {
                "metric": {
                    "namespace": "SDK.unittests",
                    "dimensions": self.dimensions,
                    "metric_name": "cpu_util"
                },
                "ttl": 604800,
                "collect_time": utils.get_epoch_time(
                    self.now - datetime.timedelta(minutes=5)),
                "value": 60,
                "unit": "%"
            },
            {
                "metric": {
                    "namespace": "SDK.unittests",
                    "dimensions": self.dimensions,
                    "metric_name": "cpu_util"
                },
                "ttl": 604800,
                "collect_time": utils.get_epoch_time(self.now),
                "value": 60,
                "unit": "%"
            }
        ]
        self.conn.cloud_eye.add_metric_data(data)

    def test_2_list_metric_aggr_data(self):
        query = {
            "namespace": "SDK.unittests",
            "metric_name": "cpu_util",
            "from": utils.get_epoch_time(
                self.now - datetime.timedelta(minutes=5)),
            "to": utils.get_epoch_time(self.now),
            "period": 300,
            "filter": "average",
            "dimensions": self.dimensions
        }
        aggregations = list(self.conn.cloud_eye.metric_aggregations(**query))
        self.assertTrue(len(aggregations) == 2)
        self.assertEqual(60, aggregations[0].average)
        self.assertEqual(60, aggregations[1].average)
