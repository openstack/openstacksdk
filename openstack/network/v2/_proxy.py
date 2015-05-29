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
        """Find a single extension

        :param name_or_id: The name or ID of a extension.
        :returns: One :class:`~openstack.compute.v2.extension.Extension`
                  or None
        """
        return extension.Extension.find(self.session, name_or_id)

    def extensions(self):
        """Return a generator of extensions

        :returns: A generator of extension objects
        :rtype: :class:`~openstack.network.v2.extension.Extension`
        """
        return self._list(extension.Extension)

    def create_ip(self, **attrs):
        """Create a new floating ip from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.floating_ip.FloatingIP`,
            comprised of the properties on the FloatingIP class.

        :returns: The results of floating ip creation
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._create(floating_ip.FloatingIP, **attrs)

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
        self._delete(floating_ip.FloatingIP, value,
                     ignore_missing=ignore_missing)

    def find_available_ip(self):
        """Find an available IP

        :returns: One :class:`~openstack.compute.v2.floating_ip.FloatingIP`
                  or None
        """
        return floating_ip.FloatingIP.find_available(self.session)

    def find_ip(self, name_or_id):
        """Find a single IP

        :param name_or_id: The name or ID of an IP.
        :returns: One :class:`~openstack.compute.v2.floating_ip.FloatingIP`
                  or None
        """
        return floating_ip.FloatingIP.find(self.session, name_or_id)

    def get_ip(self, value):
        """Get a single floating ip

        :param value: The value can be the ID of a floating ip or a
                      :class:`~openstack.network.v2.floating_ip.FloatingIP`
                      instance.

        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(floating_ip.FloatingIP, value)

    def ips(self):
        """Return a generator of ips

        :returns: A generator of floating IP objects
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._list(floating_ip.FloatingIP)

    def update_ip(self, value, **attrs):
        """Update a ip

        :param value: Either the id of a ip or a
                      :class:`~openstack.network.v2.floating_ip.FloatingIP`
                      instance.
        :attrs kwargs: The attributes to update on the ip represented
                       by ``value``.

        :returns: The updated ip
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._update(floating_ip.FloatingIP, value, **attrs)

    def create_health_monitor(self, **attrs):
        """Create a new health monitor from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.health_monitor.HealthMonitor`,
            comprised of the properties on the HealthMonitor class.

        :returns: The results of health monitor creation
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._create(health_monitor.HealthMonitor, **attrs)

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
        self._delete(health_monitor.HealthMonitor, value,
                     ignore_missing=ignore_missing)

    def find_health_monitor(self, name_or_id):
        """Find a single health monitor

        :param name_or_id: The name or ID of a health monitor.
        :returns: One :class:`~openstack.compute.v2.health_monitor.
                  HealthMonitor` or None
        """
        return health_monitor.HealthMonitor.find(self.session, name_or_id)

    def get_health_monitor(self, value):
        """Get a single health monitor

        :param value: The value can be the ID of a health monitor or a
               :class:`~openstack.network.v2.health_monitor.HealthMonitor`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(health_monitor.HealthMonitor, value)

    def health_monitors(self):
        """Return a generator of health monitors

        :returns: A generator of health monitor objects
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._list(health_monitor.HealthMonitor)

    def update_health_monitor(self, value, **attrs):
        """Update a health monitor

        :param value: Either the id of a health monitor or a
                      :class:`~openstack.network.v2.health_monitor.
                      HealthMonitor` instance.
        :attrs kwargs: The attributes to update on the health monitor
                       represented by ``value``.

        :returns: The updated health monitor
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._update(health_monitor.HealthMonitor, value, **attrs)

    def create_listener(self, **attrs):
        """Create a new listener from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.listener.Listener`,
                           comprised of the properties on the Listener class.

        :returns: The results of listener creation
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._create(listener.Listener, **attrs)

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
        self._delete(listener.Listener, value, ignore_missing=ignore_missing)

    def find_listener(self, name_or_id):
        """Find a single listener

        :param name_or_id: The name or ID of a listener.
        :returns: One :class:`~openstack.compute.v2.listener.Listener` or None
        """
        return listener.Listener.find(self.session, name_or_id)

    def get_listener(self, value):
        """Get a single listener

        :param value: The value can be the ID of a listener or a
               :class:`~openstack.network.v2.listener.Listener`
               instance.

        :returns: One :class:`~openstack.network.v2.listener.Listener`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(listener.Listener, value)

    def listeners(self):
        """Return a generator of listeners

        :returns: A generator of listener objects
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._list(listener.Listener)

    def update_listener(self, value, **attrs):
        """Update a listener

        :param value: Either the id of a listener or a
                      :class:`~openstack.network.v2.listener.Listener`
                      instance.
        :attrs kwargs: The attributes to update on the listener represented
                       by ``value``.

        :returns: The updated listener
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._update(listener.Listener, value, **attrs)

    def create_load_balancer(self, **attrs):
        """Create a new load balancer from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.load_balancer.LoadBalancer`,
            comprised of the properties on the LoadBalancer class.

        :returns: The results of load balancer creation
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._create(load_balancer.LoadBalancer, **attrs)

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
        self._delete(load_balancer.LoadBalancer, value,
                     ignore_missing=ignore_missing)

    def find_load_balancer(self, name_or_id):
        """Find a single load balancer

        :param name_or_id: The name or ID of a load balancer.
        :returns: One :class:`~openstack.compute.v2.load_balancer.LoadBalancer`
                  or None
        """
        return load_balancer.LoadBalancer.find(self.session, name_or_id)

    def get_load_balancer(self, value):
        """Get a single load balancer

        :param value: The value can be the ID of a load balancer or a
               :class:`~openstack.network.v2.load_balancer.LoadBalancer`
               instance.

        :returns: One :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(load_balancer.LoadBalancer, value)

    def load_balancers(self):
        """Return a generator of load balancers

        :returns: A generator of load balancer objects
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._list(load_balancer.LoadBalancer)

    def update_load_balancer(self, value, **attrs):
        """Update a load balancer

        :param value: Either the id of a load balancer or a
                      :class:`~openstack.network.v2.load_balancer.LoadBalancer`
                      instance.
        :attrs kwargs: The attributes to update on the load balancer
                       represented by ``value``.

        :returns: The updated load balancer
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._update(load_balancer.LoadBalancer, value, **attrs)

    def create_metering_label(self, **attrs):
        """Create a new metering label from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.metering_label.MeteringLabel`,
            comprised of the properties on the MeteringLabel class.

        :returns: The results of metering label creation
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._create(metering_label.MeteringLabel, **attrs)

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
        self._delete(metering_label.MeteringLabel, value,
                     ignore_missing=ignore_missing)

    def find_metering_label(self, name_or_id):
        """Find a single metering label

        :param name_or_id: The name or ID of a metering label.
        :returns: One :class:`~openstack.compute.v2.metering_label.
                  MeteringLabel` or None
        """
        return metering_label.MeteringLabel.find(self.session, name_or_id)

    def get_metering_label(self, value):
        """Get a single metering label

        :param value: The value can be the ID of a metering label or a
               :class:`~openstack.network.v2.metering_label.MeteringLabel`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.metering_label.MeteringLabel`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(metering_label.MeteringLabel, value)

    def metering_labels(self):
        """Return a generator of metering labels

        :returns: A generator of metering label objects
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._list(metering_label.MeteringLabel)

    def update_metering_label(self, value, **attrs):
        """Update a metering label

        :param value: Either the id of a metering label or a
                      :class:`~openstack.network.v2.metering_label.
                      MeteringLabel` instance.
        :attrs kwargs: The attributes to update on the metering label
                       represented by ``value``.

        :returns: The updated metering label
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._update(metering_label.MeteringLabel, value, **attrs)

    def create_metering_label_rule(self, **attrs):
        """Create a new metering label rule from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule`, comprised of the properties on
            the MeteringLabelRule class.

        :returns: The results of metering label rule creation
        :rtype: :class:`~openstack.network.v2.metering_label_rule.\
                MeteringLabelRule`
        """
        return self._create(metering_label_rule.MeteringLabelRule, **attrs)

    def delete_metering_label_rule(self, value, ignore_missing=True):
        """Delete a metering label rule

        :param value: The value can be either the ID of a metering label rule
            or a :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the metering label rule does not exist.  When set to ``True``,
            no exception will be set when attempting to delete a nonexistent
            metering label rule.

        :returns: ``None``
        """
        self._delete(metering_label_rule.MeteringLabelRule,
                     value, ignore_missing=ignore_missing)

    def find_metering_label_rule(self, name_or_id):
        """Find a single metering label rule

        :param name_or_id: The name or ID of a metering label rule.
        :returns: One :class:`~openstack.compute.v2.metering_label_rule.
                  MeteringLabelRule` or None
        """
        return metering_label_rule.MeteringLabelRule.find(self.session,
                                                          name_or_id)

    def get_metering_label_rule(self, value):
        """Get a single metering label rule

        :param value: The value can be the ID of a metering label rule or a
            :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule` instance.

        :returns: One
            :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(metering_label_rule.MeteringLabelRule, value)

    def metering_label_rules(self):
        """Return a generator of metering label rules

        :returns: A generator of metering label rule objects
        :rtype: :class:`~openstack.network.v2.metering_label_rule.
                MeteringLabelRule`
        """
        return self._list(metering_label_rule.MeteringLabelRule)

    def update_metering_label_rule(self, value, **attrs):
        """Update a metering label rule

        :param value: Either the id of a metering label rule or a
                      :class:`~openstack.network.v2.metering_label_rule.
                      MeteringLabelRule` instance.
        :attrs kwargs: The attributes to update on the metering label rule
                       represented by ``value``.

        :returns: The updated metering label rule
        :rtype: :class:`~openstack.network.v2.metering_label_rule.
                       MeteringLabelRule`
        """
        return self._update(metering_label_rule.MeteringLabelRule, value,
                            **attrs)

    def create_network(self, **attrs):
        """Create a new network from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.network.Network`,
                           comprised of the properties on the Network class.

        :returns: The results of network creation
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._create(network.Network, **attrs)

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
        self._delete(network.Network, value, ignore_missing=ignore_missing)

    def find_network(self, name_or_id):
        """Find a single network

        :param name_or_id: The name or ID of a network.
        :returns: One :class:`~openstack.compute.v2.network.Network` or None
        """
        return network.Network.find(self.session, name_or_id)

    def get_network(self, value):
        """Get a single network

        :param value: The value can be the ID of a network or a
                      :class:`~openstack.network.v2.network.Network` instance.

        :returns: One :class:`~openstack.network.v2.network.Network`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(network.Network, value)

    def networks(self):
        """Return a generator of networks

        :returns: A generator of network objects
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._list(network.Network)

    def update_network(self, value, **attrs):
        """Update a network

        :param value: Either the id of a network or a
                      :class:`~openstack.network.v2.network.Network` instance.
        :attrs kwargs: The attributes to update on the network represented
                       by ``value``.

        :returns: The updated network
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._update(network.Network, value, **attrs)

    def create_pool(self, **attrs):
        """Create a new pool from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.pool.Pool`,
                           comprised of the properties on the Pool class.

        :returns: The results of pool creation
        :rtype: :class:`~openstack.network.v2.pool.Pool`
        """
        return self._create(pool.Pool, **attrs)

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
        self._delete(pool.Pool, value, ignore_missing=ignore_missing)

    def find_pool(self, name_or_id):
        """Find a single pool

        :param name_or_id: The name or ID of a pool.
        :returns: One :class:`~openstack.compute.v2.pool.Pool` or None
        """
        return pool.Pool.find(self.session, name_or_id)

    def get_pool(self, value):
        """Get a single pool

        :param value: The value can be the ID of a pool or a
                      :class:`~openstack.network.v2.pool.Pool` instance.

        :returns: One :class:`~openstack.network.v2.pool.Pool`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(pool.Pool, value)

    def pools(self):
        """Return a generator of pools

        :returns: A generator of pool objects
        :rtype: :class:`~openstack.network.v2.pool.Pool`
        """
        return self._list(pool.Pool)

    def update_pool(self, value, **attrs):
        """Update a pool

        :param value: Either the id of a pool or a
                      :class:`~openstack.network.v2.pool.Pool` instance.
        :attrs kwargs: The attributes to update on the pool represented
                       by ``value``.

        :returns: The updated pool
        :rtype: :class:`~openstack.network.v2.pool.Pool`
        """
        return self._update(pool.Pool, value, **attrs)

    def create_pool_member(self, **attrs):
        """Create a new pool member from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.pool_member.PoolMember`,
            comprised of the properties on the PoolMember class.

        :returns: The results of pool member creation
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        return self._create(pool_member.PoolMember, **attrs)

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
        self._delete(pool_member.PoolMember, value,
                     ignore_missing=ignore_missing)

    def find_pool_member(self, name_or_id):
        """Find a single pool member

        :param name_or_id: The name or ID of a pool member.
        :returns: One :class:`~openstack.compute.v2.pool_member.PoolMember`
                  or None
        """
        return pool_member.PoolMember.find(self.session, name_or_id)

    def get_pool_member(self, value):
        """Get a single pool member

        :param value: The value can be the ID of a pool member or a
                      :class:`~openstack.network.v2.pool_member.PoolMember`
                      instance.

        :returns: One :class:`~openstack.network.v2.pool_member.PoolMember`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(pool_member.PoolMember, value)

    def pool_members(self):
        """Return a generator of pool members

        :returns: A generator of pool member objects
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        return self._list(pool_member.PoolMember)

    def update_pool_member(self, value, **attrs):
        """Update a pool member

        :param value: Either the id of a pool member or a
                      :class:`~openstack.network.v2.pool_member.PoolMember`
                      instance.
        :attrs kwargs: The attributes to update on the pool member represented
                       by ``value``.

        :returns: The updated pool member
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        return self._update(pool_member.PoolMember, value, **attrs)

    def create_port(self, **attrs):
        """Create a new port from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.port.Port`,
                           comprised of the properties on the Port class.

        :returns: The results of port creation
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._create(port.Port, **attrs)

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
        self._delete(port.Port, value, ignore_missing=ignore_missing)

    def find_port(self, name_or_id):
        """Find a single port

        :param name_or_id: The name or ID of a port.
        :returns: One :class:`~openstack.compute.v2.port.Port` or None
        """
        return port.Port.find(self.session, name_or_id)

    def get_port(self, value):
        """Get a single port

        :param value: The value can be the ID of a port or a
                      :class:`~openstack.network.v2.port.Port` instance.

        :returns: One :class:`~openstack.network.v2.port.Port`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(port.Port, value)

    def ports(self):
        """Return a generator of ports

        :returns: A generator of port objects
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._list(port.Port)

    def update_port(self, value, **attrs):
        """Update a port

        :param value: Either the id of a port or a
                      :class:`~openstack.network.v2.port.Port` instance.
        :attrs kwargs: The attributes to update on the port represented
                       by ``value``.

        :returns: The updated port
        :rtype: :class:`~openstack.network.v2.port.Port`
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
        ports = self.ports()
        for puerta in ports:
            for fixed_ip in puerta.fixed_ips:
                if fixed_ip['subnet_id'] == subnet_id:
                    result.append(puerta)
        return result

    def quotas(self):
        """Return a generator of quotas

        :returns: A generator of quota objects
        :rtype: :class:`~openstack.network.v2.quota.Quota`
        """
        return self._list(quota.Quota)

    def create_router(self, **attrs):
        """Create a new router from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.router.Router`,
                           comprised of the properties on the Router class.

        :returns: The results of router creation
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._create(router.Router, **attrs)

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
        self._delete(router.Router, value, ignore_missing=ignore_missing)

    def find_router(self, name_or_id):
        """Find a single router

        :param name_or_id: The name or ID of a router.
        :returns: One :class:`~openstack.compute.v2.router.Router` or None
        """
        return router.Router.find(self.session, name_or_id)

    def get_router(self, value):
        """Get a single router

        :param value: The value can be the ID of a router or a
                      :class:`~openstack.network.v2.router.Router` instance.

        :returns: One :class:`~openstack.network.v2.router.Router`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(router.Router, value)

    def routers(self):
        """Return a generator of routers

        :returns: A generator of router objects
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._list(router.Router)

    def update_router(self, value, **attrs):
        """Update a router

        :param value: Either the id of a router or a
                      :class:`~openstack.network.v2.router.Router` instance.
        :attrs kwargs: The attributes to update on the router represented
                       by ``value``.

        :returns: The updated router
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._update(router.Router, value, **attrs)

    def router_add_interface(self, router, subnet_id):
        router.add_interface(self.session, subnet_id)

    def router_remove_interface(self, router, subnet_id):
        router.remove_interface(self.session, subnet_id)

    def create_security_group(self, **attrs):
        """Create a new security group from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.security_group.SecurityGroup`,
            comprised of the properties on the SecurityGroup class.

        :returns: The results of security group creation
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._create(security_group.SecurityGroup, **attrs)

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
        self._delete(security_group.SecurityGroup, value,
                     ignore_missing=ignore_missing)

    def find_security_group(self, name_or_id):
        """Find a single security group

        :param name_or_id: The name or ID of a security group.
        :returns: One :class:`~openstack.compute.v2.security_group.
                  SecurityGroup` or None
        """
        return security_group.SecurityGroup.find(self.session, name_or_id)

    def get_security_group(self, value):
        """Get a single security group

        :param value: The value can be the ID of a security group or a
               :class:`~openstack.network.v2.security_group.SecurityGroup`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.security_group.SecurityGroup`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(security_group.SecurityGroup, value)

    def security_groups(self):
        """Return a generator of security groups

        :returns: A generator of security group objects
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._list(security_group.SecurityGroup)

    def update_security_group(self, value, **attrs):
        """Update a security group

        :param value: Either the id of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.
        :attrs kwargs: The attributes to update on the security group
                       represented by ``value``.

        :returns: The updated security group
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
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

    def create_security_group_rule(self, **attrs):
        """Create a new security group rule from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.network.v2.security_group_rule.
            SecurityGroupRule`, comprised of the properties on the
            SecurityGroupRule class.

        :returns: The results of security group rule creation
        :rtype: :class:`~openstack.network.v2.security_group_rule.\
            SecurityGroupRule`
        """
        return self._create(security_group_rule.SecurityGroupRule, **attrs)

    def delete_security_group_rule(self, value, ignore_missing=True):
        """Delete a security group rule

        :param value: The value can be either the ID of a security group rule
            or a :class:`~openstack.network.v2.security_group_rule.
            SecurityGroupRule` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the security group rule does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent security group rule.

        :returns: ``None``
        """
        self._delete(security_group_rule.SecurityGroupRule,
                     value, ignore_missing=ignore_missing)

    def find_security_group_rule(self, name_or_id):
        """Find a single security group rule

        :param name_or_id: The name or ID of a security group rule.
        :returns: One :class:`~openstack.compute.v2.security_group_rule.
                  SecurityGroupRule` or None
        """
        return security_group_rule.SecurityGroupRule.find(self.session,
                                                          name_or_id)

    def get_security_group_rule(self, value):
        """Get a single security group rule

        :param value: The value can be the ID of a security group rule or a
            :class:`~openstack.network.v2.security_group_rule.\
            SecurityGroupRule` instance.

        :returns: :class:`~openstack.network.v2.security_group_rule.\
            SecurityGroupRule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(security_group_rule.SecurityGroupRule, value)

    def security_group_rules(self):
        """Return a generator of security group rules

        :returns: A generator of security group rule objects
        :rtype: :class:`~openstack.network.v2.security_group_rule.
                SecurityGroupRule`
        """
        return self._list(security_group_rule.SecurityGroupRule)

    def update_security_group_rule(self, value, **attrs):
        """Update a security group rule

        :param value: Either the id of a security group rule or a
                      :class:`~openstack.network.v2.security_group_rule.
                      SecurityGroupRule` instance.
        :attrs kwargs: The attributes to update on the security group rule
                       represented by ``value``.

        :returns: The updated security group rule
        :rtype: :class:`~openstack.network.v2.security_group_rule.
                        SecurityGroupRule`
        """
        return self._update(security_group_rule.SecurityGroupRule, value,
                            **attrs)

    def create_subnet(self, **attrs):
        """Create a new subnet from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.subnet.Subnet`,
                           comprised of the properties on the Subnet class.

        :returns: The results of subnet creation
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._create(subnet.Subnet, **attrs)

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
        self._delete(subnet.Subnet, value, ignore_missing=ignore_missing)

    def find_subnet(self, name_or_id):
        """Find a single subnet

        :param name_or_id: The name or ID of a subnet.
        :returns: One :class:`~openstack.compute.v2.subnet.Subnet` or None
        """
        return subnet.Subnet.find(self.session, name_or_id)

    def get_subnet(self, value):
        """Get a single subnet

        :param value: The value can be the ID of a subnet or a
                      :class:`~openstack.network.v2.subnet.Subnet` instance.

        :returns: One :class:`~openstack.network.v2.subnet.Subnet`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(subnet.Subnet, value)

    def subnets(self):
        """Return a generator of subnets

        :returns: A generator of subnet objects
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._list(subnet.Subnet)

    def update_subnet(self, value, **attrs):
        """Update a subnet

        :param value: Either the id of a subnet or a
                      :class:`~openstack.network.v2.subnet.Subnet` instance.
        :attrs kwargs: The attributes to update on the subnet represented
                       by ``value``.

        :returns: The updated subnet
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._update(subnet.Subnet, value, **attrs)
