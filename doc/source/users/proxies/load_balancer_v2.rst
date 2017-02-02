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
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.get_load_balancer
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.load_balancers
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.delete_load_balancer
   .. automethod:: openstack.load_balancer.v2._proxy.Proxy.find_load_balancer
