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
import json

import mock

from openstack import profile
from openstack import session
from openstack.cloud_eye import cloud_eye_service
from openstack.cloud_eye.v1 import _proxy
from openstack.tests.unit import base
from openstack.cloud_eye.v1 import metric as _metric
from openstack.tests.unit.test_proxy_base3 import BaseProxyTestCase


class TestCloudEyeProxy(BaseProxyTestCase):
    def __init__(self, *args, **kwargs):
        super(TestCloudEyeProxy, self).__init__(
            *args,
            proxy_class=_proxy.Proxy,
            service_class=cloud_eye_service.CloudEyeService,
            **kwargs)

    def test_list_metric(self):
        query = {
            'namespace': 'SYS.ECS',
            'metric_name': 'cpu_util',
            'dimensions': [{
                "name": "instance_id",
                "value": "d9112af5-6913-4f3b-bd0a-3f96711e004d"
            }],
            'order': 'desc',
            'marker': '3',
            'limit': 10
        }
        self.mock_response_json_file_values('list_metric.json')
        metrics = list(self.proxy.metrics(**query))

        transferred_query = {
            'namespace': 'SYS.ECS',
            'metric_name': 'cpu_util',
            'dim.0': 'instance_id,d9112af5-6913-4f3b-bd0a-3f96711e004d',
            'order': 'desc',
            'start': '3',
            'limit': 10
        }
        self.assert_session_get_with('/metrics', params=transferred_query)

        self.assertEquals(1, len(metrics))
        self.assertIsInstance(metrics[0], _metric.Metric)
        self.assertEquals("SYS.ECS", metrics[0].namespace)
        self.assertEquals("cpu_util", metrics[0].metric_name)
        self.assertEquals("%", metrics[0].unit)
        self.assertEquals([{
            "name": "instance_id",
            "value": "d9112af5-6913-4f3b-bd0a-3f96711e004d"
        }], metrics[0].dimensions)
