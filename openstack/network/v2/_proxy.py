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

from openstack.network.v2 import extension
from openstack.network.v2 import floating_ip
from openstack.network.v2 import health_monitor
from openstack.network.v2 import listener
from openstack.network.v2 import load_balancer
from openstack.network.v2 import metering_label
from openstack.network.v2 import metering_label_rule
from openstack.network.v2 import network
from openstack.network.v2 import pool
from openstack.network.v2 import pool_member
from openstack.network.v2 import port
from openstack.network.v2 import quota
from openstack.network.v2 import router
from openstack.network.v2 import security_group
from openstack.network.v2 import security_group_rule
from openstack.network.v2 import subnet


class Proxy(object):

    def __init__(self, session):
        self.session = session

    def find_extension(self, name_or_id):
        return extension.Extension.find(self.session, name_or_id)

    def list_extensions(self):
        return extension.Extension.list(self.session)

    def create_ip(self, **data):
        return floating_ip.FloatingIP(data).create(self.session)

    def delete_ip(self, **data):
        floating_ip.FloatingIP(**data).delete(self.session)

    def find_available_ip(self):
        return floating_ip.FloatingIP.find_available(self.session)

    def find_ip(self, name_or_id):
        return floating_ip.FloatingIP.find(self.session, name_or_id)

    def get_ip(self, **data):
        return floating_ip.FloatingIP(**data).get(self.session)

    def list_ips(self, **params):
        return floating_ip.FloatingIP.list(self.session, **params)

    def update_ip(self, **data):
        return floating_ip.FloatingIP(**data).update(self.session)

    def create_health_monitor(self, **data):
        return health_monitor.HealthMonitor(data).create(self.session)

    def delete_health_monitor(self, **data):
        health_monitor.HealthMonitor(data).delete(self.session)

    def find_health_monitor(self, name_or_id):
        return health_monitor.HealthMonitor.find(self.session, name_or_id)

    def get_health_monitor(self, **data):
        return health_monitor.HealthMonitor(data).get(self.session)

    def list_health_monitors(self):
        return health_monitor.HealthMonitor.list(self.session)

    def update_health_monitor(self, **data):
        return health_monitor.HealthMonitor(data).update(self.session)

    def create_listener(self, **data):
        return listener.Listener(data).create(self.session)

    def delete_listener(self, **data):
        listener.Listener(data).delete(self.session)

    def find_listener(self, name_or_id):
        return listener.Listener.find(self.session, name_or_id)

    def get_listener(self, **data):
        return listener.Listener(data).get(self.session)

    def list_listeners(self):
        return listener.Listener.list(self.session)

    def update_listener(self, **data):
        return listener.Listener(data).update(self.session)

    def create_load_balancer(self, **data):
        return load_balancer.LoadBalancer(data).create(self.session)

    def delete_load_balancer(self, **data):
        load_balancer.LoadBalancer(data).delete(self.session)

    def find_load_balancer(self, name_or_id):
        return load_balancer.LoadBalancer.find(self.session, name_or_id)

    def get_load_balancer(self, **data):
        return load_balancer.LoadBalancer(data).get(self.session)

    def list_load_balancers(self):
        return load_balancer.LoadBalancer.list(self.session)

    def update_load_balancer(self, **data):
        return load_balancer.LoadBalancer(data).update(self.session)

    def create_metering_label(self, **data):
        return metering_label.MeteringLabel(data).create(self.session)

    def delete_metering_label(self, **data):
        metering_label.MeteringLabel(data).delete(self.session)

    def find_metering_label(self, name_or_id):
        return metering_label.MeteringLabel.find(self.session, name_or_id)

    def get_metering_label(self, **data):
        return metering_label.MeteringLabel(data).get(self.session)

    def list_metering_labels(self):
        return metering_label.MeteringLabel.list(self.session)

    def update_metering_label(self, **data):
        return metering_label.MeteringLabel(data).update(self.session)

    def create_metering_label_rule(self, **data):
        return metering_label_rule.MeteringLabelRule(data).create(self.session)

    def delete_metering_label_rule(self, **data):
        metering_label_rule.MeteringLabelRule(data).delete(self.session)

    def find_metering_label_rule(self, name_or_id):
        return metering_label_rule.MeteringLabelRule.find(self.session,
                                                          name_or_id)

    def get_metering_label_rule(self, **data):
        return metering_label_rule.MeteringLabelRule(data).get(self.session)

    def list_metering_label_rules(self):
        return metering_label_rule.MeteringLabelRule.list(self.session)

    def update_metering_label_rule(self, **data):
        return metering_label_rule.MeteringLabelRule(data).update(self.session)

    def create_network(self, **data):
        return network.Network(data).create(self.session)

    def delete_network(self, **data):
        network.Network(data).delete(self.session)

    def find_network(self, name_or_id):
        return network.Network.find(self.session, name_or_id)

    def get_network(self, **data):
        return network.Network(data).get(self.session)

    def list_networks(self, **params):
        return network.Network.list(self.session, **params)

    def update_network(self, **data):
        return network.Network(data).update(self.session)

    def create_pool(self, **data):
        return pool.Pool(data).create(self.session)

    def delete_pool(self, **data):
        pool.Pool(data).delete(self.session)

    def find_pool(self, name_or_id):
        return pool.Pool.find(self.session, name_or_id)

    def get_pool(self, **data):
        return pool.Pool(data).get(self.session)

    def list_pools(self):
        return pool.Pool.list(self.session)

    def update_pool(self, **data):
        return pool.Pool(data).update(self.session)

    def create_pool_member(self, **data):
        return pool_member.PoolMember(data).create(self.session)

    def delete_pool_member(self, **data):
        pool_member.PoolMember(data).delete(self.session)

    def find_pool_member(self, name_or_id):
        return pool_member.PoolMember.find(self.session, name_or_id)

    def get_pool_member(self, **data):
        return pool_member.PoolMember(data).get(self.session)

    def list_pool_members(self):
        return pool_member.PoolMember.list(self.session)

    def update_pool_member(self, **data):
        return pool_member.PoolMember(data).update(self.session)

    def create_port(self, **data):
        return port.Port(data).create(self.session)

    def delete_port(self, **data):
        return port.Port(data).delete(self.session)

    def find_port(self, name_or_id):
        return port.Port.find(self.session, name_or_id)

    def get_port(self, **data):
        return port.Port(data).get(self.session)

    def list_ports(self, **params):
        return port.Port.list(self.session, **params)

    def update_port(self, **data):
        return port.Port(data).update(self.session)

    def add_ip_to_port(self, port, ip):
        ip['port_id'] = port.id
        return ip.update(self.session)

    def remove_ip_from_port(self, ip):
        ip['port_id'] = None
        return ip.update(self.session)

    def get_subnet_ports(self, subnet_id):
        result = []
        ports = self.list_ports()
        for puerta in ports:
            for fixed_ip in puerta.fixed_ips:
                if fixed_ip['subnet_id'] == subnet_id:
                    result.append(puerta)
        return result

    def list_quotas(self):
        return quota.Quota.list(self.session)

    def create_router(self, **data):
        return router.Router(data).create(self.session)

    def delete_router(self, **data):
        return router.Router(**data).delete(self.session)

    def find_router(self, name_or_id):
        return router.Router.find(self.session, name_or_id)

    def get_router(self, **data):
        return router.Router(**data).get(self.session)

    def list_routers(self, **params):
        return router.Router.list(self.session, **params)

    def update_router(self, **data):
        return router.Router(**data).update(self.session)

    def router_add_interface(self, router, subnet_id):
        router.add_interface(self.session, subnet_id)

    def router_remove_interface(self, router, subnet_id):
        router.remove_interface(self.session, subnet_id)

    def create_security_group(self, **data):
        return security_group.SecurityGroup(data).create(self.session)

    def delete_security_group(self, **data):
        return security_group.SecurityGroup(**data).delete(self.session)

    def find_security_group(self, name_or_id):
        return security_group.SecurityGroup.find(self.session, name_or_id)

    def get_security_group(self, **data):
        return security_group.SecurityGroup(**data).get(self.session)

    def list_security_groups(self, **params):
        return security_group.SecurityGroup.list(self.session, **params)

    def update_security_group(self, **data):
        return security_group.SecurityGroup(**data).update(self.session)

    def create_security_group_rule(self, **data):
        obj = security_group_rule.SecurityGroupRule(data)
        return obj.create(self.session)

    def delete_security_group_rule(self, **data):
        obj = security_group_rule.SecurityGroupRule(**data)
        return obj.delete(self.session)

    def find_security_group_rule(self, name_or_id):
        return security_group_rule.SecurityGroupRule.find(self.session,
                                                          name_or_id)

    def get_security_group_rule(self, **data):
        obj = security_group_rule.SecurityGroupRule(**data)
        return obj.get(self.session)

    def list_security_group_rules(self, **params):
        return security_group_rule.SecurityGroupRule.list(self.session,
                                                          **params)

    def update_security_group_rule(self, **data):
        obj = security_group_rule.SecurityGroupRule(**data)
        return obj.update(self.session)

    def create_subnet(self, **data):
        return subnet.Subnet(data).create(self.session)

    def delete_subnet(self, **data):
        return subnet.Subnet(**data).delete(self.session)

    def find_subnet(self, name_or_id):
        return subnet.Subnet.find(self.session, name_or_id)

    def get_subnet(self, **data):
        return subnet.Subnet(**data).get(self.session)

    def list_subnets(self, **params):
        return subnet.Subnet.list(self.session, **params)

    def update_subnet(self, **data):
        return subnet.Subnet(**data).update(self.session)
