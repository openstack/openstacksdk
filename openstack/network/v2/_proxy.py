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

from openstack.network.v2 import address_scope as _address_scope
from openstack.network.v2 import agent as _agent
from openstack.network.v2 import availability_zone
from openstack.network.v2 import extension
from openstack.network.v2 import floating_ip as _floating_ip
from openstack.network.v2 import health_monitor as _health_monitor
from openstack.network.v2 import listener as _listener
from openstack.network.v2 import load_balancer as _load_balancer
from openstack.network.v2 import metering_label as _metering_label
from openstack.network.v2 import metering_label_rule as _metering_label_rule
from openstack.network.v2 import network as _network
from openstack.network.v2 import network_ip_availability
from openstack.network.v2 import pool as _pool
from openstack.network.v2 import pool_member as _pool_member
from openstack.network.v2 import port as _port
from openstack.network.v2 import quota as _quota
from openstack.network.v2 import router as _router
from openstack.network.v2 import security_group as _security_group
from openstack.network.v2 import security_group_rule as _security_group_rule
from openstack.network.v2 import segment as _segment
from openstack.network.v2 import subnet as _subnet
from openstack.network.v2 import subnet_pool as _subnet_pool
from openstack.network.v2 import vpn_service as _vpn_service
from openstack import proxy
from openstack import resource


