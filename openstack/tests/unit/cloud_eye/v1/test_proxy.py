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

from openstack.cloud_eye import cloud_eye_service
from openstack.cloud_eye.v1 import _proxy
from openstack.cloud_eye.v1 import alarm as _alarm
from openstack.cloud_eye.v1 import metric as _metric
from openstack.cloud_eye.v1 import metric_data as _metric_data
from openstack.cloud_eye.v1 import quota as _quota
from openstack.tests.unit.test_proxy_base3 import BaseProxyTestCase
from openstack import utils


class TestCloudEyeProxy(BaseProxyTestCase):
    def __init__(self, *args, **kwargs):
        super(TestCloudEyeProxy, self).__init__(
            *args,
            proxy_class=_proxy.Proxy,
            service_class=cloud_eye_service.CloudEyeService,
            **kwargs)


class TestCloudEyeMetric(TestCloudEyeProxy):
    def __init__(self, *args, **kwargs):
        super(TestCloudEyeMetric, self).__init__(*args, **kwargs)

    def test_list_metrics(self):
        query = {
            "namespace": "SYS.ECS",
            "metric_name": "cpu_util",
            "dimensions": [{
                "name": "instance_id",
                "value": "d9112af5-6913-4f3b-bd0a-3f96711e004d"
            }],
            "order": "desc",
            "marker": "3",
            "limit": 10
        }
        self.mock_response_json_file_values("list_metric.json")
        metrics = list(self.proxy.metrics(**query))

        transferred_query = {
            "namespace": "SYS.ECS",
            "metric_name": "cpu_util",
            "dim.0": "instance_id,d9112af5-6913-4f3b-bd0a-3f96711e004d",
            "order": "desc",
            "start": "3",
            "limit": 10
        }
        self.assert_session_list_with("/metrics", params=transferred_query)

        self.assertEqual(1, len(metrics))
        self.assertIsInstance(metrics[0], _metric.Metric)
        self.assertEqual("SYS.ECS", metrics[0].namespace)
        self.assertEqual("cpu_util", metrics[0].metric_name)
        self.assertEqual("%", metrics[0].unit)
        self.assertEqual([{
            "name": "instance_id",
            "value": "d9112af5-6913-4f3b-bd0a-3f96711e004d"
        }], metrics[0].dimensions)

    def test_list_favorite_metrics(self):
        self.mock_response_json_file_values("list_metric.json")
        favorite_metrics = list(self.proxy.favorite_metrics())
        self.assert_session_list_with("/favorite-metrics", params={})

        self.assertEqual(1, len(favorite_metrics))
        self.assertIsInstance(favorite_metrics[0], _metric.Metric)
        self.assertEqual("SYS.ECS", favorite_metrics[0].namespace)
        self.assertEqual("cpu_util", favorite_metrics[0].metric_name)
        self.assertEqual("%", favorite_metrics[0].unit)
        self.assertEqual([{
            "name": "instance_id",
            "value": "d9112af5-6913-4f3b-bd0a-3f96711e004d"
        }], favorite_metrics[0].dimensions)


