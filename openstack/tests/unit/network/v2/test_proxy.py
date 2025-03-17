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

from unittest import mock
import uuid

from openstack import exceptions
from openstack.network.v2 import _proxy
from openstack.network.v2 import address_group
from openstack.network.v2 import address_scope
from openstack.network.v2 import agent
from openstack.network.v2 import auto_allocated_topology
from openstack.network.v2 import availability_zone
from openstack.network.v2 import bgp_peer
from openstack.network.v2 import bgp_speaker
from openstack.network.v2 import bgpvpn
from openstack.network.v2 import bgpvpn_network_association
from openstack.network.v2 import bgpvpn_port_association
from openstack.network.v2 import bgpvpn_router_association
from openstack.network.v2 import extension
from openstack.network.v2 import firewall_group
from openstack.network.v2 import firewall_policy
from openstack.network.v2 import firewall_rule
from openstack.network.v2 import flavor
from openstack.network.v2 import floating_ip
from openstack.network.v2 import health_monitor
from openstack.network.v2 import l3_conntrack_helper
from openstack.network.v2 import listener
from openstack.network.v2 import load_balancer
from openstack.network.v2 import local_ip
from openstack.network.v2 import local_ip_association
from openstack.network.v2 import metering_label
from openstack.network.v2 import metering_label_rule
from openstack.network.v2 import ndp_proxy
from openstack.network.v2 import network
from openstack.network.v2 import network_ip_availability
from openstack.network.v2 import network_segment_range
from openstack.network.v2 import pool
from openstack.network.v2 import pool_member
from openstack.network.v2 import port
from openstack.network.v2 import port_binding
from openstack.network.v2 import port_forwarding
from openstack.network.v2 import qos_bandwidth_limit_rule
from openstack.network.v2 import qos_dscp_marking_rule
from openstack.network.v2 import qos_minimum_bandwidth_rule
from openstack.network.v2 import qos_minimum_packet_rate_rule
from openstack.network.v2 import qos_packet_rate_limit_rule
from openstack.network.v2 import qos_policy
from openstack.network.v2 import qos_rule_type
from openstack.network.v2 import quota
from openstack.network.v2 import rbac_policy
from openstack.network.v2 import router
from openstack.network.v2 import security_group
from openstack.network.v2 import security_group_rule
from openstack.network.v2 import segment
from openstack.network.v2 import service_profile
from openstack.network.v2 import service_provider
from openstack.network.v2 import subnet
from openstack.network.v2 import subnet_pool
from openstack.network.v2 import tap_mirror
from openstack.network.v2 import vpn_endpoint_group
from openstack.network.v2 import vpn_ike_policy
from openstack.network.v2 import vpn_ipsec_policy
from openstack.network.v2 import vpn_ipsec_site_connection
from openstack.network.v2 import vpn_service
from openstack import proxy as proxy_base
from openstack.tests.unit import test_proxy_base


QOS_POLICY_ID = 'qos-policy-id-' + uuid.uuid4().hex
QOS_RULE_ID = 'qos-rule-id-' + uuid.uuid4().hex
NETWORK_ID = 'network-id-' + uuid.uuid4().hex
AGENT_ID = 'agent-id-' + uuid.uuid4().hex
ROUTER_ID = 'router-id-' + uuid.uuid4().hex
FIP_ID = 'fip-id-' + uuid.uuid4().hex
CT_HELPER_ID = 'ct-helper-id-' + uuid.uuid4().hex
LOCAL_IP_ID = 'lip-id-' + uuid.uuid4().hex
BGPVPN_ID = 'bgpvpn-id-' + uuid.uuid4().hex
PORT_ID = 'port-id-' + uuid.uuid4().hex


class TestNetworkProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)

    def verify_update(
        self,
        test_method,
        resource_type,
        base_path=None,
        *,
        method_args=None,
        method_kwargs=None,
        expected_args=None,
        expected_kwargs=None,
        expected_result="result",
        mock_method="openstack.network.v2._proxy.Proxy._update",
    ):
        super().verify_update(
            test_method,
            resource_type,
            base_path=base_path,
            method_args=method_args,
            method_kwargs=method_kwargs,
            expected_args=expected_args,
            expected_kwargs=expected_kwargs,
            expected_result=expected_result,
            mock_method=mock_method,
        )

    def verify_delete(
        self,
        test_method,
        resource_type,
        ignore_missing=True,
        *,
        method_args=None,
        method_kwargs=None,
        expected_args=None,
        expected_kwargs=None,
        mock_method="openstack.network.v2._proxy.Proxy._delete",
    ):
        super().verify_delete(
            test_method,
            resource_type,
            ignore_missing=ignore_missing,
            method_args=method_args,
            method_kwargs=method_kwargs,
            expected_args=expected_args,
            expected_kwargs=expected_kwargs,
            mock_method=mock_method,
        )


class TestNetworkAddressGroup(TestNetworkProxy):
    def test_address_group_create_attrs(self):
        self.verify_create(
            self.proxy.create_address_group, address_group.AddressGroup
        )

    def test_address_group_delete(self):
        self.verify_delete(
            self.proxy.delete_address_group, address_group.AddressGroup, False
        )

    def test_address_group_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_address_group, address_group.AddressGroup, True
        )

    def test_address_group_find(self):
        self.verify_find(
            self.proxy.find_address_group, address_group.AddressGroup
        )

    def test_address_group_get(self):
        self.verify_get(
            self.proxy.get_address_group, address_group.AddressGroup
        )

    def test_address_groups(self):
        self.verify_list(self.proxy.address_groups, address_group.AddressGroup)

    def test_address_group_update(self):
        self.verify_update(
            self.proxy.update_address_group, address_group.AddressGroup
        )

    @mock.patch(
        'openstack.network.v2._proxy.Proxy.add_addresses_to_address_group'
    )
    def test_add_addresses_to_address_group(self, add_addresses):
        data = mock.sentinel

        self.proxy.add_addresses_to_address_group(
            address_group.AddressGroup, data
        )

        add_addresses.assert_called_once_with(address_group.AddressGroup, data)

    @mock.patch(
        'openstack.network.v2._proxy.Proxy.remove_addresses_from_address_group'
    )
    def test_remove_addresses_from_address_group(self, remove_addresses):
        data = mock.sentinel

        self.proxy.remove_addresses_from_address_group(
            address_group.AddressGroup, data
        )

        remove_addresses.assert_called_once_with(
            address_group.AddressGroup, data
        )


class TestNetworkAddressScope(TestNetworkProxy):
    def test_address_scope_create_attrs(self):
        self.verify_create(
            self.proxy.create_address_scope, address_scope.AddressScope
        )

    def test_address_scope_delete(self):
        self.verify_delete(
            self.proxy.delete_address_scope, address_scope.AddressScope, False
        )

    def test_address_scope_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_address_scope, address_scope.AddressScope, True
        )

    def test_address_scope_find(self):
        self.verify_find(
            self.proxy.find_address_scope, address_scope.AddressScope
        )

    def test_address_scope_get(self):
        self.verify_get(
            self.proxy.get_address_scope, address_scope.AddressScope
        )

    def test_address_scopes(self):
        self.verify_list(self.proxy.address_scopes, address_scope.AddressScope)

    def test_address_scope_update(self):
        self.verify_update(
            self.proxy.update_address_scope, address_scope.AddressScope
        )


class TestNetworkAgent(TestNetworkProxy):
    def test_agent_delete(self):
        self.verify_delete(self.proxy.delete_agent, agent.Agent, True)

    def test_agent_get(self):
        self.verify_get(self.proxy.get_agent, agent.Agent)

    def test_agents(self):
        self.verify_list(self.proxy.agents, agent.Agent)

    def test_agent_update(self):
        self.verify_update(self.proxy.update_agent, agent.Agent)


class TestNetworkAvailability(TestNetworkProxy):
    def test_availability_zones(self):
        self.verify_list(
            self.proxy.availability_zones, availability_zone.AvailabilityZone
        )

    def test_dhcp_agent_hosting_networks(self):
        self.verify_list(
            self.proxy.dhcp_agent_hosting_networks,
            network.DHCPAgentHostingNetwork,
            method_kwargs={'agent': AGENT_ID},
            expected_kwargs={'agent_id': AGENT_ID},
        )

    def test_network_hosting_dhcp_agents(self):
        self.verify_list(
            self.proxy.network_hosting_dhcp_agents,
            agent.NetworkHostingDHCPAgent,
            method_kwargs={'network': NETWORK_ID},
            expected_kwargs={'network_id': NETWORK_ID},
        )


class TestNetworkExtension(TestNetworkProxy):
    def test_extension_find(self):
        self.verify_find(self.proxy.find_extension, extension.Extension)

    def test_extensions(self):
        self.verify_list(self.proxy.extensions, extension.Extension)

    def test_floating_ip_create_attrs(self):
        self.verify_create(self.proxy.create_ip, floating_ip.FloatingIP)

    def test_floating_ip_delete(self):
        self.verify_delete(
            self.proxy.delete_ip,
            floating_ip.FloatingIP,
            False,
            expected_kwargs={'if_revision': None},
        )

    def test_floating_ip_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_ip,
            floating_ip.FloatingIP,
            True,
            expected_kwargs={'if_revision': None},
        )

    def test_floating_ip_delete_if_revision(self):
        self.verify_delete(
            self.proxy.delete_ip,
            floating_ip.FloatingIP,
            True,
            method_kwargs={'if_revision': 42},
            expected_kwargs={'if_revision': 42},
        )

    def test_floating_ip_find(self):
        self.verify_find(self.proxy.find_ip, floating_ip.FloatingIP)

    def test_floating_ip_get(self):
        self.verify_get(self.proxy.get_ip, floating_ip.FloatingIP)

    def test_ips(self):
        self.verify_list(self.proxy.ips, floating_ip.FloatingIP)

    def test_floating_ip_update(self):
        self.verify_update(
            self.proxy.update_ip,
            floating_ip.FloatingIP,
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': None},
        )

    def test_floating_ip_update_if_revision(self):
        self.verify_update(
            self.proxy.update_ip,
            floating_ip.FloatingIP,
            method_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
        )


