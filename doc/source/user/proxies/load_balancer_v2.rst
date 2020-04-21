Load Balancer v2 API
====================

.. automodule:: openstack.load_balancer.v2._proxy

The LoadBalancer Class
----------------------

The load_balancer high-level interface is available through the
``load_balancer`` member of a :class:`~openstack.connection.Connection` object.
The ``load_balancer`` member will only be added if the service is detected.

Load Balancer Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_load_balancer, delete_load_balancer, find_load_balancer,
            get_load_balancer, get_load_balancer_statistics, load_balancers,
            update_load_balancer, failover_load_balancer

Listener Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_listener, delete_listener, find_listener, get_listener,
            get_listener_statistics, listeners, update_listener

Pool Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_pool, delete_pool, find_pool, get_pool, pools, update_pool

Member Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_member, delete_member, find_member, get_member, members,
            update_member

Health Monitor Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_health_monitor, delete_health_monitor, find_health_monitor,
            get_health_monitor, health_monitors, update_health_monitor

L7 Policy Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_l7_policy, delete_l7_policy, find_l7_policy,
            get_l7_policy, l7_policies, update_l7_policy

L7 Rule Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_l7_rule, delete_l7_rule, find_l7_rule,
            get_l7_rule, l7_rules, update_l7_rule

Provider Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: providers, provider_flavor_capabilities

Flavor Profile Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_flavor_profile, get_flavor_profile, flavor_profiles,
            delete_flavor_profile, find_flavor_profile, update_flavor_profile

Flavor Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_flavor, get_flavor, flavors, delete_flavor,
            find_flavor, update_flavor

Quota Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: update_quota, delete_quota, quotas, get_quota, get_quota_default

Amphora Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: amphorae, get_amphora, find_amphora, configure_amphora,
            failover_amphora

Availability Zone Profile Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_availability_zone_profile, get_availability_zone_profile,
            availability_zone_profiles, delete_availability_zone_profile,
            find_availability_zone_profile, update_availability_zone_profile

Availability Zone Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy
  :noindex:
  :members: create_availability_zone, get_availability_zone,
            availability_zones, delete_availability_zone,
            find_availability_zone, update_availability_zone
