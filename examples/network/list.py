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
List resources from the Network service.

For a full guide see TODO(etoews):link to docs on developer.openstack.org
"""


def list_networks(conn):
    print("List Networks:")

    for network in conn.network.networks():
        print(network)


def list_subnets(conn):
    print("List Subnets:")

    for subnet in conn.network.subnets():
        print(subnet)


def list_ports(conn):
    print("List Ports:")

    for port in conn.network.ports():
        print(port)


def list_security_groups(conn):
    print("List Security Groups:")

    for port in conn.network.security_groups():
        print(port)


def list_routers(conn):
    print("List Routers:")

    for router in conn.network.routers():
        print(router)


def list_network_agents(conn):
    print("List Network Agents:")

    for agent in conn.network.agents():
        print(agent)