class TestNetworkHealthMonitor(TestNetworkProxy):
    def test_health_monitor_create_attrs(self):
        self.verify_create(
            self.proxy.create_health_monitor, health_monitor.HealthMonitor
        )

    def test_health_monitor_delete(self):
        self.verify_delete(
            self.proxy.delete_health_monitor,
            health_monitor.HealthMonitor,
            False,
        )

    def test_health_monitor_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_health_monitor,
            health_monitor.HealthMonitor,
            True,
        )

    def test_health_monitor_find(self):
        self.verify_find(
            self.proxy.find_health_monitor, health_monitor.HealthMonitor
        )

    def test_health_monitor_get(self):
        self.verify_get(
            self.proxy.get_health_monitor, health_monitor.HealthMonitor
        )

    def test_health_monitors(self):
        self.verify_list(
            self.proxy.health_monitors, health_monitor.HealthMonitor
        )

    def test_health_monitor_update(self):
        self.verify_update(
            self.proxy.update_health_monitor, health_monitor.HealthMonitor
        )


class TestNetworkListener(TestNetworkProxy):
    def test_listener_create_attrs(self):
        self.verify_create(self.proxy.create_listener, listener.Listener)

    def test_listener_delete(self):
        self.verify_delete(
            self.proxy.delete_listener, listener.Listener, False
        )

    def test_listener_delete_ignore(self):
        self.verify_delete(self.proxy.delete_listener, listener.Listener, True)

    def test_listener_find(self):
        self.verify_find(self.proxy.find_listener, listener.Listener)

    def test_listener_get(self):
        self.verify_get(self.proxy.get_listener, listener.Listener)

    def test_listeners(self):
        self.verify_list(self.proxy.listeners, listener.Listener)

    def test_listener_update(self):
        self.verify_update(self.proxy.update_listener, listener.Listener)


class TestNetworkLoadBalancer(TestNetworkProxy):
    def test_load_balancer_create_attrs(self):
        self.verify_create(
            self.proxy.create_load_balancer, load_balancer.LoadBalancer
        )

    def test_load_balancer_delete(self):
        self.verify_delete(
            self.proxy.delete_load_balancer, load_balancer.LoadBalancer, False
        )

    def test_load_balancer_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_load_balancer, load_balancer.LoadBalancer, True
        )

    def test_load_balancer_find(self):
        self.verify_find(
            self.proxy.find_load_balancer, load_balancer.LoadBalancer
        )

    def test_load_balancer_get(self):
        self.verify_get(
            self.proxy.get_load_balancer, load_balancer.LoadBalancer
        )

    def test_load_balancers(self):
        self.verify_list(self.proxy.load_balancers, load_balancer.LoadBalancer)

    def test_load_balancer_update(self):
        self.verify_update(
            self.proxy.update_load_balancer, load_balancer.LoadBalancer
        )


class TestNetworkMeteringLabel(TestNetworkProxy):
    def test_metering_label_create_attrs(self):
        self.verify_create(
            self.proxy.create_metering_label, metering_label.MeteringLabel
        )

    def test_metering_label_delete(self):
        self.verify_delete(
            self.proxy.delete_metering_label,
            metering_label.MeteringLabel,
            False,
        )

    def test_metering_label_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_metering_label,
            metering_label.MeteringLabel,
            True,
        )

    def test_metering_label_find(self):
        self.verify_find(
            self.proxy.find_metering_label, metering_label.MeteringLabel
        )

    def test_metering_label_get(self):
        self.verify_get(
            self.proxy.get_metering_label, metering_label.MeteringLabel
        )

    def test_metering_labels(self):
        self.verify_list(
            self.proxy.metering_labels, metering_label.MeteringLabel
        )

    def test_metering_label_update(self):
        self.verify_update(
            self.proxy.update_metering_label, metering_label.MeteringLabel
        )

    def test_metering_label_rule_create_attrs(self):
        self.verify_create(
            self.proxy.create_metering_label_rule,
            metering_label_rule.MeteringLabelRule,
        )

    def test_metering_label_rule_delete(self):
        self.verify_delete(
            self.proxy.delete_metering_label_rule,
            metering_label_rule.MeteringLabelRule,
            False,
        )

    def test_metering_label_rule_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_metering_label_rule,
            metering_label_rule.MeteringLabelRule,
            True,
        )

    def test_metering_label_rule_find(self):
        self.verify_find(
            self.proxy.find_metering_label_rule,
            metering_label_rule.MeteringLabelRule,
        )

    def test_metering_label_rule_get(self):
        self.verify_get(
            self.proxy.get_metering_label_rule,
            metering_label_rule.MeteringLabelRule,
        )

    def test_metering_label_rules(self):
        self.verify_list(
            self.proxy.metering_label_rules,
            metering_label_rule.MeteringLabelRule,
        )

    def test_metering_label_rule_update(self):
        self.verify_update(
            self.proxy.update_metering_label_rule,
            metering_label_rule.MeteringLabelRule,
        )


class TestNetworkNetwork(TestNetworkProxy):
    def test_network_create_attrs(self):
        self.verify_create(self.proxy.create_network, network.Network)

    def test_network_delete(self):
        self.verify_delete(
            self.proxy.delete_network,
            network.Network,
            False,
            expected_kwargs={'if_revision': None},
        )

    def test_network_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_network,
            network.Network,
            True,
            expected_kwargs={'if_revision': None},
        )

    def test_network_delete_if_revision(self):
        self.verify_delete(
            self.proxy.delete_network,
            network.Network,
            True,
            method_kwargs={'if_revision': 42},
            expected_kwargs={'if_revision': 42},
        )

    def test_network_find(self):
        self.verify_find(self.proxy.find_network, network.Network)

    def test_network_find_with_filter(self):
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_network,
            method_args=["net1"],
            method_kwargs={"project_id": "1"},
            expected_args=[network.Network, "net1"],
            expected_kwargs={"project_id": "1", "ignore_missing": True},
        )

    def test_network_get(self):
        self.verify_get(self.proxy.get_network, network.Network)

    def test_networks(self):
        self.verify_list(self.proxy.networks, network.Network)

    def test_network_update(self):
        self.verify_update(
            self.proxy.update_network,
            network.Network,
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': None},
        )

    def test_network_update_if_revision(self):
        self.verify_update(
            self.proxy.update_network,
            network.Network,
            method_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
        )


class TestNetworkFlavor(TestNetworkProxy):
    def test_flavor_create_attrs(self):
        self.verify_create(self.proxy.create_flavor, flavor.Flavor)

    def test_flavor_delete(self):
        self.verify_delete(self.proxy.delete_flavor, flavor.Flavor, True)

    def test_flavor_find(self):
        self.verify_find(self.proxy.find_flavor, flavor.Flavor)

    def test_flavor_get(self):
        self.verify_get(self.proxy.get_flavor, flavor.Flavor)

    def test_flavor_update(self):
        self.verify_update(self.proxy.update_flavor, flavor.Flavor)

    def test_flavors(self):
        self.verify_list(self.proxy.flavors, flavor.Flavor)


class TestNetworkLocalIp(TestNetworkProxy):
    def test_local_ip_create_attrs(self):
        self.verify_create(self.proxy.create_local_ip, local_ip.LocalIP)

    def test_local_ip_delete(self):
        self.verify_delete(
            self.proxy.delete_local_ip,
            local_ip.LocalIP,
            False,
            expected_kwargs={'if_revision': None},
        )

    def test_local_ip_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_local_ip,
            local_ip.LocalIP,
            True,
            expected_kwargs={'if_revision': None},
        )

    def test_local_ip_delete_if_revision(self):
        self.verify_delete(
            self.proxy.delete_local_ip,
            local_ip.LocalIP,
            True,
            method_kwargs={'if_revision': 42},
            expected_kwargs={'if_revision': 42},
        )

    def test_local_ip_find(self):
        self.verify_find(self.proxy.find_local_ip, local_ip.LocalIP)

    def test_local_ip_get(self):
        self.verify_get(self.proxy.get_local_ip, local_ip.LocalIP)

    def test_local_ips(self):
        self.verify_list(self.proxy.local_ips, local_ip.LocalIP)

    def test_local_ip_update(self):
        self.verify_update(
            self.proxy.update_local_ip,
            local_ip.LocalIP,
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': None},
        )

    def test_local_ip_update_if_revision(self):
        self.verify_update(
            self.proxy.update_local_ip,
            local_ip.LocalIP,
            method_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
        )


class TestNetworkLocalIpAssociation(TestNetworkProxy):
    def test_local_ip_association_create_attrs(self):
        self.verify_create(
            self.proxy.create_local_ip_association,
            local_ip_association.LocalIPAssociation,
            method_kwargs={'local_ip': LOCAL_IP_ID},
            expected_kwargs={'local_ip_id': LOCAL_IP_ID},
        )

    def test_local_ip_association_delete(self):
        self.verify_delete(
            self.proxy.delete_local_ip_association,
            local_ip_association.LocalIPAssociation,
            ignore_missing=False,
            method_args=[LOCAL_IP_ID, "resource_or_id"],
            expected_args=["resource_or_id"],
            expected_kwargs={'if_revision': None, 'local_ip_id': LOCAL_IP_ID},
        )

    def test_local_ip_association_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_local_ip_association,
            local_ip_association.LocalIPAssociation,
            ignore_missing=True,
            method_args=[LOCAL_IP_ID, "resource_or_id"],
            expected_args=["resource_or_id"],
            expected_kwargs={'if_revision': None, 'local_ip_id': LOCAL_IP_ID},
        )

    def test_local_ip_association_find(self):
        lip = local_ip.LocalIP.new(id=LOCAL_IP_ID)

        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_local_ip_association,
            method_args=['local_ip_association_id', lip],
            expected_args=[
                local_ip_association.LocalIPAssociation,
                'local_ip_association_id',
            ],
            expected_kwargs={
                'ignore_missing': True,
                'local_ip_id': LOCAL_IP_ID,
            },
        )

    def test_local_ip_association_get(self):
        lip = local_ip.LocalIP.new(id=LOCAL_IP_ID)

        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_local_ip_association,
            method_args=['local_ip_association_id', lip],
            expected_args=[
                local_ip_association.LocalIPAssociation,
                'local_ip_association_id',
            ],
            expected_kwargs={'local_ip_id': LOCAL_IP_ID},
        )

    def test_local_ip_associations(self):
        self.verify_list(
            self.proxy.local_ip_associations,
            local_ip_association.LocalIPAssociation,
            method_kwargs={'local_ip': LOCAL_IP_ID},
            expected_kwargs={'local_ip_id': LOCAL_IP_ID},
        )


