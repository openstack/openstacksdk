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
import sys

from examples.connect import create_connection_from_config
from openstack import utils
from openstack.dns.v2.zone import Zone

# utils.enable_logging(debug=False, stream=sys.stdout)

# You must initialize logging, otherwise you'll not see debug output.
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
root_log = logging.getLogger()
root_log.setLevel(logging.DEBUG)
requests_log = logging.getLogger('requests.packages.urllib3')
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

os.environ.setdefault(
    'OS_CLOUD_EYE_ENDPOINT_OVERRIDE',
    'https://ces.eu-de.otc.t-systems.com/V1.0/%(project_id)s'
)
connection = create_connection_from_config()


def list_metrics(conn):
    query = {
        'limit': 10
    }
    for metric in conn.cloud_eye.metrics(**query):
        logging.info(metric)


list_metrics(connection)
