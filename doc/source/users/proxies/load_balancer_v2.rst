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

   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.create_load_balancer
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.delete_load_balancer
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.find_load_balancer
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.get_load_balancer
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.load_balancers
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.update_load_balancer

Listener Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy

   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.create_listener
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.delete_listener
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.find_listener
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.get_listener
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.listeners
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.update_listener

Pool Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy

   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.create_pool
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.delete_pool
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.find_pool
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.get_pool
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.pools
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.update_pool

Member Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy

   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.create_member
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.delete_member
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.find_member
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.get_member
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.members
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.update_member

Health Monitor Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy

   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.create_health_monitor
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.delete_health_monitor
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.find_health_monitor
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.get_health_monitor
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.health_monitors
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.update_health_monitor

L7 Policy Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy

   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.create_l7_policy
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.delete_l7_policy
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.find_l7_policy
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.get_l7_policy
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.l7_policies
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.update_l7_policy

L7 Rule Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.load_balancer.v2._proxy.Proxy

   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.create_l7_rule
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.delete_l7_rule
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.find_l7_rule
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.get_l7_rule
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.l7_rules
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.update_l7_rule