class TestNetworkServiceProfile(TestNetworkProxy):
    def test_service_profile_create_attrs(self):
        self.verify_create(
            self.proxy.create_service_profile, service_profile.ServiceProfile
        )

    def test_service_profile_delete(self):
        self.verify_delete(
            self.proxy.delete_service_profile,
            service_profile.ServiceProfile,
            True,
        )

    def test_service_profile_find(self):
        self.verify_find(
            self.proxy.find_service_profile, service_profile.ServiceProfile
        )

    def test_service_profile_get(self):
        self.verify_get(
            self.proxy.get_service_profile, service_profile.ServiceProfile
        )

    def test_service_profiles(self):
        self.verify_list(
            self.proxy.service_profiles, service_profile.ServiceProfile
        )

    def test_service_profile_update(self):
        self.verify_update(
            self.proxy.update_service_profile, service_profile.ServiceProfile
        )


class TestNetworkIpAvailability(TestNetworkProxy):
    def test_network_ip_availability_find(self):
        self.verify_find(
            self.proxy.find_network_ip_availability,
            network_ip_availability.NetworkIPAvailability,
        )

    def test_network_ip_availability_get(self):
        self.verify_get(
            self.proxy.get_network_ip_availability,
            network_ip_availability.NetworkIPAvailability,
        )

    def test_network_ip_availabilities(self):
        self.verify_list(
            self.proxy.network_ip_availabilities,
            network_ip_availability.NetworkIPAvailability,
        )

    def test_pool_member_create_attrs(self):
        self.verify_create(
            self.proxy.create_pool_member,
            pool_member.PoolMember,
            method_kwargs={"pool": "test_id"},
            expected_kwargs={"pool_id": "test_id"},
        )


class TestNetworkPoolMember(TestNetworkProxy):
    def test_pool_member_delete(self):
        self.verify_delete(
            self.proxy.delete_pool_member,
            pool_member.PoolMember,
            ignore_missing=False,
            method_kwargs={"pool": "test_id"},
            expected_kwargs={"pool_id": "test_id"},
        )

    def test_pool_member_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_pool_member,
            pool_member.PoolMember,
            ignore_missing=True,
            method_kwargs={"pool": "test_id"},
            expected_kwargs={"pool_id": "test_id"},
        )

    def test_pool_member_find(self):
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_pool_member,
            method_args=["MEMBER", "POOL"],
            expected_args=[pool_member.PoolMember, "MEMBER"],
            expected_kwargs={"pool_id": "POOL", "ignore_missing": True},
        )

    def test_pool_member_get(self):
        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_pool_member,
            method_args=["MEMBER", "POOL"],
            expected_args=[pool_member.PoolMember, "MEMBER"],
            expected_kwargs={"pool_id": "POOL"},
        )

    def test_pool_members(self):
        self.verify_list(
            self.proxy.pool_members,
            pool_member.PoolMember,
            method_args=["test_id"],
            expected_args=[],
            expected_kwargs={"pool_id": "test_id"},
        )

    def test_pool_member_update(self):
        self._verify(
            "openstack.network.v2._proxy.Proxy._update",
            self.proxy.update_pool_member,
            method_args=["MEMBER", "POOL"],
            expected_args=[pool_member.PoolMember, "MEMBER"],
            expected_kwargs={"pool_id": "POOL"},
        )


class TestNetworkPool(TestNetworkProxy):
    def test_pool_create_attrs(self):
        self.verify_create(self.proxy.create_pool, pool.Pool)

    def test_pool_delete(self):
        self.verify_delete(self.proxy.delete_pool, pool.Pool, False)

    def test_pool_delete_ignore(self):
        self.verify_delete(self.proxy.delete_pool, pool.Pool, True)

    def test_pool_find(self):
        self.verify_find(self.proxy.find_pool, pool.Pool)

    def test_pool_get(self):
        self.verify_get(self.proxy.get_pool, pool.Pool)

    def test_pools(self):
        self.verify_list(self.proxy.pools, pool.Pool)

    def test_pool_update(self):
        self.verify_update(self.proxy.update_pool, pool.Pool)

    def test_port_create_attrs(self):
        self.verify_create(self.proxy.create_port, port.Port)

    def test_port_delete(self):
        self.verify_delete(
            self.proxy.delete_port,
            port.Port,
            False,
            expected_kwargs={'if_revision': None},
        )

    def test_port_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_port,
            port.Port,
            True,
            expected_kwargs={'if_revision': None},
        )

    def test_port_delete_if_revision(self):
        self.verify_delete(
            self.proxy.delete_port,
            port.Port,
            True,
            method_kwargs={'if_revision': 42},
            expected_kwargs={'if_revision': 42},
        )

    def test_port_find(self):
        self.verify_find(self.proxy.find_port, port.Port)

    def test_port_get(self):
        self.verify_get(self.proxy.get_port, port.Port)

    def test_ports(self):
        self.verify_list(self.proxy.ports, port.Port)

    def test_port_update(self):
        self.verify_update(
            self.proxy.update_port,
            port.Port,
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': None},
        )

    def test_port_update_if_revision(self):
        self.verify_update(
            self.proxy.update_port,
            port.Port,
            method_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
        )

    @mock.patch('openstack.network.v2._proxy.Proxy._bulk_create')
    def test_ports_create(self, bc):
        data = mock.sentinel

        self.proxy.create_ports(data)

        bc.assert_called_once_with(port.Port, data)


