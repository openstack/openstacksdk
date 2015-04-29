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
Example Delete a jenkins server

Delete all the pieces parts to your jenkins server.

To run:
    python examples/jenkins/delete.py
"""

import sys

from examples import common
from examples import connection
from examples.keypair import delete as keypair
from examples.network import delete as network


def delete_jenkins(conn, name, opts):
    server = conn.compute.find_server(name)
    if server is not None:
        server = conn.get(server)
        print(str(server))
        ips = server.get_floating_ips()
        for ip in ips:
            print(str(ip))
            ip = conn.network.find_ip(ip)
            conn.network.remove_ip_from_port(ip)
            conn.delete(ip)
        conn.delete(server)

    keypair.delete(conn, name)
    network.delete(conn, name)


def run_jenkins(opts):
    conn = connection.make_connection(opts)
    name = opts.data.pop('name', 'jenkins')
    return(delete_jenkins(conn, name, opts))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_jenkins))
