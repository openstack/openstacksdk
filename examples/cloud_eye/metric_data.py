# Copyright 2017 HuaWei Tld
# Copyright 2017 OpenStack.org
#
# Licensed under the Apache License, Version 2.0 (the 'License'); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import datetime
import logging

from openstack import utils


def list_metric_aggregations(connection):
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
    for aggregation in connection.cloud_eye.metric_aggregations(**query):
        logging.info(aggregation)


def add_metric_data(connection):
    data = [
        {
            "metric": {
                "namespace": "MINE.APP",
                "dimensions": [
                    {
                        "name": "instance_id",
                        "value": "33328f02-3814-422e-b688-bfdba93d4050"
                    }
                ],
                "metric_name": "cpu_util"
            },
            "ttl": 172800,
            "collect_time": 1463598260000,
            "value": 60,
            "unit": "%"
        },
        {
            "metric": {
                "namespace": "MINE.APP",
                "dimensions": [
                    {
                        "name": "instance_id",
                        "value": "33328f02-3814-422e-b688-bfdba93d4050"
                    }
                ],
                "metric_name": "cpu_util"
            },
            "ttl": 172800,
            "collect_time": 1463598270000,
            "value": 70,
            "unit": "%"
        }
    ]
    connection.cloud_eye.add_metric_data(data)