class TestNetworkQosBandwidth(TestNetworkProxy):
    def test_qos_bandwidth_limit_rule_create_attrs(self):
        self.verify_create(
            self.proxy.create_qos_bandwidth_limit_rule,
            qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_bandwidth_limit_rule_delete(self):
        self.verify_delete(
            self.proxy.delete_qos_bandwidth_limit_rule,
            qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            ignore_missing=False,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_bandwidth_limit_rule_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_qos_bandwidth_limit_rule,
            qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            ignore_missing=True,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_bandwidth_limit_rule_find(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_qos_bandwidth_limit_rule,
            method_args=['rule_id', policy],
            expected_args=[
                qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
                'rule_id',
            ],
            expected_kwargs={
                'ignore_missing': True,
                'qos_policy_id': QOS_POLICY_ID,
            },
        )

    def test_qos_bandwidth_limit_rule_get(self):
        self.verify_get(
            self.proxy.get_qos_bandwidth_limit_rule,
            qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_bandwidth_limit_rules(self):
        self.verify_list(
            self.proxy.qos_bandwidth_limit_rules,
            qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_bandwidth_limit_rule_update(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.network.v2._proxy.Proxy._update',
            self.proxy.update_qos_bandwidth_limit_rule,
            method_args=['rule_id', policy],
            method_kwargs={'foo': 'bar'},
            expected_args=[
                qos_bandwidth_limit_rule.QoSBandwidthLimitRule,
                'rule_id',
            ],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID, 'foo': 'bar'},
        )


class TestNetworkQosDscpMarking(TestNetworkProxy):
    def test_qos_dscp_marking_rule_create_attrs(self):
        self.verify_create(
            self.proxy.create_qos_dscp_marking_rule,
            qos_dscp_marking_rule.QoSDSCPMarkingRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_dscp_marking_rule_delete(self):
        self.verify_delete(
            self.proxy.delete_qos_dscp_marking_rule,
            qos_dscp_marking_rule.QoSDSCPMarkingRule,
            ignore_missing=False,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_dscp_marking_rule_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_qos_dscp_marking_rule,
            qos_dscp_marking_rule.QoSDSCPMarkingRule,
            ignore_missing=True,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_dscp_marking_rule_find(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_qos_dscp_marking_rule,
            method_args=['rule_id', policy],
            expected_args=[
                qos_dscp_marking_rule.QoSDSCPMarkingRule,
                'rule_id',
            ],
            expected_kwargs={
                'ignore_missing': True,
                'qos_policy_id': QOS_POLICY_ID,
            },
        )

    def test_qos_dscp_marking_rule_get(self):
        self.verify_get(
            self.proxy.get_qos_dscp_marking_rule,
            qos_dscp_marking_rule.QoSDSCPMarkingRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_dscp_marking_rules(self):
        self.verify_list(
            self.proxy.qos_dscp_marking_rules,
            qos_dscp_marking_rule.QoSDSCPMarkingRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_dscp_marking_rule_update(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.network.v2._proxy.Proxy._update',
            self.proxy.update_qos_dscp_marking_rule,
            method_args=['rule_id', policy],
            method_kwargs={'foo': 'bar'},
            expected_args=[
                qos_dscp_marking_rule.QoSDSCPMarkingRule,
                'rule_id',
            ],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID, 'foo': 'bar'},
        )


class TestNetworkQosMinimumBandwidth(TestNetworkProxy):
    def test_qos_minimum_bandwidth_rule_create_attrs(self):
        self.verify_create(
            self.proxy.create_qos_minimum_bandwidth_rule,
            qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_bandwidth_rule_delete(self):
        self.verify_delete(
            self.proxy.delete_qos_minimum_bandwidth_rule,
            qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            ignore_missing=False,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_bandwidth_rule_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_qos_minimum_bandwidth_rule,
            qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            ignore_missing=True,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_bandwidth_rule_find(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_qos_minimum_bandwidth_rule,
            method_args=['rule_id', policy],
            expected_args=[
                qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
                'rule_id',
            ],
            expected_kwargs={
                'ignore_missing': True,
                'qos_policy_id': QOS_POLICY_ID,
            },
        )

    def test_qos_minimum_bandwidth_rule_get(self):
        self.verify_get(
            self.proxy.get_qos_minimum_bandwidth_rule,
            qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_bandwidth_rules(self):
        self.verify_list(
            self.proxy.qos_minimum_bandwidth_rules,
            qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_bandwidth_rule_update(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.network.v2._proxy.Proxy._update',
            self.proxy.update_qos_minimum_bandwidth_rule,
            method_args=['rule_id', policy],
            method_kwargs={'foo': 'bar'},
            expected_args=[
                qos_minimum_bandwidth_rule.QoSMinimumBandwidthRule,
                'rule_id',
            ],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID, 'foo': 'bar'},
        )


class TestNetworkQosMinimumPacketRate(TestNetworkProxy):
    def test_qos_minimum_packet_rate_rule_create_attrs(self):
        self.verify_create(
            self.proxy.create_qos_minimum_packet_rate_rule,
            qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_packet_rate_rule_delete(self):
        self.verify_delete(
            self.proxy.delete_qos_minimum_packet_rate_rule,
            qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            ignore_missing=False,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_packet_rate_rule_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_qos_minimum_packet_rate_rule,
            qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            ignore_missing=True,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_packet_rate_rule_find(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_qos_minimum_packet_rate_rule,
            method_args=['rule_id', policy],
            expected_args=[
                qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
                'rule_id',
            ],
            expected_kwargs={
                'ignore_missing': True,
                'qos_policy_id': QOS_POLICY_ID,
            },
        )

    def test_qos_minimum_packet_rate_rule_get(self):
        self.verify_get(
            self.proxy.get_qos_minimum_packet_rate_rule,
            qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_packet_rate_rules(self):
        self.verify_list(
            self.proxy.qos_minimum_packet_rate_rules,
            qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_minimum_packet_rate_rule_update(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.network.v2._proxy.Proxy._update',
            self.proxy.update_qos_minimum_packet_rate_rule,
            method_args=['rule_id', policy],
            method_kwargs={'foo': 'bar'},
            expected_args=[
                qos_minimum_packet_rate_rule.QoSMinimumPacketRateRule,
                'rule_id',
            ],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID, 'foo': 'bar'},
        )


class TestNetworkQosPacketRateLimitRule(TestNetworkProxy):
    def test_qos_packet_rate_limit_rule_create_attrs(self):
        self.verify_create(
            self.proxy.create_qos_packet_rate_limit_rule,
            qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_packet_rate_limit_rule_delete(self):
        self.verify_delete(
            self.proxy.delete_qos_packet_rate_limit_rule,
            qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            ignore_missing=False,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_packet_rate_limit_rule_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_qos_packet_rate_limit_rule,
            qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            ignore_missing=True,
            method_args=["resource_or_id", QOS_POLICY_ID],
            expected_args=["resource_or_id"],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_packet_rate_limit_rule_find(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_qos_packet_rate_limit_rule,
            method_args=['rule_id', policy],
            expected_args=[
                qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
                'rule_id',
            ],
            expected_kwargs={
                'ignore_missing': True,
                'qos_policy_id': QOS_POLICY_ID,
            },
        )

    def test_qos_packet_rate_limit_rule_get(self):
        self.verify_get(
            self.proxy.get_qos_packet_rate_limit_rule,
            qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_packet_rate_limit_rules(self):
        self.verify_list(
            self.proxy.qos_packet_rate_limit_rules,
            qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
            method_kwargs={'qos_policy': QOS_POLICY_ID},
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID},
        )

    def test_qos_packet_rate_limit_rule_update(self):
        policy = qos_policy.QoSPolicy.new(id=QOS_POLICY_ID)
        self._verify(
            'openstack.network.v2._proxy.Proxy._update',
            self.proxy.update_qos_packet_rate_limit_rule,
            method_args=['rule_id', policy],
            method_kwargs={'foo': 'bar'},
            expected_args=[
                qos_packet_rate_limit_rule.QoSPacketRateLimitRule,
                'rule_id',
            ],
            expected_kwargs={'qos_policy_id': QOS_POLICY_ID, 'foo': 'bar'},
        )


class TestNetworkQosRuleType(TestNetworkProxy):
    def test_qos_rule_type_find(self):
        self.verify_find(
            self.proxy.find_qos_rule_type, qos_rule_type.QoSRuleType
        )

    def test_qos_rule_type_get(self):
        self.verify_get(
            self.proxy.get_qos_rule_type, qos_rule_type.QoSRuleType
        )

    def test_qos_rule_types(self):
        self.verify_list(self.proxy.qos_rule_types, qos_rule_type.QoSRuleType)


class TestNetworkQuota(TestNetworkProxy):
    def test_quota_delete(self):
        self.verify_delete(self.proxy.delete_quota, quota.Quota, False)

    def test_quota_delete_ignore(self):
        self.verify_delete(self.proxy.delete_quota, quota.Quota, True)

    def test_quota_get(self):
        self.verify_get(self.proxy.get_quota, quota.Quota)

    @mock.patch.object(proxy_base.Proxy, "_get_resource")
    def test_quota_get_details(self, mock_get):
        fake_quota = mock.Mock(project_id='PROJECT')
        mock_get.return_value = fake_quota
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_quota,
            method_args=['QUOTA_ID'],
            method_kwargs={'details': True},
            expected_args=[quota.QuotaDetails],
            expected_kwargs={'project': fake_quota.id, 'requires_id': False},
        )
        mock_get.assert_called_once_with(quota.Quota, 'QUOTA_ID')

    @mock.patch.object(proxy_base.Proxy, "_get_resource")
    def test_quota_default_get(self, mock_get):
        fake_quota = mock.Mock(project_id='PROJECT')
        mock_get.return_value = fake_quota
        self._verify(
            "openstack.proxy.Proxy._get",
            self.proxy.get_quota_default,
            method_args=['QUOTA_ID'],
            expected_args=[quota.QuotaDefault],
            expected_kwargs={'project': fake_quota.id, 'requires_id': False},
        )
        mock_get.assert_called_once_with(quota.Quota, 'QUOTA_ID')

    def test_quotas(self):
        self.verify_list(self.proxy.quotas, quota.Quota)

    def test_quota_update(self):
        self.verify_update(self.proxy.update_quota, quota.Quota)


class TestNetworkRbacPolicy(TestNetworkProxy):
    def test_rbac_policy_create_attrs(self):
        self.verify_create(
            self.proxy.create_rbac_policy, rbac_policy.RBACPolicy
        )

    def test_rbac_policy_delete(self):
        self.verify_delete(
            self.proxy.delete_rbac_policy, rbac_policy.RBACPolicy, False
        )

    def test_rbac_policy_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_rbac_policy, rbac_policy.RBACPolicy, True
        )

    def test_rbac_policy_find(self):
        self.verify_find(self.proxy.find_rbac_policy, rbac_policy.RBACPolicy)

    def test_rbac_policy_get(self):
        self.verify_get(self.proxy.get_rbac_policy, rbac_policy.RBACPolicy)

    def test_rbac_policies(self):
        self.verify_list(self.proxy.rbac_policies, rbac_policy.RBACPolicy)

    def test_rbac_policy_update(self):
        self.verify_update(
            self.proxy.update_rbac_policy, rbac_policy.RBACPolicy
        )


class TestNetworkRouter(TestNetworkProxy):
    def test_router_create_attrs(self):
        self.verify_create(self.proxy.create_router, router.Router)

    def test_router_delete(self):
        self.verify_delete(
            self.proxy.delete_router,
            router.Router,
            False,
            expected_kwargs={'if_revision': None},
        )

    def test_router_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_router,
            router.Router,
            True,
            expected_kwargs={'if_revision': None},
        )

    def test_router_delete_if_revision(self):
        self.verify_delete(
            self.proxy.delete_router,
            router.Router,
            True,
            method_kwargs={'if_revision': 42},
            expected_kwargs={'if_revision': 42},
        )

    def test_router_find(self):
        self.verify_find(self.proxy.find_router, router.Router)

    def test_router_get(self):
        self.verify_get(self.proxy.get_router, router.Router)

    def test_routers(self):
        self.verify_list(self.proxy.routers, router.Router)

    def test_router_update(self):
        self.verify_update(
            self.proxy.update_router,
            router.Router,
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': None},
        )

    def test_router_update_if_revision(self):
        self.verify_update(
            self.proxy.update_router,
            router.Router,
            method_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
        )

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'add_interface')
    def test_add_interface_to_router_with_port(
        self, mock_add_interface, mock_get
    ):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.add_interface",
            self.proxy.add_interface_to_router,
            method_args=["FAKE_ROUTER"],
            method_kwargs={"port_id": "PORT"},
            expected_args=[self.proxy],
            expected_kwargs={"port_id": "PORT"},
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'add_interface')
    def test_add_interface_to_router_with_subnet(
        self, mock_add_interface, mock_get
    ):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.add_interface",
            self.proxy.add_interface_to_router,
            method_args=["FAKE_ROUTER"],
            method_kwargs={"subnet_id": "SUBNET"},
            expected_args=[self.proxy],
            expected_kwargs={"subnet_id": "SUBNET"},
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'remove_interface')
    def test_remove_interface_from_router_with_port(
        self, mock_remove, mock_get
    ):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.remove_interface",
            self.proxy.remove_interface_from_router,
            method_args=["FAKE_ROUTER"],
            method_kwargs={"port_id": "PORT"},
            expected_args=[self.proxy],
            expected_kwargs={"port_id": "PORT"},
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'remove_interface')
    def test_remove_interface_from_router_with_subnet(
        self, mock_remove, mock_get
    ):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.remove_interface",
            self.proxy.remove_interface_from_router,
            method_args=["FAKE_ROUTER"],
            method_kwargs={"subnet_id": "SUBNET"},
            expected_args=[self.proxy],
            expected_kwargs={"subnet_id": "SUBNET"},
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'add_extra_routes')
    def test_add_extra_routes_to_router(self, mock_add_extra_routes, mock_get):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.add_extra_routes",
            self.proxy.add_extra_routes_to_router,
            method_args=["FAKE_ROUTER"],
            method_kwargs={"body": {"router": {"routes": []}}},
            expected_args=[self.proxy],
            expected_kwargs={"body": {"router": {"routes": []}}},
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'remove_extra_routes')
    def test_remove_extra_routes_from_router(
        self, mock_remove_extra_routes, mock_get
    ):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.remove_extra_routes",
            self.proxy.remove_extra_routes_from_router,
            method_args=["FAKE_ROUTER"],
            method_kwargs={"body": {"router": {"routes": []}}},
            expected_args=[self.proxy],
            expected_kwargs={"body": {"router": {"routes": []}}},
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'add_gateway')
    def test_add_gateway_to_router(self, mock_add, mock_get):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.add_gateway",
            self.proxy.add_gateway_to_router,
            method_args=["FAKE_ROUTER"],
            method_kwargs={"foo": "bar"},
            expected_args=[self.proxy],
            expected_kwargs={"foo": "bar"},
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'remove_gateway')
    def test_remove_gateway_from_router(self, mock_remove, mock_get):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.remove_gateway",
            self.proxy.remove_gateway_from_router,
            method_args=["FAKE_ROUTER"],
            method_kwargs={"foo": "bar"},
            expected_args=[self.proxy],
            expected_kwargs={"foo": "bar"},
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'add_external_gateways')
    def test_add_external_gateways(self, mock_add, mock_get):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.add_external_gateways",
            self.proxy.add_external_gateways,
            method_args=["FAKE_ROUTER", "bar"],
            expected_args=[self.proxy, "bar"],
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'update_external_gateways')
    def test_update_external_gateways(self, mock_remove, mock_get):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.update_external_gateways",
            self.proxy.update_external_gateways,
            method_args=["FAKE_ROUTER", "bar"],
            expected_args=[self.proxy, "bar"],
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    @mock.patch.object(router.Router, 'remove_external_gateways')
    def test_remove_external_gateways(self, mock_remove, mock_get):
        x_router = router.Router.new(id="ROUTER_ID")
        mock_get.return_value = x_router

        self._verify(
            "openstack.network.v2.router.Router.remove_external_gateways",
            self.proxy.remove_external_gateways,
            method_args=["FAKE_ROUTER", "bar"],
            expected_args=[self.proxy, "bar"],
        )
        mock_get.assert_called_once_with(router.Router, "FAKE_ROUTER")

    def test_router_hosting_l3_agents_list(self):
        self.verify_list(
            self.proxy.routers_hosting_l3_agents,
            agent.RouterL3Agent,
            method_kwargs={'router': ROUTER_ID},
            expected_kwargs={'router_id': ROUTER_ID},
        )

    def test_agent_hosted_routers_list(self):
        self.verify_list(
            self.proxy.agent_hosted_routers,
            router.L3AgentRouter,
            method_kwargs={'agent': AGENT_ID},
            expected_kwargs={'agent_id': AGENT_ID},
        )


class TestNetworkFirewallGroup(TestNetworkProxy):
    def test_firewall_group_create_attrs(self):
        self.verify_create(
            self.proxy.create_firewall_group, firewall_group.FirewallGroup
        )

    def test_firewall_group_delete(self):
        self.verify_delete(
            self.proxy.delete_firewall_group,
            firewall_group.FirewallGroup,
            False,
        )

    def test_firewall_group_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_firewall_group,
            firewall_group.FirewallGroup,
            True,
        )

    def test_firewall_group_find(self):
        self.verify_find(
            self.proxy.find_firewall_group, firewall_group.FirewallGroup
        )

    def test_firewall_group_get(self):
        self.verify_get(
            self.proxy.get_firewall_group, firewall_group.FirewallGroup
        )

    def test_firewall_groups(self):
        self.verify_list(
            self.proxy.firewall_groups, firewall_group.FirewallGroup
        )

    def test_firewall_group_update(self):
        self.verify_update(
            self.proxy.update_firewall_group, firewall_group.FirewallGroup
        )


