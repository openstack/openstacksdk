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

"""
Example Connection Command

Make sure you can authenticate before running this command.

For example:
    python -m examples.connection
"""

import sys

import os_client_config

from examples import common
from openstack import connection


def make_connection(opts):
    occ = os_client_config.OpenStackConfig()
    cloud = occ.get_one_cloud(opts.cloud, opts)
    opts.preferences.set_region(opts.preferences.ALL, cloud.region)
    auth = cloud.config['auth']
    if 'insecure' in cloud.config:
        auth['verify'] = cloud.config['insecure']
    conn = connection.Connection(profile=opts.preferences, **auth)
    return conn


def run_connection(opts):
    conn = make_connection(opts)
    print("Connection: %s" % conn)
    for flavor in conn.compute.flavors():
        print(flavor.id + " " + flavor.name)
    return


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_connection))
