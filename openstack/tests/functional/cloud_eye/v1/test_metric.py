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

from openstack.cloud_eye.v1 import metric
from openstack.tests.functional import base


class TestMetric(base.BaseFunctionalTest):
    @classmethod
    def setUpClass(cls):
        super(TestMetric, cls).setUpClass()

    def test_list_metric(self):
        query = {
            "namespace": "SYS.ECS",
            "metric_name": "cpu_util",
            "limit": 10
        }
        names = [metric.metric_name for metric in
                 self.conn.cloud_eye.metrics(**query)]
        self.assertIn("cpu_util", names)

    def test_list_favorite_metric(self):
        metrics = list(self.conn.cloud_eye.favorite_metrics())
        if len(metrics) > 0:
            self.assertIsInstance(metrics[0], metric.FavoriteMetric)