class TestNetworkPolicy(TestNetworkProxy):
    def test_firewall_policy_create_attrs(self):
        self.verify_create(
            self.proxy.create_firewall_policy, firewall_policy.FirewallPolicy
        )

    def test_firewall_policy_delete(self):
        self.verify_delete(
            self.proxy.delete_firewall_policy,
            firewall_policy.FirewallPolicy,
            False,
        )

    def test_firewall_policy_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_firewall_policy,
            firewall_policy.FirewallPolicy,
            True,
        )

    def test_firewall_policy_find(self):
        self.verify_find(
            self.proxy.find_firewall_policy, firewall_policy.FirewallPolicy
        )

    def test_firewall_policy_get(self):
        self.verify_get(
            self.proxy.get_firewall_policy, firewall_policy.FirewallPolicy
        )

    def test_firewall_policies(self):
        self.verify_list(
            self.proxy.firewall_policies, firewall_policy.FirewallPolicy
        )

    def test_firewall_policy_update(self):
        self.verify_update(
            self.proxy.update_firewall_policy, firewall_policy.FirewallPolicy
        )


class TestNetworkRule(TestNetworkProxy):
    def test_firewall_rule_create_attrs(self):
        self.verify_create(
            self.proxy.create_firewall_rule, firewall_rule.FirewallRule
        )

    def test_firewall_rule_delete(self):
        self.verify_delete(
            self.proxy.delete_firewall_rule, firewall_rule.FirewallRule, False
        )

    def test_firewall_rule_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_firewall_rule, firewall_rule.FirewallRule, True
        )

    def test_firewall_rule_find(self):
        self.verify_find(
            self.proxy.find_firewall_rule, firewall_rule.FirewallRule
        )

    def test_firewall_rule_get(self):
        self.verify_get(
            self.proxy.get_firewall_rule, firewall_rule.FirewallRule
        )

    def test_firewall_rules(self):
        self.verify_list(self.proxy.firewall_rules, firewall_rule.FirewallRule)

    def test_firewall_rule_update(self):
        self.verify_update(
            self.proxy.update_firewall_rule, firewall_rule.FirewallRule
        )


class TestNetworkNetworkSegment(TestNetworkProxy):
    def test_network_segment_range_create_attrs(self):
        self.verify_create(
            self.proxy.create_network_segment_range,
            network_segment_range.NetworkSegmentRange,
        )

    def test_network_segment_range_delete(self):
        self.verify_delete(
            self.proxy.delete_network_segment_range,
            network_segment_range.NetworkSegmentRange,
            False,
        )

    def test_network_segment_range_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_network_segment_range,
            network_segment_range.NetworkSegmentRange,
            True,
        )

    def test_network_segment_range_find(self):
        self.verify_find(
            self.proxy.find_network_segment_range,
            network_segment_range.NetworkSegmentRange,
        )

    def test_network_segment_range_get(self):
        self.verify_get(
            self.proxy.get_network_segment_range,
            network_segment_range.NetworkSegmentRange,
        )

    def test_network_segment_ranges(self):
        self.verify_list(
            self.proxy.network_segment_ranges,
            network_segment_range.NetworkSegmentRange,
        )

    def test_network_segment_range_update(self):
        self.verify_update(
            self.proxy.update_network_segment_range,
            network_segment_range.NetworkSegmentRange,
        )


class TestNetworkSecurityGroup(TestNetworkProxy):
    def test_security_group_create_attrs(self):
        self.verify_create(
            self.proxy.create_security_group, security_group.SecurityGroup
        )

    def test_security_group_delete(self):
        self.verify_delete(
            self.proxy.delete_security_group,
            security_group.SecurityGroup,
            False,
            expected_kwargs={'if_revision': None},
        )

    def test_security_group_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_security_group,
            security_group.SecurityGroup,
            True,
            expected_kwargs={'if_revision': None},
        )

    def test_security_group_delete_if_revision(self):
        self.verify_delete(
            self.proxy.delete_security_group,
            security_group.SecurityGroup,
            True,
            method_kwargs={'if_revision': 42},
            expected_kwargs={'if_revision': 42},
        )

    def test_security_group_find(self):
        self.verify_find(
            self.proxy.find_security_group, security_group.SecurityGroup
        )

    def test_security_group_get(self):
        self.verify_get(
            self.proxy.get_security_group, security_group.SecurityGroup
        )

    def test_security_groups(self):
        self.verify_list(
            self.proxy.security_groups, security_group.SecurityGroup
        )

    def test_security_group_update(self):
        self.verify_update(
            self.proxy.update_security_group,
            security_group.SecurityGroup,
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': None},
        )

    def test_security_group_update_if_revision(self):
        self.verify_update(
            self.proxy.update_security_group,
            security_group.SecurityGroup,
            method_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': 42},
        )

    def test_security_group_rule_create_attrs(self):
        self.verify_create(
            self.proxy.create_security_group_rule,
            security_group_rule.SecurityGroupRule,
        )

    def test_security_group_rule_delete(self):
        self.verify_delete(
            self.proxy.delete_security_group_rule,
            security_group_rule.SecurityGroupRule,
            False,
            expected_kwargs={'if_revision': None},
        )

    def test_security_group_rule_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_security_group_rule,
            security_group_rule.SecurityGroupRule,
            True,
            expected_kwargs={'if_revision': None},
        )

    def test_security_group_rule_delete_if_revision(self):
        self.verify_delete(
            self.proxy.delete_security_group_rule,
            security_group_rule.SecurityGroupRule,
            True,
            method_kwargs={'if_revision': 42},
            expected_kwargs={'if_revision': 42},
        )

    def test_security_group_rule_find(self):
        self.verify_find(
            self.proxy.find_security_group_rule,
            security_group_rule.SecurityGroupRule,
        )

    def test_security_group_rule_get(self):
        self.verify_get(
            self.proxy.get_security_group_rule,
            security_group_rule.SecurityGroupRule,
        )

    def test_security_group_rules(self):
        self.verify_list(
            self.proxy.security_group_rules,
            security_group_rule.SecurityGroupRule,
        )

    @mock.patch('openstack.network.v2._proxy.Proxy._bulk_create')
    def test_security_group_rules_create(self, bc):
        data = mock.sentinel

        self.proxy.create_security_group_rules(data)

        bc.assert_called_once_with(security_group_rule.SecurityGroupRule, data)


