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

from examples.connect import create_connection_from_config

# utils.enable_logging(debug=False, stream=sys.stdout)

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

# initial connection
connection = create_connection_from_config()

# run examples


