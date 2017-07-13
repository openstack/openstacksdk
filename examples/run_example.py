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

import logging
import os

from examples.cloud_eye import metric_data
from examples.cloud_eye import metrics
from examples.connect import create_connection_from_config
from examples.load_balancer import load_balancer

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
root_log = logging.getLogger()
root_log.setLevel(logging.DEBUG)
requests_log = logging.getLogger('requests.packages.urllib3')
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# setup endpoint overrides
os.environ.setdefault(
    'OS_CLOUD_EYE_ENDPOINT_OVERRIDE',
    'https://ces.eu-de.otc.t-systems.com/V1.0/%(project_id)s'
)

os.environ.setdefault(
    'OS_LOAD_BALANCER_ENDPOINT_OVERRIDE',
    'https://elb.eu-de.otc.t-systems.com/v1.0/%(project_id)s'
)

os.environ.setdefault(
    'OS_MAP_REDUCE_ENDPOINT_OVERRIDE',
    'https://mrs.eu-de.otc.t-systems.com/v1.1/%(project_id)s'
)

# initial connection
conn = create_connection_from_config()
detail = conn.map_reduce.get_cluster("0f4ab6b7-a723-4b6c-b326-f8a5711d365a")
#
# load_balancer.list_loadbalancers(conn)

# subnets = conn.network.subnets(limit=1)
# routers = conn.network.routers(limit=1)
# for subnet in routers:
#     print subnet
#     break
# Cloud Eye Examples
# metrics.list_metrics(conn)
# metrics.list_favorite_metrics(connection)

# alarms.list_alarms(connection)
# alarms.enable_alarm(connection)
# alarms.get_alarm(connection)
# alarms.disable_alarm(connection)

# metric_data.add_metric_data(conn)
# metric_data.list_metric_aggregations(conn)

# quotas.list_quotas(connection)