class TestNetworkSegment(TestNetworkProxy):
    def test_segment_create_attrs(self):
        self.verify_create(self.proxy.create_segment, segment.Segment)

    def test_segment_delete(self):
        self.verify_delete(self.proxy.delete_segment, segment.Segment, False)

    def test_segment_delete_ignore(self):
        self.verify_delete(self.proxy.delete_segment, segment.Segment, True)

    def test_segment_find(self):
        self.verify_find(self.proxy.find_segment, segment.Segment)

    def test_segment_get(self):
        self.verify_get(self.proxy.get_segment, segment.Segment)

    def test_segments(self):
        self.verify_list(self.proxy.segments, segment.Segment)

    def test_segment_update(self):
        self.verify_update(self.proxy.update_segment, segment.Segment)


class TestNetworkSubnet(TestNetworkProxy):
    def test_subnet_create_attrs(self):
        self.verify_create(self.proxy.create_subnet, subnet.Subnet)

    def test_subnet_delete(self):
        self.verify_delete(
            self.proxy.delete_subnet,
            subnet.Subnet,
            False,
            expected_kwargs={'if_revision': None},
        )

    def test_subnet_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_subnet,
            subnet.Subnet,
            True,
            expected_kwargs={'if_revision': None},
        )

    def test_subnet_delete_if_revision(self):
        self.verify_delete(
            self.proxy.delete_subnet,
            subnet.Subnet,
            True,
            method_kwargs={'if_revision': 42},
            expected_kwargs={'if_revision': 42},
        )

    def test_subnet_find(self):
        self.verify_find(self.proxy.find_subnet, subnet.Subnet)

    def test_subnet_get(self):
        self.verify_get(self.proxy.get_subnet, subnet.Subnet)

    def test_subnets(self):
        self.verify_list(self.proxy.subnets, subnet.Subnet)

    def test_subnet_update(self):
        self.verify_update(
            self.proxy.update_subnet,
            subnet.Subnet,
            expected_kwargs={'x': 1, 'y': 2, 'z': 3, 'if_revision': None},
        )

    def test_subnet_pool_create_attrs(self):
        self.verify_create(
            self.proxy.create_subnet_pool, subnet_pool.SubnetPool
        )

    def test_subnet_pool_delete(self):
        self.verify_delete(
            self.proxy.delete_subnet_pool, subnet_pool.SubnetPool, False
        )

    def test_subnet_pool_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_subnet_pool, subnet_pool.SubnetPool, True
        )

    def test_subnet_pool_find(self):
        self.verify_find(self.proxy.find_subnet_pool, subnet_pool.SubnetPool)

    def test_subnet_pool_get(self):
        self.verify_get(self.proxy.get_subnet_pool, subnet_pool.SubnetPool)

    def test_subnet_pools(self):
        self.verify_list(self.proxy.subnet_pools, subnet_pool.SubnetPool)

    def test_subnet_pool_update(self):
        self.verify_update(
            self.proxy.update_subnet_pool, subnet_pool.SubnetPool
        )


class TestNetworkVpnEndpointGroup(TestNetworkProxy):
    def test_vpn_endpoint_group_create_attrs(self):
        self.verify_create(
            self.proxy.create_vpn_endpoint_group,
            vpn_endpoint_group.VpnEndpointGroup,
        )

    def test_vpn_endpoint_group_delete(self):
        self.verify_delete(
            self.proxy.delete_vpn_endpoint_group,
            vpn_endpoint_group.VpnEndpointGroup,
            False,
        )

    def test_vpn_endpoint_group_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_vpn_endpoint_group,
            vpn_endpoint_group.VpnEndpointGroup,
            True,
        )

    def test_vpn_endpoint_group_find(self):
        self.verify_find(
            self.proxy.find_vpn_endpoint_group,
            vpn_endpoint_group.VpnEndpointGroup,
        )

    def test_vpn_endpoint_group_get(self):
        self.verify_get(
            self.proxy.get_vpn_endpoint_group,
            vpn_endpoint_group.VpnEndpointGroup,
        )

    def test_vpn_endpoint_groups(self):
        self.verify_list(
            self.proxy.vpn_endpoint_groups, vpn_endpoint_group.VpnEndpointGroup
        )

    def test_vpn_endpoint_group_update(self):
        self.verify_update(
            self.proxy.update_vpn_endpoint_group,
            vpn_endpoint_group.VpnEndpointGroup,
        )


class TestNetworkVpnSiteConnection(TestNetworkProxy):
    def test_ipsec_site_connection_create_attrs(self):
        self.verify_create(
            self.proxy.create_vpn_ipsec_site_connection,
            vpn_ipsec_site_connection.VpnIPSecSiteConnection,
        )

    def test_ipsec_site_connection_delete(self):
        self.verify_delete(
            self.proxy.delete_vpn_ipsec_site_connection,
            vpn_ipsec_site_connection.VpnIPSecSiteConnection,
            False,
        )

    def test_ipsec_site_connection_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_vpn_ipsec_site_connection,
            vpn_ipsec_site_connection.VpnIPSecSiteConnection,
            True,
        )

    def test_ipsec_site_connection_find(self):
        self.verify_find(
            self.proxy.find_vpn_ipsec_site_connection,
            vpn_ipsec_site_connection.VpnIPSecSiteConnection,
        )

    def test_ipsec_site_connection_get(self):
        self.verify_get(
            self.proxy.get_vpn_ipsec_site_connection,
            vpn_ipsec_site_connection.VpnIPSecSiteConnection,
        )

    def test_ipsec_site_connections(self):
        self.verify_list(
            self.proxy.vpn_ipsec_site_connections,
            vpn_ipsec_site_connection.VpnIPSecSiteConnection,
        )

    def test_ipsec_site_connection_update(self):
        self.verify_update(
            self.proxy.update_vpn_ipsec_site_connection,
            vpn_ipsec_site_connection.VpnIPSecSiteConnection,
        )


class TestNetworkVpnIkePolicy(TestNetworkProxy):
    def test_ike_policy_create_attrs(self):
        self.verify_create(
            self.proxy.create_vpn_ike_policy, vpn_ike_policy.VpnIkePolicy
        )

    def test_ike_policy_delete(self):
        self.verify_delete(
            self.proxy.delete_vpn_ike_policy,
            vpn_ike_policy.VpnIkePolicy,
            False,
        )

    def test_ike_policy_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_vpn_ike_policy, vpn_ike_policy.VpnIkePolicy, True
        )

    def test_ike_policy_find(self):
        self.verify_find(
            self.proxy.find_vpn_ike_policy, vpn_ike_policy.VpnIkePolicy
        )

    def test_ike_policy_get(self):
        self.verify_get(
            self.proxy.get_vpn_ike_policy, vpn_ike_policy.VpnIkePolicy
        )

    def test_ike_policies(self):
        self.verify_list(
            self.proxy.vpn_ike_policies, vpn_ike_policy.VpnIkePolicy
        )

    def test_ike_policy_update(self):
        self.verify_update(
            self.proxy.update_vpn_ike_policy, vpn_ike_policy.VpnIkePolicy
        )


class TestNetworkVpnIpsecPolicy(TestNetworkProxy):
    def test_ipsec_policy_create_attrs(self):
        self.verify_create(
            self.proxy.create_vpn_ipsec_policy, vpn_ipsec_policy.VpnIpsecPolicy
        )

    def test_ipsec_policy_delete(self):
        self.verify_delete(
            self.proxy.delete_vpn_ipsec_policy,
            vpn_ipsec_policy.VpnIpsecPolicy,
            False,
        )

    def test_ipsec_policy_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_vpn_ipsec_policy,
            vpn_ipsec_policy.VpnIpsecPolicy,
            True,
        )

    def test_ipsec_policy_find(self):
        self.verify_find(
            self.proxy.find_vpn_ipsec_policy, vpn_ipsec_policy.VpnIpsecPolicy
        )

    def test_ipsec_policy_get(self):
        self.verify_get(
            self.proxy.get_vpn_ipsec_policy, vpn_ipsec_policy.VpnIpsecPolicy
        )

    def test_ipsec_policies(self):
        self.verify_list(
            self.proxy.vpn_ipsec_policies, vpn_ipsec_policy.VpnIpsecPolicy
        )

    def test_ipsec_policy_update(self):
        self.verify_update(
            self.proxy.update_vpn_ipsec_policy, vpn_ipsec_policy.VpnIpsecPolicy
        )


class TestNetworkVpnService(TestNetworkProxy):
    def test_vpn_service_create_attrs(self):
        self.verify_create(
            self.proxy.create_vpn_service, vpn_service.VpnService
        )

    def test_vpn_service_delete(self):
        self.verify_delete(
            self.proxy.delete_vpn_service, vpn_service.VpnService, False
        )

    def test_vpn_service_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_vpn_service, vpn_service.VpnService, True
        )

    def test_vpn_service_find(self):
        self.verify_find(self.proxy.find_vpn_service, vpn_service.VpnService)

    def test_vpn_service_get(self):
        self.verify_get(self.proxy.get_vpn_service, vpn_service.VpnService)

    def test_vpn_services(self):
        self.verify_list(self.proxy.vpn_services, vpn_service.VpnService)

    def test_vpn_service_update(self):
        self.verify_update(
            self.proxy.update_vpn_service, vpn_service.VpnService
        )


