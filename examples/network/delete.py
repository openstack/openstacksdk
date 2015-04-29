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
Network examples

Destroy all the pieces parts of a working network.

To run:
    python examples/network/delete.py
"""

import sys

from examples import common
from examples import connection


def delete(conn, name):

    router = conn.network.find_router(name)
    if router is not None:
        print(str(router))

    subnet = conn.network.find_subnet(name)
    if subnet is not None:
        print(str(subnet))
        if router:
            try:
                conn.network.router_remove_interface(router, subnet.id)
            except Exception:
                pass
        for port in conn.network.get_subnet_ports(subnet.id):
            print(str(port))
            conn.delete(port)

    if router is not None:
        conn.delete(router)

    if subnet:
        conn.delete(subnet)

    network = conn.network.find_network(name)
    if network is not None:
        print(str(network))
        conn.delete(network)


def run_network(opts):
    name = opts.data.pop('name', 'netty')
    conn = connection.make_connection(opts)
    return(delete(conn, name))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_network))
