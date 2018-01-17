Baremetal API
==============

For details on how to use baremetal, see :doc:`/user/guides/baremetal`

.. automodule:: openstack.baremetal.v1._proxy

The Baremetal Class
--------------------

The baremetal high-level interface is available through the ``baremetal``
member of a :class:`~openstack.connection.Connection` object.
The ``baremetal`` member will only be added if the service is detected.

Node Operations
^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.create_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.update_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.delete_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.find_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.nodes

Port Operations
^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.create_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.update_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.delete_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.find_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.ports

Port Group Operations
^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.create_port_group
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.update_port_group
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.delete_port_group
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_port_group
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.find_port_group
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.port_groups

Driver Operations
^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.drivers
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_driver

Chassis Operations
^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.create_chassis
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.update_chassis
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.delete_chassis
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_chassis
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.find_chassis
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.chassis

Deprecated Methods
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.create_portgroup
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.update_portgroup
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.delete_portgroup
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_portgroup
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.find_portgroup
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.portgroups
