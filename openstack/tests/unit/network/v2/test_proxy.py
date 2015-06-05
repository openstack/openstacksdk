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

import mock

from openstack.network.v2 import _proxy
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
from openstack.network.v2 import vpn_service
from openstack.tests.unit import test_proxy_base


class TestNetworkProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestNetworkProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_extension_find(self):
        self.verify_find('openstack.network.v2.extension.Extension.find',
                         self.proxy.find_extension)

    def test_extensions(self):
        self.verify_list2(self.proxy.extensions,
                          expected_args=[extension.Extension],
                          expected_kwargs={})

    def test_floating_ip_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_ip,
                            method_kwargs=kwargs,
                            expected_args=[floating_ip.FloatingIP],
                            expected_kwargs=kwargs)

    def test_floating_ip_delete(self):
        self.verify_delete2(floating_ip.FloatingIP, self.proxy.delete_ip,
                            False)

    def test_floating_ip_delete_ignore(self):
        self.verify_delete2(floating_ip.FloatingIP, self.proxy.delete_ip,
                            True)

    def test_floating_ip_find(self):
        self.verify_find('openstack.network.v2.floating_ip.FloatingIP.find',
                         self.proxy.find_ip)

    def test_floating_ip_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_ip,
                         method_args=["resource_or_id"],
                         expected_args=[floating_ip.FloatingIP,
                                        "resource_or_id"])

    def test_ips(self):
        self.verify_list2(self.proxy.ips,
                          expected_args=[floating_ip.FloatingIP],
                          expected_kwargs={})

    def test_floating_ip_update(self):
        self.verify_update(self.proxy.update_ip, floating_ip.FloatingIP)

    def test_health_monitor_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_health_monitor,
                            method_kwargs=kwargs,
                            expected_args=[health_monitor.HealthMonitor],
                            expected_kwargs=kwargs)

    def test_health_monitor_delete(self):
        self.verify_delete2(health_monitor.HealthMonitor,
                            self.proxy.delete_health_monitor, False)

    def test_health_monitor_delete_ignore(self):
        self.verify_delete2(health_monitor.HealthMonitor,
                            self.proxy.delete_health_monitor, True)

    def test_health_monitor_find(self):
        self.verify_find(
            'openstack.network.v2.health_monitor.HealthMonitor.find',
            self.proxy.find_health_monitor)

    def test_health_monitor_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_health_monitor,
                         method_args=["resource_or_id"],
                         expected_args=[health_monitor.HealthMonitor,
                                        "resource_or_id"])

    def test_health_monitors(self):
        self.verify_list2(self.proxy.health_monitors,
                          expected_args=[health_monitor.HealthMonitor],
                          expected_kwargs={})

    def test_health_monitor_update(self):
        self.verify_update(self.proxy.update_health_monitor,
                           health_monitor.HealthMonitor)

    def test_listener_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_listener,
                            method_kwargs=kwargs,
                            expected_args=[listener.Listener],
                            expected_kwargs=kwargs)

    def test_listener_delete(self):
        self.verify_delete2(listener.Listener,
                            self.proxy.delete_listener, False)

    def test_listener_delete_ignore(self):
        self.verify_delete2(listener.Listener,
                            self.proxy.delete_listener, True)

    def test_listener_find(self):
        self.verify_find('openstack.network.v2.listener.Listener.find',
                         self.proxy.find_listener)

    def test_listener_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_listener,
                         method_args=["resource_or_id"],
                         expected_args=[listener.Listener, "resource_or_id"])

    def test_listeners(self):
        self.verify_list2(self.proxy.listeners,
                          expected_args=[listener.Listener],
                          expected_kwargs={})

    def test_listener_update(self):
        self.verify_update(self.proxy.update_listener, listener.Listener)

    def test_load_balancer_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_load_balancer,
                            method_kwargs=kwargs,
                            expected_args=[load_balancer.LoadBalancer],
                            expected_kwargs=kwargs)

    def test_load_balancer_delete(self):
        self.verify_delete2(load_balancer.LoadBalancer,
                            self.proxy.delete_load_balancer, False)

    def test_load_balancer_delete_ignore(self):
        self.verify_delete2(load_balancer.LoadBalancer,
                            self.proxy.delete_load_balancer, True)

    def test_load_balancer_find(self):
        self.verify_find(
            'openstack.network.v2.load_balancer.LoadBalancer.find',
            self.proxy.find_load_balancer)

    def test_load_balancer_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_load_balancer,
                         method_args=["resource_or_id"],
                         expected_args=[load_balancer.LoadBalancer,
                                        "resource_or_id"])

    def test_load_balancers(self):
        self.verify_list2(self.proxy.load_balancers,
                          expected_args=[load_balancer.LoadBalancer],
                          expected_kwargs={})

    def test_load_balancer_update(self):
        self.verify_update(self.proxy.update_load_balancer,
                           load_balancer.LoadBalancer)

    def test_metering_label_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_metering_label,
                            method_kwargs=kwargs,
                            expected_args=[metering_label.MeteringLabel],
                            expected_kwargs=kwargs)

    def test_metering_label_delete(self):
        self.verify_delete2(metering_label.MeteringLabel,
                            self.proxy.delete_metering_label, False)

    def test_metering_label_delete_ignore(self):
        self.verify_delete2(metering_label.MeteringLabel,
                            self.proxy.delete_metering_label, True)

    def test_metering_label_find(self):
        self.verify_find(
            'openstack.network.v2.metering_label.MeteringLabel.find',
            self.proxy.find_metering_label)

    def test_metering_label_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_metering_label,
                         method_args=["resource_or_id"],
                         expected_args=[metering_label.MeteringLabel,
                                        "resource_or_id"])

    def test_metering_labels(self):
        self.verify_list2(self.proxy.metering_labels,
                          expected_args=[metering_label.MeteringLabel],
                          expected_kwargs={})

    def test_metering_label_update(self):
        self.verify_update(self.proxy.update_metering_label,
                           metering_label.MeteringLabel)

    def test_metering_label_rule_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_metering_label_rule,
                            method_kwargs=kwargs,
                            expected_args=[
                                metering_label_rule.MeteringLabelRule],
                            expected_kwargs=kwargs)

    def test_metering_label_rule_delete(self):
        self.verify_delete2(metering_label_rule.MeteringLabelRule,
                            self.proxy.delete_metering_label_rule, False)

    def test_metering_label_rule_delete_ignore(self):
        self.verify_delete2(metering_label_rule.MeteringLabelRule,
                            self.proxy.delete_metering_label_rule, True)

    def test_metering_label_rule_find(self):
        self.verify_find(
            'openstack.network.v2.metering_label_rule.MeteringLabelRule.find',
            self.proxy.find_metering_label_rule)

    def test_metering_label_rule_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_metering_label_rule,
                         method_args=["resource_or_id"],
                         expected_args=[metering_label_rule.MeteringLabelRule,
                                        "resource_or_id"])

    def test_metering_label_rules(self):
        self.verify_list2(
            self.proxy.metering_label_rules,
            expected_args=[metering_label_rule.MeteringLabelRule],
            expected_kwargs={})

    def test_metering_label_rule_update(self):
        self.verify_update(self.proxy.update_metering_label_rule,
                           metering_label_rule.MeteringLabelRule)

    def test_network_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_network,
                            method_kwargs=kwargs,
                            expected_args=[network.Network],
                            expected_kwargs=kwargs)

    def test_network_delete(self):
        self.verify_delete2(network.Network, self.proxy.delete_network, False)

    def test_network_delete_ignore(self):
        self.verify_delete2(network.Network, self.proxy.delete_network, True)

    def test_network_find(self):
        self.verify_find('openstack.network.v2.network.Network.find',
                         self.proxy.find_network)

    def test_network_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_network,
                         method_args=["resource_or_id"],
                         expected_args=[network.Network, "resource_or_id"])

    def test_networks(self):
        self.verify_list2(self.proxy.networks,
                          expected_args=[network.Network],
                          expected_kwargs={})

    def test_network_update(self):
        self.verify_update(self.proxy.update_network, network.Network)

    def test_pool_member_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_pool_member,
                            method_kwargs=kwargs,
                            expected_args=[pool_member.PoolMember],
                            expected_kwargs=kwargs)

    def test_pool_member_delete(self):
        self.verify_delete2(pool_member.PoolMember,
                            self.proxy.delete_pool_member, False)

    def test_pool_member_delete_ignore(self):
        self.verify_delete2(pool_member.PoolMember,
                            self.proxy.delete_pool_member, True)

    def test_pool_member_find(self):
        self.verify_find('openstack.network.v2.pool_member.PoolMember.find',
                         self.proxy.find_pool_member)

    def test_pool_member_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_pool_member,
                         method_args=["resource_or_id"],
                         expected_args=[pool_member.PoolMember,
                                        "resource_or_id"])

    def test_pool_members(self):
        self.verify_list2(self.proxy.pool_members,
                          expected_args=[pool_member.PoolMember],
                          expected_kwargs={})

    def test_pool_member_update(self):
        self.verify_update(self.proxy.update_pool_member,
                           pool_member.PoolMember)

    def test_pool_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_pool,
                            method_kwargs=kwargs,
                            expected_args=[pool.Pool],
                            expected_kwargs=kwargs)

    def test_pool_delete(self):
        self.verify_delete2(pool.Pool, self.proxy.delete_pool, False)

    def test_pool_delete_ignore(self):
        self.verify_delete2(pool.Pool, self.proxy.delete_pool, True)

    def test_pool_find(self):
        self.verify_find('openstack.network.v2.pool.Pool.find',
                         self.proxy.find_pool)

    def test_pool_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_pool,
                         method_args=["resource_or_id"],
                         expected_args=[pool.Pool, "resource_or_id"])

    def test_pools(self):
        self.verify_list2(self.proxy.pools,
                          expected_args=[pool.Pool],
                          expected_kwargs={})

    def test_pool_update(self):
        self.verify_update(self.proxy.update_pool, pool.Pool)

    def test_port_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_port,
                            method_kwargs=kwargs,
                            expected_args=[port.Port],
                            expected_kwargs=kwargs)

    def test_port_delete(self):
        self.verify_delete2(port.Port, self.proxy.delete_port, False)

    def test_port_delete_ignore(self):
        self.verify_delete2(port.Port, self.proxy.delete_port, True)

    def test_port_find(self):
        self.verify_find('openstack.network.v2.port.Port.find',
                         self.proxy.find_port)

    def test_port_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_port,
                         method_args=["resource_or_id"],
                         expected_args=[port.Port, "resource_or_id"])

    def test_ports(self):
        self.verify_list2(self.proxy.ports,
                          expected_args=[port.Port],
                          expected_kwargs={})

    def test_port_update(self):
        self.verify_update(self.proxy.update_port, port.Port)

    def test_quotas(self):
        self.verify_list2(self.proxy.quotas,
                          expected_args=[quota.Quota],
                          expected_kwargs={})

    def test_router_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_router,
                            method_kwargs=kwargs,
                            expected_args=[router.Router],
                            expected_kwargs=kwargs)

    def test_router_delete(self):
        self.verify_delete2(router.Router, self.proxy.delete_router, False)

    def test_router_delete_ignore(self):
        self.verify_delete2(router.Router, self.proxy.delete_router, True)

    def test_router_find(self):
        self.verify_find('openstack.network.v2.router.Router.find',
                         self.proxy.find_router)

    def test_router_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_router,
                         method_args=["resource_or_id"],
                         expected_args=[router.Router, "resource_or_id"])

    def test_routers(self):
        self.verify_list2(self.proxy.routers,
                          expected_args=[router.Router],
                          expected_kwargs={})

    def test_router_update(self):
        self.verify_update(self.proxy.update_router, router.Router)

    def test_security_group_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_security_group,
                            method_kwargs=kwargs,
                            expected_args=[security_group.SecurityGroup],
                            expected_kwargs=kwargs)

    def test_security_group_delete(self):
        self.verify_delete2(security_group.SecurityGroup,
                            self.proxy.delete_security_group, False)

    def test_security_group_delete_ignore(self):
        self.verify_delete2(security_group.SecurityGroup,
                            self.proxy.delete_security_group, True)

    def test_security_group_find(self):
        self.verify_find(
            'openstack.network.v2.security_group.SecurityGroup.find',
            self.proxy.find_security_group)

    def test_security_group_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_security_group,
                         method_args=["resource_or_id"],
                         expected_args=[security_group.SecurityGroup,
                                        "resource_or_id"])

    def test_security_groups(self):
        self.verify_list2(self.proxy.security_groups,
                          expected_args=[security_group.SecurityGroup],
                          expected_kwargs={})

    def test_security_group_update(self):
        self.verify_update(self.proxy.update_security_group,
                           security_group.SecurityGroup)

    def test_security_group_open_port(self):
        mock_class = 'openstack.network.v2._proxy.Proxy'
        mock_method = mock_class + '.create_security_group_rule'
        expected_result = 'result'
        sgid = 1
        port = 2
        with mock.patch(mock_method) as mocked:
            mocked.return_value = expected_result
            actual = self.proxy.security_group_open_port(sgid, port)
            self.assertEqual(expected_result, actual)
            expected_args = {
                'direction': 'ingress',
                'protocol': 'tcp',
                'remote_ip_prefix': '0.0.0.0/0',
                'port_range_max': port,
                'security_group_id': sgid,
                'port_range_min': port,
                'ethertype': 'IPv4',
            }
            mocked.assert_called_with(**expected_args)

    def test_security_group_allow_ping(self):
        mock_class = 'openstack.network.v2._proxy.Proxy'
        mock_method = mock_class + '.create_security_group_rule'
        expected_result = 'result'
        sgid = 1
        with mock.patch(mock_method) as mocked:
            mocked.return_value = expected_result
            actual = self.proxy.security_group_allow_ping(sgid)
            self.assertEqual(expected_result, actual)
            expected_args = {
                'direction': 'ingress',
                'protocol': 'icmp',
                'remote_ip_prefix': '0.0.0.0/0',
                'port_range_max': None,
                'security_group_id': sgid,
                'port_range_min': None,
                'ethertype': 'IPv4',
            }
            mocked.assert_called_with(**expected_args)

    def test_security_group_rule_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_security_group_rule,
                            method_kwargs=kwargs,
                            expected_args=[
                                security_group_rule.SecurityGroupRule],
                            expected_kwargs=kwargs)

    def test_security_group_rule_delete(self):
        self.verify_delete2(security_group_rule.SecurityGroupRule,
                            self.proxy.delete_security_group_rule, False)

    def test_security_group_rule_delete_ignore(self):
        self.verify_delete2(security_group_rule.SecurityGroupRule,
                            self.proxy.delete_security_group_rule, True)

    def test_security_group_rule_find(self):
        self.verify_find(
            'openstack.network.v2.security_group_rule.SecurityGroupRule.find',
            self.proxy.find_security_group_rule)

    def test_security_group_rule_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_security_group_rule,
                         method_args=["resource_or_id"],
                         expected_args=[security_group_rule.SecurityGroupRule,
                                        "resource_or_id"])

    def test_security_group_rules(self):
        self.verify_list2(
            self.proxy.security_group_rules,
            expected_args=[security_group_rule.SecurityGroupRule],
            expected_kwargs={})

    def test_security_group_rule_update(self):
        self.verify_update(self.proxy.update_security_group_rule,
                           security_group_rule.SecurityGroupRule)

    def test_subnet_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_subnet,
                            method_kwargs=kwargs,
                            expected_args=[subnet.Subnet],
                            expected_kwargs=kwargs)

    def test_subnet_delete(self):
        self.verify_delete2(subnet.Subnet, self.proxy.delete_subnet, False)

    def test_subnet_delete_ignore(self):
        self.verify_delete2(subnet.Subnet, self.proxy.delete_subnet, True)

    def test_subnet_find(self):
        self.verify_find('openstack.network.v2.subnet.Subnet.find',
                         self.proxy.find_subnet)

    def test_subnet_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_subnet,
                         method_args=["resource_or_id"],
                         expected_args=[subnet.Subnet, "resource_or_id"])

    def test_subnets(self):
        self.verify_list2(self.proxy.subnets,
                          expected_args=[subnet.Subnet],
                          expected_kwargs={})

    def test_subnet_update(self):
        self.verify_update(self.proxy.update_subnet, subnet.Subnet)

    def test_vpn_service_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_vpn_service,
                            method_kwargs=kwargs,
                            expected_args=[vpn_service.VPNService],
                            expected_kwargs=kwargs)

    def test_vpn_service_delete(self):
        self.verify_delete2(vpn_service.VPNService,
                            self.proxy.delete_vpn_service, False)

    def test_vpn_service_delete_ignore(self):
        self.verify_delete2(vpn_service.VPNService,
                            self.proxy.delete_vpn_service, True)

    def test_vpn_service_find(self):
        self.verify_find('openstack.network.v2.vpn_service.VPNService.find',
                         self.proxy.find_vpn_service)

    def test_vpn_service_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_vpn_service,
                         method_args=["resource_or_id"],
                         expected_args=[vpn_service.VPNService,
                                        "resource_or_id"])

    def test_vpn_services(self):
        self.verify_list2(self.proxy.vpn_services,
                          expected_args=[vpn_service.VPNService],
                          expected_kwargs={})

    def test_vpn_service_update(self):
        self.verify_update(self.proxy.update_vpn_service,
                           vpn_service.VPNService)
