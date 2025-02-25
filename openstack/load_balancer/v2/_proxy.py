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

import typing as ty

from openstack.load_balancer.v2 import amphora as _amphora
from openstack.load_balancer.v2 import availability_zone as _availability_zone
from openstack.load_balancer.v2 import (
    availability_zone_profile as _availability_zone_profile,
)
from openstack.load_balancer.v2 import flavor as _flavor
from openstack.load_balancer.v2 import flavor_profile as _flavor_profile
from openstack.load_balancer.v2 import health_monitor as _hm
from openstack.load_balancer.v2 import l7_policy as _l7policy
from openstack.load_balancer.v2 import l7_rule as _l7rule
from openstack.load_balancer.v2 import listener as _listener
from openstack.load_balancer.v2 import load_balancer as _lb
from openstack.load_balancer.v2 import member as _member
from openstack.load_balancer.v2 import pool as _pool
from openstack.load_balancer.v2 import provider as _provider
from openstack.load_balancer.v2 import quota as _quota
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):
    _resource_registry = {
        "amphora": _amphora.Amphora,
        "availability_zone": _availability_zone.AvailabilityZone,
        "availability_zone_profile": _availability_zone_profile.AvailabilityZoneProfile,  # noqa: E501
        "flavor": _flavor.Flavor,
        "flavor_profile": _flavor_profile.FlavorProfile,
        "health_monitor": _hm.HealthMonitor,
        "l7_policy": _l7policy.L7Policy,
        "l7_rule": _l7rule.L7Rule,
        "load_balancer": _lb.LoadBalancer,
        "member": _member.Member,
        "pool": _pool.Pool,
        "provider": _provider.Provider,
        "quota": _quota.Quota,
    }

    def create_load_balancer(self, **attrs):
        """Create a new load balancer from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`,
            comprised of the properties on the
            LoadBalancer class.

        :returns: The results of load balancer creation
        :rtype: :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
        """
        return self._create(_lb.LoadBalancer, **attrs)

    def get_load_balancer(self, *attrs):
        """Get a load balancer

        :param load_balancer: The value can be the ID of a load balancer
            or :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
            instance.

        :returns: One
            :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
        """
        return self._get(_lb.LoadBalancer, *attrs)

    def get_load_balancer_statistics(self, load_balancer):
        """Get the load balancer statistics

        :param load_balancer: The value can be the ID of a load balancer
            or :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
            instance.

        :returns: One
            :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancerStats`
        """
        return self._get(
            _lb.LoadBalancerStats, lb_id=load_balancer, requires_id=False
        )

    def load_balancers(self, **query):
        """Retrieve a generator of load balancers

        :returns: A generator of load balancer instances
        """
        return self._list(_lb.LoadBalancer, **query)

    def delete_load_balancer(
        self, load_balancer, ignore_missing=True, cascade=False
    ):
        """Delete a load balancer

        :param load_balancer: The load_balancer can be either the ID or a
            :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the load balancer does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent load balancer.
        :param bool cascade: If true will delete all child objects of
            the load balancer.

        :returns: ``None``
        """
        load_balancer = self._get_resource(_lb.LoadBalancer, load_balancer)
        load_balancer.cascade = cascade
        return self._delete(
            _lb.LoadBalancer, load_balancer, ignore_missing=ignore_missing
        )

    def find_load_balancer(self, name_or_id, ignore_missing=True):
        """Find a single load balancer

        :param name_or_id: The name or ID of a load balancer
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the load balancer does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent load balancer.

        :returns: ``None``
        """
        return self._find(
            _lb.LoadBalancer, name_or_id, ignore_missing=ignore_missing
        )

    def update_load_balancer(self, load_balancer, **attrs):
        """Update a load balancer

        :param load_balancer: The load_balancer can be either the ID or a
            :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
            instance
        :param dict attrs: The attributes to update on the load balancer
            represented by ``load_balancer``.

        :returns: The updated load_balancer
        :rtype: :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
        """
        return self._update(_lb.LoadBalancer, load_balancer, **attrs)

    def wait_for_load_balancer(
        self,
        name_or_id,
        status='ACTIVE',
        failures=['ERROR'],
        interval=2,
        wait=300,
    ):
        """Wait for load balancer status

        :param name_or_id: The name or ID of the load balancer.
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
            Default to ['ERROR'].
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait between consecutive
            checks. Defaults to 2.
        :param wait: Maximum number of seconds to wait before the status
            to be reached. Defaults to 300.
        :returns: The load balancer is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to the desired status failed to occur within the specified wait
            time.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute.
        """
        lb = self._find(_lb.LoadBalancer, name_or_id, ignore_missing=False)

        return resource.wait_for_status(
            self,
            lb,
            status,
            failures,
            interval,
            wait,
            attribute='provisioning_status',
        )

    def failover_load_balancer(self, load_balancer):
        """Failover a load balancer

        :param load_balancer: The value can be the ID of a load balancer
            or :class:`~openstack.load_balancer.v2.load_balancer.LoadBalancer`
            instance.

        :returns: ``None``
        """
        lb = self._get_resource(_lb.LoadBalancer, load_balancer)
        lb.failover(self)

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

        :param listener: The value can be either the ID of a listener or a
            :class:`~openstack.load_balancer.v2.listener.Listener` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the listner does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent listener.

        :returns: ``None``
        """
        self._delete(
            _listener.Listener, listener, ignore_missing=ignore_missing
        )

    def find_listener(self, name_or_id, ignore_missing=True):
        """Find a single listener

        :param name_or_id: The name or ID of a listener.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.

        :returns: One :class:`~openstack.load_balancer.v2.listener.Listener`
            or None
        """
        return self._find(
            _listener.Listener, name_or_id, ignore_missing=ignore_missing
        )

    def get_listener(self, listener):
        """Get a single listener

        :param listener: The value can be the ID of a listener or a
            :class:`~openstack.load_balancer.v2.listener.Listener`
            instance.

        :returns: One :class:`~openstack.load_balancer.v2.listener.Listener`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_listener.Listener, listener)

    def get_listener_statistics(self, listener):
        """Get the listener statistics

        :param listener: The value can be the ID of a listener or a
            :class:`~openstack.load_balancer.v2.listener.Listener`
            instance.

        :returns: One
            :class:`~openstack.load_balancer.v2.listener.ListenerStats`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(
            _listener.ListenerStats, listener_id=listener, requires_id=False
        )

    def listeners(self, **query):
        """Return a generator of listeners

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Valid parameters are:
        :returns: A generator of listener objects
        :rtype: :class:`~openstack.load_balancer.v2.listener.Listener`
        """
        return self._list(_listener.Listener, **query)

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
            a :class:`~openstack.load_balancer.v2.pool.Pool`, comprised of the
            properties on the Pool class.

        :returns: The results of Pool creation
        :rtype: :class:`~openstack.load_balancer.v2.pool.Pool`
        """
        return self._create(_pool.Pool, **attrs)

    def get_pool(self, *attrs):
        """Get a pool

        :param pool: Value is either a pool ID or a
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
        return self._list(_pool.Pool, **query)

    def delete_pool(self, pool, ignore_missing=True):
        """Delete a pool

        :param pool: The pool is either a pool ID or a
            :class:`~openstack.load_balancer.v2.pool.Pool`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the pool does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent pool.

        :returns: ``None``
        """
        return self._delete(_pool.Pool, pool, ignore_missing=ignore_missing)

    def find_pool(self, name_or_id, ignore_missing=True):
        """Find a single pool

        :param name_or_id: The name or ID of a pool
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the pool does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent pool.

        :returns: ``None``
        """
        return self._find(
            _pool.Pool, name_or_id, ignore_missing=ignore_missing
        )

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
        return self._create(_member.Member, pool_id=poolobj.id, **attrs)

    def delete_member(self, member, pool, ignore_missing=True):
        """Delete a member

        :param member:
            The member can be either the ID of a member or a
            :class:`~openstack.load_balancer.v2.member.Member` instance.
        :param pool: The pool can be either the ID of a pool or a
            :class:`~openstack.load_balancer.v2.pool.Pool` instance
            that the member belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the member does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent member.

        :returns: ``None``
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        self._delete(
            _member.Member,
            member,
            ignore_missing=ignore_missing,
            pool_id=poolobj.id,
        )

    def find_member(self, name_or_id, pool, ignore_missing=True):
        """Find a single member

        :param str name_or_id: The name or ID of a member.
        :param pool: The pool can be either the ID of a pool or a
            :class:`~openstack.load_balancer.v2.pool.Pool` instance
            that the member belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.

        :returns: One :class:`~openstack.load_balancer.v2.member.Member`
            or None
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._find(
            _member.Member,
            name_or_id,
            ignore_missing=ignore_missing,
            pool_id=poolobj.id,
        )

    def get_member(self, member, pool):
        """Get a single member

        :param member: The member can be the ID of a member or a
            :class:`~openstack.load_balancer.v2.member.Member`
            instance.
        :param pool: The pool can be either the ID of a pool or a
            :class:`~openstack.load_balancer.v2.pool.Pool` instance
            that the member belongs to.

        :returns: One :class:`~openstack.load_balancer.v2.member.Member`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        poolobj = self._get_resource(_pool.Pool, pool)
        return self._get(_member.Member, member, pool_id=poolobj.id)

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
        return self._list(_member.Member, pool_id=poolobj.id, **query)

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
        return self._update(
            _member.Member, member, pool_id=poolobj.id, **attrs
        )

    def find_health_monitor(self, name_or_id, ignore_missing=True):
        """Find a single health monitor

        :param name_or_id: The name or ID of a health monitor
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the health monitor does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent health monitor.

        :returns: The
            :class:`openstack.load_balancer.v2.healthmonitor.HealthMonitor`
            object matching the given name or id or None if nothing matches.

        :raises: :class:`openstack.exceptions.DuplicateResource` if more
            than one resource is found for this request.
        :raises: :class:`openstack.exceptions.NotFoundException` if nothing
            is found and ignore_missing is ``False``.
        """
        return self._find(
            _hm.HealthMonitor, name_or_id, ignore_missing=ignore_missing
        )

    def create_health_monitor(self, **attrs):
        """Create a new health monitor from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`,
            comprised of the properties on the HealthMonitor class.

        :returns: The results of HealthMonitor creation
        :rtype:
            :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`
        """

        return self._create(_hm.HealthMonitor, **attrs)

    def get_health_monitor(self, healthmonitor):
        """Get a health monitor

        :param healthmonitor: The value can be the ID of a health monitor or
            :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`
            instance.

        :returns: One health monitor
        :rtype:
            :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`
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
        return self._list(_hm.HealthMonitor, **query)

    def delete_health_monitor(self, healthmonitor, ignore_missing=True):
        """Delete a health monitor

        :param healthmonitor: The healthmonitor can be either the ID of the
            health monitor or a
            :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the healthmonitor does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent healthmonitor.

        :returns: ``None``
        """
        return self._delete(
            _hm.HealthMonitor, healthmonitor, ignore_missing=ignore_missing
        )

    def update_health_monitor(self, healthmonitor, **attrs):
        """Update a health monitor

        :param healthmonitor: The healthmonitor can be either the ID of the
            health monitor or a
            :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`
            instance
        :param dict attrs: The attributes to update on the health monitor
            represented by ``healthmonitor``.

        :returns: The updated health monitor
        :rtype:
            :class:`~openstack.load_balancer.v2.healthmonitor.HealthMonitor`
        """
        return self._update(_hm.HealthMonitor, healthmonitor, **attrs)

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
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the l7policy does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent l7policy.

        :returns: ``None``
        """
        self._delete(
            _l7policy.L7Policy, l7_policy, ignore_missing=ignore_missing
        )

    def find_l7_policy(self, name_or_id, ignore_missing=True):
        """Find a single l7policy

        :param name_or_id: The name or ID of a l7policy.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.

        :returns: One :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
            or None
        """
        return self._find(
            _l7policy.L7Policy, name_or_id, ignore_missing=ignore_missing
        )

    def get_l7_policy(self, l7_policy):
        """Get a single l7policy

        :param l7_policy: The value can be the ID of a l7policy or a
            :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
            instance.

        :returns: One :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
        :raises: :class:`~openstack.exceptions.NotFoundException`
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
        return self._list(_l7policy.L7Policy, **query)

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
        return self._create(
            _l7rule.L7Rule, l7policy_id=l7policyobj.id, **attrs
        )

    def delete_l7_rule(self, l7rule, l7_policy, ignore_missing=True):
        """Delete a l7rule

        :param l7rule: The l7rule can be either the ID of a l7rule or a
            :class:`~openstack.load_balancer.v2.l7_rule.L7Rule` instance.
        :param l7_policy: The l7_policy can be either the ID of a l7policy or
            :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
            instance that the l7rule belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the l7rule does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent l7rule.

        :returns: ``None``
        """
        l7policyobj = self._get_resource(_l7policy.L7Policy, l7_policy)
        self._delete(
            _l7rule.L7Rule,
            l7rule,
            ignore_missing=ignore_missing,
            l7policy_id=l7policyobj.id,
        )

    def find_l7_rule(self, name_or_id, l7_policy, ignore_missing=True):
        """Find a single l7rule

        :param str name_or_id: The name or ID of a l7rule.
        :param l7_policy: The l7_policy can be either the ID of a l7policy or
            :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
            instance that the l7rule belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.

        :returns: One :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
            or None
        """
        l7policyobj = self._get_resource(_l7policy.L7Policy, l7_policy)
        return self._find(
            _l7rule.L7Rule,
            name_or_id,
            ignore_missing=ignore_missing,
            l7policy_id=l7policyobj.id,
        )

    def get_l7_rule(self, l7rule, l7_policy):
        """Get a single l7rule

        :param l7rule: The l7rule can be the ID of a l7rule or a
            :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
            instance.
        :param l7_policy: The l7_policy can be either the ID of a l7policy or
            :class:`~openstack.load_balancer.v2.l7_policy.L7Policy`
            instance that the l7rule belongs to.

        :returns: One :class:`~openstack.load_balancer.v2.l7_rule.L7Rule`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        l7policyobj = self._get_resource(_l7policy.L7Policy, l7_policy)
        return self._get(_l7rule.L7Rule, l7rule, l7policy_id=l7policyobj.id)

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
        return self._list(_l7rule.L7Rule, l7policy_id=l7policyobj.id, **query)

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
        return self._update(
            _l7rule.L7Rule, l7rule, l7policy_id=l7policyobj.id, **attrs
        )

    def quotas(self, **query):
        """Return a generator of quotas

        :param dict query: Optional query parameters to be sent to limit
            the resources being returned. Currently no query
            parameter is supported.

        :returns: A generator of quota objects
        :rtype: :class:`~openstack.load_balancer.v2.quota.Quota`
        """
        return self._list(_quota.Quota, **query)

    def get_quota(self, quota):
        """Get a quota

        :param quota: The value can be the ID of a quota or a
            :class:`~openstack.load_balancer.v2.quota.Quota`
            instance. The ID of a quota is the same as the project
            ID for the quota.

        :returns: One :class:`~openstack.load_balancer.v2.quota.Quota`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_quota.Quota, quota)

    def update_quota(self, quota, **attrs):
        """Update a quota

        :param quota: Either the ID of a quota or a
            :class:`~openstack.load_balancer.v2.quota.Quota`
            instance. The ID of a quota is the same as the
            project ID for the quota.
        :param dict attrs: The attributes to update on the quota represented
            by ``quota``.

        :returns: The updated quota
        :rtype: :class:`~openstack.load_balancer.v2.quota.Quota`
        """
        return self._update(_quota.Quota, quota, **attrs)

    def get_quota_default(self):
        """Get a default quota

        :returns: One :class:`~openstack.load_balancer.v2.quota.QuotaDefault`
        """
        return self._get(_quota.QuotaDefault, requires_id=False)

    def delete_quota(self, quota, ignore_missing=True):
        """Delete a quota (i.e. reset to the default quota)

        :param quota: The value can be either the ID of a quota or a
            :class:`~openstack.load_balancer.v2.quota.Quota`
            instance. The ID of a quota is the same as the
            project ID for the quota.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when quota does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent quota.

        :returns: ``None``
        """
        self._delete(_quota.Quota, quota, ignore_missing=ignore_missing)

    def providers(self, **query):
        """Retrieve a generator of providers

        :returns: A generator of providers instances
        """
        return self._list(_provider.Provider, **query)

    def provider_flavor_capabilities(self, provider, **query):
        """Retrieve a generator of provider flavor capabilities

        :returns: A generator of provider flavor capabilities instances
        """
        return self._list(
            _provider.ProviderFlavorCapabilities, provider=provider, **query
        )

    def create_flavor_profile(self, **attrs):
        """Create a new flavor profile from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.load_balancer.v2.flavor_profile.FlavorProfile`,
            comprised of the properties on the FlavorProfile class.

        :returns: The results of profile creation creation
        :rtype:
            :class:`~openstack.load_balancer.v2.flavor_profile.FlavorProfile`
        """
        return self._create(_flavor_profile.FlavorProfile, **attrs)

    def get_flavor_profile(self, *attrs):
        """Get a flavor profile

        :param flavor_profile: The value can be the name of a flavor profile or
            :class:`~openstack.load_balancer.v2.flavor_profile.FlavorProfile`
            instance.

        :returns: One
            :class:`~openstack.load_balancer.v2.flavor_profile.FlavorProfile`
        """
        return self._get(_flavor_profile.FlavorProfile, *attrs)

    def flavor_profiles(self, **query):
        """Retrieve a generator of flavor profiles

        :returns: A generator of flavor profiles instances
        """
        return self._list(_flavor_profile.FlavorProfile, **query)

    def delete_flavor_profile(self, flavor_profile, ignore_missing=True):
        """Delete a flavor profile

        :param flavor_profile: The flavor_profile can be either the ID or a
            :class:`~openstack.load_balancer.v2.flavor_profile.FlavorProfile`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the flavor profile does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent flavor profile.

        :returns: ``None``
        """
        self._delete(
            _flavor_profile.FlavorProfile,
            flavor_profile,
            ignore_missing=ignore_missing,
        )

    def find_flavor_profile(self, name_or_id, ignore_missing=True):
        """Find a single flavor profile

        :param name_or_id: The name or ID of a flavor profile
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the flavor profile does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent flavor profile.

        :returns: ``None``
        """
        return self._find(
            _flavor_profile.FlavorProfile,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def update_flavor_profile(self, flavor_profile, **attrs):
        """Update a flavor profile

        :param flavor_profile: The flavor_profile can be either the ID or a
            :class:`~openstack.load_balancer.v2.flavor_profile.FlavorProfile`
            instance
        :param dict attrs: The attributes to update on the flavor profile
            represented by ``flavor_profile``.

        :returns: The updated flavor profile
        :rtype:
            :class:`~openstack.load_balancer.v2.flavor_profile.FlavorProfile`
        """
        return self._update(
            _flavor_profile.FlavorProfile, flavor_profile, **attrs
        )

    def create_flavor(self, **attrs):
        """Create a new flavor from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.load_balancer.v2.flavor.Flavor`,
            comprised of the properties on the Flavorclass.

        :returns: The results of flavor creation creation
        :rtype: :class:`~openstack.load_balancer.v2.flavor.Flavor`
        """
        return self._create(_flavor.Flavor, **attrs)

    def get_flavor(self, *attrs):
        """Get a flavor

        :param flavor: The value can be the ID of a flavor
            or :class:`~openstack.load_balancer.v2.flavor.Flavor` instance.

        :returns: One
            :class:`~openstack.load_balancer.v2.flavor.Flavor`
        """
        return self._get(_flavor.Flavor, *attrs)

    def flavors(self, **query):
        """Retrieve a generator of flavors

        :returns: A generator of flavor instances
        """
        return self._list(_flavor.Flavor, **query)

    def delete_flavor(self, flavor, ignore_missing=True):
        """Delete a flavor

        :param flavor: The flavorcan be either the ID or a
            :class:`~openstack.load_balancer.v2.flavor.Flavor` instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the flavor does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent flavor.

        :returns: ``None``
        """
        self._delete(_flavor.Flavor, flavor, ignore_missing=ignore_missing)

    def find_flavor(self, name_or_id, ignore_missing=True):
        """Find a single flavor

        :param name_or_id: The name or ID of a flavor
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the flavor does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent flavor.

        :returns: ``None``
        """
        return self._find(
            _flavor.Flavor, name_or_id, ignore_missing=ignore_missing
        )

    def update_flavor(self, flavor, **attrs):
        """Update a flavor

        :param flavor: The flavor can be either the ID or a
            :class:`~openstack.load_balancer.v2.flavor.Flavor` instance
        :param dict attrs: The attributes to update on the flavor
            represented by ``flavor``.

        :returns: The updated flavor
        :rtype: :class:`~openstack.load_balancer.v2.flavor.Flavor`
        """
        return self._update(_flavor.Flavor, flavor, **attrs)

    def amphorae(self, **query):
        """Retrieve a generator of amphorae

        :returns: A generator of amphora instances
        """
        return self._list(_amphora.Amphora, **query)

    def get_amphora(self, *attrs):
        """Get a amphora

        :param amphora: The value can be the ID of an amphora
            or :class:`~openstack.load_balancer.v2.amphora.Amphora` instance.

        :returns: One
            :class:`~openstack.load_balancer.v2.amphora.Amphora`
        """
        return self._get(_amphora.Amphora, *attrs)

    def find_amphora(self, amphora_id, ignore_missing=True):
        """Find a single amphora

        :param amphora_id: The ID of a amphora
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the amphora does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent amphora.

        :returns: ``None``
        """
        return self._find(
            _amphora.Amphora, amphora_id, ignore_missing=ignore_missing
        )

    def configure_amphora(self, amphora_id):
        """Update the configuration of an amphora agent

        :param amphora_id: The ID of an amphora

        :returns: ``None``
        """
        lb = self._get_resource(_amphora.Amphora, amphora_id)
        lb.configure(self)

    def failover_amphora(self, amphora_id):
        """Failover an amphora

        :param amphora_id: The ID of an amphora

        :returns: ``None``
        """
        lb = self._get_resource(_amphora.Amphora, amphora_id)
        lb.failover(self)

    def create_availability_zone_profile(self, **attrs):
        """Create a new availability zone profile from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.load_balancer.v2.availability_zone_profile.AvailabilityZoneProfile`
            comprised of the properties on the AvailabilityZoneProfile
            class.

        :returns: The results of profile creation
        :rtype:
            :class:`~openstack.load_balancer.v2.availability_zone_profile.AvailabilityZoneProfile`
        """
        return self._create(
            _availability_zone_profile.AvailabilityZoneProfile, **attrs
        )

    def get_availability_zone_profile(self, *attrs):
        """Get an availability zone profile

        :param availability_zone_profile: The value can be the ID of an
            availability_zone profile or
            :class:`~openstack.load_balancer.v2.availability_zone_profile.AvailabilityZoneProfile`
            instance.

        :returns: One
            :class:`~openstack.load_balancer.v2.availability_zone_profile.AvailabilityZoneProfile`
        """
        return self._get(
            _availability_zone_profile.AvailabilityZoneProfile, *attrs
        )

    def availability_zone_profiles(self, **query):
        """Retrieve a generator of availability zone profiles

        :returns: A generator of availability zone profiles instances
        """
        return self._list(
            _availability_zone_profile.AvailabilityZoneProfile, **query
        )

    def delete_availability_zone_profile(
        self, availability_zone_profile, ignore_missing=True
    ):
        """Delete an availability zone profile

        :param availability_zone_profile: The availability_zone_profile can be
            either the ID or a
            :class:`~openstack.load_balancer.v2.availability_zone_profile.AvailabilityZoneProfile`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the availability zone profile does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent availability zone profile.

        :returns: ``None``
        """
        self._delete(
            _availability_zone_profile.AvailabilityZoneProfile,
            availability_zone_profile,
            ignore_missing=ignore_missing,
        )

    def find_availability_zone_profile(self, name_or_id, ignore_missing=True):
        """Find a single availability zone profile

        :param name_or_id: The name or ID of a availability zone profile
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the availability zone profile does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent availability zone profile.

        :returns: ``None``
        """
        return self._find(
            _availability_zone_profile.AvailabilityZoneProfile,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def update_availability_zone_profile(
        self, availability_zone_profile, **attrs
    ):
        """Update an availability zone profile

        :param availability_zone_profile: The availability_zone_profile can be
            either the ID or a
            :class:`~openstack.load_balancer.v2.availability_zone_profile.AvailabilityZoneProfile`
            instance
        :param dict attrs: The attributes to update on the availability_zone
            profile represented by ``availability_zone_profile``.

        :returns: The updated availability zone profile
        :rtype:
            :class:`~openstack.load_balancer.v2.availability_zone_profile.AvailabilityZoneProfile`
        """
        return self._update(
            _availability_zone_profile.AvailabilityZoneProfile,
            availability_zone_profile,
            **attrs,
        )

    def create_availability_zone(self, **attrs):
        """Create a new availability zone from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.load_balancer.v2.availability_zone.AvailabilityZone`
            comprised of the properties on the AvailabilityZoneclass.

        :returns: The results of availability_zone creation creation
        :rtype:
            :class:`~openstack.load_balancer.v2.availability_zone.AvailabilityZone`
        """
        return self._create(_availability_zone.AvailabilityZone, **attrs)

    def get_availability_zone(self, *attrs):
        """Get an availability zone

        :param availability_zone: The value can be the ID of a
            availability_zone or
            :class:`~openstack.load_balancer.v2.availability_zone.AvailabilityZone`
            instance.

        :returns: One
            :class:`~openstack.load_balancer.v2.availability_zone.AvailabilityZone`
        """
        return self._get(_availability_zone.AvailabilityZone, *attrs)

    def availability_zones(self, **query):
        """Retrieve a generator of availability zones

        :returns: A generator of availability zone instances
        """
        return self._list(_availability_zone.AvailabilityZone, **query)

    def delete_availability_zone(self, availability_zone, ignore_missing=True):
        """Delete an availability_zone

        :param availability_zone: The availability_zone can be either the ID
            or a
            :class:`~openstack.load_balancer.v2.availability_zone.AvailabilityZone`
            instance
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the availability zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent availability zone.

        :returns: ``None``
        """
        self._delete(
            _availability_zone.AvailabilityZone,
            availability_zone,
            ignore_missing=ignore_missing,
        )

    def find_availability_zone(self, name_or_id, ignore_missing=True):
        """Find a single availability zone

        :param name_or_id: The name or ID of a availability zone
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the availability zone does not exist.
            When set to ``True``, no exception will be set when attempting
            to find a nonexistent availability zone.

        :returns: ``None``
        """
        return self._find(
            _availability_zone.AvailabilityZone,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def update_availability_zone(self, availability_zone, **attrs):
        """Update an availability zone

        :param availability_zone: The availability_zone can be either the ID
            or a
            :class:`~openstack.load_balancer.v2.availability_zone.AvailabilityZone`
            instance
        :param dict attrs: The attributes to update on the availability_zone
            represented by ``availability_zone``.

        :returns: The updated availability_zone
        :rtype:
            :class:`~openstack.load_balancer.v2.availability_zone.AvailabilityZone`
        """
        return self._update(
            _availability_zone.AvailabilityZone, availability_zone, **attrs
        )

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: ty.Optional[list[str]] = None,
        interval: ty.Union[int, float, None] = 2,
        wait: ty.Optional[int] = None,
        attribute: str = 'status',
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :return: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int = 2,
        wait: int = 120,
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)
