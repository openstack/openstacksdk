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

Create all the pieces parts to have a working network.

To run:
    python examples/network/create.py
"""

import sys

from examples import common
from examples import connection


def create(conn, name, opts, ports_to_open=[80, 22]):
    dns_nameservers = opts.data.pop('dns_nameservers', '206.164.176.34')
    cidr = opts.data.pop('cidr', '10.3.3.0/24')

    network = conn.network.find_network(name)
    if network is None:
        network = conn.network.create_network(name=name)
    print(str(network))

    subnet = conn.network.find_subnet(name)
    if subnet is None:
        args = {
            "name": name,
            "network_id": network.id,
            "ip_version": "4",
            "dns_nameservers": [dns_nameservers],
            "cidr": cidr,
        }
        subnet = conn.network.create_subnet(**args)
    print(str(subnet))

    extnet = conn.network.find_network("Ext-Net")
    router = conn.network.find_router(name)
    if router is None:
        args = {
            "name": name,
            "external_gateway_info": {"network_id": extnet.id}
        }
        router = conn.network.create_router(**args)
        conn.network.router_add_interface(router, subnet.id)
    print(str(router))

    sg = conn.network.find_security_group(name)
    if sg is None:
        sg = conn.network.create_security_group(name=name)
        for port in ports_to_open:
            conn.network.security_group_open_port(sg.id, port)
        conn.network.security_group_allow_ping(sg.id)
    print(str(sg))

    return network


def run_network(opts):
    name = opts.data.pop('name', 'netty')
    conn = connection.make_connection(opts)
    return(create(conn, name, opts))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_network))
