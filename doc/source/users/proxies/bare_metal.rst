Bare Metal API
==============

For details on how to use bare_metal, see :doc:`/users/guides/bare_metal`

.. automodule:: openstack.bare_metal.v1._proxy

The BareMetal Class
--------------------

The bare_metal high-level interface is available through the ``bare_metal``
member of a :class:`~openstack.connection.Connection` object.
The ``bare_metal`` member will only be added if the service is detected.

Node Operations
^^^^^^^^^^^^^^^
.. autoclass:: openstack.bare_metal.v1._proxy.Proxy

   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.create_node
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.update_node
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.delete_node
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.get_node
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.find_node
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.nodes

Port Operations
^^^^^^^^^^^^^^^
.. autoclass:: openstack.bare_metal.v1._proxy.Proxy

   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.create_port
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.update_port
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.delete_port
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.get_port
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.find_port
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.ports

Port Group Operations
^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.bare_metal.v1._proxy.Proxy

   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.create_port_group
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.update_port_group
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.delete_port_group
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.get_port_group
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.find_port_group
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.port_groups

Driver Operations
^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.bare_metal.v1._proxy.Proxy

   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.drivers
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.get_driver

Chassis Operations
^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.bare_metal.v1._proxy.Proxy

   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.create_chassis
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.update_chassis
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.delete_chassis
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.get_chassis
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.find_chassis
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.chassis

Deprecated Methods
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.bare_metal.v1._proxy.Proxy

   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.create_portgroup
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.update_portgroup
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.delete_portgroup
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.get_portgroup
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.find_portgroup
   .. automethod:: openstack.bare_metal.v1._proxy.Proxy.portgroups