class TestNetworkServiceProvider(TestNetworkProxy):
    def test_service_provider(self):
        self.verify_list(
            self.proxy.service_providers, service_provider.ServiceProvider
        )


class TestNetworkAutoAllocatedTopology(TestNetworkProxy):
    def test_auto_allocated_topology_get(self):
        self.verify_get(
            self.proxy.get_auto_allocated_topology,
            auto_allocated_topology.AutoAllocatedTopology,
        )

    def test_auto_allocated_topology_delete(self):
        self.verify_delete(
            self.proxy.delete_auto_allocated_topology,
            auto_allocated_topology.AutoAllocatedTopology,
            False,
        )

    def test_auto_allocated_topology_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_auto_allocated_topology,
            auto_allocated_topology.AutoAllocatedTopology,
            True,
        )

    def test_validate_topology(self):
        self.verify_get(
            self.proxy.validate_auto_allocated_topology,
            auto_allocated_topology.ValidateTopology,
            method_args=[mock.sentinel.project_id],
            expected_args=[],
            expected_kwargs={
                "project": mock.sentinel.project_id,
                "requires_id": False,
            },
        )


class TestNetworkTags(TestNetworkProxy):
    def test_set_tags(self):
        x_network = network.Network.new(id='NETWORK_ID')
        self._verify(
            'openstack.network.v2.network.Network.set_tags',
            self.proxy.set_tags,
            method_args=[x_network, ['TAG1', 'TAG2']],
            expected_args=[self.proxy, ['TAG1', 'TAG2']],
            expected_result=mock.sentinel.result_set_tags,
        )

    @mock.patch('openstack.network.v2.network.Network.set_tags')
    def test_set_tags_resource_without_tag_suport(self, mock_set_tags):
        no_tag_resource = object()
        self.assertRaises(
            exceptions.InvalidRequest,
            self.proxy.set_tags,
            no_tag_resource,
            ['TAG1', 'TAG2'],
        )
        self.assertEqual(0, mock_set_tags.call_count)


class TestNetworkFloatingIp(TestNetworkProxy):
    def test_create_floating_ip_port_forwarding(self):
        self.verify_create(
            self.proxy.create_floating_ip_port_forwarding,
            port_forwarding.PortForwarding,
            method_kwargs={'floating_ip': FIP_ID},
            expected_kwargs={'floatingip_id': FIP_ID},
        )

    def test_delete_floating_ip_port_forwarding(self):
        self.verify_delete(
            self.proxy.delete_floating_ip_port_forwarding,
            port_forwarding.PortForwarding,
            ignore_missing=False,
            method_args=[FIP_ID, "resource_or_id"],
            expected_args=["resource_or_id"],
            expected_kwargs={'floatingip_id': FIP_ID},
        )

    def test_delete_floating_ip_port_forwarding_ignore(self):
        self.verify_delete(
            self.proxy.delete_floating_ip_port_forwarding,
            port_forwarding.PortForwarding,
            ignore_missing=True,
            method_args=[FIP_ID, "resource_or_id"],
            expected_args=["resource_or_id"],
            expected_kwargs={'floatingip_id': FIP_ID},
        )

    def test_find_floating_ip_port_forwarding(self):
        fip = floating_ip.FloatingIP.new(id=FIP_ID)
        self._verify(
            'openstack.proxy.Proxy._find',
            self.proxy.find_floating_ip_port_forwarding,
            method_args=[fip, 'port_forwarding_id'],
            expected_args=[
                port_forwarding.PortForwarding,
                'port_forwarding_id',
            ],
            expected_kwargs={'ignore_missing': True, 'floatingip_id': FIP_ID},
        )

    def test_get_floating_ip_port_forwarding(self):
        fip = floating_ip.FloatingIP.new(id=FIP_ID)
        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_floating_ip_port_forwarding,
            method_args=[fip, 'port_forwarding_id'],
            expected_args=[
                port_forwarding.PortForwarding,
                'port_forwarding_id',
            ],
            expected_kwargs={'floatingip_id': FIP_ID},
        )

    def test_floating_ip_port_forwardings(self):
        self.verify_list(
            self.proxy.floating_ip_port_forwardings,
            port_forwarding.PortForwarding,
            method_kwargs={'floating_ip': FIP_ID},
            expected_kwargs={'floatingip_id': FIP_ID},
        )

    def test_update_floating_ip_port_forwarding(self):
        fip = floating_ip.FloatingIP.new(id=FIP_ID)
        self._verify(
            'openstack.network.v2._proxy.Proxy._update',
            self.proxy.update_floating_ip_port_forwarding,
            method_args=[fip, 'port_forwarding_id'],
            method_kwargs={'foo': 'bar'},
            expected_args=[
                port_forwarding.PortForwarding,
                'port_forwarding_id',
            ],
            expected_kwargs={'floatingip_id': FIP_ID, 'foo': 'bar'},
        )

    def test_create_l3_conntrack_helper(self):
        self.verify_create(
            self.proxy.create_conntrack_helper,
            l3_conntrack_helper.ConntrackHelper,
            method_kwargs={'router': ROUTER_ID},
            expected_kwargs={'router_id': ROUTER_ID},
        )

    def test_delete_l3_conntrack_helper(self):
        r = router.Router.new(id=ROUTER_ID)
        self.verify_delete(
            self.proxy.delete_conntrack_helper,
            l3_conntrack_helper.ConntrackHelper,
            ignore_missing=False,
            method_args=['resource_or_id', r],
            expected_args=['resource_or_id'],
            expected_kwargs={'router_id': ROUTER_ID},
        )

    def test_delete_l3_conntrack_helper_ignore(self):
        r = router.Router.new(id=ROUTER_ID)
        self.verify_delete(
            self.proxy.delete_conntrack_helper,
            l3_conntrack_helper.ConntrackHelper,
            ignore_missing=True,
            method_args=['resource_or_id', r],
            expected_args=['resource_or_id'],
            expected_kwargs={'router_id': ROUTER_ID},
        )

    def test_get_l3_conntrack_helper(self):
        r = router.Router.new(id=ROUTER_ID)
        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_conntrack_helper,
            method_args=['conntrack_helper_id', r],
            expected_args=[
                l3_conntrack_helper.ConntrackHelper,
                'conntrack_helper_id',
            ],
            expected_kwargs={'router_id': ROUTER_ID},
        )

    def test_l3_conntrack_helpers(self):
        self.verify_list(
            self.proxy.conntrack_helpers,
            l3_conntrack_helper.ConntrackHelper,
            method_args=[ROUTER_ID],
            expected_args=[],
            expected_kwargs={'router_id': ROUTER_ID},
        )

    def test_update_l3_conntrack_helper(self):
        r = router.Router.new(id=ROUTER_ID)
        self._verify(
            'openstack.network.v2._proxy.Proxy._update',
            self.proxy.update_conntrack_helper,
            method_args=['conntrack_helper_id', r],
            method_kwargs={'foo': 'bar'},
            expected_args=[
                l3_conntrack_helper.ConntrackHelper,
                'conntrack_helper_id',
            ],
            expected_kwargs={'router_id': ROUTER_ID, 'foo': 'bar'},
        )


class TestNetworkNDPProxy(TestNetworkProxy):
    def test_ndp_proxy_create_attrs(self):
        self.verify_create(self.proxy.create_ndp_proxy, ndp_proxy.NDPProxy)

    def test_ndp_proxy_delete(self):
        self.verify_delete(
            self.proxy.delete_ndp_proxy, ndp_proxy.NDPProxy, False
        )

    def test_ndp_proxy_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_ndp_proxy, ndp_proxy.NDPProxy, True
        )

    def test_ndp_proxy_find(self):
        self.verify_find(self.proxy.find_ndp_proxy, ndp_proxy.NDPProxy)

    def test_ndp_proxy_get(self):
        self.verify_get(self.proxy.get_ndp_proxy, ndp_proxy.NDPProxy)

    def test_ndp_proxies(self):
        self.verify_list(self.proxy.ndp_proxies, ndp_proxy.NDPProxy)

    def test_ndp_proxy_update(self):
        self.verify_update(self.proxy.update_ndp_proxy, ndp_proxy.NDPProxy)


class TestNetworkBGP(TestNetworkProxy):
    def test_bgp_speaker_create(self):
        self.verify_create(
            self.proxy.create_bgp_speaker, bgp_speaker.BgpSpeaker
        )

    def test_bgp_speaker_delete(self):
        self.verify_delete(
            self.proxy.delete_bgp_speaker, bgp_speaker.BgpSpeaker, False
        )

    def test_bgp_speaker_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_bgp_speaker, bgp_speaker.BgpSpeaker, True
        )

    def test_bgp_speaker_find(self):
        self.verify_find(self.proxy.find_bgp_speaker, bgp_speaker.BgpSpeaker)

    def test_bgp_speaker_get(self):
        self.verify_get(self.proxy.get_bgp_speaker, bgp_speaker.BgpSpeaker)

    def test_bgp_speakers(self):
        self.verify_list(self.proxy.bgp_speakers, bgp_speaker.BgpSpeaker)

    def test_bgp_speaker_update(self):
        self.verify_update(
            self.proxy.update_bgp_speaker, bgp_speaker.BgpSpeaker
        )

    def test_bgp_peer_create(self):
        self.verify_create(self.proxy.create_bgp_peer, bgp_peer.BgpPeer)

    def test_bgp_peer_delete(self):
        self.verify_delete(self.proxy.delete_bgp_peer, bgp_peer.BgpPeer, False)

    def test_bgp_peer_delete_ignore(self):
        self.verify_delete(self.proxy.delete_bgp_peer, bgp_peer.BgpPeer, True)

    def test_bgp_peer_find(self):
        self.verify_find(self.proxy.find_bgp_peer, bgp_peer.BgpPeer)

    def test_bgp_peer_get(self):
        self.verify_get(self.proxy.get_bgp_peer, bgp_peer.BgpPeer)

    def test_bgp_peers(self):
        self.verify_list(self.proxy.bgp_peers, bgp_peer.BgpPeer)

    def test_bgp_peer_update(self):
        self.verify_update(self.proxy.update_bgp_peer, bgp_peer.BgpPeer)


