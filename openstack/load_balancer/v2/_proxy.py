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

from openstack.load_balancer.v2 import health_monitor as _hm
from openstack.load_balancer.v2 import l7_policy as _l7policy
from openstack.load_balancer.v2 import l7_rule as _l7rule
from openstack.load_balancer.v2 import listener as _listener
from openstack.load_balancer.v2 import load_balancer as _lb
from openstack.load_balancer.v2 import member as _member
from openstack.load_balancer.v2 import pool as _pool
from openstack import proxy


class Proxy(proxy.Proxy):

    def create_load_balancer(self, **attrs):
        """Create a new load balancer from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.load_balancer.v2.
                           load_balancer.LoadBalancer`,
                           comprised of the properties on the
                           LoadBalancer class.

        :returns: The results of load balancer creation
        :rtype: :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
        """
        return self._create(_lb.LoadBalancer, **attrs)

    def get_load_balancer(self, *attrs):
        """Get a load balancer

        :param load_balancer: The value can be the name of a load balancer
             or :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
             instance.

        :returns: One
             :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
        """
        return self._get(_lb.LoadBalancer, *attrs)

    def load_balancers(self, **query):
        """Retrieve a generator of load balancers

        :returns: A generator of load balancer instances
        """
        return self._list(_lb.LoadBalancer, paginated=True, **query)

    def delete_load_balancer(self, load_balancer, ignore_missing=True,
                             cascade=False):
        """Delete a load balancer

        :param load_balancer: The load_balancer can be either the name or a
            :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the load balancer does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent load balancer.
        :param bool cascade: If true will delete all child objects of
            the load balancer.

        :returns: ``None``
        """
        load_balancer = self._get_resource(_lb.LoadBalancer, load_balancer)
        load_balancer.cascade = cascade
        return self._delete(_lb.LoadBalancer, load_balancer,
                            ignore_missing=ignore_missing)

    def find_load_balancer(self, name_or_id, ignore_missing=True):
        """Find a single load balancer

        :param name_or_id: The name or ID of a load balancer
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the load balancer does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent load balancer.

        :returns: ``None``
        """
        return self._find(_lb.LoadBalancer, name_or_id,
                          ignore_missing=ignore_missing)

    def update_load_balancer(self, load_balancer, **attrs):
        """Update a load balancer

        :param load_balancer: The load_balancer can be either the name or a
            :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
            instance
        :param dict attrs: The attributes to update on the load balancer
                           represented by ``load_balancer``.

        :returns: The updated load_balancer
        :rtype: :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
        """
        return self._update(_lb.LoadBalancer, load_balancer, **attrs)

    def create_listener(self, **attrs):
        """Create a new listener from attributes

        :param dict attrs: Keyword arguments which will be used to create a
                        :class:`~openstack.load_balancer.v2.listener.Listener`,
                        comprised of the properties on the Listener class.

        :returns: The results of listener creation
        :rtype: :class:`~openstack.load_balancer.v2.listener.Listener`
        """
        return self._create(_listener.Listener, **attrs)

    def delete_listener(self, listener, ignore_missing=True):
        """Delete a listener

        :param listener: The value can be either the ID of a listner or a
               :class:`~openstack.load_balancer.v2.listener.Listener` instance.
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

        :returns: One :class:`~openstack.load_balancer.v2.listener.Listener`
         or None
        """
        return self._find(_listener.Listener, name_or_id,
                          ignore_missing=ignore_missing)

    def get_listener(self, listener):
        """Get a single listener

        :param listener: The value can be the ID of a listener or a
               :class:`~openstack.load_balancer.v2.listener.Listener`
               instance.

        :returns: One :class:`~openstack.load_balancer.v2.listener.Listener`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_listener.Listener, listener)

    def listeners(self, **query):
        """Return a generator of listeners

        :param dict query: Optional query parameters to be sent to limit
                           the resources being returned. Valid parameters are:
        :returns: A generator of listener objects
        :rtype: :class:`~openstack.load_balancer.v2.listener.Listener`
        """
        return self._list(_listener.Listener, paginated=True, **query)

    def update_listener(self, listener, **attrs):
        """Update a listener

        :param listener: Either the id of a listener or a
                      :class:`~openstack.load_balancer.v2.listener.Listener`
                      instance.
        :param dict attrs: The attributes to update on the listener
                           represented by ``listener``.

        :returns: The updated listener
        :rtype: :class:`~openstack.load_balancer.v2.listener.Listener`
        """
        return self._update(_listener.Listener, listener, **attrs)

    def create_pool(self, **attrs):
        """Create a new pool from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.load_balancer.v2.
                           pool.Pool`,
                           comprised of the properties on the
                           Pool class.

        :returns: The results of Pool creation
        :rtype: :class:`~openstack.load_balancer.v2.pool.Pool`
        """
        return self._create(_pool.Pool, **attrs)

    def get_pool(self, *attrs):
        """Get a pool

        :param pool: Value is
            :class:`~openstack.load_balancer.v2.pool.Pool`
            instance.

        :returns: One
             :class:`~openstack.load_balancer.v2.pool.Pool`
        """
        return self._get(_pool.Pool, *attrs)

    def pools(self, **query):
        """Retrieve a generator of pools

        :returns: A generator of Pool instances
        """
        return self._list(_pool.Pool, paginated=True, **query)

    def delete_pool(self, pool, ignore_missing=True):
        """Delete a pool

        :param pool: The pool is a
            :class:`~openstack.load_balancer.v2.pool.Pool`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the pool does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent pool.

        :returns: ``None``
        """
        return self._delete(_pool.Pool, pool,
                            ignore_missing=ignore_missing)

    def find_pool(self, name_or_id, ignore_missing=True):
        """Find a single pool

        :param name_or_id: The name or ID of a pool
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the pool does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent pool.

        :returns: ``None``
        """
        return self._find(_pool.Pool, name_or_id,
                          ignore_missing=ignore_missing)

    def update_pool(self, pool, **attrs):
        """Update a pool

        :param pool: Either the id of a pool or a
                      :class:`~openstack.load_balancer.v2.pool.Pool`
                      instance.
        :param dict attrs: The attributes to update on the pool
                           represented by ``pool``.

        :returns: The updated pool
        :rtype: :class:`~openstack.load_balancer.v2.pool.Pool`
        """
        return self._update(_pool.Pool, pool, **attrs)

    def create_member(self, pool, **attrs):
        """Create a new member from attributes

        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.load_balancer.v2.pool.Pool` instance
                     that the member will be created in.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.load_balancer.v2.member.Member`,
            comprised of the properties on the Member class.

        :returns: The results of member creation
        :rtype: :class:`~openstack.load_balancer.v2.member.Member`
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._create(_member.Member, pool_id=poolobj.id,
                            **attrs)

    def delete_member(self, member, pool, ignore_missing=True):
        """Delete a member

        :param member:
            The member can be either the ID of a member or a
            :class:`~openstack.load_balancer.v2.member.Member` instance.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.load_balancer.v2.pool.Pool` instance
                     that the member belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the member does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent member.

        :returns: ``None``
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        self._delete(_member.Member, member,
                     ignore_missing=ignore_missing, pool_id=poolobj.id)

    def find_member(self, name_or_id, pool, ignore_missing=True):
        """Find a single member

        :param str name_or_id: The name or ID of a member.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.load_balancer.v2.pool.Pool` instance
                     that the member belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.

        :returns: One :class:`~openstack.load_balancer.v2.member.Member`
                  or None
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._find(_member.Member, name_or_id,
                          ignore_missing=ignore_missing, pool_id=poolobj.id)

    def get_member(self, member, pool):
        """Get a single member

        :param member: The member can be the ID of a member or a
                       :class:`~openstack.load_balancer.v2.member.Member`
                       instance.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.load_balancer.v2.pool.Pool` instance
                     that the member belongs to.

        :returns: One :class:`~openstack.load_balancer.v2.member.Member`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._get(_member.Member, member,
                         pool_id=poolobj.id)

    def members(self, pool, **query):
        """Return a generator of members

        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.load_balancer.v2.pool.Pool` instance
                     that the member belongs to.
        :param dict query: Optional query parameters to be sent to limit
                           the resources being returned. Valid parameters are:

        :returns: A generator of member objects
        :rtype: :class:`~openstack.load_balancer.v2.member.Member`
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._list(_member.Member, paginated=True,
                          pool_id=poolobj.id, **query)

    def update_member(self, member, pool, **attrs):
        """Update a member

        :param member: Either the ID of a member or a
                       :class:`~openstack.load_balancer.v2.member.Member`
                       instance.
        :param pool: The pool can be either the ID of a pool or a
                     :class:`~openstack.load_balancer.v2.pool.Pool` instance
                     that the member belongs to.
        :param dict attrs: The attributes to update on the member
                           represented by ``member``.

        :returns: The updated member
        :rtype: :class:`~openstack.load_balancer.v2.member.Member`
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._update(_member.Member, member,
                            pool_id=poolobj.id, **attrs)

    def find_health_monitor(self, name_or_id, ignore_missing=True):
        """Find a single health monitor

        :param name_or_id: The name or ID of a health monitor
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the health monitor does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent health monitor.

        :returns: The
            :class:`openstack.load_balancer.v2.healthmonitor.HealthMonitor`
            object matching the given name or id or None if nothing matches.

        :raises: :class:`openstack.exceptions.DuplicateResource` if more
                 than one resource is found for this request.
        :raises: :class:`openstack.exceptions.ResourceNotFound` if nothing
                 is found and ignore_missing is ``False``.
        """
        return self._find(_hm.HealthMonitor, name_or_id,
                          ignore_missing=ignore_missing)

    def create_health_monitor(self, **attrs):
        """Create a new health monitor from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.load_balancer.v2.
                           healthmonitor.HealthMonitor`,
                           comprised of the properties on the
                           HealthMonitor class.

        :returns: The results of HealthMonitor creation
        :rtype: :class:`~openstack.load_balancer.v2.
            healthmonitor.HealthMonitor`
        """

        return self._create(_hm.HealthMonitor, **attrs)

    def get_health_monitor(self, healthmonitor):
        """Get a health monitor

        :param healthmonitor: The value can be the ID of a health monitor or
            :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`
            instance.

        :returns: One health monitor
        :rtype: :class:`~openstack.load_balancer.v2.
            healthmonitor.HealthMonitor`
        """
        return self._get(_hm.HealthMonitor, healthmonitor)

    def health_monitors(self, **query):
        """Retrieve a generator of health monitors

        :param dict query: Optional query parameters to be sent to limit
                           the resources being returned. Valid parameters are:
                           'name', 'created_at', 'updated_at', 'delay',
                           'expected_codes', 'http_method', 'max_retries',
                           'max_retries_down', 'pool_id',
                           'provisioning_status', 'operating_status',
                           'timeout', 'project_id', 'type', 'url_path',
                           'is_admin_state_up'.

        :returns: A generator of health monitor instances
        """
        return self._list(_hm.HealthMonitor, paginated=True, **query)

    def delete_health_monitor(self, healthmonitor, ignore_missing=True):
        """Delete a health monitor

        :param healthmonitor: The healthmonitor can be either the ID of the
            health monitor or a
            :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the healthmonitor does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent healthmonitor.

        :returns: ``None``
        """
        return self._delete(_hm.HealthMonitor, healthmonitor,
                            ignore_missing=ignore_missing)

    def update_health_monitor(self, healthmonitor, **attrs):
        """Update a health monitor

        :param healthmonitor: The healthmonitor can be either the ID of the
            health monitor or a
            :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`
            instance
        :param dict attrs: The attributes to update on the health monitor
                           represented by ``healthmonitor``.

        :returns: The updated health monitor
        :rtype: :class:`~openstack.load_balancer.v2.
            healthmonitor.HealthMonitor`
        """
        return self._update(_hm.HealthMonitor, healthmonitor,
                            **attrs)

    def create_l7_policy(self, **attrs):
        """Create a new l7policy from attributes

        :param dict attrs: Keyword arguments which will be used to create a
                        :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`,
                        comprised of the properties on the L7Policy class.

        :returns: The results of l7policy creation
        :rtype: :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
        """
        return self._create(_l7policy.L7Policy, **attrs)

    def delete_l7_policy(self, l7_policy, ignore_missing=True):
        """Delete a l7policy

        :param l7_policy: The value can be either the ID of a l7policy or a
          :class:`~openstack.load_balancer.v2.l7_policy.L7Policy` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the l7policy does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent l7policy.

        :returns: ``None``
        """
        self._delete(_l7policy.L7Policy, l7_policy,
                     ignore_missing=ignore_missing)

    def find_l7_policy(self, name_or_id, ignore_missing=True):
        """Find a single l7policy

        :param name_or_id: The name or ID of a l7policy.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.

        :returns: One :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
         or None
        """
        return self._find(_l7policy.L7Policy, name_or_id,
                          ignore_missing=ignore_missing)

    def get_l7_policy(self, l7_policy):
        """Get a single l7policy

        :param l7_policy: The value can be the ID of a l7policy or a
               :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
               instance.

        :returns: One :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_l7policy.L7Policy, l7_policy)

    def l7_policies(self, **query):
        """Return a generator of l7policies

        :param dict query: Optional query parameters to be sent to limit
                           the resources being returned. Valid parameters are:

        :returns: A generator of l7policy objects
        :rtype: :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
        """
        return self._list(_l7policy.L7Policy, paginated=True, **query)

    def update_l7_policy(self, l7_policy, **attrs):
        """Update a l7policy

        :param l7_policy: Either the id of a l7policy or a
                      :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
                      instance.
        :param dict attrs: The attributes to update on the l7policy
                           represented by ``l7policy``.

        :returns: The updated l7policy
        :rtype: :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
        """
        return self._update(_l7policy.L7Policy, l7_policy, **attrs)

    def create_l7_rule(self, l7_policy, **attrs):
        """Create a new l7rule from attributes

        :param l7_policy: The l7_policy can be either the ID of a l7policy or
                     :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
                     instance that the l7rule will be created in.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`,
            comprised of the properties on the L7Rule class.

        :returns: The results of l7rule creation
        :rtype: :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
        """
        l7policyobj = self._get_resource(_l7policy.L7Policy, l7_policy)
        return self._create(_l7rule.L7Rule, l7policy_id=l7policyobj.id,
                            **attrs)

    def delete_l7_rule(self, l7rule, l7_policy, ignore_missing=True):
        """Delete a l7rule

        :param l7rule:
            The l7rule can be either the ID of a l7rule or a
            :class:`~openstack.load_balancer.v2.l7_rule.L7Rule` instance.
        :param l7_policy: The l7_policy can be either the ID of a l7policy or
                     :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
                     instance that the l7rule belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the l7rule does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent l7rule.

        :returns: ``None``
        """
        l7policyobj = self._get_resource(_l7policy.L7Policy, l7_policy)
        self._delete(_l7rule.L7Rule, l7rule, ignore_missing=ignore_missing,
                     l7policy_id=l7policyobj.id)

    def find_l7_rule(self, name_or_id, l7_policy, ignore_missing=True):
        """Find a single l7rule

        :param str name_or_id: The name or ID of a l7rule.
        :param l7_policy: The l7_policy can be either the ID of a l7policy or
                     :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
                     instance that the l7rule belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.

        :returns: One :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
                  or None
        """
        l7policyobj = self._get_resource(_l7policy.L7Policy, l7_policy)
        return self._find(_l7rule.L7Rule, name_or_id,
                          ignore_missing=ignore_missing,
                          l7policy_id=l7policyobj.id)

    def get_l7_rule(self, l7rule, l7_policy):
        """Get a single l7rule

        :param l7rule: The l7rule can be the ID of a l7rule or a
                       :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
                       instance.
        :param l7_policy: The l7_policy can be either the ID of a l7policy or
                     :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
                     instance that the l7rule belongs to.

        :returns: One :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        l7policyobj = self._get_resource(_l7policy.L7Policy, l7_policy)
        return self._get(_l7rule.L7Rule, l7rule,
                         l7policy_id=l7policyobj.id)

    def l7_rules(self, l7_policy, **query):
        """Return a generator of l7rules

        :param l7_policy: The l7_policy can be either the ID of a l7_policy or
                     :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
                     instance that the l7rule belongs to.
        :param dict query: Optional query parameters to be sent to limit
                           the resources being returned. Valid parameters are:

        :returns: A generator of l7rule objects
        :rtype: :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
        """
        l7policyobj = self._get_resource(_l7policy.L7Policy, l7_policy)
        return self._list(_l7rule.L7Rule, paginated=True,
                          l7policy_id=l7policyobj.id, **query)

    def update_l7_rule(self, l7rule, l7_policy, **attrs):
        """Update a l7rule

        :param l7rule: Either the ID of a l7rule or a
                       :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
                       instance.
        :param l7_policy: The l7_policy can be either the ID of a l7policy or
                     :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
                     instance that the l7rule belongs to.
        :param dict attrs: The attributes to update on the l7rule
                           represented by ``l7rule``.

        :returns: The updated l7rule
        :rtype: :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
        """
        l7policyobj = self._get_resource(_l7policy.L7Policy, l7_policy)
        return self._update(_l7rule.L7Rule, l7rule,
                            l7policy_id=l7policyobj.id, **attrs)