class Proxy(proxy.BaseProxy):

    def create_address_scope(self, **attrs):
        """Create a new address scope from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.address_scope.AddressScope`,
            comprised of the properties on the AddressScope class.

        :returns: The results of address scope creation
        :rtype: :class:`~openstack.network.v2.address_scope.AddressScope`
        """
        return self._create(_address_scope.AddressScope, **attrs)

    def delete_address_scope(self, address_scope, ignore_missing=True):
        """Delete an address scope

        :param address_scope: The value can be either the ID of an
            address scope or
            a :class:`~openstack.network.v2.address_scope.AddressScope`
            instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the address scope does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent address scope.

        :returns: ``None``
        """
        self._delete(_address_scope.AddressScope, address_scope,
                     ignore_missing=ignore_missing)

    def find_address_scope(self, name_or_id, ignore_missing=True):
        """Find a single address scope

        :param name_or_id: The name or ID of an address scope.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.address_scope.AddressScope`
                  or None
        """
        return self._find(_address_scope.AddressScope, name_or_id,
                          ignore_missing=ignore_missing)

    def get_address_scope(self, address_scope):
        """Get a single address scope

        :param address_scope: The value can be the ID of an address scope or a
            :class:`~openstack.network.v2.address_scope.AddressScope` instance.

        :returns: One :class:`~openstack.network.v2.address_scope.AddressScope`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_address_scope.AddressScope, address_scope)

    def address_scopes(self, **query):
        """Return a generator of address scopes

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of address scope objects
        :rtype: :class:`~openstack.network.v2.address_scope.AddressScope`
        """
        return self._list(_address_scope.AddressScope,
                          paginated=False,
                          **query)

    def update_address_scope(self, address_scope, **attrs):
        """Update an address scope

        :param address_scope: Either the ID of an address scope or a
            :class:`~openstack.network.v2.address_scope.AddressScope` instance.
        :attrs kwargs: The attributes to update on the address scope
                       represented by ``value``.

        :returns: The updated address scope
        :rtype: :class:`~openstack.network.v2.address_scope.AddressScope`
        """
        return self._update(_address_scope.AddressScope,
                            address_scope,
                            **attrs)

    def agents(self, **query):
        """Return a generator of network agents

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of agents
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        """
        return self._list(_agent.Agent, paginated=False, **query)

    def delete_agent(self, agent, ignore_missing=True):
        """Delete a network agent

        :param agent: The value can be the ID of a agent or a
                     :class:`~openstack.network.v2.agent.Agent` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the agent does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent agent.

        :returns: ``None``
        """
        self._delete(_agent.Agent, agent,
                     ignore_missing=ignore_missing)

    def get_agent(self, agent, ignore_missing=True):
        """Get a single network agent

        :param agent: The value can be the ID of a agent or a
                     :class:`~openstack.network.v2.agent.Agent` instance.

        :returns: One :class:`~openstack.network.v2.agent.Agent`
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_agent.Agent, agent)

    def update_agent(self, agent, **attrs):
        """Update a network agent

        :param agent: The value can be the ID of a agent or a
                     :class:`~openstack.network.v2.agent.Agent` instance.
        :attrs kwargs: The attributes to update on the agent represented
                       by ``value``.

        :returns: One :class:`~openstack.network.v2.agent.Agent`
        :rtype: :class:`~openstack.network.v2.agent.Agent`
        """
        return self._update(_agent.Agent, agent, **attrs)

    def availability_zones(self):
        """Return a generator of availability zones

        :returns: A generator of availability zone objects
        :rtype:
            :class:`~openstack.network.v2.availability_zone.AvailabilityZone`
        """
        return self._list(availability_zone.AvailabilityZone, paginated=False)

    def find_extension(self, name_or_id, ignore_missing=True):
        """Find a single extension

        :param name_or_id: The name or ID of a extension.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.extension.Extension`
                  or None
        """
        return self._find(extension.Extension, name_or_id,
                          ignore_missing=ignore_missing)

    def extensions(self, **query):
        """Return a generator of extensions

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of extension objects
        :rtype: :class:`~openstack.network.v2.extension.Extension`
        """
        return self._list(extension.Extension, paginated=False, **query)

    def create_ip(self, **attrs):
        """Create a new floating ip from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.floating_ip.FloatingIP`,
            comprised of the properties on the FloatingIP class.

        :returns: The results of floating ip creation
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._create(_floating_ip.FloatingIP, **attrs)

    def delete_ip(self, floating_ip, ignore_missing=True):
        """Delete a floating ip

        :param floating_ip: The value can be either the ID of a floating ip
                    or a :class:`~openstack.network.v2.floating_ip.FloatingIP`
                    instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the floating ip does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent ip.

        :returns: ``None``
        """
        self._delete(_floating_ip.FloatingIP, floating_ip,
                     ignore_missing=ignore_missing)

    def find_available_ip(self):
        """Find an available IP

        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
                  or None
        """
        return _floating_ip.FloatingIP.find_available(self.session)

    def find_ip(self, name_or_id, ignore_missing=True):
        """Find a single IP

        :param name_or_id: The name or ID of an IP.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
                  or None
        """
        return self._find(_floating_ip.FloatingIP, name_or_id,
                          ignore_missing=ignore_missing)

    def get_ip(self, floating_ip):
        """Get a single floating ip

        :param floating_ip: The value can be the ID of a floating ip or a
                      :class:`~openstack.network.v2.floating_ip.FloatingIP`
                      instance.

        :returns: One :class:`~openstack.network.v2.floating_ip.FloatingIP`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_floating_ip.FloatingIP, floating_ip)

    def ips(self, **query):
        """Return a generator of ips

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of floating IP objects
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._list(_floating_ip.FloatingIP, paginated=False, **query)

    def update_ip(self, floating_ip, **attrs):
        """Update a ip

        :param floating_ip: Either the id of a ip or a
                      :class:`~openstack.network.v2.floating_ip.FloatingIP`
                      instance.
        :attrs kwargs: The attributes to update on the ip represented
                       by ``value``.

        :returns: The updated ip
        :rtype: :class:`~openstack.network.v2.floating_ip.FloatingIP`
        """
        return self._update(_floating_ip.FloatingIP, floating_ip, **attrs)

    def create_health_monitor(self, **attrs):
        """Create a new health monitor from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.health_monitor.HealthMonitor`,
            comprised of the properties on the HealthMonitor class.

        :returns: The results of health monitor creation
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._create(_health_monitor.HealthMonitor, **attrs)

    def delete_health_monitor(self, health_monitor, ignore_missing=True):
        """Delete a health monitor

        :param health_monitor: The value can be either the ID of a
            health monitor or a
            :class:`~openstack.network.v2.health_monitor.HealthMonitor`
            instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the health monitor does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent health monitor.

        :returns: ``None``
        """
        self._delete(_health_monitor.HealthMonitor, health_monitor,
                     ignore_missing=ignore_missing)

    def find_health_monitor(self, name_or_id, ignore_missing=True):
        """Find a single health monitor

        :param name_or_id: The name or ID of a health monitor.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.health_monitor.
                  HealthMonitor` or None
        """
        return self._find(_health_monitor.HealthMonitor,
                          name_or_id, ignore_missing=ignore_missing)

    def get_health_monitor(self, health_monitor):
        """Get a single health monitor

        :param health_monitor: The value can be the ID of a health monitor or a
               :class:`~openstack.network.v2.health_monitor.HealthMonitor`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_health_monitor.HealthMonitor, health_monitor)

    def health_monitors(self, **query):
        """Return a generator of health monitors

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of health monitor objects
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._list(_health_monitor.HealthMonitor, paginated=False,
                          **query)

    def update_health_monitor(self, health_monitor, **attrs):
        """Update a health monitor

        :param health_monitor: Either the id of a health monitor or a
                      :class:`~openstack.network.v2.health_monitor.
                      HealthMonitor` instance.
        :attrs kwargs: The attributes to update on the health monitor
                       represented by ``value``.

        :returns: The updated health monitor
        :rtype: :class:`~openstack.network.v2.health_monitor.HealthMonitor`
        """
        return self._update(_health_monitor.HealthMonitor, health_monitor,
                            **attrs)

    def create_listener(self, **attrs):
        """Create a new listener from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.listener.Listener`,
                           comprised of the properties on the Listener class.

        :returns: The results of listener creation
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._create(_listener.Listener, **attrs)

    def delete_listener(self, listener, ignore_missing=True):
        """Delete a listener

        :param listener: The value can be either the ID of a listner or a
               :class:`~openstack.network.v2.listener.Listener` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the listner does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent listener.

        :returns: ``None``
        """
        self._delete(_listener.Listener, listener,
                     ignore_missing=ignore_missing)

    def find_listener(self, name_or_id, ignore_missing=True):
        """Find a single listener

        :param name_or_id: The name or ID of a listener.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.listener.Listener` or None
        """
        return self._find(_listener.Listener, name_or_id,
                          ignore_missing=ignore_missing)

    def get_listener(self, listener):
        """Get a single listener

        :param listener: The value can be the ID of a listener or a
               :class:`~openstack.network.v2.listener.Listener`
               instance.

        :returns: One :class:`~openstack.network.v2.listener.Listener`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_listener.Listener, listener)

    def listeners(self, **query):
        """Return a generator of listeners

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of listener objects
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._list(_listener.Listener, paginated=False, **query)

    def update_listener(self, listener, **attrs):
        """Update a listener

        :param listener: Either the id of a listener or a
                      :class:`~openstack.network.v2.listener.Listener`
                      instance.
        :attrs kwargs: The attributes to update on the listener represented
                       by ``value``.

        :returns: The updated listener
        :rtype: :class:`~openstack.network.v2.listener.Listener`
        """
        return self._update(_listener.Listener, listener, **attrs)

    def create_load_balancer(self, **attrs):
        """Create a new load balancer from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.load_balancer.LoadBalancer`,
            comprised of the properties on the LoadBalancer class.

        :returns: The results of load balancer creation
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._create(_load_balancer.LoadBalancer, **attrs)

    def delete_load_balancer(self, load_balancer, ignore_missing=True):
        """Delete a load balancer

        :param load_balancer: The value can be the ID of a load balancer or a
               :class:`~openstack.network.v2.load_balancer.LoadBalancer`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the load balancer does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent load balancer.

        :returns: ``None``
        """
        self._delete(_load_balancer.LoadBalancer, load_balancer,
                     ignore_missing=ignore_missing)

    def find_load_balancer(self, name_or_id, ignore_missing=True):
        """Find a single load balancer

        :param name_or_id: The name or ID of a load balancer.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.load_balancer.LoadBalancer`
                  or None
        """
        return self._find(_load_balancer.LoadBalancer, name_or_id,
                          ignore_missing=ignore_missing)

    def get_load_balancer(self, load_balancer):
        """Get a single load balancer

        :param load_balancer: The value can be the ID of a load balancer or a
               :class:`~openstack.network.v2.load_balancer.LoadBalancer`
               instance.

        :returns: One :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_load_balancer.LoadBalancer, load_balancer)

    def load_balancers(self, **query):
        """Return a generator of load balancers

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of load balancer objects
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._list(_load_balancer.LoadBalancer, paginated=False,
                          **query)

    def update_load_balancer(self, load_balancer, **attrs):
        """Update a load balancer

        :param load_balancer: Either the id of a load balancer or a
                      :class:`~openstack.network.v2.load_balancer.LoadBalancer`
                      instance.
        :attrs kwargs: The attributes to update on the load balancer
                       represented by ``value``.

        :returns: The updated load balancer
        :rtype: :class:`~openstack.network.v2.load_balancer.LoadBalancer`
        """
        return self._update(_load_balancer.LoadBalancer, load_balancer,
                            **attrs)

    def create_metering_label(self, **attrs):
        """Create a new metering label from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.metering_label.MeteringLabel`,
            comprised of the properties on the MeteringLabel class.

        :returns: The results of metering label creation
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._create(_metering_label.MeteringLabel, **attrs)

    def delete_metering_label(self, metering_label, ignore_missing=True):
        """Delete a metering label

        :param metering_label:
                The value can be either the ID of a metering label or a
                :class:`~openstack.network.v2.metering_label.MeteringLabel`
                instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the metering label does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent metering label.

        :returns: ``None``
        """
        self._delete(_metering_label.MeteringLabel, metering_label,
                     ignore_missing=ignore_missing)

    def find_metering_label(self, name_or_id, ignore_missing=True):
        """Find a single metering label

        :param name_or_id: The name or ID of a metering label.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.metering_label.
                  MeteringLabel` or None
        """
        return self._find(_metering_label.MeteringLabel, name_or_id,
                          ignore_missing=ignore_missing)

    def get_metering_label(self, metering_label):
        """Get a single metering label

        :param metering_label: The value can be the ID of a metering label or a
               :class:`~openstack.network.v2.metering_label.MeteringLabel`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.metering_label.MeteringLabel`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_metering_label.MeteringLabel, metering_label)

    def metering_labels(self, **query):
        """Return a generator of metering labels

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of metering label objects
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._list(_metering_label.MeteringLabel, paginated=False,
                          **query)

    def update_metering_label(self, metering_label, **attrs):
        """Update a metering label

        :param metering_label: Either the id of a metering label or a
                      :class:`~openstack.network.v2.metering_label.
                      MeteringLabel` instance.
        :attrs kwargs: The attributes to update on the metering label
                       represented by ``value``.

        :returns: The updated metering label
        :rtype: :class:`~openstack.network.v2.metering_label.MeteringLabel`
        """
        return self._update(_metering_label.MeteringLabel, metering_label,
                            **attrs)

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
        return self._create(_metering_label_rule.MeteringLabelRule, **attrs)

    def delete_metering_label_rule(self, metering_label_rule,
                                   ignore_missing=True):
        """Delete a metering label rule

        :param metering_label_rule:
            The value can be either the ID of a metering label rule
            or a :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the metering label rule does not exist.  When set to ``True``,
            no exception will be set when attempting to delete a nonexistent
            metering label rule.

        :returns: ``None``
        """
        self._delete(_metering_label_rule.MeteringLabelRule,
                     metering_label_rule, ignore_missing=ignore_missing)

    def find_metering_label_rule(self, name_or_id, ignore_missing=True):
        """Find a single metering label rule

        :param name_or_id: The name or ID of a metering label rule.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.metering_label_rule.
                  MeteringLabelRule` or None
        """
        return self._find(_metering_label_rule.MeteringLabelRule, name_or_id,
                          ignore_missing=ignore_missing)

    def get_metering_label_rule(self, metering_label_rule):
        """Get a single metering label rule

        :param metering_label_rule:
            The value can be the ID of a metering label rule or a
            :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule` instance.

        :returns: One
            :class:`~openstack.network.v2.metering_label_rule.\
            MeteringLabelRule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_metering_label_rule.MeteringLabelRule,
                         metering_label_rule)

    def metering_label_rules(self, **query):
        """Return a generator of metering label rules

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of metering label rule objects
        :rtype: :class:`~openstack.network.v2.metering_label_rule.
                MeteringLabelRule`
        """
        return self._list(_metering_label_rule.MeteringLabelRule,
                          paginated=False, **query)

    def update_metering_label_rule(self, metering_label_rule, **attrs):
        """Update a metering label rule

        :param metering_label_rule:
                      Either the id of a metering label rule or a
                      :class:`~openstack.network.v2.metering_label_rule.
                      MeteringLabelRule` instance.
        :attrs kwargs: The attributes to update on the metering label rule
                       represented by ``value``.

        :returns: The updated metering label rule
        :rtype: :class:`~openstack.network.v2.metering_label_rule.
                       MeteringLabelRule`
        """
        return self._update(_metering_label_rule.MeteringLabelRule,
                            metering_label_rule, **attrs)

    def create_network(self, **attrs):
        """Create a new network from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.network.Network`,
                           comprised of the properties on the Network class.

        :returns: The results of network creation
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._create(_network.Network, **attrs)

    def delete_network(self, network, ignore_missing=True):
        """Delete a network

        :param network:
            The value can be either the ID of a network or a
            :class:`~openstack.network.v2.network.Network` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the network does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent network.

        :returns: ``None``
        """
        self._delete(_network.Network, network, ignore_missing=ignore_missing)

    def find_network(self, name_or_id, ignore_missing=True):
        """Find a single network

        :param name_or_id: The name or ID of a network.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.network.Network` or None
        """
        return self._find(_network.Network, name_or_id,
                          ignore_missing=ignore_missing)

    def get_network(self, network):
        """Get a single network

        :param network:
            The value can be the ID of a network or a
            :class:`~openstack.network.v2.network.Network` instance.

        :returns: One :class:`~openstack.network.v2.network.Network`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_network.Network, network)

    def networks(self, **query):
        """Return a generator of networks

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of network objects
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._list(_network.Network, paginated=False, **query)

    def update_network(self, network, **attrs):
        """Update a network

        :param network:
            Either the id of a network or a
            :class:`~openstack.network.v2.network.Network` instance.
        :attrs kwargs: The attributes to update on the network represented
                       by ``value``.

        :returns: The updated network
        :rtype: :class:`~openstack.network.v2.network.Network`
        """
        return self._update(_network.Network, network, **attrs)

    def find_network_ip_availability(self, name_or_id, ignore_missing=True):
        """Find IP availability of a network

        :param name_or_id: The name or ID of a network.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.network_ip_availability.
                       NetworkIPAvailability` or None
        """
        return self._find(network_ip_availability.NetworkIPAvailability,
                          name_or_id,
                          ignore_missing=ignore_missing)

    def get_network_ip_availability(self, network):
        """Get IP availability of a network

        :param network:
            The value can be the ID of a network or a
            :class:`~openstack.network.v2.network.Network` instance.

        :returns: One :class:`~openstack.network.v2.network_ip_availability.
                      NetworkIPAvailability`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(network_ip_availability.NetworkIPAvailability,
                         network)

    def network_ip_availabilities(self, **query):
        """Return a generator of network ip availabilities

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of network ip availability objects
        :rtype: :class:`~openstack.network.v2.network_ip_availability.
                NetworkIPAvailability`
        """
        return self._list(network_ip_availability.NetworkIPAvailability,
                          paginated=False, **query)

    def create_pool(self, **attrs):
        """Create a new pool from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.pool.Pool`,
                           comprised of the properties on the Pool class.

        :returns: The results of pool creation
        :rtype: :class:`~openstack.network.v2.pool.Pool`
        """
        return self._create(_pool.Pool, **attrs)

    def delete_pool(self, pool, ignore_missing=True):
        """Delete a pool

        :param pool: The value can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the pool does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent pool.

        :returns: ``None``
        """
        self._delete(_pool.Pool, pool, ignore_missing=ignore_missing)

    def find_pool(self, name_or_id, ignore_missing=True):
        """Find a single pool

        :param name_or_id: The name or ID of a pool.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.pool.Pool` or None
        """
        return self._find(_pool.Pool, name_or_id,
                          ignore_missing=ignore_missing)

    def get_pool(self, pool):
        """Get a single pool

        :param pool: The value can be the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance.

        :returns: One :class:`~openstack.network.v2.pool.Pool`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_pool.Pool, pool)

    def pools(self, **query):
        """Return a generator of pools

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of pool objects
        :rtype: :class:`~openstack.network.v2.pool.Pool`
        """
        return self._list(_pool.Pool, paginated=False, **query)

    def update_pool(self, pool, **attrs):
        """Update a pool

        :param pool: Either the id of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance.
        :attrs kwargs: The attributes to update on the pool represented
                       by ``value``.

        :returns: The updated pool
        :rtype: :class:`~openstack.network.v2.pool.Pool`
        """
        return self._update(_pool.Pool, pool, **attrs)

    def create_pool_member(self, pool, **attrs):
        """Create a new pool member from attributes

        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member will be created in.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.pool_member.PoolMember`,
            comprised of the properties on the PoolMember class.

        :returns: The results of pool member creation
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        pool_id = resource.Resource.get_id(pool)
        return self._create(_pool_member.PoolMember,
                            path_args={'pool_id': pool_id},
                            **attrs)

    def delete_pool_member(self, pool_member, pool, ignore_missing=True):
        """Delete a pool member

        :param pool_member:
            The member can be either the ID of a pool member or a
            :class:`~openstack.network.v2.pool_member.PoolMember` instance.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the pool member does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent pool member.

        :returns: ``None``
        """
        pool_id = resource.Resource.get_id(pool)
        self._delete(_pool_member.PoolMember, pool_member,
                     path_args={'pool_id': pool_id},
                     ignore_missing=ignore_missing)

    def find_pool_member(self, name_or_id, pool, ignore_missing=True):
        """Find a single pool member

        :param str name_or_id: The name or ID of a pool member.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.pool_member.PoolMember`
                  or None
        """
        pool_id = resource.Resource.get_id(pool)
        return self._find(_pool_member.PoolMember, name_or_id,
                          path_args={'pool_id': pool_id},
                          ignore_missing=ignore_missing)

    def get_pool_member(self, pool_member, pool):
        """Get a single pool member

        :param pool_member: The member can be the ID of a pool member or a
                       :class:`~openstack.network.v2.pool_member.PoolMember`
                       instance.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member belongs to.

        :returns: One :class:`~openstack.network.v2.pool_member.PoolMember`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        pool_id = resource.Resource.get_id(pool)
        return self._get(_pool_member.PoolMember, pool_member,
                         path_args={'pool_id': pool_id})

    def pool_members(self, pool, **query):
        """Return a generator of pool members

        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member belongs to.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of pool member objects
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        pool_id = resource.Resource.get_id(pool)
        return self._list(_pool_member.PoolMember,
                          path_args={'pool_id': pool_id}, paginated=False,
                          **query)

    def update_pool_member(self, pool_member, pool, **attrs):
        """Update a pool member

        :param pool_member: Either the ID of a pool member or a
                       :class:`~openstack.network.v2.pool_member.PoolMember`
                       instance.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.network.v2.pool.Pool` instance that
                     the member belongs to.
        :attrs kwargs: The attributes to update on the pool member represented
                       by ``value``.

        :returns: The updated pool member
        :rtype: :class:`~openstack.network.v2.pool_member.PoolMember`
        """
        pool_id = resource.Resource.get_id(pool)
        return self._update(_pool_member.PoolMember, pool_member,
                            path_args={'pool_id': pool_id}, **attrs)

    def create_port(self, **attrs):
        """Create a new port from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.port.Port`,
                           comprised of the properties on the Port class.

        :returns: The results of port creation
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._create(_port.Port, **attrs)

    def delete_port(self, port, ignore_missing=True):
        """Delete a port

        :param port: The value can be either the ID of a port or a
                     :class:`~openstack.network.v2.port.Port` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the port does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent port.

        :returns: ``None``
        """
        self._delete(_port.Port, port, ignore_missing=ignore_missing)

    def find_port(self, name_or_id, ignore_missing=True):
        """Find a single port

        :param name_or_id: The name or ID of a port.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.port.Port` or None
        """
        return self._find(_port.Port, name_or_id,
                          ignore_missing=ignore_missing)

    def get_port(self, port):
        """Get a single port

        :param port: The value can be the ID of a port or a
                     :class:`~openstack.network.v2.port.Port` instance.

        :returns: One :class:`~openstack.network.v2.port.Port`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_port.Port, port)

    def ports(self, **query):
        """Return a generator of ports

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of port objects
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._list(_port.Port, paginated=False, **query)

    def update_port(self, port, **attrs):
        """Update a port

        :param port: Either the id of a port or a
                     :class:`~openstack.network.v2.port.Port` instance.
        :attrs kwargs: The attributes to update on the port represented
                       by ``value``.

        :returns: The updated port
        :rtype: :class:`~openstack.network.v2.port.Port`
        """
        return self._update(_port.Port, port, **attrs)

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

    def delete_quota(self, quota, ignore_missing=True):
        """Delete a quota (i.e. reset to the default quota)

        :param quota: The value can be either the ID of a quota or a
                      :class:`~openstack.network.v2.quota.Quota` instance.
                      The ID of a quota is the same as the project ID
                      for the quota.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when quota does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent quota.

        :returns: ``None``
        """
        self._delete(_quota.Quota, quota, ignore_missing=ignore_missing)

    def get_quota(self, quota):
        """Get a quota

        :param quota: The value can be the ID of a quota or a
                      :class:`~openstack.network.v2.quota.Quota` instance.
                      The ID of a quota is the same as the project ID
                      for the quota.

        :returns: One :class:`~openstack.network.v2.quota.Quota`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_quota.Quota, quota)

    def quotas(self, **query):
        """Return a generator of quotas

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of quota objects
        :rtype: :class:`~openstack.network.v2.quota.Quota`
        """
        return self._list(_quota.Quota, paginated=False, **query)

    def update_quota(self, quota, **attrs):
        """Update a quota

        :param quota: Either the ID of a quota or a
                      :class:`~openstack.network.v2.quota.Quota` instance.
                      The ID of a quota is the same as the project ID
                      for the quota.
        :attrs kwargs: The attributes to update on the quota represented
                       by ``value``.

        :returns: The updated quota
        :rtype: :class:`~openstack.network.v2.quota.Quota`
        """
        return self._update(_quota.Quota, quota, **attrs)

    def create_router(self, **attrs):
        """Create a new router from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.router.Router`,
                           comprised of the properties on the Router class.

        :returns: The results of router creation
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._create(_router.Router, **attrs)

    def delete_router(self, router, ignore_missing=True):
        """Delete a router

        :param router: The value can be either the ID of a router or a
                       :class:`~openstack.network.v2.router.Router` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the router does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent router.

        :returns: ``None``
        """
        self._delete(_router.Router, router, ignore_missing=ignore_missing)

    def find_router(self, name_or_id, ignore_missing=True):
        """Find a single router

        :param name_or_id: The name or ID of a router.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.router.Router` or None
        """
        return self._find(_router.Router, name_or_id,
                          ignore_missing=ignore_missing)

    def get_router(self, router):
        """Get a single router

        :param router: The value can be the ID of a router or a
                       :class:`~openstack.network.v2.router.Router` instance.

        :returns: One :class:`~openstack.network.v2.router.Router`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_router.Router, router)

    def routers(self, **query):
        """Return a generator of routers

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of router objects
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._list(_router.Router, paginated=False, **query)

    def update_router(self, router, **attrs):
        """Update a router

        :param router: Either the id of a router or a
                       :class:`~openstack.network.v2.router.Router` instance.
        :attrs kwargs: The attributes to update on the router represented
                       by ``value``.

        :returns: The updated router
        :rtype: :class:`~openstack.network.v2.router.Router`
        """
        return self._update(_router.Router, router, **attrs)

    def router_add_interface(self, router, subnet_id=None, port_id=None):
        """Add Interface to a router

        :param router: Either the router ID or an instance of
                       :class:`~openstack.network.v2.router.Router`
        :param subnet_id: ID of the subnet
        :param port_id: ID of the port
        :returns: Router with updated interface
        :rtype: :class: `~openstack.network.v2.router.Router`
        """

        body = {}
        if port_id:
            body = {'port_id': port_id}
        else:
            body = {'subnet_id': subnet_id}
        return router.add_interface(self.session, **body)

    def router_remove_interface(self, router, subnet_id=None, port_id=None):
        """Remove Interface from a router

        :param router: Either the router ID or an instance of
                       :class:`~openstack.network.v2.router.Router`
        :param subnet: ID of the subnet
        :param port: ID of the port
        :returns: Router with updated interface
        :rtype: :class: `~openstack.network.v2.router.Router`
        """

        body = {}
        if port_id:
            body = {'port_id': port_id}
        else:
            body = {'subnet_id': subnet_id}
        return router.remove_interface(self.session, **body)

    def create_security_group(self, **attrs):
        """Create a new security group from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.security_group.SecurityGroup`,
            comprised of the properties on the SecurityGroup class.

        :returns: The results of security group creation
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._create(_security_group.SecurityGroup, **attrs)

    def delete_security_group(self, security_group, ignore_missing=True):
        """Delete a security group

        :param security_group:
            The value can be either the ID of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the security group does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent security group.

        :returns: ``None``
        """
        self._delete(_security_group.SecurityGroup, security_group,
                     ignore_missing=ignore_missing)

    def find_security_group(self, name_or_id, ignore_missing=True):
        """Find a single security group

        :param name_or_id: The name or ID of a security group.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.security_group.
                  SecurityGroup` or None
        """
        return self._find(_security_group.SecurityGroup, name_or_id,
                          ignore_missing=ignore_missing)

    def get_security_group(self, security_group):
        """Get a single security group

        :param security_group: The value can be the ID of a security group or a
               :class:`~openstack.network.v2.security_group.SecurityGroup`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.security_group.SecurityGroup`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_security_group.SecurityGroup, security_group)

    def security_groups(self, **query):
        """Return a generator of security groups

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of security group objects
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._list(_security_group.SecurityGroup, paginated=False,
                          **query)

    def update_security_group(self, security_group, **attrs):
        """Update a security group

        :param security_group: Either the id of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.
        :attrs kwargs: The attributes to update on the security group
                       represented by ``value``.

        :returns: The updated security group
        :rtype: :class:`~openstack.network.v2.security_group.SecurityGroup`
        """
        return self._update(_security_group.SecurityGroup, security_group,
                            **attrs)

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
        return self._create(_security_group_rule.SecurityGroupRule, **attrs)

    def delete_security_group_rule(self, security_group_rule,
                                   ignore_missing=True):
        """Delete a security group rule

        :param security_group_rule:
            The value can be either the ID of a security group rule
            or a :class:`~openstack.network.v2.security_group_rule.
            SecurityGroupRule` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the security group rule does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent security group rule.

        :returns: ``None``
        """
        self._delete(_security_group_rule.SecurityGroupRule,
                     security_group_rule, ignore_missing=ignore_missing)

    def find_security_group_rule(self, name_or_id, ignore_missing=True):
        """Find a single security group rule

        :param str name_or_id: The ID of a security group rule.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.security_group_rule.
                  SecurityGroupRule` or None
        """
        return self._find(_security_group_rule.SecurityGroupRule,
                          name_or_id, ignore_missing=ignore_missing)

    def get_security_group_rule(self, security_group_rule):
        """Get a single security group rule

        :param security_group_rule:
            The value can be the ID of a security group rule or a
            :class:`~openstack.network.v2.security_group_rule.\
            SecurityGroupRule` instance.

        :returns: :class:`~openstack.network.v2.security_group_rule.\
            SecurityGroupRule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_security_group_rule.SecurityGroupRule,
                         security_group_rule)

    def security_group_rules(self, **query):
        """Return a generator of security group rules

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of security group rule objects
        :rtype: :class:`~openstack.network.v2.security_group_rule.
                SecurityGroupRule`
        """
        return self._list(_security_group_rule.SecurityGroupRule,
                          paginated=False, **query)

    def find_segment(self, name_or_id, ignore_missing=True):
        """Find a single segment

        .. caution::
           BETA: This API is a work in progress and is subject to change.

        :param name_or_id: The name or ID of a segment.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.segment.Segment` or None
        """
        return self._find(_segment.Segment, name_or_id,
                          ignore_missing=ignore_missing)

    def get_segment(self, segment):
        """Get a single segment

        .. caution::
           BETA: This API is a work in progress and is subject to change.

        :param segment: The value can be the ID of a segment or a
                        :class:`~openstack.network.v2.segment.Segment`
                        instance.

        :returns: One :class:`~openstack.network.v2.segment.Segment`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_segment.Segment, segment)

    def segments(self, **query):
        """Return a generator of segments

        .. caution::
           BETA: This API is a work in progress and is subject to change.

        :param kwargs \*\*query: Optional query parameters to be sent to limit
            the resources being returned. Available parameters include:

            * network_id: ID of the network that owns the segments
            * network_type: Network type for the segments
            * physical_network: Physical network name for the segments
            * segmentation_id: Segmentation ID for the segments

        :returns: A generator of segment objects
        :rtype: :class:`~openstack.network.v2.segment.Segment`
        """
        return self._list(_segment.Segment, paginated=False, **query)

    def create_subnet(self, **attrs):
        """Create a new subnet from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.network.v2.subnet.Subnet`,
                           comprised of the properties on the Subnet class.

        :returns: The results of subnet creation
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._create(_subnet.Subnet, **attrs)

    def delete_subnet(self, subnet, ignore_missing=True):
        """Delete a subnet

        :param subnet: The value can be either the ID of a subnet or a
                       :class:`~openstack.network.v2.subnet.Subnet` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the subnet does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent subnet.

        :returns: ``None``
        """
        self._delete(_subnet.Subnet, subnet, ignore_missing=ignore_missing)

    def find_subnet(self, name_or_id, ignore_missing=True):
        """Find a single subnet

        :param name_or_id: The name or ID of a subnet.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.subnet.Subnet` or None
        """
        return self._find(_subnet.Subnet, name_or_id,
                          ignore_missing=ignore_missing)

    def get_subnet(self, subnet):
        """Get a single subnet

        :param subnet: The value can be the ID of a subnet or a
                       :class:`~openstack.network.v2.subnet.Subnet` instance.

        :returns: One :class:`~openstack.network.v2.subnet.Subnet`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_subnet.Subnet, subnet)

    def subnets(self, **query):
        """Return a generator of subnets

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of subnet objects
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._list(_subnet.Subnet, paginated=False, **query)

    def update_subnet(self, subnet, **attrs):
        """Update a subnet

        :param subnet: Either the id of a subnet or a
                       :class:`~openstack.network.v2.subnet.Subnet` instance.
        :attrs kwargs: The attributes to update on the subnet represented
                       by ``value``.

        :returns: The updated subnet
        :rtype: :class:`~openstack.network.v2.subnet.Subnet`
        """
        return self._update(_subnet.Subnet, subnet, **attrs)

    def create_subnet_pool(self, **attrs):
        """Create a new subnet pool from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.subnet_pool.SubnetPool`,
            comprised of the properties on the SubnetPool class.

        :returns: The results of subnet pool creation
        :rtype: :class:`~openstack.network.v2.subnet_pool.SubnetPool`
        """
        return self._create(_subnet_pool.SubnetPool, **attrs)

    def delete_subnet_pool(self, subnet_pool, ignore_missing=True):
        """Delete a subnet pool

        :param subnet_pool: The value can be either the ID of a subnet pool or
            a :class:`~openstack.network.v2.subnet_pool.SubnetPool` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the subnet pool does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent subnet pool.

        :returns: ``None``
        """
        self._delete(_subnet_pool.SubnetPool, subnet_pool,
                     ignore_missing=ignore_missing)

    def find_subnet_pool(self, name_or_id, ignore_missing=True):
        """Find a single subnet pool

        :param name_or_id: The name or ID of a subnet pool.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.subnet_pool.SubnetPool`
                  or None
        """
        return self._find(_subnet_pool.SubnetPool, name_or_id,
                          ignore_missing=ignore_missing)

    def get_subnet_pool(self, subnet_pool):
        """Get a single subnet pool

        :param subnet_pool: The value can be the ID of a subnet pool or a
            :class:`~openstack.network.v2.subnet_pool.SubnetPool` instance.

        :returns: One :class:`~openstack.network.v2.subnet_pool.SubnetPool`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_subnet_pool.SubnetPool, subnet_pool)

    def subnet_pools(self, **query):
        """Return a generator of subnet pools

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of subnet pool objects
        :rtype: :class:`~openstack.network.v2.subnet_pool.SubnetPool`
        """
        return self._list(_subnet_pool.SubnetPool, paginated=False, **query)

    def update_subnet_pool(self, subnet_pool, **attrs):
        """Update a subnet pool

        :param subnet_pool: Either the ID of a subnet pool or a
            :class:`~openstack.network.v2.subnet_pool.SubnetPool` instance.
        :attrs kwargs: The attributes to update on the subnet pool
                       represented by ``value``.

        :returns: The updated subnet pool
        :rtype: :class:`~openstack.network.v2.subnet_pool.SubnetPool`
        """
        return self._update(_subnet_pool.SubnetPool, subnet_pool, **attrs)

    def create_vpn_service(self, **attrs):
        """Create a new vpn service from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.network.v2.vpn_service.VPNService`,
            comprised of the properties on the VPNService class.

        :returns: The results of vpn service creation
        :rtype: :class:`~openstack.network.v2.vpn_service.VPNService`
        """
        return self._create(_vpn_service.VPNService, **attrs)

    def delete_vpn_service(self, vpn_service, ignore_missing=True):
        """Delete a vpn service

        :param vpn_service:
            The value can be either the ID of a vpn service or a
            :class:`~openstack.network.v2.vpn_service.VPNService` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the vpn service does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent vpn service.

        :returns: ``None``
        """
        self._delete(_vpn_service.VPNService, vpn_service,
                     ignore_missing=ignore_missing)

    def find_vpn_service(self, name_or_id, ignore_missing=True):
        """Find a single vpn service

        :param name_or_id: The name or ID of a vpn service.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.network.v2.vpn_service.VPNService`
                  or None
        """
        return self._find(_vpn_service.VPNService, name_or_id,
                          ignore_missing=ignore_missing)

    def get_vpn_service(self, vpn_service):
        """Get a single vpn service

        :param vpn_service: The value can be the ID of a vpn service or a
               :class:`~openstack.network.v2.vpn_service.VPNService`
               instance.

        :returns: One
                  :class:`~openstack.network.v2.vpn_service.VPNService`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_vpn_service.VPNService, vpn_service)

    def vpn_services(self, **query):
        """Return a generator of vpn services

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of vpn service objects
        :rtype: :class:`~openstack.network.v2.vpn_service.VPNService`
        """
        return self._list(_vpn_service.VPNService, paginated=False, **query)

    def update_vpn_service(self, vpn_service, **attrs):
        """Update a vpn service

        :param vpn_service: Either the id of a vpn service or a
            :class:`~openstack.network.v2.vpn_service.VPNService` instance.
        :attrs kwargs: The attributes to update on the vpnservice represented
                       by ``value``.

        :returns: The updated vpnservice
        :rtype: :class:`~openstack.network.v2.vpn_service.VPNService`
        """
        return self._update(_vpn_service.VPNService, vpn_service, **attrs)
