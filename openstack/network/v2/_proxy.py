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
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def find_extension(self, name_or_id):
        return extension.Extension.find(self.session, name_or_id)

    def list_extensions(self):
        return extension.Extension.list(self.session)

    def create_ip(self, **data):
        return floating_ip.FloatingIP(data).create(self.session)

    def delete_ip(self, value, ignore_missing=True):
        """Delete a floating ip

        :param value: The value can be either the ID of a floating ip or a
               :class:`~openstack.network.v2.floating_ip.FloatingIP` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the floating ip does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent ip.

        :returns: ``None``
        """
        self._delete(floating_ip.FloatingIP, value, ignore_missing)

    def find_available_ip(self):
        return floating_ip.FloatingIP.find_available(self.session)

    def find_ip(self, name_or_id):
        return floating_ip.FloatingIP.find(self.session, name_or_id)

    def get_ip(self, **data):
        return floating_ip.FloatingIP(**data).get(self.session)

    def list_ips(self, **params):
        return floating_ip.FloatingIP.list(self.session, **params)

    def update_ip(self, value, **attrs):
        """Update a ip

        :param value: Either the id of a ip or a
                      :class:`~openstack.compute.v2.floating_ip.FloatingIP`
                      instance.
        :attrs kwargs: The attributes to update on the ip represented
                       by ``value``.

        :returns: The updated ip
        :rtype: :class:`~openstack.compute.v2.floating_ip.FloatingIP`
        """
        return self._update(floating_ip.FloatingIP, value, **attrs)

    def create_health_monitor(self, **data):
        return health_monitor.HealthMonitor(data).create(self.session)

        health_monitor.HealthMonitor(data).delete(self.session)

    def delete_health_monitor(self, value, ignore_missing=True):
        """Delete a health monitor

        :param value: The value can be either the ID of a health monitor or a
               :class:`~openstack.network.v2.health_monitor.HealthMonitor`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the health monitor does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent health monitor.

        :returns: ``None``
        """
        self._delete(health_monitor.HealthMonitor, value, ignore_missing)

    def find_health_monitor(self, name_or_id):
        return health_monitor.HealthMonitor.find(self.session, name_or_id)

    def get_health_monitor(self, **data):
        return health_monitor.HealthMonitor(data).get(self.session)

    def list_health_monitors(self):
        return health_monitor.HealthMonitor.list(self.session)

    def update_health_monitor(self, value, **attrs):
        """Update a health monitor

        :param value: Either the id of a health monitor or a
                      :class:`~openstack.compute.v2.health_monitor.
                      HealthMonitor` instance.
        :attrs kwargs: The attributes to update on the health monitor
                       represented by ``value``.

        :returns: The updated health monitor
        :rtype: :class:`~openstack.compute.v2.health_monitor.HealthMonitor`
        """
        return self._update(health_monitor.HealthMonitor, value, **attrs)

    def create_listener(self, **data):
        return listener.Listener(data).create(self.session)

    def delete_listener(self, value, ignore_missing=True):
        """Delete a listener

        :param value: The value can be either the ID of a listner or a
               :class:`~openstack.network.v2.listener.Listener` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the listner does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent listener.

        :returns: ``None``
        """
        self._delete(listener.Listener, value, ignore_missing)

    def find_listener(self, name_or_id):
        return listener.Listener.find(self.session, name_or_id)

    def get_listener(self, **data):
        return listener.Listener(data).get(self.session)

    def list_listeners(self):
        return listener.Listener.list(self.session)

    def update_listener(self, value, **attrs):
        """Update a listener

        :param value: Either the id of a listener or a
                      :class:`~openstack.compute.v2.listener.Listener`
                      instance.
        :attrs kwargs: The attributes to update on the listener represented
                       by ``value``.

        :returns: The updated listener
        :rtype: :class:`~openstack.compute.v2.listener.Listener`
        """
        return self._update(listener.Listener, value, **attrs)

    def create_load_balancer(self, **data):
        return load_balancer.LoadBalancer(data).create(self.session)

    def delete_load_balancer(self, value, ignore_missing=True):
        """Delete a load balancer

        :param value: The value can be either the ID of a load balancer or a
               :class:`~openstack.network.v2.load_balancer.LoadBalancer`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the load balancer does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent load balancer.

        :returns: ``None``
        """
        self._delete(load_balancer.LoadBalancer, value, ignore_missing)

    def find_load_balancer(self, name_or_id):
        return load_balancer.LoadBalancer.find(self.session, name_or_id)

    def get_load_balancer(self, **data):
        return load_balancer.LoadBalancer(data).get(self.session)

    def list_load_balancers(self):
        return load_balancer.LoadBalancer.list(self.session)

    def update_load_balancer(self, value, **attrs):
        """Update a load balancer

        :param value: Either the id of a load balancer or a
                      :class:`~openstack.compute.v2.load_balancer.LoadBalancer`
                      instance.
        :attrs kwargs: The attributes to update on the load balancer
                       represented by ``value``.

        :returns: The updated load balancer
        :rtype: :class:`~openstack.compute.v2.load_balancer.LoadBalancer`
        """
        return self._update(load_balancer.LoadBalancer, value, **attrs)

    def create_metering_label(self, **data):
        return metering_label.MeteringLabel(data).create(self.session)

    def delete_metering_label(self, value, ignore_missing=True):
        """Delete a metering label

        :param value: The value can be either the ID of a metering label or a
               :class:`~openstack.network.v2.metering_label.MeteringLabel`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the metering label does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent metering label.

        :returns: ``None``
        """
        self._delete(metering_label.MeteringLabel, value, ignore_missing)

    def find_metering_label(self, name_or_id):
        return metering_label.MeteringLabel.find(self.session, name_or_id)

    def get_metering_label(self, **data):
        return metering_label.MeteringLabel(data).get(self.session)

    def list_metering_labels(self):
        return metering_label.MeteringLabel.list(self.session)

    def update_metering_label(self, value, **attrs):
        """Update a metering label

        :param value: Either the id of a metering label or a
                      :class:`~openstack.compute.v2.metering_label.
                      MeteringLabel` instance.
        :attrs kwargs: The attributes to update on the metering label
                       represented by ``value``.

        :returns: The updated metering label
        :rtype: :class:`~openstack.compute.v2.metering_label.MeteringLabel`
        """
        return self._update(metering_label.MeteringLabel, value, **attrs)

    def create_metering_label_rule(self, **data):
        return metering_label_rule.MeteringLabelRule(data).create(self.session)

    def delete_metering_label_rule(self, value, ignore_missing=True):
        """Delete a metering label rule

        :param value: The value can be either the ID of a metering label rule
        or a
        :class:`~openstack.network.v2.metering_label_rule.MeteringLabelRule`
        instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the metering label rule does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent metering label rule.

        :returns: ``None``
        """
        self._delete(metering_label_rule.MeteringLabelRule,
                     value, ignore_missing)

    def find_metering_label_rule(self, name_or_id):
        return metering_label_rule.MeteringLabelRule.find(self.session,
                                                          name_or_id)

    def get_metering_label_rule(self, **data):
        return metering_label_rule.MeteringLabelRule(data).get(self.session)

    def list_metering_label_rules(self):
        return metering_label_rule.MeteringLabelRule.list(self.session)

    def update_metering_label_rule(self, value, **attrs):
        """Update a metering label rule

        :param value: Either the id of a metering label rule or a
                      :class:`~openstack.compute.v2.metering_label_rule.
                      MeteringLabelRule` instance.
        :attrs kwargs: The attributes to update on the metering label rule
                       represented by ``value``.

        :returns: The updated metering label rule
        :rtype: :class:`~openstack.compute.v2.metering_label_rule.
                       MeteringLabelRule`
        """
        return self._update(metering_label_rule.MeteringLabelRule, value,
                            **attrs)

    def create_network(self, **data):
        return network.Network(data).create(self.session)

    def delete_network(self, value, ignore_missing=True):
        """Delete a network

        :param value: The value can be either the ID of a network or a
                      :class:`~openstack.network.v2.network.Network` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the network does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent network.

        :returns: ``None``
        """
        self._delete(network.Network, value, ignore_missing)

    def find_network(self, name_or_id):
        return network.Network.find(self.session, name_or_id)

    def get_network(self, **data):
        return network.Network(data).get(self.session)

    def list_networks(self, **params):
        return network.Network.list(self.session, **params)

    def update_network(self, value, **attrs):
        """Update a network

        :param value: Either the id of a network or a
                      :class:`~openstack.compute.v2.network.Network` instance.
        :attrs kwargs: The attributes to update on the network represented
                       by ``value``.

        :returns: The updated network
        :rtype: :class:`~openstack.compute.v2.network.Network`
        """
        return self._update(network.Network, value, **attrs)

    def create_pool(self, **data):
        return pool.Pool(data).create(self.session)

    def delete_pool(self, value, ignore_missing=True):
        """Delete a pool

        :param value: The value can be either the ID of a pool or a
                      :class:`~openstack.network.v2.pool.Pool` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the pool does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent pool.

        :returns: ``None``
        """
        self._delete(pool.Pool, value, ignore_missing)

    def find_pool(self, name_or_id):
        return pool.Pool.find(self.session, name_or_id)

    def get_pool(self, **data):
        return pool.Pool(data).get(self.session)

    def list_pools(self):
        return pool.Pool.list(self.session)

    def update_pool(self, value, **attrs):
        """Update a pool

        :param value: Either the id of a pool or a
                      :class:`~openstack.compute.v2.pool.Pool` instance.
        :attrs kwargs: The attributes to update on the pool represented
                       by ``value``.

        :returns: The updated pool
        :rtype: :class:`~openstack.compute.v2.pool.Pool`
        """
        return self._update(pool.Pool, value, **attrs)

    def create_pool_member(self, **data):
        return pool_member.PoolMember(data).create(self.session)

    def delete_pool_member(self, value, ignore_missing=True):
        """Delete a pool member

        :param value: The value can be either the ID of a pool member or a
                      :class:`~openstack.network.v2.pool_member.PoolMember`
                      instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the pool member does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent pool member.

        :returns: ``None``
        """
        self._delete(pool_member.PoolMember, value, ignore_missing)

    def find_pool_member(self, name_or_id):
        return pool_member.PoolMember.find(self.session, name_or_id)

    def get_pool_member(self, **data):
        return pool_member.PoolMember(data).get(self.session)

    def list_pool_members(self):
        return pool_member.PoolMember.list(self.session)

    def update_pool_member(self, value, **attrs):
        """Update a pool member

        :param value: Either the id of a pool member or a
                      :class:`~openstack.compute.v2.pool_member.PoolMember`
                      instance.
        :attrs kwargs: The attributes to update on the pool member represented
                       by ``value``.

        :returns: The updated pool member
        :rtype: :class:`~openstack.compute.v2.pool_member.PoolMember`
        """
        return self._update(pool_member.PoolMember, value, **attrs)

    def create_port(self, **data):
        return port.Port(data).create(self.session)

    def delete_port(self, value, ignore_missing=True):
        """Delete a port

        :param value: The value can be either the ID of a port or a
                      :class:`~openstack.network.v2.port.Port` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the port does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent port.

        :returns: ``None``
        """
        self._delete(port.Port, value, ignore_missing)

    def find_port(self, name_or_id):
        return port.Port.find(self.session, name_or_id)

    def get_port(self, **data):
        return port.Port(data).get(self.session)

    def list_ports(self, **params):
        return port.Port.list(self.session, **params)

    def update_port(self, value, **attrs):
        """Update a port

        :param value: Either the id of a port or a
                      :class:`~openstack.compute.v2.port.Port` instance.
        :attrs kwargs: The attributes to update on the port represented
                       by ``value``.

        :returns: The updated port
        :rtype: :class:`~openstack.compute.v2.port.Port`
        """
        return self._update(port.Port, value, **attrs)

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

    def delete_router(self, value, ignore_missing=True):
        """Delete a router

        :param value: The value can be either the ID of a router or a
                      :class:`~openstack.network.v2.router.Router` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the router does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent router.

        :returns: ``None``
        """
        self._delete(router.Router, value, ignore_missing)

    def find_router(self, name_or_id):
        return router.Router.find(self.session, name_or_id)

    def get_router(self, **data):
        return router.Router(**data).get(self.session)

    def list_routers(self, **params):
        return router.Router.list(self.session, **params)

    def update_router(self, value, **attrs):
        """Update a router

        :param value: Either the id of a router or a
                      :class:`~openstack.compute.v2.router.Router` instance.
        :attrs kwargs: The attributes to update on the router represented
                       by ``value``.

        :returns: The updated router
        :rtype: :class:`~openstack.compute.v2.router.Router`
        """
        return self._update(router.Router, value, **attrs)

    def router_add_interface(self, router, subnet_id):
        router.add_interface(self.session, subnet_id)

    def router_remove_interface(self, router, subnet_id):
        router.remove_interface(self.session, subnet_id)

    def create_security_group(self, **data):
        return security_group.SecurityGroup(data).create(self.session)

    def delete_security_group(self, value, ignore_missing=True):
        """Delete a security group

        :param value: The value can be either the ID of a security group or a
               :class:`~openstack.network.v2.security_group.SecurityGroup`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the security group does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent security group.

        :returns: ``None``
        """
        self._delete(security_group.SecurityGroup, value, ignore_missing)

    def find_security_group(self, name_or_id):
        return security_group.SecurityGroup.find(self.session, name_or_id)

    def get_security_group(self, **data):
        return security_group.SecurityGroup(**data).get(self.session)

    def list_security_groups(self, **params):
        return security_group.SecurityGroup.list(self.session, **params)

    def update_security_group(self, value, **attrs):
        """Update a security group

        :param value: Either the id of a security group or a
                      :class:`~openstack.compute.v2.security_group.
                              SecurityGroup`
                      instance.
        :attrs kwargs: The attributes to update on the security group
                       represented by ``value``.

        :returns: The updated security group
        :rtype: :class:`~openstack.compute.v2.security_group.SecurityGroup`
        """
        return self._update(security_group.SecurityGroup, value, **attrs)

    def security_group_open_port(self, sgid, port, protocol='tcp'):
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': protocol,
            'port_range_max': port,
            'port_range_min': port,
            'security_group_id': sgid,
            'ethertype': 'IPv4'
        }
        return self.create_security_group_rule(**rule)

    def security_group_allow_ping(self, sgid):
        rule = {
            'direction': 'ingress',
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': 'icmp',
            'port_range_max': None,
            'port_range_min': None,
            'security_group_id': sgid,
            'ethertype': 'IPv4'
        }
        return self.create_security_group_rule(**rule)

    def create_security_group_rule(self, **data):
        obj = security_group_rule.SecurityGroupRule(data)
        return obj.create(self.session)

    def delete_security_group_rule(self, value, ignore_missing=True):
        """Delete a security group rule

        :param value: The value can be either the ID of a security group rule
        or a
        :class:`~openstack.network.v2.security_group_rule.SecurityGroupRule`
        instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the security group rule does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent security group rule.

        :returns: ``None``
        """
        self._delete(security_group_rule.SecurityGroupRule,
                     value, ignore_missing)

    def find_security_group_rule(self, name_or_id):
        return security_group_rule.SecurityGroupRule.find(self.session,
                                                          name_or_id)

    def get_security_group_rule(self, **data):
        obj = security_group_rule.SecurityGroupRule(**data)
        return obj.get(self.session)

    def list_security_group_rules(self, **params):
        return security_group_rule.SecurityGroupRule.list(self.session,
                                                          **params)

    def update_security_group_rule(self, value, **attrs):
        """Update a security group rule

        :param value: Either the id of a security group rule or a
                      :class:`~openstack.compute.v2.security_group_rule.
                      SecurityGroupRule` instance.
        :attrs kwargs: The attributes to update on the security group rule
                       represented by ``value``.

        :returns: The updated security group rule
        :rtype: :class:`~openstack.compute.v2.security_group_rule.
                        SecurityGroupRule`
        """
        return self._update(security_group_rule.SecurityGroupRule, value,
                            **attrs)

    def create_subnet(self, **data):
        return subnet.Subnet(data).create(self.session)

    def delete_subnet(self, value, ignore_missing=True):
        """Delete a subnet

        :param value: The value can be either the ID of a subnet or a
                      :class:`~openstack.network.v2.subnet.Subnet` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the subnet does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent subnet.

        :returns: ``None``
        """
        self._delete(subnet.Subnet, value, ignore_missing)

    def find_subnet(self, name_or_id):
        return subnet.Subnet.find(self.session, name_or_id)

    def get_subnet(self, **data):
        return subnet.Subnet(**data).get(self.session)

    def list_subnets(self, **params):
        return subnet.Subnet.list(self.session, **params)

    def update_subnet(self, value, **attrs):
        """Update a subnet

        :param value: Either the id of a subnet or a
                      :class:`~openstack.compute.v2.subnet.Subnet` instance.
        :attrs kwargs: The attributes to update on the subnet represented
                       by ``value``.

        :returns: The updated subnet
        :rtype: :class:`~openstack.compute.v2.subnet.Subnet`
        """
        return self._update(subnet.Subnet, value, **attrs)
