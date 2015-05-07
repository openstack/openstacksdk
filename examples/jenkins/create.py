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
Example Create a jenkins server

Create all the pieces parts to get a jenkins server up and running.

To run:
    python examples/jenkins/create.py
"""

import base64
import sys

from examples import common
from examples import connection
from examples.keypair import create as keypair
from examples.network import create as network


def create_jenkins(conn, name, opts):
    flavor = opts.data.pop('flavor', '103')
    image = opts.data.pop('image', 'bec3cab5-4722-40b9-a78a-3489218e22fe')

    ports = [9022, 443, 80, 8080, 422, 22]
    net = network.create(conn, name, opts, ports_to_open=ports)
    keypair.create(conn, name)

    server = conn.compute.find_server(name)
    if server is None:
        f = open('examples/cloud-init.sh', 'r')
        cmd = f.read()
        f.close()
        b64str = base64.b64encode(cmd)
        args = {
            "name": name,
            "flavorRef": flavor,
            "imageRef": image,
            "key_name": name,
            "networks": [{"uuid": net.id}],
            "user_data": b64str,
        }
        server = conn.compute.create_server(**args)
    else:
        server = conn.get(server)
    print(str(server))
    print('Waiting for the server to come up....')
    conn.compute.wait_for_server(server)
    print('Server is up.')

    if len(server.get_floating_ips()) <= 0:
        extnet = conn.network.find_network("Ext-Net")
        ip = conn.network.find_available_ip()
        if ip is None:
            ip = conn.network.create_ip(floating_network_id=extnet.id)
        port = next(conn.network.list_ports(device_id=server.id, fields='id'))
        conn.network.add_ip_to_port(port, ip)
        print(str(port))
        ip = conn.get(ip)
        print("ssh -i jenkins ubuntu@%s" % ip.floating_ip_address)
        print("http://%s:8080" % ip.floating_ip_address)
        print("login jenkins/demo")

    return


def run_jenkins(opts):
    conn = connection.make_connection(opts)
    name = opts.data.pop('name', 'jenkins')
    return(create_jenkins(conn, name, opts))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_jenkins))