class TestCloudEyeAlarm(TestCloudEyeProxy):
    def __init__(self, *args, **kwargs):
        super(TestCloudEyeAlarm, self).__init__(*args, **kwargs)

    def test_list_alarms(self):
        response_json = self.get_file_content("list_alarm.json")
        self.response.json.side_effect = [response_json, {}]

        query = {
            "marker": "last-alarm-id",
            "order": "desc"
        }
        alarms = list(self.proxy.alarms(**query))
        self.session.get.assert_has_calls([
            mock.call("/alarms",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      headers={"Accept": "application/json"},
                      params={"start": "last-alarm-id",
                              "order": "desc"}),
            mock.call("/alarms",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      headers={"Accept": "application/json"},
                      params={"start": "al1441967036681YkazZ0deN",
                              "limit": 1,
                              "order": "desc"}),
        ])
        self.assertEqual(1, len(alarms))
        self._verify_alarm_properties(alarms[0])

    def test_get_alarm_with_id(self):
        self.mock_response_json_file_values("get_alarm.json")
        alarm = self.proxy.get_alarm("al1441967036681YkazZ0deN")
        self.session.get.assert_called_once_with(
            "alarms/al1441967036681YkazZ0deN",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        self._verify_alarm_properties(alarm)

    def test_get_alarm_with_instance(self):
        self.mock_response_json_file_values("get_alarm.json")
        instance = _alarm.Alarm(id="al1441967036681YkazZ0deN")
        alarm = self.proxy.get_alarm(instance)
        self.session.get.assert_called_once_with(
            "alarms/al1441967036681YkazZ0deN",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        self._verify_alarm_properties(alarm)

    def _verify_alarm_properties(self, alarm):
        self.assertIsInstance(alarm, _alarm.Alarm)
        self.assertEqual("al1441967036681YkazZ0deN", alarm.id)
        self.assertEqual("test0911_1825", alarm.name)
        self.assertEqual("", alarm.description)
        self.assertEqual("ok", alarm.state)
        self.assertEqual(True, alarm.alarm_enabled)
        self.assertEqual({
            "period": 300,
            "filter": "average",
            "comparison_operator": ">=",
            "value": 2,
            "unit": "Count",
            "count": 1
        }, alarm.condition)
        self.assertEqual(_metric.Metric.new(**{
            "namespace": "SYS.ECS",
            "dimensions": [
                {
                    "name": "instance_id",
                    "value": "d9112af5-6913-4f3b-bd0a-3f96711e004d"
                }
            ],
            "metric_name": "cpu_util"
        }), alarm.metric)

    def test_delete_alarm(self):
        self.proxy.delete_alarm("al1441967036681YkazZ0deN")
        self.assert_session_delete("alarms/al1441967036681YkazZ0deN")

    def test_enable_alarm(self):
        self.proxy.enable_alarm("al1441967036681YkazZ0deN")
        uri = "alarms/al1441967036681YkazZ0deN/action"
        self.assert_session_put_with(uri, json={"alarm_enabled": True})

    def test_disable_alarm(self):
        self.proxy.disable_alarm("al1441967036681YkazZ0deN")
        uri = "alarms/al1441967036681YkazZ0deN/action"
        self.assert_session_put_with(uri, json={"alarm_enabled": False})


class TestCloudEyeMetricData(TestCloudEyeProxy):
    def __init__(self, *args, **kwargs):
        super(TestCloudEyeMetricData, self).__init__(*args, **kwargs)

    def test_list_metric_aggregations(self):
        start_time = datetime.datetime(2017, 6, 18, hour=18)
        end_time = datetime.datetime(2017, 6, 19, hour=18)
        query = {
            "namespace": "SYS.ECS",
            "metric_name": "cpu_util",
            "from": utils.get_epoch_time(start_time),
            "to": utils.get_epoch_time(end_time),
            "period": 300,
            "filter": "average",
            "dimensions": [{
                "name": "instance_id",
                "value": "d9112af5-6913-4f3b-bd0a-3f96711e004d"
            }]
        }
        self.mock_response_json_file_values("list_metric_aggregations.json")
        aggregations = list(self.proxy.metric_aggregations(**query))

        transferred_query = {
            "namespace": "SYS.ECS",
            "metric_name": "cpu_util",
            "from": 1497780000000,
            "to": 1497866400000,
            "period": 300,
            "filter": "average",
            "dim.0": "instance_id,d9112af5-6913-4f3b-bd0a-3f96711e004d",
        }
        self.assert_session_list_with("/metric-data", params=transferred_query)

        self.assertEqual(1, len(aggregations))
        aggregation = aggregations[0]
        self.assertIsInstance(aggregation, _metric_data.MetricAggregation)
        self.assertEqual(0, aggregation.average)
        self.assertEqual(1442341200000, aggregation.timestamp)
        self.assertEqual("Count", aggregation.unit)

    def test_add_metric_data(self):
        data = self.get_file_content('add_metric_data.json')
        self.proxy.add_metric_data(data)
        self.session.post.assert_called_once_with(
            "/metric-data",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
            json=data
        )


class TestCloudEyeQuota(TestCloudEyeProxy):
    def __init__(self, *args, **kwargs):
        super(TestCloudEyeQuota, self).__init__(*args, **kwargs)

    def test_list_quota(self):
        self.mock_response_json_file_values("list_quota.json")
        quotas = list(self.proxy.quotas())
        self.assert_session_list_with("/quotas")
        quota = quotas[0]
        self.assertIsInstance(quota, _quota.Quota)
        self.assertEqual("alarm", quota.type)
        self.assertEqual("", quota.unit)
        self.assertEqual(0, quota.used)
        self.assertEqual(20, quota.quota)
