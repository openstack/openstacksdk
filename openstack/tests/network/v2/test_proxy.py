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

from openstack.network.v2 import _proxy
from openstack.tests import test_proxy_base


class TestNetworkProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestNetworkProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_extension(self):
        self.verify_find('openstack.network.v2.extension.Extension.find',
                         self.proxy.find_extension)
        self.verify_list('openstack.network.v2.extension.Extension.list',
                         self.proxy.list_extension)

    def test_ip(self):
        self.verify_create('openstack.network.v2.floatingip.FloatingIP.create',
                           self.proxy.create_ip)
        self.verify_delete('openstack.network.v2.floatingip.FloatingIP.delete',
                           self.proxy.delete_ip)
        self.verify_find('openstack.network.v2.floatingip.FloatingIP.find',
                         self.proxy.find_ip)
        self.verify_get('openstack.network.v2.floatingip.FloatingIP.get',
                        self.proxy.get_ip)
        self.verify_list('openstack.network.v2.floatingip.FloatingIP.list',
                         self.proxy.list_ips)
        self.verify_update('openstack.network.v2.floatingip.FloatingIP.update',
                           self.proxy.update_ip)

    def test_health_monitor(self):
        self.verify_create(
            'openstack.network.v2.health_monitor.HealthMonitor.create',
            self.proxy.create_health_monitor
        )
        self.verify_delete(
            'openstack.network.v2.health_monitor.HealthMonitor.delete',
            self.proxy.delete_health_monitor
        )
        self.verify_find(
            'openstack.network.v2.health_monitor.HealthMonitor.find',
            self.proxy.find_health_monitor
        )
        self.verify_get(
            'openstack.network.v2.health_monitor.HealthMonitor.get',
            self.proxy.get_health_monitor
        )
        self.verify_list(
            'openstack.network.v2.health_monitor.HealthMonitor.list',
            self.proxy.list_health_monitor
        )
        self.verify_update(
            'openstack.network.v2.health_monitor.HealthMonitor.update',
            self.proxy.update_health_monitor
        )

    def test_listener(self):
        self.verify_create('openstack.network.v2.listener.Listener.create',
                           self.proxy.create_listener)
        self.verify_delete('openstack.network.v2.listener.Listener.delete',
                           self.proxy.delete_listener)
        self.verify_find('openstack.network.v2.listener.Listener.find',
                         self.proxy.find_listener)
        self.verify_get('openstack.network.v2.listener.Listener.get',
                        self.proxy.get_listener)
        self.verify_list('openstack.network.v2.listener.Listener.list',
                         self.proxy.list_listener)
        self.verify_update('openstack.network.v2.listener.Listener.update',
                           self.proxy.update_listener)

    def test_load_balancer(self):
        self.verify_create(
            'openstack.network.v2.load_balancer.LoadBalancer.create',
            self.proxy.create_load_balancer
        )
        self.verify_delete(
            'openstack.network.v2.load_balancer.LoadBalancer.delete',
            self.proxy.delete_load_balancer
        )
        self.verify_find(
            'openstack.network.v2.load_balancer.LoadBalancer.find',
            self.proxy.find_load_balancer
        )
        self.verify_get('openstack.network.v2.load_balancer.LoadBalancer.get',
                        self.proxy.get_load_balancer)
        self.verify_list(
            'openstack.network.v2.load_balancer.LoadBalancer.list',
            self.proxy.list_load_balancer
        )
        self.verify_update(
            'openstack.network.v2.load_balancer.LoadBalancer.update',
            self.proxy.update_load_balancer
        )

    def test_metering_label(self):
        self.verify_create(
            'openstack.network.v2.metering_label.MeteringLabel.create',
            self.proxy.create_metering_label
        )
        self.verify_delete(
            'openstack.network.v2.metering_label.MeteringLabel.delete',
            self.proxy.delete_metering_label
        )
        self.verify_find(
            'openstack.network.v2.metering_label.MeteringLabel.find',
            self.proxy.find_metering_label
        )
        self.verify_get(
            'openstack.network.v2.metering_label.MeteringLabel.get',
            self.proxy.get_metering_label
        )
        self.verify_list(
            'openstack.network.v2.metering_label.MeteringLabel.list',
            self.proxy.list_metering_label
        )
        self.verify_update(
            'openstack.network.v2.metering_label.MeteringLabel.update',
            self.proxy.update_metering_label
        )

    def test_metering_label_rule(self):
        self.verify_create(
            ('openstack.network.v2.' +
             'metering_label_rule.MeteringLabelRule.create'),
            self.proxy.create_metering_label_rule
        )
        self.verify_delete(
            ('openstack.network.v2.' +
             'metering_label_rule.MeteringLabelRule.delete'),
            self.proxy.delete_metering_label_rule
        )
        self.verify_find(
            'openstack.network.v2.metering_label_rule.MeteringLabelRule.find',
            self.proxy.find_metering_label_rule
        )
        self.verify_get(
            'openstack.network.v2.metering_label_rule.MeteringLabelRule.get',
            self.proxy.get_metering_label_rule
        )
        self.verify_list(
            'openstack.network.v2.metering_label_rule.MeteringLabelRule.list',
            self.proxy.list_metering_label_rule
        )
        self.verify_update(
            ('openstack.network.v2.' +
             'metering_label_rule.MeteringLabelRule.update'),
            self.proxy.update_metering_label_rule
        )

    def test_network(self):
        self.verify_create('openstack.network.v2.network.Network.create',
                           self.proxy.create_network)
        self.verify_delete('openstack.network.v2.network.Network.delete',
                           self.proxy.delete_network)
        self.verify_find('openstack.network.v2.network.Network.find',
                         self.proxy.find_network)
        self.verify_get('openstack.network.v2.network.Network.get',
                        self.proxy.get_network)
        self.verify_list('openstack.network.v2.network.Network.list',
                         self.proxy.list_networks)
        self.verify_update('openstack.network.v2.network.Network.update',
                           self.proxy.update_network)

    def test_pool(self):
        self.verify_create('openstack.network.v2.pool.Pool.create',
                           self.proxy.create_pool)
        self.verify_delete('openstack.network.v2.pool.Pool.delete',
                           self.proxy.delete_pool)
        self.verify_find('openstack.network.v2.pool.Pool.find',
                         self.proxy.find_pool)
        self.verify_get('openstack.network.v2.pool.Pool.get',
                        self.proxy.get_pool)
        self.verify_list('openstack.network.v2.pool.Pool.list',
                         self.proxy.list_pool)
        self.verify_update('openstack.network.v2.pool.Pool.update',
                           self.proxy.update_pool)

    def test_pool_member(self):
        self.verify_create(
            'openstack.network.v2.pool_member.PoolMember.create',
            self.proxy.create_pool_member
        )
        self.verify_delete(
            'openstack.network.v2.pool_member.PoolMember.delete',
            self.proxy.delete_pool_member
        )
        self.verify_find('openstack.network.v2.pool_member.PoolMember.find',
                         self.proxy.find_pool_member)
        self.verify_get('openstack.network.v2.pool_member.PoolMember.get',
                        self.proxy.get_pool_member)
        self.verify_list('openstack.network.v2.pool_member.PoolMember.list',
                         self.proxy.list_pool_member)
        self.verify_update(
            'openstack.network.v2.pool_member.PoolMember.update',
            self.proxy.update_pool_member
        )

    def test_port(self):
        self.verify_create('openstack.network.v2.port.Port.create',
                           self.proxy.create_port)
        self.verify_delete('openstack.network.v2.port.Port.delete',
                           self.proxy.delete_port)
        self.verify_find('openstack.network.v2.port.Port.find',
                         self.proxy.find_port)
        self.verify_get('openstack.network.v2.port.Port.get',
                        self.proxy.get_port)
        self.verify_list('openstack.network.v2.port.Port.list',
                         self.proxy.list_ports)
        self.verify_update('openstack.network.v2.port.Port.update',
                           self.proxy.update_port)

    def test_quota(self):
        self.verify_list('openstack.network.v2.quota.Quota.list',
                         self.proxy.list_quota)

    def test_router(self):
        self.verify_create('openstack.network.v2.router.Router.create',
                           self.proxy.create_router)
        self.verify_delete('openstack.network.v2.router.Router.delete',
                           self.proxy.delete_router)
        self.verify_find('openstack.network.v2.router.Router.find',
                         self.proxy.find_router)
        self.verify_get('openstack.network.v2.router.Router.get',
                        self.proxy.get_router)
        self.verify_list('openstack.network.v2.router.Router.list',
                         self.proxy.list_routers)
        self.verify_update('openstack.network.v2.router.Router.update',
                           self.proxy.update_router)

    def test_security_group(self):
        self.verify_create(
            'openstack.network.v2.security_group.SecurityGroup.create',
            self.proxy.create_security_group)
        self.verify_delete(
            'openstack.network.v2.security_group.SecurityGroup.delete',
            self.proxy.delete_security_group)
        self.verify_find(
            'openstack.network.v2.security_group.SecurityGroup.find',
            self.proxy.find_security_group)
        self.verify_get(
            'openstack.network.v2.security_group.SecurityGroup.get',
            self.proxy.get_security_group)
        self.verify_list(
            'openstack.network.v2.security_group.SecurityGroup.list',
            self.proxy.list_security_groups)
        self.verify_update(
            'openstack.network.v2.security_group.SecurityGroup.update',
            self.proxy.update_security_group)

    def test_security_group_rule(self):
        self.verify_create(
            ('openstack.network.v2.' +
             'security_group_rule.SecurityGroupRule.create'),
            self.proxy.create_security_group_rule)
        self.verify_delete(
            ('openstack.network.v2.' +
             'security_group_rule.SecurityGroupRule.delete'),
            self.proxy.delete_security_group_rule)
        self.verify_find(
            ('openstack.network.v2.' +
             'security_group_rule.SecurityGroupRule.find'),
            self.proxy.find_security_group_rule)
        self.verify_get(
            ('openstack.network.v2.' +
             'security_group_rule.SecurityGroupRule.get'),
            self.proxy.get_security_group_rule)
        self.verify_list(
            ('openstack.network.v2.' +
             'security_group_rule.SecurityGroupRule.list'),
            self.proxy.list_security_group_rules)
        self.verify_update(
            ('openstack.network.v2.' +
             'security_group_rule.SecurityGroupRule.update'),
            self.proxy.update_security_group_rule)

    def test_subnet(self):
        self.verify_create('openstack.network.v2.subnet.Subnet.create',
                           self.proxy.create_subnet)
        self.verify_delete('openstack.network.v2.subnet.Subnet.delete',
                           self.proxy.delete_subnet)
        self.verify_find('openstack.network.v2.subnet.Subnet.find',
                         self.proxy.find_subnet)
        self.verify_get('openstack.network.v2.subnet.Subnet.get',
                        self.proxy.get_subnet)
        self.verify_list('openstack.network.v2.subnet.Subnet.list',
                         self.proxy.list_subnets)
        self.verify_update('openstack.network.v2.subnet.Subnet.update',
                           self.proxy.update_subnet)
