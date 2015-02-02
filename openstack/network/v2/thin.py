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

"""Thin interface to network objects.

This class provides a meaningful thin interface to network objects.  The
interface does not create resource objects, it just returns dictionairies.
Except in special cases, the signatures of the methods are as follows:

    create_*(session, attrs, r_id=None, path_args=None)
    delete_*(session, r_id, path_args=None)
    find_*(session, name_or_id, path_args=None, id_only=True)
    get_*(session, r_id, path_args=None, include_headers=False)
    head_*(session, r_id, path_args=None)
    list_*(session, limit=None, marker=None, path_args=None, **params)
    update_*(session, r_id, attrs, path_args=None)

Examples
--------

Find a router and update the administrative state.

    from openstack.network.v2 import thin
    requests = thin.Thin()
    my_router = requests.find_router(session, 'awesome'):
    my_router['admin_state_up'] = False
    requests.update_router(session, my_router['id], my_router)

"""

from openstack.network.v2 import floating_ip
from openstack.network.v2 import network
from openstack.network.v2 import port
from openstack.network.v2 import router
from openstack.network.v2 import security_group as group
from openstack.network.v2 import security_group_rule as rule
from openstack.network.v2 import subnet


class Thin(object):

    create_ip = floating_ip.FloatingIP.create_by_id
    delete_ip = floating_ip.FloatingIP.delete_by_id
    find_ip = floating_ip.FloatingIP.find
    get_ip = floating_ip.FloatingIP.get_data_by_id
    list_ips = floating_ip.FloatingIP.list
    update_ip = floating_ip.FloatingIP.update_by_id

    create_network = network.Network.create_by_id
    delete_network = network.Network.delete_by_id
    find_network = network.Network.find
    get_network = network.Network.get_data_by_id
    list_networks = network.Network.list
    update_network = network.Network.update_by_id

    create_port = port.Port.create_by_id
    delete_port = port.Port.delete_by_id
    find_port = port.Port.find
    get_port = port.Port.get_data_by_id
    list_ports = port.Port.list
    update_port = port.Port.update_by_id

    create_router = router.Router.create_by_id
    delete_router = router.Router.delete_by_id
    find_router = router.Router.find
    get_router = router.Router.get_data_by_id
    list_routers = router.Router.list
    update_router = router.Router.update_by_id

    create_security_group = group.SecurityGroup.create_by_id
    delete_security_group = group.SecurityGroup.delete_by_id
    find_security_group = group.SecurityGroup.find
    get_security_group = group.SecurityGroup.get_data_by_id
    list_security_groups = group.SecurityGroup.list
    update_security_group = group.SecurityGroup.update_by_id

    create_security_group_rule = rule.SecurityGroupRule.create_by_id
    delete_security_group_rule = rule.SecurityGroupRule.delete_by_id
    find_security_group_rule = rule.SecurityGroupRule.find
    get_security_group_rule = rule.SecurityGroupRule.get_data_by_id
    list_security_group_rules = rule.SecurityGroupRule.list
    update_security_group_rule = rule.SecurityGroupRule.update_by_id

    create_subnet = subnet.Subnet.create_by_id
    delete_subnet = subnet.Subnet.delete_by_id
    find_subnet = subnet.Subnet.find
    get_subnet = subnet.Subnet.get_data_by_id
    list_subnets = subnet.Subnet.list
    update_subnet = subnet.Subnet.update_by_id
