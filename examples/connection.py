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
    # TODO(thowe): There is a general smell here that this code is
    # repeated in two places at that we flatten the auth structure.
    # The connection class should take OCC config and just deal, but
    # I'd just like to get cacert working for now.
    auth = cloud.config['auth']
    if 'cacert' in cloud.config:
        auth['verify'] = cloud.config['cacert']
    if 'insecure' in cloud.config:
        auth['verify'] = not bool(cloud.config['insecure'])
    conn = connection.Connection(profile=opts.preferences, **auth)
    return conn


def run_connection(opts):
    conn = make_connection(opts)
    print("Connection: %s" % conn)
    for resource in conn.compute.flavors():
        print(resource)
    return


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_connection))
