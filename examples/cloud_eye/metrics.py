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


def list_metrics(connection):
    query = {
        "namespace": "SYS.ECS",
        # "metric_name": "cpu_util",
        # "dimensions": [{
        #     "name": "instance_id",
        #     "value": "9f31d05a-76d5-478a-b864-b1b5e8708482"
        # }],
        # "order": "desc",
        # "marker": ("SYS.ECS.cpu_util.instance_id:"
        #            "9f31d05a-76d5-478a-b864-b1b5e8708482"),
        "limit": 100
    }
    for metric in connection.cloud_eye.metrics(**query):
        logging.info(metric)


def list_favorite_metrics(connection):
    favorite_metrics = connection.cloud_eye.favorite_metrics()
    for metric in favorite_metrics:
        logging.info(metric)