class TestNetworkBGPVPN(TestNetworkProxy):
    NETWORK_ASSOCIATION = 'net-assoc-id' + uuid.uuid4().hex
    PORT_ASSOCIATION = 'port-assoc-id' + uuid.uuid4().hex
    ROUTER_ASSOCIATION = 'router-assoc-id' + uuid.uuid4().hex

    def test_bgpvpn_create(self):
        self.verify_create(self.proxy.create_bgpvpn, bgpvpn.BgpVpn)

    def test_bgpvpn_delete(self):
        self.verify_delete(self.proxy.delete_bgpvpn, bgpvpn.BgpVpn, False)

    def test_bgpvpn_delete_ignore(self):
        self.verify_delete(self.proxy.delete_bgpvpn, bgpvpn.BgpVpn, True)

    def test_bgpvpn_find(self):
        self.verify_find(self.proxy.find_bgpvpn, bgpvpn.BgpVpn)

    def test_bgpvpn_get(self):
        self.verify_get(self.proxy.get_bgpvpn, bgpvpn.BgpVpn)

    def test_bgpvpns(self):
        self.verify_list(self.proxy.bgpvpns, bgpvpn.BgpVpn)

    def test_bgpvpn_update(self):
        self.verify_update(self.proxy.update_bgpvpn, bgpvpn.BgpVpn)

    def test_bgpvpn_network_association_create(self):
        self.verify_create(
            self.proxy.create_bgpvpn_network_association,
            bgpvpn_network_association.BgpVpnNetworkAssociation,
            method_kwargs={'bgpvpn': BGPVPN_ID},
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_network_association_delete(self):
        self.verify_delete(
            self.proxy.delete_bgpvpn_network_association,
            bgpvpn_network_association.BgpVpnNetworkAssociation,
            False,
            method_args=[BGPVPN_ID, self.NETWORK_ASSOCIATION],
            expected_args=[self.NETWORK_ASSOCIATION],
            expected_kwargs={'ignore_missing': False, 'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_network_association_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_bgpvpn_network_association,
            bgpvpn_network_association.BgpVpnNetworkAssociation,
            True,
            method_args=[BGPVPN_ID, self.NETWORK_ASSOCIATION],
            expected_args=[self.NETWORK_ASSOCIATION],
            expected_kwargs={'ignore_missing': True, 'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_network_association_get(self):
        self.verify_get(
            self.proxy.get_bgpvpn_network_association,
            bgpvpn_network_association.BgpVpnNetworkAssociation,
            method_args=[BGPVPN_ID, self.NETWORK_ASSOCIATION],
            expected_args=[self.NETWORK_ASSOCIATION],
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_network_associations(self):
        self.verify_list(
            self.proxy.bgpvpn_network_associations,
            bgpvpn_network_association.BgpVpnNetworkAssociation,
            method_args=[
                BGPVPN_ID,
            ],
            expected_args=[],
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_port_association_create(self):
        self.verify_create(
            self.proxy.create_bgpvpn_port_association,
            bgpvpn_port_association.BgpVpnPortAssociation,
            method_kwargs={'bgpvpn': BGPVPN_ID},
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_port_association_delete(self):
        self.verify_delete(
            self.proxy.delete_bgpvpn_port_association,
            bgpvpn_port_association.BgpVpnPortAssociation,
            False,
            method_args=[BGPVPN_ID, self.PORT_ASSOCIATION],
            expected_args=[self.PORT_ASSOCIATION],
            expected_kwargs={'ignore_missing': False, 'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_port_association_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_bgpvpn_port_association,
            bgpvpn_port_association.BgpVpnPortAssociation,
            True,
            method_args=[BGPVPN_ID, self.PORT_ASSOCIATION],
            expected_args=[self.PORT_ASSOCIATION],
            expected_kwargs={'ignore_missing': True, 'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_port_association_find(self):
        self.verify_find(
            self.proxy.find_bgpvpn_port_association,
            bgpvpn_port_association.BgpVpnPortAssociation,
            method_args=[BGPVPN_ID],
            expected_args=['resource_name'],
            method_kwargs={'ignore_missing': True},
            expected_kwargs={'ignore_missing': True, 'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_port_association_get(self):
        self.verify_get(
            self.proxy.get_bgpvpn_port_association,
            bgpvpn_port_association.BgpVpnPortAssociation,
            method_args=[BGPVPN_ID, self.PORT_ASSOCIATION],
            expected_args=[self.PORT_ASSOCIATION],
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_port_associations(self):
        self.verify_list(
            self.proxy.bgpvpn_port_associations,
            bgpvpn_port_association.BgpVpnPortAssociation,
            method_args=[
                BGPVPN_ID,
            ],
            expected_args=[],
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_port_association_update(self):
        self.verify_update(
            self.proxy.update_bgpvpn_port_association,
            bgpvpn_port_association.BgpVpnPortAssociation,
            method_args=[BGPVPN_ID, self.PORT_ASSOCIATION],
            method_kwargs={},
            expected_args=[self.PORT_ASSOCIATION],
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_router_association_create(self):
        self.verify_create(
            self.proxy.create_bgpvpn_router_association,
            bgpvpn_router_association.BgpVpnRouterAssociation,
            method_kwargs={'bgpvpn': BGPVPN_ID},
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_router_association_delete(self):
        self.verify_delete(
            self.proxy.delete_bgpvpn_router_association,
            bgpvpn_router_association.BgpVpnRouterAssociation,
            False,
            method_args=[BGPVPN_ID, self.ROUTER_ASSOCIATION],
            expected_args=[self.ROUTER_ASSOCIATION],
            expected_kwargs={'ignore_missing': False, 'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_router_association_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_bgpvpn_router_association,
            bgpvpn_router_association.BgpVpnRouterAssociation,
            True,
            method_args=[BGPVPN_ID, self.ROUTER_ASSOCIATION],
            expected_args=[self.ROUTER_ASSOCIATION],
            expected_kwargs={'ignore_missing': True, 'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_router_association_get(self):
        self.verify_get(
            self.proxy.get_bgpvpn_router_association,
            bgpvpn_router_association.BgpVpnRouterAssociation,
            method_args=[BGPVPN_ID, self.ROUTER_ASSOCIATION],
            expected_args=[self.ROUTER_ASSOCIATION],
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_router_associations(self):
        self.verify_list(
            self.proxy.bgpvpn_router_associations,
            bgpvpn_router_association.BgpVpnRouterAssociation,
            method_args=[
                BGPVPN_ID,
            ],
            expected_args=[],
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )

    def test_bgpvpn_router_association_update(self):
        self.verify_update(
            self.proxy.update_bgpvpn_router_association,
            bgpvpn_router_association.BgpVpnRouterAssociation,
            method_args=[BGPVPN_ID, self.ROUTER_ASSOCIATION],
            method_kwargs={},
            expected_args=[self.ROUTER_ASSOCIATION],
            expected_kwargs={'bgpvpn_id': BGPVPN_ID},
        )


class TestNetworkTapMirror(TestNetworkProxy):
    def test_create_tap_mirror(self):
        self.verify_create(self.proxy.create_tap_mirror, tap_mirror.TapMirror)

    def test_delete_tap_mirror(self):
        self.verify_delete(
            self.proxy.delete_tap_mirror, tap_mirror.TapMirror, False
        )

    def test_delete_tap_mirror_ignore(self):
        self.verify_delete(
            self.proxy.delete_tap_mirror, tap_mirror.TapMirror, True
        )

    def test_find_tap_mirror(self):
        self.verify_find(self.proxy.find_tap_mirror, tap_mirror.TapMirror)

    def test_get_tap_mirror(self):
        self.verify_get(self.proxy.get_tap_mirror, tap_mirror.TapMirror)

    def test_tap_mirrors(self):
        self.verify_list(self.proxy.tap_mirrors, tap_mirror.TapMirror)

    def test_update_tap_mirror(self):
        self.verify_update(self.proxy.update_tap_mirror, tap_mirror.TapMirror)


class TestNetworkPortBinding(TestNetworkProxy):
    @mock.patch.object(proxy_base.Proxy, '_get')
    def test_create_port_binding(self, mock_get):
        res_port = port.Port.new(id=PORT_ID)
        mock_get.return_value = res_port

        self.verify_create(
            self.proxy.create_port_binding,
            port_binding.PortBinding,
            method_kwargs={'port': PORT_ID},
            expected_kwargs={'port_id': PORT_ID},
        )

    @mock.patch('openstack.network.v2._proxy.Proxy.activate_port_binding')
    def test_activate_port_binding(self, activate_binding):
        data = mock.sentinel
        self.proxy.activate_port_binding(port_binding.PortBinding, data)
        activate_binding.assert_called_once_with(
            port_binding.PortBinding, data
        )

    @mock.patch.object(proxy_base.Proxy, '_get')
    def test_port_bindings(self, mock_get):
        res_port = port.Port.new(id=PORT_ID)
        mock_get.return_value = res_port

        self.verify_list(
            self.proxy.port_bindings,
            port_binding.PortBinding,
            method_kwargs={'port': PORT_ID},
            expected_kwargs={'port_id': PORT_ID},
        )

    @mock.patch('openstack.network.v2._proxy.Proxy.delete_port_binding')
    @mock.patch.object(proxy_base.Proxy, '_get')
    def test_delete_port_binding(self, mock_get, delete_port_binding):
        res_port = port.Port.new(id=PORT_ID)
        mock_get.return_value = res_port
        data = mock.sentinel

        self.proxy.delete_port_binding(port_binding.PortBinding, data)
        delete_port_binding.assert_called_once_with(
            port_binding.PortBinding, data
        )
