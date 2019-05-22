Baremetal API
=============

For details on how to use baremetal, see :doc:`/user/guides/baremetal`

.. automodule:: openstack.baremetal.v1._proxy

The Baremetal Class
-------------------

The baremetal high-level interface is available through the ``baremetal``
member of a :class:`~openstack.connection.Connection` object.
The ``baremetal`` member will only be added if the service is detected.

Node Operations
^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.create_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.update_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.patch_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.delete_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.find_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.nodes
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.set_node_power_state
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.set_node_provision_state
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.wait_for_nodes_provision_state
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.wait_for_node_reservation
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.validate_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.set_node_maintenance
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.unset_node_maintenance

Port Operations
^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.create_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.update_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.patch_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.delete_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.find_port
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.ports

Port Group Operations
^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.create_port_group
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.update_port_group
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.patch_port_group
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
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.patch_chassis
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.delete_chassis
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_chassis
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.find_chassis
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.chassis

VIF Operations
^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.attach_vif_to_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.detach_vif_from_node
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.list_node_vifs

Allocation Operations
^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy

   .. automethod:: openstack.baremetal.v1._proxy.Proxy.create_allocation
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.update_allocation
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.patch_allocation
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.delete_allocation
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.get_allocation
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.allocations
   .. automethod:: openstack.baremetal.v1._proxy.Proxy.wait_for_allocation

Utilities
---------

Building config drives
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: openstack.baremetal.configdrive
   :members:
