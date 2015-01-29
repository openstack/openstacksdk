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
    python examples/jenkins.py
"""

import base64
import os
import sys

from examples import common
from openstack import connection


def create_jenkins(opts):
    name = opts.data.pop('name', 'jenkins')
    dns_nameservers = opts.data.pop('dns_nameservers', '206.164.176.34')
    cidr = opts.data.pop('cidr', '10.3.3.0/24')
    flavor = opts.data.pop('flavor', '103')
    image = opts.data.pop('image', 'bec3cab5-4722-40b9-a78a-3489218e22fe')

    args = vars(opts)
    conn = connection.Connection(preference=opts.user_preferences, **args)

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
        print(str(sg))
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': 'tcp',
            'port_range_max': 9022,
            'port_range_min': 9022,
            'security_group_id': sg.id,
            'ethertype': 'IPv4'
        }
        conn.network.create_security_group_rule(**rule)
        print('rule allow 9022')
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': 'tcp',
            'port_range_max': 443,
            'port_range_min': 443,
            'security_group_id': sg.id,
            'ethertype': 'IPv4'
        }
        conn.network.create_security_group_rule(**rule)
        print('rule allow HTTPS')
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': 'icmp',
            'port_range_max': None,
            'port_range_min': None,
            'security_group_id': sg.id,
            'ethertype': 'IPv4'
        }
        conn.network.create_security_group_rule(**rule)
        print('rule allow ping')
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': 'tcp',
            'port_range_max': 80,
            'port_range_min': 80,
            'security_group_id': sg.id,
            'ethertype': 'IPv4'
        }
        conn.network.create_security_group_rule(**rule)
        print('rule allow HTTP')
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': None,
            'protocol': None,
            'port_range_max': None,
            'port_range_min': None,
            'security_group_id': sg.id,
            'ethertype': 'IPv6'
        }
        conn.network.create_security_group_rule(**rule)
        print('rule allow IPv6')
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': 'tcp',
            'port_range_max': 8080,
            'port_range_min': 8080,
            'security_group_id': sg.id,
            'ethertype': 'IPv4'
        }
        conn.network.create_security_group_rule(**rule)
        print('rule allow 8080')
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': 'tcp',
            'port_range_max': 4222,
            'port_range_min': 4222,
            'security_group_id': sg.id,
            'ethertype': 'IPv4'
        }
        conn.network.create_security_group_rule(**rule)
        print('rule allow 4222')
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': 'tcp',
            'port_range_max': 22,
            'port_range_min': 22,
            'security_group_id': sg.id,
            'ethertype': 'IPv4'
        }
        conn.network.create_security_group_rule(**rule)
        print('rule allow ssh')
    print(str(sg))

    kp = conn.compute.find_keypair(name)
    if kp is None:
        kp = conn.compute.create_keypair(name=name)
        try:
            os.remove('jenkins')
        except OSError:
            pass
        try:
            os.remove('jenkins.pub')
        except OSError:
            pass
        print(str(kp))
        f = open('jenkins', 'w')
        f.write("%s" % kp.private_key)
        f.close()
        f = open('jenkins.pub', 'w')
        f.write("%s" % kp.public_key)
        f.close()
    print(str(kp))

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
            "imageRef": image,
            "key_name": name,
            "networks": [{"uuid": network.id}],
            "user_data": b64str,
        }
        server = conn.compute.create_server(**args)
    else:
        server = conn.get(server)
    print(str(server))
    print('Waiting for the server to come up....')
    conn.compute.wait_for_status(server)
    print('Server is up.')

    if len(server.get_floating_ips()) <= 0:
        ip = conn.network.find_available_ip()
        if ip is None:
            ip = conn.network.create_ip(floating_network_id=extnet.id)
        port = next(conn.network.list_ports(device_id=server.id, fields='id'))
        conn.network.add_ip_to_port(port, ip)
        print(str(port))
        ip = conn.get(ip)
        print("ssh -i jenkins ubuntu@%s" % ip.floating_ip_address)
        print("http://%s:8080" % ip.floating_ip_address)

    return


def delete_jenkins(opts):
    name = opts.data.pop('name', 'jenkins')
    args = vars(opts)
    conn = connection.Connection(preference=opts.user_preferences, **args)

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

    kp = conn.compute.find_keypair(name)
    if kp is not None:
        print(str(kp))
        conn.delete(kp)

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


def run_jenkins(opts):
    argument = opts.argument
    if argument == "delete":
        return(delete_jenkins(opts))
    return(create_jenkins(opts))


if __name__ == "__main__":
    opts = common.setup()
    sys.exit(common.main(opts, run_jenkins))
